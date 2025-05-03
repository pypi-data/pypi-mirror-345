from typing import List, Union, Any
from core.schemas.document.blocks import Block


class Group(Block):
    """Base class for all group blocks that can contain other blocks"""
    children: List[Union[Any, Block]] | None = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.children is None:
            self.children = []
            
    def add_child(self, block: Block):
        """Add a child block to this group"""
        if self.children is None:
            self.children = []
        self.children.append(block)