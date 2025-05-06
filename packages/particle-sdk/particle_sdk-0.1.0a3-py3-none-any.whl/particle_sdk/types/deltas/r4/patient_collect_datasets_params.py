# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["PatientCollectDatasetsParams"]


class PatientCollectDatasetsParams(TypedDict, total=False):
    _count: int
    """Maximum number of results per page"""

    _since: str
    """Resources updated after this time will be included"""

    _type: str
    """Comma-delimited FHIR resource types"""

    end: str
    """End date"""

    page_token: str
    """Token for next or previous page"""

    start: str
    """Start date"""
