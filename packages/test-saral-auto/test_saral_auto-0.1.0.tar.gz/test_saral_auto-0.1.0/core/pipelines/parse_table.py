"""
Pipeline for detecting and parsing tables in documents.
"""

import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
import json
import argparse
import logging
import numpy as np

from core.pipelines import BasePipeline
from core.pipelines.utils.utils import extract_table_data, safe_json_dump
from core.transformers.processors import BaseProcessor
from core.transformers.processors.rectangle_detector import RectangleDetectorProcessor
from core.transformers.processors.fill_missing_rectangle import FillMissingRectanglesProcessor
from core.transformers.processors.roi_text_analysis import ROITextAnalysisProcessor
from core.transformers.processors.table_header_mapper import HeaderMapperProcessor

from core.schemas.document.document import Document

# Import our custom JSON renderer
from core.renderers.json_renderer import JSONRenderer


# Configure logger
logger = logging.getLogger(__name__)

class ParseTable(BasePipeline):
    """
    Pipeline for detecting and parsing tables in documents.
    
    This pipeline applies a sequence of processors to identify tables, detect cells,
    analyze text within cells, and map header structure.
    """
    
    default_processors: Tuple[BaseProcessor, ...] = (
        RectangleDetectorProcessor,
        FillMissingRectanglesProcessor,
        ROITextAnalysisProcessor,
        HeaderMapperProcessor,
    )
    
    def __init__(self, config: Dict[str, Any] = None, image_path: str = None):
        """
        Initialize the table parsing pipeline.
        
        Args:
            config: Configuration dictionary for the pipeline and its processors
            image_path: Path to the image to process
        """
        # Pass config and image_path to the parent class
        super().__init__(config or {}, image_path)
        
        # Override output directory
        self.output_dir = self.config.get("output_dir", "output/table_analysis")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Store output_dir in artifact_dict for dependency resolution
        self.artifact_dict['output_dir'] = self.output_dir
        
        # Initialize processors using the parent class method and default_processors
        self.processors = self.initialize_processors(self.default_processors)
        
        # Initialize the JSON renderer
        self.renderer = JSONRenderer(config={'include_text': True})
        
        logger.info(f"ParseTable pipeline initialized with {len(self.processors)} processors")
    
    def __call__(self, document: Optional[Document] = None) -> Document:
        """
        Apply the table parsing pipeline to a document.
        If no document is provided, initialize one from the image path.
        
        Args:
            document: The document to process or None to initialize from image_path
            
        Returns:
            Document: The processed document with table information
        """
        # Initialize document if not provided
        if document is None:
            if not self.image_path:
                raise ValueError("No document provided and no image_path set")
            document = self._initialize_document()
            
        logger.info(f"Starting table parsing pipeline for document: {document.filepath}")
        
        # Apply each processor in sequence
        for processor in self.processors:
            logger.info(f"Applying processor: {processor.__class__.__name__}")
            try:
                document = processor(document)
            except Exception as e:
                logger.error(f"Error in processor {processor.__class__.__name__}: {str(e)}")
                # Get checkpoint data from processor if available
                if hasattr(processor, 'get_checkpoint'):
                    checkpoint_data = processor.get_checkpoint("error") or {}
                    logger.error(f"Last checkpoint data: {checkpoint_data}")
                raise
        
        logger.info("Table parsing pipeline completed successfully")
        return document
    
    def extract_table_data(self, document: Document) -> List[Dict[str, Any]]:
        """
        Extract structured table data from the processed document.
        
        Args:
            document: The processed document
            
        Returns:
            List[Dict[str, Any]]: List of extracted table data
        """
        return extract_table_data(document)
    
    def render_to_json(self, document: Document) -> Dict[str, Any]:
        """
        Render the document to a JSON-serializable dictionary.
        
        Args:
            document: The document to render
            
        Returns:
            Dict: JSON-serializable dictionary representation of the document
        """
        return self.renderer(document)
    
    def save_to_json(self, document: Document, output_path: str) -> None:
        """
        Save the document to a JSON file.
        
        Args:
            document: The document to save
            output_path: Path to save the JSON file
        """
        self.renderer.save_to_file(document, output_path)


def main():
    """
    Main function to demonstrate the ParseTable pipeline.
    
    This function:
    1. Parses command line arguments
    2. Loads the input image
    3. Processes it through the table parsing pipeline
    4. Extracts structured data
    5. Saves results to a JSON file
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Parse tables from an image')
    parser.add_argument('--image', default='core/input/input.png', help='Path to the input image')
    parser.add_argument('--output', default='core/processed/result_table.json', 
                       help='Path to the output JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Check if image exists
    if not os.path.exists(args.image):
        logger.error(f"Image file not found: {args.image}")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create pipeline configuration
    config = {
        "output_dir": "output/table_analysis",
        "rectangle_detector": {
            "debug_mode": args.debug
        },
        "roi_text_analysis": {
            "debug_mode": args.debug
        }
    }
    
    # Initialize and run the pipeline
    logger.info("Initializing table parsing pipeline")
    pipeline = ParseTable(config=config, image_path=args.image)
    
    # Process the image (initialize document and apply processors)
    logger.info("Processing image...")
    document = pipeline()
    
    # Extract structured data
    logger.info("Extracting table data...")
    table_data = pipeline.extract_table_data(document)
    
    # Create result structure
    result = {
        "input_file": args.image,
        "tables": table_data,
        "summary": {
            "table_count": len(table_data),
            "timestamp": str(Path(args.image).stat().st_mtime)
        }
    }
    
    # Save results to JSON file
    logger.info(f"Saving results to: {args.output}")
    safe_json_dump(result, args.output)
    
    # Save full document as JSON for debugging
    debug_output = os.path.join(os.path.dirname(args.output), "full_document.json")
    logger.info(f"Saving full document JSON to: {debug_output}")
    pipeline.save_to_json(document, debug_output)
    
    logger.info("Table parsing completed successfully")
    
    # Print summary
    print(f"\nTable Parsing Summary:")
    print(f"  Input image: {args.image}")
    print(f"  Tables detected: {len(table_data)}")
    if table_data:
        total_cells = sum(t["metadata"]["total_cells"] for t in table_data)
        print(f"  Total cells: {total_cells}")
        total_headers = sum(len(t["headers"]) for t in table_data)
        print(f"  Total headers: {total_headers}")
    print(f"  Results saved to: {args.output}")
    print(f"  Full document JSON saved to: {debug_output}")


if __name__ == "__main__":
    main()