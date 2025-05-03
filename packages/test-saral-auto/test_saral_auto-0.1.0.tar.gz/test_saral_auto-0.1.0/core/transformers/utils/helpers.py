import base64
import io
from PIL import Image
import fitz
import os
import json
import re
import html
from typing import Dict, Any, List, Optional
from core.constants import EMOJI
from core.schemas.document.document import Document, PageGroup, BlockTypes, BaseModel
from core.transformers.utils.debug_write import dump_document_with_images

def get_pdf_page_count(pdf_path):
    """Get the total number of pages in a PDF file using fitz (PyMuPDF)."""
    try:
        print(f"{EMOJI['pdf']} Starting PDF Analysis")
        print(f"{EMOJI['pdf']} Opening PDF: {os.path.basename(pdf_path)}")
        doc = fitz.open(pdf_path)
        page_count = doc.page_count
        doc.close()
        print(f"{EMOJI['pdf']} Found {page_count} pages in PDF")
        return page_count
    except Exception as e:
        print(f"{EMOJI['error']} Error reading PDF {os.path.basename(pdf_path)}: {str(e)}")
        return 0

def create_page_json(document: Document, page: int, write: bool = True) -> Dict[str, Any]:
    """
    Creates a detailed page JSON structure for LLM processing.
    
    Args:
        document: The document object containing the page data
        page: The page number to create the JSON for
        write: Whether to write to file

    Returns:
        dict: Detailed page JSON structure
    """
    try:
        page_obj = document.get_page(page)
        if not isinstance(page_obj, PageGroup):
            raise ValueError(f"Page is not a PageGroup")
        
        if not isinstance(page_obj, BaseModel):
            raise ValueError(f"Page is not a BaseModel")
        
        # Create a safe file path with just the page number, not the whole page object
        file_path = os.path.join(document.debug_data_path, f"BPAI1to3/page_{page}/page_{page}.json")
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if write and document.debug_data_path:
            # Generate JSON and write to file with a safe path
            page_json = dump_document_with_images(page_obj, file_path=file_path, write=True)
        else:
            # Generate JSON without writing
            page_json = dump_document_with_images(page_obj, file_path=file_path, write=False)
        
        return page_json
    except Exception as e:
        print(f"{EMOJI['error']} Error creating page JSON for page {page}: {str(e)}")
        return {}

def create_str_id(page_id, block_type, block_id):
    """
    Creates a standardized string ID from page_id, block_type, and block_id.
    
    Args:
        page_id: The page identifier
        block_type: The type of block
        block_id: The block identifier
        
    Returns:
        str: Formatted string ID in the form "/page/{page_id}/{block_type}/{block_id}"
    """
    return f"/page/{page_id}/{block_type}/{block_id}"


def _create_block_html(block) -> str:
    """Create HTML string for a block based on its type"""
    try:
        if block.block_type == "4":  # Table
            # Create table HTML
            table_html = "<table>"
            if hasattr(block, 'rows'):
                for row in block.rows:
                    table_html += "<tr>"
                    for cell in row:
                        if hasattr(cell, 'is_header') and cell.is_header:
                            table_html += f"<th>{getattr(cell, 'text', '')}</th>"
                        else:
                            table_html += f"<td>{getattr(cell, 'text', '')}</td>"
                    table_html += "</tr>"
            table_html += "</table>"
            return table_html
            
        elif block.block_type == "26":  # Table cell
            if hasattr(block, 'is_header') and block.is_header:
                return f"<th>{getattr(block, 'text', '')}</th>"
            else:
                return f"<td>{getattr(block, 'text', '')}</td>"
                
        elif hasattr(block, 'text'):
            return block.text
            
        return ""
        
    except Exception as e:
        return ""

def backmap_html_json(document: Document, mapping_json: Dict, 
                     page: int, pdf_name: str, output_dir: str) -> Document:
    """
    Map the HTML structure back into document blocks
    
    Args:
        document: Document instance
        mapping_json: Mapping results from LLM
        page: Page number
        pdf_name: Name of the PDF
        output_dir: Output directory
        
    Returns:
        Updated document
    """
    try:
        page_data = document.pages[page]
        
        # Update each block based on mapping
        for block_id, block_data in mapping_json.items():
            try:
                # Find the block
                block = next((b for b in page_data.children if str(b.block_id) == block_id), None)
                if not block:
                    continue
                    
                # Update block metadata
                block.metadata = block.metadata or {}
                block.metadata.update(block_data)
                
            except Exception as block_error:
                continue
                
        return document
        
    except Exception as e:
        return document
    
