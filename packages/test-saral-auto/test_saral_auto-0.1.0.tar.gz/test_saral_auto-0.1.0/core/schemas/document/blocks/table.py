from core.schemas.document import BlockTypes
from core.schemas.document.blocks.base_table import BaseTable


class Table(BaseTable):
    block_type: BlockTypes = BlockTypes.Table
    block_description: str = "A table of data, like a results table.  It will be in a tabular format."