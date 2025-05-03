# Template Generator

A specialized module for generating document templates and extracting structured data based on these templates.

## Overview

The Template Generator creates structured templates from processed documents and extracts data using these templates. It supports both form and table document types, providing a standardized way to convert unstructured document content into usable data.

## Features

- **Template Generation**: Creates structured templates from document data
- **Form Templates**: Generates templates for form-based documents with sections and fields
- **Table Templates**: Creates templates for tabular documents with column definitions
- **Data Extraction**: Extracts structured data from documents using templates
- **JSON Output**: Saves generated templates as JSON files for reuse

## Components

### TemplateGenerator Class

Responsible for generating templates from document data:

- Supports both form and table document types
- Organizes form fields into sections
- Defines table columns with metadata
- Outputs standardized JSON template files

### DataExtractor Class

Extracts structured data from documents using templates:

- Maps document content to template fields
- Organizes extracted data according to the template structure
- Supports both form and table data extraction
- Preserves field types and hierarchical structure

## Template Types

### Form Templates

```json
{
  "name": "Form Template",
  "type": "form",
  "sections": [
    {
      "name": "Section 1",
      "fields": [
        {
          "name": "Field Name",
          "type": "text",
          "required": false,
          "roi": { "left": 100, "top": 200, "right": 300, "bottom": 230, "page": 0 }
        }
      ]
    }
  ]
}
```

### Table Templates

```json
{
  "name": "Table Template",
  "type": "table",
  "columns": [
    {
      "name": "Column Name",
      "type": "text",
      "required": false,
      "roi": { "left": 50, "top": 100, "right": 200, "bottom": 130, "page": 0 }
    }
  ]
}
```

## Usage

### Template Generation

```python
from core.transformers.template_generator.templete_generator import TemplateGenerator
from core.transformers.document_processor.document_processor import DocumentType

# Initialize the template generator
generator = TemplateGenerator(output_dir="./templates")

# Generate a template for a form document
template = generator.generate_template(document_data, DocumentType.FORM)

# Generate a template for a table document
template = generator.generate_template(document_data, DocumentType.TABLE)
```

### Data Extraction

```python
from core.transformers.template_generator.templete_generator import DataExtractor

# Extract data using a template
extracted_data = DataExtractor.extract_data(document_data, template)

# Access extracted form data
if template.get("type") == "form":
    for section in extracted_data["sections"]:
        for field in section["fields"]:
            print(f"{field['name']}: {field['value']}")

# Access extracted table data
if template.get("type") == "table":
    columns = extracted_data["columns"]
    for row in extracted_data["rows"]:
        for col in columns:
            print(f"{col}: {row.get(col, '')}")
```

## Integration

The Template Generator integrates with other system components:

- **Document Processor**: Uses processed document data as input
- **Field Detector**: Leverages field type information in templates
- **Document Analysis Pipeline**: Provides standardized templates for consistent data extraction
- **Data Export**: Creates structured data suitable for database storage or API transmission

## Benefits

- **Consistency**: Ensures consistent data extraction across similar documents
- **Reusability**: Generated templates can be reused for similar documents
- **Structured Data**: Converts unstructured document content into structured, usable data
- **Field Typing**: Preserves field type information for proper data handling
