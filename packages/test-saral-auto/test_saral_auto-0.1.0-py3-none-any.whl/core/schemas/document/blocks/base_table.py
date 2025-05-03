from typing import List, Optional, Union, Any

from core.schemas.document import BlockTypes
from core.schemas.document.blocks.base import Block
from core.schemas.document.blocks.tablecell import TableCell


class BaseTable(Block):
    """Base class for table-like blocks."""
    block_type: BlockTypes = BlockTypes.Table
    block_description: str = "A base table block"
    children: List[Union[Any, TableCell]] | None = None  # Initialize children list
    
    # Table-specific properties
    rows: Optional[List[List[str]]] = None
    columns: Optional[int] = None
    headers: Optional[List[str]] = None 