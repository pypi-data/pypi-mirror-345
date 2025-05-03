# Document Processing System

A system for processing documents to detect their type, extract fields, and generate templates.

## Features

- Document type detection (Form or Table)
- Field detection and extraction
- Template generation
- Data extraction from filled documents
- Web API and UI for document processing

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/document-processing.git
cd document-processing
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r src/requirements.txt
```

## Usage

### Command-line Interface

Process a document using the command-line interface:

```bash
python src/process_document.py path/to/document.pdf --output-dir output --filled
```

Options:
- `--output-dir`: Directory to save the output files (default: processed directory in the same location as the input file)
- `--filled`: Flag to indicate that the document is filled (default: False)

#### CLI Examples

**Quick Start Example**:
```bash
# Install dependencies
pip install -r src/requirements.txt

# Process a sample document
python src/process_document.py sample_documents/invoice.pdf

# The command will output JSON with document structure
# and save files to a 'processed' directory next to the original file
```

**Basic usage with default options** (process an unfilled document):
```bash
python src/process_document.py sample_documents/invoice.pdf
```

**Process a filled form and extract the data**:
```bash
python src/process_document.py sample_documents/filled_form.pdf --filled
```

**Specify an output directory**:
```bash
python src/process_document.py sample_documents/contract.pdf --output-dir ./processed_results
```

**Process a filled document and specify an output directory**:
```bash
python src/process_document.py sample_documents/filled_invoice.jpg --filled --output-dir ./processed_results
```

**Process an image document** (JPG or PNG):
```bash
python src/process_document.py sample_documents/form.png
```

The CLI will output the JSON result to the console and save detailed results to the specified output directory. The output includes:

- `document_type`: The detected type (form or table)
- `template`: The generated template structure
- `fields` or `rows`: The detected fields or table rows
- `extracted_data`: (Only when `--filled` is used) The extracted values from the document

### Web Interface

The application consists of two parts that need to be run separately:

1. Start the API server:

```bash
python run_server.py
```

2. Start the NextJS frontend (in a separate terminal):

```bash
cd www
npm install  # Only needed the first time
npm run dev
```

Then open your browser and navigate to http://localhost:3000 to access the web interface.

## API

The system provides a REST API for document processing:

### Process Document

```
POST /api/
```

Parameters:
- `document`: Document file (PDF, PNG, JPG)
- `is_filled`: Whether the document is filled or not (default: False)

Response:
```json
{
  "document_type": "form",
  "template": {
    "name": "Form Template",
    "type": "form",
    "sections": [
      {
        "name": "Section 1",
        "fields": [
          {
            "name": "Field 1",
            "type": "text",
            "required": false,
            "roi": {
              "left": 100,
              "top": 200,
              "right": 300,
              "bottom": 250,
              "page": 0
            }
          }
        ]
      }
    ]
  },
  "fields": [
    {
      "name": "Field 1",
      "value": "",
      "type": "text"
    }
  ],
  "extracted_data": {
    "form_name": "Form Template",
    "sections": [
      {
        "name": "Section 1",
        "fields": [
          {
            "name": "Field 1",
            "value": "Extracted Value",
            "type": "text"
          }
        ]
      }
    ]
  }
}
```

## Architecture

The system consists of the following components:

1. **Document Processor**: Detects the type of document and extracts ROIs.
2. **Field Detector**: Detects and extracts fields from the document.
3. **Template Generator**: Generates templates from the document.
4. **Data Extractor**: Extracts data from filled documents using templates.
5. **Web API**: Provides a REST API for document processing.
6. **Web UI**: Provides a user interface for document processing.

## Supported Document Types

- **Form**: Documents with a vertical layout where you have entries pertaining to a single entity per page.
- **Table**: Documents with a horizontal layout where you can have one entry per row but multiple entries in a page.

## Supported Field Types

- **Text**: Free flowing text.
- **Boxed Text**: Text where you have to fill a character in the box forming a full word or phrase.
- **Number**: A number (e.g., phone number).
- **Date**: A date.
- **Radio Button**: A radio button.
- **Signature**: Free flowing text but orientation may not be horizontal.
- **Checkbox**: A checkbox.
- **Image**: An image.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
