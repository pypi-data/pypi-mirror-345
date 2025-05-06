# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from particle_sdk import ParticleSDK, AsyncParticleSDK
from particle_sdk.types.deltas import Datasets

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFlat:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_collect_datasets(self, client: ParticleSDK) -> None:
        flat = client.deltas.flat.collect_datasets(
            particle_patient_id="particle_patient_id",
        )
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_collect_datasets_with_all_params(self, client: ParticleSDK) -> None:
        flat = client.deltas.flat.collect_datasets(
            particle_patient_id="particle_patient_id",
            _since="_since",
        )
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_collect_datasets(self, client: ParticleSDK) -> None:
        response = client.deltas.flat.with_raw_response.collect_datasets(
            particle_patient_id="particle_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flat = response.parse()
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_collect_datasets(self, client: ParticleSDK) -> None:
        with client.deltas.flat.with_streaming_response.collect_datasets(
            particle_patient_id="particle_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flat = response.parse()
            assert_matches_type(Datasets, flat, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_collect_datasets(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `particle_patient_id` but received ''"):
            client.deltas.flat.with_raw_response.collect_datasets(
                particle_patient_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_resource(self, client: ParticleSDK) -> None:
        flat = client.deltas.flat.get_resource(
            resource_id="resource_id",
            particle_patient_id="particle_patient_id",
            resource_type="resource_type",
        )
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_resource(self, client: ParticleSDK) -> None:
        response = client.deltas.flat.with_raw_response.get_resource(
            resource_id="resource_id",
            particle_patient_id="particle_patient_id",
            resource_type="resource_type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flat = response.parse()
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_resource(self, client: ParticleSDK) -> None:
        with client.deltas.flat.with_streaming_response.get_resource(
            resource_id="resource_id",
            particle_patient_id="particle_patient_id",
            resource_type="resource_type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flat = response.parse()
            assert_matches_type(Datasets, flat, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_resource(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `particle_patient_id` but received ''"):
            client.deltas.flat.with_raw_response.get_resource(
                resource_id="resource_id",
                particle_patient_id="",
                resource_type="resource_type",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_type` but received ''"):
            client.deltas.flat.with_raw_response.get_resource(
                resource_id="resource_id",
                particle_patient_id="particle_patient_id",
                resource_type="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            client.deltas.flat.with_raw_response.get_resource(
                resource_id="",
                particle_patient_id="particle_patient_id",
                resource_type="resource_type",
            )


class TestAsyncFlat:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_collect_datasets(self, async_client: AsyncParticleSDK) -> None:
        flat = await async_client.deltas.flat.collect_datasets(
            particle_patient_id="particle_patient_id",
        )
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_collect_datasets_with_all_params(self, async_client: AsyncParticleSDK) -> None:
        flat = await async_client.deltas.flat.collect_datasets(
            particle_patient_id="particle_patient_id",
            _since="_since",
        )
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_collect_datasets(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.deltas.flat.with_raw_response.collect_datasets(
            particle_patient_id="particle_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flat = await response.parse()
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_collect_datasets(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.deltas.flat.with_streaming_response.collect_datasets(
            particle_patient_id="particle_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flat = await response.parse()
            assert_matches_type(Datasets, flat, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_collect_datasets(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `particle_patient_id` but received ''"):
            await async_client.deltas.flat.with_raw_response.collect_datasets(
                particle_patient_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_resource(self, async_client: AsyncParticleSDK) -> None:
        flat = await async_client.deltas.flat.get_resource(
            resource_id="resource_id",
            particle_patient_id="particle_patient_id",
            resource_type="resource_type",
        )
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_resource(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.deltas.flat.with_raw_response.get_resource(
            resource_id="resource_id",
            particle_patient_id="particle_patient_id",
            resource_type="resource_type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flat = await response.parse()
        assert_matches_type(Datasets, flat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_resource(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.deltas.flat.with_streaming_response.get_resource(
            resource_id="resource_id",
            particle_patient_id="particle_patient_id",
            resource_type="resource_type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flat = await response.parse()
            assert_matches_type(Datasets, flat, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_resource(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `particle_patient_id` but received ''"):
            await async_client.deltas.flat.with_raw_response.get_resource(
                resource_id="resource_id",
                particle_patient_id="",
                resource_type="resource_type",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_type` but received ''"):
            await async_client.deltas.flat.with_raw_response.get_resource(
                resource_id="resource_id",
                particle_patient_id="particle_patient_id",
                resource_type="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource_id` but received ''"):
            await async_client.deltas.flat.with_raw_response.get_resource(
                resource_id="",
                particle_patient_id="particle_patient_id",
                resource_type="resource_type",
            )
