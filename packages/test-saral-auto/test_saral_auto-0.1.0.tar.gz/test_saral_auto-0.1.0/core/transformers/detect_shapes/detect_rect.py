import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from pathlib import Path
import os

# Create the folder if it doesn't exist
output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "processed")
output_dir = os.path.abspath(output_dir)

# Default configuration for rectangle detection
DEFAULT_CONFIG = {
    # Preprocessing parameters
    'gaussian_kernel': (5, 5),
    'gaussian_sigma': 0,
    
    # Line detection parameters
    'horizontal_kernel_size': (40, 1),
    'vertical_kernel_size': (1, 10),
    'morph_iterations': 3,
    
    # Rectangle detection parameters
    'epsilon_factor': 0.04,
    'min_rect_vertices': 4,
    'max_rect_vertices': 4,
    
    # Area thresholds
    'min_area_factor': 0.0005,  # 0.05% of image area
    'max_area_factor': 0.5,     # 50% of image area
    'area_similarity_factor': 0.2,
    
    # Rectangle filtering
    'min_aspect_ratio': 0.1,
    'max_aspect_ratio': 10.0,
    'area_group_tolerance': 0.2,  # 20% tolerance for grouping similar areas
    'min_group_size': 3,         # Minimum rectangles to consider a common size
    'min_area_adjustment': 0.5,   # Factor to adjust min_area for common sizes
    
    # Concentric rectangle filtering
    'overlap_threshold': 0.7,
    'center_distance_threshold': 15,
    
    # Visualization parameters
    'valid_contour_color': (0, 255, 0),    # Green
    'invalid_contour_color': (0, 0, 255),   # Red
    'original_contour_color': (255, 0, 0),  # Blue
    'text_color': (0, 0, 255),             # Red
    'line_thickness': {
        'valid': 2,
        'invalid': 1,
        'text': 1
    },
    'font': {
        'face': cv2.FONT_HERSHEY_SIMPLEX,
        'scale': 0.5,
        'thickness': 1
    },
    'text_offset': (-10, 5)  # (x, y) offset for contour numbering
}
            
def detect_rectangles(img: np.ndarray, config: Optional[Dict[str, Any]] = None,
                     debug_mode: bool = False, output_dir: Optional[Path] = None) -> Tuple[List[np.ndarray], float, np.ndarray]:
    """
    Main detection method for rectangles in an image
    
    Args:
        img: Input image to process
        config: Configuration dictionary for detection parameters
        debug_mode: Whether to save debug images
        output_dir: Directory to save debug images
        
    Returns:
        Tuple containing filtered contours, mean area, and result image
    """
    if img is None:
        raise ValueError("Input image cannot be None")
    if len(img.shape) != 3:
        raise ValueError("Input image must be a color image (3 channels)")
    
    # Use default config if none provided
    if config is None:
        config = DEFAULT_CONFIG
    
    # Initialize state
    original_img = img
    result_img = img.copy()
    
    # Process the image through each step
    preprocessed = preprocess_image(original_img, config)
    edges, detect_horizontal, detect_vertical = detect_lines(preprocessed, config)
    contours = find_contours(edges, original_img)
    filtered_contours, invalid_rectangles, mean_area = filter_rectangles(contours, original_img, config)
    filtered_contours = filter_concentric(filtered_contours, original_img, config)
    result_img = draw_results(original_img, filtered_contours, invalid_rectangles, mean_area, config)
    
    # Save debug images
    if debug_mode and output_dir:
        output_dir.mkdir(exist_ok=True)
        cv2.imwrite(os.path.join(output_dir, "edges_from_horizontal_and_vertical_lines.png"), edges)
        cv2.imwrite(os.path.join(output_dir, "horizontal_and_vertical_lines.png"), 
                   cv2.bitwise_or(detect_horizontal, detect_vertical))
        cv2.imwrite(os.path.join(output_dir, "concentric_rectangle_filtering.png"), result_img)
        
        # Save invalid rectangles info
        with open(os.path.join(output_dir, "invalid_rectangle.txt"), "w") as f:
            for rect in invalid_rectangles:
                f.write(f"{rect}\n")
    
    return filtered_contours, mean_area, result_img
    
