"""
Template generator module for generating templates from documents.
"""

import os
import json
from typing import Dict, List, Tuple, Optional, Any, Union

from core.transformers.document_processor.document_processor import DocumentType, FieldType


class TemplateGenerator:
    """
    Class for generating templates from documents.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the template generator.
        
        Args:
            output_dir: Directory to save the output files
        """
        self.output_dir = output_dir
    
    def generate_template(self, document_data: Dict[str, Any], document_type: DocumentType) -> Dict[str, Any]:
        """
        Generate a template from document data.
        
        Args:
            document_data: Document data
            document_type: Type of the document
            
        Returns:
            Template data
        """
        if document_type == DocumentType.FORM:
            return self._generate_form_template(document_data)
        elif document_type == DocumentType.TABLE:
            return self._generate_table_template(document_data)
        else:
            return {"error": "Unsupported document type"}
    
    def _generate_form_template(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a template from form data.
        
        Args:
            form_data: Form data
            
        Returns:
            Form template data
        """
        template = {
            "name": form_data.get("template", {}).get("name", "Form Template"),
            "type": "form",
            "sections": []
        }
        
        # Process sections
        for section in form_data.get("template", {}).get("sections", []):
            template_section = {
                "name": section.get("name", ""),
                "fields": []
            }
            
            # Process fields
            for field in section.get("fields", []):
                template_field = {
                    "name": field.get("name", ""),
                    "type": field.get("type", FieldType.TEXT.value),
                    "required": field.get("required", False),
                    "roi": field.get("roi", {})
                }
                
                template_section["fields"].append(template_field)
            
            template["sections"].append(template_section)
        
        # Save the template to a JSON file
        if self.output_dir:
            template_path = os.path.join(self.output_dir, "form_template.json")
            with open(template_path, "w") as f:
                json.dump(template, f, indent=2)
        
        return template
    
    def _generate_table_template(self, table_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a template from table data.
        
        Args:
            table_data: Table data
            
        Returns:
            Table template data
        """
        template = {
            "name": table_data.get("template", {}).get("name", "Table Template"),
            "type": "table",
            "columns": []
        }
        
        # Process columns
        for column in table_data.get("template", {}).get("columns", []):
            template_column = {
                "name": column.get("name", ""),
                "type": column.get("type", FieldType.TEXT.value),
                "required": column.get("required", False),
                "roi": column.get("roi", {})
            }
            
            template["columns"].append(template_column)
        
        # Save the template to a JSON file
        if self.output_dir:
            template_path = os.path.join(self.output_dir, "table_template.json")
            with open(template_path, "w") as f:
                json.dump(template, f, indent=2)
        
        return template