def create_html_json(document: Document, page: int = None, pdf_name: str = None, output_dir: str = "temp") -> List[Dict[str, Any]]:
    """
    Creates a structured HTML JSON for LLM processing, optimized for strikethrough detection.
    
    This function converts the detailed page JSON structure into a simpler HTML-like 
    structure that can be used by the LLM to map coordinates to block elements.
    
    Args:
        document: The document object containing the page data
        page: Page number (optional, for saving files)
        pdf_name: Name of the PDF file (optional, for saving files)
        output_dir: Directory to save the HTML JSON (optional, default is 'temp')
        
    Returns:
        list: List of HTML JSON structures with elements array
    """
    try:
        # Get page object
        page_obj = document.get_page(page)
        if not page_obj:
            print(f"{EMOJI['error']} Error: Page {page} not found in document")
            return []
            
        # Create the page JSON
        page_json = create_page_json(document, page, write=True)
        if not page_json:
            print(f"{EMOJI['error']} Error: Failed to create page JSON for page {page}")
            return []
                    
        html_json = []

        for child in page_obj.children:
            block_type = BlockTypes(child.block_type).name
            # print(f"block_type: {block_type}")

            if block_type == "TableGroup":
                html_json.append({
                    "id": create_str_id(page, block_type, child.block_id),
                    "html": create_table_html(child.rows, child.columns, child.headers),
                })

                # Add children to html_json
                for child_item in getattr(child, 'children', []):
                    child_block_type = BlockTypes(child_item.block_type).name
                    html_json.append({
                        "id": create_str_id(page, child_block_type, child_item.block_id),
                        "html": getattr(child_item, 'html', ''),
                    })
            else:
                html_json.append({
                    "id": create_str_id(page, block_type, child.block_id),
                    "html": getattr(child, 'html', ''),
                })

        # Save html_json in a file
        if pdf_name is not None and output_dir is not None:
            try:
                # Create a proper directory path with just the page number
                page_dir = os.path.join(output_dir, pdf_name, f"page_{page}")
                os.makedirs(page_dir, exist_ok=True)
            
                html_path = os.path.join(page_dir, f"html_json.json")
                with open(html_path, "w", encoding="utf-8") as f:
                    json.dump(html_json, f, ensure_ascii=False, indent=2)
                print(f"{EMOJI['save']} Saved HTML JSON to {html_path}")
            except Exception as e:
                print(f"{EMOJI['error']} Error saving HTML JSON: {str(e)}")

        return html_json
    except Exception as e:
        print(f"{EMOJI['error']} Error creating HTML JSON for page {page}: {str(e)}")
        return []


def unescape_html_content(html_content: str) -> str:
    """
    Unescapes JSON-encoded and HTML-escaped content.
    
    Args:
        html_content (str): HTML content with escaped Unicode and HTML entities
        
    Returns:
        str: Clean HTML content
    """
    if not html_content or not isinstance(html_content, str):
        return html_content
    
    try:
        # Decode common JSON-encoded Unicode sequences
        unicode_map = {
            '\\u003c': '<', '\\u003e': '>', '\\u0027': "'", '\\u0022': '"',
            '\\u0026': '&', '\\u0023': '#', '\\u0025': '%', '\\u0021': '!',
            '\\u0024': '$', '\\u0028': '(', '\\u0029': ')'
        }
        
        for escaped, char in unicode_map.items():
            html_content = html_content.replace(escaped, char)
            
    except Exception as e:
        print(f"{EMOJI['warning']} Warning: Error processing HTML content: {str(e)}")

    return html_content


