import os
import cv2
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from core.schemas.document import BlockTypes
from core.schemas.document.document import Document
from core.transformers.processors import BaseProcessor
from core.transformers.roi.roi_text_analysis import (
    analyze, TextCell, AnalysisStats
)

# Configure logger
logger = logging.getLogger(__name__)

class ROITextAnalysisProcessor(BaseProcessor):
    """Processor for analyzing text in ROIs"""
    
    block_types = (BlockTypes.Table,)
    output_dir: Optional[str] = None
    debug_mode: bool = True
    header_y_threshold: int = 250
    
    def __init__(self, config: Optional[Any] = None, output_dir: str = None):
        """
        Initialize the processor.
        
        Args:
            config: Configuration dictionary or BaseModel for the processor
            output_dir: Output directory for debug files
        """
        super().__init__(config)
        self.output_dir = output_dir
        self.output_path = Path(output_dir) if output_dir else None
        self.text_regions_dir = self.output_path / "text_regions" if self.output_path else None
        self._setup_output_dirs()
        
        # Store header structure
        self.header_structure = None
        
        # Text detection configuration
        self.config = {
            'gaussian_blur': (5, 5),
            'adaptive_threshold': {
                'block_size': 11,
                'C': 2
            },
            'visualization': {
                'printed_color': (0, 255, 0),    # Green
                'handwritten_color': (0, 0, 255), # Red
                'font_scale': 0.6,
                'font_thickness': 1,
                'rect_thickness': 2,
                'text_offset': (5, 20)
            },
            'row_grouping': {
                'y_tolerance': 20  # Pixels tolerance for same row detection
            },
            'text_detection': {
                'ocr': {
                    'psm': 7,
                    'oem': 2,
                    'lang': 'eng',
                    'confidence_threshold': 65.0
                },
                'uniformity': {
                    'min_contours': 2,
                    'confidence_threshold': 75.0
                },
                'stroke': {
                    'canny': {
                        'low': 100,
                        'high': 200
                    },
                    'kernel_size': (3, 3),
                    'dilate_iterations': 1,
                    'ratio_threshold': 1.5,
                    'max_ratio': 2.0
                },
                'weights': {
                    'ocr': 0.4,
                    'uniformity': 0.3,
                    'stroke': 0.3
                },
                'overall_threshold': 65.0
            }
        }
        
        # Store initialization checkpoint
        self._checkpoint("init", {"output_dir": output_dir})
    
    def _setup_output_dirs(self) -> None:
        """Create necessary output directories"""
        if self.output_path:
            self.output_path.mkdir(parents=True, exist_ok=True)
            if self.text_regions_dir:
                self.text_regions_dir.mkdir(parents=True, exist_ok=True)
    
    def __call__(self, document: Document, *args, **kwargs) -> Document:
        """
        Analyze text in ROIs with comprehensive checkpointing.
        
        Args:
            document: The document to process
            
        Returns:
            Document: The updated document
        """
        try:
            # Initial processing checkpoint
            self._checkpoint("processing_start", {
                "timestamp": str(datetime.now()),
                "document_pages": len(document.pages)
            })

            logger.info("Analyzing ROI text...")
            
            # Get the first page
            page = document.pages[0]
            
            # Pre-processing metadata checkpoint
            self._checkpoint("metadata_check", {
                "has_metadata": hasattr(page, 'metadata'),
                "metadata_exists": page.metadata is not None if hasattr(page, 'metadata') else False,
                "timestamp": str(datetime.now())
            })
            
            # Make sure page has a metadata dictionary
            if not hasattr(page, 'metadata') or page.metadata is None:
                page.__dict__['metadata'] = {}
                self._checkpoint("metadata_initialized", {
                    "timestamp": str(datetime.now())
                })
                
            # Get the image and ROIs from page metadata
            img = page.__dict__['metadata']["original_image"]
            rect_rois = page.__dict__['metadata']["rect_rois"]
            
            # Image and ROIs checkpoint
            self._checkpoint("data_loaded", {
                "image_shape": img.shape if img is not None else None,
                "roi_count": len(rect_rois),
                "timestamp": str(datetime.now())
            })
            
            # Store pre-processing checkpoint
            self._checkpoint("pre_processing", {
                "roi_count": len(rect_rois),
                "config": self.config,
                "header_structure": self.header_structure is not None,
                "timestamp": str(datetime.now())
            })
            
            # Analysis start checkpoint
            self._checkpoint("analysis_start", {
                "timestamp": str(datetime.now())
            })
            
            # Use the standalone analyze function
            analysis_result = analyze(
                image=img, 
                rect_rois=rect_rois, 
                config=self.config,
                output_dir=self.output_path,
                debug_visualization=self.debug_mode,
                header_structure=self.header_structure
            )
            
            # Analysis completion checkpoint
            self._checkpoint("analysis_complete", {
                "result_type": str(type(analysis_result)),
                "timestamp": str(datetime.now())
            })
            
            logger.info(f"ROI analysis complete, result type: {type(analysis_result)}")
            
            # Extract the cells from the results
            all_cells = analysis_result.get("all_cells", [])
            printed_cells = analysis_result.get("printed_cells", [])
            handwritten_cells = analysis_result.get("handwritten_cells", [])
            
            # Cell extraction checkpoint
            self._checkpoint("cells_extracted", {
                "total_cells": len(all_cells),
                "printed_cells": len(printed_cells),
                "handwritten_cells": len(handwritten_cells),
                "timestamp": str(datetime.now())
            })
            
            logger.info(f"Found {len(all_cells)} total cells, {len(printed_cells)} printed, {len(handwritten_cells)} handwritten")
            
            # Convert cells to a format suitable for header mapping
            cell_dicts = []
            for cell in all_cells:
                cell_dict = {
                    "bbox": [cell.x, cell.y, cell.width, cell.height],
                    "text": cell.text,
                    "is_header_candidate": cell.is_printed and cell.y < self.header_y_threshold,
                    "confidence": cell.confidence.get("overall_confidence", 0) if hasattr(cell.confidence, "get") else 0
                }
                cell_dicts.append(cell_dict)
            
            # Cell conversion checkpoint
            self._checkpoint("cells_converted", {
                "cell_count": len(cell_dicts),
                "header_candidates": sum(1 for c in cell_dicts if c["is_header_candidate"]),
                "timestamp": str(datetime.now())
            })
            
            # Store the ROI results in the page metadata
            page.__dict__['metadata']["roi_results"] = cell_dicts
            
            # Metadata update checkpoint
            self._checkpoint("metadata_updated", {
                "updated_keys": list(page.__dict__['metadata'].keys()),
                "timestamp": str(datetime.now())
            })
            
            logger.info(f"Analyzed ROI results prepared for header mapping")
            
            # Get the table block directly from metadata
            table_block = page.__dict__['metadata'].get("table_block")
            
            # Table block checkpoint
            self._checkpoint("table_block_check", {
                "table_block_exists": table_block is not None,
                "timestamp": str(datetime.now())
            })
            
            # Update table block
            if table_block:
                if not hasattr(table_block, 'metadata') or table_block.metadata is None:
                    table_block.__dict__['metadata'] = {}
                table_block.__dict__['metadata']["roi_results"] = cell_dicts
                # Table block update checkpoint
                self._checkpoint("table_block_updated", {
                    "metadata_keys": list(table_block.__dict__['metadata'].keys()),
                    "timestamp": str(datetime.now())
                })
            else:
                logger.warning("Table block not found in page metadata")
                self._checkpoint("table_block_missing", {
                    "timestamp": str(datetime.now())
                })
            
            # Store completion checkpoint
            self._checkpoint("completion", {
                "status": "success",
                "cells_count": len(cell_dicts),
                "has_table_block": table_block is not None,
                "timestamp": str(datetime.now())
            })
            
            return document
            
        except Exception as e:
            # Error checkpoint
            self._checkpoint("error", {
                "error": str(e),
                "stage": "roi_text_analysis",
                "timestamp": str(datetime.now())
            })
            logger.error(f"Error in ROI text analysis: {str(e)}")
            return document
