from core.transformers.processors.LLM_processors import BaseLLMProcessor
import concurrent.futures
import json
import logging
import os
import traceback
from typing import Dict, Any, List, Optional, Tuple
from core.schemas.document.document import Document, BlockTypes
from core.schemas.document.groups.merged_table import MergedTable, TableRef
from core.transformers.processors.LLM_processors.prompt_loader import PromptLoader
from core.transformers.utils.helpers import crop_image_to_table, create_table_html
from core.constants import EMOJI
import math

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TableMergingLLMProcessor(BaseLLMProcessor):
    def __init__(self, model="gemini-2.0-flash-thinking-exp-01-21", log_level=logging.INFO, config: Optional[Dict] = None, output_dir: Optional[str] = None, prompt_loader=None):
        super().__init__(model, log_level)

        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        # TODO: Will also deduce the hard mergeing to llm based merge config
        self.merge_config_path = os.path.join("core", "constants", "hard_merge_config.json")
        try:
            self.merge_config = json.load(open(self.merge_config_path))
            logger.info(f"{EMOJI['config']} Loaded merge configuration from {self.merge_config_path}")
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error loading merge configuration: {str(e)}")
            self.merge_config = {}

        self.output_dir = output_dir or "output"
        self.config = config or {}

        # Create output directory if it doesn't exist
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"{EMOJI['folder']} Created output directory: {self.output_dir}")
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error creating output directory: {str(e)}")

        # Settings for parallel processing
        self.max_workers = self.config.get("max_workers", 2)
        self.batch_size = math.ceil(self.max_workers * 1.5)
        
        # Templates and prompts
        self.merge_prompt_path = self.config.get("merge_template_path") or "constants/merge_table_llm.j2"
        
        # Set up prompt loaders
        self.merge_prompt_loader = prompt_loader or PromptLoader(self.merge_prompt_path)
        logger.info(f"{EMOJI['template']} Loaded merge prompt template from {self.merge_prompt_path}")
        
        # TODO: Other configs might be added here

    def __call__(self, document: Document) -> Document:
        """
        Process the document to merge tables across pages
        """
        try:
            logger.info(f"{EMOJI['start']} Starting table merging across pages")
            
            # Get the Hard Merge Config 
            hard_merge_config = self.merge_config

            # {
            #     "merged_table_1": [1, 2], -> Means last table of page 1 and first table of page 2 are to be merged
            #     "merged_table_2": [4, 5], -> Means last table of page 4 and first table of page 5 are to be merged
            #     "merged_table_3": [6, 7], -> Means last table of page 6 and first table of page 7 are to be merged
            #     "merged_table_4": [7, 13] -> Means last table of page 7 all tables in between and first table of page 13 are to be merged
            # }

            if not hard_merge_config:
                logger.warning(f"{EMOJI['warning']} No merge configuration found, skipping table merging")
                return document

            merged_result = {}
            logger.info(f"{EMOJI['table']} Found {len(hard_merge_config)} table merging tasks")

            # Get the pages to merge
            for merge_key, pages in hard_merge_config.items():
                try:
                    logger.info(f"{EMOJI['processing']} Processing merge task: {merge_key}")
                    start_page, end_page = pages

                    # Structure needed for the result
                    pages_range = list(range(start_page, end_page + 1))
                    logger.info(f"{EMOJI['page']} Merging tables across pages {start_page} to {end_page}")

                    # Create Table HTMLS
                    table_htmls = []
                    table_refs = [] # -> list of { page_id, table_id (block_id of the TableGroup)}
                    cropped_tables_base64 = []
                    
                    page_id = start_page
                
                    while page_id <= end_page:
                        try:
                            # If the page_id is the first page, then get the last table of the page
                            if page_id == start_page:
                                logger.info(f"{EMOJI['search']} Getting last table from page {page_id}")
                                id, html, cropped_table_base64 = self.get_last_table_of_page(document, page_id)
                                if id is not None:
                                    table_htmls.append(html)
                                    table_refs.append(TableRef(
                                        page_id=int(page_id),
                                        table_id=int(id)
                                    ))
                                    cropped_tables_base64.append(cropped_table_base64)

                            # If the page_id is the last page, then get the first table of the page
                            elif page_id == end_page:
                                logger.info(f"{EMOJI['search']} Getting first table from page {page_id}")
                                id, html, cropped_table_base64 = self.get_first_table_of_page(document, page_id)
                                if id is not None:
                                    table_htmls.append(html)
                                    table_refs.append(TableRef(
                                        page_id=int(page_id),
                                        table_id=int(id)
                                    ))
                                    cropped_tables_base64.append(cropped_table_base64)

                            # If the page_id is in between, then get all tables of the page
                            else:
                                logger.info(f"{EMOJI['search']} Getting all tables from page {page_id}")
                                tables = self.get_all_tables_of_page(document, page_id)
                                for table in tables:
                                    id, html, cropped_table_base64 = table
                                    if id is not None:
                                        table_htmls.append(html)
                                        table_refs.append(TableRef(
                                            page_id=int(page_id),
                                            table_id=int(id)
                                        ))
                                        cropped_tables_base64.append(cropped_table_base64)
                                
                                logger.info(f"{EMOJI['table']} Found {len(tables)} tables on page {page_id}")

                        except Exception as page_error:
                            logger.error(f"{EMOJI['error']} Error processing page {page_id}: {str(page_error)}")
                            logger.error(traceback.format_exc())
                            
                        page_id = page_id + 1

                    logger.info(f"{EMOJI['processing']} Processing {len(table_htmls)} table HTMLs for merging")
                    merged_table_html = self.process_table_htmls(pages_range, table_htmls, cropped_tables_base64)
                    
                    # Create MergedTable object
                    merged_table = MergedTable(
                        html=merged_table_html,
                        page_numbers=pages_range,
                        tables=table_refs
                    )
                    
                    # Add to results
                    merged_result[merge_key] = merged_table
                    
                    # Update document
                    if document.merged_tables is None:
                        document.merged_tables = {}
                    document.merged_tables[merge_key] = merged_table

                    logger.info(f"{EMOJI['success']} Successfully merged tables for {merge_key}")

                except Exception as merge_error:
                    logger.error(f"{EMOJI['error']} Error processing merge task {merge_key}: {str(merge_error)}")
                    logger.error(traceback.format_exc())
                    continue

            # Save the merged result
            pdf_name = os.path.splitext(os.path.basename(document.filepath))[0]
            merged_result_path = os.path.join(self.output_dir, pdf_name, "merged_result.json")
            
            # Convert merged_result to dict for JSON serialization
            merged_result_json = {
                key: value.dict() for key, value in merged_result.items()
            }
            
            with open(merged_result_path, "w") as f:
                json.dump(merged_result_json, f, indent=4)
            logger.info(f"{EMOJI['save']} Saved merged result to {merged_result_path}")

            logger.info(f"{EMOJI['complete']} Completed table merging with {len(merged_result)} successful merges")
            return document
            
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error in table merging process: {str(e)}")
            logger.error(traceback.format_exc())
            return document
    

    def process_table_htmls(self, pages, table_htmls, cropped_tables_base64):
        """
        Process the table htmls using LLM
        """
        try:
            logger.info(f"{EMOJI['processing']} Processing table HTMLs across pages {pages[0]}-{pages[-1]}")
            
            merge_prompt = self.merge_prompt_loader.get_prompt('merge_tables_prompt', page_numbers=pages, table_htmls=table_htmls)
            logger.info(f"{EMOJI['model']} Sending prompt to LLM for table merging")
            
            merged_html = self.process_image(merge_prompt, cropped_tables_base64, type_json=False)

            # Verify whether its an html
            if isinstance(merged_html, str):
                logger.info(f"{EMOJI['processing']} Cleaning up merged HTML response")
                if merged_html.startswith("```html") or merged_html.startswith("```"):
                    start_pos = merged_html.find("```")
                    if start_pos >= 0:
                        # Skip the ``` and find the end of the first line
                        start_pos = merged_html.find("\n", start_pos) + 1
                        # Find the end of the code block
                        end_pos = merged_html.find("```", start_pos)
                        if end_pos >= 0:
                            merged_html = merged_html[start_pos:end_pos].strip()
                
                # If there are still no table tags, look for them
                if "<table" in merged_html and "</table>" in merged_html:
                    table_start = merged_html.find("<table")
                    table_end = merged_html.rfind("</table>") + 8
                    merged_html = merged_html[table_start:table_end]

            logger.info(f"{EMOJI['success']} Successfully processed and cleaned merged HTML")
            return merged_html
            
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error processing table HTMLs: {str(e)}")
            logger.error(traceback.format_exc())
            return "<table><tr><td>Error processing tables</td></tr></table>"
    

    def get_last_table_of_page(self, document: Document, page_id: int) -> Tuple[int, str, str]:
        """
        Get the last table of the page
        """
        try:
            logger.info(f"{EMOJI['search']} Getting last table from page {page_id}")
            # Get the page
            tables = self.get_all_tables_of_page(document, page_id)
            if not tables:
                logger.warning(f"{EMOJI['warning']} No tables found on page {page_id}")
                return None, "<table></table>", ""
                
            logger.info(f"{EMOJI['success']} Found last table on page {page_id}")
            return tables[-1]
            
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error getting last table from page {page_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return None, "<table></table>", ""
        

    def get_first_table_of_page(self, document: Document, page_id: int) -> Tuple[int, str, str]:
        """
        Get the first table of the page
        """
        try:
            logger.info(f"{EMOJI['search']} Getting first table from page {page_id}")
            
            tables = self.get_all_tables_of_page(document, page_id)
            if not tables:
                logger.warning(f"{EMOJI['warning']} No tables found on page {page_id}")
                return None, "<table></table>", ""
                
            logger.info(f"{EMOJI['success']} Found first table on page {page_id}")
            return tables[0]
            
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error getting first table from page {page_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return None, "<table></table>", ""

    def get_all_tables_of_page(self, document: Document, page_id: int) -> List[Tuple[int, str, str]]:
        """
        Get all tables of the page
        """
        try:
            logger.info(f"{EMOJI['search']} Getting all tables from page {page_id}")
            
            # Get the page
            page = document.get_page(page_id)
            if not page:
                logger.warning(f"{EMOJI['warning']} Page {page_id} not found in document")
                return []
                
            all_children = page.children
            tables = []
            
            for child in all_children:
                try:
                    block_type = BlockTypes(child.block_type).name
                    if block_type in ["Table", "TableGroup", "TableOfContents"]:
                        logger.info(f"{EMOJI['table']} Found table block: {child.block_id}")

                        # Create HTML
                        child_html = create_table_html(child.rows, child.columns, child.headers)
                        # Get BBOXES
                        bboxes = child.polygon.bbox
                        pdf_name = os.path.splitext(os.path.basename(document.filepath))[0] # if document.filepath = "C:\\Users\\debat\\OneDrive\\Desktop\\Devs\\saral-auto\\input\\BPAI1to3.pdf" then pdf_name = "BPAI1to3"
                        
                        # Get the cropped table base64
                        try:
                            image_path = os.path.join(self.output_dir, pdf_name, f"page_{page_id}", f"{pdf_name}_page_{page_id}.png")
                            logger.info(f"{EMOJI['image']} Cropping table from image: {image_path}")
                            
                            cropped_table_base64 = crop_image_to_table(image_path, bboxes)
                            if not cropped_table_base64:
                                logger.warning(f"{EMOJI['warning']} Failed to crop table image, using empty base64")
                                cropped_table_base64 = ""
                                
                            tables.append((child.block_id, child_html, cropped_table_base64))
                            
                        except Exception as crop_error:
                            logger.error(f"{EMOJI['error']} Error cropping table image: {str(crop_error)}")
                            tables.append((child.block_id, child_html, ""))
                            
                except Exception as child_error:
                    logger.error(f"{EMOJI['error']} Error processing child block: {str(child_error)}")
                    continue
                    
            logger.info(f"{EMOJI['success']} Found {len(tables)} tables on page {page_id}")
            return tables
            
        except Exception as e:
            logger.error(f"{EMOJI['error']} Error getting tables from page {page_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
