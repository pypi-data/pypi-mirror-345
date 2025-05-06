# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["DeltaSubmitResponse"]


class DeltaSubmitResponse(BaseModel):
    external_patient_id: str
    """The external patient id of the patient."""

    particle_patient_id: str
    """
    The particle patient id that corresponds to the patient that the query is meant
    to be run against.
    """

    purpose_of_use: str
    """The purpose of use for which this request is being made."""

    query_id: str
    """The unique ID of the query that was initiated."""

    hints: Optional[List[str]] = None
    """Postal codes hinting at the believed location of records."""

    specialties: Optional[List[str]] = None
    """The list of specialty searches requested for this patient"""
