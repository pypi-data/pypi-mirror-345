# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["PatientSubmitParams", "Consent"]


class PatientSubmitParams(TypedDict, total=False):
    address_city: Required[str]
    """The patient's home city."""

    address_state: Required[str]
    """The patient's home state."""

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

    patient_id: Required[str]
    """The unique patient id in an external system."""

    postal_code: Required[str]
    """The patient's home postal (zip) code."""

    address_lines: List[str]
    """The patient's home street address.

    This should not include the patient's city, state, or zip code.
    """

    consent: Iterable[Consent]
    """The patient's consent information."""

    email: str
    """The patient's email, must be a valid email address."""

    particle_patient_id: str
    """The Particle Assigned Patient ID. Output only."""

    ssn: str
    """
    The patient's social security number, must be a valid US social security number.
    """

    telephone: str
    """The patient's telephone number."""


class Consent(TypedDict, total=False):
    consent_date: Required[str]

    partner: Required[str]

    permission: Required[Literal["permit", "deMA"]]
