# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["TranscriptionRetrieveResponse", "Data", "DataPayload", "DataTimestamp"]


class DataPayload(BaseModel):
    transcription: Optional[str] = None
    """Transcription of the audio"""


class DataTimestamp(BaseModel):
    complete: Optional[int] = None
    """Complete timestamp"""

    start: Optional[int] = None
    """Start timestamp"""


class Data(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the audio transcription"""

    payload: Optional[DataPayload] = None
    """Either markdown or JSON representation of the note.

    Both can be present as well.
    """

    timestamp: Optional[DataTimestamp] = None


class TranscriptionRetrieveResponse(BaseModel):
    data: Optional[Data] = None

    date: Optional[datetime] = None
    """Timestamp of the response"""

    status: Optional[str] = None
    """Status of the response"""
