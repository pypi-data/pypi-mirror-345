from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class ROI(BaseModel):
    """ROI (Region of Interest) schema representing a text region in a document."""
    left: int = Field(..., description="Left coordinate of the ROI")
    top: int = Field(..., description="Top coordinate of the ROI")
    right: int = Field(..., description="Right coordinate of the ROI")
    bottom: int = Field(..., description="Bottom coordinate of the ROI")
    text: str = Field(..., description="Text content of the ROI")
    textSize: int = Field(..., description="Size of the text in pixels")
    isBold: bool = Field(..., description="Whether the text is bold")
    boldRatio: float = Field(..., description="Ratio of bold characters to total characters")
    confidence: Optional[float] = Field(None, description="Confidence score for text recognition")
    type: Optional[str] = Field(None, description="Type of ROI (e.g., header, field, label)")
    group_id: Optional[int] = Field(None, description="Group ID for related ROIs")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ROI to dictionary for serialization"""
        return {
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom,
            "text": self.text,
            "textSize": self.textSize,
            "isBold": self.isBold,
            "boldRatio": self.boldRatio,
            "confidence": self.confidence,
            "type": self.type,
            "group_id": self.group_id
        }
    
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

class ROIList(BaseModel):
    """List of ROIs found in a document."""
    rois: List[ROI] = Field(..., description="List of ROIs in the document")
    
    @classmethod
    def from_list(cls, roi_list: List[dict]) -> 'ROIList':
        """Create ROIList from a list of ROI dictionaries."""
        return cls(rois=[ROI(**roi) for roi in roi_list])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ROIList to dictionary for serialization"""
        return {
            "rois": [roi.to_dict() for roi in self.rois]
        }
    
    def filter_by_type(self, roi_type: str) -> 'ROIList':
        """Filter ROIs by type"""
        return ROIList(rois=[roi for roi in self.rois if roi.type == roi_type])
    
    def filter_by_group(self, group_id: int) -> 'ROIList':
        """Filter ROIs by group ID"""
        return ROIList(rois=[roi for roi in self.rois if roi.group_id == group_id])
