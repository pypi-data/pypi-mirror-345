# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from particle_sdk import ParticleSDK, AsyncParticleSDK
from particle_sdk.types import Document, ResponseMessage, DocumentGetPatientDocumentsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocuments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: ParticleSDK) -> None:
        document = client.documents.retrieve(
            "id",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: ParticleSDK) -> None:
        response = client.documents.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: ParticleSDK) -> None:
        with client.documents.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.documents.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: ParticleSDK) -> None:
        document = client.documents.delete(
            "id",
        )
        assert_matches_type(ResponseMessage, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: ParticleSDK) -> None:
        response = client.documents.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(ResponseMessage, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: ParticleSDK) -> None:
        with client.documents.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(ResponseMessage, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.documents.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_patient_documents(self, client: ParticleSDK) -> None:
        document = client.documents.get_patient_documents(
            "id",
        )
        assert_matches_type(DocumentGetPatientDocumentsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_patient_documents(self, client: ParticleSDK) -> None:
        response = client.documents.with_raw_response.get_patient_documents(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentGetPatientDocumentsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_patient_documents(self, client: ParticleSDK) -> None:
        with client.documents.with_streaming_response.get_patient_documents(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentGetPatientDocumentsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_patient_documents(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.documents.with_raw_response.get_patient_documents(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_submit(self, client: ParticleSDK) -> None:
        document = client.documents.submit(
            file=b"raw file contents",
            metadata="metadata",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit(self, client: ParticleSDK) -> None:
        response = client.documents.with_raw_response.submit(
            file=b"raw file contents",
            metadata="metadata",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit(self, client: ParticleSDK) -> None:
        with client.documents.with_streaming_response.submit(
            file=b"raw file contents",
            metadata="metadata",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDocuments:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncParticleSDK) -> None:
        document = await async_client.documents.retrieve(
            "id",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.documents.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.documents.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.documents.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncParticleSDK) -> None:
        document = await async_client.documents.delete(
            "id",
        )
        assert_matches_type(ResponseMessage, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.documents.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(ResponseMessage, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.documents.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(ResponseMessage, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.documents.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_patient_documents(self, async_client: AsyncParticleSDK) -> None:
        document = await async_client.documents.get_patient_documents(
            "id",
        )
        assert_matches_type(DocumentGetPatientDocumentsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_patient_documents(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.documents.with_raw_response.get_patient_documents(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentGetPatientDocumentsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_patient_documents(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.documents.with_streaming_response.get_patient_documents(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentGetPatientDocumentsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_patient_documents(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.documents.with_raw_response.get_patient_documents(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit(self, async_client: AsyncParticleSDK) -> None:
        document = await async_client.documents.submit(
            file=b"raw file contents",
            metadata="metadata",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.documents.with_raw_response.submit(
            file=b"raw file contents",
            metadata="metadata",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.documents.with_streaming_response.submit(
            file=b"raw file contents",
            metadata="metadata",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True
