# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["NoteCreateResponse", "Data"]


class Data(BaseModel):
    note_id: Optional[str] = FieldInfo(alias="noteId", default=None)
    """Unique identifier for the created note"""


class NoteCreateResponse(BaseModel):
    data: Optional[Data] = None

    date: Optional[datetime] = None
    """Timestamp of the response"""

    status: Optional[str] = None
    """Status of the response"""
