# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

from ..types import query_create_params
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
from ..types.query import Query
from .._base_client import make_request_options
from ..types.query_list_response import QueryListResponse

__all__ = ["QueriesResource", "AsyncQueriesResource"]


class QueriesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> QueriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return QueriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> QueriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return QueriesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        date_of_birth: str,
        family_name: str,
        gender: str,
        given_name: str,
        purpose_of_use: str,
        address_city: str | NotGiven = NOT_GIVEN,
        address_lines: List[str] | NotGiven = NOT_GIVEN,
        address_state: str | NotGiven = NOT_GIVEN,
        email: str | NotGiven = NOT_GIVEN,
        encounter_date: str | NotGiven = NOT_GIVEN,
        encounter_type: str | NotGiven = NOT_GIVEN,
        hints: List[str] | NotGiven = NOT_GIVEN,
        npi: str | NotGiven = NOT_GIVEN,
        patient_id: str | NotGiven = NOT_GIVEN,
        postal_code: str | NotGiven = NOT_GIVEN,
        specialties: List[str] | NotGiven = NOT_GIVEN,
        ssn: str | NotGiven = NOT_GIVEN,
        telephone: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Query:
        """
        Create Query

        Args:
          date_of_birth: The patient's date of birth, this field is required and must be of the format
              YYYY-MM-DD.

          family_name: The patient's family name (last name), this field is required.

          gender: The patient's gender, must be either Female or Female.

          given_name: The patient's given name (first name), this field is required.

          purpose_of_use: The purpose of use for which this request is being made

          address_city: The patient's home city.

          address_lines: The patient's home street address. This should not include the patient's city,
              state, or zip code.

          address_state: The patient's home state.

          email: The patient's email, must be a valid email address.

          encounter_date: Encounter Date for which this query is being made

          encounter_type: Encounter Type for which this query is being made

          hints: Postal codes hinting at the believed location of records.

          npi: The National Provider Identifier of the provider that this request is being made
              by.

          patient_id: The unique patient id in an external system

          postal_code: The patient's home postal (zip) code.

          specialties: The list of specialty searches requested for this patient

          ssn: The patient's social security number, must be a valid US social security number.

          telephone: The patient's telephone number.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/queries",
            body=maybe_transform(
                {
                    "date_of_birth": date_of_birth,
                    "family_name": family_name,
                    "gender": gender,
                    "given_name": given_name,
                    "purpose_of_use": purpose_of_use,
                    "address_city": address_city,
                    "address_lines": address_lines,
                    "address_state": address_state,
                    "email": email,
                    "encounter_date": encounter_date,
                    "encounter_type": encounter_type,
                    "hints": hints,
                    "npi": npi,
                    "patient_id": patient_id,
                    "postal_code": postal_code,
                    "specialties": specialties,
                    "ssn": ssn,
                    "telephone": telephone,
                },
                query_create_params.QueryCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Query,
        )

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
    ) -> Query:
        """
        Get Query

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/v1/queries/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Query,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QueryListResponse:
        """List Queries"""
        return self._get(
            "/api/v1/queries/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QueryListResponse,
        )


class AsyncQueriesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncQueriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncQueriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncQueriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return AsyncQueriesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        date_of_birth: str,
        family_name: str,
        gender: str,
        given_name: str,
        purpose_of_use: str,
        address_city: str | NotGiven = NOT_GIVEN,
        address_lines: List[str] | NotGiven = NOT_GIVEN,
        address_state: str | NotGiven = NOT_GIVEN,
        email: str | NotGiven = NOT_GIVEN,
        encounter_date: str | NotGiven = NOT_GIVEN,
        encounter_type: str | NotGiven = NOT_GIVEN,
        hints: List[str] | NotGiven = NOT_GIVEN,
        npi: str | NotGiven = NOT_GIVEN,
        patient_id: str | NotGiven = NOT_GIVEN,
        postal_code: str | NotGiven = NOT_GIVEN,
        specialties: List[str] | NotGiven = NOT_GIVEN,
        ssn: str | NotGiven = NOT_GIVEN,
        telephone: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Query:
        """
        Create Query

        Args:
          date_of_birth: The patient's date of birth, this field is required and must be of the format
              YYYY-MM-DD.

          family_name: The patient's family name (last name), this field is required.

          gender: The patient's gender, must be either Female or Female.

          given_name: The patient's given name (first name), this field is required.

          purpose_of_use: The purpose of use for which this request is being made

          address_city: The patient's home city.

          address_lines: The patient's home street address. This should not include the patient's city,
              state, or zip code.

          address_state: The patient's home state.

          email: The patient's email, must be a valid email address.

          encounter_date: Encounter Date for which this query is being made

          encounter_type: Encounter Type for which this query is being made

          hints: Postal codes hinting at the believed location of records.

          npi: The National Provider Identifier of the provider that this request is being made
              by.

          patient_id: The unique patient id in an external system

          postal_code: The patient's home postal (zip) code.

          specialties: The list of specialty searches requested for this patient

          ssn: The patient's social security number, must be a valid US social security number.

          telephone: The patient's telephone number.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/queries",
            body=await async_maybe_transform(
                {
                    "date_of_birth": date_of_birth,
                    "family_name": family_name,
                    "gender": gender,
                    "given_name": given_name,
                    "purpose_of_use": purpose_of_use,
                    "address_city": address_city,
                    "address_lines": address_lines,
                    "address_state": address_state,
                    "email": email,
                    "encounter_date": encounter_date,
                    "encounter_type": encounter_type,
                    "hints": hints,
                    "npi": npi,
                    "patient_id": patient_id,
                    "postal_code": postal_code,
                    "specialties": specialties,
                    "ssn": ssn,
                    "telephone": telephone,
                },
                query_create_params.QueryCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Query,
        )

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
    ) -> Query:
        """
        Get Query

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/v1/queries/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Query,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QueryListResponse:
        """List Queries"""
        return await self._get(
            "/api/v1/queries/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QueryListResponse,
        )


class QueriesResourceWithRawResponse:
    def __init__(self, queries: QueriesResource) -> None:
        self._queries = queries

        self.create = to_raw_response_wrapper(
            queries.create,
        )
        self.retrieve = to_raw_response_wrapper(
            queries.retrieve,
        )
        self.list = to_raw_response_wrapper(
            queries.list,
        )


class AsyncQueriesResourceWithRawResponse:
    def __init__(self, queries: AsyncQueriesResource) -> None:
        self._queries = queries

        self.create = async_to_raw_response_wrapper(
            queries.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            queries.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            queries.list,
        )


class QueriesResourceWithStreamingResponse:
    def __init__(self, queries: QueriesResource) -> None:
        self._queries = queries

        self.create = to_streamed_response_wrapper(
            queries.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            queries.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            queries.list,
        )


class AsyncQueriesResourceWithStreamingResponse:
    def __init__(self, queries: AsyncQueriesResource) -> None:
        self._queries = queries

        self.create = async_to_streamed_response_wrapper(
            queries.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            queries.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            queries.list,
        )
