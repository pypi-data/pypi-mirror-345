# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from particle_sdk import ParticleSDK, AsyncParticleSDK
from particle_sdk.types import Query, DeltaSubmitResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeltas:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_status(self, client: ParticleSDK) -> None:
        delta = client.deltas.retrieve_status(
            "particle_patient_id",
        )
        assert_matches_type(Query, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_status(self, client: ParticleSDK) -> None:
        response = client.deltas.with_raw_response.retrieve_status(
            "particle_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        delta = response.parse()
        assert_matches_type(Query, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_status(self, client: ParticleSDK) -> None:
        with client.deltas.with_streaming_response.retrieve_status(
            "particle_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            delta = response.parse()
            assert_matches_type(Query, delta, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_status(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `particle_patient_id` but received ''"):
            client.deltas.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_submit(self, client: ParticleSDK) -> None:
        delta = client.deltas.submit(
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            purpose_of_use="TREATMENT",
        )
        assert_matches_type(DeltaSubmitResponse, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_with_all_params(self, client: ParticleSDK) -> None:
        delta = client.deltas.submit(
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            purpose_of_use="TREATMENT",
            encounter_date="2020-01-17",
            encounter_type="AMBULATORY",
            hints=["02215"],
            specialties=["ONCOLOGY"],
        )
        assert_matches_type(DeltaSubmitResponse, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit(self, client: ParticleSDK) -> None:
        response = client.deltas.with_raw_response.submit(
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            purpose_of_use="TREATMENT",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        delta = response.parse()
        assert_matches_type(DeltaSubmitResponse, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit(self, client: ParticleSDK) -> None:
        with client.deltas.with_streaming_response.submit(
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            purpose_of_use="TREATMENT",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            delta = response.parse()
            assert_matches_type(DeltaSubmitResponse, delta, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDeltas:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncParticleSDK) -> None:
        delta = await async_client.deltas.retrieve_status(
            "particle_patient_id",
        )
        assert_matches_type(Query, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.deltas.with_raw_response.retrieve_status(
            "particle_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        delta = await response.parse()
        assert_matches_type(Query, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.deltas.with_streaming_response.retrieve_status(
            "particle_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            delta = await response.parse()
            assert_matches_type(Query, delta, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_status(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `particle_patient_id` but received ''"):
            await async_client.deltas.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit(self, async_client: AsyncParticleSDK) -> None:
        delta = await async_client.deltas.submit(
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            purpose_of_use="TREATMENT",
        )
        assert_matches_type(DeltaSubmitResponse, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncParticleSDK) -> None:
        delta = await async_client.deltas.submit(
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            purpose_of_use="TREATMENT",
            encounter_date="2020-01-17",
            encounter_type="AMBULATORY",
            hints=["02215"],
            specialties=["ONCOLOGY"],
        )
        assert_matches_type(DeltaSubmitResponse, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.deltas.with_raw_response.submit(
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            purpose_of_use="TREATMENT",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        delta = await response.parse()
        assert_matches_type(DeltaSubmitResponse, delta, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.deltas.with_streaming_response.submit(
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            purpose_of_use="TREATMENT",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            delta = await response.parse()
            assert_matches_type(DeltaSubmitResponse, delta, path=["response"])

        assert cast(Any, response.is_closed) is True
