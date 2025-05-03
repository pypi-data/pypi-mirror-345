from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class TableRef(BaseModel):
    page_id: int
    table_id: int
    
    class Config:
        frozen = True

class MergedTable(BaseModel):
    """
    Represents a merged table in the document.
    """
    html: str = Field(description="The HTML representation of the merged table")
    page_numbers: List[int] = Field(description="List of page numbers where the tables are located") 
    tables: List[TableRef] = Field(description="List of tables merged, with their page and table_id")
    
    class Config:
        frozen = True  # Make the model immutable
        validate_assignment = True  # Validate data on assignment

    def model_post_init(self, __context) -> None:
        """Validate that page numbers match table references"""
        page_ids = set(ref.page_id for ref in self.tables)
        if not all(page in page_ids for page in self.page_numbers):
            raise ValueError("All page numbers must have corresponding table references")
