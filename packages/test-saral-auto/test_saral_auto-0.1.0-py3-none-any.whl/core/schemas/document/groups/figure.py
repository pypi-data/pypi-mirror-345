from core.schemas.document import BlockTypes
from core.schemas.document.groups.base import Group


class FigureGroup(Group):
    block_type: BlockTypes = BlockTypes.FigureGroup
    block_description: str = "A group that contains a figure and associated captions."