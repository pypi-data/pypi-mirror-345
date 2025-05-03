import os
import cv2
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from core.schemas.document import BlockTypes
from core.schemas.document.document import Document

from core.transformers.processors import BaseProcessor
from core.transformers.fill.fill import fill_and_find_missing_rectangles
from core.transformers.utils.debug_utils import save_debug_image

# Configure logger
logger = logging.getLogger(__name__)

class FillMissingRectanglesProcessor(BaseProcessor):
    """Processor for filling missing rectangles in tables."""
    
    def __init__(self, config: Optional[BaseModel | dict] = None, 
                 output_dir: str = None, 
                 checkpoint_dir: str = None):
        """Initialize the processor with checkpointing support."""
        super().__init__(config, checkpoint_dir=checkpoint_dir)
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
        """Apply checkpoint data when resuming."""
        if 'result' not in self._checkpoint_data:
            return document
            
        result_data = self._checkpoint_data['result']
        
        try:
            # Get the first page
            page = document.pages[0]
            if not hasattr(page, 'metadata'):
                page.__dict__['metadata'] = {}
                
            # Apply checkpoint data
            page_data = result_data.get('page_data', {})
            if page_data:
                page.__dict__['metadata'].update({
                    'processed_image': cv2.imread(page_data['result_image_path']) if page_data.get('result_image_path') else None,
                    'rect_rois': page_data.get('rect_rois', []),
                    'rect_count': page_data.get('rect_count', 0)
                })
                
                # Restore table block data
                if page_data.get('table_block_data'):
                    if 'table_block' in page.__dict__['metadata']:
                        table_block = page.__dict__['metadata']['table_block']
                        if not hasattr(table_block, 'metadata'):
                            table_block.__dict__['metadata'] = {}
                        table_block.__dict__['metadata'].update(page_data['table_block_data'])
                        
        except Exception as e:
            logger.error(f"Error applying checkpoint: {str(e)}")
            
        return document
        
    def __call__(self, document: Document, *args, **kwargs) -> Document:
        """Fill missing rectangles with checkpoint support."""
        try:
            # Check for cached result
            cached_result = self._get_cache(document)
            if cached_result:
                logger.info("Using cached result for FillMissingRectanglesProcessor")
                return cached_result
            
            # Check for completed checkpoint
            if 'completed' in self._checkpoint_data and self._checkpoint_data['completed']:
                logger.info("Resuming from completed checkpoint")
                return self._apply_checkpoint_to_document(document)
            
            logger.info("Filling missing rectangles...")
            
            # Get the first page
            page = document.pages[0]
            
            # Make sure page has metadata
            if not hasattr(page, 'metadata') or page.metadata is None:
                page.__dict__['metadata'] = {}
                
            # Get required data
            metadata = page.__dict__['metadata']
            img = metadata.get("original_image")
            contours = metadata.get("contours")
            mean_area = metadata.get("mean_area")
            
            if any(x is None for x in [img, contours, mean_area]):
                raise ValueError("Missing required input data")
            
            # Store pre-processing checkpoint
            self._checkpoint("pre_processing", {
                "contours_count": len(contours),
                "mean_area": mean_area
            })
            
            # Process rectangles
            result_img, index, rect_rois = fill_and_find_missing_rectangles(
                img, contours, mean_area, self.output_dir
            )
            
            # Save result image for checkpoint
            result_image_path = None
            if self.debug_mode and self.output_dir:
                result_image_path = os.path.join(self.output_dir, "table_cells_detected.png")
                cv2.imwrite(result_image_path, result_img)
            
            # Update metadata
            metadata.update({
                "processed_image": result_img,
                "rect_rois": rect_rois,
                "rect_count": index
            })
            
            # Update table block if present
            table_block_data = None
            table_block = metadata.get("table_block")
            if table_block:
                if not hasattr(table_block, 'metadata'):
                    table_block.__dict__['metadata'] = {}
                table_block.__dict__['metadata'].update({
                    "rect_count": index,
                    "rois": rect_rois
                })
                table_block_data = {
                    "rect_count": index,
                    "rois": rect_rois
                }
            
            # Store completion checkpoint
            result_data = {
                'page_data': {
                    'rect_count': index,
                    'rect_rois': rect_rois,
                    'result_image_path': result_image_path,
                    'table_block_data': table_block_data
                }
            }
            self._mark_completed(result_data)
            
            # Cache the result
            self._set_cache(document, document)
            
            logger.info(f"Total rectangle ROIs: {index}")
            return document
            
        except Exception as e:
            logger.error(f"Error in FillMissingRectanglesProcessor: {str(e)}")
            return document