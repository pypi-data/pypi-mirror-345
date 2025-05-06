# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["NoteRetrieveResponse", "Data", "DataPayload", "DataTimestamp"]


class DataPayload(BaseModel):
    json_: Optional[object] = FieldInfo(alias="json", default=None)
    """JSON object of the note.

    The note style used will determine which fields are present. See the
    [SOAP Note](/api-reference/schemas/soap-note) example.
    """

    markdown: Optional[str] = None
    """Markdown string of the note"""


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

    status: Optional[str] = None
    """Processing status of the note"""

    timestamp: Optional[DataTimestamp] = None


class NoteRetrieveResponse(BaseModel):
    data: Optional[Data] = None

    date: Optional[datetime] = None
    """Timestamp of the response"""

    status: Optional[str] = None
    """Status of the response"""
