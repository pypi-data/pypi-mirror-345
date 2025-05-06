# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TYPE_CHECKING, List, Union, Optional
from typing_extensions import Literal, TypeAlias, TypeAliasType

from pydantic import Field as FieldInfo

from ..._compat import PYDANTIC_V2
from ..._models import BaseModel

__all__ = ["Section", "UnionMember1", "UnionMember1Properties", "UnionMember2", "UnionMember2Properties"]


class UnionMember1Properties(BaseModel):
    bold: Optional[bool] = None
    """Whether the text should be bold."""

    detail_level: Optional[Literal["exhaustive", "detailed", "standard", "brief", "minimal"]] = None
    """Determines the level of detail in the text content."""

    empty_placeholder: Optional[str] = FieldInfo(alias="emptyPlaceholder", default=None)
    """Placeholder text to display if content is empty."""

    formatting_style: Optional[Literal["markdown", "plain"]] = None
    """Specifies the formatting style of the text."""

    hide_if_empty: Optional[bool] = FieldInfo(alias="hideIfEmpty", default=None)
    """Whether to hide the content if it's empty."""

    italic: Optional[bool] = None
    """Whether the text should be italicized."""

    tone: Optional[Literal["formal", "casual", "technical", "friendly", "instructional"]] = None
    """Defines the tone of the generated text."""


class UnionMember1(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the section."""

    bold_label: Optional[bool] = None
    """Whether the label should be bold."""

    italic_label: Optional[bool] = None
    """Whether the label should be italicized."""

    label: Optional[str] = None
    """An optional label for the text section."""

    list_type: Optional[Literal["bullet", "numeric"]] = None
    """Defines whether text should be formatted as a bullet or numeric list."""

    max_paragraphs: Optional[int] = None
    """Maximum number of paragraphs allowed."""

    max_sentences: Optional[int] = None
    """Maximum number of sentences allowed."""

    min_paragraphs: Optional[int] = None
    """Minimum number of paragraphs required."""

    min_sentences: Optional[int] = None
    """Minimum number of sentences required."""

    properties: Optional[UnionMember1Properties] = None
    """Common properties for text-based content."""

    result: Optional[str] = None
    """The generated text content."""

    type: Optional[Literal["text", "heading", "list"]] = None


class UnionMember2Properties(BaseModel):
    bold: Optional[bool] = None
    """Whether the text should be bold."""

    detail_level: Optional[Literal["exhaustive", "detailed", "standard", "brief", "minimal"]] = None
    """Determines the level of detail in the text content."""

    empty_placeholder: Optional[str] = FieldInfo(alias="emptyPlaceholder", default=None)
    """Placeholder text to display if content is empty."""

    formatting_style: Optional[Literal["markdown", "plain"]] = None
    """Specifies the formatting style of the text."""

    hide_if_empty: Optional[bool] = FieldInfo(alias="hideIfEmpty", default=None)
    """Whether to hide the content if it's empty."""

    italic: Optional[bool] = None
    """Whether the text should be italicized."""

    tone: Optional[Literal["formal", "casual", "technical", "friendly", "instructional"]] = None
    """Defines the tone of the generated text."""


class UnionMember2(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the section."""

    list_type: Optional[Literal["bullet", "numeric"]] = None
    """Defines whether the list is bulleted or numbered."""

    max_items: Optional[int] = None
    """Maximum number of items allowed in the list."""

    min_items: Optional[int] = None
    """Minimum number of items required in the list."""

    properties: Optional[UnionMember2Properties] = None
    """Common properties for text-based content."""

    result: Optional[List[str]] = None
    """The generated list items."""

    type: Optional[Literal["list", "heading", "text"]] = None


if TYPE_CHECKING or PYDANTIC_V2:
    Section = TypeAliasType("Section", Union["HeadingSection", UnionMember1, UnionMember2])
else:
    Section: TypeAlias = Union["HeadingSection", UnionMember1, UnionMember2]

from .heading_section import HeadingSection

if PYDANTIC_V2:
    UnionMember1.model_rebuild()
    UnionMember1Properties.model_rebuild()
    UnionMember2.model_rebuild()
    UnionMember2Properties.model_rebuild()
else:
    UnionMember1.update_forward_refs()  # type: ignore
    UnionMember1Properties.update_forward_refs()  # type: ignore
    UnionMember2.update_forward_refs()  # type: ignore
    UnionMember2Properties.update_forward_refs()  # type: ignore
