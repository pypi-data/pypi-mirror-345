# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .patient import (
    PatientResource,
    AsyncPatientResource,
    PatientResourceWithRawResponse,
    AsyncPatientResourceWithRawResponse,
    PatientResourceWithStreamingResponse,
    AsyncPatientResourceWithStreamingResponse,
)
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
from ....types.deltas import r4_search_resources_params
from ....types.deltas.r4.bundle import Bundle
from ....types.deltas.r4_read_resource_response import R4ReadResourceResponse

__all__ = ["R4Resource", "AsyncR4Resource"]


class R4Resource(SyncAPIResource):
    @cached_property
    def patient(self) -> PatientResource:
        return PatientResource(self._client)

    @cached_property
    def with_raw_response(self) -> R4ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return R4ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> R4ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return R4ResourceWithStreamingResponse(self)

    def read_resource(
        self,
        resource_id: str,
        *,
        resource_type: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> R4ReadResourceResponse:
        """
        Read a specified FHIR resource.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_type:
            raise ValueError(f"Expected a non-empty value for `resource_type` but received {resource_type!r}")
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return self._get(
            f"/deltas/R4/{resource_type}/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=R4ReadResourceResponse,
        )

    def search_resources(
        self,
        resource_type: str,
        *,
        person: str,
        _last_updated: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Bundle:
        """
        Search for FHIR resources.

        Args:
          person: Particle Patient ID

          _last_updated: Resources updated after this time will be included

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_type:
            raise ValueError(f"Expected a non-empty value for `resource_type` but received {resource_type!r}")
        return self._get(
            f"/deltas/R4/{resource_type}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "person": person,
                        "_last_updated": _last_updated,
                    },
                    r4_search_resources_params.R4SearchResourcesParams,
                ),
            ),
            cast_to=Bundle,
        )


class AsyncR4Resource(AsyncAPIResource):
    @cached_property
    def patient(self) -> AsyncPatientResource:
        return AsyncPatientResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncR4ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncR4ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncR4ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return AsyncR4ResourceWithStreamingResponse(self)

    async def read_resource(
        self,
        resource_id: str,
        *,
        resource_type: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> R4ReadResourceResponse:
        """
        Read a specified FHIR resource.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_type:
            raise ValueError(f"Expected a non-empty value for `resource_type` but received {resource_type!r}")
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return await self._get(
            f"/deltas/R4/{resource_type}/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=R4ReadResourceResponse,
        )

    async def search_resources(
        self,
        resource_type: str,
        *,
        person: str,
        _last_updated: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Bundle:
        """
        Search for FHIR resources.

        Args:
          person: Particle Patient ID

          _last_updated: Resources updated after this time will be included

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_type:
            raise ValueError(f"Expected a non-empty value for `resource_type` but received {resource_type!r}")
        return await self._get(
            f"/deltas/R4/{resource_type}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "person": person,
                        "_last_updated": _last_updated,
                    },
                    r4_search_resources_params.R4SearchResourcesParams,
                ),
            ),
            cast_to=Bundle,
        )


class R4ResourceWithRawResponse:
    def __init__(self, r4: R4Resource) -> None:
        self._r4 = r4

        self.read_resource = to_raw_response_wrapper(
            r4.read_resource,
        )
        self.search_resources = to_raw_response_wrapper(
            r4.search_resources,
        )

    @cached_property
    def patient(self) -> PatientResourceWithRawResponse:
        return PatientResourceWithRawResponse(self._r4.patient)


class AsyncR4ResourceWithRawResponse:
    def __init__(self, r4: AsyncR4Resource) -> None:
        self._r4 = r4

        self.read_resource = async_to_raw_response_wrapper(
            r4.read_resource,
        )
        self.search_resources = async_to_raw_response_wrapper(
            r4.search_resources,
        )

    @cached_property
    def patient(self) -> AsyncPatientResourceWithRawResponse:
        return AsyncPatientResourceWithRawResponse(self._r4.patient)


class R4ResourceWithStreamingResponse:
    def __init__(self, r4: R4Resource) -> None:
        self._r4 = r4

        self.read_resource = to_streamed_response_wrapper(
            r4.read_resource,
        )
        self.search_resources = to_streamed_response_wrapper(
            r4.search_resources,
        )

    @cached_property
    def patient(self) -> PatientResourceWithStreamingResponse:
        return PatientResourceWithStreamingResponse(self._r4.patient)


class AsyncR4ResourceWithStreamingResponse:
    def __init__(self, r4: AsyncR4Resource) -> None:
        self._r4 = r4

        self.read_resource = async_to_streamed_response_wrapper(
            r4.read_resource,
        )
        self.search_resources = async_to_streamed_response_wrapper(
            r4.search_resources,
        )

    @cached_property
    def patient(self) -> AsyncPatientResourceWithStreamingResponse:
        return AsyncPatientResourceWithStreamingResponse(self._r4.patient)
