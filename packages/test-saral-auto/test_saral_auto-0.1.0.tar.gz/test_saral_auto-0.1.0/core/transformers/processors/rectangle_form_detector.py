import os
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime

from core.transformers.processors import BaseProcessor
from core.schemas.document.document import Document
from core.transformers.detect_shapes.detect_shapes import detect_and_filter_rectangles
import logging

logger = logging.getLogger(__name__)

class RectangleFormDetectorProcessor(BaseProcessor):
    """
    Processor for detecting and filtering rectangles in form documents.
    """
    
    def __init__(self, config: Dict[str, Any] = None, output_dir: str = None):
        """Initialize the rectangle detector processor."""
        super().__init__(config or {})
        self.config = config or {}
        self.output_dir = output_dir
        self.debug_mode = self.config.get('debug_mode', False)
        
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)

        # Initialize checkpoint
        self._checkpoint("init", {
            "output_dir": output_dir,
            "debug_mode": self.debug_mode,
            "timestamp": str(datetime.now())
        })
    
    def __call__(self, document: Document) -> Document:
        """Apply rectangle detection with checkpointing."""
        try:
            # Start processing checkpoint
            self._checkpoint("processing_start", {
                "total_pages": len(document.pages),
                "timestamp": str(datetime.now())
            })

            logger.info("Applying rectangle form detection")
            
            for i, page in enumerate(document.pages):
                try:
                    # Page processing start checkpoint
                    self._checkpoint(f"page_{i}_start", {
                        "status": "processing",
                        "page_number": i,
                        "timestamp": str(datetime.now())
                    })

                    # Get the original image from page metadata
                    if not hasattr(page, 'metadata') or page.metadata is None:
                        logger.warning(f"No metadata found for page {i}")
                        self._checkpoint(f"page_{i}_error", {
                            "error": "No metadata found",
                            "page_number": i,
                            "timestamp": str(datetime.now())
                        })
                        continue
                        
                    original_image = page.__dict__['metadata'].get('original_image')
                    if original_image is None:
                        logger.warning(f"No original image found for page {i}")
                        self._checkpoint(f"page_{i}_error", {
                            "error": "Missing original image",
                            "page_number": i,
                            "timestamp": str(datetime.now())
                        })
                        continue

                    # Image loading checkpoint
                    self._checkpoint(f"page_{i}_image_loaded", {
                        "image_shape": original_image.shape,
                        "timestamp": str(datetime.now())
                    })
                    
                    # Detect and filter rectangles
                    contours, mean_area, result_img = detect_and_filter_rectangles(original_image)
                    
                    # Detection checkpoint
                    self._checkpoint(f"page_{i}_detection", {
                        "contours_count": len(contours),
                        "mean_area": mean_area,
                        "timestamp": str(datetime.now())
                    })
                    
                    # Update page metadata
                    page.__dict__['metadata'].update({
                        'rectangle_contours': contours,
                        'mean_rectangle_area': mean_area,
                        'result_image': result_img,
                        'rect_roi_count': 0  # Will be updated by later processors
                    })
                    
                    # Metadata update checkpoint
                    self._checkpoint(f"page_{i}_metadata_update", {
                        "metadata_keys": list(page.__dict__['metadata'].keys()),
                        "timestamp": str(datetime.now())
                    })
                    
                    # Save debug image
                    debug_path = None
                    if self.debug_mode and self.output_dir:
                        debug_path = os.path.join(self.output_dir, f"page_{i}_rectangles.png")
                        cv2.imwrite(debug_path, result_img)
                        self._checkpoint(f"page_{i}_debug_saved", {
                            "debug_path": debug_path,
                            "timestamp": str(datetime.now())
                        })
                        
                    logger.info(f"Detected {len(contours)} rectangles on page {i}")
                    
                    # Page completion checkpoint
                    self._checkpoint(f"page_{i}_complete", {
                        "status": "success",
                        "rectangles_detected": len(contours),
                        "debug_image": debug_path,
                        "timestamp": str(datetime.now())
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing page {i}: {str(e)}")
                    self._checkpoint(f"page_{i}_error", {
                        "error": str(e),
                        "page_number": i,
                        "timestamp": str(datetime.now())
                    })
                    continue

            # Final completion checkpoint
            self._checkpoint("processing_complete", {
                "status": "completed",
                "total_pages_processed": len(document.pages),
                "timestamp": str(datetime.now())
            })
            
            return document
            
        except Exception as e:
            logger.error(f"Error in rectangle detection: {str(e)}")
            self._checkpoint("processing_error", {
                "error": str(e),
                "timestamp": str(datetime.now())
            })
            return document