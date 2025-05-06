# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from .stream import (
    StreamResource,
    AsyncStreamResource,
    StreamResourceWithRawResponse,
    AsyncStreamResourceWithRawResponse,
    StreamResourceWithStreamingResponse,
    AsyncStreamResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ...._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.audio import transcription_create_params
from ...._base_client import make_request_options
from ....types.delete_response import DeleteResponse
from ....types.audio.transcription_create_response import TranscriptionCreateResponse
from ....types.audio.transcription_retrieve_response import TranscriptionRetrieveResponse

__all__ = ["TranscriptionsResource", "AsyncTranscriptionsResource"]


class TranscriptionsResource(SyncAPIResource):
    @cached_property
    def stream(self) -> StreamResource:
        return StreamResource(self._client)

    @cached_property
    def with_raw_response(self) -> TranscriptionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sullyai/sullyai-python#accessing-raw-response-data-eg-headers
        """
        return TranscriptionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TranscriptionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sullyai/sullyai-python#with_streaming_response
        """
        return TranscriptionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        audio: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionCreateResponse:
        """
        Creates a new audio transcription

        Args:
          audio: Audio file to transcribe (supported formats: wav, mp3, m4a, ogg)

          language:
              Language code for transcription:

              - English (en-US, en-GB) - Spanish (es) - French (fr) - German (de) - Italian
                (it) - Portuguese (pt) - Dutch (nl) - Japanese (ja) - Korean (ko) - Chinese
                (zh) - Russian (ru)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "audio": audio,
                "language": language,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["audio"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/v1/audio/transcriptions",
            body=maybe_transform(body, transcription_create_params.TranscriptionCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TranscriptionCreateResponse,
        )

    def retrieve(
        self,
        transcription_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionRetrieveResponse:
        """
        Gets a single audio transcription based on the ID supplied

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transcription_id:
            raise ValueError(f"Expected a non-empty value for `transcription_id` but received {transcription_id!r}")
        return self._get(
            f"/v1/audio/transcriptions/{transcription_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TranscriptionRetrieveResponse,
        )

    def delete(
        self,
        transcription_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Deletes a single audio transcription based on the ID supplied

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transcription_id:
            raise ValueError(f"Expected a non-empty value for `transcription_id` but received {transcription_id!r}")
        return self._delete(
            f"/v1/audio/transcriptions/{transcription_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncTranscriptionsResource(AsyncAPIResource):
    @cached_property
    def stream(self) -> AsyncStreamResource:
        return AsyncStreamResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTranscriptionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sullyai/sullyai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTranscriptionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTranscriptionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sullyai/sullyai-python#with_streaming_response
        """
        return AsyncTranscriptionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        audio: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionCreateResponse:
        """
        Creates a new audio transcription

        Args:
          audio: Audio file to transcribe (supported formats: wav, mp3, m4a, ogg)

          language:
              Language code for transcription:

              - English (en-US, en-GB) - Spanish (es) - French (fr) - German (de) - Italian
                (it) - Portuguese (pt) - Dutch (nl) - Japanese (ja) - Korean (ko) - Chinese
                (zh) - Russian (ru)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "audio": audio,
                "language": language,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["audio"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/v1/audio/transcriptions",
            body=await async_maybe_transform(body, transcription_create_params.TranscriptionCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TranscriptionCreateResponse,
        )

    async def retrieve(
        self,
        transcription_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionRetrieveResponse:
        """
        Gets a single audio transcription based on the ID supplied

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transcription_id:
            raise ValueError(f"Expected a non-empty value for `transcription_id` but received {transcription_id!r}")
        return await self._get(
            f"/v1/audio/transcriptions/{transcription_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TranscriptionRetrieveResponse,
        )

    async def delete(
        self,
        transcription_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Deletes a single audio transcription based on the ID supplied

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transcription_id:
            raise ValueError(f"Expected a non-empty value for `transcription_id` but received {transcription_id!r}")
        return await self._delete(
            f"/v1/audio/transcriptions/{transcription_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class TranscriptionsResourceWithRawResponse:
    def __init__(self, transcriptions: TranscriptionsResource) -> None:
        self._transcriptions = transcriptions

        self.create = to_raw_response_wrapper(
            transcriptions.create,
        )
        self.retrieve = to_raw_response_wrapper(
            transcriptions.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            transcriptions.delete,
        )

    @cached_property
    def stream(self) -> StreamResourceWithRawResponse:
        return StreamResourceWithRawResponse(self._transcriptions.stream)


class AsyncTranscriptionsResourceWithRawResponse:
    def __init__(self, transcriptions: AsyncTranscriptionsResource) -> None:
        self._transcriptions = transcriptions

        self.create = async_to_raw_response_wrapper(
            transcriptions.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            transcriptions.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            transcriptions.delete,
        )

    @cached_property
    def stream(self) -> AsyncStreamResourceWithRawResponse:
        return AsyncStreamResourceWithRawResponse(self._transcriptions.stream)


class TranscriptionsResourceWithStreamingResponse:
    def __init__(self, transcriptions: TranscriptionsResource) -> None:
        self._transcriptions = transcriptions

        self.create = to_streamed_response_wrapper(
            transcriptions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            transcriptions.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            transcriptions.delete,
        )

    @cached_property
    def stream(self) -> StreamResourceWithStreamingResponse:
        return StreamResourceWithStreamingResponse(self._transcriptions.stream)


class AsyncTranscriptionsResourceWithStreamingResponse:
    def __init__(self, transcriptions: AsyncTranscriptionsResource) -> None:
        self._transcriptions = transcriptions

        self.create = async_to_streamed_response_wrapper(
            transcriptions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            transcriptions.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            transcriptions.delete,
        )

    @cached_property
    def stream(self) -> AsyncStreamResourceWithStreamingResponse:
        return AsyncStreamResourceWithStreamingResponse(self._transcriptions.stream)