def preprocess_image(img: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
    """
    Preprocess the image with grayscale and blur
    
    Args:
        img: Original image
        config: Configuration parameters
        
    Returns:
        Preprocessed image
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(
        gray, 
        config['gaussian_kernel'], 
        config['gaussian_sigma']
    )
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    return thresh
        
def detect_lines(preprocessed: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Detect horizontal and vertical lines
    
    Args:
        preprocessed: Preprocessed image
        config: Configuration parameters
        
    Returns:
        Tuple containing edges, horizontal lines, vertical lines
    """
    # Horizontal lines
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, config['horizontal_kernel_size'])
    detect_horizontal = cv2.morphologyEx(preprocessed, cv2.MORPH_OPEN, h_kernel, iterations=config['morph_iterations'])
    
    # Vertical lines
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, config['vertical_kernel_size'])
    detect_vertical = cv2.morphologyEx(preprocessed, cv2.MORPH_OPEN, v_kernel, iterations=config['morph_iterations'])
    
    # Combine lines
    edges = cv2.bitwise_or(detect_horizontal, detect_vertical)
    
    return edges, detect_horizontal, detect_vertical
        
def find_contours(edges: np.ndarray, original_img: np.ndarray) -> List[np.ndarray]:
    """
    Find contours in the edge image
    
    Args:
        edges: Edge image
        original_img: Original image for visualization
        
    Returns:
        List of contours
    """
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    return contours
        
def filter_rectangles(contours: List[np.ndarray], original_img: np.ndarray, 
                     config: Dict[str, Any]) -> Tuple[List[np.ndarray], List[np.ndarray], float]:
    """
    Filter rectangles based on area and aspect ratio
    
    Args:
        contours: List of contours
        original_img: Original image
        config: Configuration parameters
        
    Returns:
        Tuple containing filtered contours, invalid rectangles, mean area
    """
    img_area = original_img.shape[0] * original_img.shape[1]
    min_area = img_area * config['min_area_factor']
    max_area = img_area * config['max_area_factor']
    
    # First pass to collect areas
    areas = []
    for cnt in contours:
        epsilon = config['epsilon_factor'] * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        if len(approx) == config['min_rect_vertices']:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            areas.append(area)
    
    # Analyze area distribution with configured tolerance
    area_groups = {}
    if areas:
        for a in areas:
            found_group = False
            for group_key in area_groups:
                lower_bound = group_key * (1 - config['area_group_tolerance'])
                upper_bound = group_key * (1 + config['area_group_tolerance'])
                if lower_bound <= a <= upper_bound:
                    area_groups[group_key].append(a)
                    found_group = True
                    break
            if not found_group:
                area_groups[a] = [a]
        
        # Find most common rectangle size
        if area_groups:
            most_common_group = max(area_groups.items(), key=lambda x: len(x[1]))
            if len(most_common_group[1]) > config['min_group_size']:
                common_area = most_common_group[0]
                min_area = common_area * config['min_area_adjustment']
    
    # Second pass to filter contours
    filtered_contours = []
    invalid_rectangles = []
    
    for cnt in contours:
        epsilon = config['epsilon_factor'] * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        if len(approx) == config['min_rect_vertices']:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            aspect_ratio = float(w) / h if h != 0 else float('inf')
            
            # Check if rectangle meets criteria
            if (min_area < area < max_area and 
                config['min_aspect_ratio'] < aspect_ratio < config['max_aspect_ratio']):
                filtered_contours.append(cnt)
            else:
                invalid_rectangles.append(cnt)
        else:
            # Handle non-rectangular contours
            contour_array = np.array(cnt)
            is_valid, _, rect_area = analyze_invalid_rectangle(contour_array, config)
            
            if is_valid and min_area < rect_area < max_area:
                filtered_contours.append(cnt)
            else:
                invalid_rectangles.append(cnt)
    
    # Calculate mean area of filtered contours
    mean_area = 0
    if filtered_contours:
        areas = [cv2.contourArea(cnt) for cnt in filtered_contours]
        mean_area = np.mean(areas)
    
    return filtered_contours, invalid_rectangles, mean_area

def get_rejection_reason(area: float, aspect_ratio: float, 
                        min_area: float, max_area: float, config: Dict[str, Any]) -> str:
    """
    Helper method to determine why a rectangle was rejected
    
    Args:
        area: Rectangle area
        aspect_ratio: Rectangle aspect ratio
        min_area: Minimum area threshold
        max_area: Maximum area threshold
        config: Configuration parameters
        
    Returns:
        Reason for rejection
    """
    if area < min_area:
        return f"Area too small: {area:.2f} < {min_area:.2f}"
    if area > max_area:
        return f"Area too large: {area:.2f} > {max_area:.2f}"
    if aspect_ratio < config['min_aspect_ratio']:
        return f"Aspect ratio too small: {aspect_ratio:.2f}"
    if aspect_ratio > config['max_aspect_ratio']:
        return f"Aspect ratio too large: {aspect_ratio:.2f}"
    return "Unknown reason"

