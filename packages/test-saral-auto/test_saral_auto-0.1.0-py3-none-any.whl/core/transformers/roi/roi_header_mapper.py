from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import numpy as np
import json

@dataclass
class CellMetadata:
    """Enhanced cell metadata with structural information"""
    is_header: bool = False
    row_type: str = "data"  # "header", "data", or "merged"
    row_index: int = 0
    col_index: int = 0
    header_level: int = 0  # Depth in header hierarchy
    parent_header_id: Optional[int] = None
    is_repeating: bool = False
    pattern_group: Optional[str] = None
    confidence: float = 0.0

# Standalone functions extracted from ROIHeaderRowMapper

def convert_to_json_serializable(obj: Dict) -> Dict:
    """Convert NumPy types to Python native types"""
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) 
               for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj

def analyze_structure(roi_results: Dict,
                      header_structure: Optional[Dict] = None,
                      similarity_threshold: float = 0.85,
                      min_pattern_count: int = 3,
                      header_y_threshold: int = 250) -> Dict:
    """
    Analyze ROI results to identify headers and data rows
    
    Args:
        roi_results: Output from ROITextAnalyzer
        header_structure: Optional table structure from parser
        similarity_threshold: Threshold for determining pattern similarity
        min_pattern_count: Minimum count for a pattern to be considered
        header_y_threshold: Y-coordinate threshold for headers
        
    Returns:
        Dict with enhanced ROI information
    """
    try:
        cells = roi_results.get("all_cells", [])
        if not cells:
            return roi_results

        # Sort cells by position
        sorted_cells = sorted(cells, key=lambda c: (c.y, c.x))
        
        # Find row patterns
        row_patterns = identify_row_patterns(sorted_cells, min_pattern_count)
        
        # Group cells into rows
        rows = group_into_rows(sorted_cells)
        
        # Analyze each row
        mapped_cells = []
        for row_idx, row in enumerate(rows):
            # Sort row by x position
            row.sort(key=lambda c: c.x)
            
            # Get row pattern if it exists
            row_pattern = get_row_pattern(row, row_patterns, similarity_threshold)
            
            # Determine if this is a header row
            is_header_row = is_header_row_func(row, header_structure, header_y_threshold)
            
            # Process each cell in the row
            for col_idx, cell in enumerate(row):
                metadata = analyze_cell(
                    cell, row_idx, col_idx,
                    is_header_row, row_pattern,
                    header_structure
                )
                
                mapped_cells.append({
                    "id": cell.id,
                    "text": cell.text,
                    "position": {
                        "x": cell.x,
                        "y": cell.y,
                        "width": cell.width,
                        "height": cell.height
                    },
                    "analysis": {
                        "is_printed": cell.is_printed,
                        "orientation": cell.orientation,
                        "confidence": cell.confidence
                    },
                    "metadata": metadata.__dict__
                })
        
        result = {
            "mapped_cells": mapped_cells,
            "row_patterns": row_patterns,
            "statistics": generate_statistics(mapped_cells)
        }

        # Convert all data to JSON serializable format
        return convert_to_json_serializable(result)

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def identify_row_patterns(cells: List, min_pattern_count: int = 3) -> Dict:
    """
    Identify repeating patterns in rows
    
    Args:
        cells: List of cell objects
        min_pattern_count: Minimum number of occurrences for a pattern to be considered valid
        
    Returns:
        Dictionary of identified patterns
    """
    patterns = {}
    
    # Group cells by y-coordinate (within tolerance)
    y_tolerance = 10
    rows = {}
    
    for cell in cells:
        row_key = cell.y // y_tolerance
        if row_key not in rows:
            rows[row_key] = []
        rows[row_key].append(cell)
    
    # Analyze patterns in each row
    for y, row_cells in rows.items():
        if len(row_cells) < 2:
            continue
            
        # Calculate cell widths and spacing
        widths = [c.width for c in sorted(row_cells, key=lambda x: x.x)]
        spaces = [
            row_cells[i+1].x - (row_cells[i].x + row_cells[i].width)
            for i in range(len(row_cells)-1)
        ]
        
        pattern_key = f"w{'_'.join(map(str, widths))}_s{'_'.join(map(str, spaces))}"
        
        if pattern_key not in patterns:
            patterns[pattern_key] = {
                "count": 0,
                "widths": widths,
                "spaces": spaces,
                "rows": []
            }
        
        patterns[pattern_key]["count"] += 1
        patterns[pattern_key]["rows"].append(y)
    
    # Filter patterns by minimum count
    return {k: v for k, v in patterns.items() 
            if v["count"] >= min_pattern_count}

def group_into_rows(cells: List) -> List[List]:
    """
    Group cells into rows based on y-position
    
    Args:
        cells: List of cell objects
        
    Returns:
        List of rows, where each row is a list of cells
    """
    if not cells:
        return []
        
    rows = []
    current_row = [cells[0]]
    y_tolerance = 10
    
    for cell in cells[1:]:
        if abs(cell.y - current_row[0].y) <= y_tolerance:
            current_row.append(cell)
        else:
            rows.append(current_row)
            current_row = [cell]
    
    if current_row:
        rows.append(current_row)
    
    return rows

