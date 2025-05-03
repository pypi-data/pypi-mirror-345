import cv2
import numpy as np
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import pytesseract

@dataclass
class TextCell:
    """Represents a cell containing text in the document"""
    id: int
    x: int
    y: int
    width: int
    height: int
    text: str
    orientation: str
    is_printed: bool
    confidence: Dict[str, float]

@dataclass
class AnalysisStats:
    """Statistics for text analysis"""
    horizontal_printed: int = 0
    horizontal_handwritten: int = 0
    vertical_printed: int = 0
    vertical_handwritten: int = 0
    unknown: int = 0

# Convert class methods to standalone functions

def setup_output_dirs(output_dir: Path, text_regions_dir: Path) -> None:
    """Create necessary output directories"""
    output_dir.mkdir(parents=True, exist_ok=True)
    text_regions_dir.mkdir(parents=True, exist_ok=True)

def analyze(image: np.ndarray, rect_rois: List[Dict], config: Dict, 
            output_dir: Optional[Path] = None, debug_visualization: bool = True,
            header_structure: Optional[Dict] = None) -> Dict:
    """Main analysis method"""
    # Initialize required structures
    stats = AnalysisStats()
    printed_cells: List[TextCell] = []
    handwritten_cells: List[TextCell] = []
    original_img = image
    visual_result = image.copy()
    clean_vis = np.ones_like(image) * 255
    
    # Setup directories if provided
    text_regions_dir = output_dir / "text_regions" if output_dir else None
    if output_dir and text_regions_dir:
        setup_output_dirs(output_dir, text_regions_dir)
    
    # Initialize header lookup if provided
    header_lookup = build_header_lookup(header_structure) if header_structure else {}
    
    # Process the image
    thresh = preprocess_image(original_img, config)
    analyze_rois(rect_rois, visual_result, thresh, config, stats, printed_cells, 
                handwritten_cells, text_regions_dir, header_lookup, debug_visualization)
    create_visualizations(printed_cells, handwritten_cells, visual_result, clean_vis, config, debug_visualization)
    
    if output_dir:
        save_results(printed_cells, handwritten_cells, stats, visual_result, clean_vis, output_dir, config)
    
    # Get all cells in proper order
    all_cells = sorted(
        printed_cells + handwritten_cells,
        key=lambda c: (c.y, c.x)  # Sort by y, then x
    )
    
    return {
        "stats": stats,
        "printed_cells": printed_cells,
        "handwritten_cells": handwritten_cells,
        "all_cells": all_cells,  # Include all cells
        "visualizations": {
            "detailed": visual_result,
            "clean": clean_vis
        }
    }

def preprocess_image(original_img: np.ndarray, config: Dict) -> np.ndarray:
    """Preprocess the image for better text recognition"""
    gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, config['gaussian_blur'], 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        config['adaptive_threshold']['block_size'],
        config['adaptive_threshold']['C']
    )
    return thresh

def analyze_rois(rect_rois: List[Dict], visual_result: np.ndarray, thresh: np.ndarray, 
                config: Dict, stats: AnalysisStats, printed_cells: List[TextCell], 
                handwritten_cells: List[TextCell], text_regions_dir: Optional[Path] = None,
                header_lookup: Dict = None, debug_visualization: bool = True) -> None:
    """Analyze each ROI for text type"""
    for i, roi in enumerate(rect_rois, 1):
        process_single_roi(i, roi, visual_result, thresh, config, stats, 
                          printed_cells, handwritten_cells, text_regions_dir, 
                          header_lookup, debug_visualization)

