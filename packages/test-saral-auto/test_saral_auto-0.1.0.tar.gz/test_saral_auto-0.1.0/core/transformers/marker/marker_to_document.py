# This will convert marker output into a document object
from core.schemas.document.document import *
from core.schemas.document.blocks import *
from core.schemas.document.groups import *
from core.schemas.document.text import *
from core.schemas.document.polygon import PolygonBox

from typing import Dict, Any, List, Optional, Tuple, Union
import base64
from io import BytesIO
from PIL import Image

from bs4 import BeautifulSoup

# Add a function to convert PIL Image to base64 for serialization
def image_to_base64(image):
    """Convert PIL Image to base64 string for serialization"""
    if image is None:
        return None
    
    if isinstance(image, str):
        return image
    
    if isinstance(image, Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return img_str
    
    return None

# Add this method to make Picture objects serializable
def make_image_serializable(obj):
    """Make sure image objects are serializable"""
    if hasattr(obj, 'highres_image') and obj.highres_image is not None:
        if isinstance(obj.highres_image, Image.Image):
            # Convert to base64 string
            obj.highres_image = image_to_base64(obj.highres_image)
    return obj

class MarkerToDocument:
    def __init__(self, marker_output: dict):
        self.marker_output = marker_output
    
    def convert(self, document: Document) -> Document:
        """
        Convert marker output to a Document object.
        """
        self._process_marker_output(document)
        return document

    def _process_marker_output(self, document: Document) -> None:
        """
        Process the marker output and update the document.
        
        This function converts the marker JSON output format into the Document schema structure.
        It handles pages, blocks, and their hierarchical relationships while preserving text content,
        formatting, and metadata.
        
        Args:
            document: Document object to be updated with marker output data
        """
        if not hasattr(self, 'marker_output') or not self.marker_output:
            raise ValueError("No marker output available")
        
        # Ensure document.pages exists and is a list
        if not hasattr(document, 'pages') or document.pages is None:
            document.pages = []

        # Process metadata
        if "metadata" in self.marker_output:
            metadata = self.marker_output["metadata"]
            
            # Process table of contents
            if "table_of_contents" in metadata:
                processed_toc = []
                toc_group_for_potential_later_use = {
                    "type": "toc",
                    "id": "toc_" + str(hash(str(metadata["table_of_contents"]))),
                    "blocks": [],
                    "title": "Table of Contents"
                }

                for entry in metadata["table_of_contents"]:
                    toc_item_data = {
                        "title": entry["title"],
                        "heading_level": entry.get("heading_level", 0),
                        "page_id": entry["page_id"],
                        "polygon": PolygonBox(polygon=entry.get('polygon', []))
                    }
                    try:
                        processed_toc.append(TocItem(**toc_item_data))
                    except Exception as e:
                        print(f"Warning: Could not create TocItem for entry {entry.get('title', '')}: {e}")

                    toc_group_for_potential_later_use["blocks"].append({
                        "type": "paragraph", 
                        "id": f"toc_entry_{entry['page_id']}_{hash(entry['title'])}",
                        "text": entry["title"],
                        "spans": [{
                            "start": 0,
                            "end": len(entry["title"]),
                            "type": "link",
                            "url": f"#page_{entry['page_id']}"
                        }]
                    })
                
                if processed_toc:
                    document.table_of_contents = processed_toc

        print("Processing Pages....")
        # Process pages (pages will the top level children of the marker output)
        for i, page_data in enumerate(self.marker_output["children"]):
            print(f"--| Processing Page {i} of {len(self.marker_output['children'])}")
            # print(f"----| Page Data: {page_data}")
            id_parts = page_data["id"].split("/")
            page_group_data = {
                "type": "page",
                "id": str(page_data["id"]),
                "page_id": i, # The index of the page is the page id also same as the id_parts[1]
                "block_id": int(id_parts[-1]), # The last part of the id is the block id
                "polygon": PolygonBox(polygon=page_data.get('polygon', [])),
                "children": [],
                "structure": []
            }

            pageGroup = PageGroup(**page_group_data)
            
            if "children" in page_data and page_data["children"]:
                print(f"----| Processing Children of Page {i}")
                for child in page_data["children"]:
                    print(f"------| Processing Child {child['id']}")
                    processed_blocks = self._process_block(i, child)
                    if processed_blocks:
                        curr_block = pageGroup.add_full_block(processed_blocks)
                        pageGroup.add_structure(curr_block)
            
            document.pages.append(pageGroup)
        
        # Add this line to make all images serializable before returning
        for page in document.pages:
            for block in page.children:
                if hasattr(block, 'highres_image'):
                    make_image_serializable(block)
        
        # TODO: May not need this because we are using the structure field in the page group. Will see later
        # Organize document sections by processing section hierarchies
        # self._process_section_hierarchies(document)

    def _process_block(self, page_id: int, block_data) -> Block:
        """
        Process a single block and its children, converting from marker format to document schema.
        
        Args:
            block_data: The block data from marker output
            
        Returns:
            List of block objects in document schema format
        """
        
        if not block_data:
            return None
        
        id_parts = block_data["id"].split("/")
        block_id = block_data["id"]
        block_type = block_data["block_type"]
        polygon = PolygonBox(polygon=block_data.get('polygon', []))

        print(f"----| Processing Block {block_id} of type {block_type}")

        common_block_data = {
            "id": block_id,
            "page_id": page_id,
            "block_id": id_parts[-1],
            "polygon": polygon,
        }


        block = None
        
        # Process based on block type
        if block_type == "Text":
            # Regular paragraph
            text_block = {
                **common_block_data, # Spread the common block data
                "html": block_data["html"],
                "text": self._extract_text_from_html(block_data["html"]),
                "annotations": self._extract_spans_from_html(block_data["html"])
            }
            return Text(**text_block)
        
        elif block_type == "Handwriting":
            handwriting_block = {
                **common_block_data,
                "html": block_data["html"],
                "text": self._extract_text_from_html(block_data["html"]),
                "annotations": self._extract_spans_from_html(block_data["html"])
            }
            return Handwriting(**handwriting_block)
        
        elif block_type == "SectionHeader":
            # Extract heading level from HTML (h1, h2, etc.)
            def get_heading_level(html: str) -> int:
                for i in range(1, 7):
                    if f"<h{i}" in html:
                        return i
                return 1  # Default
            
            section_header = {
                **common_block_data,
                "html": block_data["html"],
                "text": self._extract_text_from_html(block_data["html"]),
                "annotations": self._extract_spans_from_html(block_data["html"]),
                "heading_level": get_heading_level(block_data["html"])
            }
            return SectionHeader(**section_header)
        
        # TODO: Currently we will not get any list data from marker output
        elif block_type == "ListGroup":
            list_type = "unordered"
            if "html" in block_data and "<ol" in block_data["html"]:
                list_type = "ordered"
            
            block = {
                "type": "list",
                "id": block_id,
                "list_type": list_type,
                "items": []
            }
            
            # Process list items
            if "children" in block_data and block_data["children"]:
                for child in block_data["children"]:
                    if child["block_type"] == "ListItem":
                        item = {
                            "text": self._extract_text_from_html(child["html"]),
                            "spans": self._extract_spans_from_html(child["html"])
                        }
                        block["items"].append(item)
            
            # result.append(block)
        
        elif block_type == "Table" or block_type == "TableGroup" or block_type == "TableOfContents":
            # Get rows (List[List[str]]), columns(int), headers(List[str]) from html in the block data
            rows, columns, headers = self._extract_table_data_from_html(block_data["html"])
            
            table = {
                **common_block_data,
                "rows": rows,
                "columns": columns,
                "headers": headers,
                "structure": [],
                "children": []  # Initialize children list
            }
            table = TableGroup(**table)
            
            # Process table children (children of Table is always TableCell)
            if "children" in block_data and block_data["children"]:
                # Some implementations might have each row/cell as children
                for child in block_data["children"]:
                    common_table_cell_data = {
                        "id": child["id"],
                        "page_id": page_id,
                        "block_id": child["id"].split("/")[-1],
                        "polygon": PolygonBox(polygon=child.get('polygon', [])),
                    }
                    if child["block_type"] == "TableCell": # Not handling any other children of Table
                        text = self._extract_text_from_html(child["html"])
                        def get_rowspan_and_colspan(html: str) -> Tuple[int, int]:
                            soup = BeautifulSoup(html, 'html.parser')
                            rowspan = 1
                            colspan = 1

                            # Check for rowspan attribute
                            rowspan_tag = soup.find('td') or soup.find('th')
                            if rowspan_tag and rowspan_tag.get('rowspan'):
                                rowspan = int(rowspan_tag['rowspan'])

                            # Check for colspan attribute
                            colspan_tag = soup.find('td') or soup.find('th')
                            if colspan_tag and colspan_tag.get('colspan'):
                                colspan = int(colspan_tag['colspan'])

                            return rowspan, colspan
                        
                        # Get the row_id and col_id
                        row_id = 0
                        col_id = 0
                        for row_idx, row in enumerate(rows):
                            if text in row:
                                row_id = row_idx
                                col_id = row.index(text)
                                break

                        rowspan, colspan = get_rowspan_and_colspan(child["html"])

                        table_cell = {
                            **common_table_cell_data,
                            "html": child["html"],
                            "text": text,
                            "text_lines": [text],
                            "rowspan": rowspan,
                            "colspan": colspan,
                            "row_id": row_id,
                            "col_id": col_id,
                            "is_header": '<th>' in child["html"],
                            "dubious": True if "dubious" in child else False
                        }
                        table_cell = TableCell(**table_cell)
                        table.add_structure(table_cell)  # Add to structure
                        table.children.append(table_cell)  # Also add to children list

            return table
        
        # TODO: Currently we will not get any figure data from marker output
        elif block_type == "Figure" or block_type == "FigureGroup":
            figure = {
                "type": "figure",
                "id": block_id,
                "blocks": []
            }
            
            # Process figure children
            if "children" in block_data and block_data["children"]:
                for child in block_data["children"]:
                    child_blocks = self._process_block(child)
                    if child_blocks:
                        figure["blocks"].extend(child_blocks)
            
            # result.append(figure)
        
        elif block_type == "Picture" or block_type == "PictureGroup":
            # Extract image data
            image_data = None
            if "images" in block_data and block_id in block_data["images"]:
                # Convert base64 string to PIL Image
                base64_data = block_data["images"][block_id]
                if base64_data and isinstance(base64_data, str):
                    try:
                        # Remove potential header and decode
                        if "base64," in base64_data:
                            base64_data = base64_data.split("base64,")[1]
                        image_bytes = base64.b64decode(base64_data)
                        image_data = Image.open(BytesIO(image_bytes))
                    except Exception as e:
                        print(f"Error converting base64 to image: {e}")
                        image_data = None
            
            image = {
                **common_block_data,
                "highres_image": image_data,
            }

            image = Picture(**image)
            return image
        
        # TODO: Currently we will not get any caption data from marker output
        elif block_type == "Caption":
            caption = {
                "type": "caption",
                "id": block_id,
                "blocks": [{
                    "type": "paragraph",
                    "id": f"{block_id}_text",
                    "text": self._extract_text_from_html(block_data["html"]),
                    "spans": self._extract_spans_from_html(block_data["html"])
                }]
            }
            # result.append(caption)
        
        # TODO: Currently we will not get any code data from marker output
        elif block_type == "Code":
            code = {
                "type": "code",
                "id": block_id,
                "text": self._extract_code_from_html(block_data["html"]),
                "language": ""  # Try to detect language or leave empty
            }
            # result.append(code)
        
        # TODO: Currently we will not get any equation data from marker output
        elif block_type == "Equation":
            equation = {
                "type": "equation",
                "id": block_id,
                "text": self._extract_text_from_html(block_data["html"])
            }
            # result.append(equation)
        
        # TODO: Currently we will not get any text inline math data from marker output
        elif block_type == "TextInlineMath":
            # This is a paragraph with inline math
            block = {
                "type": "paragraph",
                "id": block_id,
                "text": self._extract_text_from_html(block_data["html"]),
                "spans": self._extract_spans_from_html(block_data["html"])
            }
            # result.append(block)
        
        # TODO: Currently we will not get any footnote data from marker output
        elif block_type == "Footnote":
            footnote = {
                "type": "footnote",
                "id": block_id,
                "label": "",  # Extract label if available
                "blocks": [{
                    "type": "paragraph",
                    "id": f"{block_id}_text",
                    "text": self._extract_text_from_html(block_data["html"]),
                    "spans": self._extract_spans_from_html(block_data["html"])
                }]
            }
            # result.append(footnote)
        
        # TODO: Currently we will not get any page header data from marker output
        elif block_type == "PageHeader":
            header = {
                "type": "header",
                "id": block_id,
                "blocks": [{
                    "type": "paragraph",
                    "id": f"{block_id}_text",
                    "text": self._extract_text_from_html(block_data["html"]),
                    "spans": self._extract_spans_from_html(block_data["html"])
                }]
            }
            # result.append(header)
        
        # TODO: Currently we will not get any page footer data from marker output
        elif block_type == "PageFooter":
            footer = {
                "type": "footer",
                "id": block_id,
                "blocks": [{
                    "type": "paragraph",
                    "id": f"{block_id}_text",
                    "text": self._extract_text_from_html(block_data["html"]),
                }]
            }
            # result.append(footer)
        
        
        # Process other block types or handle unknown types
        else:
            # Generic block handling for types not specifically handled above
            block = Block(**common_block_data)
        
        # Process children recursively if they exist and we haven't processed them already
        if block_type not in ["ListGroup", "TableGroup", "FigureGroup", "PictureGroup"] and "children" in block_data and block_data["children"]:
            for child in block_data["children"]:
                child_blocks = self._process_block(page_id, child)
                if child_blocks:
                    block.children.extend(child_blocks)
        
        return block

    def _extract_text_from_html(self, html):
        """
        Extract plain text from HTML content using BeautifulSoup.
        
        Args:
            html: HTML content
            
        Returns:
            Plain text extracted from HTML
        """
        if not html:
            return ""
        
        # Use BeautifulSoup for HTML parsing
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()

    def _extract_spans_from_html(self, html):
        """
        Extract formatting spans from HTML content using BeautifulSoup.
        
        Args:
            html: HTML content
            
        Returns:
            List of span objects
        """
        if not html:
            return []
        
        spans = []
        soup = BeautifulSoup(html, 'html.parser')
        plain_text = soup.get_text()
        
        # Process bold tags
        for bold_tag in soup.find_all('b'):
            bold_text = bold_tag.get_text()
            start_index = plain_text.find(bold_text)
            if start_index >= 0:
                spans.append({
                    "start": start_index,
                    "end": start_index + len(bold_text),
                    "type": "bold"
                })
        
        # Process italic tags
        for italic_tag in soup.find_all('i'):
            italic_text = italic_tag.get_text()
            start_index = plain_text.find(italic_text)
            if start_index >= 0:
                spans.append({
                    "start": start_index,
                    "end": start_index + len(italic_text),
                    "type": "italic"
                })
        
        # Process underline tags
        for u_tag in soup.find_all('u'):
            u_text = u_tag.get_text()
            start_index = plain_text.find(u_text)
            if start_index >= 0:
                spans.append({
                    "start": start_index,
                    "end": start_index + len(u_text),
                    "type": "underline"
                })
        
        # Process link tags
        for a_tag in soup.find_all('a'):
            link_text = a_tag.get_text()
            start_index = plain_text.find(link_text)
            if start_index >= 0:
                spans.append({
                    "start": start_index,
                    "end": start_index + len(link_text),
                    "type": "link",
                    "url": a_tag.get('href', '#')
                })

        # Process <strikethrough> or <del> tags
        for del_tag in soup.find_all('del', 'strikethrough'):
            del_text = del_tag.get_text()
            start_index = plain_text.find(del_text)
            if start_index >= 0:
                spans.append({
                    "start": start_index,
                    "end": start_index + len(del_text),
                    "type": "strikethrough"
                })
        
        return spans

    def _extract_table_rows_from_html(self, html):
        """
        Extract table rows and cells from HTML using BeautifulSoup.
        
        Args:
            html: HTML content containing a table
            
        Returns:
            List of row objects with cells
        """
        if not html:
            return []
        
        rows = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all table rows
        tr_tags = soup.find_all('tr')
        
        for tr_tag in tr_tags:
            # Check if it's a header row by looking for th tags
            is_header = tr_tag.find('th') is not None
            cells = []
            
            # Process cells (th for headers, td for data)
            cell_tags = tr_tag.find_all('th') if is_header else tr_tag.find_all('td')
            
            for cell_tag in cell_tags:
                cell_html = str(cell_tag)
                cell_text = cell_tag.get_text()
                
                cells.append({
                    "text": cell_text,
                    "spans": self._extract_spans_from_html(cell_html)
                })
            
            if cells:
                rows.append({
                    "cells": cells,
                    "is_header": is_header
                })
        
        return rows

    def _extract_code_from_html(self, html):
        """
        Extract code content from HTML using BeautifulSoup.
        
        Args:
            html: HTML content containing code
            
        Returns:
            Code text
        """
        if not html:
            return ""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for code tag first
        code_tag = soup.find('code')
        if code_tag:
            return code_tag.get_text()
        
        # If no code tag, try pre tag
        pre_tag = soup.find('pre')
        if pre_tag:
            return pre_tag.get_text()
        
        # If neither is found, return the plain text
        return soup.get_text()

    # TODO: This is not needed 
    def _process_section_hierarchies(self, document):
        """
        Process section hierarchies to organize content into proper sections.
        
        Args:
            document: Document object to update
        """
        section_blocks = {}
        pages_to_process = document.pages

        for page_idx, page_group in enumerate(pages_to_process):
            if not isinstance(page_group, dict) or "blocks" not in page_group:
                print(f"Warning: Skipping page {page_idx} in section processing - unexpected format.")
                continue

            blocks_to_remove_indices = []
            
            for block_idx, block in enumerate(page_group["blocks"]):
                if isinstance(block, dict) and "section_hierarchy" in block and block["section_hierarchy"]:
                    for level, section_id_raw in block["section_hierarchy"].items():
                        section_id = str(section_id_raw).replace("/", "_")
                        if section_id not in section_blocks:
                            section_blocks[section_id] = {
                                "type": "section",
                                "id": section_id,
                                "level": int(level),
                                "blocks": [],
                            }
                        
                        section_blocks[section_id]["blocks"].append(block)
                        blocks_to_remove_indices.append(block_idx)
            
            for idx in sorted(blocks_to_remove_indices, reverse=True):
                try:
                    page_group["blocks"].pop(idx)
                except IndexError:
                    print(f"Warning: Index error removing block {idx} from page {page_idx}.")

    def _extract_table_data_from_html(self, html: str) -> Tuple[List[List[str]], int, List[str]]:
        """
        Extract table data from HTML using BeautifulSoup.
        
        Args:
            html: HTML content containing a table
        
        Returns:
            Tuple containing:
            - List of rows (each row is a list of cell values)
            - Number of columns
            - List of header values
        """
        if not html:
            return [], 0, []
        
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        if not table:
            return [], 0, []    
        
        rows = []
        headers = []
        current_row = []

        for row in table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            row_data = [cell.get_text(strip=True) for cell in cells]

            if row.find('th'):
                headers.extend(row_data)
            else:
                current_row.extend(row_data)

            if len(current_row) > 0:
                rows.append(current_row)
                current_row = []

        return rows, len(headers), headers



