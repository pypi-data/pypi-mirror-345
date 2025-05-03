from core.schemas.document import BlockTypes
from core.schemas.document.blocks import BaseTable


class TableOfContents(BaseTable):
    block_type: str = BlockTypes.TableOfContents
    block_description: str = "A table of contents."