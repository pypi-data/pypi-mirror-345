# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["Document", "SharedDocument"]


class SharedDocument(BaseModel):
    deleted: Optional[str] = None

    retrieved: Optional[str] = None

    status: Optional[str] = None

    subscriber_project_id: Optional[str] = None

    updated: Optional[str] = None


class Document(BaseModel):
    class_code: str
    """The code specifying the high-level kind of document (e.g.

    Prescription, Discharge Summary, Report, etc.). Reference -
    https://www.hl7.org/fhir/r4/valueset-document-classcodes.html
    """

    creation_time: str
    """The timestamp representing when the document was created.

    Must be in the format of RFC3339
    """

    document_id: str
    """The unique document id in an external system"""

    format_code: str
    """The code specifying the technical format of the document.

    Reference - https://www.hl7.org/fhir/r4/valueset-formatcodes.html
    """

    mime_type: str
    """The document's mime-type"""

    patient_id: str
    """The unique patient id in an external system"""

    practice_setting_code: str
    """
    The code specifying the clinical specialty where the act that resulted in the
    document was performed (e.g., Family Practice, Laboratory, Radiology).
    Reference - https://www.hl7.org/fhir/valueset-c80-practice-codes.html
    """

    title: str
    """The document's human readable title"""

    type: str
    """The high-level document type"""

    type_code: str
    """
    The code specifying the precise type of document from the user perspective
    (e.g., LOINC code). Reference -
    https://www.hl7.org/fhir/r4/valueset-doc-typecodes.html
    """

    confidentiality_code: Optional[str] = None
    """The code specifying the security classification of the document.

    Reference -https://terminology.hl7.org/2.1.0/CodeSystem-v3-Confidentiality.html
    """

    healthcare_facility_type_code: Optional[str] = None
    """
    The code specifying the type of organizational setting of the clinical encounter
    during which the documented act occurred. Reference -
    https://www.hl7.org/fhir/valueset-c80-facilitycodes.html
    """

    service_start_time: Optional[str] = None
    """The start time of the service being documented.

    Must be in the format of RFC3339
    """

    service_stop_time: Optional[str] = None
    """The stop time of the service being documented. Must be in the format of RFC3339"""

    shared_documents: Optional[List[SharedDocument]] = None
    """Document status shared with the subscribers"""
