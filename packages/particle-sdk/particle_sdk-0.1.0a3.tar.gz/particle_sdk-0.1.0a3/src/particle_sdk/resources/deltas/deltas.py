# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

from .flat import (
    FlatResource,
    AsyncFlatResource,
    FlatResourceWithRawResponse,
    AsyncFlatResourceWithRawResponse,
    FlatResourceWithStreamingResponse,
    AsyncFlatResourceWithStreamingResponse,
)
from .r4.r4 import (
    R4Resource,
    AsyncR4Resource,
    R4ResourceWithRawResponse,
    AsyncR4ResourceWithRawResponse,
    R4ResourceWithStreamingResponse,
    AsyncR4ResourceWithStreamingResponse,
)
from ...types import delta_submit_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.query import Query
from ..._base_client import make_request_options
from ...types.delta_submit_response import DeltaSubmitResponse

__all__ = ["DeltasResource", "AsyncDeltasResource"]


class DeltasResource(SyncAPIResource):
    @cached_property
    def r4(self) -> R4Resource:
        return R4Resource(self._client)

    @cached_property
    def flat(self) -> FlatResource:
        return FlatResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeltasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return DeltasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeltasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return DeltasResourceWithStreamingResponse(self)

    def retrieve_status(
        self,
        particle_patient_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Query:
        """
        Get Deltas Query Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not particle_patient_id:
            raise ValueError(
                f"Expected a non-empty value for `particle_patient_id` but received {particle_patient_id!r}"
            )
        return self._get(
            f"/deltas/{particle_patient_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Query,
        )

    def submit(
        self,
        *,
        particle_patient_id: str,
        purpose_of_use: str,
        encounter_date: str | NotGiven = NOT_GIVEN,
        encounter_type: str | NotGiven = NOT_GIVEN,
        hints: List[str] | NotGiven = NOT_GIVEN,
        specialties: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeltaSubmitResponse:
        """
        Submit Deltas Query

        Args:
          particle_patient_id: The particle patient id that corresponds to the patient that the query is meant
              to be run against.

          purpose_of_use: The purpose of use for which this request is being made.

          encounter_date: Encounter Date for the query used to get SureScripts data

          encounter_type: Encounter Type for the query used to get SureScripts data

          hints: Postal codes hinting at the believed location of records.

          specialties: The list of specialty searches requested for this patient

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/deltas",
            body=maybe_transform(
                {
                    "particle_patient_id": particle_patient_id,
                    "purpose_of_use": purpose_of_use,
                    "encounter_date": encounter_date,
                    "encounter_type": encounter_type,
                    "hints": hints,
                    "specialties": specialties,
                },
                delta_submit_params.DeltaSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeltaSubmitResponse,
        )


class AsyncDeltasResource(AsyncAPIResource):
    @cached_property
    def r4(self) -> AsyncR4Resource:
        return AsyncR4Resource(self._client)

    @cached_property
    def flat(self) -> AsyncFlatResource:
        return AsyncFlatResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeltasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDeltasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeltasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return AsyncDeltasResourceWithStreamingResponse(self)

    async def retrieve_status(
        self,
        particle_patient_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Query:
        """
        Get Deltas Query Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not particle_patient_id:
            raise ValueError(
                f"Expected a non-empty value for `particle_patient_id` but received {particle_patient_id!r}"
            )
        return await self._get(
            f"/deltas/{particle_patient_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Query,
        )

    async def submit(
        self,
        *,
        particle_patient_id: str,
        purpose_of_use: str,
        encounter_date: str | NotGiven = NOT_GIVEN,
        encounter_type: str | NotGiven = NOT_GIVEN,
        hints: List[str] | NotGiven = NOT_GIVEN,
        specialties: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeltaSubmitResponse:
        """
        Submit Deltas Query

        Args:
          particle_patient_id: The particle patient id that corresponds to the patient that the query is meant
              to be run against.

          purpose_of_use: The purpose of use for which this request is being made.

          encounter_date: Encounter Date for the query used to get SureScripts data

          encounter_type: Encounter Type for the query used to get SureScripts data

          hints: Postal codes hinting at the believed location of records.

          specialties: The list of specialty searches requested for this patient

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/deltas",
            body=await async_maybe_transform(
                {
                    "particle_patient_id": particle_patient_id,
                    "purpose_of_use": purpose_of_use,
                    "encounter_date": encounter_date,
                    "encounter_type": encounter_type,
                    "hints": hints,
                    "specialties": specialties,
                },
                delta_submit_params.DeltaSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeltaSubmitResponse,
        )


class DeltasResourceWithRawResponse:
    def __init__(self, deltas: DeltasResource) -> None:
        self._deltas = deltas

        self.retrieve_status = to_raw_response_wrapper(
            deltas.retrieve_status,
        )
        self.submit = to_raw_response_wrapper(
            deltas.submit,
        )

    @cached_property
    def r4(self) -> R4ResourceWithRawResponse:
        return R4ResourceWithRawResponse(self._deltas.r4)

    @cached_property
    def flat(self) -> FlatResourceWithRawResponse:
        return FlatResourceWithRawResponse(self._deltas.flat)


class AsyncDeltasResourceWithRawResponse:
    def __init__(self, deltas: AsyncDeltasResource) -> None:
        self._deltas = deltas

        self.retrieve_status = async_to_raw_response_wrapper(
            deltas.retrieve_status,
        )
        self.submit = async_to_raw_response_wrapper(
            deltas.submit,
        )

    @cached_property
    def r4(self) -> AsyncR4ResourceWithRawResponse:
        return AsyncR4ResourceWithRawResponse(self._deltas.r4)

    @cached_property
    def flat(self) -> AsyncFlatResourceWithRawResponse:
        return AsyncFlatResourceWithRawResponse(self._deltas.flat)


class DeltasResourceWithStreamingResponse:
    def __init__(self, deltas: DeltasResource) -> None:
        self._deltas = deltas

        self.retrieve_status = to_streamed_response_wrapper(
            deltas.retrieve_status,
        )
        self.submit = to_streamed_response_wrapper(
            deltas.submit,
        )

    @cached_property
    def r4(self) -> R4ResourceWithStreamingResponse:
        return R4ResourceWithStreamingResponse(self._deltas.r4)

    @cached_property
    def flat(self) -> FlatResourceWithStreamingResponse:
        return FlatResourceWithStreamingResponse(self._deltas.flat)


class AsyncDeltasResourceWithStreamingResponse:
    def __init__(self, deltas: AsyncDeltasResource) -> None:
        self._deltas = deltas

        self.retrieve_status = async_to_streamed_response_wrapper(
            deltas.retrieve_status,
        )
        self.submit = async_to_streamed_response_wrapper(
            deltas.submit,
        )

    @cached_property
    def r4(self) -> AsyncR4ResourceWithStreamingResponse:
        return AsyncR4ResourceWithStreamingResponse(self._deltas.r4)

    @cached_property
    def flat(self) -> AsyncFlatResourceWithStreamingResponse:
        return AsyncFlatResourceWithStreamingResponse(self._deltas.flat)
