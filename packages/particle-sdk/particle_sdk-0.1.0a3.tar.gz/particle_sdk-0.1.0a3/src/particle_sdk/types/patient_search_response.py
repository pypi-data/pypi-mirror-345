# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .patient import Patient

__all__ = ["PatientSearchResponse"]

PatientSearchResponse: TypeAlias = List[Patient]