def process_single_roi(idx: int, roi: Dict, visual_result: np.ndarray, thresh: np.ndarray,
                      config: Dict, stats: AnalysisStats, printed_cells: List[TextCell],
                      handwritten_cells: List[TextCell], text_regions_dir: Optional[Path] = None,
                      header_lookup: Dict = None, debug_visualization: bool = True) -> None:
    """Process a single ROI with validation rules"""
    x, y, w, h = roi["x"], roi["y"], roi["w"], roi["h"]
    
    # Create cell first to get position
    cell = TextCell(
        id=idx,
        x=x, y=y,
        width=w, height=h,
        text="",  # Temporary
        orientation="unknown",
        is_printed=False,
        confidence={}
    )
    
    # Get validation rules for this position
    validation_rules = get_cell_validation_rules(cell, header_lookup)
    
    # Update OCR config based on rules
    local_config = config.copy()
    if validation_rules:
        update_ocr_config(cell, validation_rules, local_config)
    
    # Extract and process text region
    text_region = visual_result[y:y+h, x:x+w]
    if text_region.size == 0:
        return
        
    if text_regions_dir:
        save_text_region(idx, text_region, x, y, w, h, visual_result, thresh, text_regions_dir)
    
    # Detect text type with validation context
    detection = detect_text_type(text_region, local_config, validation_rules=validation_rules)
    
    # Update cell with detection results
    cell.text = detection["text"].strip()
    cell.orientation = detection["orientation"]
    cell.is_printed = detection["is_printed_overall"]
    cell.confidence = get_confidence_dict(detection)
    
    # Additional validation based on rules
    if validation_rules:
        cell.validation_result = validate_cell_text(
            cell.text, 
            validation_rules['validation_config']
        )
    
    categorize_cell(cell, stats, printed_cells, handwritten_cells)
    update_visualizations(cell, visual_result, local_config, debug_visualization)

def categorize_cell(cell: TextCell, stats: AnalysisStats, 
                   printed_cells: List[TextCell], handwritten_cells: List[TextCell]) -> None:
    """Categorize cell and update statistics"""
    if cell.is_printed:
        printed_cells.append(cell)
        if cell.orientation == "vertical":
            stats.vertical_printed += 1
        elif cell.orientation == "horizontal":
            stats.horizontal_printed += 1
        else:
            stats.unknown += 1
    else:
        handwritten_cells.append(cell)
        if cell.orientation == "vertical":
            stats.vertical_handwritten += 1
        elif cell.orientation == "horizontal":
            stats.horizontal_handwritten += 1
        else:
            stats.unknown += 1

def analyze_table_structure(printed_cells: List[TextCell], 
                           handwritten_cells: List[TextCell], config: Dict) -> List[List[TextCell]]:
    """Analyze the table structure by grouping cells into rows"""
    all_cells = printed_cells + handwritten_cells
    all_cells.sort(key=lambda c: (c.y, c.x))  # Sort by y, then x
    
    row_groups = []
    current_row = []
    last_y = -1
    
    for cell in all_cells:
        if last_y == -1 or abs(cell.y - last_y) < config['row_grouping']['y_tolerance']:
            current_row.append(cell)
        else:
            if current_row:
                current_row.sort(key=lambda c: c.x)  # Sort by x within row
                row_groups.append(current_row)
            current_row = [cell]
        last_y = cell.y
    
    if current_row:
        current_row.sort(key=lambda c: c.x)
        row_groups.append(current_row)
    
    return row_groups

def save_analysis_report(printed_cells: List[TextCell], handwritten_cells: List[TextCell], 
                         stats: AnalysisStats, output_dir: Path, config: Dict) -> None:
    """Save a detailed analysis report"""
    report_path = output_dir / "analysis_report.txt"
    with open(report_path, 'w', encoding='utf-8') as report:
        write_header_section(report)
        write_statistics_section(report, stats)
        write_table_structure_section(report, printed_cells, handwritten_cells, config)

def save_results(printed_cells: List[TextCell], handwritten_cells: List[TextCell], 
                stats: AnalysisStats, visual_result: np.ndarray, clean_vis: np.ndarray, 
                output_dir: Path, config: Dict) -> None:
    """Save all analysis results"""
    # Save visualizations
    cv2.imwrite(str(output_dir / "text_type_detection.png"), visual_result)
    cv2.imwrite(str(output_dir / "clean_visualization.png"), clean_vis)
    
    # Save CSV results
    save_csv_results(printed_cells, handwritten_cells, output_dir)
    
    # Save statistics
    save_statistics(stats, output_dir)
    
    # Save analysis report
    save_analysis_report(printed_cells, handwritten_cells, stats, output_dir, config)

