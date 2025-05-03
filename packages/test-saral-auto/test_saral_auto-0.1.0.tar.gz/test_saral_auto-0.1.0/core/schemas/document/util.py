import inspect
import os
from importlib import import_module
from typing import List, Annotated, Dict, Tuple, Sequence

import numpy as np
import requests
from pydantic import BaseModel
import json

from core.schemas.document.polygon import PolygonBox
from core.schemas.document.settings import settings
from core.schemas.document.document import Document
from core.schemas.document import BlockTypes
# Import math utility functions from the math_utils module
from core.schemas.document.math_utils import matrix_intersection_area, matrix_distance, sort_text_lines


def strings_to_classes(items: List[str]) -> List[type]:
    classes = []
    for item in items:
        module_name, class_name = item.rsplit('.', 1)
        module = import_module(module_name)
        classes.append(getattr(module, class_name))
    return classes


def classes_to_strings(items: List[type]) -> List[str]:
    for item in items:
        if not inspect.isclass(item):
            raise ValueError(f"Item {item} is not a class")

    return [f"{item.__module__}.{item.__name__}" for item in items]


def verify_config_keys(obj):
    annotations = inspect.get_annotations(obj.__class__)

    none_vals = ""
    for attr_name, annotation in annotations.items():
        if isinstance(annotation, type(Annotated[str, ""])):
            value = getattr(obj, attr_name)
            if value is None:
                none_vals += f"{attr_name}, "

    assert len(none_vals) == 0, f"In order to use {obj.__class__.__name__}, you must set the configuration values `{none_vals}`."


def assign_config(cls, config: BaseModel | dict | None):
    cls_name = cls.__class__.__name__
    if config is None:
        return
    elif isinstance(config, BaseModel):
        dict_config = config.dict()
    elif isinstance(config, dict):
        dict_config = config
    else:
        raise ValueError("config must be a dict or a pydantic BaseModel")

    for k in dict_config:
        if hasattr(cls, k):
            setattr(cls, k, dict_config[k])
    for k in dict_config:
        if cls_name not in k:
            continue
        # Enables using class-specific keys, like "MarkdownRenderer_remove_blocks"
        split_k = k.removeprefix(cls_name + "_")

        if hasattr(cls, split_k):
            setattr(cls, split_k, dict_config[k])


def parse_range_str(range_str: str) -> List[int]:
    range_lst = range_str.split(",")
    page_lst = []
    for i in range_lst:
        if "-" in i:
            start, end = i.split("-")
            page_lst += list(range(int(start), int(end) + 1))
        else:
            page_lst.append(int(i))
    page_lst = sorted(list(set(page_lst)))  # Deduplicate page numbers and sort in order
    return page_lst


def download_font():
    if not os.path.exists(settings.FONT_PATH):
        os.makedirs(os.path.dirname(settings.FONT_PATH), exist_ok=True)
        font_dl_path = f"{settings.ARTIFACT_URL}/{settings.FONT_NAME}"
        with requests.get(font_dl_path, stream=True) as r, open(settings.FONT_PATH, 'wb') as f:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def validate_document(document: Document) -> Tuple[bool, List[str]]:
    """
    Validate a Document object against the schema.
    
    Args:
        document: The Document object to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check basic required fields
    if not document.filepath:
        errors.append("Document missing filepath")
    
    if not document.pages:
        errors.append("Document has no pages")
        return False, errors
    
    # Validate each page
    for i, page in enumerate(document.pages):
        if page.page_id != i:
            errors.append(f"Page {i} has incorrect page_id: {page.page_id}")
        
        if not page.structure:
            errors.append(f"Page {i} has no structure")
            continue
            
        # Validate blocks on the page
        for block_id in page.structure:
            block = page.get_block(block_id)
            if not block:
                errors.append(f"Page {i} references non-existent block: {block_id}")
                continue
                
            if block.page_id != page.page_id:
                errors.append(f"Block {block_id} has incorrect page_id: {block.page_id}")
                
            if block.block_id != block_id.block_id:
                errors.append(f"Block {block_id} has incorrect block_id: {block.block_id}")
                
    # Return validation result
    return len(errors) == 0, errors


def save_document_to_json(document: Document, output_path: str) -> None:
    """
    Save document to a simplified JSON format.
    
    Args:
        document: The document to save
        output_path: The path to save the document to
    """
    # Convert document to a serializable dictionary
    doc_dict = {
        "filepath": document.filepath,
        "page_count": len(document.pages),
        "pages": []
    }
    
    # Process each page
    for page in document.pages:
        page_dict = {
            "page_id": page.page_id,
            "blocks": []
        }
        
        # Process each block in the page
        for block_id in page.structure:
            block = page.get_block(block_id)
            
            # Common block properties
            block_dict = {
                "block_id": block.block_id,
                "block_type": str(block.block_type),
                "position": {
                    "polygon": block.polygon.polygon
                }
            }
            
            # Add type-specific properties
            if block.block_type == BlockTypes.Text:
                # Get text content
                text_content = block.raw_text(document) if hasattr(block, "raw_text") else ""
                
                # Check if this is a text block converted from ROI by examining the block description
                if "from ROI:" in block.block_description:
                    # Extract ROI properties from the block description
                    import re
                    
                    # Extract text size
                    text_size = None
                    size_match = re.search(r'size=(\d+\.?\d*)', block.block_description)
                    if size_match:
                        try:
                            text_size = float(size_match.group(1))
                        except ValueError:
                            pass
                    
                    # Extract bold state
                    is_bold = False
                    bold_match = re.search(r'bold=(True|False)', block.block_description)
                    if bold_match:
                        is_bold = bold_match.group(1) == "True"
                    
                    # Extract bold ratio
                    bold_ratio = 0.0
                    ratio_match = re.search(r'boldRatio=(\d+\.?\d*)', block.block_description)
                    if ratio_match:
                        try:
                            bold_ratio = float(ratio_match.group(1))
                        except ValueError:
                            pass
                    
                    # This text block came from an ROI, so include the extracted ROI properties
                    block_dict.update({
                        "text": text_content,
                        "textSize": text_size,
                        "isBold": is_bold,
                        "boldRatio": bold_ratio
                    })
                else:
                    # Regular text block
                    block_dict.update({
                        "text": text_content
                    })
            
            page_dict["blocks"].append(block_dict)
        
        doc_dict["pages"].append(page_dict)
    
    # Save to JSON file
    with open(output_path, "w") as f:
        json.dump(doc_dict, f, indent=2)