def get_row_pattern(row: List, patterns: Dict, similarity_threshold: float = 0.85) -> Optional[str]:
    """
    Find matching pattern for a row
    
    Args:
        row: List of cells in a row
        patterns: Dictionary of identified patterns
        similarity_threshold: Threshold for pattern similarity
        
    Returns:
        Pattern key if found, None otherwise
    """
    if not row or len(row) < 2:
        return None
        
    # Calculate row signature
    widths = [c.width for c in sorted(row, key=lambda x: x.x)]
    spaces = [
        row[i+1].x - (row[i].x + row[i].width)
        for i in range(len(row)-1)
    ]
    
    # Find best matching pattern
    best_match = None
    best_score = 0
    
    for pattern_key, pattern in patterns.items():
        if len(widths) != len(pattern["widths"]):
            continue
            
        # Calculate similarity score
        width_similarity = calculate_sequence_similarity(
            widths, pattern["widths"]
        )
        space_similarity = calculate_sequence_similarity(
            spaces, pattern["spaces"]
        )
        
        score = (width_similarity * 0.6 + space_similarity * 0.4)
        
        if score > best_score and score >= similarity_threshold:
            best_score = score
            best_match = pattern_key
    
    return best_match

def calculate_sequence_similarity(seq1: List[float], seq2: List[float]) -> float:
    """
    Calculate similarity between two sequences of numbers
    
    Args:
        seq1: First sequence
        seq2: Second sequence
        
    Returns:
        Similarity score between 0 and 1
    """
    if len(seq1) != len(seq2):
        return 0.0
        
    differences = [abs(a - b) / max(a, b) for a, b in zip(seq1, seq2)]
    return 1 - (sum(differences) / len(differences))

def is_header_row_func(row: List, header_structure: Optional[Dict], header_y_threshold: int = 250) -> bool:
    """
    Determine if a row is a header row
    
    Args:
        row: List of cells in a row
        header_structure: Optional predefined header structure
        header_y_threshold: Y-coordinate threshold for headers
        
    Returns:
        True if the row is a header row, False otherwise
    """
    if not row:
        return False
        
    # Check position (headers are typically at the top)
    if row[0].y > header_y_threshold:
        return False
        
    # Check if cells are printed
    if not all(cell.is_printed for cell in row):
        return False
        
    # If we have header structure, check against it
    if header_structure:
        header_texts = {h["text"].lower() for h in header_structure.get("headers", [])}
        row_texts = {cell.text.lower() for cell in row}
        
        # If any cell matches known headers
        return bool(header_texts & row_texts)
        
    return True

def analyze_cell(cell: Any, row_idx: int, col_idx: int,
                is_header_row: bool, row_pattern: Optional[str],
                header_structure: Optional[Dict]) -> CellMetadata:
    """
    Analyze a cell to determine its structural role
    
    Args:
        cell: Cell object
        row_idx: Row index
        col_idx: Column index
        is_header_row: Whether the cell is in a header row
        row_pattern: Pattern key for the row
        header_structure: Optional predefined header structure
        
    Returns:
        Cell metadata
    """
    metadata = CellMetadata(
        is_header=is_header_row,
        row_type="header" if is_header_row else "data",
        row_index=row_idx,
        col_index=col_idx,
        pattern_group=row_pattern
    )
    
    # Update confidence based on printed status and position
    base_confidence = cell.confidence.get("overall_confidence", 0)
    if is_header_row:
        base_confidence *= 1.2  # Boost header confidence
    
    metadata.confidence = min(100, base_confidence)
    
    # Set header level and parent if we have structure
    if header_structure and is_header_row:
        update_header_metadata(metadata, cell, header_structure)
    
    # Mark as repeating if part of a pattern
    metadata.is_repeating = bool(row_pattern)
    
    return metadata

def update_header_metadata(metadata: CellMetadata, cell: Any, header_structure: Dict) -> None:
    """
    Update header metadata using structure information
    
    Args:
        metadata: Cell metadata to update
        cell: Cell object
        header_structure: Predefined header structure
    """
    def find_header_info(headers: List, level: int = 0) -> Optional[Dict]:
        for header in headers:
            if header["text"].lower() == cell.text.lower():
                return {"level": level, "id": header.get("id")}
            if "children" in header:
                result = find_header_info(header["children"], level + 1)
                if result:
                    return result
        return None
    
    if header_info := find_header_info(header_structure.get("headers", [])):
        metadata.header_level = header_info["level"]
        metadata.parent_header_id = header_info["id"]

def generate_statistics(mapped_cells: List[Dict]) -> Dict:
    """
    Generate statistics about the mapping
    
    Args:
        mapped_cells: List of mapped cell dictionaries
        
    Returns:
        Dictionary with statistics
    """
    total_cells = len(mapped_cells)
    header_cells = sum(1 for c in mapped_cells if c["metadata"]["is_header"])
    repeating_cells = sum(1 for c in mapped_cells if c["metadata"]["is_repeating"])
    
    return {
        "total_cells": total_cells,
        "header_cells": header_cells,
        "repeating_cells": repeating_cells,
        "data_cells": total_cells - header_cells,
        "pattern_coverage": repeating_cells / total_cells if total_cells > 0 else 0
    }

# Keep a simple wrapper class for backward compatibility if needed
class ROIHeaderRowMapper:
    """Maps ROIs to header/row structure using pattern recognition"""
    
    def __init__(self, 
                 similarity_threshold: float = 0.85,
                 min_pattern_count: int = 3,
                 header_y_threshold: int = 250):
        self.similarity_threshold = similarity_threshold
        self.min_pattern_count = min_pattern_count
        self.header_y_threshold = header_y_threshold
        self.pattern_cache = {}
    
    def analyze_structure(self, 
                         roi_results: Dict,
                         header_structure: Optional[Dict] = None) -> Dict:
        """
        Legacy wrapper around the standalone analyze_structure function
        """
        return analyze_structure(
            roi_results=roi_results,
            header_structure=header_structure,
            similarity_threshold=self.similarity_threshold,
            min_pattern_count=self.min_pattern_count, 
            header_y_threshold=self.header_y_threshold
        )