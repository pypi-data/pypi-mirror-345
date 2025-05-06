# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["PatientListResponse", "Patient"]


class Patient(BaseModel):
    date_of_birth: Optional[str] = None
    """
    The patient's date of birth, this field is required and must be of the format
    YYYY-MM-DD.
    """

    expected_completion_time: Optional[str] = None
    """ExpectedCompletionTime is the number of files found for a paritcular patient."""

    external_patient_id: Optional[str] = None
    """External Patient ID assigned by the customer"""

    family_name: Optional[str] = None
    """The patient's family name (last name), this field is required."""

    file_count: Optional[str] = None
    """FileCount is the number of files found for a paritcular patient."""

    gender: Optional[str] = None
    """The patient's gender, must be either Female or Female."""

    given_name: Optional[str] = None
    """The patient's given name (first name), this field is required."""

    particle_patient_id: Optional[str] = None
    """
    ParticlePatientID is the unique identifier for the patient in the Particle
    Health system.
    """

    query_date: Optional[str] = None
    """Query Date"""

    query_id: Optional[str] = None
    """Query ID"""

    query_status: Optional[str] = None
    """Query Status"""

    request_endpoint: Optional[str] = None
    """RequestEndpoint is the endpoint used to initiate the query."""


class PatientListResponse(BaseModel):
    continuation_token: Optional[str] = None

    patients: Optional[List[Patient]] = None
