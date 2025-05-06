# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from particle_sdk import ParticleSDK, AsyncParticleSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_generate_token(self, client: ParticleSDK) -> None:
        auth = client.auth.generate_token(
            client_id="client-id",
            client_secret="client-secret",
            scope="scope",
        )
        assert_matches_type(str, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_generate_token(self, client: ParticleSDK) -> None:
        response = client.auth.with_raw_response.generate_token(
            client_id="client-id",
            client_secret="client-secret",
            scope="scope",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(str, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_generate_token(self, client: ParticleSDK) -> None:
        with client.auth.with_streaming_response.generate_token(
            client_id="client-id",
            client_secret="client-secret",
            scope="scope",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(str, auth, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAuth:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_generate_token(self, async_client: AsyncParticleSDK) -> None:
        auth = await async_client.auth.generate_token(
            client_id="client-id",
            client_secret="client-secret",
            scope="scope",
        )
        assert_matches_type(str, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_generate_token(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.auth.with_raw_response.generate_token(
            client_id="client-id",
            client_secret="client-secret",
            scope="scope",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(str, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_generate_token(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.auth.with_streaming_response.generate_token(
            client_id="client-id",
            client_secret="client-secret",
            scope="scope",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(str, auth, path=["response"])

        assert cast(Any, response.is_closed) is True
