# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["NoteStyleCreateParams"]


class NoteStyleCreateParams(TypedDict, total=False):
    sample_note: Required[Annotated[str, PropertyInfo(alias="sampleNote")]]
    """Sample note text to base the style on"""

    instructions: List[str]
    """Optional instructions for note generation"""
