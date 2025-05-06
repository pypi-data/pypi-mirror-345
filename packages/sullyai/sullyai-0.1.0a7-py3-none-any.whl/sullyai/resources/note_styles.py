# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

from ..types import note_style_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.note_style_create_response import NoteStyleCreateResponse

__all__ = ["NoteStylesResource", "AsyncNoteStylesResource"]


class NoteStylesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NoteStylesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sullyai/sullyai-python#accessing-raw-response-data-eg-headers
        """
        return NoteStylesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NoteStylesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sullyai/sullyai-python#with_streaming_response
        """
        return NoteStylesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        sample_note: str,
        instructions: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteStyleCreateResponse:
        """
        Creates a note style

        Args:
          sample_note: Sample note text to base the style on

          instructions: Optional instructions for note generation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/note-styles",
            body=maybe_transform(
                {
                    "sample_note": sample_note,
                    "instructions": instructions,
                },
                note_style_create_params.NoteStyleCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteStyleCreateResponse,
        )


class AsyncNoteStylesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNoteStylesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sullyai/sullyai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNoteStylesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNoteStylesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sullyai/sullyai-python#with_streaming_response
        """
        return AsyncNoteStylesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        sample_note: str,
        instructions: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteStyleCreateResponse:
        """
        Creates a note style

        Args:
          sample_note: Sample note text to base the style on

          instructions: Optional instructions for note generation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/note-styles",
            body=await async_maybe_transform(
                {
                    "sample_note": sample_note,
                    "instructions": instructions,
                },
                note_style_create_params.NoteStyleCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteStyleCreateResponse,
        )


class NoteStylesResourceWithRawResponse:
    def __init__(self, note_styles: NoteStylesResource) -> None:
        self._note_styles = note_styles

        self.create = to_raw_response_wrapper(
            note_styles.create,
        )


class AsyncNoteStylesResourceWithRawResponse:
    def __init__(self, note_styles: AsyncNoteStylesResource) -> None:
        self._note_styles = note_styles

        self.create = async_to_raw_response_wrapper(
            note_styles.create,
        )


class NoteStylesResourceWithStreamingResponse:
    def __init__(self, note_styles: NoteStylesResource) -> None:
        self._note_styles = note_styles

        self.create = to_streamed_response_wrapper(
            note_styles.create,
        )


class AsyncNoteStylesResourceWithStreamingResponse:
    def __init__(self, note_styles: AsyncNoteStylesResource) -> None:
        self._note_styles = note_styles

        self.create = async_to_streamed_response_wrapper(
            note_styles.create,
        )
