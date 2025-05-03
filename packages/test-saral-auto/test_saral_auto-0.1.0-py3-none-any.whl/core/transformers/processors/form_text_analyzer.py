import os
import cv2
import numpy as np
import pytesseract
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from core.transformers.contour.contour import get_leftmost_shapes
from core.transformers.roi.roi_processing import merge_rois_if_no_text, find_missed_strips
from core.transformers.text.text_processing import get_text_boundary
from core.transformers.detect_shapes.detect_shapes import get_largest_rectangle_roi

from core.transformers.processors import BaseProcessor
from core.schemas.document.document import Document
import logging

logger = logging.getLogger(__name__)

class FormTextAnalyzerProcessor(BaseProcessor):
    """
    Processor for analyzing text in form documents.
    Extracts text from regions of interest around form elements.
    """
    
    def __init__(self, config: Dict[str, Any] = None, output_dir: str = None):
        """
        Initialize the form text analyzer processor.
        
        Args:
            config: Configuration dictionary for the processor
            output_dir: Directory to save debug outputs
        """
        super().__init__(config or {})
        self.config = config or {}  # Store the config explicitly
        self.output_dir = output_dir
        self.debug_mode = self.config.get('debug_mode', False)
        
        # Configure pytesseract path if provided
        if 'tesseract_path' in self.config:
            pytesseract.pytesseract.tesseract_cmd = self.config['tesseract_path']
        
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)

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
            for page_idx, page in enumerate(document.pages):
                page_key = f'page_{page_idx}'
                page_data = result_data.get(page_key, {})
                
                if not page_data:
                    continue
                    
                if not hasattr(page, 'metadata'):
                    page.__dict__['metadata'] = {}
                    
                # Restore page data
                if page_data.get('result_image_path'):
                    page.__dict__['metadata']['result_image'] = cv2.imread(page_data['result_image_path'])
                    
                page.__dict__['metadata'].update({
                    'text_rois': page_data.get('text_rois', []),
                })
                
        except Exception as e:
            logger.error(f"Error applying checkpoint: {str(e)}")
            
        return document  
    
    def extract_text_from_rois(self, image: np.ndarray, rectangles: List[np.ndarray], circles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract text from regions of interest near form elements.
        
        Args:
            image: Input image
            rectangles: List of rectangle contours
            circles: List of circle dictionaries
            
        Returns:
            List of ROI dictionaries with extracted text
        """
        # Get leftmost rectangles
        text_rois_left_to_rectangles = get_leftmost_shapes(rectangles, shape_type="rectangle")
        
        # Get leftmost circles' ROIs
        circle_left_text_rois = []
        for circle in circles:
            if circle.get('contour') is not None:
                circle_left_text_rois.append(circle['contour'])
        
        text_rois_left_to_circles = get_leftmost_shapes(circle_left_text_rois, shape_type="rectangle")
        
        # Combine all ROIs
        all_shapes = text_rois_left_to_rectangles + text_rois_left_to_circles
        
        # Extract text from ROIs
        rois = []
        for shape in all_shapes:
            x, y, w, h = cv2.boundingRect(shape)
            
            # Define the text region to the left of the shape
            roi_left = 300  # Fixed left position
            roi_right = x - 50  # Excluding some margin from the shape
            roi_top = y
            roi_bottom = y + h
            
            # Skip invalid ROIs
            if roi_right <= roi_left or roi_bottom <= roi_top:
                continue
                
            # Extract text from the region
            try:
                text_region = image[roi_top:roi_bottom, roi_left:roi_right]
                if text_region.size == 0:
                    continue
                    
                text = pytesseract.image_to_string(text_region)
                
                rois.append({
                    'left': roi_left,
                    'top': roi_top,
                    'right': roi_right,
                    'bottom': roi_bottom,
                    'text': text.strip()
                })
            except Exception as e:
                logger.error(f"Error extracting text: {str(e)}")
        
        # Merge ROIs if they don't have meaningful text
        merged_rois = merge_rois_if_no_text(rois)
        
        return merged_rois
    
    def process_missed_strips(self, image: np.ndarray, missed_strips: List[Tuple[int, int]], 
                              page_roi: List[Tuple[int, int]]) -> List[Dict[str, Any]]:
        """
        Process missed strips to extract text from them.
        
        Args:
            image: Input image
            missed_strips: List of (top, bottom) coordinates for missed strips
            page_roi: Page boundary points
            
        Returns:
            List of ROI dictionaries for the missed strips
        """
        rois = []
        offset = 20  # Offset for clean boundary
        
        for strip in missed_strips:
            # Skip invalid strips
            if strip[0] >= strip[1] or page_roi[0][0] >= page_roi[2][0]:
                continue
                
            # Extract the text region from the strip
            text_region = image[
                strip[0] + offset : strip[1] - offset,
                page_roi[0][0] + offset : page_roi[2][0] - offset
            ]
            
            # Skip if the text region is empty
            if text_region.size == 0:
                continue
                
            # Extract text from the region
            text = pytesseract.image_to_string(text_region)
            
            # Skip if no text was found
            if not text.strip():
                continue
                
            # Get the boundary of the text
            boundary = get_text_boundary(text_region)
            
            # Skip invalid boundaries
            if (boundary == ((float("inf"), float("inf")), (float("-inf"), float("-inf"))) or 
                boundary == ((0, 0), (0, 0))):
                continue
                
            # Skip if the text is too short
            if len(text.strip()) < 3:
                continue
                
            # Create ROI
            roi = {
                "left": page_roi[0][0] + offset,
                "top": strip[0] + offset,
                "right": page_roi[0][0] + boundary[1][0] + offset,
                "bottom": strip[1] - offset,
                "text": text.strip()
            }
            
            rois.append(roi)
            
        return rois
    
    def __call__(self, document: Document) -> Document:
        """
        Apply text analysis to each page in the document.
        
        Args:
            document: Input document with detected rectangles and circles
            
        Returns:
            Document: Document with extracted text ROIs
        """
        try:
            # Initialize processor checkpoint
            self._checkpoint("processing_start", {
                "total_pages": len(document.pages),
                "timestamp": str(datetime.now())
            })

            logger.info("Applying form text analysis")
            
            for i, page in enumerate(document.pages):
                try:
                    # Page processing start checkpoint
                    self._checkpoint(f"page_{i}_start", {
                        "status": "processing",
                        "page_number": i
                    })

                    # Get the necessary data from page metadata
                    if not hasattr(page, 'metadata') or page.metadata is None:
                        logger.warning(f"No metadata found for page {i}")
                        self._checkpoint(f"page_{i}_error", {
                            "error": "No metadata found",
                            "page_number": i
                        })
                        continue
                        
                    metadata = page.__dict__['metadata']
                    original_image = metadata.get('original_image')
                    rectangle_contours = metadata.get('rectangle_contours', [])
                    circles = metadata.get('circles', [])
                    
                    if original_image is None:
                        logger.warning(f"Missing original image for page {i}")
                        self._checkpoint(f"page_{i}_error", {
                            "error": "Missing original image",
                            "page_number": i
                        })
                        continue
                    
                    # Checkpoint before ROI extraction
                    self._checkpoint(f"page_{i}_roi_start", {
                        "rectangles": len(rectangle_contours),
                        "circles": len(circles)
                    })
                    
                    # Get page ROI
                    page_roi = get_largest_rectangle_roi(original_image)
                    
                    # Extract text from ROIs
                    rois = self.extract_text_from_rois(original_image, rectangle_contours, circles)
                    
                    # Checkpoint after initial ROI extraction
                    self._checkpoint(f"page_{i}_initial_rois", {
                        "rois_count": len(rois)
                    })
                    
                    # Find missed strips
                    missed_strips = find_missed_strips(original_image, rois, page_roi, 60)
                    
                    # Process missed strips
                    missed_rois = self.process_missed_strips(original_image, missed_strips, page_roi)
                    
                    # Checkpoint after missed strips processing
                    self._checkpoint(f"page_{i}_missed_rois", {
                        "missed_rois_count": len(missed_rois)
                    })
                    
                    # Combine all ROIs
                    all_rois = rois + missed_rois
                    
                    # Draw ROIs on result image
                    result_img = metadata.get('result_image', original_image.copy())
                    for roi in all_rois:
                        cv2.rectangle(result_img, 
                                     (roi['left'], roi['top']), 
                                     (roi['right'], roi['bottom']), 
                                     (0, 255, 0), 2)
                    
                    # Save debug image and create checkpoint path
                    debug_path = None
                    if self.debug_mode and self.output_dir:
                        debug_path = os.path.join(self.output_dir, f"page_{i}_text_rois.png")
                        cv2.imwrite(debug_path, result_img)
                    
                    # Update page metadata
                    metadata.update({
                        'text_rois': all_rois,
                        'result_image': result_img
                    })
                    
                    # Page completion checkpoint
                    self._checkpoint(f"page_{i}_complete", {
                        "status": "completed",
                        "total_rois": len(all_rois),
                        "debug_image_path": debug_path,
                        "timestamp": str(datetime.now())
                    })
                    
                    logger.info(f"Extracted {len(all_rois)} text ROIs on page {i}")
                    
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
            logger.error(f"Error in form text analysis: {str(e)}")
            self._checkpoint("processing_error", {
                "error": str(e),
                "timestamp": str(datetime.now())
            })
            return document