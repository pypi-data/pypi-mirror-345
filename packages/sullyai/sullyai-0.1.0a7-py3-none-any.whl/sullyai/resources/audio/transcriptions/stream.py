# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.audio.transcriptions import stream_create_token_params
from ....types.audio.transcriptions.stream_create_token_response import StreamCreateTokenResponse

__all__ = ["StreamResource", "AsyncStreamResource"]


class StreamResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StreamResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sullyai/sullyai-python#accessing-raw-response-data-eg-headers
        """
        return StreamResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StreamResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sullyai/sullyai-python#with_streaming_response
        """
        return StreamResourceWithStreamingResponse(self)

    def create_token(
        self,
        *,
        expires_in: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StreamCreateTokenResponse:
        """
        Create a temporary authentication token for Streaming Speech-to-Text

        Args:
          expires_in: Duration of the token in seconds

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/audio/transcriptions/stream/token",
            body=maybe_transform({"expires_in": expires_in}, stream_create_token_params.StreamCreateTokenParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StreamCreateTokenResponse,
        )


class AsyncStreamResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStreamResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sullyai/sullyai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStreamResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStreamResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sullyai/sullyai-python#with_streaming_response
        """
        return AsyncStreamResourceWithStreamingResponse(self)

    async def create_token(
        self,
        *,
        expires_in: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StreamCreateTokenResponse:
        """
        Create a temporary authentication token for Streaming Speech-to-Text

        Args:
          expires_in: Duration of the token in seconds

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/audio/transcriptions/stream/token",
            body=await async_maybe_transform(
                {"expires_in": expires_in}, stream_create_token_params.StreamCreateTokenParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StreamCreateTokenResponse,
        )


class StreamResourceWithRawResponse:
    def __init__(self, stream: StreamResource) -> None:
        self._stream = stream

        self.create_token = to_raw_response_wrapper(
            stream.create_token,
        )


class AsyncStreamResourceWithRawResponse:
    def __init__(self, stream: AsyncStreamResource) -> None:
        self._stream = stream

        self.create_token = async_to_raw_response_wrapper(
            stream.create_token,
        )


class StreamResourceWithStreamingResponse:
    def __init__(self, stream: StreamResource) -> None:
        self._stream = stream

        self.create_token = to_streamed_response_wrapper(
            stream.create_token,
        )


class AsyncStreamResourceWithStreamingResponse:
    def __init__(self, stream: AsyncStreamResource) -> None:
        self._stream = stream

        self.create_token = async_to_streamed_response_wrapper(
            stream.create_token,
        )
