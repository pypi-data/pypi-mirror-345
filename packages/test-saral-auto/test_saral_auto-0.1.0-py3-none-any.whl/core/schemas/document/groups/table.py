from typing import List, Optional, Union, Any
from core.schemas.document import BlockTypes
from core.schemas.document.groups.base import Group
from core.schemas.document.blocks import Block


class TableGroup(Group):
    block_type: BlockTypes = BlockTypes.TableGroup
    block_description: str = "A table along with associated captions."
    children: List[Union[Any, Block]] | None = None  # Initialize children list

    # Table-specific properties
    rows: Optional[List[List[str]]] = None
    columns: Optional[int] = None
    headers: Optional[List[str]] = None 
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.children is None:
            self.children = []