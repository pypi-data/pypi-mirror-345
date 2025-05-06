# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["QueryCreateParams"]


class QueryCreateParams(TypedDict, total=False):
    date_of_birth: Required[str]
    """
    The patient's date of birth, this field is required and must be of the format
    YYYY-MM-DD.
    """

    family_name: Required[str]
    """The patient's family name (last name), this field is required."""

    gender: Required[str]
    """The patient's gender, must be either Female or Female."""

    given_name: Required[str]
    """The patient's given name (first name), this field is required."""

    purpose_of_use: Required[str]
    """The purpose of use for which this request is being made"""

    address_city: str
    """The patient's home city."""

    address_lines: List[str]
    """The patient's home street address.

    This should not include the patient's city, state, or zip code.
    """

    address_state: str
    """The patient's home state."""

    email: str
    """The patient's email, must be a valid email address."""

    encounter_date: str
    """Encounter Date for which this query is being made"""

    encounter_type: str
    """Encounter Type for which this query is being made"""

    hints: List[str]
    """Postal codes hinting at the believed location of records."""

    npi: str
    """
    The National Provider Identifier of the provider that this request is being made
    by.
    """

    patient_id: str
    """The unique patient id in an external system"""

    postal_code: str
    """The patient's home postal (zip) code."""

    specialties: List[str]
    """The list of specialty searches requested for this patient"""

    ssn: str
    """
    The patient's social security number, must be a valid US social security number.
    """

    telephone: str
    """The patient's telephone number."""
