from typing import List

from core.schemas.document import BlockTypes
from core.schemas.document.blocks.base_table import BaseTable


class Form(BaseTable):
    block_type: BlockTypes = BlockTypes.Form
    block_description: str = "A form, such as a tax form, that contains fields and labels.  It most likely doesn't have a table structure."