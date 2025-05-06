# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from particle_sdk import ParticleSDK, AsyncParticleSDK
from particle_sdk.types import Query, QueryListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestQueries:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: ParticleSDK) -> None:
        query = client.queries.create(
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            purpose_of_use="TREATMENT",
        )
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: ParticleSDK) -> None:
        query = client.queries.create(
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            purpose_of_use="TREATMENT",
            address_city="Boston",
            address_lines=["703 Ankunding Trail Unit 45"],
            address_state="Boston",
            email="john@doe.com",
            encounter_date="2022-01-20",
            encounter_type="AMBULATORY",
            hints=["02215"],
            npi="9876543210",
            patient_id="patient_id",
            postal_code="02215",
            specialties=["ONCOLOGY"],
            ssn="123-45-6789",
            telephone="234-567-8910",
        )
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: ParticleSDK) -> None:
        response = client.queries.with_raw_response.create(
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            purpose_of_use="TREATMENT",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        query = response.parse()
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: ParticleSDK) -> None:
        with client.queries.with_streaming_response.create(
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            purpose_of_use="TREATMENT",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            query = response.parse()
            assert_matches_type(Query, query, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: ParticleSDK) -> None:
        query = client.queries.retrieve(
            "id",
        )
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: ParticleSDK) -> None:
        response = client.queries.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        query = response.parse()
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: ParticleSDK) -> None:
        with client.queries.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            query = response.parse()
            assert_matches_type(Query, query, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.queries.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: ParticleSDK) -> None:
        query = client.queries.list()
        assert_matches_type(QueryListResponse, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: ParticleSDK) -> None:
        response = client.queries.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        query = response.parse()
        assert_matches_type(QueryListResponse, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: ParticleSDK) -> None:
        with client.queries.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            query = response.parse()
            assert_matches_type(QueryListResponse, query, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncQueries:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncParticleSDK) -> None:
        query = await async_client.queries.create(
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            purpose_of_use="TREATMENT",
        )
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncParticleSDK) -> None:
        query = await async_client.queries.create(
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            purpose_of_use="TREATMENT",
            address_city="Boston",
            address_lines=["703 Ankunding Trail Unit 45"],
            address_state="Boston",
            email="john@doe.com",
            encounter_date="2022-01-20",
            encounter_type="AMBULATORY",
            hints=["02215"],
            npi="9876543210",
            patient_id="patient_id",
            postal_code="02215",
            specialties=["ONCOLOGY"],
            ssn="123-45-6789",
            telephone="234-567-8910",
        )
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.queries.with_raw_response.create(
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            purpose_of_use="TREATMENT",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        query = await response.parse()
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.queries.with_streaming_response.create(
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            purpose_of_use="TREATMENT",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            query = await response.parse()
            assert_matches_type(Query, query, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncParticleSDK) -> None:
        query = await async_client.queries.retrieve(
            "id",
        )
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.queries.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        query = await response.parse()
        assert_matches_type(Query, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.queries.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            query = await response.parse()
            assert_matches_type(Query, query, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.queries.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncParticleSDK) -> None:
        query = await async_client.queries.list()
        assert_matches_type(QueryListResponse, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.queries.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        query = await response.parse()
        assert_matches_type(QueryListResponse, query, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.queries.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            query = await response.parse()
            assert_matches_type(QueryListResponse, query, path=["response"])

        assert cast(Any, response.is_closed) is True
