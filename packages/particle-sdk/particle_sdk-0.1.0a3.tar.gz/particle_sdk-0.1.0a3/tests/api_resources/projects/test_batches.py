# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from particle_sdk import ParticleSDK, AsyncParticleSDK
from particle_sdk.types.projects import Batch

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBatches:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: ParticleSDK) -> None:
        batch = client.projects.batches.create(
            project_id="project_id",
        )
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: ParticleSDK) -> None:
        batch = client.projects.batches.create(
            project_id="project_id",
            batch_id="batch_id",
            batch_type="batch_type",
            demographics_csv=b"raw file contents",
            demographics_json="demographics_json",
            expected_finish_time="expected_finish_time",
            query_count=0,
            state="state",
        )
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: ParticleSDK) -> None:
        response = client.projects.batches.with_raw_response.create(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: ParticleSDK) -> None:
        with client.projects.batches.with_streaming_response.create(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(Batch, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.batches.with_raw_response.create(
                project_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: ParticleSDK) -> None:
        batch = client.projects.batches.retrieve(
            batch_id="batch_id",
            project_id="project_id",
        )
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: ParticleSDK) -> None:
        response = client.projects.batches.with_raw_response.retrieve(
            batch_id="batch_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: ParticleSDK) -> None:
        with client.projects.batches.with_streaming_response.retrieve(
            batch_id="batch_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(Batch, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.batches.with_raw_response.retrieve(
                batch_id="batch_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            client.projects.batches.with_raw_response.retrieve(
                batch_id="",
                project_id="project_id",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: ParticleSDK) -> None:
        batch = client.projects.batches.list(
            "project_id",
        )
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: ParticleSDK) -> None:
        response = client.projects.batches.with_raw_response.list(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = response.parse()
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: ParticleSDK) -> None:
        with client.projects.batches.with_streaming_response.list(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = response.parse()
            assert_matches_type(Batch, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.projects.batches.with_raw_response.list(
                "",
            )


class TestAsyncBatches:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncParticleSDK) -> None:
        batch = await async_client.projects.batches.create(
            project_id="project_id",
        )
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncParticleSDK) -> None:
        batch = await async_client.projects.batches.create(
            project_id="project_id",
            batch_id="batch_id",
            batch_type="batch_type",
            demographics_csv=b"raw file contents",
            demographics_json="demographics_json",
            expected_finish_time="expected_finish_time",
            query_count=0,
            state="state",
        )
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.projects.batches.with_raw_response.create(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.projects.batches.with_streaming_response.create(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(Batch, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.batches.with_raw_response.create(
                project_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncParticleSDK) -> None:
        batch = await async_client.projects.batches.retrieve(
            batch_id="batch_id",
            project_id="project_id",
        )
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.projects.batches.with_raw_response.retrieve(
            batch_id="batch_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.projects.batches.with_streaming_response.retrieve(
            batch_id="batch_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(Batch, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.batches.with_raw_response.retrieve(
                batch_id="batch_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            await async_client.projects.batches.with_raw_response.retrieve(
                batch_id="",
                project_id="project_id",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncParticleSDK) -> None:
        batch = await async_client.projects.batches.list(
            "project_id",
        )
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.projects.batches.with_raw_response.list(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch = await response.parse()
        assert_matches_type(Batch, batch, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.projects.batches.with_streaming_response.list(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch = await response.parse()
            assert_matches_type(Batch, batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.projects.batches.with_raw_response.list(
                "",
            )
