import os
import math
import json
import base64
import logging
import traceback
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from  constants import EMOJI
from core.schemas.document.document import Document, BlockId
from core.schemas.document import BlockTypes
from core.schemas.document.groups.page import PageGroup
from core.schemas.document.polygon import PolygonBox
from core.transformers.processors.LLM_processors import BaseLLMProcessor
from core.transformers.processors.LLM_processors.prompt_loader import PromptLoader
from core.transformers.utils.debug_write import dump_document_with_images
from core.transformers.utils.helpers import crop_image_to_table, find_all_tables, create_table_html

logger = logging.getLogger(__name__)

class TableIdentifierLLMProcessor(BaseLLMProcessor):
    """
    Process tables in PDF documents using LLM
    Combines table identification and processing in one unified class
    """
    
    def __init__(self, model="gemini-2.0-flash-thinking-exp-01-21", log_level=logging.INFO, 
                 config: Optional[Dict] = None, output_dir: Optional[str] = None,
                 prompt_loader=None):
        """
        Initialize TableProcessor
        
        Args:
            model (str): The LLM model to use
            log_level (int): Logging level
            config (dict, optional): Configuration options
            output_dir (str, optional): Output directory for saving results
            prompt_loader: Optional prompt loader instance
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
        self.table_template_path = self.config.get("table_template_path") or "constants/table_prompt.j2"
        
        # Set up prompt loaders
        self.table_prompt_loader = prompt_loader or PromptLoader(self.table_template_path)
        
        # Table processing configuration
        self.table_config = {
            "min_confidence": self.config.get("table_min_confidence", 0.7),
            "max_tables_per_page": self.config.get("max_tables_per_page", 10),
            "merge_tables": self.config.get("merge_tables", False),
            "detect_headers": self.config.get("detect_headers", True),
            "extract_cell_types": self.config.get("extract_cell_types", True),
            "save_intermediate": self.config.get("save_intermediate", True)
        }
        
        # Load any custom table processing templates
        self.table_prompt_template = None
        template_path = self.config.get("table_prompt_template")
        if template_path and os.path.exists(template_path):
            with open(template_path, 'r') as f:
                self.table_prompt_template = f.read()


    def __call__(self, document: Document) -> Document:
        """
        Process document tables using LLM
        
        Args:
            document: The document to process
            
        Returns:
            Document: Processed document with table data
        """
        try:
            logger.info(f"{EMOJI['start']} Starting table processing")
            # This function will do necessary setups and call the _process_pages_parallel function

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

            self._process_pages_parallel(
                page_numbers=page_numbers,
                pdf_name=pdf_name,
                document=document,
                max_workers=self.max_workers,
                api_keys=self.api_keys
            )
            # This will manipulate the document in place
            return document
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error in TableProcessor: {str(e)}")
            logger.error(traceback.format_exc())
            return document

    def _process_pages_parallel(self, page_numbers: list, pdf_name: str, document: Document,
                               max_workers: int = 2, api_keys: list = None) -> Document:
        """
        Process multiple pages in parallel using ThreadPoolExecutor with rate limiting
        
        Args:
            page_numbers (list): List of page numbers to process
            pdf_name (str): Name of the PDF file
            document (Document): The document being processed
            max_workers (int, optional): Maximum number of worker threads. Defaults to 2.
            api_keys (list, optional): List of API keys to distribute across workers.
        
        Returns:
            Document: The processed document with integrated LLM results
        """
        logger.info(f"{EMOJI['start']} Starting parallel processing")
        logger.info(f"{EMOJI['page']} Processing {len(page_numbers)} pages with {max_workers} workers")
        
        if api_keys:
            logger.info(f"{EMOJI['key']} Using {len(api_keys)} API keys for distributed processing")
        
        # Process pages in smaller batches to avoid rate limits
        batch_size = math.ceil(max_workers * 1.5)
        for i in range(0, len(page_numbers), batch_size):
            batch = page_numbers[i:i + batch_size]
            logger.info(f"\nProcessing batch {i//batch_size + 1} of {(len(page_numbers) + batch_size - 1)//batch_size}")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                
                for idx, page in enumerate(batch):
                    # Distribute API keys evenly if provided
                    page_api_key = None
                    if api_keys and len(api_keys) > 0:
                        # Round-robin assignment of API keys
                        page_api_key = api_keys[idx % len(api_keys)]
                    
                    futures[executor.submit(
                        self._process_single_page, 
                        page, 
                        pdf_name, 
                        document, 
                        page_api_key
                    )] = page
        
        return document
    
    def _process_single_page(self, page: int, pdf_name: str, document: Document,
                            api_key: str = None) -> tuple:
        """
        Process a single page of the document and return its processed data
        
        Args:
            page (int): Page number to process
            pdf_name (str): Name of the PDF file
            document (Document): The document being processed
            api_key (str, optional): API key to use for this page.
        
        Returns:
            tuple: (page number, processed JSON data)
        """
        try:
            logger.info(f"{EMOJI['page']} Processing page {page + 1}")
            
            # Initialize image path
            img_path = os.path.join(self.output_dir, pdf_name, f"page_{page}", f"{pdf_name}_page_{page}.png")
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: {img_path}")

            logger.info(f"{EMOJI['table']} Finding and processing tables")
            
            # Find all tables in the page
            tables = find_all_tables(document, page=page)

            processed_tables = []

            # Save the tables in a json file
            tables_dir = os.path.join(self.output_dir, pdf_name, f"page_{page}")
            os.makedirs(tables_dir, exist_ok=True)
            with open(os.path.join(tables_dir, f"tables_page_{page}.json"), "w", encoding='utf-8') as f:
                json.dump(tables, f, ensure_ascii=False, indent=2)
            
            if tables:
                logger.info(f"{EMOJI['table']} Found {len(tables)} tables to process")
                    
                for table_idx, table in enumerate(tables):
                    table_id = table["id"]
                    
                    logger.info(f"{EMOJI['processing']} Processing table {table_id}")
                    
                    try:                        
                        processed_table_data = self.process_table(img_path, tables_dir, table_idx, table)
                        processed_tables.append(processed_table_data)
                        
                    except Exception as table_error:
                        logger.error(f"{EMOJI['error']} Error processing table {table_id}: {str(table_error)}")
                        continue

                # Save the processed tables in a json file
                with open(os.path.join(tables_dir, f"processed_tables_page_{page}.json"), "w", encoding='utf-8') as f:
                    json.dump(processed_tables, f, ensure_ascii=False, indent=2)
                    
                # Backmap the processed table data back into the document with the help of the table_json
                document = self._backmap_table_to_page_json(document, processed_tables, tables, page)
                return (page, document)
                
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error processing page {page + 1}: {str(e)}")
            logger.debug(traceback.format_exc())
            return (page, document)
    
    def process_table(self, page_image_path: str, tables_dir: str, table_idx: int, table_json: Dict) -> Dict:
        """
        Process a table in a PDF page
        
        Args:
            page_image_path: Path to the page image
            page_json: JSON data for the page
            
        Returns:
            Dictionary with table data
        """
        try:
            logger.info(f"{EMOJI['table']} Processing table in image {os.path.basename(page_image_path)}")

            table_bbox = table_json["bbox"]
            table_html = table_json["html"]
            
            # Try to crop the image to the table region
            if table_bbox:
                logger.info(f"{EMOJI['image']} Cropping image to table region")
                img_base64 = crop_image_to_table(page_image_path, table_bbox)
                if img_base64 is None:
                    # If cropping failed, use the full image
                    logger.warning(f"{EMOJI['warning']} Table cropping failed, using full page image")
                    with open(page_image_path, "rb") as image_file:
                        img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            else:
                # No bbox provided, use the full image
                with open(page_image_path, "rb") as image_file:
                    img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Step 1: Extract table headers
            headers_schema = self._extract_table_headers(img_base64, table_html)
            if not headers_schema:
                logger.warning(f"{EMOJI['warning']} Failed to extract table headers")
                return None
            
            # Save headers schema
            headers_path = os.path.join(tables_dir, f"table_{table_idx}_headers_schema.json")
            with open(headers_path, "w", encoding='utf-8') as f:
                json.dump(headers_schema, f, ensure_ascii=False, indent=2)
            logger.debug(f"{EMOJI['save']} Saved headers schema to {headers_path}")
            
            # Step 2: Process table rows
            processed_table_data = self._process_table_rows(img_base64, headers_schema, table_html)
            if not processed_table_data:
                logger.warning(f"{EMOJI['warning']} Failed to process table rows")
                return None
            
            # Save table data
            rows_path = os.path.join(tables_dir, f"table_{table_idx}_rows_data.json")
            with open(rows_path, "w", encoding='utf-8') as f:
                json.dump(processed_table_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"{EMOJI['save']} Saved table data to {rows_path}")
                
            result = {
                "headers_schema": headers_schema,
                "table_data": processed_table_data
            }
            
            # Add table ID and bbox to result
            result["table_id"] = table_json["id"]
            result["bbox"] = table_bbox
            
            logger.info(f"{EMOJI['success']} Successfully processed table with {len(processed_table_data['complete'])} rows")
            return result
            
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error processing table: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def _extract_table_headers(self, image_base64: str, table_html: str) -> Optional[Dict]:
        """Extract table headers using LLM"""
        try:
            headers_prompt = self.table_prompt_loader.get_prompt("table_headers_prompt", 
                                                         table_html=table_html)
            headers_response = self.process_image(
                user_prompt=headers_prompt,
                image_base64_list=image_base64
            )
            
            # Parse response
            if (isinstance(headers_response, dict)):
                headers_schema = headers_response
            else:
                headers_schema = json.loads(headers_response)
                
            return headers_schema
                
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error extracting table headers: {str(e)}")
            return None
            
    def _process_table_rows(self, image_base64: str, headers_schema: Dict, table_html: str) -> Optional[List[Dict]]:
        """Process all rows in the table"""

        processed_rows = {
            "complete": [],
            "rows": []
        }

        try:
            # Get complete table data in one shot
            complete_table_prompt = self.table_prompt_loader.get_prompt("table_complete_prompt", headers_schema=headers_schema, table_html=table_html)
            
            table_response = self.process_image(
                user_prompt=complete_table_prompt,
                image_base64_list=image_base64
            )
            
            # Parse response
            if (isinstance(table_response, list) or isinstance(table_response, dict)):
                logger.info(f"{EMOJI['success']} Got in correct format")
                processed_rows["complete"] = table_response
            else:
                logger.info(f"{EMOJI['success']} Got in incorrect format, {type(table_response)}")
                processed_rows["complete"] = json.loads(table_response)
                
            number_of_rows = len(processed_rows["complete"])
            logger.info(f"{EMOJI['success']} Successfully processed table with {number_of_rows} rows")
            
            # Process each row
            try:
                for row_idx, _ in enumerate(processed_rows["complete"]):
                    logger.info(f"{EMOJI['processing']} Processing row {row_idx + 1}")
                    row_prompt = self.table_prompt_loader.get_prompt("table_row_prompt", row_number=row_idx, headers_schema=headers_schema)
                    row_response = self.process_image(
                        user_prompt=row_prompt,
                        image_base64_list=image_base64
                    )

                    # Parse response
                    if (isinstance(row_response, list) or isinstance(row_response, dict)):
                        logger.info(f"{EMOJI['success']} Got in correct format")
                        processed_rows["rows"].append(row_response)
                    else:
                        logger.info(f"{EMOJI['success']} Got in incorrect format, {type(row_response)}")
                        processed_rows["rows"].append(json.loads(row_response))                    
                    
            except Exception as e:
                logger.error(f"{EMOJI['error']} Error processing table rows: {str(e)}")
                return None

            return processed_rows
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error processing table rows: {str(e)}")
            return None
    
    def _backmap_table_to_page_json(self, document: Document, processed_tables: List[Dict], tables: List[Dict], page: int) -> Document:
        """
        Map processed table data back into the document structure
        """
        # Get the page group
        page_group = document.pages[page]
        # If I change in page_group, it will change in the document because it is a reference
        
        for table_idx, table in enumerate(processed_tables):
            # Get the reference block_id
            block_id = table["table_id"]["block_id"]

            table_block = None
            # Get the table block reference
            for block in page_group.children:
                if block.block_id == block_id:
                    table_block = block
                    logger.info(f"{EMOJI['success']} Found table block {table_block.block_id} -> {BlockTypes(table_block.block_type).name}")
                    break

            if table_block is None:
                raise ValueError(f"Table block not found for table {table_idx}")
            if BlockTypes(table_block.block_type).name not in ["TableGroup", "Table", "TableofContents"]:
                raise ValueError(f"Table block is not a table or tablegroup or table of contents for table {table_idx}")
            
            # This is means that the table block is a valid tablegroup or table or table of contents
            # Get the new rows, headers and columns after processing

            header_schema = table["headers_schema"]
            # Headers are in header_schema["properties"]
            headers = list(header_schema["properties"].keys())
            # So columns is len(headers)
            columns = len(headers)

            # Get the rows
            rows_from_llm = table["table_data"]["rows"]

            rows: List[List[str]] = []
            for row in rows_from_llm:
                single_row: List[str] = []
                for header in headers:
                    single_row.append(row[header])
                rows.append(single_row)

            # Creating the llm_table_html from the rows and headers and columns
            llm_table_html = create_table_html(rows, columns, headers)

            # Update the table block reference with the new rows, headers and columns and llm_table_html
            table_block.rows = rows
            table_block.headers = headers
            table_block.columns = columns
            table_block.llm_html = llm_table_html

            # This will automatically update the document because it is a reference

        return document
        
        