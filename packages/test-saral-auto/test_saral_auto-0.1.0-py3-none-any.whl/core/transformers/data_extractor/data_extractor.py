"""
Template generator module for generating templates from documents.
"""

import os
import json
from typing import Dict, List, Tuple, Optional, Any, Union

from core.transformers.document_processor.document_processor import FieldType

class DataExtractor:
    """
    Class for extracting data from documents using templates.
    """
    
    @staticmethod
    def extract_data(document_data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from a document using a template.
        
        Args:
            document_data: Document data
            template: Template data
            
        Returns:
            Extracted data
        """
        if template.get("type") == "form":
            return DataExtractor._extract_form_data(document_data, template)
        elif template.get("type") == "table":
            return DataExtractor._extract_table_data(document_data, template)
        else:
            return {"error": "Unsupported template type"}
    
    @staticmethod
    def _extract_form_data(form_data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from a form using a template.
        
        Args:
            form_data: Form data
            template: Form template
            
        Returns:
            Extracted form data
        """
        extracted_data = {
            "form_name": template.get("name", ""),
            "sections": []
        }
        
        # Process sections
        for section in template.get("sections", []):
            extracted_section = {
                "name": section.get("name", ""),
                "fields": []
            }
            
            # Process fields
            for field in section.get("fields", []):
                field_name = field.get("name", "")
                
                # Find the field value in the form data
                field_value = ""
                for form_field in form_data.get("fields", []):
                    if form_field.get("name") == field_name:
                        field_value = form_field.get("value", "")
                        break
                
                extracted_field = {
                    "name": field_name,
                    "value": field_value,
                    "type": field.get("type", FieldType.TEXT.value)
                }
                
                extracted_section["fields"].append(extracted_field)
            
            extracted_data["sections"].append(extracted_section)
        
        return extracted_data
    
    @staticmethod
    def _extract_table_data(table_data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from a table using a template.
        
        Args:
            table_data: Table data
            template: Table template
            
        Returns:
            Extracted table data
        """
        extracted_data = {
            "table_name": template.get("name", ""),
            "columns": [col.get("name", "") for col in template.get("columns", [])],
            "rows": table_data.get("rows", [])
        }
        
        return extracted_data 