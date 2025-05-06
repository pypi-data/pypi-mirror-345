# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

from ..._compat import PYDANTIC_V2
from ..._models import BaseModel

__all__ = ["HeadingSection"]


class HeadingSection(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the section."""

    children: Optional[List["Section"]] = None
    """Nested sections under the heading."""

    level: Optional[int] = None
    """Specifies the heading level (e.g., H1 to H6)."""

    text: Optional[str] = None
    """The actual text of the heading."""

    type: Optional[Literal["heading", "text", "list"]] = None


from .section import Section

if PYDANTIC_V2:
    HeadingSection.model_rebuild()
else:
    HeadingSection.update_forward_refs()  # type: ignore
