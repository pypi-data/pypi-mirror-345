# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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
from ..._base_client import make_request_options
from ...types.deltas import flat_collect_datasets_params
from ...types.deltas.datasets import Datasets

__all__ = ["FlatResource", "AsyncFlatResource"]


class FlatResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FlatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return FlatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FlatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return FlatResourceWithStreamingResponse(self)

    def collect_datasets(
        self,
        particle_patient_id: str,
        *,
        _since: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Datasets:
        """
        Collect Deltas Flat Datasets

        Args:
          _since: Resources updated after this time will be included

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
            f"/deltas/flat/{particle_patient_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"_since": _since}, flat_collect_datasets_params.FlatCollectDatasetsParams),
            ),
            cast_to=Datasets,
        )

    def get_resource(
        self,
        resource_id: str,
        *,
        particle_patient_id: str,
        resource_type: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Datasets:
        """
        Get Deltas Flat Resource

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
        if not resource_type:
            raise ValueError(f"Expected a non-empty value for `resource_type` but received {resource_type!r}")
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return self._get(
            f"/deltas/flat/{particle_patient_id}/{resource_type}/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Datasets,
        )


class AsyncFlatResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFlatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncFlatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFlatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return AsyncFlatResourceWithStreamingResponse(self)

    async def collect_datasets(
        self,
        particle_patient_id: str,
        *,
        _since: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Datasets:
        """
        Collect Deltas Flat Datasets

        Args:
          _since: Resources updated after this time will be included

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
            f"/deltas/flat/{particle_patient_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"_since": _since}, flat_collect_datasets_params.FlatCollectDatasetsParams
                ),
            ),
            cast_to=Datasets,
        )

    async def get_resource(
        self,
        resource_id: str,
        *,
        particle_patient_id: str,
        resource_type: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Datasets:
        """
        Get Deltas Flat Resource

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
        if not resource_type:
            raise ValueError(f"Expected a non-empty value for `resource_type` but received {resource_type!r}")
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return await self._get(
            f"/deltas/flat/{particle_patient_id}/{resource_type}/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Datasets,
        )


class FlatResourceWithRawResponse:
    def __init__(self, flat: FlatResource) -> None:
        self._flat = flat

        self.collect_datasets = to_raw_response_wrapper(
            flat.collect_datasets,
        )
        self.get_resource = to_raw_response_wrapper(
            flat.get_resource,
        )


class AsyncFlatResourceWithRawResponse:
    def __init__(self, flat: AsyncFlatResource) -> None:
        self._flat = flat

        self.collect_datasets = async_to_raw_response_wrapper(
            flat.collect_datasets,
        )
        self.get_resource = async_to_raw_response_wrapper(
            flat.get_resource,
        )


class FlatResourceWithStreamingResponse:
    def __init__(self, flat: FlatResource) -> None:
        self._flat = flat

        self.collect_datasets = to_streamed_response_wrapper(
            flat.collect_datasets,
        )
        self.get_resource = to_streamed_response_wrapper(
            flat.get_resource,
        )


class AsyncFlatResourceWithStreamingResponse:
    def __init__(self, flat: AsyncFlatResource) -> None:
        self._flat = flat

        self.collect_datasets = async_to_streamed_response_wrapper(
            flat.collect_datasets,
        )
        self.get_resource = async_to_streamed_response_wrapper(
            flat.get_resource,
        )
