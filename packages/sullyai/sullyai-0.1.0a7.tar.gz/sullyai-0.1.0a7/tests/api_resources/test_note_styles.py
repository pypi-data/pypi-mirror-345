# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sullyai import SullyAI, AsyncSullyAI
from tests.utils import assert_matches_type
from sullyai.types import NoteStyleCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNoteStyles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: SullyAI) -> None:
        note_style = client.note_styles.create(
            sample_note="sampleNote",
        )
        assert_matches_type(NoteStyleCreateResponse, note_style, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: SullyAI) -> None:
        note_style = client.note_styles.create(
            sample_note="sampleNote",
            instructions=["string"],
        )
        assert_matches_type(NoteStyleCreateResponse, note_style, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: SullyAI) -> None:
        response = client.note_styles.with_raw_response.create(
            sample_note="sampleNote",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        note_style = response.parse()
        assert_matches_type(NoteStyleCreateResponse, note_style, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: SullyAI) -> None:
        with client.note_styles.with_streaming_response.create(
            sample_note="sampleNote",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            note_style = response.parse()
            assert_matches_type(NoteStyleCreateResponse, note_style, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncNoteStyles:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncSullyAI) -> None:
        note_style = await async_client.note_styles.create(
            sample_note="sampleNote",
        )
        assert_matches_type(NoteStyleCreateResponse, note_style, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSullyAI) -> None:
        note_style = await async_client.note_styles.create(
            sample_note="sampleNote",
            instructions=["string"],
        )
        assert_matches_type(NoteStyleCreateResponse, note_style, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSullyAI) -> None:
        response = await async_client.note_styles.with_raw_response.create(
            sample_note="sampleNote",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        note_style = await response.parse()
        assert_matches_type(NoteStyleCreateResponse, note_style, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSullyAI) -> None:
        async with async_client.note_styles.with_streaming_response.create(
            sample_note="sampleNote",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            note_style = await response.parse()
            assert_matches_type(NoteStyleCreateResponse, note_style, path=["response"])

        assert cast(Any, response.is_closed) is True
