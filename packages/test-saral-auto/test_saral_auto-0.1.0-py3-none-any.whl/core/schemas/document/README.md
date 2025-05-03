# Document Schema Documentation

This document provides comprehensive documentation of the document schema used for representing documents processed by the Saral-Auto system. The schema is built on Pydantic models and follows a hierarchical structure to represent document content.

## Overview

The document schema is inspired by the [Marker](https://github.com/VikParuchuri/marker) project with customizations for better form representation. It provides a structured way to represent documents with pages, blocks, and nested elements, as well as annotations added by various processors.

## Core Classes Hierarchy

### 1. Document Class

The `Document` is the top-level container representing a complete document.

#### Required Fields:
- **filepath**: `str` - Path to the original document file
- **pages**: `List[PageGroup]` - List of pages in the document

#### Optional Fields:
- **block_type**: `BlockTypes` - Type identifier, defaults to `BlockTypes.Document`
- **table_of_contents**: `List[TocItem] | None` - Optional table of contents
- **debug_data_path**: `str | None` - Path where debug data was saved
- **metadata**: `Dict` - Document metadata (implicitly added during processing)

### 2. PageGroup Class

Represents a single page in the document.

#### Required Fields:
- **block_type**: `BlockTypes` - Set to `BlockTypes.Page`
- **polygon**: `PolygonBox` - The bounding box of the page
- **block_description**: `str` - Description of the page
- **page_id**: `int` - Unique identifier for the page

#### Optional Fields:
- **lowres_image**: `Image.Image | None | bytes` - Low-resolution image of the page
- **highres_image**: `Image.Image | None | bytes` - High-resolution image of the page
- **children**: `List[Block]` - Child blocks on the page
- **structure**: `List[BlockId]` - Page structure (ordering of blocks)
- **layout_sliced**: `bool` - Whether the layout model had to slice the image (default: False)
- **excluded_block_types**: `Sequence[BlockTypes]` - Block types to exclude (default includes Line, Span)
- **refs**: `List[Reference] | None` - References detected on the page

### 3. Block Class (Base)

Base class for all content blocks in the document.

#### Required Fields:
- **polygon**: `PolygonBox` - Coordinates defining the block's boundaries
- **block_description**: `str` - Human-readable description of the block

#### Optional Fields:
- **block_type**: `BlockTypes` - Type of block
- **block_id**: `int` - Unique identifier within a page
- **page_id**: `int` - ID of the page containing this block
- **text_extraction_method**: `Literal['pdftext', 'surya', 'gemini']` - Method used for text extraction
- **structure**: `List[BlockId]` - Child blocks within this block
- **ignore_for_output**: `bool` - Whether to ignore this block in output (default: False)
- **replace_output_newlines**: `bool` - Whether to replace newlines with spaces (default: False)
- **source**: `Literal['layout', 'heuristics', 'processor']` - Source of the block (default: 'layout')
- **top_k**: `Dict[BlockTypes, float]` - Confidence scores for block type classification
- **metadata**: `BlockMetadata` - Metadata about processing (requests, errors, tokens)
- **lowres_image**: `Image.Image` - Low-resolution image of just this block
- **highres_image**: `Image.Image` - High-resolution image of just this block
- **removed**: `bool` - Whether this block has been replaced by a new block (default: False)

## Specialized Block Types

### 1. Text Block

Represents a paragraph or line of text.

#### Required Fields:
- Inherits all required fields from Block

#### Optional Fields:
- **has_continuation**: `bool` - Whether this text continues from a previous block (default: False)
- **blockquote**: `bool` - Whether this text is a blockquote (default: False)
- **blockquote_level**: `int` - Nesting level of the blockquote (default: 0)
- **html**: `str | None` - HTML representation of the text
- **strikethrough_content**: `Optional[str]` - Text content with strikethrough markings (added by LLM processors)
- **annotations**: `Optional[List[dict]]` - Additional annotations for the text (like strikethrough details)

### 2. TableCell Block

Represents a cell within a table.

#### Required Fields:
- Inherits all required fields from Block
- **rowspan**: `int` - Number of rows this cell spans
- **colspan**: `int` - Number of columns this cell spans
- **row_id**: `int` - Row index of this cell
- **col_id**: `int` - Column index of this cell
- **is_header**: `bool` - Whether this cell is a header cell

#### Optional Fields:
- **text_lines**: `List[str] | None` - Lines of text in this cell
- **strikethrough_content**: `Optional[str]` - Cell content with strikethrough markings
- **annotations**: `Optional[List[dict]]` - Additional annotations for the cell

### 3. Table Block

Represents a table in the document.

#### Required Fields:
- Inherits all required fields from Block

#### Optional Fields:
- **num_rows**: `int` - Number of rows in the table
- **num_cols**: `int` - Number of columns in the table
- **has_header**: `bool` - Whether the table has a header row
- **llm_table_html**: `str | None` - HTML representation of the table generated by an LLM

## Supporting Classes

### 1. PolygonBox

Represents the geometric boundaries of a block.

#### Required Fields:
- **polygon**: `List[List[float]]` - List of four points (coordinates) defining the polygon corners

#### Properties:
- **bbox**: `List[float]` - Bounding box [x_min, y_min, x_max, y_max]
- **height**: `float` - Height of the polygon
- **width**: `float` - Width of the polygon
- **area**: `float` - Area of the polygon
- **center**: `List[float]` - Center point [x, y] of the polygon

### 2. BlockId

Identifies a specific block within the document.

#### Required Fields:
- **page_id**: `int` - ID of the page containing the block

#### Optional Fields:
- **block_id**: `Optional[int]` - ID of the block within the page
- **block_type**: `Optional[BlockTypes]` - Type of the block

### 3. BlockMetadata

Stores metadata about processing operations on a block.

#### Fields:
- **llm_request_count**: `int` - Number of LLM requests made for this block (default: 0)
- **llm_error_count**: `int` - Number of errors encountered in LLM processing (default: 0)
- **llm_tokens_used**: `int` - Number of tokens used in LLM processing (default: 0)

## Document Class Methods

The `Document` class provides several methods for working with document structure:

### 1. `render()`
Creates a hierarchical `DocumentOutput` structure optimized for presentation, including HTML content and section hierarchies. This is primarily intended for displaying the document to users.

### 2. `marshal()`
Serializes the entire `Document` object into a JSON-compatible dictionary structure. This includes all blocks and their properties, suitable for debugging or storage. Use this method when you need to inspect the complete document structure.

### 3. Navigation Methods
- `get_block(block_id)`: Retrieves a specific block by ID
- `get_page(page_id)`: Retrieves a specific page by ID
- `get_next_block(block)`: Finds the next block in reading order
- `get_prev_block(block)`: Finds the previous block in reading order
- `contained_blocks(block_types)`: Returns all blocks matching specified types

## Sample JSON Structure

The document schema is serialized to JSON in a hierarchical structure when using the `marshal()` method. Below is a simplified example of how a document with LLM-detected annotations would be represented:

```json
{
  "block_type": "Document",
  "filepath": "/path/to/document.pdf",
  "debug_data_path": "/path/to/debug/output",
  "metadata": {
    "processor_version": "1.2.3",
    "processing_time": 5.67
  },
  "table_of_contents": [
    {
      "title": "Introduction",
      "heading_level": 1,
      "page_id": 0,
      "polygon": [[100, 50], [500, 50], [500, 70], [100, 70]]
    },
    {
      "title": "Methodology",
      "heading_level": 1,
      "page_id": 1,
      "polygon": [[100, 50], [500, 50], [500, 70], [100, 70]]
    }
  ],
  "pages": [
    {
      "block_id": 0,
      "page_id": 0,
      "block_type": "Page",
      "block_description": "A single page in the document.",
      "polygon": {
        "polygon": [[0, 0], [612, 0], [612, 792], [0, 792]],
        "bbox": [0, 0, 612, 792]
      },
      "structure": [
        "/page/0/SectionHeader/0",
        "/page/0/Text/1",
        "/page/0/Table/2"
      ],
      "children": [
        {
          "block_id": 0,
          "page_id": 0,
          "block_type": "SectionHeader",
          "block_description": "A section heading in the document.",
          "polygon": {
            "polygon": [[100, 50], [500, 50], [500, 70], [100, 70]],
            "bbox": [100, 50, 500, 70]
          },
          "text": "Introduction",
          "heading_level": 1
        },
        {
          "block_id": 1,
          "page_id": 0,
          "block_type": "Text",
          "block_description": "A paragraph or line of text.",
          "polygon": {
            "polygon": [[100, 80], [500, 80], [500, 120], [100, 120]],
            "bbox": [100, 80, 500, 120]
          },
          "text": "This document details the process for applying corrections.",
          "strikethrough_content": "This document details the process for <strikethrough>submitting</strikethrough> applying corrections.",
          "annotations": [
            {
              "type": "strikethrough",
              "content": "This document details the process for <strikethrough>submitting</strikethrough> applying corrections.",
              "source": "llm"
            }
          ]
        },
        {
          "block_id": 2,
          "page_id": 0,
          "block_type": "Table",
          "block_description": "A table in the document.",
          "polygon": {
            "polygon": [[100, 150], [500, 150], [500, 300], [100, 300]],
            "bbox": [100, 150, 500, 300]
          },
          "num_rows": 3,
          "num_cols": 2,
          "has_header": true,
          "children": [
            {
              "block_id": 3,
              "page_id": 0,
              "block_type": "TableCell",
              "block_description": "A cell in a table.",
              "polygon": {
                "polygon": [[100, 150], [300, 150], [300, 180], [100, 180]],
                "bbox": [100, 150, 300, 180]
              },
              "row_id": 0,
              "col_id": 0,
              "is_header": true,
              "rowspan": 1,
              "colspan": 1,
              "text_lines": ["ID"]
            },
            {
              "block_id": 4,
              "page_id": 0,
              "block_type": "TableCell",
              "block_description": "A cell in a table.",
              "polygon": {
                "polygon": [[300, 150], [500, 150], [500, 180], [300, 180]],
                "bbox": [300, 150, 500, 180]
              },
              "row_id": 0,
              "col_id": 1,
              "is_header": true,
              "rowspan": 1,
              "colspan": 1,
              "text_lines": ["Amount"]
            },
            {
              "block_id": 5,
              "page_id": 0,
              "block_type": "TableCell",
              "block_description": "A cell in a table.",
              "polygon": {
                "polygon": [[100, 180], [300, 180], [300, 210], [100, 210]],
                "bbox": [100, 180, 300, 210]
              },
              "row_id": 1,
              "col_id": 0,
              "is_header": false,
              "rowspan": 1,
              "colspan": 1,
              "text_lines": ["A001"]
            },
            {
              "block_id": 6,
              "page_id": 0,
              "block_type": "TableCell",
              "block_description": "A cell in a table.",
              "polygon": {
                "polygon": [[300, 180], [500, 180], [500, 210], [300, 210]],
                "bbox": [300, 180, 500, 210]
              },
              "row_id": 1,
              "col_id": 1,
              "is_header": false,
              "rowspan": 1,
              "colspan": 1,
              "text_lines": ["500"],
              "strikethrough_content": "<strikethrough>500</strikethrough> 250",
              "annotations": [
                {
                  "type": "strikethrough",
                  "content": "<strikethrough>500</strikethrough> 250",
                  "source": "llm"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Document Output Structure

When a Document is rendered with the `render()` method, it produces a `DocumentOutput` structure like this:

```json
{
  "children": [
    {
      "id": "/page/0",
      "block_type": "Page",
      "polygon": {
        "polygon": [[0, 0], [612, 0], [612, 792], [0, 792]],
        "bbox": [0, 0, 612, 792]
      },
      "html": "<content-ref src='/page/0/SectionHeader/0'></content-ref><content-ref src='/page/0/Text/1'></content-ref><content-ref src='/page/0/Table/2'></content-ref>",
      "section_hierarchy": {},
      "children": [
        {
          "id": "/page/0/SectionHeader/0",
          "block_type": "SectionHeader",
          "polygon": {
            "polygon": [[100, 50], [500, 50], [500, 70], [100, 70]],
            "bbox": [100, 50, 500, 70]
          },
          "html": "<h1>Introduction</h1>",
          "section_hierarchy": {
            "1": "/page/0/SectionHeader/0"
          }
        },
        {
          "id": "/page/0/Text/1",
          "block_type": "Text",
          "polygon": {
            "polygon": [[100, 80], [500, 80], [500, 120], [100, 120]],
            "bbox": [100, 80, 500, 120]
          },
          "html": "This document details the process for <strikethrough>submitting</strikethrough> applying corrections.",
          "section_hierarchy": {
            "1": "/page/0/SectionHeader/0"
          }
        }
      ]
    }
  ],
  "html": "<content-ref src='/page/0'></content-ref>",
  "block_type": "Document"
}
```

### Metadata Structure

The document processing pipeline also generates metadata about the document:

```json
{
  "page_stats": [
    {
      "page_id": 0,
      "text_extraction_method": "pdftext",
      "block_counts": {
        "SectionHeader": 2,
        "Text": 5,
        "Table": 1,
        "TableCell": 6
      },
      "llm_processing": {
        "request_count": 2,
        "error_count": 0,
        "tokens_used": 512
      }
    }
  ],
  "document_metadata": {
    "filename": "document.pdf",
    "pages": 1,
    "has_tables": true,
    "has_forms": false,
    "processing_time": 5.67
  }
}
```

## LLM Annotation Integration

The schema supports integration of AI-detected annotations, particularly strikethrough content:

1. **Text and TableCell blocks** have `strikethrough_content` and `annotations` fields
2. **Rendering pipeline** integrates detected strikethrough content in HTML output
3. **JSON serialization** includes annotations in the output

### Example Annotation Structure:
```json
{
  "type": "strikethrough",
  "content": "Text with <strikethrough>crossed out</strikethrough> content",
  "source": "llm"
}
```

## Rendering Process

The document schema includes a comprehensive rendering pipeline:

1. The `Document.render()` method creates a hierarchical `DocumentOutput` structure
2. Each block's `assemble_html()` method generates the HTML representation
3. Text blocks with strikethrough content use that instead of the original text
4. Special handling is applied for different block types (tables, blockquotes, etc.)

## Block Types Enumeration

The schema defines an extensive set of block types via the `BlockTypes` enum, including:

- Document, Page, Text, Table, TableCell, SectionHeader
- Lists (ListGroup, ListItem)
- Media (Figure, Picture, PictureGroup)
- Structure (Line, Span, PageHeader, PageFooter)
- Special content (Code, Equation, Form, ComplexRegion)

This rich typing system allows for precise identification and processing of different document elements.

## Hierarchical Structure

The document follows a hierarchical structure:
- Document contains Pages
- Pages contain Blocks
- Blocks can contain other Blocks (via structure field)
- Specific blocks like Tables contain specialized child blocks (TableCells)

This hierarchical design allows for representing complex document layouts while maintaining relationships between elements.
