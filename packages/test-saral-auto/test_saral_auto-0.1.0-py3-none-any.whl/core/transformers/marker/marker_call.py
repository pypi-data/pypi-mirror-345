"""
Converts PDF to JSON using Marker
"""


from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser
import json
import os


class MarkerCall:
    def __init__(self, pdf_path: str, config=None):
        self.pdf_path = pdf_path
        
        # Initialize configuration
        self.config_dict = config or {
            "output_format": "json",
            "use_llm": False,
            "gemini_api_key": os.environ.get("GEMINI_API_KEY")
        }
        
        # Setup config parser and converter
        self.config_parser = ConfigParser(self.config_dict)
        self.converter = PdfConverter(
            config=self.config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=self.config_parser.get_processors(),
            renderer=self.config_parser.get_renderer(),
            llm_service=self.config_parser.get_llm_service(),
        )
        self.marker_output = None

    def convert_pdf(self):
        rendered = self.converter(self.pdf_path)
        text, _, images = text_from_rendered(rendered)
        self.marker_output = json.loads(text)
        return self.marker_output

    def get_config(self):
        return self.config_parser

    def get_converter(self):
        return self.converter

    def get_pdf_path(self):
        return self.pdf_path
    
    def get_marker_output(self):
        if not self.marker_output:
            self.convert_pdf()
        return self.marker_output
    