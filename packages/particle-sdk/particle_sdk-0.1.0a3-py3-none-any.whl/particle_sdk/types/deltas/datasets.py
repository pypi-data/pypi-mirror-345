# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..patient import Patient
from ..._models import BaseModel

__all__ = [
    "Datasets",
    "Allergy",
    "Composition",
    "Coverage",
    "DocumentReference",
    "Encounter",
    "FamilyMemberHistory",
    "Immunization",
    "Lab",
    "Location",
    "Medication",
    "MedRec",
    "Organization",
    "Practitioner",
    "Problem",
    "Procedure",
    "Provenance",
    "RelatedPerson",
    "SocialHistory",
    "VitalSign",
]


class Allergy(BaseModel):
    allergy_code: Optional[str] = None

    allergy_code_system: Optional[str] = None

    allergy_id: Optional[str] = None

    allergy_name: Optional[str] = None

    allergy_onset_end: Optional[str] = None

    allergy_onset_start: Optional[str] = None

    patient_id: Optional[str] = None

    practitioner_role_id: Optional[str] = None

    reaction_manifestation: Optional[str] = None

    reaction_manifestation_code: Optional[str] = None

    reaction_manifestation_code_system: Optional[str] = None

    recorded_date: Optional[str] = None


class Composition(BaseModel):
    composition_all_allergy_ids: Optional[str] = None

    composition_all_document_reference_ids: Optional[str] = None

    composition_all_encounter_ids: Optional[str] = None

    composition_all_immunization_ids: Optional[str] = None

    composition_all_lab_ids: Optional[str] = None

    composition_all_location_ids: Optional[str] = None

    composition_all_medication_statements_ids: Optional[str] = None

    composition_all_practitioner_role_ids: Optional[str] = None

    composition_all_problem_ids: Optional[str] = None

    composition_all_procedure_ids: Optional[str] = None

    composition_all_social_history_ids: Optional[str] = None

    composition_all_vital_sign_ids: Optional[str] = None

    composition_custodian_organization_id: Optional[str] = None

    composition_date: Optional[str] = None

    composition_encounter_id: Optional[str] = None

    composition_event: Optional[str] = None

    composition_event_code: Optional[str] = None

    composition_event_code_system: Optional[str] = None

    composition_event_encounter_reference_id: Optional[str] = None

    composition_event_period_end: Optional[str] = None

    composition_event_period_start: Optional[str] = None

    composition_id: Optional[str] = None

    composition_original_file_name: Optional[str] = None

    composition_title: Optional[str] = None

    composition_type: Optional[str] = None

    composition_type_code: Optional[str] = None

    composition_type_code_system: Optional[str] = None

    patient_id: Optional[str] = None


class Coverage(BaseModel):
    beneficiary_reference: Optional[str] = None

    class_type_code: Optional[str] = None

    class_type_code_system: Optional[str] = None

    class_type_display: Optional[str] = None

    class_value: Optional[str] = None

    coverage_id: Optional[str] = None

    identifier_system: Optional[str] = None

    identifier_value: Optional[str] = None

    order: Optional[str] = None

    patient_id: Optional[str] = None

    payor_reference: Optional[str] = None

    relationship_code: Optional[str] = None

    relationship_code_system: Optional[str] = None

    relationship_display: Optional[str] = None

    status: Optional[str] = None

    subscriber_id: Optional[str] = None

    subscriber_reference: Optional[str] = None

    type_code: Optional[str] = None

    type_code_system: Optional[str] = None

    type_display: Optional[str] = None


class DocumentReference(BaseModel):
    document_reference_content_data: Optional[str] = None

    document_reference_content_type: Optional[str] = None

    document_reference_id: Optional[str] = None

    document_reference_type: Optional[str] = None

    document_reference_type_coding: Optional[str] = None

    document_reference_type_coding_system: Optional[str] = None

    encounter_reference_id: Optional[str] = None

    patient_id: Optional[str] = None

    practitioner_role_reference_id: Optional[str] = None


