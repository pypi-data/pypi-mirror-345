"""
JSON renderer for document models that uses BaseRenderer.
Converts Document objects to structured JSON format with enhanced functionality.
"""

import json
import base64
import logging
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple

from core.schemas.document.document import Document, Block
from core.pipelines.utils.utils import numpy_to_list

from . import BaseRenderer, JSONBlockOutput, JSONOutput
from .serializers import DocumentEncoder

logger = logging.getLogger(__name__)

class JSONRenderer(BaseRenderer):
    """
    Renders Document objects as structured JSON using BaseRenderer's capabilities.
    
    This renderer converts Document objects to a comprehensive JSON format,
    handling special types like numpy arrays and extracting images when requested.
    """
    
    def __init__(self, config: Optional[Dict | Any] = None):
        """Initialize renderer with configuration"""
        super().__init__(config)
        self.extract_images = config.get('extract_images', True) if config else True
        self.include_text = config.get('include_text', True) if config else True
        self.include_metadata = config.get('include_metadata', True) if config else True
    
    def __call__(self, document: Document) -> Dict[str, Any]:
        """Convert a Document to JSON format."""
        try:
            logger.info("Rendering document to JSON")
            processed_blocks = []
            
            for page_num, page in enumerate(document.pages):
                try:
                    # Process page and all its blocks using _process_block_output
                    page_json = self._process_block_output(document, page, None)
                    if page_json:
                        processed_blocks.append(page_json)
                    logger.debug(f"Processed page {page_num + 1}")
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                    continue
            
            # Generate document metadata
            metadata = {
                'table_of_contents': getattr(document, 'table_of_contents', None),
                'page_stats': self._generate_page_stats(processed_blocks),
                'debug_data_path': getattr(document, 'debug_data_path', None)
            }
            
            # Create final JSON output
            json_output = JSONOutput(
                children=processed_blocks,
                block_type="Document",
                metadata=metadata,
                merged_tables=getattr(document, 'merged_tables', None)  # Include merged tables
            )
            
            return json_output.model_dump()
            
        except Exception as e:
            logger.error(f"Error in JSON rendering: {str(e)}")
            return {
                "error": str(e),
                "children": [],
                "metadata": {},
                "merged_tables": None
            }

    def _get_block_counts(self, blocks: List[JSONBlockOutput]) -> List[Tuple[str, int]]:
        """Count blocks by type"""
        counts = {}
        for block in blocks:
            block_type = block.block_type
            counts[block_type] = counts.get(block_type, 0) + 1
        return [[k, v] for k, v in counts.items()]

    def _generate_page_stats(self, pages: List[JSONBlockOutput]) -> List[Dict]:
        """Generate page statistics"""
        stats = []
        for page in pages:
            page_stat = {
                'page_id': int(page.id.split('/')[-1]),
                'text_extraction_method': None,
                'block_counts': self._get_block_counts(page.children),
                'block_metadata': {
                    'llm_request_count': 0,
                    'llm_error_count': 0,
                    'llm_tokens_used': 0
                }
            }
            stats.append(page_stat)
        return stats
    
    def _extract_text_from_block(self, block) -> str:
        """Extract text content from a block, handling various text storage formats.
        
        Args:
            block: The block to extract text from
            
        Returns:
            Extracted text content as string
        """
        # Try different text attributes in order of preference
        if hasattr(block, 'content') and block.content:
            return str(block.content)
            
        if hasattr(block, 'text'):
            text = block.text
            if callable(text):
                text = text()
            if isinstance(text, (list, tuple)):
                return " ".join(str(t) for t in text if t)
            return str(text) if text else ""
            
        if hasattr(block, 'text_lines') and block.text_lines:
            return "\n".join(str(line) for line in block.text_lines if line)
            
        if hasattr(block, 'words') and block.words:
            return " ".join(str(word) for word in block.words if word)
            
        if hasattr(block, 'raw_text') and block.raw_text:
            return str(block.raw_text)
            
        return ""

    def _extract_html_content(self, block) -> str:
        """Extract clean HTML content from a block.
        
        Args:
            block: The block to extract HTML from
            
        Returns:
            Clean HTML content string
        """
        if hasattr(block, 'html'):
            # Extract HTML content from inside html='...' attribute
            html = block.html
            if "html='" in str(html):
                start = str(html).find("html='") + 6
                end = str(html).find("'", start)
                if start > 5 and end > start:
                    return str(html)[start:end]
            return str(html)
            
        return ""
        
    def _extract_image_content(self, block) -> str:
        """Extract image content from a block.
        
        Args:
            block: The block to extract image from
            
        Returns:
            Image content string
        """
        if hasattr(block, 'highres_image'):
            return str(block.highres_image)
        return ""

    def _extract_table_cell_content(self, cell) -> str:
        """Extract text content from a table cell.
        
        Args:
            cell: The table cell to extract content from
            
        Returns:
            Cell content as string
        """
        # Try different text sources in order of preference
        if hasattr(cell, 'content') and cell.content:
            return str(cell.content)
            
        if hasattr(cell, 'text'):
            text = cell.text
            if callable(text):
                text = text()
            return str(text) if text else ""
            
        if hasattr(cell, 'html'):
            html = str(cell.html)
            if "html='" in html:
                start = html.find("html='") + 6
                end = html.find("'", start)
                if start > 5 and end > start:
                    return html[start:end].strip()
            return html.strip()
            
        return ""

    def _process_block_output(self, document: Document, block: Block, parent_block=None) -> Optional[JSONBlockOutput]:
        """Process block and its children to match marker output format"""
        try:
            # Get basic block info
            block_id = block.id
            block_type = str(block.block_type)
            text = self._extract_text_from_block(block) if self.include_text else None
            children = []

            # Process children blocks
            if hasattr(block, 'children') and block.children:
                for child in block.children:
                    child_output = self._process_block_output(document, child, block)
                    if child_output:
                        children.append(child_output)

            # Handle HTML content based on block type
            html = ""
            if block_type == "Document":
                # For document blocks, combine child refs
                if children:
                    child_refs = []
                    for child in children:
                        child_refs.append(f"<content-ref src='{child.id}'></content-ref>")
                    html = "".join(child_refs)
            elif block_type == "Picture":
                # For Picture blocks, use the highres_image content
                html = self._extract_image_content(block)
            elif block_type == "TableGroup":
                html = self._process_table_group(block)
            elif block_type == "TableCell":
                # For TableCell blocks, use their text content
                html = f"<td>{text}</td>" if text else ""
            else:
                # For all other blocks, extract clean HTML content
                html = self._extract_html_content(block) or self._generate_html_from_text(text, block_type)

            # Process polygon and bbox
            polygon = self._process_polygon(block.polygon) if hasattr(block, 'polygon') else []
            bbox = self._get_bbox(block.polygon) if hasattr(block, 'polygon') else [0, 0, 0, 0]

            # Get section hierarchy
            section_hierarchy = self._get_section_hierarchy(block)

            # Get block metadata if enabled
            metadata = self._get_block_metadata(document, block) if self.include_metadata else None

            # Extract any images
            images = self._extract_images(document, block)

            # Get merged tables from the block
            merged_tables = getattr(block, 'merged_tables', None)

            # Create JSON output for this block
            return JSONBlockOutput(
                id=str(block_id),
                block_type=self._normalize_block_type(block_type),
                html=html,
                polygon=polygon,
                bbox=bbox,
                children=children if children else None,
                section_hierarchy=section_hierarchy,
                images=images,
                text=text,
                metadata=metadata,
                merged_tables=merged_tables
            )

        except Exception as e:
            logger.error(f"Error processing block {block.id if hasattr(block, 'id') else 'unknown'}: {str(e)}")
            return None

    def _generate_html_from_text(self, text: str, block_type: str) -> str:
        """Generate HTML from text based on block type"""
        if block_type in ['22', 'Text']:
            return f"<p>{text}</p>"
        elif block_type in ['21', 'Table']:
            return f"<div class='table'>{text}</div>"
        else:
            return f"<div>{text}</div>"

    def _generate_html_from_description(self, description: str, block_type: str) -> str:
        """Generate HTML from block description"""
        if block_type in ['22', 'Text']:
            return f"<p block-type=\"Text\">{description}</p>"
        elif block_type in ['21', 'Table']:
            return f"<div class='table'>{description}</div>"
        else:
            return f"<div block-type=\"{block_type}\">{description}</div>"
    
    def _get_section_hierarchy(self, block):
        """Get section hierarchy from block"""
        if hasattr(block, 'section_hierarchy'):
            return block.section_hierarchy
        return {}
    
    def _get_block_text(self, document, block):
        """Get text content from block including table data"""
        if not self.include_text:
            return None
            
        # Direct text access
        if hasattr(block, 'text') and block.text:
            return block.text
            
        # For table blocks, extract text from cells
        if hasattr(block, 'block_type') and str(block.block_type) == '21':  # Table type
            table_text = []
            
            # Try to get cells if they exist as children
            if hasattr(block, 'children') and block.children:
                for row in block.children:
                    row_text = []
                    if hasattr(row, 'children') and row.children:
                        for cell in row.children:
                            if hasattr(cell, 'text') and cell.text:
                                row_text.append(cell.text)
                    if row_text:
                        table_text.append(" | ".join(row_text))
                        
            return "\n".join(table_text) if table_text else None
            
        # For container blocks, try to assemble text from children
        if hasattr(block, 'children') and block.children:
            child_texts = []
            for child in block.children:
                child_text = self._get_block_text(document, child)
                if child_text:
                    child_texts.append(child_text)
            return "\n".join(child_texts) if child_texts else None
                
        return None
    
    def _get_block_metadata(self, document, block):
        """Get metadata from block"""
        if not self.include_metadata:
            return None
        if hasattr(block, 'metadata'):
            return block.metadata
        return {}
    
    def _extract_images(self, document, block):
        """Extract images from block if applicable"""
        if not self.extract_images:
            return None
        
        if hasattr(block, 'id') and block.id.block_type in self.image_blocks:
            try:
                image = block.get_image(document)
                if image:
                    return {str(block.id): self._image_to_base64(image)}
            except Exception as e:
                logger.error(f"Failed to extract image for block {block.id}: {str(e)}")
        
        return {}

    def _image_to_base64(self, image):
        """Convert PIL Image to base64 string"""
        if isinstance(image, str):
            if "base64," not in image:
                return f"data:image/jpeg;base64,{image}"
            return image
            
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{img_str}"

    def _block_to_json(self, document, block):
        """Convert a block to JSON format"""
        block_json = {}

        # Add common block properties
        if hasattr(block, 'id'):
            block_json["id"] = str(block.id)
        if hasattr(block, 'block_type'):
            block_json["type"] = block.block_type.value
        if hasattr(block, 'block_description'):
            block_json["description"] = block.block_description
        
        # Add metadata if configured
        metadata = self._get_block_metadata(document, block)
        if metadata:
            block_json["metadata"] = metadata

        # Extract images if configured
        images = self._extract_images(document, block)
        if images:
            block_json["images"] = images

        # Handle specific block types
        if hasattr(block, 'children') and block.children:
            children = []
            for child in block.children:
                child_json = self._block_to_json(document, child)
                if child_json:
                    children.append(child_json)
            if children:
                block_json["children"] = children

        return block_json
    
    def _process_polygon(self, polygon) -> List[List[float]]:
        """
        Process polygon data to ensure it's in the correct format.
        
        Args:
            polygon: The polygon data (can be PolygonBox, list, or None)
            
        Returns:
            List[List[float]]: Processed polygon points
        """
        if polygon is None:
            return []
        
        # Handle PolygonBox object
        if hasattr(polygon, 'polygon'):
            return numpy_to_list(polygon.polygon)
        
        # Handle numpy array
        if hasattr(polygon, 'tolist'):
            return polygon.tolist()
        
        # Already a list
        return polygon
    
    def _get_bbox(self, polygon) -> List[float]:
        """
        Get bounding box from polygon data.
        
        Args:
            polygon: The polygon data (can be PolygonBox, list, or None)
            
        Returns:
            List[float]: [x_min, y_min, x_max, y_max]
        """
        if polygon is None:
            return [0, 0, 0, 0]
        
        # Handle PolygonBox object - use its bbox property
        if hasattr(polygon, 'bbox'):
            return numpy_to_list(polygon.bbox)
        
        # Calculate bbox from polygon points
        points = self._process_polygon(polygon)
        if not points:
            return [0, 0, 0, 0]
        
        # Extract x and y coordinates
        x_coords = [point[0] for point in points]
        y_coords = [point[1] for point in points]
        
        # Calculate bounds
        x_min = min(x_coords)
        y_min = min(y_coords)
        x_max = max(x_coords)
        y_max = max(y_coords)
        
        return [x_min, y_min, x_max, y_max]
    
    def save_to_file(self, document: Document, output_path: str) -> None:
        """
        Render the document and save it to a JSON file.
        
        Args:
            document: The Document to render
            output_path: Path to save the JSON output
        """
        import os
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Get JSON data
        try:
            logger.info(f"Rendering document to JSON")
            result = self(document)
            
            # Try using DocumentEncoder
            try:
                logger.info(f"Saving document JSON to: {output_path}")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, cls=DocumentEncoder)
            except Exception as e:
                logger.warning(f"Error using DocumentEncoder: {str(e)}")
                # Fallback to default serialization
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, 
                                default=lambda o: str(o))
                except Exception as e2:
                    logger.warning(f"Error using default handler: {str(e2)}")
                    # Last resort: string representation
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(str(result)))
        except Exception as e:
            logger.error(f"Failed to render document to JSON: {str(e)}")
            # Write error message to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"ERROR: Could not serialize document: {str(e)}")

    def _normalize_block_type(self, block_type: str) -> str:
        """Normalize block type to a standard format.
        
        Args:
            block_type: The block type to normalize
            
        Returns:
            Normalized block type string
        """
        if not block_type:
            return "unknown"
            
        # Convert to string if not already
        block_type = str(block_type).strip()
        
        # Handle numeric types
        type_map = {
            "21": "Table",
            "22": "Text",
            "23": "Picture",
            "24": "TableGroup",
            "25": "SectionHeader",
            "26": "TableCell"
        }
        
        if block_type in type_map:
            return type_map[block_type]
            
        # Return as-is if already a text type
        valid_types = [
            "Page", "Text", "Table", "TableGroup", "Picture", 
            "SectionHeader", "List", "ListItem", "Cell", "Row",
            "TableCell"  # Added TableCell as valid type
        ]
        
        if block_type in valid_types:
            return block_type
            
        # Check for substring matches
        block_type_lower = block_type.lower()
        if "cell" in block_type_lower or "tablecell" in block_type_lower:
            return "TableCell"
            
        # Default to unknown if not recognized
        return "unknown"

    def _process_table_group(self, table_block):
        """Process a table group block into HTML format.
        
        Args:
            table_block: The table block to process
            
        Returns:
            HTML string representation of the table
        """
        table_html = ["<table>"]
        current_row = []
        if hasattr(table_block, 'children') and table_block.children:
            for cell in table_block.children:
                if not hasattr(cell, 'html'):
                    continue
                    
                cell_html = cell.html
                if not cell_html:
                    cell_text = self._extract_text_from_block(cell)
                    cell_html = f"<td>{cell_text}</td>"
                
                current_row.append(cell_html)
                
                # Add row when we reach column count or last cell
                if len(current_row) == getattr(table_block, 'columns', 2):
                    table_html.append("<tr>" + "".join(current_row) + "</tr>")
                    current_row = []
                    
        # Add any remaining cells as last row
        if current_row:
            table_html.append("<tr>" + "".join(current_row) + "</tr>")
                
        table_html.append("</table>")
        return "".join(table_html)