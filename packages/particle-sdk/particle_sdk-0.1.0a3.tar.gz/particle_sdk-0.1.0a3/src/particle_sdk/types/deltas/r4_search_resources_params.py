# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["R4SearchResourcesParams"]


class R4SearchResourcesParams(TypedDict, total=False):
    person: Required[str]
    """Particle Patient ID"""

    _last_updated: Annotated[str, PropertyInfo(alias="_lastUpdated")]
    """Resources updated after this time will be included"""