def save_text_region(idx: int, text_region: np.ndarray, x: int, y: int, w: int, h: int, 
                    original_img: np.ndarray, thresh: np.ndarray, text_regions_dir: Path) -> None:
    """
    Save the text region images
    
    Args:
        idx: Region identifier
        text_region: Original text region image
        x, y: Top-left coordinates
        w, h: Width and height of region
        original_img: Original image
        thresh: Thresholded image
        text_regions_dir: Directory to save images
    """
    cv2.imwrite(str(text_regions_dir / f"text_region_{idx}_original.png"), text_region)
    preprocessed_region = thresh[y:y+h, x:x+w]
    cv2.imwrite(str(text_regions_dir / f"text_region_{idx}_preprocessed.png"), preprocessed_region)

def get_confidence_dict(detection: Dict) -> Dict[str, float]:
    """Extract confidence values from detection results"""
    return {
        "ocr_confidence": detection["ocr_confidence"],
        "uniformity_confidence": detection["uniformity_confidence"],
        "stroke_width_confidence": detection["stroke_width_confidence"],
        "overall_confidence": detection["overall_confidence"]
    }

def update_visualizations(cell: TextCell, visual_result: np.ndarray, config: Dict, debug_visualization: bool = True) -> None:
    """Update visualizations with new cell information"""
    # Skip visualizations if debugging is disabled
    if not debug_visualization:
        return
        
    color = config['visualization']['printed_color'] if cell.is_printed else config['visualization']['handwritten_color']
    cv2.rectangle(visual_result, (cell.x, cell.y), (cell.x + cell.width, cell.y + cell.height), color, config['visualization']['rect_thickness'])
    cv2.putText(visual_result, f"#{cell.id}", (cell.x + config['visualization']['text_offset'][0], cell.y + config['visualization']['text_offset'][1]), 
                cv2.FONT_HERSHEY_SIMPLEX, config['visualization']['font_scale'], (255, 255, 255), 2)
    cv2.putText(visual_result, f"#{cell.id}", (cell.x + config['visualization']['text_offset'][0], cell.y + config['visualization']['text_offset'][1]), 
                cv2.FONT_HERSHEY_SIMPLEX, config['visualization']['font_scale'], (0, 0, 0), 1)

def save_csv_results(printed_cells: List[TextCell], handwritten_cells: List[TextCell], output_dir: Path) -> None:
    """Save detailed results to a CSV file"""
    csv_path = output_dir / "text_analysis_results.csv"
    with open(csv_path, 'w', encoding='utf-8') as csv_file:
        csv_file.write("Cell,X,Y,Width,Height,Orientation,Text_Type,OCR_Confidence,Uniformity,Stroke_Width,Overall_Confidence,Has_Text,Text\n")
        
        # Sort all cells by position
        all_cells = sorted(
            printed_cells + handwritten_cells,
            key=lambda c: (c.y, c.x)
        )
        
        for cell in all_cells:
            text_type = "PRINTED" if cell.is_printed else "HANDWRITTEN"
            has_text = "YES" if cell.text.strip() else "NO"
            csv_file.write(
                f"{cell.id},{cell.x},{cell.y},{cell.width},{cell.height},"
                f"{cell.orientation.upper()},{text_type},"
                f"{cell.confidence['ocr_confidence']:.2f},"
                f"{cell.confidence['uniformity_confidence']:.2f},"
                f"{cell.confidence['stroke_width_confidence']:.2f},"
                f"{cell.confidence['overall_confidence']:.2f},"
                f"{has_text},\"{cell.text}\"\n"
            )

def save_statistics(stats: AnalysisStats, output_dir: Path) -> None:
    """Save statistics to a file"""
    stats_path = output_dir / "statistics.txt"
    with open(stats_path, 'w', encoding='utf-8') as stats_file:
        stats_file.write("TEXT DETECTION STATISTICS\n")
        stats_file.write("="*30 + "\n")
        stats_file.write(f"Horizontal printed text cells: {stats.horizontal_printed}\n")
        stats_file.write(f"Horizontal handwritten text cells: {stats.horizontal_handwritten}\n")
        stats_file.write(f"Vertical printed text cells: {stats.vertical_printed}\n")
        stats_file.write(f"Vertical handwritten text cells: {stats.vertical_handwritten}\n")
        stats_file.write(f"Unknown orientation cells: {stats.unknown}\n")
        stats_file.write(f"Total cells with text: {sum(vars(stats).values())}\n")

