import os
import cv2
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from dataclasses import dataclass
from datetime import datetime

from core.schemas.document import BlockTypes
from core.schemas.document.document import Document

from core.transformers.processors import BaseProcessor
from core.transformers.utils.debug_utils import save_to_json
from core.transformers.roi.roi_header_mapper import (
    analyze_structure,
)

# Configure logger
logger = logging.getLogger(__name__)

class HeaderMapperProcessor(BaseProcessor):
    """
    Processor for mapping header structure in tables.
    """
    
    block_types = (BlockTypes.Table,)
    output_dir: Optional[str] = None
    similarity_threshold: float = 0.85
    min_pattern_count: int = 3
    header_y_threshold: int = 250
    
    def __init__(self, config: Optional[BaseModel | dict] = None, output_dir: str = None):
        """
        Initialize the processor.
        
        Args:
            config: Configuration dictionary or BaseModel for the processor
            output_dir: Output directory for debug files
        """
        super().__init__(config)
        self.output_dir = output_dir
        
        # Store initialization checkpoint
        self._checkpoint("init", {"output_dir": output_dir})
    
    def __call__(self, document: Document, *args, **kwargs) -> Document:
        """
        Map header structure in the table with comprehensive checkpointing.
        
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

            logger.info("Mapping header structure...")
            
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
                
            # Get the ROI results from page metadata
            roi_results = page.__dict__['metadata']["roi_results"]
            
            # ROI validation checkpoint
            self._checkpoint("roi_validation", {
                "roi_type": str(type(roi_results)),
                "is_list": isinstance(roi_results, list),
                "roi_count": len(roi_results) if isinstance(roi_results, list) else 0,
                "timestamp": str(datetime.now())
            })
            
            # Store pre-processing checkpoint
            if isinstance(roi_results, list):
                self._checkpoint("pre_processing", {
                    "roi_count": len(roi_results),
                    "timestamp": str(datetime.now())
                })
            else:
                self._checkpoint("pre_processing", {
                    "roi_format": str(type(roi_results)),
                    "timestamp": str(datetime.now())
                })
            
            # Check if roi_results is in the expected format
            if not isinstance(roi_results, list) or (len(roi_results) > 0 and not isinstance(roi_results[0], dict)):
                logger.warning("ROI results are not in the expected format. Creating empty mapped results.")
                self._checkpoint("format_error", {
                    "error": "Invalid ROI results format",
                    "timestamp": str(datetime.now())
                })
                mapped_results = {"cells": [], "pattern_coverage": 0}
            else:
                # Map header structure using standalone functions
                try:
                    # Analysis preparation checkpoint
                    self._checkpoint("analysis_preparation", {
                        "similarity_threshold": self.similarity_threshold,
                        "min_pattern_count": self.min_pattern_count,
                        "header_y_threshold": self.header_y_threshold,
                        "timestamp": str(datetime.now())
                    })
                    
                    # Create a dictionary to pass to analyze_structure
                    analysis_input = {"all_cells": roi_results}
                    
                    # Analysis start checkpoint
                    self._checkpoint("analysis_start", {
                        "input_cells": len(roi_results),
                        "timestamp": str(datetime.now())
                    })
                    
                    mapped_results = analyze_structure(
                        roi_results=analysis_input,
                        header_structure=None,
                        similarity_threshold=self.similarity_threshold,
                        min_pattern_count=self.min_pattern_count,
                        header_y_threshold=self.header_y_threshold
                    )
                    
                    # Analysis completion checkpoint
                    self._checkpoint("analysis_complete", {
                        "result_type": str(type(mapped_results)),
                        "has_error": "status" in mapped_results and mapped_results["status"] == "error",
                        "timestamp": str(datetime.now())
                    })
                    
                    # Check for errors in analysis
                    if "status" in mapped_results and mapped_results["status"] == "error":
                        logger.error(f"Analysis error: {mapped_results.get('error', 'Unknown error')}")
                        self._checkpoint("analysis_error", {
                            "error": mapped_results.get("error", "Unknown error"),
                            "timestamp": str(datetime.now())
                        })
                        mapped_results = {"cells": [], "pattern_coverage": 0}
                    else:
                        # Extract cells from mapped_results
                        mapped_cells = mapped_results.get("mapped_cells", [])
                        
                        # Cell extraction checkpoint
                        self._checkpoint("cell_extraction", {
                            "mapped_cells_count": len(mapped_cells),
                            "timestamp": str(datetime.now())
                        })
                        
                        # Flatten the structure to match expected format
                        mapped_results = {
                            "cells": [
                                {
                                    "bbox": [cell["position"]["x"], cell["position"]["y"], 
                                             cell["position"]["width"], cell["position"]["height"]],
                                    "text": cell["text"],
                                    "is_header": cell["metadata"]["is_header"],
                                    "row_index": cell["metadata"]["row_index"],
                                    "col_index": cell["metadata"]["col_index"],
                                    "row_type": cell["metadata"]["row_type"],
                                    "pattern_group": cell["metadata"]["pattern_group"],
                                    "is_repeating": cell["metadata"]["is_repeating"]
                                }
                                for cell in mapped_cells
                            ],
                            "pattern_coverage": mapped_results.get("statistics", {}).get("pattern_coverage", 0)
                        }
                        
                        # Results flattening checkpoint
                        self._checkpoint("results_flattened", {
                            "flattened_cells": len(mapped_results["cells"]),
                            "pattern_coverage": mapped_results["pattern_coverage"],
                            "timestamp": str(datetime.now())
                        })
                        
                except Exception as e:
                    logger.error(f"Error mapping header structure: {str(e)}")
                    mapped_results = {"cells": [], "pattern_coverage": 0}
                    self._checkpoint("mapping_error", {
                        "error": str(e),
                        "timestamp": str(datetime.now())
                    })
            
            # Store the mapped results in the page metadata
            page.__dict__['metadata']["mapped_results"] = mapped_results
            
            # Metadata update checkpoint
            self._checkpoint("metadata_updated", {
                "updated_keys": list(page.__dict__['metadata'].keys()),
                "timestamp": str(datetime.now())
            })
            
            # Calculate statistics
            total_cells = len(mapped_results.get("cells", []))
            header_cells = sum(1 for cell in mapped_results.get("cells", []) if cell.get("is_header", False))
            data_cells = total_cells - header_cells
            pattern_coverage = mapped_results.get("pattern_coverage", 0)
            
            # Statistics checkpoint
            self._checkpoint("statistics_calculated", {
                "total_cells": total_cells,
                "header_cells": header_cells,
                "data_cells": data_cells,
                "pattern_coverage": pattern_coverage,
                "timestamp": str(datetime.now())
            })
            
            logger.info(f"Total cells: {total_cells}")
            logger.info(f"Header cells: {header_cells}")
            logger.info(f"Data cells: {data_cells}")
            logger.info(f"Pattern coverage: {pattern_coverage:.2f}")
            
            # Save the mapped results to a JSON file
            if self.output_dir:
                json_path = os.path.join(self.output_dir, "table_analysis.json")
                save_to_json(mapped_results, json_path)
                self._checkpoint("json_saved", {
                    "json_path": json_path,
                    "timestamp": str(datetime.now())
                })
            
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
                table_block.__dict__['metadata'].update({
                    "mapped_results": mapped_results,
                    "has_header": header_cells > 0,
                    "total_cells": total_cells,
                    "header_cells": header_cells,
                    "data_cells": data_cells,
                    "pattern_coverage": pattern_coverage
                })
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
                "total_cells": total_cells,
                "header_cells": header_cells,
                "data_cells": data_cells,
                "pattern_coverage": pattern_coverage,
                "has_table_block": table_block is not None,
                "timestamp": str(datetime.now())
            })
            
            return document
            
        except Exception as e:
            # Error checkpoint
            self._checkpoint("error", {
                "error": str(e),
                "stage": "header_mapping",
                "timestamp": str(datetime.now())
            })
            logger.error(f"Error in header mapping: {str(e)}")
            return document