def backmap_html_json(document: Document, mapping_json: Dict[str, Any], 
                      page: int = None, pdf_name: str = None, output_dir: str = "temp") -> Document:
    """
    Backmap the LLM-detected strikethrough results to the Document object in-place
    
    Args:
        document: The document object to update
        mapping_json: The mapping results with strikethrough data
        page: Page number (optional, for saving files)
        pdf_name: Name of the PDF file (optional, for saving files)
        output_dir: Directory to save debug files (optional, default is 'temp')
        
    Returns:
        Document: The updated Document object with strikethrough annotations
    """
    print(f"{EMOJI['start']} Starting backmap operation for page {page}")

    # Get page object from document
    page_obj = document.get_page(page)
    if not page_obj:
        print(f"{EMOJI['error']} Error: Page {page} not found in document")
        return document

    # Ensure the mapping results is a list, even if there's only one item
    if isinstance(mapping_json, dict) and all(key in mapping_json for key in ["id", "text", "tag"]):
        # Single item dictionary with expected keys
        mappings = [mapping_json]
    elif isinstance(mapping_json, list):
        # Already a list
        mappings = mapping_json
    else:
        # Try to extract from potential nested structure
        mappings = mapping_json.get("elements", []) if isinstance(mapping_json, dict) else []
        # If still empty, just use the original as is
        if not mappings:
            mappings = [mapping_json] if mapping_json else []
    
    # Track statistics
    total_entries = len(mappings)
    updated_blocks = 0
    skipped_entries = 0
    
    print(f"{EMOJI['start']} Processing {total_entries} mappings")
    
    # Process each mapping result
    for mapping in mappings:
        # Validate the entry
        required_fields = ["id", "text", "tag"]
        if not all(field in mapping for field in required_fields):
            print(f"{EMOJI['warning']} Warning: Invalid strikethrough entry missing required fields: {mapping}")
            skipped_entries += 1
            continue
        
        # Get the block ID from the mapping
        block_id_str = mapping.get("id")
        if not block_id_str or not isinstance(block_id_str, str):
            print(f"{EMOJI['warning']} Warning: Invalid block ID: {block_id_str}")
            skipped_entries += 1
            continue
            
        # Get the text with strikethrough
        strikethrough_text = mapping.get("text")
        if not strikethrough_text:
            print(f"{EMOJI['warning']} Warning: Empty strikethrough text for ID: {block_id_str}")
            skipped_entries += 1
            continue
        
        # Clean up the strikethrough text if needed
        strikethrough_text = unescape_html_content(strikethrough_text)
        
        # Parse the block ID to find the corresponding block
        # Format: /page/{page_id}/{block_type}/{block_id}
        try:
            parts = block_id_str.strip('/').split('/')
            if len(parts) >= 4:
                block_page_id = int(parts[1])
                block_type_str = parts[2]
                block_block_id = int(parts[3])
                
                # Get the block from the document directly
                if block_page_id == page:
                    block = None
                    for child in page_obj.children:
                        if child.block_id == block_block_id:
                            block = child
                            break
                    
                    if block:
                        print(f"Updating block {block_id_str} with strikethrough")
                        # Updating HTML content
                        block.html = strikethrough_text
                        
                        # Update dubious to True
                        block.dubious = True

                        # Add annotation
                        block.annotations.append({
                            "type": "strikethrough",
                            "text": strikethrough_text,
                            "tag": mapping.get("tag", "strikethrough")
                        })
                        
                        # Mark the block as updated
                        updated_blocks += 1
                        print(f"{EMOJI['success']} Updated block {block_id_str} with strikethrough")
                    else:
                        print(f"{EMOJI['warning']} Warning: No matching block found for ID: {block_id_str}")
                        skipped_entries += 1
                else:
                    print(f"{EMOJI['warning']} Warning: Block page ID {block_page_id} doesn't match current page {page}")
                    skipped_entries += 1
            else:
                # Fallback method: try to match by block_id in the ID string
                updated = False
                for child in page_obj.children:
                    # Extract the last part of the ID as block_id
                    last_part = block_id_str.split('/')[-1]
                    if last_part.isdigit() and child.block_id == int(last_part):
                        # Add classification data to the block
                        if not hasattr(child, 'classification'):
                            setattr(child, 'classification', {})
                        
                        # Add the strikethrough text and tag
                        child.classification = {
                            "text": strikethrough_text,
                            "tag": mapping.get("tag", "strikethrough")
                        }
                        
                        # Also set strikethrough_content if it exists in the model
                        if hasattr(child, 'strikethrough_content'):
                            child.strikethrough_content = strikethrough_text
                        
                        # Mark the block as updated
                        updated = True
                        updated_blocks += 1
                        print(f"{EMOJI['success']} Updated block {block_id_str} with strikethrough (using fallback)")
                        break
                
                if not updated:
                    print(f"{EMOJI['warning']} Warning: Could not parse block ID: {block_id_str}")
                    skipped_entries += 1
        except Exception as e:
            print(f"{EMOJI['error']} Error processing block ID {block_id_str}: {str(e)}")
            skipped_entries += 1
    
    # Save for debugging if page and pdf_name are provided
    if page is not None and pdf_name is not None:
        try:
            # Create a proper directory path with just the page number
            page_dir = os.path.join(output_dir, pdf_name, f"page_{page}")
            os.makedirs(page_dir, exist_ok=True)
            
            # Save statistics
            stats = {
                "total_entries": total_entries,
                "updated_blocks": updated_blocks,
                "skipped_entries": skipped_entries
            }
            
            stats_path = os.path.join(page_dir, f"backmap_stats.json")
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            print(f"{EMOJI['save']} Saved backmap statistics to {stats_path}")
            
            # Save the updated page as JSON for debugging (using a safe path)
            debug_path = os.path.join(page_dir, f"updated_page_json.json")
            page_json = dump_document_with_images(page_obj, file_path=debug_path, write=True)
            print(f"{EMOJI['save']} Saved updated page JSON to {debug_path}")
            
            # Print summary
            print(f"\n=== Backmap Summary ===")
            print(f"Total entries processed: {total_entries}")
            print(f"Successfully updated blocks: {updated_blocks}")
            print(f"Skipped entries: {skipped_entries}")
        except Exception as e:
            print(f"{EMOJI['error']} Error saving debug data: {str(e)}")
    
    return document