class Encounter(BaseModel):
    condition_id_references: Optional[str] = None

    encounter_end_time: Optional[str] = None

    encounter_id: Optional[str] = None

    encounter_start_time: Optional[str] = None

    encounter_text: Optional[str] = None

    encounter_type_code: Optional[str] = None

    encounter_type_code_system: Optional[str] = None

    encounter_type_name: Optional[str] = None

    hospitalization_discharge_disposition: Optional[str] = None

    location_id_references: Optional[str] = None

    patient_id: Optional[str] = None

    practitioner_role_id_references: Optional[str] = None


class FamilyMemberHistory(BaseModel):
    family_member_history_condition_code: Optional[str] = None

    family_member_history_condition_code_system: Optional[str] = None

    family_member_history_condition_display: Optional[str] = None

    family_member_history_id: Optional[str] = None

    family_member_history_relationship_code: Optional[str] = None

    family_member_history_relationship_code_system: Optional[str] = None

    family_member_history_relationship_display: Optional[str] = None

    family_member_history_sex_code: Optional[str] = None

    family_member_history_sex_code_system: Optional[str] = None

    family_member_history_sex_display: Optional[str] = None

    patient_id: Optional[str] = None


class Immunization(BaseModel):
    immunization_code: Optional[str] = None

    immunization_code_system: Optional[str] = None

    immunization_dosage_unit: Optional[str] = None

    immunization_dosage_value: Optional[float] = None

    immunization_id: Optional[str] = None

    immunization_lot_number: Optional[str] = None

    immunization_manufacturer_name: Optional[str] = None

    immunization_name: Optional[str] = None

    immunization_occurrence_time: Optional[str] = None

    immunization_route: Optional[str] = None

    immunization_route_code: Optional[str] = None

    immunization_route_code_system: Optional[str] = None

    immunization_site: Optional[str] = None

    immunization_site_code: Optional[str] = None

    immunization_site_code_system: Optional[str] = None

    immunization_status: Optional[str] = None

    patient_id: Optional[str] = None

    performer_practitioner_role_reference_id: Optional[str] = None


class Lab(BaseModel):
    diagnostic_interpreter_practitioner_role_reference_id: Optional[str] = None

    diagnostic_performer_practitioner_role_reference_id: Optional[str] = None

    diagnostic_report_id: Optional[str] = None

    diagnostic_report_name: Optional[str] = None

    lab_code: Optional[str] = None

    lab_code_system: Optional[str] = None

    lab_interpretation: Optional[str] = None

    lab_name: Optional[str] = None

    lab_observation_id: Optional[str] = None

    lab_text: Optional[str] = None

    lab_timestamp: Optional[str] = None

    lab_unit: Optional[str] = None

    lab_unit_quantity: Optional[str] = None

    lab_value: Optional[str] = None

    lab_value_boolean: Optional[str] = None

    lab_value_code: Optional[str] = None

    lab_value_code_system: Optional[str] = None

    lab_value_quantity: Optional[str] = None

    lab_value_string: Optional[str] = None

    observation_category: Optional[str] = None

    patient_id: Optional[str] = None


class Location(BaseModel):
    location_address: Optional[str] = None

    location_address_use: Optional[str] = None

    location_city: Optional[str] = None

    location_id: Optional[str] = None

    location_name: Optional[str] = None

    location_postal_code: Optional[str] = None

    location_state: Optional[str] = None

    location_type: Optional[str] = None

    location_type_code: Optional[str] = None

    location_type_code_system: Optional[str] = None

    patient_id: Optional[str] = None


class Medication(BaseModel):
    medication_code: Optional[str] = None

    medication_code_system: Optional[str] = None

    medication_id: Optional[str] = None

    medication_name: Optional[str] = None

    medication_reference: Optional[str] = None

    medication_resource_type: Optional[str] = None

    medication_statement_dose_route: Optional[str] = None

    medication_statement_dose_unit: Optional[str] = None

    medication_statement_dose_value: Optional[float] = None

    medication_statement_end_time: Optional[str] = None

    medication_statement_id: Optional[str] = None

    medication_statement_patient_instructions: Optional[str] = None

    medication_statement_start_time: Optional[str] = None

    medication_statement_status: Optional[str] = None

    medication_statement_text: Optional[str] = None

    patient_id: Optional[str] = None

    practitioner_role_id: Optional[str] = None


