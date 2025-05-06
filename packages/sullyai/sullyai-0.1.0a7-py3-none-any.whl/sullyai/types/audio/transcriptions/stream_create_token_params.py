# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["StreamCreateTokenParams"]


class StreamCreateTokenParams(TypedDict, total=False):
    expires_in: Required[Annotated[int, PropertyInfo(alias="expiresIn")]]
    """Duration of the token in seconds"""
