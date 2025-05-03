import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
import json
import argparse

from core.pipelines import BasePipeline
from core.pipelines.utils.utils import extract_form_data, safe_json_dump
from core.transformers.processors import BaseProcessor
from core.transformers.processors.rectangle_form_detector import RectangleFormDetectorProcessor
from core.transformers.processors.fill_missing_form_rectangles import FillMissingFormRectanglesProcessor
from core.transformers.processors.circle_form_detector import CircleFormDetectorProcessor
from core.transformers.processors.form_text_analyzer import FormTextAnalyzerProcessor
from ..renderers.json_renderer import JSONRenderer 
from core.schemas.document.document import Document
import logging

# Configure logger
logger = logging.getLogger(__name__)

class ParseForm(BasePipeline):
    """
    Pipeline for detecting and parsing forms in documents.
    
    This pipeline applies a sequence of processors to identify form elements like
    rectangles and circles, and extract text labels associated with them.
    """
    
    default_processors: Tuple[BaseProcessor, ...] = (
        RectangleFormDetectorProcessor,
        FillMissingFormRectanglesProcessor,
        CircleFormDetectorProcessor,
        FormTextAnalyzerProcessor,
    )
    
    def __init__(self, config: Dict[str, Any] = None, image_path: str = None):
        """
        Initialize the form parsing pipeline.
        
        Args:
            config: Configuration dictionary for the pipeline and its processors
            image_path: Path to the image to process
        """
        # Pass config and image_path to the parent class
        super().__init__(config or {}, image_path)
        
        # Override output directory
        self.output_dir = self.config.get("output_dir", "output/form_analysis")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Store output_dir in artifact_dict for dependency resolution
        self.artifact_dict['output_dir'] = self.output_dir
        
        # Initialize processors using the parent class method and default_processors
        self.processors = self.initialize_processors(self.default_processors)
        
        # Initialize the JSON renderer
        self.renderer = JSONRenderer()
        
        logger.info(f"ParseForm pipeline initialized with {len(self.processors)} processors")
    
    def __call__(self, document: Optional[Document] = None) -> Document:
        """
        Apply the form parsing pipeline to a document.
        If no document is provided, initialize one from the image path.
        
        Args:
            document: The document to process or None to initialize from image_path
            
        Returns:
            Document: The processed document with form information
        """
        # Initialize document if not provided
        if document is None:
            if not self.image_path:
                raise ValueError("No document provided and no image_path set")
            document = self._initialize_document()
            
        logger.info(f"Starting form parsing pipeline for document: {document.filepath}")
        
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
        
        logger.info("Form parsing pipeline completed successfully")
        return document
    
    def extract_form_data(self, document: Document) -> Dict[str, Any]:
        """
        Extract structured form data from the processed document.
        
        Args:
            document: The processed document
            
        Returns:
            Dict[str, Any]: Extracted form data
        """
        return extract_form_data(document)
    
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
    Main function to demonstrate the ParseForm pipeline.
    
    This function:
    1. Parses command line arguments
    2. Loads the input image
    3. Processes it through the form parsing pipeline
    4. Extracts structured data
    5. Saves results to a JSON file
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Parse forms from an image')
    parser.add_argument('--image', default='core/input/input.png', help='Path to the input image')
    parser.add_argument('--output', default='core/processed/result_form.json', 
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
        "output_dir": "output/form_analysis",
        "rectangle_detector": {
            "debug_mode": args.debug
        },
        "text_analyzer": {
            "debug_mode": args.debug
        }
    }
    
    # Initialize and run the pipeline
    logger.info("Initializing form parsing pipeline")
    pipeline = ParseForm(config=config, image_path=args.image)
    
    # Process the image (initialize document and apply processors)
    logger.info("Processing image...")
    document = pipeline()
    
    # Extract structured data
    logger.info("Extracting form data...")
    form_data = pipeline.extract_form_data(document)
    
    # Create result structure
    result = {
        "input_file": args.image,
        "form_data": form_data,
        "summary": {
            "field_count": len(form_data),
            "timestamp": str(Path(args.image).stat().st_mtime)
        }
    }
    
    # Save results to JSON file
    logger.info(f"Saving results to: {args.output}")
    safe_json_dump(result, args.output)

    debug_output = os.path.join(os.path.dirname(args.output), "full_document.json")
    logger.info(f"Saving full document JSON to: {debug_output}")
    pipeline.save_to_json(document, debug_output)
    # with open(args.output, 'w', encoding='utf-8') as f:
    #     json.dump(result, f, indent=2, ensure_ascii=False)
    
    # logger.info("Form parsing completed successfully")
    
    # Print summary
    print(f"\nForm Parsing Summary:")
    print(f"  Input image: {args.image}")
    print(f"  Fields extracted: {len(form_data)}")
    if form_data:
        print(f"  Sample fields:")
        for i, (key, value) in enumerate(form_data.items()):
            if i >= 3:  # Show max 3 sample fields
                break
            print(f"    {key}: {value}")
    print(f"  Results saved to: {args.output}")
    print(f"  Full document saved to: {debug_output}")


if __name__ == "__main__":
    main()
# RUN: python -m core.pipelines.parse_form --debug
