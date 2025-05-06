# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["R4ReadResourceResponse", "Address", "Name", "Identifier", "IdentifierType", "Telecom"]


class Address(BaseModel):
    city: Optional[str] = None
    """The person's home city."""

    line: Optional[List[str]] = None
    """The person's home street address.

    This should not include the person's city, state, or zip code.
    """

    postal_code: Optional[str] = FieldInfo(alias="postalCode", default=None)
    """The person's home postal code."""

    state: Optional[str] = None
    """The person's home state."""


class Name(BaseModel):
    family: str
    """The person's family (last) name."""

    given: List[str]
    """The peron's known given (first) names."""


class IdentifierType(BaseModel):
    text: Optional[str] = None
    """The type of identifier being provided, must be SSN."""


class Identifier(BaseModel):
    type: Optional[IdentifierType] = None
    """The type of identifier provided."""

    value: Optional[str] = None
    """The identifier associated with the person."""


class Telecom(BaseModel):
    system: Optional[str] = None
    """The type of contact information, must be PHONE or EMAIL."""

    value: Optional[str] = None
    """
    The person's contact information, must be a valid phone number or email address.
    """


class R4ReadResourceResponse(BaseModel):
    address: List[Address]
    """The person's home address."""

    birth_date: str = FieldInfo(alias="birthDate")
    """The person's date of birth, must be of the format YYYY-MM-DD."""

    gender: str
    """The person's gender, must be either Female or Female."""

    name: List[Name]
    """The person's name."""

    resource_type: str = FieldInfo(alias="resourceType")
    """The type of resource being provided."""

    id: Optional[str] = None
    """The person's FHIR resource ID.

    This field will be ignored if provided in create requests and an ID will be
    provided in the response.
    """

    identifier: Optional[List[Identifier]] = None
    """Information used to identify the person provided."""

    telecom: Optional[List[Telecom]] = None
    """Contact information used to identify the person provided."""
