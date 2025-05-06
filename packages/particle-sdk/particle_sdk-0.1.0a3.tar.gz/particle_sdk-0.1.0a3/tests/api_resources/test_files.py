# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from particle_sdk import ParticleSDK, AsyncParticleSDK
from particle_sdk._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download(self, client: ParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/file_id").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        file = client.files.download(
            file_id="file_id",
            query_id="query_id",
        )
        assert file.is_closed
        assert file.json() == {"foo": "bar"}
        assert cast(Any, file.is_closed) is True
        assert isinstance(file, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download(self, client: ParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/file_id").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        file = client.files.with_raw_response.download(
            file_id="file_id",
            query_id="query_id",
        )

        assert file.is_closed is True
        assert file.http_request.headers.get("X-Stainless-Lang") == "python"
        assert file.json() == {"foo": "bar"}
        assert isinstance(file, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download(self, client: ParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/file_id").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.files.with_streaming_response.download(
            file_id="file_id",
            query_id="query_id",
        ) as file:
            assert not file.is_closed
            assert file.http_request.headers.get("X-Stainless-Lang") == "python"

            assert file.json() == {"foo": "bar"}
            assert cast(Any, file.is_closed) is True
            assert isinstance(file, StreamedBinaryAPIResponse)

        assert cast(Any, file.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `query_id` but received ''"):
            client.files.with_raw_response.download(
                file_id="file_id",
                query_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.files.with_raw_response.download(
                file_id="",
                query_id="query_id",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download_zip(self, client: ParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/zip").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        file = client.files.download_zip(
            "query_id",
        )
        assert file.is_closed
        assert file.json() == {"foo": "bar"}
        assert cast(Any, file.is_closed) is True
        assert isinstance(file, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download_zip(self, client: ParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/zip").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        file = client.files.with_raw_response.download_zip(
            "query_id",
        )

        assert file.is_closed is True
        assert file.http_request.headers.get("X-Stainless-Lang") == "python"
        assert file.json() == {"foo": "bar"}
        assert isinstance(file, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download_zip(self, client: ParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/zip").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.files.with_streaming_response.download_zip(
            "query_id",
        ) as file:
            assert not file.is_closed
            assert file.http_request.headers.get("X-Stainless-Lang") == "python"

            assert file.json() == {"foo": "bar"}
            assert cast(Any, file.is_closed) is True
            assert isinstance(file, StreamedBinaryAPIResponse)

        assert cast(Any, file.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download_zip(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `query_id` but received ''"):
            client.files.with_raw_response.download_zip(
                "",
            )


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download(self, async_client: AsyncParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/file_id").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        file = await async_client.files.download(
            file_id="file_id",
            query_id="query_id",
        )
        assert file.is_closed
        assert await file.json() == {"foo": "bar"}
        assert cast(Any, file.is_closed) is True
        assert isinstance(file, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download(self, async_client: AsyncParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/file_id").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        file = await async_client.files.with_raw_response.download(
            file_id="file_id",
            query_id="query_id",
        )

        assert file.is_closed is True
        assert file.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await file.json() == {"foo": "bar"}
        assert isinstance(file, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download(self, async_client: AsyncParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/file_id").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.files.with_streaming_response.download(
            file_id="file_id",
            query_id="query_id",
        ) as file:
            assert not file.is_closed
            assert file.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await file.json() == {"foo": "bar"}
            assert cast(Any, file.is_closed) is True
            assert isinstance(file, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, file.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `query_id` but received ''"):
            await async_client.files.with_raw_response.download(
                file_id="file_id",
                query_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.files.with_raw_response.download(
                file_id="",
                query_id="query_id",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download_zip(self, async_client: AsyncParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/zip").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        file = await async_client.files.download_zip(
            "query_id",
        )
        assert file.is_closed
        assert await file.json() == {"foo": "bar"}
        assert cast(Any, file.is_closed) is True
        assert isinstance(file, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download_zip(self, async_client: AsyncParticleSDK, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/v1/files/query_id/zip").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        file = await async_client.files.with_raw_response.download_zip(
            "query_id",
        )

        assert file.is_closed is True
        assert file.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await file.json() == {"foo": "bar"}
        assert isinstance(file, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download_zip(
        self, async_client: AsyncParticleSDK, respx_mock: MockRouter
    ) -> None:
        respx_mock.get("/api/v1/files/query_id/zip").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.files.with_streaming_response.download_zip(
            "query_id",
        ) as file:
            assert not file.is_closed
            assert file.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await file.json() == {"foo": "bar"}
            assert cast(Any, file.is_closed) is True
            assert isinstance(file, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, file.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download_zip(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `query_id` but received ''"):
            await async_client.files.with_raw_response.download_zip(
                "",
            )
