# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["Bundle", "Entry", "EntrySearch", "Link"]


class EntrySearch(BaseModel):
    mode: Optional[str] = None


class Entry(BaseModel):
    full_url: Optional[str] = FieldInfo(alias="fullUrl", default=None)
    """The URL at which the resource represented by this entry can be accessed."""

    resource: Optional[Dict[str, object]] = None
    """The resource represented by this bundle entry."""

    search: Optional[EntrySearch] = None
    """Metadata associated with a searchset bundle."""


class Link(BaseModel):
    relation: Optional[str] = None
    """The type of relation between the bundle and the link."""

    url: Optional[str] = None
    """The URL at which the link can be accessed."""


class Bundle(BaseModel):
    entry: Optional[List[Entry]] = None
    """The set of search results."""

    link: Optional[List[Link]] = None
    """Links related to this bundle."""

    resource_type: Optional[str] = FieldInfo(alias="resourceType", default=None)
    """The type of the FHIR resource."""

    total: Optional[int] = None
    """The total number of resources in the bundle."""

    type: Optional[str] = None
    """The type of bundle."""
