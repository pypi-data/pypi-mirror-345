"""
Utility functions for debugging and visualization.
"""

import os
import cv2
import json
import numpy as np
from typing import Dict, List, Optional, Callable
import logging

# Configure logger
logger = logging.getLogger(__name__)

class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles NumPy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

def save_to_json(data, file_path):
    """
    Save data to a JSON file
    
    Args:
        data: Data to save
        file_path: Path to the output file
        
    Returns:
        str: Path to the saved file
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, cls=NumpyEncoder)
    
    return file_path

def save_debug_image(img, filename, output_dir):
    """
    Save a debug image to the processed directory
    
    Args:
        img: Image to save
        filename: Name of the file
        output_dir: Output directory path
    """
    output_path = os.path.join(output_dir, filename)
    cv2.imwrite(output_path, img)
    print(f"Saved: {filename}")

def save_debug_text(data, filename, output_dir):
    """
    Save debug text to the processed directory
    
    Args:
        data: Text data to save
        filename: Name of the file
        output_dir: Output directory path
    """
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"Saved: {filename}")

def save_dict_to_file(data: Dict, file_path: str) -> None:
    """
    Save dictionary data to a file.
    
    Args:
        data: Dictionary data to save
        file_path: Path to save the file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                json.dump(data, f, indent=2)
            else:
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")
    except Exception as e:
        logger.error(f"Error saving dictionary to file {file_path}: {str(e)}")

def save_list_to_file(data: List, output_path: str, format_fn: Optional[Callable] = None) -> None:
    """
    Save list data to a file.
    
    Args:
        data: List data to save
        output_path: Path to save the file
        format_fn: Optional formatting function for each item
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            if output_path.endswith('.json'):
                json.dump(data, f, indent=2)
            else:
                for item in data:
                    if format_fn:
                        f.write(format_fn(item) + "\n")
                    else:
                        f.write(str(item) + "\n")
    except Exception as e:
        logger.error(f"Error saving list to file {output_path}: {str(e)}") 