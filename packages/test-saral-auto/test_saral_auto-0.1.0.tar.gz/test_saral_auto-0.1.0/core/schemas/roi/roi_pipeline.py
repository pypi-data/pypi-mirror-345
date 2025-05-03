from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field as PydanticField
from .roi import ROI

class SimpleROI(BaseModel):
    """A simplified ROI model as found in the pipeline results."""
    left: int = PydanticField(..., description="Left coordinate of the ROI")
    top: int = PydanticField(..., description="Top coordinate of the ROI")
    right: int = PydanticField(..., description="Right coordinate of the ROI")
    bottom: int = PydanticField(..., description="Bottom coordinate of the ROI")
    page: int = PydanticField(0, description="Page number where the ROI is located")
    
    def to_full_roi(self, text: str = "", text_size: int = 0, is_bold: bool = False, bold_ratio: float = 0.0) -> ROI:
        """Convert to a full ROI object with text properties."""
        return ROI(
            left=self.left,
            top=self.top,
            right=self.right,
            bottom=self.bottom,
            text=text,
            textSize=text_size,
            isBold=is_bold,
            boldRatio=bold_ratio
        )
    
    @property
    def width(self) -> int:
        """Get width of the ROI"""
        return self.right - self.left
    
    @property
    def height(self) -> int:
        """Get height of the ROI"""
        return self.bottom - self.top
    
    @property
    def area(self) -> int:
        """Get area of the ROI"""
        return self.width * self.height
    
    @property
    def center(self) -> tuple[int, int]:
        """Get center coordinates of the ROI"""
        return ((self.left + self.right) // 2, (self.top + self.bottom) // 2)


class TemplateField(BaseModel):
    """A field in a form template."""
    name: str = PydanticField(..., description="Name of the field")
    type: str = PydanticField(..., description="Type of the field (e.g., text)")
    required: bool = PydanticField(False, description="Whether the field is required")
    roi: SimpleROI = PydanticField(..., description="ROI (Region of Interest) for the field")


class TemplateSection(BaseModel):
    """A section in a form template."""
    name: str = PydanticField(..., description="Name of the section")
    fields: List[TemplateField] = PydanticField(..., description="Fields in the section")


class Template(BaseModel):
    """A form template."""
    name: str = PydanticField(..., description="Name of the template")
    type: str = PydanticField(..., description="Type of the template (e.g., form)")
    sections: List[TemplateSection] = PydanticField(..., description="Sections in the template")


class FormField(BaseModel):
    """A field with extracted value."""
    name: str = PydanticField(..., description="Name of the field")
    value: str = PydanticField(..., description="Extracted value of the field")
    type: str = PydanticField(..., description="Type of the field (e.g., text)")


class ExtractedField(BaseModel):
    """A field in the extracted data."""
    name: str = PydanticField(..., description="Name of the field")
    value: str = PydanticField(..., description="Extracted value of the field")
    type: str = PydanticField(..., description="Type of the field (e.g., text)")


class ExtractedSection(BaseModel):
    """A section in the extracted data."""
    name: str = PydanticField(..., description="Name of the section")
    fields: List[ExtractedField] = PydanticField(..., description="Fields in the section")


class ExtractedData(BaseModel):
    """Extracted data from a form document."""
    form_name: str = PydanticField(..., description="Name of the form")
    sections: List[ExtractedSection] = PydanticField(..., description="Sections in the extracted data")


class ROIPipelineResult(BaseModel):
    """ROI pipeline result schema representing the output of the ROI pipeline."""
    template: Template = PydanticField(..., description="Template structure")
    fields: List[FormField] = PydanticField(..., description="List of fields with extracted values")
    document_type: str = PydanticField(..., description="Type of the document (e.g., form)")
    extracted_data: ExtractedData = PydanticField(..., description="Structured extracted data")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the pipeline result to a dictionary."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ROIPipelineResult':
        """Create a pipeline result from a dictionary."""
        return cls.model_validate(data) 