class MedRec(BaseModel):
    brand_name: Optional[str] = None

    class_1_code: Optional[str] = None

    class_1_name: Optional[str] = None

    class_2_code: Optional[str] = None

    class_2_name: Optional[str] = None

    class_3_code: Optional[str] = None

    class_3_name: Optional[str] = None

    class_4_code: Optional[str] = None

    class_4_name: Optional[str] = None

    drug_name: Optional[str] = None

    generic_name: Optional[str] = None

    med_rec_id: Optional[str] = None

    medication_id: Optional[str] = None

    medication_reference: Optional[str] = None

    medication_resource_type: Optional[str] = None

    medication_statement_id: Optional[str] = None

    normalized_package_ndc: Optional[str] = None

    package_ndc: Optional[str] = None

    patient_id: Optional[str] = None

    product_ndc: Optional[str] = None

    rxcui: Optional[str] = None


class Organization(BaseModel):
    organization_address_city: Optional[str] = None

    organization_address_country: Optional[str] = None

    organization_address_lines: Optional[str] = None

    organization_address_postal_code: Optional[str] = None

    organization_address_state: Optional[str] = None

    organization_address_use: Optional[str] = None

    organization_id: Optional[str] = None

    organization_name: Optional[str] = None

    organization_telecom_system: Optional[str] = None

    organization_telecom_use: Optional[str] = None

    organization_telecom_value: Optional[str] = None

    patient_id: Optional[str] = None


class Practitioner(BaseModel):
    patient_id: Optional[str] = None

    practitioner_address_city: Optional[str] = None

    practitioner_address_state: Optional[str] = None

    practitioner_address_street: Optional[str] = None

    practitioner_address_use: Optional[str] = None

    practitioner_family_name: Optional[str] = None

    practitioner_given_name: Optional[str] = None

    practitioner_id: Optional[str] = None

    practitioner_identifier_system: Optional[str] = None

    practitioner_identifier_value: Optional[str] = None

    practitioner_name_suffix: Optional[str] = None

    practitioner_role: Optional[str] = None

    practitioner_role_code: Optional[str] = None

    practitioner_role_code_system: Optional[str] = None

    practitioner_role_id: Optional[str] = None

    practitioner_role_specialty: Optional[str] = None

    practitioner_role_specialty_code: Optional[str] = None

    practitioner_role_specialty_code_system: Optional[str] = None

    practitioner_telecom_system: Optional[str] = None

    practitioner_telecom_value: Optional[str] = None


class Problem(BaseModel):
    condition_category_code: Optional[str] = None

    condition_category_code_name: Optional[str] = None

    condition_category_code_system: Optional[str] = None

    condition_clinical_status: Optional[str] = None

    condition_code: Optional[str] = None

    condition_code_system: Optional[str] = None

    condition_id: Optional[str] = None

    condition_name: Optional[str] = None

    condition_onset_date: Optional[str] = None

    condition_recorded_date: Optional[str] = None

    condition_text: Optional[str] = None

    encounter_id: Optional[str] = None

    patient_id: Optional[str] = None


class Procedure(BaseModel):
    asserter_practitioner_role_reference_id: Optional[str] = None

    encounter_reference_id: Optional[str] = None

    patient_id: Optional[str] = None

    performer_practitioner_role_reference_id: Optional[str] = None

    procedure_code: Optional[str] = None

    procedure_code_system: Optional[str] = None

    procedure_date_time: Optional[str] = None

    procedure_id: Optional[str] = None

    procedure_name: Optional[str] = None

    procedure_reason: Optional[str] = None

    procedure_reason_code: Optional[str] = None

    procedure_reason_code_system: Optional[str] = None

    procedure_text: Optional[str] = None


