# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import date

import httpx

from ..types import note_create_params
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
from ..types.delete_response import DeleteResponse
from ..types.note_create_response import NoteCreateResponse
from ..types.note_retrieve_response import NoteRetrieveResponse

__all__ = ["NotesResource", "AsyncNotesResource"]


class NotesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NotesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sullyai/sullyai-python#accessing-raw-response-data-eg-headers
        """
        return NotesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NotesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sullyai/sullyai-python#with_streaming_response
        """
        return NotesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        date: Union[str, date],
        transcript: str,
        context: Optional[str] | NotGiven = NOT_GIVEN,
        instructions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        medication_list: str | NotGiven = NOT_GIVEN,
        note_type: note_create_params.NoteType | NotGiven = NOT_GIVEN,
        patient_info: note_create_params.PatientInfo | NotGiven = NOT_GIVEN,
        previous_note: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteCreateResponse:
        """
        Creates a new note

        Args:
          date: Date of the patient encounter

          context: Additional context for note generation. This field is optional.

          instructions: Special instructions for note generation. This field is optional.

          medication_list: List of up to 50 medications (comma separated) to use as reference for fixing
              spelling errors. This field is optional.

          patient_info: Optional patient information

          previous_note: Reference to a previous note if this is a follow-up. This field is optional.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/notes",
            body=maybe_transform(
                {
                    "date": date,
                    "transcript": transcript,
                    "context": context,
                    "instructions": instructions,
                    "medication_list": medication_list,
                    "note_type": note_type,
                    "patient_info": patient_info,
                    "previous_note": previous_note,
                },
                note_create_params.NoteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteCreateResponse,
        )

    def retrieve(
        self,
        note_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteRetrieveResponse:
        """
        Gets a single note based on the ID supplied

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not note_id:
            raise ValueError(f"Expected a non-empty value for `note_id` but received {note_id!r}")
        return self._get(
            f"/v1/notes/{note_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteRetrieveResponse,
        )

    def delete(
        self,
        note_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Deletes a single note based on the ID supplied

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not note_id:
            raise ValueError(f"Expected a non-empty value for `note_id` but received {note_id!r}")
        return self._delete(
            f"/v1/notes/{note_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncNotesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNotesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sullyai/sullyai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNotesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNotesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sullyai/sullyai-python#with_streaming_response
        """
        return AsyncNotesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        date: Union[str, date],
        transcript: str,
        context: Optional[str] | NotGiven = NOT_GIVEN,
        instructions: Optional[List[str]] | NotGiven = NOT_GIVEN,
        medication_list: str | NotGiven = NOT_GIVEN,
        note_type: note_create_params.NoteType | NotGiven = NOT_GIVEN,
        patient_info: note_create_params.PatientInfo | NotGiven = NOT_GIVEN,
        previous_note: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteCreateResponse:
        """
        Creates a new note

        Args:
          date: Date of the patient encounter

          context: Additional context for note generation. This field is optional.

          instructions: Special instructions for note generation. This field is optional.

          medication_list: List of up to 50 medications (comma separated) to use as reference for fixing
              spelling errors. This field is optional.

          patient_info: Optional patient information

          previous_note: Reference to a previous note if this is a follow-up. This field is optional.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/notes",
            body=await async_maybe_transform(
                {
                    "date": date,
                    "transcript": transcript,
                    "context": context,
                    "instructions": instructions,
                    "medication_list": medication_list,
                    "note_type": note_type,
                    "patient_info": patient_info,
                    "previous_note": previous_note,
                },
                note_create_params.NoteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteCreateResponse,
        )

    async def retrieve(
        self,
        note_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NoteRetrieveResponse:
        """
        Gets a single note based on the ID supplied

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not note_id:
            raise ValueError(f"Expected a non-empty value for `note_id` but received {note_id!r}")
        return await self._get(
            f"/v1/notes/{note_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoteRetrieveResponse,
        )

    async def delete(
        self,
        note_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Deletes a single note based on the ID supplied

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not note_id:
            raise ValueError(f"Expected a non-empty value for `note_id` but received {note_id!r}")
        return await self._delete(
            f"/v1/notes/{note_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class NotesResourceWithRawResponse:
    def __init__(self, notes: NotesResource) -> None:
        self._notes = notes

        self.create = to_raw_response_wrapper(
            notes.create,
        )
        self.retrieve = to_raw_response_wrapper(
            notes.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            notes.delete,
        )


class AsyncNotesResourceWithRawResponse:
    def __init__(self, notes: AsyncNotesResource) -> None:
        self._notes = notes

        self.create = async_to_raw_response_wrapper(
            notes.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            notes.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            notes.delete,
        )


class NotesResourceWithStreamingResponse:
    def __init__(self, notes: NotesResource) -> None:
        self._notes = notes

        self.create = to_streamed_response_wrapper(
            notes.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            notes.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            notes.delete,
        )


class AsyncNotesResourceWithStreamingResponse:
    def __init__(self, notes: AsyncNotesResource) -> None:
        self._notes = notes

        self.create = async_to_streamed_response_wrapper(
            notes.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            notes.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            notes.delete,
        )
