"""
Utility functions for working with ROI schemas and JSON files.
"""

import json
from typing import List, Union, Dict, Any, Optional
import os
from pathlib import Path

from core.schemas.roi.roi import ROI, ROIList
from core.schemas.roi.cell import Cell, CellList

def load_roi_json(file_path: Union[str, Path]) -> ROIList:
    """
    Load ROIs from a JSON file and validate against the schema.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        ROIList object with validated ROIs
    """
    with open(file_path, 'r') as f:
        roi_data = json.load(f)
    
    # If the data is already a list of ROIs
    if isinstance(roi_data, list):
        return ROIList.from_list(roi_data)
    
    # If the data has a specific format with ROIs under a key
    if isinstance(roi_data, dict):
        if 'rois' in roi_data:
            return ROIList(**roi_data)
        # If it's a mapped_cells format
        elif 'mapped_cells' in roi_data:
            return convert_mapped_cells_to_rois(roi_data['mapped_cells'])
    
    raise ValueError(f"Invalid ROI JSON format in {file_path}")

def convert_mapped_cells_to_rois(mapped_cells: List[Dict[str, Any]]) -> ROIList:
    """
    Convert mapped cells data to ROI schema format.
    
    Args:
        mapped_cells: List of mapped cell dictionaries
        
    Returns:
        ROIList with converted cells
    """
    rois = []
    for cell in mapped_cells:
        # Extract position information
        position = cell.get("position", {})
        x = position.get("x", 0)
        y = position.get("y", 0)
        width = position.get("width", 0)
        height = position.get("height", 0)
        
        # Extract text and other properties
        text = cell.get("detected_text", "")
        is_header = cell.get("is_header", False)
        confidence = cell.get("confidence", None)
        
        # Create ROI with available fields
        roi = ROI(
            left=x,
            top=y,
            right=x + width,
            bottom=y + height,
            text=text,
            textSize=16 if is_header else 14,  # Default size
            isBold=is_header,
            boldRatio=0.1 if is_header else 0.3,  # Default bold ratio
            confidence=confidence,
            type="header" if is_header else "field",
            group_id=cell.get("parent_header", None)
        )
        rois.append(roi)
    
    return ROIList(rois=rois)

def save_roi_json(rois: Union[ROIList, List[ROI], List[Dict[str, Any]]], file_path: Union[str, Path]) -> None:
    """
    Save ROIs to a JSON file.
    
    Args:
        rois: ROI data (either ROIList, List[ROI], or List[Dict])
        file_path: Path to save the JSON file
    """
    # Convert to list of dictionaries for serialization
    if isinstance(rois, ROIList):
        roi_list = [roi.to_dict() for roi in rois.rois]
    elif isinstance(rois, list):
        if all(isinstance(roi, ROI) for roi in rois):
            roi_list = [roi.to_dict() for roi in rois]
        else:
            # Assume it's already a list of dictionaries
            roi_list = rois
    else:
        raise TypeError(f"Expected ROIList or List[ROI], got {type(rois)}")
    
    with open(file_path, 'w') as f:
        json.dump(roi_list, f, indent=4)

def validate_roi_json(file_path: Union[str, Path]) -> bool:
    """
    Validate that a JSON file conforms to the ROI schema.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        True if valid, raises exception if invalid
    """
    try:
        load_roi_json(file_path)
        return True
    except Exception as e:
        raise ValueError(f"Invalid ROI JSON: {str(e)}")

def load_cell_json(file_path: Union[str, Path]) -> CellList:
    """
    Load cell data from a JSON file and validate against the schema.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        CellList object with validated cells
    """
    with open(file_path, 'r') as f:
        cell_data = json.load(f)
    
    # If the data is already a list of cells
    if isinstance(cell_data, list):
        return CellList.from_list(cell_data)
    
    # If the data has cells under a key
    if isinstance(cell_data, dict) and 'cells' in cell_data:
        return CellList(**cell_data)
    
    raise ValueError(f"Invalid cell JSON format in {file_path}")

def save_cell_json(cells: Union[CellList, List[Cell], List[Dict[str, Any]]], file_path: Union[str, Path]) -> None:
    """
    Save cells to a JSON file.
    
    Args:
        cells: Cell data (either CellList, List[Cell], or List[Dict])
        file_path: Path to save the JSON file
    """
    # Convert to list of dictionaries for serialization
    if isinstance(cells, CellList):
        cell_list = [cell.to_dict() for cell in cells.cells]
    elif isinstance(cells, list):
        if all(isinstance(cell, Cell) for cell in cells):
            cell_list = [cell.to_dict() for cell in cells]
        else:
            # Assume it's already a list of dictionaries
            cell_list = cells
    else:
        raise TypeError(f"Expected CellList or List[Cell], got {type(cells)}")
    
    with open(file_path, 'w') as f:
        json.dump(cell_list, f, indent=4)

def convert_cells_to_rois(cells: CellList) -> ROIList:
    """
    Convert a CellList to an ROIList.
    
    Args:
        cells: CellList to convert
        
    Returns:
        ROIList with converted cells
    """
    rois = []
    for cell in cells.cells:
        roi = ROI(
            left=cell.x,
            top=cell.y,
            right=cell.x + cell.width,
            bottom=cell.y + cell.height,
            text=cell.text,
            textSize=16 if cell.metadata.is_header else 14,  # Default size
            isBold=cell.metadata.is_header,
            boldRatio=0.1 if cell.metadata.is_header else 0.3,  # Default bold ratio
            confidence=cell.confidence.get("text", None),
            type="header" if cell.metadata.is_header else "field",
            group_id=cell.metadata.group_id
        )
        rois.append(roi)
    
    return ROIList(rois=rois) 