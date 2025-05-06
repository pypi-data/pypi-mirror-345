# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Union, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import auth, files, queries, patients, documents
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.deltas import deltas
from .resources.projects import projects

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "ParticleSDK",
    "AsyncParticleSDK",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "sandbox": "https://sandbox.particlehealth.com",
    "production": "https://api.particlehealth.com",
}


class ParticleSDK(SyncAPIClient):
    documents: documents.DocumentsResource
    files: files.FilesResource
    patients: patients.PatientsResource
    projects: projects.ProjectsResource
    queries: queries.QueriesResource
    auth: auth.AuthResource
    deltas: deltas.DeltasResource
    with_raw_response: ParticleSDKWithRawResponse
    with_streaming_response: ParticleSDKWithStreamedResponse

    # client options
    api_key: str | None

    _environment: Literal["sandbox", "production"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["sandbox", "production"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous ParticleSDK client instance.

        This automatically infers the `api_key` argument from the `PARTICLE_SDK_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("PARTICLE_SDK_API_KEY")
        self.api_key = api_key

        self._environment = environment

        base_url_env = os.environ.get("PARTICLE_SDK_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `PARTICLE_SDK_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "sandbox"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.documents = documents.DocumentsResource(self)
        self.files = files.FilesResource(self)
        self.patients = patients.PatientsResource(self)
        self.projects = projects.ProjectsResource(self)
        self.queries = queries.QueriesResource(self)
        self.auth = auth.AuthResource(self)
        self.deltas = deltas.DeltasResource(self)
        self.with_raw_response = ParticleSDKWithRawResponse(self)
        self.with_streaming_response = ParticleSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if api_key is None:
            return {}
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self.api_key and headers.get("Authorization"):
            return
        if isinstance(custom_headers.get("Authorization"), Omit):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected the api_key to be set. Or for the `Authorization` headers to be explicitly omitted"'
        )

    def copy(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["sandbox", "production"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncParticleSDK(AsyncAPIClient):
    documents: documents.AsyncDocumentsResource
    files: files.AsyncFilesResource
    patients: patients.AsyncPatientsResource
    projects: projects.AsyncProjectsResource
    queries: queries.AsyncQueriesResource
    auth: auth.AsyncAuthResource
    deltas: deltas.AsyncDeltasResource
    with_raw_response: AsyncParticleSDKWithRawResponse
    with_streaming_response: AsyncParticleSDKWithStreamedResponse

    # client options
    api_key: str | None

    _environment: Literal["sandbox", "production"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["sandbox", "production"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncParticleSDK client instance.

        This automatically infers the `api_key` argument from the `PARTICLE_SDK_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("PARTICLE_SDK_API_KEY")
        self.api_key = api_key

        self._environment = environment

        base_url_env = os.environ.get("PARTICLE_SDK_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `PARTICLE_SDK_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "sandbox"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.documents = documents.AsyncDocumentsResource(self)
        self.files = files.AsyncFilesResource(self)
        self.patients = patients.AsyncPatientsResource(self)
        self.projects = projects.AsyncProjectsResource(self)
        self.queries = queries.AsyncQueriesResource(self)
        self.auth = auth.AsyncAuthResource(self)
        self.deltas = deltas.AsyncDeltasResource(self)
        self.with_raw_response = AsyncParticleSDKWithRawResponse(self)
        self.with_streaming_response = AsyncParticleSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if api_key is None:
            return {}
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self.api_key and headers.get("Authorization"):
            return
        if isinstance(custom_headers.get("Authorization"), Omit):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected the api_key to be set. Or for the `Authorization` headers to be explicitly omitted"'
        )

    def copy(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["sandbox", "production"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class ParticleSDKWithRawResponse:
    def __init__(self, client: ParticleSDK) -> None:
        self.documents = documents.DocumentsResourceWithRawResponse(client.documents)
        self.files = files.FilesResourceWithRawResponse(client.files)
        self.patients = patients.PatientsResourceWithRawResponse(client.patients)
        self.projects = projects.ProjectsResourceWithRawResponse(client.projects)
        self.queries = queries.QueriesResourceWithRawResponse(client.queries)
        self.auth = auth.AuthResourceWithRawResponse(client.auth)
        self.deltas = deltas.DeltasResourceWithRawResponse(client.deltas)


class AsyncParticleSDKWithRawResponse:
    def __init__(self, client: AsyncParticleSDK) -> None:
        self.documents = documents.AsyncDocumentsResourceWithRawResponse(client.documents)
        self.files = files.AsyncFilesResourceWithRawResponse(client.files)
        self.patients = patients.AsyncPatientsResourceWithRawResponse(client.patients)
        self.projects = projects.AsyncProjectsResourceWithRawResponse(client.projects)
        self.queries = queries.AsyncQueriesResourceWithRawResponse(client.queries)
        self.auth = auth.AsyncAuthResourceWithRawResponse(client.auth)
        self.deltas = deltas.AsyncDeltasResourceWithRawResponse(client.deltas)


class ParticleSDKWithStreamedResponse:
    def __init__(self, client: ParticleSDK) -> None:
        self.documents = documents.DocumentsResourceWithStreamingResponse(client.documents)
        self.files = files.FilesResourceWithStreamingResponse(client.files)
        self.patients = patients.PatientsResourceWithStreamingResponse(client.patients)
        self.projects = projects.ProjectsResourceWithStreamingResponse(client.projects)
        self.queries = queries.QueriesResourceWithStreamingResponse(client.queries)
        self.auth = auth.AuthResourceWithStreamingResponse(client.auth)
        self.deltas = deltas.DeltasResourceWithStreamingResponse(client.deltas)


class AsyncParticleSDKWithStreamedResponse:
    def __init__(self, client: AsyncParticleSDK) -> None:
        self.documents = documents.AsyncDocumentsResourceWithStreamingResponse(client.documents)
        self.files = files.AsyncFilesResourceWithStreamingResponse(client.files)
        self.patients = patients.AsyncPatientsResourceWithStreamingResponse(client.patients)
        self.projects = projects.AsyncProjectsResourceWithStreamingResponse(client.projects)
        self.queries = queries.AsyncQueriesResourceWithStreamingResponse(client.queries)
        self.auth = auth.AsyncAuthResourceWithStreamingResponse(client.auth)
        self.deltas = deltas.AsyncDeltasResourceWithStreamingResponse(client.deltas)


Client = ParticleSDK

AsyncClient = AsyncParticleSDK
