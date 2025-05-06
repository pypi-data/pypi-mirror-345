# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["DeltaSubmitParams"]


class DeltaSubmitParams(TypedDict, total=False):
    particle_patient_id: Required[str]
    """
    The particle patient id that corresponds to the patient that the query is meant
    to be run against.
    """

    purpose_of_use: Required[str]
    """The purpose of use for which this request is being made."""

    encounter_date: str
    """Encounter Date for the query used to get SureScripts data"""

    encounter_type: str
    """Encounter Type for the query used to get SureScripts data"""

    hints: List[str]
    """Postal codes hinting at the believed location of records."""

    specialties: List[str]
    """The list of specialty searches requested for this patient"""
