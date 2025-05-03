from __future__ import annotations

from typing import List, Sequence, Dict

from pydantic import BaseModel

from core.schemas.base_types import BlockOutput
from core.schemas.document import BlockTypes
from core.schemas.document.blocks import Block, BlockId
from core.schemas.document.groups.page import PageGroup
from core.schemas.document.groups.merged_table import MergedTable
import logging

logger = logging.getLogger(__name__)

class DocumentOutput(BaseModel):
    children: List[BlockOutput]
    html: str
    block_type: BlockTypes = BlockTypes.Document
    merged_tables: Dict[str, MergedTable] | None = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.merged_tables is None:
            self.merged_tables = {}

class TocItem(BaseModel):
    title: str
    heading_level: int
    page_id: int
    polygon: List[List[float]]


class Document(BaseModel):
    filepath: str
    pages: List[PageGroup]
    block_type: BlockTypes = BlockTypes.Document
    table_of_contents: List[TocItem] | None = None
    debug_data_path: str | None = None # Path that debug data was saved to
    merged_tables: Dict[str, MergedTable] | None = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.merged_tables is None:
            self.merged_tables = {}
            
    def get_block(self, block_id: BlockId):
        """
        Retrieve a block by its ID.

        Args:
            block_id: The ID of the block to retrieve.

        Returns:
            Block: The block with the given ID, or None if it doesn't exist.
        """
        logger.debug(f"Attempting to retrieve block with ID: {block_id.block_id} on page ID: {block_id.page_id}")
        page = self.get_page(block_id.page_id)
        if not page:
            logger.warning(f"Page with ID {block_id.page_id} not found. Cannot retrieve block.")
            return None

        block = page.get_block(block_id)
        if block:
            logger.info(f"Successfully retrieved block with ID: {block_id.block_id} on page ID: {block_id.page_id}")
            return block
        else:
            logger.warning(f"Block with ID {block_id.block_id} not found on page ID: {block_id.page_id}")
            return None

    def get_page(self, page_id):
        """
        Retrieve a page by its ID.

        Args:
            page_id: The ID of the page to retrieve.

        Returns:
            PageGroup: The page with the given ID, or None if it doesn't exist.
        """
        logger.debug(f"Attempting to retrieve page with ID: {page_id}")
        for page in self.pages:
            if page.page_id == page_id:
                logger.info(f"Successfully retrieved page with ID: {page_id}")
                return page

        logger.warning(f"Page with ID {page_id} not found.")
        return None

    def get_next_block(self, block: Block, ignored_block_types: List[BlockTypes] = None):
        if ignored_block_types is None:
            ignored_block_types = []
        next_block = None

        # Try to find the next block in the current page
        page = self.get_page(block.page_id)
        next_block = page.get_next_block(block, ignored_block_types)
        if next_block:
            return next_block

        # If no block found, search subsequent pages
        for page in self.pages[self.pages.index(page) + 1:]:
            next_block = page.get_next_block(None, ignored_block_types)
            if next_block:
                return next_block
        return None

    def get_next_page(self, page: PageGroup):
        page_idx = self.pages.index(page)
        if page_idx + 1 < len(self.pages):
            return self.pages[page_idx + 1]
        return None

    def get_prev_block(self, block: Block):
        page = self.get_page(block.page_id)
        prev_block = page.get_prev_block(block)
        if prev_block:
            return prev_block
        prev_page = self.get_prev_page(page)
        if not prev_page:
            return None
        return prev_page.get_block(prev_page.structure[-1])
    
    def get_prev_page(self, page: PageGroup):
        page_idx = self.pages.index(page)
        if page_idx > 0:
            return self.pages[page_idx - 1]
        return None

    def assemble_html(self, child_blocks: List[Block]):
        template = ""
        for c in child_blocks:
            template += f"<content-ref src='{c.id}'></content-ref>"
        return template

    def render(self):
        """Render document with complete block information"""
        child_content = []
        section_hierarchy = {}
        
        for page in self.pages:
            page_output = BlockOutput(
                id=page.id,
                block_type=page.block_type,  # Set the block type
                polygon=page.polygon,
                html="",
                section_hierarchy=section_hierarchy,
                children=[]
            )
            
            # Process page blocks
            for block in page.children:
                # For text or table cells that have strikethrough content, use that for HTML
                html_content = ""
                if hasattr(block, 'text'):
                    html_content = block.text
                
                # If we have LLM-detected strikethrough, use that instead
                if hasattr(block, 'strikethrough_content') and block.strikethrough_content:
                    html_content = block.strikethrough_content
                
                block_output = BlockOutput(
                    id=block.id,
                    block_type=block.block_type,  # Set the block type
                    polygon=block.polygon,
                    html=html_content,
                    section_hierarchy={},
                    children=[]
                )
                page_output.children.append(block_output)
            
            child_content.append(page_output)
            section_hierarchy = page_output.section_hierarchy.copy()

        return DocumentOutput(
            children=child_content,
            html=self.assemble_html(child_content),
            block_type=BlockTypes.Document,
            merged_tables=self.merged_tables
        )

    def contained_blocks(self, block_types: Sequence[BlockTypes] = None) -> List[Block]:
        blocks = []
        for page in self.pages:
            blocks += page.contained_blocks(self, block_types)
        return blocks

    def marshal(self, output_path=None):
        """
        Marshal document to a structured JSON format.
        
        Args:
            output_path: Optional file path to save the JSON output
            
        Returns:
            dict: The document as a JSON-serializable dictionary
        """
        # Create the document structure
        document_json = {
            "block_type": str(BlockTypes.Document),
            "filepath": self.filepath,
            "debug_data_path": self.debug_data_path,
            "metadata": self.metadata if hasattr(self, "metadata") else {},
            "pages": []
        }
        
        # Add table of contents if present
        if hasattr(self, "table_of_contents") and self.table_of_contents:
            toc_list = []
            for item in self.table_of_contents:
                toc_item = {
                    "title": item.title,
                    "heading_level": item.heading_level,
                    "page_id": item.page_id,
                    "polygon": item.polygon.to_dict() if item.polygon else None
                }
                toc_list.append(toc_item)
            
            document_json["metadata"]["table_of_contents"] = toc_list
        
        # Add page stats if available
        if hasattr(self, "page_stats") and self.page_stats:
            document_json["metadata"]["page_stats"] = self.page_stats
        
        # Process each page
        for page in self.pages:
            page_json = self._block_to_json(page)
            document_json["pages"].append(page_json)
        
        # Save to file if path is provided
        if output_path:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(document_json, f, indent=2, ensure_ascii=False, 
                         default=lambda o: o.to_dict() if hasattr(o, 'to_dict') else str(o))
        
        return document_json
    
    def _block_to_json(self, block):
        """
        Convert a block to JSON format.
        
        Args:
            block: The block to convert
            
        Returns:
            dict: Block as a JSON-serializable dictionary
        """
        # Base properties for all blocks
        block_json = {
            "id": block.block_id,  # Changed from block_id to id to match expected schema
            "block_type": str(block.block_type),
            "polygon": block.polygon.to_dict() if block.polygon else None,
        }
        
        # Generate HTML content reference for children
        if hasattr(block, "children") and block.children:
            html_content = ""
            for child in block.children:
                child_ref = f"<content-ref src='{child.block_id}'></content-ref>"
                html_content += child_ref
            block_json["html"] = html_content
        
        # Add page-specific properties
        if block.block_type == BlockTypes.Page:
            block_json["page_id"] = block.page_id
        
        # Add table-specific properties
        if block.block_type == BlockTypes.Table:
            if hasattr(block, "num_rows"):
                block_json["num_rows"] = block.num_rows
            if hasattr(block, "num_cols"):
                block_json["num_cols"] = block.num_cols
            if hasattr(block, "has_header"):
                block_json["has_header"] = block.has_header
            if hasattr(block, "llm_table_html"):
                # Instead of storing raw HTML, set it in html field
                block_json["html"] = block.llm_table_html
        
        # Handle text blocks (including headers, paragraphs)
        if block.block_type in [BlockTypes.Text, BlockTypes.SectionHeader, BlockTypes.ListItem]:
            if hasattr(block, "text"):
                # For text blocks, generate appropriate HTML
                text = block.text
                
                # Determine if this is a heading and what level
                heading_level = None
                if block.block_type == BlockTypes.SectionHeader and hasattr(block, "heading_level"):
                    heading_level = block.heading_level
                
                # Generate HTML based on block type
                if heading_level:
                    block_json["html"] = f"<h{heading_level}>{text}</h{heading_level}>"
                elif block.block_type == BlockTypes.ListItem:
                    block_json["html"] = f"<li>{text}</li>"
                else:
                    block_json["html"] = f"<p>{text}</p>"
        
        # Add structure if available (important for section hierarchy)
        if hasattr(block, "structure") and block.structure:
            block_json["structure"] = [str(item) for item in block.structure]
            
            # Create section hierarchy information
            section_hierarchy = {}
            for structure_item in block.structure:
                if hasattr(structure_item, "level") and hasattr(structure_item, "id"):
                    section_hierarchy[str(structure_item.level)] = structure_item.id
            
            if section_hierarchy:
                block_json["section_hierarchy"] = section_hierarchy
        
        # Handle annotations and formatting
        if hasattr(block, "annotations") and block.annotations:
            # Convert annotations to spans that can be used in HTML
            if "html" in block_json and block_json["html"]:
                # Process annotations to enhance HTML with spans
                # This is a simplified approach - in practice you'd need more sophisticated HTML generation
                for annotation in block.annotations:
                    if annotation.type == "bold":
                        # Example: replace text with bold tags
                        text_to_replace = block.text[annotation.start:annotation.end]
                        block_json["html"] = block_json["html"].replace(
                            text_to_replace, f"<b>{text_to_replace}</b>"
                        )
                    # Handle other annotation types similarly
        
        # Handle strikethrough content
        if hasattr(block, "strikethrough_content") and block.strikethrough_content:
            # Update HTML to include strikethrough
            if "html" in block_json and block_json["html"]:
                for strike in block.strikethrough_content:
                    text_to_replace = block.text[strike.start:strike.end]
                    block_json["html"] = block_json["html"].replace(
                        text_to_replace, f"<s>{text_to_replace}</s>"
                    )
        
        # Handle images
        if block.block_type == BlockTypes.Picture:
            # Add image data if available
            image_data = ""
            if hasattr(block, "image_data") and block.image_data:
                import base64
                # Convert image data to base64 if it's not already
                if isinstance(block.image_data, bytes):
                    image_data = base64.b64encode(block.image_data).decode('utf-8')
                else:
                    image_data = block.image_data
                    
            if hasattr(block, "alt_text"):
                block_json["alt"] = block.alt_text
                
            if image_data:
                if "images" not in block_json:
                    block_json["images"] = {}
                block_json["images"][block.block_id] = image_data
        
        # Recursively process children
        if hasattr(block, "children") and block.children:
            children = []
            for child in block.children:
                child_json = self._block_to_json(child)
                children.append(child_json)
            block_json["children"] = children
        
        return block_json