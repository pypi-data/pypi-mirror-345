import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
import json
import argparse

from core.pipelines import BasePipeline
from core.transformers.processors import BaseProcessor
from core.transformers.processors.marker_processor import MarkerProcessor
from core.transformers.processors.add_tesseract_words import AddTesseractWords
from core.transformers.processors.LLM_processors.dubious_identifier_llm import DubiousProcessor
from core.transformers.processors.LLM_processors.table_identifier_llm import TableIdentifierLLMProcessor
from core.transformers.processors.LLM_processors.table_merging_across_pages import TableMergingLLMProcessor
from core.renderers.json_renderer import JSONRenderer
from core.schemas.document.document import Document
from core.transformers.utils.debug_write import dump_document_with_images

import logging

logger = logging.getLogger(__name__)

def serialize_for_json(data):
    """
    Process data to make it JSON serializable.
    
    Args:
        data: The data structure to process
        
    Returns:
        Data structure with all objects converted to JSON serializable types
    """
    if isinstance(data, dict):
        return {k: serialize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_for_json(item) for item in data]
    elif hasattr(data, 'to_dict'):
        return serialize_for_json(data.to_dict())
    elif hasattr(data, 'model_dump'):
        return serialize_for_json(data.model_dump())
    elif hasattr(data, '__dict__'):
        return serialize_for_json(data.__dict__)
    else:
        return data

class BPAIPipeline(BasePipeline):
    """Pipeline for processing documents using Marker.
    
    This pipeline uses the MarkerProcessor to extract structured information
    from documents using the Marker API/library.
    """
    
    base_processors: Tuple[BaseProcessor, ...] = (
        MarkerProcessor,
    )
    
    def __init__(self, config: Dict[str, Any] = None, image_path: str = None):
        """Initialize the BPAI pipeline."""
        # Initialize base pipeline
        super().__init__(config or {}, image_path)
        
        # Override output directory
        self.output_dir = self.config.get("output_dir", "output/bpai")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Store output_dir in artifact_dict for dependency resolution
        self.artifact_dict['output_dir'] = self.output_dir
        
        # Set up folders for page images if using tesseract
        if (self.config.get("use_tesseract", False) or self.config.get("use_llm", False)) and self.image_path:
            self._setup_image_folders()
        
        # Initialize processors based on configuration
        self.processors = self.initialize_processors(self._get_processors())
        
        # Initialize JSON renderer
        self.renderer = JSONRenderer()
        
        logger.info(f"BPAI pipeline initialized with {len(self.processors)} processors")
    
    def _get_processors(self):
        """Determine which processors to use based on configuration."""
        processors = list(self.base_processors)
        
        # Add tesseract processor if enabled
        if self.config.get("use_tesseract", False):
            processors.append(AddTesseractWords)
        
        # Add LLM processor if enabled
        if self.config.get("use_llm", False):
            processors.append(DubiousProcessor)
            processors.append(TableIdentifierLLMProcessor)
            processors.append(TableMergingLLMProcessor)
            
        return tuple(processors)
    
    def _setup_image_folders(self):
        """Set up folders for page images extraction."""
        if not self.image_path:
            logger.warning("No image path provided, skipping folder setup")
            return
            
        try:
            # Create main output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Get PDF name for folder structure
            pdf_name = os.path.splitext(os.path.basename(self.image_path))[0]
            
            # Create a folder for the PDF
            pdf_folder = os.path.join(self.output_dir, pdf_name)
            os.makedirs(pdf_folder, exist_ok=True)
            logger.info(f"Created PDF folder: {pdf_folder}")
            
            # Store the path for later use by processors
            self.artifact_dict['pdf_folder'] = pdf_folder
            
            # Try to determine number of pages to create page folders
            try:
                import pymupdf
                pdf_document = pymupdf.open(self.image_path)
                num_pages = len(pdf_document)
                logger.info(f"PDF has {num_pages} pages")
                
                # Create folders for each page
                for page_num in range(num_pages):
                    page_dir = os.path.join(pdf_folder, f"page_{page_num}")
                    os.makedirs(page_dir, exist_ok=True)
                    # Render the page to a PNG image
                    page = pdf_document.load_page(page_num)
                    pix1 = page.get_pixmap(dpi=300)  # Increase dpi for higher quality
                    image_path = os.path.join(page_dir, f"page_{page_num}.png")
                    pix1.save(image_path)
                    logger.debug(f"Saved higher resolution page image: {image_path}")

                    pix2 = page.get_pixmap()  # same resolution as the original image
                    image_path = os.path.join(page_dir, f"{pdf_name}_page_{page_num}.png")
                    pix2.save(image_path)
                    logger.debug(f"Saved lower resolution page image: {image_path}")
                
                logger.info(f"Setup complete: created {num_pages} page directories")
            except Exception as e:
                logger.warning(f"Could not determine page count: {str(e)}. Will create folders during processing.")
        
        except Exception as e:
            logger.error(f"Error setting up image folders: {str(e)}")
    
    def __call__(self, document: Optional[Document] = None) -> Document:
        """Apply the BPAI pipeline to a document."""

        if document is None:
            # Create minimal document with just the filepath
            document = Document(
                filepath=self.image_path,
                pages=[],
                debug_data_path=self.output_dir
            )
            logger.debug(f"Created document with filepath: {self.image_path}")
    
        # Apply each processor in sequence
        for processor in self.processors:
            logger.info(f"Applying processor: {processor.__class__.__name__}")
            try:
                document = processor(document)
            except Exception as e:
                logger.error(f"Error in processor {processor.__class__.__name__}: {str(e)}")
                # Get checkpoint data if available
                if hasattr(processor, 'get_checkpoint'):
                    checkpoint_data = processor.get_checkpoint("error") or {}
                    logger.error(f"Last checkpoint data: {checkpoint_data}")
                raise
        
        logger.info("Pipeline processing completed successfully")

        # Save a debug copy of the document using marshal
        debug_output = os.path.join(self.output_dir, "debug_document.json")
        logger.debug(f"Saving debug document to: {debug_output}")
        
        try:        
            dump_document_with_images(document, debug_output, indent=2, image_folder_name=f"images", image_key_names=("highres_image",))
        except Exception as e:
            logger.error(f"Failed to save debug document: {str(e)}")
        
        # Render document as a json
        # try: 
        #     rendered_output = document.render_json()
        # except Exception as e:
        #     logger.error(f"Failed to render document: {str(e)}")
                

        return document # TODO: Return rendered output when ready. (Final output JSON)
    
    def save_to_json(self, document: Document, output_path: str) -> None:
        """Save the document to a JSON file using JSONRenderer.
        
        Args:
            document: Document object to save
            output_path: Path where to save the JSON file
        """
        logger.info(f"Using JSONRenderer to save document to: {output_path}")
        self.renderer.save_to_file(document, output_path)


