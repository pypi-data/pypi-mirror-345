# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.deltas.r4 import patient_collect_datasets_params
from ....types.deltas.r4.bundle import Bundle

__all__ = ["PatientResource", "AsyncPatientResource"]


class PatientResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PatientResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return PatientResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PatientResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return PatientResourceWithStreamingResponse(self)

    def collect_datasets(
        self,
        particle_patient_id: str,
        *,
        _count: int | NotGiven = NOT_GIVEN,
        _since: str | NotGiven = NOT_GIVEN,
        _type: str | NotGiven = NOT_GIVEN,
        end: str | NotGiven = NOT_GIVEN,
        page_token: str | NotGiven = NOT_GIVEN,
        start: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Bundle:
        """
        Collect Deltas FHIR Datasets

        Args:
          _count: Maximum number of results per page

          _since: Resources updated after this time will be included

          _type: Comma-delimited FHIR resource types

          end: End date

          page_token: Token for next or previous page

          start: Start date

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
            f"/deltas/R4/Patient/{particle_patient_id}/$everything",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "_count": _count,
                        "_since": _since,
                        "_type": _type,
                        "end": end,
                        "page_token": page_token,
                        "start": start,
                    },
                    patient_collect_datasets_params.PatientCollectDatasetsParams,
                ),
            ),
            cast_to=Bundle,
        )


class AsyncPatientResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPatientResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPatientResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPatientResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return AsyncPatientResourceWithStreamingResponse(self)

    async def collect_datasets(
        self,
        particle_patient_id: str,
        *,
        _count: int | NotGiven = NOT_GIVEN,
        _since: str | NotGiven = NOT_GIVEN,
        _type: str | NotGiven = NOT_GIVEN,
        end: str | NotGiven = NOT_GIVEN,
        page_token: str | NotGiven = NOT_GIVEN,
        start: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Bundle:
        """
        Collect Deltas FHIR Datasets

        Args:
          _count: Maximum number of results per page

          _since: Resources updated after this time will be included

          _type: Comma-delimited FHIR resource types

          end: End date

          page_token: Token for next or previous page

          start: Start date

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
            f"/deltas/R4/Patient/{particle_patient_id}/$everything",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "_count": _count,
                        "_since": _since,
                        "_type": _type,
                        "end": end,
                        "page_token": page_token,
                        "start": start,
                    },
                    patient_collect_datasets_params.PatientCollectDatasetsParams,
                ),
            ),
            cast_to=Bundle,
        )


class PatientResourceWithRawResponse:
    def __init__(self, patient: PatientResource) -> None:
        self._patient = patient

        self.collect_datasets = to_raw_response_wrapper(
            patient.collect_datasets,
        )


class AsyncPatientResourceWithRawResponse:
    def __init__(self, patient: AsyncPatientResource) -> None:
        self._patient = patient

        self.collect_datasets = async_to_raw_response_wrapper(
            patient.collect_datasets,
        )


class PatientResourceWithStreamingResponse:
    def __init__(self, patient: PatientResource) -> None:
        self._patient = patient

        self.collect_datasets = to_streamed_response_wrapper(
            patient.collect_datasets,
        )


class AsyncPatientResourceWithStreamingResponse:
    def __init__(self, patient: AsyncPatientResource) -> None:
        self._patient = patient

        self.collect_datasets = async_to_streamed_response_wrapper(
            patient.collect_datasets,
        )
