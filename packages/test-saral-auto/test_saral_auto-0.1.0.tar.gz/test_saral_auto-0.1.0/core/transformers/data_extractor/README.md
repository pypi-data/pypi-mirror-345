# Data Extractor

A specialized module for extracting structured data from documents using predefined templates.

## Overview

The Data Extractor transforms raw document data into structured, usable information by mapping it to predefined templates. It supports both form and table document types, ensuring consistent data extraction across similar documents.

## Features

- **Template-based Extraction**: Extracts data using predefined templates
- **Form Data Extraction**: Extracts field values from form-based documents
- **Table Data Extraction**: Extracts row and column data from tabular documents
- **Consistent Output Format**: Provides standardized JSON output structure
- **Field Type Preservation**: Maintains field type information in extracted data

## Components

### DataExtractor Class

The primary class responsible for document data extraction:

- Supports multiple document types through a unified interface
- Maps document content to template definitions
- Preserves document structure and metadata
- Handles both hierarchical (form) and tabular data

## Methods

### Data Extraction

```python
extract_data(document_data, template)
```

Extracts data from a document using a template:
- Takes raw document data and a template as input
- Determines document type from the template
- Calls the appropriate extraction method based on document type
- Returns structured data in a consistent format

### Form Data Extraction

```python
_extract_form_data(form_data, template)
```

Extracts data from form documents:
- Maps fields in the document to fields defined in the template
- Organizes extracted data into sections as defined by the template
- Preserves field types and hierarchical structure
- Returns a structured representation of the form data

### Table Data Extraction

```python
_extract_table_data(table_data, template)
```

Extracts data from tabular documents:
- Maps table content to column definitions in the template
- Preserves row structure and column relationships
- Returns column definitions and row data in a structured format

## Output Formats

### Form Data Output

```json
{
  "form_name": "Sample Form",
  "sections": [
    {
      "name": "Personal Information",
      "fields": [
        {
          "name": "Name",
          "value": "John Doe",
          "type": "text"
        },
        {
          "name": "Date of Birth",
          "value": "01/01/1980",
          "type": "date"
        }
      ]
    }
  ]
}
```

### Table Data Output

```json
{
  "table_name": "Employee List",
  "columns": ["Name", "Position", "Department"],
  "rows": [
    {
      "Name": "John Doe",
      "Position": "Manager",
      "Department": "Sales"
    },
    {
      "Name": "Jane Smith",
      "Position": "Developer",
      "Department": "IT"
    }
  ]
}
```

## Usage

```python
from core.transformers.data_extractor.data_extractor import DataExtractor

# Extract data using a form template
form_data = {...}  # Raw document data
form_template = {...}  # Template definition
extracted_form_data = DataExtractor.extract_data(form_data, form_template)

# Extract data using a table template
table_data = {...}  # Raw document data
table_template = {...}  # Template definition
extracted_table_data = DataExtractor.extract_data(table_data, table_template)

# Access extracted data
for section in extracted_form_data["sections"]:
    print(f"Section: {section['name']}")
    for field in section["fields"]:
        print(f"  {field['name']}: {field['value']}")
```

## Integration

The Data Extractor integrates with other system components:

- **Template Generator**: Uses templates created by the template generator
- **Document Processor**: Processes the raw document data before extraction
- **Field Detector**: Respects field types detected during document processing
- **Data Processing Pipeline**: Provides structured data for downstream processing

## Benefits

- **Consistency**: Ensures uniform data extraction across similar documents
- **Flexibility**: Adapts to different document types and structures
- **Reusability**: Works with reusable templates for recurring document types
- **Data Quality**: Preserves field types and structural relationships
- **Simplicity**: Provides a clean, consistent API for document data extraction
