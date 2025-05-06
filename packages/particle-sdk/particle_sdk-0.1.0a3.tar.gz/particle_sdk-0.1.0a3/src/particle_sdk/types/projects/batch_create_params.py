# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..._types import FileTypes

__all__ = ["BatchCreateParams"]


class BatchCreateParams(TypedDict, total=False):
    batch_id: str

    batch_type: str

    demographics_csv: FileTypes
    """csv file containing queries"""

    demographics_json: str
    """json string containing queries"""

    expected_finish_time: str

    query_count: int

    state: str
