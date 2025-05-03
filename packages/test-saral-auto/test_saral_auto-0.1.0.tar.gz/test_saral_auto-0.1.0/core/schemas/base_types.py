"""Base types and models used across the document processing system."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from core.schemas.document import BlockTypes

class BlockOutput(BaseModel):
    """Base output structure for document blocks."""
    id: Any
    block_type: BlockTypes  # Add this field
    polygon: Any
    html: str
    section_hierarchy: Dict[str, Any]
    children: List['BlockOutput'] = []
    text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

BlockOutput.model_rebuild()