from core.schemas.document import BlockTypes
from core.schemas.document.blocks import Block


class PageFooter(Block):
    block_type: str = BlockTypes.PageFooter
    block_description: str = "Text that appears at the bottom of a page, like a page number."
    replace_output_newlines: bool = True
    ignore_for_output: bool = True
