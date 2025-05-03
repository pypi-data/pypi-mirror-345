from core.transformers.processors import BaseProcessor
from core.transformers.utils.image_processing import preprocess_img_for_ocr
import logging
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
import os
import base64
from io import BytesIO
import pymupdf
from PIL import Image
import pytesseract

from core.schemas.document.document import Document
from core.schemas.document.blocks import Block
from core.schemas.document.blocks.base import BlockMetadata
from core.transformers.utils.debug_write import dump_document_with_images

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TesseractConfig(BaseModel):
    tolerance: int = 2
    page_numbers: Optional[List[int]] = None
    debug: bool = False
    tesseract_path: str

class AddTesseractWords(BaseProcessor):
    """
    Processor that adds Tesseract OCR words to blocks in a document.
    
    This processor loads Tesseract OCR results from a JSON file and adds the words
    to each leaf block in the document based on whether they fall within the 
    block's bounding box.
    """
    
    def __init__(self, config: Optional[Union[TesseractConfig, dict]] = None, 
                 checkpoint_dir: Optional[str] = None, output_dir: Optional[str] = None,
                 source_path: Optional[str] = None):
        """
        Initialize the processor.
        
        Args:
            config: Configuration with processing parameters
            checkpoint_dir: Directory to store checkpoint data
            output_dir: Output directory for storing and finding files
            source_path: Path to the source PDF file
        """
        super().__init__(config, checkpoint_dir)
        
        # Store the config
        self.config = config or {}
        
        # Store output directory
        self.output_dir = output_dir
        
        # Store source path
        self.source_path = source_path
        if (source_path):
            logger.info(f"AddTesseractWords initialized with source_path: {source_path}")
        
        # Default configuration
        self.tolerance = 2
        self.page_numbers = None
        self.debug = False
        self.tesseract_path = None
        
        # Override defaults with config if provided
        if (config):
            if (isinstance(config, dict)):
                self.tolerance = config.get('tolerance', self.tolerance)
                self.page_numbers = config.get('page_numbers', self.page_numbers)
                self.debug = config.get('debug', self.debug)
                self.tesseract_path = config.get('tesseract_path')
                # Allow setting source_path through config as well
                if (not self.source_path and config.get('source_path')):
                    self.source_path = config.get('source_path')
                    logger.info(f"Using source_path from config: {self.source_path}")
            else:
                self.tolerance = config.tolerance
                self.page_numbers = config.page_numbers
                self.debug = config.debug
                self.tesseract_path = getattr(config, 'tesseract_path', None)
                # Allow setting source_path through config as well
                if (not self.source_path and getattr(config, 'source_path', None)):
                    self.source_path = getattr(config, 'source_path', None)
                    logger.info(f"Using source_path from config object: {self.source_path}")
        
        # If tesseract_path is not provided, use a default path in output_dir
        if (not self.tesseract_path and self.output_dir):
            self.tesseract_path = os.path.join(self.output_dir, "tesseract_results.json")
            logger.info(f"No tesseract_path provided. Using default: {self.tesseract_path}")
        
        # Store initialization checkpoint
        self._checkpoint("init", {
            "tolerance": self.tolerance,
            "page_numbers": self.page_numbers,
            "debug": self.debug,
            "tesseract_path": self.tesseract_path,
            "output_dir": self.output_dir,
            "source_path": self.source_path
        })
    
    def _log_debug(self, message: str):
        """Log debug message if debug mode is enabled."""
        if (self.debug):
            logger.info(message)
    
    def _get_block_bbox(self, block: Block) -> Optional[tuple]:
        """
        Return the block's bounding box as a tuple (x_min, y_min, x_max, y_max).
        Uses the polygon's bbox property.
        
        Args:
            block: The block to get the bounding box for
            
        Returns:
            tuple: A tuple (x_min, y_min, x_max, y_max) or None if no polygon
        """
        if (hasattr(block, 'polygon') and block.polygon):
            bbox = block.polygon.bbox
            self._log_debug(f"Using bbox for block {block.id}: {bbox}")
            return bbox
        else:
            self._log_debug(f"No polygon found for block {block.id}")
            return None
    
    def _process_block(self, block: Block, page_words: List[Dict[str, Any]], document: Document) -> Block:
        """
        Process a block, adding Tesseract words if it's a leaf block.
        
        Args:
            block: The block to process
            page_words: List of Tesseract words for the page
            document: The document containing the block
            
        Returns:
            Block: The processed block
        """
        self._log_debug(f"Processing block id: {block.id}")
        
        # If the block is a leaf node (no structure) and has a bounding box,
        # add the matching Tesseract words
        if (not hasattr(block, 'structure') or block.structure is None or len(block.structure) == 0):
            block_bbox = self._get_block_bbox(block)
            if (block_bbox is not None):
                sec_x_min, sec_y_min, sec_x_max, sec_y_max = block_bbox
                words_in_block = []
                
                for word in page_words:
                    bbox_data = word.get("bbox")
                    if (not bbox_data):
                        continue
                    
                    # Extract word bounding box
                    w_x_min = bbox_data.get("x")
                    w_y_min = bbox_data.get("y")
                    w_width = bbox_data.get("width", 0)
                    w_height = bbox_data.get("height", 0)
                    w_x_max = w_x_min + w_width
                    w_y_max = w_y_min + w_height
                    
                    self._log_debug(f"Checking word '{word.get('text')}' with bbox: {[w_x_min, w_y_min, w_x_max, w_y_max]}")
                    self._log_debug(f"Against block bbox: {[sec_x_min, sec_y_min, sec_x_max, sec_y_max]} with tolerance {self.tolerance}")
                    
                    # Check if the word is within the block bounding box (with tolerance)
                    if (w_x_min >= sec_x_min - self.tolerance and
                        w_y_min >= sec_y_min - self.tolerance and
                        w_x_max <= sec_x_max + self.tolerance and
                        w_y_max <= sec_y_max + self.tolerance):
                        self._log_debug(f"--> Word '{word.get('text')}' is inside block bbox")
                        words_in_block.append(word)
                    else:
                        self._log_debug(f"--> Word '{word.get('text')}' is NOT inside block bbox")
                
                # Add the words to the block as metadata
                if (not hasattr(block, 'metadata') or block.metadata is None):
                    try:
                        # Try to set metadata attribute
                        block.metadata = {}
                    except Exception as e:
                        logger.warning(f"Could not create metadata dict: {str(e)}")
                        # Try using __dict__ directly as fallback
                        try:
                            block.__dict__['metadata'] = {}
                        except Exception as e2:
                            logger.error(f"Could not set metadata via __dict__: {str(e2)}")
                            return block
                
                try:
                    if (isinstance(block.metadata, dict)):
                        block.metadata["tesseract_words"] = words_in_block
                        self._log_debug(f"Added {len(words_in_block)} words to block {block.id}")
                    else:
                        # If it's a BlockMetadata, add words as attribute
                        try:
                            setattr(block.metadata, "tesseract_words", words_in_block)
                            self._log_debug(f"Added {len(words_in_block)} words to block {block.id} metadata object")
                        except Exception as e:
                            logger.warning(f"Could not set tesseract_words attribute: {str(e)}")
                            # Try using __dict__ directly as fallback
                            try:
                                block.metadata.__dict__['tesseract_words'] = words_in_block
                            except Exception as e2:
                                logger.error(f"Could not set tesseract_words via __dict__: {str(e2)}")
                except Exception as e:
                    logger.error(f"Failed to add tesseract words to metadata: {str(e)}")
        
        # Process children recursively if they exist
        if (hasattr(block, 'structure') and block.structure):
            for child_id in block.structure:
                if (hasattr(block, 'page_id')):
                    # If this is a top-level block
                    from_page = document.get_page(block.page_id)
                    child = from_page.get_block(child_id)
                    if (child):
                        self._process_block(child, page_words, document)
                elif (hasattr(block, 'get_block')):
                    # If this is a page or group
                    child = block.get_block(child_id)
                    if (child):
                        self._process_block(child, page_words, document)
        
        return block
    
    def __call__(self, document: Document) -> Document:
        """
        Process the document, adding Tesseract words to blocks.
        
        Args:
            document: The document to process
            
        Returns:
            Document: The processed document
        """
        try:
            logger.info("Starting AddTesseractWords processor")
            
            # Check for cached results
            if (self._enable_caching):
                cached_doc = self._get_cache(document)
                if (cached_doc is not None):
                    logger.info(f"{self.__class__.__name__}: Using cached result")
                    return cached_doc

            
            # Try to find the PDF path from multiple sources in order of priority
            pdf_path = None
            
            # 1. Try our explicitly set source_path from config first
            if (self.source_path):
                pdf_path = self.source_path
                logger.info(f"Using source_path from config: {pdf_path}")
            
            # 2. If no source_path in config, check document.filepath
            if (not pdf_path and hasattr(document, 'filepath') and document.filepath):
                pdf_path = document.filepath
                logger.info(f"Using document.filepath: {pdf_path}")
            
            logger.info(f"PDF path resolved to: {pdf_path}")
            
            # Process PDF if we have a valid path
            tesseract_json = {}  # Default empty dict
            
            if (pdf_path and os.path.exists(pdf_path)):
                logger.info(f"PDF file exists at: {pdf_path}")
                
                # Run the process function to generate OCR results
                tesseract_json = self.process(pdf_path, self.page_numbers)
                
                # Log summary of tesseract results
                if (tesseract_json):
                    logger.info(f"Generated tesseract_json with {len(tesseract_json)} pages")
                    for page_num in tesseract_json:
                        page_data = tesseract_json[page_num]
                        word_count = len(page_data.get("words", []))
                        logger.debug(f"Page {page_num}: {word_count} words")
                
                logger.info(f"Generated Tesseract OCR results and saved to {self.tesseract_path}")
            else:
                if (pdf_path):
                    logger.error(f"PDF file not found at: {pdf_path}")
                else:
                    logger.error("No PDF path found from any source")
            
            # Process each page in the document
            self._checkpoint("processing_start", {
                "document_pages": len(document.pages),
                "tesseract_pages": len(tesseract_json) if (isinstance(tesseract_json, dict)) else 0
            })
            
            for page in document.pages:
                # Extract the page number
                page_num = page.page_id
                
                # Skip if page_numbers is specified and this page is not in the list
                if (self.page_numbers is not None and page_num not in self.page_numbers):
                    self._log_debug(f"Skipping page number {page_num} as it's not in {self.page_numbers}")
                    continue
                
                # Check if there's Tesseract data for this page
                if (page_num not in tesseract_json):
                    self._log_debug(f"No Tesseract data for page {page_num}")
                    continue
                
                # Get the words for this page
                page_words = tesseract_json[page_num].get("words", [])
                self._log_debug(f"Page {page_num} has {len(page_words)} words")
                logger.info(f"Processing page {page_num} with {len(page_words)} tesseract words")
                
                # Process the page
                self._checkpoint("processing_page", {
                    "page_id": page_num,
                    "words_count": len(page_words)
                })
                
                # Check if page has structure before processing blocks
                if (not hasattr(page, 'structure') or page.structure is None):
                    logger.warning(f"Page {page_num} has no structure. Creating empty structure.")
                    page.structure = []
                    
                    # Add tesseract words directly to page metadata
                    self._add_tesseract_to_page(page, page_words)
                    
                    # Try to add the page itself as a block to process
                    if (hasattr(page, 'polygon') and page.polygon):
                        logger.info(f"Processing page {page_num} as a single block")
                        self._process_block(page, page_words, document)
                    continue
                
                # Add tesseract words directly to page metadata
                # self._add_tesseract_to_page(page, page_words)
                self._add_words_to_children(page, page_words)

                # Process each block in the page
                for block_id in page.structure:
                    block = page.get_block(block_id)
                    if (block):
                        self._process_block(block, page_words, document)
                
                # Page processing complete
                self._checkpoint("page_complete", {
                    "page_id": page_num
                })
            
            # Mark processing as completed
            self._mark_completed({
                "document_id": getattr(document, "id", None),
                "pages_processed": len(document.pages),
                "timestamp": str(self._current_timestamp())
            })
            
            # Verify tesseract words were added to the document
            word_count = 0
            
            # Count words in page metadata
            for page in document.pages:
                if (hasattr(page, 'metadata') and page.metadata):
                    if (isinstance(page.metadata, dict) and "tesseract_words" in page.metadata):
                        words = page.metadata["tesseract_words"]
                        if (words):
                            word_count += len(words)
            
            # Count words in block metadata
            for page in document.pages:
                try:
                    blocks = page.contained_blocks(document)
                    if (not blocks):
                        logger.warning(f"No valid blocks found for page {page.page_id}. Skipping.")
                        continue
                except Exception as e:
                        logger.error(f"__call__ Error while retrieving blocks for page {page.page_id}: {str(e)}")
                        continue
                for block in blocks:
                    if (hasattr(block, 'metadata') and block.metadata):
                        if (isinstance(block.metadata, dict) and "tesseract_words" in block.metadata):
                            words = block.metadata["tesseract_words"]
                            if (words):
                                word_count += len(words)
            
            logger.info(f"Total tesseract words added to blocks and pages: {word_count}")
            
            # for page in document.pages:
            #     page_num = page.page_id
            #     # if page_num not in tesseract_json:
            #     #     continue

            #     page_words = tesseract_json[page_num].get("words", [])
            #     logger.info(f"Processing page {page_num} with {len(page_words)} tesseract words")

            #     # Add words to the metadata of each child block
            #     self._add_words_to_children(page, page_words)
                
            # Add Tesseract words to the metadata of each page in the document
            # for page in document.pages:
            #     page_id = page.page_id
                
            #     # Skip if page_numbers is specified and this page is not in the list
            #     if (self.page_numbers is not None and page_id not in self.page_numbers):
            #         logger.debug(f"Skipping page number {page_id} as it's not in {self.page_numbers}")
            #         continue
                
            #     # Check if there's Tesseract data for this page
            #     if (str(page_id) not in tesseract_json):
            #         logger.debug(f"No Tesseract data for page {page_id}")
            #         continue
                
            #     # Get the words for this page
            #     page_words = tesseract_json[str(page_id)].get("words", [])
            #     logger.info(f"Adding {len(page_words)} words to metadata of page {page_id}")
                
            #     # Add words to the page's metadata
            #     if (not hasattr(page, 'metadata') or page.metadata is None):
            #         page.metadata = {}
                
            #     if (isinstance(page.metadata, dict)):
            #         page.metadata["words"] = page_words
            #     else:
            #         try:
            #             setattr(page.metadata, "words", page_words)
            #         except Exception as e:
            #             logger.warning(f"Could not set 'words' attribute on page metadata: {str(e)}")

            # Save a dedicated tesseract results file that includes the blocks and their tesseract words
            if (self.output_dir):
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0] if (pdf_path) else "document"
                tesseract_results_path = os.path.join(self.output_dir, f"{pdf_name}_tesseract_blocks.json")
                self.save_tesseract_results_to_json(document, tesseract_results_path)
            
            # Cache the result
            if (self._enable_caching):
                self._set_cache(document, document)
            
            try:
                debug_output = os.path.join(self.output_dir, "debug_document_after_tesseract.json")
                logger.debug(f"Saving debug document to: {debug_output}")
                dump_document_with_images(document, debug_output, indent=2, image_folder_name=f"images", image_key_names=("highres_image",))
            except Exception as e:
                logger.error(f"Failed to save debug document: {str(e)}")

            return document
            
        except Exception as e:
            # Error checkpoint
            self._checkpoint("error", {
                "error": str(e),
                "stage": "add_tesseract_words"
            })
            logger.error(f"Error in AddTesseractWords: {str(e)}")
            import traceback
            traceback.print_exc()
            return document
    
    def _current_timestamp(self):
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now()

    def process(self, pdf_path, page_numbers=None):
        """
        Process PDF and extract words using OCR for use with the AddTesseractWords processor.
        
        Args:
            pdf_path: Path to the PDF file
            page_numbers: List of page numbers to process, if None process all pages
            
        Returns:
            dict: Results containing words and other metadata for each page
        """
        try:
            logger.info(f"\n==== STARTING OCR PROCESSING FOR: {pdf_path} ====")
            results = {}
            
            # Check if PDF file exists
            if (not os.path.exists(pdf_path)):
                logger.error(f"ERROR: PDF file does not exist: {pdf_path}")
                return {}
                
            try:
                pdf_document = pymupdf.open(pdf_path)
                logger.info(f"Successfully opened PDF with {len(pdf_document)} pages")
            except Exception as e:
                logger.error(f"ERROR: Failed to open PDF with pymupdf: {str(e)}")
                return {}
                
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            logger.info(f"Processing PDF: {pdf_name}")
            
            # If page_numbers is not provided, process all pages
            if (page_numbers is None):
                page_numbers = list(range(len(pdf_document)))
                logger.info(f"No page numbers specified, processing all {len(page_numbers)} pages")
            else:
                logger.info(f"Processing {len(page_numbers)} specified pages")
            
            # Get output directory
            output_dir = self.output_dir
            logger.info(f"Output directory: {output_dir}")
            
            # Check if we have a pre-created folder structure from BPAI.__init__
            pdf_folder = os.path.join(output_dir, pdf_name)
            logger.info(f"PDF folder: {pdf_folder}")

            for page_num in page_numbers:
                logger.info(f"\n==== Processing PDF page {page_num + 1}/{len(page_numbers)} [{pdf_name}] ====")
                
                if (page_num >= len(pdf_document)):
                    logger.error(f"ERROR: Page number {page_num} out of range (PDF has {len(pdf_document)} pages)")
                    results[page_num] = {"error": "Page number out of range"}
                    continue

                try:
                    page = pdf_document[page_num]
                    logger.info(f"Successfully loaded page {page_num}")
                except Exception as e:
                    logger.error(f"ERROR: Failed to load page {page_num}: {str(e)}")
                    results[page_num] = {"error": f"Failed to load page: {str(e)}"}
                    continue
                
                # Use pre-created page directory or create if it doesn't exist
                page_dir = os.path.join(pdf_folder, f"page_{page_num}")
                if (not os.path.exists(page_dir)):
                    logger.info(f"Creating page directory: {page_dir}")
                    os.makedirs(page_dir, exist_ok=True)
                
                # Process page image
                try:
                    logger.info("Getting page pixmap...")
                    pix = page.get_pixmap()
                    logger.info(f"Pixmap dimensions: {pix.width}x{pix.height}")
                    
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    logger.info("Successfully created PIL Image from pixmap")
                    
                    # Save page image
                    page_img_path = os.path.join(page_dir, f"{pdf_name}_page_{page_num}.png")
                    logger.info(f"Saving page image to: {page_img_path}")
                    img.save(page_img_path, "PNG")
                    
                    if (os.path.exists(page_img_path)):
                        logger.info(f"Successfully saved page image: {page_img_path}")
                    else:
                        logger.warning(f"WARNING: File was not saved: {page_img_path}")
                except Exception as e:
                    logger.error(f"ERROR: Failed to process page image: {str(e)}")
                    results[page_num] = {"error": f"Failed to process page image: {str(e)}"}
                    continue

                # Preprocess the image
                try:
                    logger.info("Preprocessing image for OCR...")
                    processed_img = preprocess_img_for_ocr(img, grayscale=True, contrast=True, threshold=True)
                    logger.info("Successfully preprocessed image")
                    
                    preprocessed_img_path = os.path.join(page_dir, f"pre_{pdf_name}_page_{page_num}.png")
                    logger.info(f"Saving preprocessed image to: {preprocessed_img_path}")
                    processed_img.save(preprocessed_img_path, "PNG")
                    
                    if (os.path.exists(preprocessed_img_path)):
                        logger.info(f"Successfully saved preprocessed image: {preprocessed_img_path}")
                    else:
                        logger.warning(f"WARNING: Preprocessed image file was not saved: {preprocessed_img_path}")
                except Exception as e:
                    logger.error(f"ERROR: Failed to preprocess image: {str(e)}")
                    # Continue with original image
                    processed_img = img
                    logger.info("Using original image for OCR due to preprocessing error")

                # Initialize page result
                page_result = {
                    "words": [],
                    "height": pix.height,
                    "width": pix.width
                }

                # Run OCR with pytesseract
                try:
                    logger.info("Running OCR with pytesseract...")
                    confidence_threshold = getattr(self, 'confidence_threshold', 0)
                    logger.info(f"Confidence threshold: {confidence_threshold}")
                    
                    # Configure Tesseract for optimal document parsing
                    config = (
                        '--oem 2'
                        ' --psm 11'
                        ' -l eng'
                    )
                    logger.info(f"Tesseract config: {config}")
                    
                    ocr_data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT, config=config)
                    logger.info(f"OCR complete. Found {len(ocr_data['text'])} potential text elements")
                    
                    words = []
                    for i in range(len(ocr_data["text"])):
                        if (ocr_data["text"][i].strip()):
                            confidence = ocr_data["conf"][i]
                            if (confidence >= confidence_threshold):
                                word_data = {
                                    "text": ocr_data["text"][i],
                                    "bbox": {
                                        "x": ocr_data["left"][i],
                                        "y": ocr_data["top"][i],
                                        "width": ocr_data["width"][i],
                                        "height": ocr_data["height"][i],
                                    },
                                    "confidence": confidence,
                                    "line_num": ocr_data["line_num"][i],
                                    "block_num": ocr_data["block_num"][i],
                                    "paragraph_num": ocr_data["par_num"][i],
                                }
                                words.append(word_data)
                    
                    page_result["words"] = words
                    logger.info(f"Found {len(words)} words with confidence >= {confidence_threshold}")
                except Exception as e:
                    logger.error(f"ERROR: OCR processing failed: {str(e)}")
                    page_result["error"] = f"OCR processing failed: {str(e)}"

                # Add base64 of original image
                try:
                    logger.info("Encoding image as base64...")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    page_result["base64"] = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    logger.info("Successfully encoded image as base64")
                except Exception as e:
                    logger.error(f"ERROR: Failed to encode image as base64: {str(e)}")

                results[page_num] = page_result
                logger.info(f"Completed processing for page {page_num}")

            # Save results to the debug folder / pdf_name folder
            debug_results_path = os.path.join(pdf_folder, f"{pdf_name}_tesseract_results.json")
            logger.info(f"\nSaving OCR results to debug folder: {debug_results_path}")
            
            try:
                with open(debug_results_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Successfully saved results to debug folder: {debug_results_path}")
            except Exception as e:
                logger.error(f"ERROR: Failed to save results to debug folder: {str(e)}")
            
            # Save results to the tesseract_path
            if (self.tesseract_path):
                logger.info(f"Saving OCR results to tesseract path: {self.tesseract_path}")
                try:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(self.tesseract_path), exist_ok=True)
                    
                    with open(self.tesseract_path, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2)
                    logger.info(f"Successfully saved results to tesseract path: {self.tesseract_path}")
                except Exception as e:
                    logger.error(f"ERROR: Failed to save results to tesseract path: {str(e)}")
            
            logger.info(f"\n==== COMPLETED OCR PROCESSING FOR: {pdf_path} ====")
            return results

        except Exception as e:
            logger.error(f"CRITICAL ERROR in process function: {str(e)}")
            logger.error(f"Error in AddTesseractWords.process: {str(e)}")
            raise
            
    def save_tesseract_results_to_json(self, document: Document, output_path: str) -> None:
        """
        Save tesseract results from the document blocks to a dedicated JSON file.
        
        Args:
            document: The document with tesseract words
            output_path: Path to save the output JSON
        """
        try:
            logger.info(f"Saving tesseract results to: {output_path}")
            
            # Get document structure using marshal() to work with
            doc_json = document.marshal()
            
            # Create a dictionary to hold all the tesseract words by page and block
            results = {}
            
            for page in document.pages:
                page_id = page.page_id
                results[page_id] = {
                    "page_id": page_id,
                    "blocks": []
                }
                
                # Check if the page itself has tesseract words in metadata
                if (hasattr(page, 'metadata') and page.metadata):
                    tesseract_words = None
                    
                    # Try to get tesseract_words from page metadata
                    if (isinstance(page.metadata, dict) and "tesseract_words" in page.metadata):
                        tesseract_words = page.metadata["tesseract_words"]
                    elif (hasattr(page.metadata, "tesseract_words")):
                        tesseract_words = page.metadata.tesseract_words
                    
                    if (tesseract_words):
                        # Add page-level tesseract words
                        results[page_id]["page_words"] = tesseract_words
                        logger.debug(f"Found {len(tesseract_words)} words in page {page_id} metadata")
                
                # Get all blocks in the page
                try:
                    blocks = page.contained_blocks(document)
                    if (not blocks):
                        logger.warning(f"No valid blocks found for page {page_id}. Skipping.")
                        continue
                except Exception as e:
                    logger.error(f"save_tesseract_Error while retrieving blocks for page {page_id}: {str(e)}")
                    continue
                
                for block in blocks:
                    # Check if the block has tesseract words
                    if (hasattr(block, 'metadata') and block.metadata):
                        tesseract_words = None
                        
                        # Try to get tesseract_words from metadata
                        if (isinstance(block.metadata, dict) and "tesseract_words" in block.metadata):
                            tesseract_words = block.metadata["tesseract_words"]
                        elif (hasattr(block.metadata, "tesseract_words")):
                            tesseract_words = block.metadata.tesseract_words
                        
                        if (tesseract_words):
                            # Add block with its tesseract words
                            block_data = {
                                "block_id": str(block.id),
                                "block_type": str(block.block_type),
                                "polygon": block.polygon.to_dict() if (block.polygon) else None,
                                "tesseract_words": tesseract_words
                            }
                            
                            # Add text if available
                            if (hasattr(block, 'text')):
                                block_data["text"] = block.text
                                
                            results[page_id]["blocks"].append(block_data)
            
            # Add summary stats
            block_count = sum(len(page_data["blocks"]) for page_data in results.values())
            word_count = 0
            
            # Count words in blocks
            for page_data in results.values():
                for block_data in page_data["blocks"]:
                    word_count += len(block_data.get("tesseract_words", []))
                
                # Count words in page metadata
                if ("page_words" in page_data):
                    word_count += len(page_data["page_words"])
            
            summary = {
                "document_path": document.filepath,
                "pages": len(results),
                "blocks_with_words": block_count,
                "total_words": word_count,
                "tesseract_path": self.tesseract_path
            }
            
            # Add the summary to the results
            output_data = {
                "summary": summary,
                "pages": results
            }
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Successfully saved tesseract results to: {output_path}")
            logger.info(f"Summary: {block_count} blocks with {word_count} words across {len(results)} pages")
            
        except Exception as e:
            logger.error(f"Error saving tesseract results: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def _add_words_to_children(self, page, page_words):
        """
        Add Tesseract words to the metadata of each leaf child block of the page
        if the word's bbox is contained within the child's polygon.bbox.

        Args:
            page: The page object containing child blocks.
            page_words: List of Tesseract words for the page.
        """
        try:
            scaling_factor = 1.5  # Scaling factor to downscale the word bbox

            def process_child(child, page_words):
                """
                Recursively process a child block to add Tesseract words to its metadata
                if it is a leaf node.
                """
                try:
                    # If the child has further children, process them recursively
                    if hasattr(child, 'children') and child.children:
                        for grandchild in child.children:
                            process_child(grandchild, page_words)
                        return  # Skip adding words to non-leaf nodes

                    # Skip children without a valid polygon or bounding box
                    if not hasattr(child, 'polygon') or not child.polygon or not child.polygon.bbox:
                        return

                    if not hasattr(child, 'metadata') or child.metadata is None:
                        try:
                            child.metadata = {}
                        except Exception as e:
                            logger.warning(f"Could not create child metadata dict: {str(e)}")
                            try:
                                child.__dict__['metadata'] = {}
                            except Exception as e2:
                                logger.error(f"Could not set page metadata via __dict__: {str(e2)}")
                                return

                    child_bbox = child.polygon.bbox  # [x_min, y_min, x_max, y_max]
                    words_in_child = []

                    for word in page_words:
                        try:
                            word_bbox = word.get("bbox")
                            if not word_bbox:
                                continue

                            # Downscale the word's bounding box
                            w_x_min = word_bbox.get("x") / scaling_factor
                            w_y_min = word_bbox.get("y") / scaling_factor
                            w_x_max = (word_bbox.get("x") + word_bbox.get("width", 0)) / scaling_factor
                            w_y_max = (word_bbox.get("y") + word_bbox.get("height", 0)) / scaling_factor

                            # Check if the word's bbox is within the child's bbox
                            if (w_x_min >= child_bbox[0] and w_y_min >= child_bbox[1] and
                                w_x_max <= child_bbox[2] and w_y_max <= child_bbox[3]):
                                words_in_child.append(word)
                        except Exception as e:
                            logger.warning(f"Error processing word bbox: {str(e)}")

                    # Add the words to the child's metadata
                    if words_in_child:
                        try:
                            if isinstance(child.metadata, dict):
                                child.metadata["tesseract_words"] = words_in_child
                                logger.info(f"Added {len(words_in_child)} words to leaf child metadata")
                            else:
                                try:
                                    setattr(child.metadata, "tesseract_words", words_in_child)
                                    logger.info(f"Added {len(words_in_child)} words to leaf child metadata object")
                                except Exception as e:
                                    logger.warning(f"Could not set tesseract_words attribute on child: {str(e)}")
                                    try:
                                        child.metadata.__dict__['tesseract_words'] = words_in_child
                                    except Exception as e2:
                                        logger.error(f"Could not set tesseract_words on child via __dict__: {str(e2)}")
                        except Exception as e:
                            logger.error(f"Error adding words to child metadata: {str(e)}")

                except Exception as e:
                    logger.error(f"Error processing child block: {str(e)}")

            # Process each child of the page
            for child in page.children:
                process_child(child, page_words)

        except Exception as e:
            logger.critical(f"Critical error in _add_words_to_children: {str(e)}")


# TODO:
# Segregate different image processing operations in different functions already present in transformers.
# Correct Serialization error in document schema to json and use it in pipeline