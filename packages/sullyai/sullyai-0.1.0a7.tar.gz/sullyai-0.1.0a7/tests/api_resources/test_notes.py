# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sullyai import SullyAI, AsyncSullyAI
from tests.utils import assert_matches_type
from sullyai.types import DeleteResponse, NoteCreateResponse, NoteRetrieveResponse
from sullyai._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNotes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: SullyAI) -> None:
        note = client.notes.create(
            date=parse_date("2019-12-27"),
            transcript="Hey, how's it going? Good good yeah, so what's going on? Yeah, hi I'm Edward yeah hi hi Edward. How's it going? Yeah, good good. So I've been having a couple of issues like my back pain and knee pain.",
        )
        assert_matches_type(NoteCreateResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: SullyAI) -> None:
        note = client.notes.create(
            date=parse_date("2019-12-27"),
            transcript="Hey, how's it going? Good good yeah, so what's going on? Yeah, hi I'm Edward yeah hi hi Edward. How's it going? Yeah, good good. So I've been having a couple of issues like my back pain and knee pain.",
            context="context",
            instructions=[
                "Use a professional and concise tone.",
                "Include key details without unnecessary elaboration.",
                "Ensure clarity for a general audience.",
            ],
            medication_list="medicationList",
            note_type={
                "description": "description",
                "include_json": True,
                "template": "write a standard clinical SOAP note with the following sections: - **Subjective**: Contains detailed HPI. - **Objective**: Contains PE and ROS. - **Assessment**: Contains differential diagnoses with corresponding plans. - **Patient Instructions**: Contains a list of instructions for the patient.",
                "type": "note_style",
            },
            patient_info={
                "date_of_birth": parse_date("2019-12-27"),
                "gender": "male",
                "name": "name",
            },
            previous_note="previousNote",
        )
        assert_matches_type(NoteCreateResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: SullyAI) -> None:
        response = client.notes.with_raw_response.create(
            date=parse_date("2019-12-27"),
            transcript="Hey, how's it going? Good good yeah, so what's going on? Yeah, hi I'm Edward yeah hi hi Edward. How's it going? Yeah, good good. So I've been having a couple of issues like my back pain and knee pain.",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        note = response.parse()
        assert_matches_type(NoteCreateResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: SullyAI) -> None:
        with client.notes.with_streaming_response.create(
            date=parse_date("2019-12-27"),
            transcript="Hey, how's it going? Good good yeah, so what's going on? Yeah, hi I'm Edward yeah hi hi Edward. How's it going? Yeah, good good. So I've been having a couple of issues like my back pain and knee pain.",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            note = response.parse()
            assert_matches_type(NoteCreateResponse, note, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: SullyAI) -> None:
        note = client.notes.retrieve(
            "noteId",
        )
        assert_matches_type(NoteRetrieveResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: SullyAI) -> None:
        response = client.notes.with_raw_response.retrieve(
            "noteId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        note = response.parse()
        assert_matches_type(NoteRetrieveResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: SullyAI) -> None:
        with client.notes.with_streaming_response.retrieve(
            "noteId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            note = response.parse()
            assert_matches_type(NoteRetrieveResponse, note, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: SullyAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `note_id` but received ''"):
            client.notes.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: SullyAI) -> None:
        note = client.notes.delete(
            "noteId",
        )
        assert_matches_type(DeleteResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: SullyAI) -> None:
        response = client.notes.with_raw_response.delete(
            "noteId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        note = response.parse()
        assert_matches_type(DeleteResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: SullyAI) -> None:
        with client.notes.with_streaming_response.delete(
            "noteId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            note = response.parse()
            assert_matches_type(DeleteResponse, note, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: SullyAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `note_id` but received ''"):
            client.notes.with_raw_response.delete(
                "",
            )


class TestAsyncNotes:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncSullyAI) -> None:
        note = await async_client.notes.create(
            date=parse_date("2019-12-27"),
            transcript="Hey, how's it going? Good good yeah, so what's going on? Yeah, hi I'm Edward yeah hi hi Edward. How's it going? Yeah, good good. So I've been having a couple of issues like my back pain and knee pain.",
        )
        assert_matches_type(NoteCreateResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSullyAI) -> None:
        note = await async_client.notes.create(
            date=parse_date("2019-12-27"),
            transcript="Hey, how's it going? Good good yeah, so what's going on? Yeah, hi I'm Edward yeah hi hi Edward. How's it going? Yeah, good good. So I've been having a couple of issues like my back pain and knee pain.",
            context="context",
            instructions=[
                "Use a professional and concise tone.",
                "Include key details without unnecessary elaboration.",
                "Ensure clarity for a general audience.",
            ],
            medication_list="medicationList",
            note_type={
                "description": "description",
                "include_json": True,
                "template": "write a standard clinical SOAP note with the following sections: - **Subjective**: Contains detailed HPI. - **Objective**: Contains PE and ROS. - **Assessment**: Contains differential diagnoses with corresponding plans. - **Patient Instructions**: Contains a list of instructions for the patient.",
                "type": "note_style",
            },
            patient_info={
                "date_of_birth": parse_date("2019-12-27"),
                "gender": "male",
                "name": "name",
            },
            previous_note="previousNote",
        )
        assert_matches_type(NoteCreateResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSullyAI) -> None:
        response = await async_client.notes.with_raw_response.create(
            date=parse_date("2019-12-27"),
            transcript="Hey, how's it going? Good good yeah, so what's going on? Yeah, hi I'm Edward yeah hi hi Edward. How's it going? Yeah, good good. So I've been having a couple of issues like my back pain and knee pain.",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        note = await response.parse()
        assert_matches_type(NoteCreateResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSullyAI) -> None:
        async with async_client.notes.with_streaming_response.create(
            date=parse_date("2019-12-27"),
            transcript="Hey, how's it going? Good good yeah, so what's going on? Yeah, hi I'm Edward yeah hi hi Edward. How's it going? Yeah, good good. So I've been having a couple of issues like my back pain and knee pain.",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            note = await response.parse()
            assert_matches_type(NoteCreateResponse, note, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSullyAI) -> None:
        note = await async_client.notes.retrieve(
            "noteId",
        )
        assert_matches_type(NoteRetrieveResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSullyAI) -> None:
        response = await async_client.notes.with_raw_response.retrieve(
            "noteId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        note = await response.parse()
        assert_matches_type(NoteRetrieveResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSullyAI) -> None:
        async with async_client.notes.with_streaming_response.retrieve(
            "noteId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            note = await response.parse()
            assert_matches_type(NoteRetrieveResponse, note, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSullyAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `note_id` but received ''"):
            await async_client.notes.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncSullyAI) -> None:
        note = await async_client.notes.delete(
            "noteId",
        )
        assert_matches_type(DeleteResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncSullyAI) -> None:
        response = await async_client.notes.with_raw_response.delete(
            "noteId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        note = await response.parse()
        assert_matches_type(DeleteResponse, note, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncSullyAI) -> None:
        async with async_client.notes.with_streaming_response.delete(
            "noteId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            note = await response.parse()
            assert_matches_type(DeleteResponse, note, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncSullyAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `note_id` but received ''"):
            await async_client.notes.with_raw_response.delete(
                "",
            )
