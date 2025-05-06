# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from particle_sdk import ParticleSDK, AsyncParticleSDK
from particle_sdk.types import (
    Patient,
    ResponseMessage,
    PatientListResponse,
    PatientSearchResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: ParticleSDK) -> None:
        patient = client.patients.retrieve(
            "id",
        )
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: ParticleSDK) -> None:
        response = client.patients.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: ParticleSDK) -> None:
        with client.patients.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(Patient, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.patients.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: ParticleSDK) -> None:
        patient = client.patients.list()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: ParticleSDK) -> None:
        patient = client.patients.list(
            continuation_token="continuation_token",
        )
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: ParticleSDK) -> None:
        response = client.patients.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: ParticleSDK) -> None:
        with client.patients.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientListResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: ParticleSDK) -> None:
        patient = client.patients.delete(
            "id",
        )
        assert_matches_type(ResponseMessage, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: ParticleSDK) -> None:
        response = client.patients.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(ResponseMessage, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: ParticleSDK) -> None:
        with client.patients.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(ResponseMessage, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: ParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.patients.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_search(self, client: ParticleSDK) -> None:
        patient = client.patients.search(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        )
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_with_all_params(self, client: ParticleSDK) -> None:
        patient = client.patients.search(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
            address_lines=["703 Ankunding Trail Unit 45"],
            consent=[
                {
                    "consent_date": "2021-01-01",
                    "partner": "Healthix",
                    "permission": "permit",
                }
            ],
            email="john@doe.com",
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            ssn="123-45-6789",
            telephone="234-567-8910",
        )
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search(self, client: ParticleSDK) -> None:
        response = client.patients.with_raw_response.search(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search(self, client: ParticleSDK) -> None:
        with client.patients.with_streaming_response.search(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientSearchResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_submit(self, client: ParticleSDK) -> None:
        patient = client.patients.submit(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        )
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_submit_with_all_params(self, client: ParticleSDK) -> None:
        patient = client.patients.submit(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
            address_lines=["703 Ankunding Trail Unit 45"],
            consent=[
                {
                    "consent_date": "2021-01-01",
                    "partner": "Healthix",
                    "permission": "permit",
                }
            ],
            email="john@doe.com",
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            ssn="123-45-6789",
            telephone="234-567-8910",
        )
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit(self, client: ParticleSDK) -> None:
        response = client.patients.with_raw_response.submit(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit(self, client: ParticleSDK) -> None:
        with client.patients.with_streaming_response.submit(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(Patient, patient, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPatients:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncParticleSDK) -> None:
        patient = await async_client.patients.retrieve(
            "id",
        )
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.patients.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.patients.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(Patient, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.patients.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncParticleSDK) -> None:
        patient = await async_client.patients.list()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncParticleSDK) -> None:
        patient = await async_client.patients.list(
            continuation_token="continuation_token",
        )
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.patients.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientListResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.patients.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientListResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncParticleSDK) -> None:
        patient = await async_client.patients.delete(
            "id",
        )
        assert_matches_type(ResponseMessage, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.patients.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(ResponseMessage, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.patients.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(ResponseMessage, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncParticleSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.patients.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_search(self, async_client: AsyncParticleSDK) -> None:
        patient = await async_client.patients.search(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        )
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncParticleSDK) -> None:
        patient = await async_client.patients.search(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
            address_lines=["703 Ankunding Trail Unit 45"],
            consent=[
                {
                    "consent_date": "2021-01-01",
                    "partner": "Healthix",
                    "permission": "permit",
                }
            ],
            email="john@doe.com",
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            ssn="123-45-6789",
            telephone="234-567-8910",
        )
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.patients.with_raw_response.search(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientSearchResponse, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.patients.with_streaming_response.search(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientSearchResponse, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit(self, async_client: AsyncParticleSDK) -> None:
        patient = await async_client.patients.submit(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        )
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncParticleSDK) -> None:
        patient = await async_client.patients.submit(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
            address_lines=["703 Ankunding Trail Unit 45"],
            consent=[
                {
                    "consent_date": "2021-01-01",
                    "partner": "Healthix",
                    "permission": "permit",
                }
            ],
            email="john@doe.com",
            particle_patient_id="1aa50979-1a8e-416d-8c13-a529033cc898",
            ssn="123-45-6789",
            telephone="234-567-8910",
        )
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncParticleSDK) -> None:
        response = await async_client.patients.with_raw_response.submit(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(Patient, patient, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncParticleSDK) -> None:
        async with async_client.patients.with_streaming_response.submit(
            address_city="Boston",
            address_state="Boston",
            date_of_birth="1970-12-26",
            family_name="Valadez",
            gender="Female",
            given_name="Elvira",
            patient_id="pati-enti-d123-4567",
            postal_code="02215",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(Patient, patient, path=["response"])

        assert cast(Any, response.is_closed) is True
