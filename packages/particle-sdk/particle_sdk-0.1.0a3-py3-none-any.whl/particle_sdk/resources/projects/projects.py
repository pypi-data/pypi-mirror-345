# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .batches import (
    BatchesResource,
    AsyncBatchesResource,
    BatchesResourceWithRawResponse,
    AsyncBatchesResourceWithRawResponse,
    BatchesResourceWithStreamingResponse,
    AsyncBatchesResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["ProjectsResource", "AsyncProjectsResource"]


class ProjectsResource(SyncAPIResource):
    @cached_property
    def batches(self) -> BatchesResource:
        return BatchesResource(self._client)

    @cached_property
    def with_raw_response(self) -> ProjectsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return ProjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProjectsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return ProjectsResourceWithStreamingResponse(self)


class AsyncProjectsResource(AsyncAPIResource):
    @cached_property
    def batches(self) -> AsyncBatchesResource:
        return AsyncBatchesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncProjectsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stsak20/particle_sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncProjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProjectsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stsak20/particle_sdk#with_streaming_response
        """
        return AsyncProjectsResourceWithStreamingResponse(self)


class ProjectsResourceWithRawResponse:
    def __init__(self, projects: ProjectsResource) -> None:
        self._projects = projects

    @cached_property
    def batches(self) -> BatchesResourceWithRawResponse:
        return BatchesResourceWithRawResponse(self._projects.batches)


class AsyncProjectsResourceWithRawResponse:
    def __init__(self, projects: AsyncProjectsResource) -> None:
        self._projects = projects

    @cached_property
    def batches(self) -> AsyncBatchesResourceWithRawResponse:
        return AsyncBatchesResourceWithRawResponse(self._projects.batches)


class ProjectsResourceWithStreamingResponse:
    def __init__(self, projects: ProjectsResource) -> None:
        self._projects = projects

    @cached_property
    def batches(self) -> BatchesResourceWithStreamingResponse:
        return BatchesResourceWithStreamingResponse(self._projects.batches)


class AsyncProjectsResourceWithStreamingResponse:
    def __init__(self, projects: AsyncProjectsResource) -> None:
        self._projects = projects

    @cached_property
    def batches(self) -> AsyncBatchesResourceWithStreamingResponse:
        return AsyncBatchesResourceWithStreamingResponse(self._projects.batches)