def analyze_invalid_rectangle(contour_array: np.ndarray, config: Dict[str, Any]) -> Tuple[bool, np.ndarray, float]:
    """
    Analyze a non-rectangular contour to see if it can be approximated as a rectangle
    
    Args:
        contour_array: Contour points array
        config: Configuration parameters
        
    Returns:
        Tuple containing validity flag, box points, and rectangle area
    """
    rect = cv2.minAreaRect(contour_array)
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    rect_area = cv2.contourArea(box)
    
    # Check if the contour is close enough to a rectangle
    contour_area = cv2.contourArea(contour_array)
    
    if rect_area == 0:
        return False, box, rect_area
    
    area_similarity = abs(rect_area - contour_area) / rect_area
    
    return area_similarity < config['area_similarity_factor'], box, rect_area

def filter_concentric(filtered_contours: List[np.ndarray], original_img: np.ndarray, 
                     config: Dict[str, Any]) -> List[np.ndarray]:
    """
    Filter out concentric rectangles, keeping the one with the median area in each group
    
    Args:
        filtered_contours: List of filtered contours
        original_img: Original image
        config: Configuration parameters
        
    Returns:
        Filtered list of contours
    """
    # Store original contours for visualization
    original_contours = filtered_contours.copy()
    
    # Get bounding rectangles and centers for all contours
    bounding_rects = []
    centers = []
    areas = []
    
    for cnt in filtered_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        bounding_rects.append((x, y, w, h))
        centers.append((x + w/2, y + h/2))
        areas.append(w * h)
    
    # Create a list to mark contours to keep
    keep = [True] * len(filtered_contours)
    
    # Group concentric rectangles
    groups = []
    for i in range(len(filtered_contours)):
        if not keep[i]:
            continue
            
        current_group = [i]
        x1, y1, w1, h1 = bounding_rects[i]
        cx1, cy1 = centers[i]
        area1 = areas[i]
        
        for j in range(i+1, len(filtered_contours)):
            if not keep[j]:
                continue
                
            x2, y2, w2, h2 = bounding_rects[j]
            cx2, cy2 = centers[j]
            area2 = areas[j]
            
            # Calculate center distance
            center_distance = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
            
            # Calculate overlap area
            x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
            y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
            overlap_area = x_overlap * y_overlap
            
            # Calculate overlap ratio relative to the smaller rectangle
            smaller_area = min(area1, area2)
            overlap_ratio = overlap_area / smaller_area if smaller_area > 0 else 0
            
            # If rectangles are concentric
            if (center_distance < config['center_distance_threshold'] and 
                overlap_ratio > config['overlap_threshold']):
                current_group.append(j)
                keep[j] = False
        
        if len(current_group) > 1:
            groups.append(current_group)
            # Mark the original rectangle as not to keep, we'll add back the best one
            keep[i] = False
    
    # Create new filtered contours list
    new_filtered_contours = []
    
    # Add non-grouped contours
    for i in range(len(filtered_contours)):
        if keep[i]:
            new_filtered_contours.append(filtered_contours[i])
    
    # For each group, add back the contour with the median area
    for group in groups:
        group_areas = [areas[i] for i in group]
        # Find the index of the median area in the group
        median_area_idx = group[np.argsort(group_areas)[len(group_areas)//2]]
        new_filtered_contours.append(filtered_contours[median_area_idx])
    
    return new_filtered_contours
            
def draw_results(original_img: np.ndarray, filtered_contours: List[np.ndarray], 
                invalid_rectangles: List[np.ndarray], mean_area: float, 
                config: Dict[str, Any]) -> np.ndarray:
    """
    Draw the final results on the image
    
    Args:
        original_img: Original image
        filtered_contours: List of filtered contours
        invalid_rectangles: List of invalid rectangles
        mean_area: Mean area of filtered contours
        config: Configuration parameters
        
    Returns:
        Result image with visualization
    """
    result = original_img.copy()
    
    # Draw valid rectangles
    cv2.drawContours(
        result, 
        filtered_contours, 
        -1, 
        config['valid_contour_color'], 
        config['line_thickness']['valid']
    )
    
    # Draw invalid rectangles
    cv2.drawContours(
        result, 
        invalid_rectangles, 
        -1, 
        config['invalid_contour_color'], 
        config['line_thickness']['invalid']
    )
    
    return result