"""
Base renderer class for document models.
Provides foundation for document rendering output formats.
"""

import base64
import io
import re
from typing import Dict, List, Any, Tuple, Optional, Literal
from collections import Counter
from bs4 import BeautifulSoup
from typing_extensions import Annotated
from pydantic import BaseModel


from core.schemas.base_types import BlockOutput
from core.schemas.document import BlockTypes

import logging

from core.schemas.document.blocks.base import Block, BlockId
from core.schemas.document.document import Document
logger = logging.getLogger(__name__)


def assign_config(instance, config):
    """Assign configuration values to instance attributes."""
    if config is None:
        return
    
    if isinstance(config, dict):
        for key, value in config.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
    else:
        # Assuming config is a BaseModel
        for key, value in config.model_dump().items():
            if hasattr(instance, key):
                setattr(instance, key, value)


def get_block_class(block_type):
    """Get the block class based on its type."""
    if block_type in (BlockTypes.Page,):
        from core.schemas.document.groups.page import PageGroup
        return PageGroup
    return Block


class BaseRenderer:
    """Base renderer class for document output."""
    image_blocks = (BlockTypes.Picture, BlockTypes.Figure)
    page_blocks = (BlockTypes.Page,)
    extract_images = True
    image_extraction_mode = "highres"


    def __init__(self, config: Optional[BaseModel | dict] = None):
        assign_config(self, config)

    def __call__(self, document):
        # Children are in reading order
        raise NotImplementedError

    def extract_image(self, document: Document, image_id, to_base64=False):
        image_block = document.get_block(image_id)
        cropped = image_block.get_image(document, highres=self.image_extraction_mode == "highres")

        if to_base64:
            image_buffer = io.BytesIO()
            cropped.save(image_buffer, format="PNG")  # Assuming PNG as default format
            cropped = base64.b64encode(image_buffer.getvalue()).decode("utf-8")
        return cropped

    @staticmethod
    def merge_consecutive_math(html, tag="math"):
        if not html:
            return html
        pattern = fr'-</{tag}>(\s*)<{tag}>'
        html = re.sub(pattern, " ", html)

        pattern = fr'-</{tag}>(\s*)<{tag} display="inline">'
        html = re.sub(pattern, " ", html)
        return html

    @staticmethod
    def merge_consecutive_tags(html, tag):
        if not html:
            return html

        def replace_whitespace(match):
            whitespace = match.group(1)
            if len(whitespace) == 0:
                return ""
            else:
                return " "

        pattern = fr'</{tag}>(\s*)<{tag}>'

        while True:
            new_merged = re.sub(pattern, replace_whitespace, html)
            if new_merged == html:
                break
            html = new_merged

        return html

    def generate_page_stats(self, document: Document, document_output):
        page_stats = []
        for page in document.pages:
            block_counts = Counter([str(block.block_type) for block in page.children]).most_common()
            block_metadata = page.aggregate_block_metadata()
            page_stats.append({
                "page_id": page.page_id,
                "text_extraction_method": page.text_extraction_method,
                "block_counts": block_counts,
                "block_metadata": block_metadata.model_dump()
            })
        return page_stats

    def generate_document_metadata(self, document: Document, document_output):
        metadata = {
            "table_of_contents": document.table_of_contents,
            "page_stats": self.generate_page_stats(document, document_output),
            "merged_tables": document.merged_tables if document.merged_tables else None,
        }
        if document.debug_data_path is not None:
            metadata["debug_data_path"] = document.debug_data_path

        return metadata

    def extract_block_html(self, document: Document, block_output: BlockOutput):
        soup = BeautifulSoup(block_output.html, 'html.parser')

        content_refs = soup.find_all('content-ref')
        ref_block_id = None
        images = {}
        merged_tables = {}
        
        for ref in content_refs:
            src = ref.get('src')
            sub_images = {}
            sub_merged_tables = {}
            for item in block_output.children:
                if item.id == src:
                    content, sub_images_, sub_merged_tables_ = self.extract_block_html(document, item)
                    sub_images.update(sub_images_)
                    sub_merged_tables.update(sub_merged_tables_)
                    ref_block_id: BlockId = item.id
                    break

            if ref_block_id and ref_block_id.block_type in self.image_blocks and self.extract_images:
                images[ref_block_id] = self.extract_image(document, ref_block_id, to_base64=True)
            else:
                images.update(sub_images)
                merged_tables.update(sub_merged_tables)
                ref.replace_with(BeautifulSoup(content, 'html.parser'))

        if block_output.id.block_type in self.image_blocks and self.extract_images:
            images[block_output.id] = self.extract_image(document, block_output.id, to_base64=True)
            
        # Include merged tables from the current block
        if hasattr(block_output, 'merged_tables') and block_output.merged_tables:
            merged_tables.update(block_output.merged_tables)

        return str(soup), images, merged_tables


class JSONBlockOutput(BaseModel):
    """Structured output for a document block in JSON format."""
    id: str
    block_type: str
    html: str
    polygon: List[List[float]]
    bbox: List[float]
    children: List['JSONBlockOutput'] | None = None
    section_hierarchy: Dict[int, str] | None = None
    images: dict | None = None
    text: str | None = None
    metadata: dict | None = None
    dubious: bool = False  # Set default value to False
    annotations: List[dict] | None = []  # Set default empty list for annotations
    llm_html: str | None = None  # Set default value to None

class JSONOutput(BaseModel):
    """Structured output for an entire document in JSON format."""
    children: List[JSONBlockOutput]
    block_type: str = str(BlockTypes.Document)
    metadata: dict
    merged_tables: Dict[str, Any] | None = None  # Store document-level merged tables


def reformat_section_hierarchy(section_hierarchy):
    """Convert section hierarchy values to strings."""
    if not section_hierarchy:
        return None
    new_section_hierarchy = {}
    for key, value in section_hierarchy.items():
        new_section_hierarchy[key] = str(value)
    return new_section_hierarchy