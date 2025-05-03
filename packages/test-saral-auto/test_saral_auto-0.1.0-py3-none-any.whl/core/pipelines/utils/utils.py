"""
Utility functions for document processing and serialization.
"""
import os
import logging
import json
import numpy as np
from typing import Any, Dict, List, Union, Optional

logger = logging.getLogger(__name__)


def ensure_directory(path: str) -> str:
    """
    Ensure the directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        str: The directory path
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


def numpy_to_list(obj: Any) -> Any:
    """
    Recursively convert numpy arrays and types to Python standard types.
    
    Args:
        obj: Object that may contain numpy arrays
        
    Returns:
        Object with numpy types converted to standard Python types
    """
    # Handle None
    if obj is None:
        return None
        
    # Handle numpy arrays
    if isinstance(obj, np.ndarray):
        return obj.tolist()
        
    # Handle numpy scalar types
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, 
                       np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    if isinstance(obj, (np.float64, np.float16, np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.bool_, np.bool)):
        return bool(obj)
    if isinstance(obj, np.complex128):
        return {'real': obj.real, 'imag': obj.imag}
        
    # Recursively handle containers
    if isinstance(obj, dict):
        return {k: numpy_to_list(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [numpy_to_list(i) for i in obj]
        
    # Handle objects with conversion methods
    if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
        try:
            return numpy_to_list(obj.to_dict())
        except Exception as e:
            logger.warning(f"Failed to use to_dict method: {str(e)}")
            
    if hasattr(obj, 'model_dump') and callable(getattr(obj, 'model_dump')):
        try:
            return numpy_to_list(obj.model_dump())
        except Exception as e:
            logger.warning(f"Failed to use model_dump method: {str(e)}")
            
    if hasattr(obj, 'tolist') and callable(getattr(obj, 'tolist')):
        try:
            return obj.tolist()
        except Exception as e:
            logger.warning(f"Failed to use tolist method: {str(e)}")
            
    # Return the object as is if no conversion is needed
    return obj


def safe_json_dump(data: Any, file_path: str, indent: int = 2) -> None:
    """
    Safely dump data to a JSON file, handling numpy arrays and other special types.
    
    Args:
        data: Data to dump
        file_path: Path to the output file
        indent: Indentation level
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Convert numpy arrays to lists recursively
    safe_data = numpy_to_list(data)
    
    # Try to write with custom encoder
    try:
        from core.renderers.serializers import DocumentEncoder
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(safe_data, f, indent=indent, ensure_ascii=False, cls=DocumentEncoder)
        return
    except (ImportError, TypeError, ValueError) as e:
        logger.warning(f"Failed to use DocumentEncoder: {str(e)}")
    
    # Fallback to standard dump with a simple default handler
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(safe_data, f, indent=indent, ensure_ascii=False, 
                     default=lambda o: str(o))
        return
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed standard JSON dump: {str(e)}")
    
    # Last resort: convert to string representation
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(str(safe_data), f)
        logger.warning("Serialized data as string due to JSON serialization issues")
    except Exception as e:
        logger.error(f"All JSON serialization attempts failed: {str(e)}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"ERROR: Could not serialize data: {str(e)}")


def extract_table_data(document) -> List[Dict[str, Any]]:
    """
    Extract structured table data from a document.
    
    Args:
        document: The document containing table data
        
    Returns:
        List[Dict]: List of extracted table data
    """
    tables = []
    
    for page in document.pages:
        # Skip pages without metadata
        if not hasattr(page, 'metadata') or page.metadata is None:
            continue
            
        # Get mapped results from page metadata
        metadata_dict = page.__dict__.get('metadata', {})
        if isinstance(metadata_dict, dict):
            mapped_results = metadata_dict.get("mapped_results", {})
        else:
            # Try to access as an attribute
            mapped_results = getattr(page.metadata, "mapped_results", {}) if page.metadata else {}
            
        if not mapped_results:
            continue
            
        # Extract table cells
        cells = mapped_results.get("cells", [])
        
        # Group by headers
        table_data = {}
        headers = []
        
        # Find headers
        for cell in cells:
            if cell.get("is_header", False):
                header_text = cell.get("text", "").strip()
                if header_text:
                    headers.append(header_text)
                    table_data[header_text] = []
        
        # Map data to headers
        for cell in cells:
            if not cell.get("is_header", False):
                header = cell.get("header", "")
                if header in table_data:
                    # Convert any numpy values
                    bbox = numpy_to_list(cell.get("bbox", []))
                    confidence = numpy_to_list(cell.get("confidence", 0))
                    
                    table_data[header].append({
                        "text": cell.get("text", ""),
                        "confidence": confidence,
                        "bbox": bbox
                    })
        
        # Add to tables list
        tables.append({
            "headers": headers,
            "data": numpy_to_list(table_data),
            "metadata": {
                "pattern_coverage": numpy_to_list(mapped_results.get("pattern_coverage", 0)),
                "total_cells": len(cells),
                "header_cells": sum(1 for c in cells if c.get("is_header", False)),
                "data_cells": sum(1 for c in cells if not c.get("is_header", False))
            }
        })
    
    return tables

def extract_form_data(document) -> Dict[str, Any]:
        """
        Extract structured form data from the processed document.
        
        Args:
            document: The processed document
            
        Returns:
            Dict[str, Any]: Extracted form data
        """
        form_data = {}
        
        for page in document.pages:
            # Skip pages without metadata
            if not hasattr(page, 'metadata') or page.metadata is None:
                continue
                
            # Get text ROIs from page metadata
            text_rois = page.__dict__['metadata'].get("text_rois", [])
            
            # Extract form fields
            for roi in text_rois:
                text = roi.get("text", "").strip()
                if not text:
                    continue
                    
                # Try to parse field name and value
                if ":" in text:
                    field_name, field_value = text.split(":", 1)
                    form_data[field_name.strip()] = field_value.strip()
                else:
                    # Just use the text as a field
                    form_data[f"field_{len(form_data)}"] = text
        
        return form_data