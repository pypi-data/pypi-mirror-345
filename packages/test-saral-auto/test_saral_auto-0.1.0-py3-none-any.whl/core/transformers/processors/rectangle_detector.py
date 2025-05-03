import os
import cv2
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel

from core.schemas.document import BlockTypes
from core.schemas.document.document import Document
from core.schemas.document.polygon import PolygonBox
from core.schemas.document.blocks.table import Table

from core.transformers.processors import BaseProcessor
from core.transformers.utils.debug_utils import save_debug_image
from core.transformers.detect_shapes.detect_rect import (
    detect_rectangles,
    DEFAULT_CONFIG
)

# Configure logger
logger = logging.getLogger(__name__)

class RectangleDetectorProcessor(BaseProcessor):
    """
    Processor for detecting rectangles in documents.
    """
    
    block_types = (BlockTypes.Table,)
    debug_mode: bool = True
    output_dir: Optional[str] = None
    rectangle_filter: Dict[str, Any] = {
        "min_width": 20,
        "min_height": 20,
        "max_width_ratio": 0.8,
        "max_height_ratio": 0.3
    }
    
    def __init__(self, config: Optional[BaseModel | dict] = None, output_dir: str = None):
        """
        Initialize the processor.
        
        Args:
            config: Configuration dictionary or BaseModel for the processor
            output_dir: Output directory for debug files
        """
        super().__init__(config)
        self.output_dir = output_dir
        self.output_path = Path(output_dir) if output_dir else None
        
        # Use the default detection config with any overrides from provided config
        self.detection_config = DEFAULT_CONFIG.copy()
        if config and isinstance(config, dict) and 'detection_config' in config:
            self.detection_config.update(config['detection_config'])
        
        # Store initialization checkpoint
        self._checkpoint("init", {"output_dir": output_dir})
    
    def __call__(self, document: Document, *args, **kwargs) -> Document:
        """
        Detect rectangles in the document.
        
        Args:
            document: The document to process
            
        Returns:
            Document: The updated document
        """
        try:
            # Initial checkpoint
            self._checkpoint("processing_start", {
                "timestamp": str(datetime.now()),
                "document_pages": len(document.pages)
            })

            logger.info("Detecting rectangles...")
            
            # Get the first page
            page = document.pages[0]
            
            # Pre-processing checkpoint
            self._checkpoint("pre_processing", {
                "has_metadata": hasattr(page, 'metadata'),
                "page_index": 0
            })
            
            # Make sure page has a metadata dictionary
            if not hasattr(page, 'metadata') or page.metadata is None:
                page.__dict__['metadata'] = {}
                self._checkpoint("metadata_initialized", {
                    "timestamp": str(datetime.now())
                })
            
            # Get the image from page metadata
            img = page.__dict__['metadata'].get("original_image")
            if img is None:
                self._checkpoint("error", {
                    "error": "Missing original image",
                    "timestamp": str(datetime.now())
                })
                return document
            
            # Image loading checkpoint
            self._checkpoint("image_loaded", {
                "image_shape": img.shape,
                "timestamp": str(datetime.now())
            })
            
            # Detect rectangles using the standalone function
            contours, mean_area, result = detect_rectangles(
                img, 
                config=self.detection_config,
                debug_mode=self.debug_mode,
                output_dir=self.output_path
            )
            
            # Detection checkpoint
            self._checkpoint("detection_complete", {
                "contours_count": len(contours),
                "mean_area": mean_area,
                "timestamp": str(datetime.now())
            })
            
            # Save debug image
            debug_path = None
            if self.output_dir:
                debug_path = os.path.join(self.output_dir, "table_detection_result.png")
                save_debug_image(result, "table_detection_result.png", self.output_dir)
                self._checkpoint("debug_image_saved", {
                    "debug_path": debug_path,
                    "timestamp": str(datetime.now())
                })
            
            # Log results
            logger.info(f"Found {len(contours)} rectangles")
            logger.info(f"Mean area: {mean_area:.2f}")
            
            # Store detection checkpoint
            self._checkpoint("detection", {
                "contours_count": len(contours), 
                "mean_area": mean_area
            })
            
            # Filter contours checkpoint
            self._checkpoint("filter_start", {
                "initial_contours": len(contours),
                "filter_config": self.rectangle_filter,
                "timestamp": str(datetime.now())
            })
            
            # Filter contours by size
            filtered_contours = []
            
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                # Filter based on config values
                if (w > self.rectangle_filter["min_width"] and 
                    h > self.rectangle_filter["min_height"] and 
                    w < img.shape[1] * self.rectangle_filter["max_width_ratio"] and 
                    h < img.shape[0] * self.rectangle_filter["max_height_ratio"]):
                    filtered_contours.append(cnt)
            
            # Post-filtering checkpoint
            self._checkpoint("filter_complete", {
                "filtered_count": len(filtered_contours),
                "timestamp": str(datetime.now())
            })
            
            logger.info(f"After filtering: {len(filtered_contours)} rectangles")
            
            # Store the filtered contours in the page metadata
            page.__dict__['metadata']["contours"] = filtered_contours
            page.__dict__['metadata']["mean_area"] = mean_area
            
            # Metadata update checkpoint
            self._checkpoint("metadata_update", {
                "contours_stored": len(filtered_contours),
                "mean_area": mean_area,
                "timestamp": str(datetime.now())
            })
            
            # Create the table block
            table_polygon = PolygonBox.from_bbox([0, 0, img.shape[1], img.shape[0]])
            table_block = page.add_block(
                Table,
                table_polygon
            )
            table_block.block_description = "Table detected from rectangles"
            
            # Table creation checkpoint
            self._checkpoint("table_created", {
                "table_bounds": [0, 0, img.shape[1], img.shape[0]],
                "timestamp": str(datetime.now())
            })
            
            # Save the table block to page structure
            page.add_structure(table_block)
            
            # Store the actual table block in page metadata for direct access
            page.__dict__['metadata']["table_block"] = table_block
            
            # Store final checkpoint
            self._checkpoint("completion", {
                "filtered_contours": len(filtered_contours),
                "table_block_added": True,
                "debug_image_path": debug_path,
                "timestamp": str(datetime.now())
            })
            
            return document
            
        except Exception as e:
            # Error checkpoint
            self._checkpoint("error", {
                "error": str(e),
                "stage": "rectangle_detection",
                "timestamp": str(datetime.now())
            })
            logger.error(f"Error in rectangle detection: {str(e)}")
            return document