def write_header_section(report) -> None:
    """Write the header section of the report"""
    report.write("TABLE STRUCTURE ANALYSIS\n")
    report.write("="*30 + "\n\n")
    
def write_statistics_section(report, stats: AnalysisStats) -> None:
    """Write the statistics section of the report"""
    report.write("TEXT DETECTION STATISTICS\n")
    report.write("="*30 + "\n")
    report.write(f"Horizontal printed text cells: {stats.horizontal_printed}\n")
    report.write(f"Horizontal handwritten text cells: {stats.horizontal_handwritten}\n")
    report.write(f"Vertical printed text cells: {stats.vertical_printed}\n")
    report.write(f"Vertical handwritten text cells: {stats.vertical_handwritten}\n")
    report.write(f"Unknown orientation cells: {stats.unknown}\n")
    report.write(f"Total cells with text: {sum(vars(stats).values())}\n")

def write_table_structure_section(report, printed_cells: List[TextCell], handwritten_cells: List[TextCell], config: Dict) -> None:
    """Write the table structure section of the report"""
    row_groups = analyze_table_structure(printed_cells, handwritten_cells, config)
    
    if printed_cells:
        report.write("Potential table headers (printed text):\n")
        for cell in printed_cells:
            report.write(f"  Cell #{cell.id}: '{cell.text}' ({cell.orientation})\n")
    
    if handwritten_cells:
        report.write("\nHandwritten entries:\n")
        for cell in handwritten_cells:
            report.write(f"  Cell #{cell.id}: '{cell.text}' ({cell.orientation})\n")
    
    report.write("\nTable Structure (grouped by rows):\n")
    for row_idx, row in enumerate(row_groups):
        report.write(f"\nRow {row_idx+1}:\n")
        for cell in row:
            cell_type = "PRINTED" if cell in printed_cells else "HANDWRITTEN"
            report.write(f"  Cell #{cell.id}: '{cell.text}' ({cell.orientation}, {cell_type})\n")

