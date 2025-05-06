# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["Batch", "Query"]


class Query(BaseModel):
    file_count: Optional[int] = None

    patient_id: Optional[str] = None

    query_id: Optional[str] = None

    state: Optional[str] = None


class Batch(BaseModel):
    batch_id: Optional[str] = None

    batch_type: Optional[str] = None

    expected_finish_time: Optional[str] = None

    queries: Optional[List[Query]] = None

    query_count: Optional[int] = None

    state: Optional[str] = None