def find_all_tables(document: Document, page: int) -> List[Dict]:
        """Find all tables in a page"""
        page_data = document.pages[page]
        tables = []
        
        # Check if the page has children
        if hasattr(page_data, 'children'):
            # Iterate through all children
            for block in page_data.children:
                block_type = BlockTypes(block.block_type).name
                block_id = block.block_id
                if block_type == "TableGroup" or block_type == "Table" or block_type == "TableofContents":  # Use enum instead of string
                    table_info = {
                        "id": {
                            "block_id": block_id,
                            "block_type": block_type,
                            "page_id": page,
                        },
                        "bbox": block.polygon.bbox if hasattr(block, 'polygon') else getattr(block, 'bbox', None),
                        "rows": getattr(block, 'rows', None),
                        "headers": getattr(block, 'headers', None),
                        "html": create_table_html(block.rows, len(block.headers), block.headers),
                    }
                    tables.append(table_info)
        
        return tables

def create_table_html(rows: List[List[str]], columns: int, headers: List[str]) -> str:
    """
    Creates an HTML table from the given rows, columns, and headers.
    
    Args:
        rows: List of rows in the table
        columns: Number of columns in the table
        headers: List of headers in the table
        
    Returns:
        str: HTML table
    """
    html_table = "<table>"
    if headers:
        html_table += "<tr>"
        for header in headers:
            html_table += f"<th>{header}</th>"
        html_table += "</tr>"
    
    for row in rows:
        html_table += "<tr>"
        for cell in row:
            html_table += f"<td>{cell}</td>"
        html_table += "</tr>"
    
    html_table += "</table>"
    return html_table

def crop_image_to_table(image_path: str, bbox: Dict) -> Optional[str]:
    """
    Crop an image to the table region based on bbox coordinates
    
    Args:
        image_path: Path to the full page image
        bbox: Bounding box dictionary or list with x0, y0, x1, y1 values
        
    Returns:
        Base64 encoded cropped image or None if cropping fails
    """
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Extract bbox coordinates
        if isinstance(bbox, list) and len(bbox) == 4:
            x0, y0, x1, y1 = bbox
        elif isinstance(bbox, dict):
            x0 = bbox[0]
            y0 = bbox[1]
            x1 = bbox[2]
            y1 = bbox[3]
        else:
            raise ValueError(f"Invalid bbox format: {bbox}")
        
        # Add padding to the crop (5% of width/height)
        width = x1 - x0
        height = y1 - y0
        padding_x = width * 0.05
        padding_y = height * 0.05
        
        # Apply padding while ensuring we stay within image bounds
        x0_padded = max(0, x0 - padding_x)
        y0_padded = max(0, y0 - padding_y)
        x1_padded = min(img.width, x1 + padding_x)
        y1_padded = min(img.height, y1 + padding_y)
        
        # Crop the image
        cropped_img = img.crop((x0_padded, y0_padded, x1_padded, y1_padded))
        
        # Convert to base64
        buffered = io.BytesIO()
        cropped_img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return img_base64
        
    except Exception as e:
        return None