def create_visualizations(printed_cells: List[TextCell], handwritten_cells: List[TextCell], 
                         visual_result: np.ndarray, clean_vis: np.ndarray, 
                         config: Dict, debug_visualization: bool = True) -> None:
    """Create visualizations for analysis results and update clean_vis"""
    # Skip if debugging is disabled
    if not debug_visualization:
        return
    
    # Create clean visualization
    for cell in printed_cells + handwritten_cells:
        cell_color = (0, 200, 0) if cell.is_printed else (200, 0, 0)  # Green/Red
        cv2.rectangle(clean_vis, (cell.x, cell.y), (cell.x + cell.width, cell.y + cell.height), 
                     cell_color, config['visualization']['rect_thickness'])
        cv2.putText(clean_vis, f"#{cell.id}", (cell.x + config['visualization']['text_offset'][0], 
                                             cell.y + config['visualization']['text_offset'][1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, config['visualization']['font_scale'], (0, 0, 0), 1)
        
        orientation_marker = "H" if cell.orientation == "horizontal" else "V" if cell.orientation == "vertical" else "?"
        cv2.putText(clean_vis, orientation_marker, (cell.x + cell.width - 20, cell.y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, config['visualization']['font_scale'], (0, 0, 0), 1)

def detect_text_type(text_region: np.ndarray, config: Dict, validation_rules: Optional[Dict] = None) -> Dict[str, Any]:
    """Enhanced text detection with validation rules"""
    result = get_default_detection_result()
    
    # Early return for invalid input
    if text_region is None or text_region.size == 0:
        return result
    
    # Get text orientation and normalize image
    orientation = detect_text_orientation(text_region, config)
    working_image = rotate_to_horizontal(text_region, orientation)
    
    # Perform OCR analysis with validation rules
    ocr_result = analyze_ocr(working_image, None, config)  # Pass None as existing_text
    text = ocr_result['text']
    ocr_confidence = ocr_result['confidence']
    
    # Apply validation rules after OCR
    if validation_rules:
        validation_config = validation_rules.get('validation_config', {})
        
        # Increase confidence for known header positions
        if not validation_rules.get('parent'):  # Top-level header
            result['is_printed_overall'] = True
            result['uniformity_confidence'] = 90.0
        
        # Adjust OCR settings based on type
        if validation_config.get('type') == 'number':
            # Re-run OCR with number-specific settings
            ocr_result = analyze_ocr(working_image, text, config, whitelist='0123456789')
            text = ocr_result['text']
            ocr_confidence = ocr_result['confidence']
        elif 'regex-tick-space' in validation_rules.get('validation_classes', []):
            # Re-run OCR for tick marks
            ocr_result = analyze_ocr(working_image, text, config, whitelist='√ ')
            text = ocr_result['text']
            ocr_confidence = ocr_result['confidence']
    
    is_printed_ocr = ocr_confidence > config['text_detection']['ocr']['confidence_threshold']
    
    # Prepare grayscale image for other analyses
    gray = ensure_grayscale(working_image)
    
    # Analyze text uniformity
    uniformity_result = analyze_uniformity(gray, config)
    uniformity_confidence = uniformity_result['confidence']
    is_printed_uniformity = uniformity_confidence > config['text_detection']['uniformity']['confidence_threshold']
    
    # Analyze stroke width
    stroke_result = analyze_stroke_width(gray, config)
    stroke_confidence = stroke_result['confidence']
    is_printed_stroke = stroke_result['ratio'] < config['text_detection']['stroke']['ratio_threshold']
    
    # Calculate overall confidence
    weights = config['text_detection']['weights']
    overall_confidence = (
        ocr_confidence * weights['ocr'] +
        uniformity_confidence * weights['uniformity'] +
        stroke_confidence * weights['stroke']
    )
    
    is_printed_overall = overall_confidence > config['text_detection']['overall_threshold']
    
    return {
        "orientation": orientation,
        "ocr_confidence": ocr_confidence,
        "uniformity_confidence": uniformity_confidence,
        "stroke_width_confidence": stroke_confidence,
        "is_printed_ocr": is_printed_ocr,
        "is_printed_uniformity": is_printed_uniformity,
        "is_printed_stroke": is_printed_stroke,
        "overall_confidence": overall_confidence,
        "is_printed_overall": is_printed_overall,
        "text": text
    }

def analyze_ocr(image: np.ndarray, existing_text: Optional[str] = None, config: Dict = None, whitelist: Optional[str] = None) -> Dict[str, Any]:
    """Analyze text using OCR with improved configuration options"""
    try:
        # Ensure image is in grayscale
        gray = ensure_grayscale(image)
        
        # Apply thresholding to improve OCR
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Configure OCR
        ocr_config = config['text_detection']['ocr']
        config_parts = [
            f'--psm {ocr_config["psm"]}',
            f'--oem {ocr_config["oem"]}'
        ]
        
        # Add whitelist if specified
        if whitelist:
            config_parts.append(f'-c tessedit_char_whitelist={whitelist}')
        
        custom_config = ' '.join(config_parts)
        
        # Perform OCR
        if existing_text is None:
            text = pytesseract.image_to_string(
                thresh,
                lang=ocr_config['lang'],
                config=custom_config
            )
        else:
            text = existing_text
        
        # Get detailed OCR data
        ocr_data = pytesseract.image_to_data(
            thresh,
            lang=ocr_config['lang'],
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        # Calculate confidence
        valid_confs = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
        confidence = sum(valid_confs) / len(valid_confs) if valid_confs else 0
        
        return {
            'text': ' '.join(text.split()),  # Clean up whitespace
            'confidence': max(0, confidence)  # Ensure non-negative confidence
        }
        
    except Exception as e:
        print(f"OCR error: {e}")
        return {
            'text': existing_text if existing_text else '',
            'confidence': 0.0
        }

def analyze_uniformity(gray_image: np.ndarray, config: Dict) -> Dict[str, float]:
    """Improved text uniformity analysis"""
    _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Return early if not enough contours
    if len(contours) < config['text_detection']['uniformity']['min_contours']:
        return {'confidence': 0.0}
    
    # Filter out noise
    min_area = gray_image.size * 0.0001  # 0.01% of image size
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
    
    if not contours:
        return {'confidence': 0.0}
    
    # Calculate statistics
    heights = [cv2.boundingRect(cnt)[3] for cnt in contours]
    widths = [cv2.boundingRect(cnt)[2] for cnt in contours]
    
    # Use coefficient of variation instead of variance
    height_cv = np.std(heights) / np.mean(heights) if np.mean(heights) > 0 else 1
    width_cv = np.std(widths) / np.mean(widths) if np.mean(widths) > 0 else 1
    
    # Convert to confidence score (0-100)
    uniformity = 100 * (1 - min(1, (height_cv + width_cv) / 2))
    return {'confidence': max(0, uniformity)}

def analyze_stroke_width(gray_image: np.ndarray, config: Dict) -> Dict[str, float]:
    """Analyze stroke width consistency"""
    stroke_config = config['text_detection']['stroke']
    
    edges = cv2.Canny(
        gray_image, 
        stroke_config['canny']['low'],
        stroke_config['canny']['high']
    )
    
    kernel = np.ones(stroke_config['kernel_size'], np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=stroke_config['dilate_iterations'])
    
    ratio = np.sum(dilated) / np.sum(edges) if np.sum(edges) > 0 else 0
    confidence = max(0, min(100, (stroke_config['max_ratio'] - ratio) * 100))
    
    return {
        'confidence': confidence,
        'ratio': ratio
    }

def get_default_detection_result() -> Dict[str, Any]:
    """Default result for empty or invalid cells"""
    return {
        "orientation": "unknown",
        "ocr_confidence": 0,
        "uniformity_confidence": 0,
        "stroke_width_confidence": 0,
        "is_printed_ocr": False,
        "is_printed_uniformity": False,
        "is_printed_stroke": False,
        "overall_confidence": 0,
        "is_printed_overall": False,
        "text": "",
        "empty": True  # New flag to indicate empty cells
    }

def detect_text_orientation(text_region: np.ndarray, config: Dict) -> str:
    """Improved text orientation detection"""
    if text_region is None or text_region.size == 0:
        return "unknown"
    
    height, width = text_region.shape[:2]
    aspect_ratio = width / height if height > 0 else 0
    
    # Strong aspect ratio indication
    if aspect_ratio > 2.0:
        return "horizontal"
    elif aspect_ratio < 0.5:
        return "vertical"
    
    # For less clear cases, use OCR confidence in both orientations
    horizontal_conf = get_ocr_confidence(text_region, config)
    
    # Try vertical orientation
    rotated = cv2.rotate(text_region, cv2.ROTATE_90_COUNTERCLOCKWISE)
    vertical_conf = get_ocr_confidence(rotated, config)
    
    # Use a minimum confidence threshold
    min_conf_threshold = 20
    if max(horizontal_conf, vertical_conf) < min_conf_threshold:
        # If neither orientation has good confidence, use aspect ratio
        return "horizontal" if aspect_ratio >= 1 else "vertical"
    
    # Return orientation with higher confidence
    return "horizontal" if horizontal_conf >= vertical_conf else "vertical"

def rotate_to_horizontal(text_region: np.ndarray, orientation: str) -> np.ndarray:
    """
    Rotate text to horizontal orientation if needed.
    """
    if orientation != "vertical":
        return text_region
    
    # Rotate 90 degrees clockwise
    rotated = cv2.transpose(text_region)
    rotated = cv2.flip(rotated, 1)
    
    return rotated

def ensure_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Ensure image is in grayscale format
    """
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def get_ocr_confidence(image: np.ndarray, config: Dict) -> float:
    """
    Get OCR confidence score for an image
    
    Args:
        image: Input image to analyze
        config: Configuration dictionary
        
    Returns:
        float: OCR confidence score (0-100)
    """
    try:
        # Ensure image is in grayscale
        gray = ensure_grayscale(image)
        
        # Apply thresholding to improve OCR
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Configure OCR
        ocr_config = config['text_detection']['ocr']
        custom_config = f'--psm {ocr_config["psm"]} --oem {ocr_config["oem"]}'
        
        # Get OCR data
        ocr_data = pytesseract.image_to_data(
            thresh,
            lang=ocr_config['lang'],
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        # Filter valid confidences
        confidences = [
            float(conf) 
            for conf in ocr_data['conf'] 
            if conf != '-1' and float(conf) > 0
        ]
        
        # Return average confidence or 0 if no valid confidences
        return sum(confidences) / len(confidences) if confidences else 0.0
        
    except Exception as e:
        print(f"OCR confidence calculation error: {e}")
        return 0.0

def build_header_lookup(header_structure: Dict) -> Dict[str, Dict]:
    """Build lookup of header validation rules by position"""
    lookup = {}
    
    if not header_structure:
        return lookup
    
    def process_header(header: Dict, parent_text: Optional[str] = None):
        # Create position key
        pos_key = f"{header['row_index']},{header['col_index']}"
        
        # Store validation info
        lookup[pos_key] = {
            'text': header['text'],
            'data_id': header['data_id'],
            'parent': parent_text,
            'validation_config': header.get('validation_config', {}),
            'validation_classes': header.get('validation_classes', []),
            'colspan': header.get('colspan', 1),
            'rowspan': header.get('rowspan', 1)
        }
        
        # Process children
        for child in header.get('children', []):
            process_header(child, header['text'])
    
    # Process all headers
    for header in header_structure.get('headers', []):
        process_header(header)
        
    return lookup

def get_cell_validation_rules(cell: TextCell, header_lookup: Dict) -> Optional[Dict]:
    """Get validation rules for a cell based on its position"""
    if not header_lookup:
        return None
        
    pos_key = f"{cell.y//30},{cell.x//30}"  # Approximate grid position
    return header_lookup.get(pos_key)

def update_ocr_config(cell: TextCell, validation_rules: Dict, config: Dict) -> None:
    """Update OCR configuration based on validation rules"""
    if not validation_rules:
        return
        
    validation_config = validation_rules.get('validation_config', {})
    
    # Update OCR settings based on validation type
    if validation_config.get('type') == 'number':
        config['text_detection']['ocr'].update({
            'psm': 7,  # Treat as single line
            'pattern': validation_config.get('pattern', '^[0-9]+$'),
            'whitelist': '0123456789'
        })
    elif 'regex-tick-space' in validation_rules.get('validation_classes', []):
        config['text_detection']['ocr'].update({
            'psm': 10,  # Treat as single character
            'pattern': '^[\u221a ]$',
            'whitelist': '\u221a '
        })
    elif 'regex-gender' in validation_rules.get('validation_classes', []):
        config['text_detection']['ocr'].update({
            'psm': 10,
            'pattern': '^[BG]$',
            'whitelist': 'BG'
        })

def validate_cell_text(text: str, config: Dict) -> Dict:
    """Validate cell text against configuration rules"""
    import re
    
    result = {
        'valid': True,
        'errors': []
    }
    
    if not text and config.get('required') == 'true':
        result['valid'] = False
        result['errors'].append('Required field is empty')
        return result
        
    if not text:
        return result
        
    # Pattern validation
    if pattern := config.get('pattern'):
        if not re.match(pattern, text):
            result['valid'] = False
            result['errors'].append(f'Text does not match pattern: {pattern}')
    
    # Range validation for numbers
    if config.get('type') == 'number' and text.isdigit():
        number = int(text)
        if range_str := config.get('range'):
            min_val, max_val = map(int, range_str.split('-'))
            if not min_val <= number <= max_val:
                result['valid'] = False
                result['errors'].append(f'Number not in range {min_val}-{max_val}')
    
    return result