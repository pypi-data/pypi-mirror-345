# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TranscriptionCreateResponse", "Data"]


class Data(BaseModel):
    message: Optional[str] = None
    """Informational message about the request status."""

    status: Optional[str] = None
    """The processing status of the transcription request. Always 'pending'."""

    transcription_id: Optional[str] = FieldInfo(alias="transcriptionId", default=None)
    """Unique identifier for the audio transcription request."""


class TranscriptionCreateResponse(BaseModel):
    data: Optional[Data] = None

    status: Optional[str] = None
