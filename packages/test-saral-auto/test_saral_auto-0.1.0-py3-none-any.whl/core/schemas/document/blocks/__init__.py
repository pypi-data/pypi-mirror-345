from __future__ import annotations

from core.schemas.document.blocks.base import Block, BlockId
from core.schemas.document.blocks.base_table import BaseTable
from core.schemas.document.blocks.caption import Caption
from core.schemas.document.blocks.code import Code
from core.schemas.document.blocks.figure import Figure
from core.schemas.document.blocks.footnote import Footnote
from core.schemas.document.blocks.form import Form
from core.schemas.document.blocks.equation import Equation
from core.schemas.document.blocks.handwriting import Handwriting
from core.schemas.document.blocks.inlinemath import InlineMath
from core.schemas.document.blocks.listitem import ListItem
from core.schemas.document.blocks.pagefooter import PageFooter
from core.schemas.document.blocks.pageheader import PageHeader
from core.schemas.document.blocks.picture import Picture
from core.schemas.document.blocks.sectionheader import SectionHeader
from core.schemas.document.blocks.table import Table
from core.schemas.document.blocks.text import Text
from core.schemas.document.blocks.toc import TableOfContents
from core.schemas.document.blocks.complexregion import ComplexRegion
from core.schemas.document.blocks.tablecell import TableCell
from core.schemas.document.blocks.reference import Reference

__all__ = [
    'Block',
    'BlockId',
    'BaseTable',
    'Caption',
    'Code',
    'Figure',
    'Footnote',
    'Form',
    'Equation',
    'Handwriting',
    'InlineMath',
    'ListItem',
    'PageFooter',
    'PageHeader',
    'Picture',
    'SectionHeader',
    'Table',
    'Text',
    'TableOfContents',
    'ComplexRegion',
    'TableCell',
    'Reference'
]