def main():
    """Main function to run the BPAI pipeline."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process document with Marker')
    parser.add_argument('--input', default='input/BPAI-Handwritten-Eng-Horizontal-2.pdf', help='Path to the input document')
    parser.add_argument('--output', default='output/bpai_result.json',help='Path to the output JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--tesseract_path', default='output/bpai2/tesseract_results.json', help='Path to Tesseract OCR results JSON file')
    parser.add_argument('--llm_model', default='gemini-2.0-flash-thinking-exp-01-21', help='LLM model to use for processing')
    parser.add_argument('--max_workers', type=int, default=4, help='Maximum number of worker threads for parallel processing')
    parser.add_argument('--bio_template', default='core/constants/bio_prompt.j2', help='Path to bio analysis prompt template')
    parser.add_argument('--table_template', default='core/constants/table_prompt.j2', help='Path to table analysis prompt template')
    parser.add_argument('--merge_template', default='core/constants/merge_table_llm.j2', help='Path to merge table prompt template')
    parser.add_argument('--use_llm', action='store_true', help='Enable LLM processing')
    parser.add_argument('--tess', action='store_true', help='Enable Tesseract OCR processing')
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Check if input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
    else:
        input_path = os.path.abspath(args.input)
        logger.info(f"Input file: {input_path}")
    
    # Create output directory
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create base output directory for BPAI
    bpai_output_dir = "output/bpai"
    os.makedirs(bpai_output_dir, exist_ok=True)
    
    # Create pipeline configuration
    config = {
        "output_dir": bpai_output_dir,
        "use_tesseract": args.tess,
        "use_llm": args.use_llm,
        "marker_processor": {
            "debug_mode": args.debug,
            "enable_caching": True,
            "cache_dir": "cache/marker"
        }
    }
    
    # Add tesseract configuration if enabled
    if args.tess:
        config["add_tesseract_words"] = {
            "debug": args.debug,
            "tolerance": 2,
            "tesseract_path": args.tesseract_path,
            "output_dir": bpai_output_dir,  # Explicitly add output_dir
            "source_path": input_path  # Pass absolute path to ensure it works
        }
        logger.info(f"Tesseract processing enabled with path: {args.tesseract_path}")
    
    # Add LLM processor configuration if enabled
    if args.use_llm:
        config["llm_bpai_processor"] = {
            "model": args.llm_model,
            "max_workers": args.max_workers,
            "bio_template_path": args.bio_template,
            "table_template_path": args.table_template,
            "merge_template_path": args.merge_template,
            "output_dir": os.path.join(bpai_output_dir, "llm_results"),
            "debug": args.debug
        }
        logger.info(f"LLM Processing enabled with model: {args.llm_model}, workers: {args.max_workers}")
    
    # Log key configuration parameters
    logger.info(f"Pipeline configuration: tesseract={args.tess}, llm={args.use_llm}, output_dir={bpai_output_dir}")
    
    # Initialize and run pipeline
    logger.info(f"Initializing BPAI pipeline")
    pipeline = BPAIPipeline(config=config, image_path=input_path)
    
    # Process the document
    logger.info("Processing document...")
    document = pipeline()

    # Get file name from input path
    file_name = os.path.basename(args.input)
    
    # Save full document JSON
    debug_output = os.path.join(os.path.dirname(args.output), f"{file_name}.json")
    logger.info(f"Saving document output to: {debug_output}")
    pipeline.save_to_json(document, debug_output)
    logger.info(f"Processing complete. Output saved to: {debug_output}")


if __name__ == "__main__":
    main()
    # python -m core.pipelines.bpai --debug --use_llm --tess