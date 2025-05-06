# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["FlatCollectDatasetsParams"]


class FlatCollectDatasetsParams(TypedDict, total=False):
    _since: str
    """Resources updated after this time will be included"""
