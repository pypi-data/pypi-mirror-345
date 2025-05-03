"""
Custom serialization utilities for document models.
Handles special types like numpy arrays for JSON serialization.
"""

import json
import numpy as np
from typing import Any


class DocumentEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles numpy arrays and other special types.
    """
    def default(self, obj: Any) -> Any:
        # Handle numpy types
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, 
                           np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        if isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.bool_, np.bool)):
            return bool(obj)
        if isinstance(obj, np.complex_):
            return {'real': obj.real, 'imag': obj.imag}
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        
        # Handle classes with conversion methods
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return obj.to_dict()
        if hasattr(obj, 'model_dump') and callable(getattr(obj, 'model_dump')):
            return obj.model_dump()
        if hasattr(obj, 'tolist') and callable(getattr(obj, 'tolist')):
            return obj.tolist()
        
        # Last resort: try string conversion
        try:
            return str(obj)
        except:
            return super().default(obj)


def numpy_safe_serialize(obj: Any) -> Any:
    """
    Recursively convert numpy types to standard Python types.
    
    Args:
        obj: Object to convert
        
    Returns:
        Converted object with numpy types replaced by standard Python types
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, 
                       np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    if isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.bool_, np.bool)):
        return bool(obj)
    if isinstance(obj, np.complex_):
        return {'real': obj.real, 'imag': obj.imag}
    if isinstance(obj, (dict, list)):
        return _convert_container(obj)
    
    # Handle pydantic models
    if hasattr(obj, 'model_dump') and callable(getattr(obj, 'model_dump')):
        return obj.model_dump()
    
    return obj


def _convert_container(container):
    """Helper function to convert containers (dict/list) recursively."""
    if isinstance(container, dict):
        return {k: numpy_safe_serialize(v) for k, v in container.items()}
    elif isinstance(container, (list, tuple)):
        return [numpy_safe_serialize(v) for v in container]
    return container


def serialize_document(document) -> dict:
    """
    Serialize a Document object to a JSON-serializable dictionary.
    
    Args:
        document: The Document object to serialize
        
    Returns:
        Dict: JSON-serializable dictionary representation of the document
    """
    # Use the numpy_safe_serialize function to convert all numpy types
    serialized_document = numpy_safe_serialize(document)
    
    # Try to use model_dump if available (for pydantic models)
    if hasattr(document, 'model_dump') and callable(getattr(document, 'model_dump')):
        model_dict = document.model_dump()
        return numpy_safe_serialize(model_dict)
    
    # Otherwise, convert to a simple dict
    if hasattr(document, '__dict__'):
        return numpy_safe_serialize(document.__dict__)
    
    return serialized_document


def serialize_block(block) -> dict:
    """
    Serialize a single Block object to a JSON-serializable dictionary.
    
    Args:
        block: The Block object to serialize
        
    Returns:
        Dict: JSON-serializable dictionary representation of the block
    """
    return numpy_safe_serialize(block)