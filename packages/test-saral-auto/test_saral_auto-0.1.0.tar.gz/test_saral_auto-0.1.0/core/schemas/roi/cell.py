from typing import Dict, Optional
from pydantic import BaseModel


class NormalizedCell(BaseModel):
    """Represents normalized coordinates for a cell"""
    x: int
    y: int
    width: int
    height: int


class CellMetadata(BaseModel):
    """Represents metadata for a cell"""
    is_header: bool
    row_id: int
    group_id: int


class Cell(BaseModel):
    """Represents a cell containing text in the document"""
    id: int
    x: int
    y: int
    width: int
    height: int
    text: str
    orientation: str
    is_printed: bool
    confidence: Dict[str, float]
    normalized: NormalizedCell
    metadata: CellMetadata

    def to_dict(self) -> Dict:
        """Convert cell to dictionary for serialization"""
        return {
            'Cell': self.id,
            'X': self.normalized.x,
            'Y': self.normalized.y,
            'Width': self.normalized.width,
            'Height': self.normalized.height,
            'Text_Type': 'HANDWRITTEN' if not self.is_printed else 'PRINTED',
            'Text': self.text,
            'GroupID': self.metadata.group_id,
            'RowID': self.metadata.row_id,
            'IsHeader': self.metadata.is_header
        }


class CellList(BaseModel):
    """List of cells found in a document."""
    cells: list[Cell]
    
    @classmethod
    def from_list(cls, cell_list: list[dict]) -> 'CellList':
        """Create CellList from a list of cell dictionaries."""
        cells = []
        for cell_dict in cell_list:
            # Handle nested objects
            if 'normalized' in cell_dict and not isinstance(cell_dict['normalized'], NormalizedCell):
                cell_dict['normalized'] = NormalizedCell(**cell_dict['normalized'])
            if 'metadata' in cell_dict and not isinstance(cell_dict['metadata'], CellMetadata):
                cell_dict['metadata'] = CellMetadata(**cell_dict['metadata'])
                
            cells.append(Cell(**cell_dict))
        
        return cls(cells=cells) 