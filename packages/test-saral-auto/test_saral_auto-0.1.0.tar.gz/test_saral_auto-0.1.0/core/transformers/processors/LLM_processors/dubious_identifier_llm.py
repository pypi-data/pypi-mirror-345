from core.transformers.processors.LLM_processors import BaseLLMProcessor
import os
import json
import base64
import logging
import time
import math
import traceback
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional, Union
from core.schemas.document.document import Document
from core.transformers.processors.LLM_processors.prompt_loader import PromptLoader
from core.constants import EMOJI
from core.transformers.utils.helpers import create_html_json, backmap_html_json, create_page_json
from core.transformers.utils.debug_write import dump_document_with_images

logger = logging.getLogger(__name__)

class DubiousProcessor(BaseLLMProcessor):
    """
    Processor that uses LLM to analyze document content using parallel processing.
    """
    
    def __init__(self, model="gemini-2.0-flash-thinking-exp-01-21", log_level=logging.INFO, 
                 config: Optional[Dict] = None, output_dir: Optional[str] = None):
        """
        Initialize the LLM BPAI processor
        
        Args:
            model (str): The LLM model to use
            log_level (int): Logging level
            config (dict, optional): Configuration options
            output_dir (str, optional): Output directory for saving results
        """
        super().__init__(model=model, log_level=log_level)
        
        # Configuration
        self.config = config or {}
        self.output_dir = output_dir or "output"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Settings for parallel processing
        self.max_workers = self.config.get("max_workers", 2)
        self.batch_size = math.ceil(self.max_workers * 1.5)
        
        # Templates and prompts
        # Get template paths from config or use defaults
        self.bio_template_path = self.config.get("bio_template_path") or "core/constants/bio_prompt.j2"
    
    def __call__(self, document: Document) -> Document:
        """
        Process the document using LLM with parallel processing and integrate results
        
        This function:
        1. Converts the document to a JSON structure
        2. Processes pages in parallel with LLM, identifying strikethrough text
        3. Maps detected strikethrough to block IDs
        4. Integrates LLM results directly into the Document structure
        
        Args:
            document: The document to process
            
        Returns:
            Document: The processed document with integrated LLM results
        """
        try:
            self.logger.info(f"{EMOJI['start']} Starting LLM BPAI processing")
            
            # Extract document data
            pdf_name = os.path.splitext(os.path.basename(document.filepath))[0] if document.filepath else "document"
            self.logger.info(f"Processing document: {pdf_name}")
            
            # Create document-specific output directory
            doc_output_dir = os.path.join(self.output_dir, pdf_name)
            os.makedirs(doc_output_dir, exist_ok=True)
            
            # Determine page numbers to process
            page_numbers = self.config.get("page_numbers")
            if page_numbers is None:
                page_numbers = list(range(len(document.pages)))
            self.logger.info(f"Processing {len(page_numbers)} pages")
            
            # Initialize prompt loaders
            prompt_loader = PromptLoader(self.bio_template_path)
            
            # Process pages in parallel. Will manipulate document in place.
            document = self._process_pages_parallel(
                page_numbers=page_numbers,
                pdf_name=pdf_name,
                document=document,
                prompt_loader=prompt_loader,
                max_workers=self.max_workers,
                api_keys=self.api_keys
            )
            
            self.logger.info(f"{EMOJI['success']} LLM BPAI processing completed with annotations integrated")
            
            try:
                debug_output = os.path.join(self.output_dir, "debug_document_after_llm.json")
                logger.debug(f"Saving debug document to: {debug_output}")
                dump_document_with_images(document, debug_output, indent=2, image_folder_name=f"images", image_key_names=("highres_image",))
            except Exception as e:
                logger.error(f"Failed to save debug document: {str(e)}")
            
            return document # As document is updated in-place
            
        except Exception as e:
            self.logger.error(f"{EMOJI['error']} Error in DubiousProcessor: {str(e)}")
            self.logger.error(traceback.format_exc())
            return document
    
    def _process_pages_parallel(self, page_numbers: list, pdf_name: str, document: Document,
                               prompt_loader, 
                               max_workers: int = 2, api_keys: list = None) -> Document:
        """
        Process multiple pages in parallel using ThreadPoolExecutor with rate limiting
        
        Args:
            page_numbers (list): List of page numbers to process
            pdf_name (str): Name of the PDF file
            document (Document): The document being processed
            prompt_loader: Prompt loader instance
            max_workers (int, optional): Maximum number of worker threads. Defaults to 2.
            api_keys (list, optional): List of API keys to distribute across workers.
                                     If provided, keys will be assigned round-robin to pages.
        
        Returns:
            Document: The processed document with integrated LLM results
        """
        page_with_response = {}
        
        self.logger.info(f"{EMOJI['start']} Starting parallel processing")
        self.logger.info(f"{EMOJI['page']} Processing {len(page_numbers)} pages with {max_workers} workers")
        
        if api_keys:
            self.logger.info(f"{EMOJI['key']} Using {len(api_keys)} API keys for distributed processing")
        
        # Process pages in smaller batches to avoid rate limits
        batch_size = math.ceil(max_workers * 1.5)
        for i in range(0, len(page_numbers), batch_size):
            batch = page_numbers[i:i + batch_size]
            self.logger.info(f"\nProcessing batch {i//batch_size + 1} of {(len(page_numbers) + batch_size - 1)//batch_size}")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                
                for idx, page in enumerate(batch):
                    
                    futures[executor.submit(
                        self._process_single_page, 
                        page, 
                        pdf_name, 
                        document, 
                        prompt_loader,
                    )] = page
        
        return document
    
    def _process_single_page(self, page: int, pdf_name: str, document: Document,
                            prompt_loader) -> tuple:
        """
        Process a single page of the document and return its processed data
        
        Args:
            page (int): Page number to process
            pdf_name (str): Name of the PDF file
            document (Document): The document being processed
            prompt_loader: Prompt loader instance
            api_key (str, optional): API key to use for this page. If provided, will override the processor's API key.
        
        Returns:
            tuple: (page number, processed JSON data) and will manipulate document in place.
        """
        try:
            self.logger.info(f"{EMOJI['page']} Strikethrough analysis for page {page + 1}")
            
            # Step 1: Create HTML JSON structure
            self.logger.info(f"{EMOJI['processing']} Creating HTML structure")
            html_json = create_html_json(document, page=page, pdf_name=pdf_name, output_dir=self.output_dir)
            
            # Find image path from document processor
            img_path = os.path.join(self.output_dir, pdf_name, f"page_{page}", f"page_{page}.png")
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: {img_path}")
            
            self.logger.debug(f"{EMOJI['image']} Reading image for page {page + 1}")
            with open(img_path, "rb") as image_file:
                img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Step 3: Get strikethrough analysis
            self.logger.info(f"{EMOJI['processing']} Step 1: Analyzing content")
            bio_prompt = prompt_loader.get_prompt("bio_prompt")
            
            # Make LLM call with the provided API key
            bio_response = self.process_image(
                user_prompt=bio_prompt, 
                image_base64_list=img_base64,
                model=self.model,
                type_json=True
            )
            
            try:
                # Handle both string and parsed JSON responses
                bio_json = bio_response if isinstance(bio_response, (list, dict)) else json.loads(bio_response)
                
                # Save bio analysis
                bio_path = os.path.join(self.output_dir, pdf_name, f"page_{page}", f"bio_response.json")
                with open(bio_path, "w", encoding='utf-8') as f:
                    json.dump(bio_json, f, ensure_ascii=False, indent=2)
                self.logger.debug(f"{EMOJI['save']} Saved bio analysis to {bio_path}")

                # If bio_json is empty then nothing to do
                if len(bio_json) == 0:
                    self.logger.info(f"No strikethrough analysis found for page {page + 1}")
                    return (page, document)
                
                # Step 4: Map to actual cell IDs
                self.logger.info(f"{EMOJI['processing']} Step 2: Mapping to cell IDs")
                mapping_prompt = prompt_loader.get_prompt("bio_mapping_prompt", html_json=html_json, strikethrough_json=bio_json)
                
                # Make LLM call with the provided API key
                mapping_response = self.process_image(
                    user_prompt=mapping_prompt, 
                    image_base64_list=img_base64,
                    model=self.model,
                    type_json=True
                )

                try:
                    # Handle both string and parsed JSON responses
                    mapping_json = mapping_response if isinstance(mapping_response, (list, dict)) else json.loads(mapping_response)
                    
                    # Save mapping response
                    mapping_path = os.path.join(self.output_dir, pdf_name, f"page_{page}", f"mapping_response.json")
                    with open(mapping_path, "w", encoding='utf-8') as f:
                        json.dump(mapping_json, f, ensure_ascii=False, indent=2)
                    self.logger.debug(f"{EMOJI['save']} Saved mapping response to {mapping_path}")
                    
                    # Step 5: Backmap the results
                    self.logger.info(f"{EMOJI['processing']} Backmapping results")
                    document = backmap_html_json(document, mapping_json, page=page, pdf_name=pdf_name, output_dir=self.output_dir)
                    
                    self.logger.info(f"{EMOJI['success']} Successfully processed page {page + 1}")
                    return (page, document)
                    
                except (json.JSONDecodeError, TypeError) as e:
                    self.logger.error(f"{EMOJI['error']} Error parsing mapping response: {str(e)}")
                    self.logger.debug(f"Response preview: {mapping_response[:200] if isinstance(mapping_response, str) else str(mapping_response)[:200]}...")
                    
                    # Save error response
                    error_path = os.path.join(self.output_dir, pdf_name, f"page_{page}", f"mapping_error_response.txt")
                    with open(error_path, "w", encoding='utf-8') as f:
                        f.write(str(mapping_response))
                    self.logger.debug(f"{EMOJI['save']} Saved mapping error response to {error_path}")
                    return (page, None)
                    
            except (json.JSONDecodeError, TypeError) as e:
                self.logger.error(f"{EMOJI['error']} Error parsing bio response: {str(e)}")
                self.logger.debug(f"Response preview: {bio_response[:200] if isinstance(bio_response, str) else str(bio_response)[:200]}...")
                
                # Save error response
                error_path = os.path.join(self.output_dir, pdf_name, f"page_{page}", f"bio_error_response.txt")
                with open(error_path, "w", encoding='utf-8') as f:
                    f.write(str(bio_response))
                self.logger.debug(f"{EMOJI['save']} Saved bio error response to {error_path}")
                return (page, None)
                
        except Exception as e:
            self.logger.error(f"{EMOJI['error']} Error processing page {page + 1}: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return (page, None)
    
    def _get_page_image_path(self, document: Document, page: int, pdf_name: str) -> str:
        """
        Get the path to the page image
        
        Args:
            document: The document
            page: Page number
            pdf_name: Name of the PDF file
            
        Returns:
            str: Path to the page image
        """
        # Try multiple possible locations for the page image
        possible_paths = [
            os.path.join(self.output_dir, pdf_name, f"page_{page}", f"{pdf_name}_page_{page}.png"),
            os.path.join("parser", "test", "outputs", pdf_name, f"{pdf_name}_page_{page}", f"{pdf_name}_page_{page}.png"),
            os.path.join("temp", pdf_name, f"page_{page}", f"{pdf_name}_page_{page}.png")
        ]
        
        # Check if tesseract processor has created images
        if hasattr(document, 'metadata') and 'tesseract_path' in document.metadata:
            tesseract_dir = os.path.dirname(document.metadata['tesseract_path'])
            possible_paths.append(os.path.join(tesseract_dir, f"{pdf_name}", f"page_{page}", f"{pdf_name}_page_{page}.png"))
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no path found, return the first path as default
        return possible_paths[0]
