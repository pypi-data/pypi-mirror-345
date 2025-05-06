# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..._types import FileTypes

__all__ = ["TranscriptionCreateParams"]


class TranscriptionCreateParams(TypedDict, total=False):
    audio: Required[FileTypes]
    """Audio file to transcribe (supported formats: wav, mp3, m4a, ogg)"""

    language: str
    """Language code for transcription:

    - English (en-US, en-GB) - Spanish (es) - French (fr) - German (de) - Italian
      (it) - Portuguese (pt) - Dutch (nl) - Japanese (ja) - Korean (ko) - Chinese
      (zh) - Russian (ru)
    """
