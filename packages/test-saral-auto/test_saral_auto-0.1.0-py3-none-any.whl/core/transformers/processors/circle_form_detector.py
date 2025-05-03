import os
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

from core.transformers.detect_shapes.detect_shapes import detect_and_filter_circles
from core.transformers.fill.fill import fill_circles

from core.transformers.processors import BaseProcessor
from core.schemas.document.document import Document
import logging

logger = logging.getLogger(__name__)

class CircleFormDetectorProcessor(BaseProcessor):
    """
    Processor for detecting and filtering circles in form documents.
    Enhanced with checkpointing for resumable execution and better error handling.
    """
    
    def __init__(self, config: Dict[str, Any] = None, output_dir: str = None, checkpoint_dir: str = None):
        """
        Initialize the circle detector processor.
        
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
        
        # Apply the circles data to each page from the checkpoint
        for i, page in enumerate(document.pages):
            if not hasattr(page, 'metadata') or page.metadata is None:
                page.__dict__['metadata'] = {}
                
            page_data = result_data.get(f'page_{i}', {})
            if page_data:
                # Apply circle data from checkpoint
                page.__dict__['metadata']['circles'] = page_data.get('circles', [])
                page.__dict__['metadata']['circle_left_text_rois'] = page_data.get('circle_left_text_rois', [])
                page.__dict__['metadata']['circle_count'] = page_data.get('circle_count', 0)
                
                # If we have a result image, load it
                result_image_path = page_data.get('result_image_path')
                if result_image_path and os.path.exists(result_image_path):
                    page.__dict__['metadata']['result_image'] = cv2.imread(result_image_path)
        
        return document
    
    def __call__(self, document: Document) -> Document:
        """
        Apply circle detection to each page in the document.
        Enhanced with checkpointing, caching and error handling.
        
        Args:
            document: Input document with rectangles already detected
            
        Returns:
            Document: Document with detected circles and their ROIs
        """
        try:
            # Check for cached result - with better error handling
            try:
                cached_result = self._get_cache(document)
                if cached_result:
                    logger.info("Using cached result for CircleFormDetectorProcessor")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache access failed: {str(e)}. Continuing with processing.")
            
            # Check if we have a completed checkpoint
            if 'completed' in self._checkpoint_data and self._checkpoint_data['completed']:
                logger.info("Resuming from completed checkpoint")
                return self._apply_checkpoint_to_document(document)
            
            logger.info("Applying circle form detection")
            
            # Create result data structure to store checkpoints
            result_data = {}
            
            for i, page in enumerate(document.pages):
                try:
                    # Check if we have a checkpoint for this page
                    page_key = f"page_{i}"
                    page_checkpoint = self.get_checkpoint(page_key)
                    
                    if page_checkpoint:
                        logger.info(f"Resuming processing from checkpoint for page {i}")
                        # Apply page checkpoint data
                        if not hasattr(page, 'metadata') or page.metadata is None:
                            page.__dict__['metadata'] = {}
                            
                        page.__dict__['metadata']['circles'] = page_checkpoint.get('circles', [])
                        page.__dict__['metadata']['circle_left_text_rois'] = page_checkpoint.get('circle_left_text_rois', [])
                        page.__dict__['metadata']['circle_count'] = page_checkpoint.get('circle_count', 0)
                        
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
                        
                    original_image = page.__dict__['metadata'].get('original_image')
                    result_image = page.__dict__['metadata'].get('result_image')
                    rect_count = page.__dict__['metadata'].get('rect_roi_count', 0)
                    
                    if original_image is None or result_image is None:
                        logger.warning(f"Missing required data for page {i}")
                        continue
                        
                    # Store pre-processing checkpoint
                    self._checkpoint(f"page_{i}_pre", {
                        "rect_count": rect_count
                    })
                    
                    # Detect and filter circles
                    circles, detect_result_img = detect_and_filter_circles(original_image, rect_count)
    
                    if self.debug_mode and self.output_dir:
                        debug_path = os.path.join(self.output_dir, f"page_{i}_circles_detected.png")
                        cv2.imwrite(debug_path, detect_result_img)
                        logger.debug(f"Detected {len(circles)} circles, saved to {debug_path}")
                        
                    # Store intermediate checkpoint
                    self._checkpoint(f"page_{i}_circles", {
                        "circle_count": len(circles)
                    })
                    
                    # Fill circles and create ROIs
                    circle_left_text_rois, fill_result_img = fill_circles(result_image, circles, rect_count, self.output_dir)
    
                    # Save result image and store path for checkpoint
                    result_image_path = None
                    if self.debug_mode and self.output_dir:
                        result_image_path = os.path.join(self.output_dir, f"page_{i}_circles.png")
                        cv2.imwrite(result_image_path, fill_result_img)
                        logger.debug(f"Created {len(circle_left_text_rois)} ROIs left to circles")
                    
                    # Update page metadata
                    page.__dict__['metadata'].update({
                        'circles': circles,
                        'circle_left_text_rois': circle_left_text_rois,
                        'result_image': fill_result_img,
                        'circle_count': len(circles)
                    })
                    
                    # Store page checkpoint
                    page_data = {
                        'circles': circles,
                        'circle_left_text_rois': circle_left_text_rois,
                        'circle_count': len(circles),
                        'result_image_path': result_image_path
                    }
                    
                    self._checkpoint(page_key, page_data)
                    result_data[page_key] = page_data
                    
                    logger.info(f"Detected {len(circles)} circles on page {i}")
                except Exception as e:
                    logger.error(f"Error processing page {i}: {str(e)}")
                    # Continue with next page
            
            # Mark processing as completed and store final result
            self._mark_completed(result_data)
            
            # Cache the result with error handling
            try:
                self._set_cache(document, document)
            except Exception as e:
                logger.warning(f"Failed to cache results: {str(e)}")
            
            return document
        except Exception as e:
            logger.error(f"Error in CircleFormDetectorProcessor: {str(e)}")
            # Return the document unchanged in case of error
            return document