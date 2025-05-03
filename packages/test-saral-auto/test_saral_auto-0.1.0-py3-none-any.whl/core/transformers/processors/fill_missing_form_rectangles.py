import os
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

from core.transformers.processors import BaseProcessor
from core.schemas.document.document import Document
from core.transformers.fill.fill import fill_and_find_missing_rectangles

import logging

# Configure logging
logger = logging.getLogger(__name__)

class FillMissingFormRectanglesProcessor(BaseProcessor):
    """
    Processor for filling missing rectangles in form documents.
    Analyzes patterns in detected rectangles and adds missing ones based on alignment.
    Enhanced with checkpointing and error handling.
    """
    
    def __init__(self, config: Dict[str, Any] = None, output_dir: str = None, checkpoint_dir: str = None):
        """
        Initialize the fill missing rectangles processor.
        
        Args:
            config: Configuration dictionary for the processor
            output_dir: Directory to save debug outputs
            checkpoint_dir: Directory to store checkpoint data
        """
        super().__init__(config or {}, checkpoint_dir=checkpoint_dir)
        self.output_dir = output_dir
        self.debug_mode = self.config.get('debug_mode', False)
        
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            
        # Store initialization checkpoint
        self._checkpoint("init", {
            "output_dir": output_dir,
            "debug_mode": self.debug_mode
        })
    
    def _apply_checkpoint_to_document(self, document: Document) -> Document:
        """
        Apply checkpoint data to document when resuming.
        
        Args:
            document: The document to apply checkpoint data to
            
        Returns:
            Document: The updated document with checkpoint data applied
        """
        if 'result' not in self._checkpoint_data:
            return document
            
        result_data = self._checkpoint_data['result']
        
        # Apply the filled rectangles data to each page from the checkpoint
        for i, page in enumerate(document.pages):
            if not hasattr(page, 'metadata') or page.metadata is None:
                page.__dict__['metadata'] = {}
                
            page_data = result_data.get(f'page_{i}', {})
            if page_data:
                page.__dict__['metadata']['rect_roi_count'] = page_data.get('rect_roi_count', 0)
                
                # If we have a result image, load it
                result_image_path = page_data.get('result_image_path')
                if result_image_path and os.path.exists(result_image_path):
                    page.__dict__['metadata']['result_image'] = cv2.imread(result_image_path)
        
        return document
    
    def __call__(self, document: Document) -> Document:
        """
        Apply filling missing rectangles to each page in the document.
        Enhanced with checkpointing, caching and error handling.
        
        Args:
            document: Input document with detected rectangles
            
        Returns:
            Document: Document with filled rectangles
        """
        try:
            # Check for cached result
            cached_result = self._get_cache(document)
            if cached_result:
                logger.info("Using cached result for FillMissingFormRectanglesProcessor")
                return cached_result
            
            # Check if we have a completed checkpoint
            if 'completed' in self._checkpoint_data and self._checkpoint_data['completed']:
                logger.info("Resuming from completed checkpoint")
                return self._apply_checkpoint_to_document(document)
                
            logger.info("Applying fill missing rectangles processor")
            
            # Create result data structure to store checkpoints
            result_data = {}
            
            for i, page in enumerate(document.pages):
                # Check if we have a checkpoint for this page
                page_key = f"page_{i}"
                page_checkpoint = self.get_checkpoint(page_key)
                
                if page_checkpoint:
                    logger.info(f"Resuming processing from checkpoint for page {i}")
                    # Apply page checkpoint data
                    if not hasattr(page, 'metadata') or page.metadata is None:
                        page.__dict__['metadata'] = {}
                        
                    page.__dict__['metadata']['rect_roi_count'] = page_checkpoint.get('rect_roi_count', 0)
                    
                    # If we have a result image path, load it
                    result_image_path = page_checkpoint.get('result_image_path')
                    if result_image_path and os.path.exists(result_image_path):
                        page.__dict__['metadata']['result_image'] = cv2.imread(result_image_path)
                        
                    # Store in result data for final checkpoint
                    result_data[page_key] = page_checkpoint
                    continue
                
                # Get the necessary data from page metadata
                if not hasattr(page, 'metadata') or page.metadata is None:
                    logger.warning(f"No metadata found for page {i}")
                    continue
                    
                try:
                    metadata = page.__dict__['metadata']
                    original_image = metadata.get('original_image')
                    contours = metadata.get('rectangle_contours')
                    mean_area = metadata.get('mean_rectangle_area')
                    
                    if original_image is None or contours is None or mean_area is None:
                        logger.warning(f"Missing required data for page {i}")
                        continue
                    
                    # Store pre-processing checkpoint
                    self._checkpoint(f"page_{i}_pre", {
                        "contour_count": len(contours),
                        "mean_area": mean_area
                    })
                    
                    # Fill missing rectangles
                    result_img, rect_count, rect_rois = fill_and_find_missing_rectangles(
                        original_image, contours, mean_area, output_dir=self.output_dir)
                    
                    # Save result image and store path for checkpoint
                    result_image_path = None
                    if self.debug_mode and self.output_dir:
                        result_image_path = os.path.join(self.output_dir, f"page_{i}_filled_rectangles.png")
                        cv2.imwrite(result_image_path, result_img)
                    
                    # Update page metadata
                    metadata.update({
                        'result_image': result_img,
                        'rect_roi_count': rect_count,
                        'rect_rois': rect_rois
                    })
                    
                    # Store page checkpoint
                    page_data = {
                        'rect_roi_count': rect_count,
                        'result_image_path': result_image_path
                    }
                    
                    self._checkpoint(page_key, page_data)
                    result_data[page_key] = page_data
                    
                    logger.info(f"Filled missing rectangles on page {i}, total count: {rect_count}")
                except Exception as e:
                    logger.error(f"Error processing page {i}: {str(e)}")
                    # Continue with the next page
            
            # Mark processing as completed and store final result
            self._mark_completed(result_data)
            
            # Cache the result
            self._set_cache(document, document)
            
            return document
        except Exception as e:
            logger.error(f"Error in FillMissingFormRectanglesProcessor: {str(e)}")
            # Return the document unchanged in case of error
            return document