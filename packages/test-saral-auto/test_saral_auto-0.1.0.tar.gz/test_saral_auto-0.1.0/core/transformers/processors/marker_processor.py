"""
Processor for processing documents using Marker.
"""

from __future__ import annotations

import os
import json
import base64
import cv2
import numpy as np
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from pydantic import BaseModel

from core.schemas.document import BlockTypes
from core.schemas.document.document import Document
from core.schemas.document.groups.page import PageGroup
from core.schemas.document.blocks import Block, BlockId
from core.schemas.document.blocks.text import Text
from core.schemas.document.blocks.picture import Picture
from core.schemas.document.blocks.table import Table
from core.schemas.document.polygon import PolygonBox

from core.transformers.processors import BaseProcessor
from core.transformers.marker.marker_call import MarkerCall
from core.transformers.marker.marker_to_document import MarkerToDocument
from core.transformers.utils.debug_write import dump_document_with_images

# Configure logger
logger = logging.getLogger(__name__)

def get_file_hash(file_path: Path) -> str:
    """Generate a hash for the file to use as cache key"""
    return hashlib.md5(file_path.read_bytes()).hexdigest()

def convert_image_to_base64(image: np.ndarray) -> str:
    """Convert an OpenCV image to base64 string"""
    # Convert image to bytes
    _, buffer = cv2.imencode('.png', image)
    # Convert to base64 string
    base64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{base64_str}"

class MarkerProcessor(BaseProcessor):
    """
    Processor for processing documents using Marker.
    
    This processor uses MarkerCall to extract structured information from documents
    and populate a Document object with the extracted data.
    """
    
    # Define the block types this processor can handle
    block_types = None  # Can handle any block type
    
    # Default configuration
    debug_mode: bool = True
    output_dir: Optional[str] = None
    enable_caching: bool = True
    cache_dir: str = "cache"
    
    def __init__(self, config: Optional[Union[BaseModel, dict]] = None, output_dir: str = None):
        """
        Initialize the processor.
        
        Args:
            config: Configuration dictionary or BaseModel for the processor
            output_dir: Output directory for debug files
        """
        super().__init__(config)
        
        # Set up output directory
        self.output_dir = output_dir or self.output_dir
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up cache directory
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Get config options
        self.use_api = config.get('use_api', False) if config else False
        if self.use_api:
            from core.transformers.marker.marker_api_call import MarkerAPICall
            self.marker_class = MarkerAPICall
        else:
            from core.transformers.marker.marker_call import MarkerCall
            self.marker_class = MarkerCall
            
        # Initialize marker processor
        self.marker_processor = None
        self.marker_output = None
        
        # Store initialization checkpoint
        self._checkpoint("init", {
            "output_dir": output_dir,
            "use_api": self.use_api
        })
    
    def __call__(self, document: Document, *args, **kwargs) -> Document:
        """
        Process the document using Marker.
        """
        try:
            # Initial checkpoint
            self._checkpoint("processing_start", {
                "timestamp": str(datetime.now())
            })
                
            # Verify filepath
            if not hasattr(document, 'filepath') or not document.filepath:
                raise ValueError("Document has no filepath")
                
            logger.info(f"Processing document: {document.filepath}")
            
            # Get the file path from the document
            file_path = Path(document.filepath)
            
            # Check if file exists
            if not file_path.exists():
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                self._checkpoint("error", {
                    "error": error_msg,
                    "timestamp": str(datetime.now())
                })
                return document
                
            # File loading checkpoint
            self._checkpoint("file_loaded", {
                "file_path": str(file_path),
                "timestamp": str(datetime.now())
            })
            
            # Check cache first
            cache_file = self._get_cache_path(file_path)
            
            if self.enable_caching and cache_file.exists():
                logger.info(f"Loading from cache: {cache_file}")
                
                try:
                    self.marker_output = json.loads(cache_file.read_text())
                    self._checkpoint("loaded_from_cache", {
                        "cache_file": str(cache_file),
                        "timestamp": str(datetime.now())
                    })
                except Exception as e:
                    logger.error(f"Error loading from cache: {str(e)}")
                    # If cache loading fails, proceed with normal processing
                    self.marker_output = None
            
            # If not loaded from cache, use marker
            if self.marker_output is None:
                # Initialize marker processor
                self.marker_processor = self.marker_class(str(file_path))
                
                # Call marker
                logger.info(f"Processing file with marker: {file_path}")
                self.marker_output = self.marker_processor.convert_pdf()
                
                self._checkpoint("marker_call_complete", {
                    "marker_output_keys": list(self.marker_output.keys()) if self.marker_output else [],
                    "timestamp": str(datetime.now())
                })
                
                # Save to cache if enabled
                if self.enable_caching:
                    self._save_to_cache(file_path)
                    self._checkpoint("saved_to_cache", {
                        "cache_file": str(cache_file),
                        "timestamp": str(datetime.now())
                    })
            
            # Save marker output to file
            marker_output_path = os.path.join(self.output_dir, "marker_output.json")
            with open(marker_output_path, 'w', encoding='utf-8') as f:
                json.dump(self.marker_output, f, indent=2, ensure_ascii=False)
            logger.debug(f"Marker output saved to: {marker_output_path}")

            # Update document with marker output
            if self.marker_output:
                m2d = MarkerToDocument(self.marker_output)
                m2d.convert(document)
                self._checkpoint("document_updated", {
                    "page_count": len(document.pages) if document.pages else 0,
                    "timestamp": str(datetime.now())
                })

            # Final checkpoint
            self._mark_completed({
                "success": True,
                "document_updated": True,
                "timestamp": str(datetime.now())
            })

            try:
                debug_output = os.path.join(self.output_dir, "debug_document_after_marker_processor.json")
                logger.debug(f"Saving debug document to: {debug_output}")
                dump_document_with_images(document, debug_output, indent=2, image_folder_name=f"images", image_key_names=("highres_image",))
            except Exception as e:
                logger.error(f"Failed to save debug document: {str(e)}")
            
            return document
            
        except Exception as e:
            # Error checkpoint
            self._checkpoint("error", {
                "error": str(e),
                "stage": "marker_processing",
                "timestamp": str(datetime.now())
            })
            logger.error(f"Error in marker processing: {str(e)}")
            return document
    
    def _get_cache_path(self, file_path: Path) -> Path:
        """Get the cache file path for a given file"""
        file_hash = get_file_hash(file_path)
        return self.cache_dir / f"{file_hash}.json"
    
    def _save_to_cache(self, file_path: Path) -> None:
        """Save the marker output to cache"""
        if not self.marker_output:
            return
            
        cache_file = self._get_cache_path(file_path)
        cache_file.write_text(json.dumps(self.marker_output, indent=2))
        logger.info(f"Saved to cache: {cache_file}")
