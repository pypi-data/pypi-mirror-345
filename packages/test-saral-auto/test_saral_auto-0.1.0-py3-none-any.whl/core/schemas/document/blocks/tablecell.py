from typing import List, Optional

from core.schemas.document import BlockTypes
from core.schemas.document.blocks import Block


class TableCell(Block):
    block_type: BlockTypes = BlockTypes.TableCell
    rowspan: int
    colspan: int
    row_id: int
    col_id: int
    is_header: bool
    text: str
    html: str
    text_lines: List[str] | None = None
    annotations: Optional[List[dict]] = None
    block_description: str = "A cell in a table."

    @property
    def text(self):
        return "\n".join(self.text_lines)

    def assemble_html(self, document, child_blocks, parent_structure=None):
        tag_cls = "th" if self.is_header else "td"
        tag = f"<{tag_cls}"
        if self.rowspan > 1:
            tag += f" rowspan={self.rowspan}"
        if self.colspan > 1:
            tag += f" colspan={self.colspan}"
        if self.text_lines is None:
            self.text_lines = []
            
        # Use the strikethrough content if available
        if self.strikethrough_content:
            text = self.strikethrough_content
        else:
            text = "<br>".join(self.text_lines)
            
        return f"{tag}>{text}</{tag_cls}>"