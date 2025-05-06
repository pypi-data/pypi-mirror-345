# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["NoteStyleCreateResponse", "Data"]


class Data(BaseModel):
    template: Optional[str] = None
    """The created note style"""


class NoteStyleCreateResponse(BaseModel):
    data: Optional[Data] = None

    date: Optional[datetime] = None
    """Timestamp of the response"""

    status: Optional[str] = None
    """Status of the response"""
