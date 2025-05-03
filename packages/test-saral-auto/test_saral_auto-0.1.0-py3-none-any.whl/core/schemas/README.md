# Schemas

This directory contains the core data structures used throughout the Saral application.

## Data Structures

### Form
The Form data structure represents a form document in a JSON-compatible format, primarily used in the frontend.

Use https://github.com/rjsf-team/react-jsonschema-form + some customizations for the form

### Document
The Document data structure represents a document during the parsing process, also in JSON format.

Use https://github.com/VikParuchuri/marker/blob/421b9f3c9db33aa5679440e8136be7b4335f2328/marker/schema/__init__.py and Some Customizations for representing forms better.

## File Structure

schemas/
├── form/
│   ├── form.py                # Form data structure definition
│   ├── __init__.py
│   ├── [README.md](./form/README.md)                     # Documentation for the form module
├── document/
│   ├── document.py            # Document data structure definition
│   ├── __init__.py
│   ├── [README.md](./document/README.md)                     # Documentation for the document module
├── __init__.py

## Usage
These data structures serve as the foundation for:
- Frontend form representation and manipulation
- Backend document processing and analysis
- Data exchange between different components of the system

Both structures are designed to be JSON-serializable for easy transmission and storage.
