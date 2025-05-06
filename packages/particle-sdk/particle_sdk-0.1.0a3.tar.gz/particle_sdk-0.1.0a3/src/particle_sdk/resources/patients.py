# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable

import httpx

from ..types import patient_list_params, patient_search_params, patient_submit_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.patient import Patient
from ..types.response_message import ResponseMessage
from ..types.patient_list_response import PatientListResponse
from ..types.patient_search_response import PatientSearchResponse

__all__ = ["PatientsResource", "AsyncPatientsResource"]


class PatientsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return PatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return PatientsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Patient:
        """
        Get Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/patients/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Patient,
        )

    def list(
        self,
        *,
        continuation_token: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientListResponse:
        """
        List Patients

        Args:
          continuation_token: Continuation Token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v1/patients",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"continuation_token": continuation_token}, patient_list_params.PatientListParams
                ),
            ),
            cast_to=PatientListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseMessage:
        """
        Delete Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/api/v1/patients/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseMessage,
        )

    def search(
        self,
        *,
        address_city: str,
        address_state: str,
        date_of_birth: str,
        family_name: str,
        gender: str,
        given_name: str,
        patient_id: str,
        postal_code: str,
        address_lines: List[str] | NotGiven = NOT_GIVEN,
        consent: Iterable[patient_search_params.Consent] | NotGiven = NOT_GIVEN,
        email: str | NotGiven = NOT_GIVEN,
        particle_patient_id: str | NotGiven = NOT_GIVEN,
        ssn: str | NotGiven = NOT_GIVEN,
        telephone: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientSearchResponse:
        """
        Search Patient

        Args:
          address_city: The patient's home city.

          address_state: The patient's home state.

          date_of_birth: The patient's date of birth, this field is required and must be of the format
              YYYY-MM-DD.

          family_name: The patient's family name (last name), this field is required.

          gender: The patient's gender, must be either Female or Female.

          given_name: The patient's given name (first name), this field is required.

          patient_id: The unique patient id in an external system.

          postal_code: The patient's home postal (zip) code.

          address_lines: The patient's home street address. This should not include the patient's city,
              state, or zip code.

          consent: The patient's consent information.

          email: The patient's email, must be a valid email address.

          particle_patient_id: The Particle Assigned Patient ID. Output only.

          ssn: The patient's social security number, must be a valid US social security number.

          telephone: The patient's telephone number.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/patients/search",
            body=maybe_transform(
                {
                    "address_city": address_city,
                    "address_state": address_state,
                    "date_of_birth": date_of_birth,
                    "family_name": family_name,
                    "gender": gender,
                    "given_name": given_name,
                    "patient_id": patient_id,
                    "postal_code": postal_code,
                    "address_lines": address_lines,
                    "consent": consent,
                    "email": email,
                    "particle_patient_id": particle_patient_id,
                    "ssn": ssn,
                    "telephone": telephone,
                },
                patient_search_params.PatientSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientSearchResponse,
        )

    def submit(
        self,
        *,
        address_city: str,
        address_state: str,
        date_of_birth: str,
        family_name: str,
        gender: str,
        given_name: str,
        patient_id: str,
        postal_code: str,
        address_lines: List[str] | NotGiven = NOT_GIVEN,
        consent: Iterable[patient_submit_params.Consent] | NotGiven = NOT_GIVEN,
        email: str | NotGiven = NOT_GIVEN,
        particle_patient_id: str | NotGiven = NOT_GIVEN,
        ssn: str | NotGiven = NOT_GIVEN,
        telephone: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Patient:
        """
        Submit Patient

        Args:
          address_city: The patient's home city.

          address_state: The patient's home state.

          date_of_birth: The patient's date of birth, this field is required and must be of the format
              YYYY-MM-DD.

          family_name: The patient's family name (last name), this field is required.

          gender: The patient's gender, must be either Female or Female.

          given_name: The patient's given name (first name), this field is required.

          patient_id: The unique patient id in an external system.

          postal_code: The patient's home postal (zip) code.

          address_lines: The patient's home street address. This should not include the patient's city,
              state, or zip code.

          consent: The patient's consent information.

          email: The patient's email, must be a valid email address.

          particle_patient_id: The Particle Assigned Patient ID. Output only.

          ssn: The patient's social security number, must be a valid US social security number.

          telephone: The patient's telephone number.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/patients",
            body=maybe_transform(
                {
                    "address_city": address_city,
                    "address_state": address_state,
                    "date_of_birth": date_of_birth,
                    "family_name": family_name,
                    "gender": gender,
                    "given_name": given_name,
                    "patient_id": patient_id,
                    "postal_code": postal_code,
                    "address_lines": address_lines,
                    "consent": consent,
                    "email": email,
                    "particle_patient_id": particle_patient_id,
                    "ssn": ssn,
                    "telephone": telephone,
                },
                patient_submit_params.PatientSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Patient,
        )


class AsyncPatientsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPatientsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return AsyncPatientsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Patient:
        """
        Get Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/patients/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Patient,
        )

    async def list(
        self,
        *,
        continuation_token: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientListResponse:
        """
        List Patients

        Args:
          continuation_token: Continuation Token

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v1/patients",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"continuation_token": continuation_token}, patient_list_params.PatientListParams
                ),
            ),
            cast_to=PatientListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseMessage:
        """
        Delete Patient

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/api/v1/patients/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseMessage,
        )

    async def search(
        self,
        *,
        address_city: str,
        address_state: str,
        date_of_birth: str,
        family_name: str,
        gender: str,
        given_name: str,
        patient_id: str,
        postal_code: str,
        address_lines: List[str] | NotGiven = NOT_GIVEN,
        consent: Iterable[patient_search_params.Consent] | NotGiven = NOT_GIVEN,
        email: str | NotGiven = NOT_GIVEN,
        particle_patient_id: str | NotGiven = NOT_GIVEN,
        ssn: str | NotGiven = NOT_GIVEN,
        telephone: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PatientSearchResponse:
        """
        Search Patient

        Args:
          address_city: The patient's home city.

          address_state: The patient's home state.

          date_of_birth: The patient's date of birth, this field is required and must be of the format
              YYYY-MM-DD.

          family_name: The patient's family name (last name), this field is required.

          gender: The patient's gender, must be either Female or Female.

          given_name: The patient's given name (first name), this field is required.

          patient_id: The unique patient id in an external system.

          postal_code: The patient's home postal (zip) code.

          address_lines: The patient's home street address. This should not include the patient's city,
              state, or zip code.

          consent: The patient's consent information.

          email: The patient's email, must be a valid email address.

          particle_patient_id: The Particle Assigned Patient ID. Output only.

          ssn: The patient's social security number, must be a valid US social security number.

          telephone: The patient's telephone number.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/patients/search",
            body=await async_maybe_transform(
                {
                    "address_city": address_city,
                    "address_state": address_state,
                    "date_of_birth": date_of_birth,
                    "family_name": family_name,
                    "gender": gender,
                    "given_name": given_name,
                    "patient_id": patient_id,
                    "postal_code": postal_code,
                    "address_lines": address_lines,
                    "consent": consent,
                    "email": email,
                    "particle_patient_id": particle_patient_id,
                    "ssn": ssn,
                    "telephone": telephone,
                },
                patient_search_params.PatientSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PatientSearchResponse,
        )

    async def submit(
        self,
        *,
        address_city: str,
        address_state: str,
        date_of_birth: str,
        family_name: str,
        gender: str,
        given_name: str,
        patient_id: str,
        postal_code: str,
        address_lines: List[str] | NotGiven = NOT_GIVEN,
        consent: Iterable[patient_submit_params.Consent] | NotGiven = NOT_GIVEN,
        email: str | NotGiven = NOT_GIVEN,
        particle_patient_id: str | NotGiven = NOT_GIVEN,
        ssn: str | NotGiven = NOT_GIVEN,
        telephone: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Patient:
        """
        Submit Patient

        Args:
          address_city: The patient's home city.

          address_state: The patient's home state.

          date_of_birth: The patient's date of birth, this field is required and must be of the format
              YYYY-MM-DD.

          family_name: The patient's family name (last name), this field is required.

          gender: The patient's gender, must be either Female or Female.

          given_name: The patient's given name (first name), this field is required.

          patient_id: The unique patient id in an external system.

          postal_code: The patient's home postal (zip) code.

          address_lines: The patient's home street address. This should not include the patient's city,
              state, or zip code.

          consent: The patient's consent information.

          email: The patient's email, must be a valid email address.

          particle_patient_id: The Particle Assigned Patient ID. Output only.

          ssn: The patient's social security number, must be a valid US social security number.

          telephone: The patient's telephone number.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/patients",
            body=await async_maybe_transform(
                {
                    "address_city": address_city,
                    "address_state": address_state,
                    "date_of_birth": date_of_birth,
                    "family_name": family_name,
                    "gender": gender,
                    "given_name": given_name,
                    "patient_id": patient_id,
                    "postal_code": postal_code,
                    "address_lines": address_lines,
                    "consent": consent,
                    "email": email,
                    "particle_patient_id": particle_patient_id,
                    "ssn": ssn,
                    "telephone": telephone,
                },
                patient_submit_params.PatientSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Patient,
        )


class PatientsResourceWithRawResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.retrieve = to_raw_response_wrapper(
            patients.retrieve,
        )
        self.list = to_raw_response_wrapper(
            patients.list,
        )
        self.delete = to_raw_response_wrapper(
            patients.delete,
        )
        self.search = to_raw_response_wrapper(
            patients.search,
        )
        self.submit = to_raw_response_wrapper(
            patients.submit,
        )


class AsyncPatientsResourceWithRawResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.retrieve = async_to_raw_response_wrapper(
            patients.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            patients.list,
        )
        self.delete = async_to_raw_response_wrapper(
            patients.delete,
        )
        self.search = async_to_raw_response_wrapper(
            patients.search,
        )
        self.submit = async_to_raw_response_wrapper(
            patients.submit,
        )


class PatientsResourceWithStreamingResponse:
    def __init__(self, patients: PatientsResource) -> None:
        self._patients = patients

        self.retrieve = to_streamed_response_wrapper(
            patients.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            patients.list,
        )
        self.delete = to_streamed_response_wrapper(
            patients.delete,
        )
        self.search = to_streamed_response_wrapper(
            patients.search,
        )
        self.submit = to_streamed_response_wrapper(
            patients.submit,
        )


class AsyncPatientsResourceWithStreamingResponse:
    def __init__(self, patients: AsyncPatientsResource) -> None:
        self._patients = patients

        self.retrieve = async_to_streamed_response_wrapper(
            patients.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            patients.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            patients.delete,
        )
        self.search = async_to_streamed_response_wrapper(
            patients.search,
        )
        self.submit = async_to_streamed_response_wrapper(
            patients.submit,
        )