class Provenance(BaseModel):
    patient_id: Optional[str] = None

    provenance_activity_code: Optional[str] = None

    provenance_activity_code_system: Optional[str] = None

    provenance_agent_type_code: Optional[str] = None

    provenance_agent_type_code_system: Optional[str] = None

    provenance_entity_role: Optional[str] = None

    provenance_entity_what_display: Optional[str] = None

    provenance_entity_what_identifier: Optional[str] = None

    provenance_id: Optional[str] = None

    provenance_target: Optional[str] = None

    provenance_who: Optional[str] = None

    recorded_date: Optional[str] = None


class RelatedPerson(BaseModel):
    patient_id: Optional[str] = None

    project_id: Optional[str] = None

    related_person_address_city: Optional[str] = None

    related_person_address_country: Optional[str] = None

    related_person_address_lines: Optional[str] = None

    related_person_address_postal_code: Optional[str] = None

    related_person_address_state: Optional[str] = None

    related_person_address_use: Optional[str] = None

    related_person_id: Optional[str] = None

    related_person_identifier_system: Optional[str] = None

    related_person_identifier_value: Optional[str] = None

    related_person_name: Optional[str] = None

    related_person_patient_reference_id: Optional[str] = None

    related_person_period_end: Optional[str] = None

    related_person_period_start: Optional[str] = None

    related_person_relationship_code: Optional[str] = None

    related_person_relationship_display: Optional[str] = None

    related_person_relationship_system: Optional[str] = None

    related_person_telecom_system: Optional[str] = None

    related_person_telecom_value: Optional[str] = None


class SocialHistory(BaseModel):
    observation_category: Optional[str] = None

    patient_id: Optional[str] = None

    practitioner_role_reference_id: Optional[str] = None

    social_history_observation_code: Optional[str] = None

    social_history_observation_code_system: Optional[str] = None

    social_history_observation_id: Optional[str] = None

    social_history_observation_name: Optional[str] = None

    social_history_observation_timestamp: Optional[str] = None

    social_history_observation_value: Optional[str] = None

    social_history_observation_value_code: Optional[str] = None

    social_history_observation_value_code_system: Optional[str] = None

    social_history_text: Optional[str] = None


class VitalSign(BaseModel):
    observation_category: Optional[str] = None

    patient_id: Optional[str] = None

    vital_sign_grouping_observation_id: Optional[str] = None

    vital_sign_observation_code: Optional[str] = None

    vital_sign_observation_code_system: Optional[str] = None

    vital_sign_observation_id: Optional[str] = None

    vital_sign_observation_name: Optional[str] = None

    vital_sign_observation_text: Optional[str] = None

    vital_sign_observation_time: Optional[str] = None

    vital_sign_observation_unit: Optional[str] = None

    vital_sign_observation_value: Optional[float] = None


class Datasets(BaseModel):
    allergies: Optional[List[Allergy]] = None

    composition: Optional[List[Composition]] = None

    coverages: Optional[List[Coverage]] = None

    document_references: Optional[List[DocumentReference]] = FieldInfo(alias="documentReferences", default=None)

    encounters: Optional[List[Encounter]] = None

    family_member_histories: Optional[List[FamilyMemberHistory]] = FieldInfo(
        alias="familyMemberHistories", default=None
    )

    immunizations: Optional[List[Immunization]] = None

    labs: Optional[List[Lab]] = None

    locations: Optional[List[Location]] = None

    medications: Optional[List[Medication]] = None

    med_recs: Optional[List[MedRec]] = FieldInfo(alias="medRecs", default=None)

    organizations: Optional[List[Organization]] = None

    patients: Optional[List[Patient]] = None

    practitioners: Optional[List[Practitioner]] = None

    problems: Optional[List[Problem]] = None

    procedures: Optional[List[Procedure]] = None

    provenances: Optional[List[Provenance]] = None

    related_persons: Optional[List[RelatedPerson]] = FieldInfo(alias="relatedPersons", default=None)

    social_histories: Optional[List[SocialHistory]] = FieldInfo(alias="socialHistories", default=None)

    vital_signs: Optional[List[VitalSign]] = FieldInfo(alias="vitalSigns", default=None)
