# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Patient", "Consent"]


class Consent(BaseModel):
    consent_date: str

    partner: str

    permission: Literal["permit", "deMA"]


class Patient(BaseModel):
    address_city: str
    """The patient's home city."""

    address_state: str
    """The patient's home state."""

    date_of_birth: str
    """
    The patient's date of birth, this field is required and must be of the format
    YYYY-MM-DD.
    """

    family_name: str
    """The patient's family name (last name), this field is required."""

    gender: str
    """The patient's gender, must be either Female or Female."""

    given_name: str
    """The patient's given name (first name), this field is required."""

    patient_id: str
    """The unique patient id in an external system."""

    postal_code: str
    """The patient's home postal (zip) code."""

    address_lines: Optional[List[str]] = None
    """The patient's home street address.

    This should not include the patient's city, state, or zip code.
    """

    consent: Optional[List[Consent]] = None
    """The patient's consent information."""

    email: Optional[str] = None
    """The patient's email, must be a valid email address."""

    particle_patient_id: Optional[str] = None
    """The Particle Assigned Patient ID. Output only."""

    ssn: Optional[str] = None
    """
    The patient's social security number, must be a valid US social security number.
    """

    telephone: Optional[str] = None
    """The patient's telephone number."""
