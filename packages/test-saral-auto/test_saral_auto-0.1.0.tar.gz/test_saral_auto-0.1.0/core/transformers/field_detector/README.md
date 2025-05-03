# Field Detector

A specialized module for detecting, classifying, and extracting field values from document images.

## Overview

The Field Detector analyzes document regions to identify field types and extract their contents. It works with various field formats commonly found in forms and structured documents.

## Features

- **Field Type Detection**: Identifies various field types based on content and visual characteristics
- **Value Extraction**: Extracts values from detected fields
- **Checkbox Detection**: Determines if checkboxes are checked/unchecked
- **Radio Button Analysis**: Identifies selected/unselected radio buttons
- **Signature Verification**: Detects the presence of signatures
- **Boxed Text Handling**: Extracts characters from boxed input fields

## Field Types

The module can detect and process the following field types:

- **Text**: Standard text fields
- **Boxed Text**: Characters written in individual boxes
- **Number**: Numeric fields and values
- **Date**: Various date formats
- **Checkbox**: Selected/unselected checkboxes
- **Radio Button**: Selected/unselected radio options
- **Signature**: Signature fields
- **Image**: Image placement areas

## Methods

### Field Type Detection

```python
detect_field_type(roi, image=None)
```

Determines the type of field based on text content and visual characteristics:
- Analyzes text keywords to identify specific field types
- Examines visual patterns to detect boxed text fields
- Returns the appropriate FieldType enumeration

### Field Value Extraction

```python
extract_field_value(roi, image, field_type)
```

Extracts the value from a field based on its type:
- For text fields: Uses OCR to extract the text content
- For checkboxes: Returns "checked" or "unchecked"
- For radio buttons: Returns "selected" or "unselected"
- For signatures: Returns "signed" or "unsigned"
- For boxed text: Extracts and concatenates individual characters

## Usage

```python
from core.transformers.field_detector.field_detector import FieldDetector
from core.transformers.document_processor.document_processor import FieldType

# Initialize the field detector
detector = FieldDetector()

# Detect the field type
roi = {"text": "Name:", "top": 100, "left": 200, "bottom": 130, "right": 400}
field_type = detector.detect_field_type(roi, image)

# Extract the field value
value = detector.extract_field_value(roi, image, field_type)

# Use the detected field type and value
print(f"Field type: {field_type.value}")
print(f"Field value: {value}")
```

## Integration

The Field Detector integrates with other system components:

- **Document Processor**: Provides field type detection for document analysis
- **Form Processing**: Extracts values from form fields
- **Data Extraction Pipeline**: Contributes to structured data extraction from documents

## Technical Details

- Uses OpenCV for image processing and analysis
- Employs pytesseract for OCR text extraction
- Utilizes contour detection for identifying visual elements
- Implements thresholding techniques for binary image analysis
