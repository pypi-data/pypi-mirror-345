from core.schemas.document import BlockTypes
from core.schemas.document.groups.base import Group


class PictureGroup(Group):
    block_type: BlockTypes = BlockTypes.PictureGroup
    block_description: str = "A picture along with associated captions."