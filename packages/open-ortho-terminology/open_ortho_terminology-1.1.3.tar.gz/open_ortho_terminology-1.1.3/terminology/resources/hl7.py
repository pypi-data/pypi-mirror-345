""" hl7: a collection of static HL7 codes.

Used whenever a code is necessary, for various implementations.
"""
from . import Code

class NAMESPACES:
    fhir_root =  "http://hl7.org/fhir"
    fhir_version_root = "http://hl7.org/fhir/5.0"
    fhir_codesystem = "http://terminology.hl7.org/CodeSystem"
    fhir_valueset = "http://hl7.org/fhir/ValueSet"
    fhir_structured_definition = "http://hl7.org/fhir/StructureDefinition"

    fhir_version_root = f"{fhir_root}/5.0"
    EncounterReasonUse = f"{fhir_root}/encounter-reason-use"

    EncounterReasonCodes = f"{ fhir_valueset}/encounter-reason"

    ParticipationType = f"{ fhir_codesystem}/v3-ParticipationType"
    LocationType = f"{ fhir_codesystem}/location-physical-type"
    EncounterType = f"{fhir_codesystem}/encounter-type"
    EncounterClass = f"{fhir_codesystem}/v3-ActCode"
    ProvenanceParticipantType = f"{ fhir_codesystem}/provenance-participant-type"
    ProvenanceParticipationType = f"{ fhir_codesystem}/provenance-participant-type"
    ServiceType = f"{fhir_codesystem}/service-type"
    ServiceCategory = f"{ fhir_codesystem}/service-category"
    Iso_21089_2017_Health_Record_Lifecycle_Events = f"{ fhir_codesystem}/iso-21089-lifecycle"
    AppointmentCancellationReason = f"{ fhir_codesystem}/appointment-cancellation-reason"

    Location = f"{fhir_structured_definition}/Location"
    Practitioner = f"{ fhir_structured_definition}/Practitioner"
    Patient = f"{fhir_structured_definition}/Patient"
    Appointment = f"{ fhir_structured_definition}/Appointment"
    Encounter = f"{fhir_structured_definition}/Encounter"


bed = Code(
    system=NAMESPACES.LocationType,
    code='bd',
    display='Bed')
""" Used for Chairs """

enterer = Code(
    system=NAMESPACES.ProvenanceParticipantType,
    code='enterer',
    display='Enterer')
""" Used for appointing_staff_member in Appointments. """

originate = Code(
    system=NAMESPACES.Iso_21089_2017_Health_Record_Lifecycle_Events,
    code='originate',
    display='Originate/Retain Record Lifecycle Event')
""" Used for appointing_staff_member. """

amend = Code(
    system=NAMESPACES.Iso_21089_2017_Health_Record_Lifecycle_Events,
    code='amend',
    display='Amend (Update) Record Lifecycle Event')
""" Used for appointing_staff_member. """

inpatient_encounter = Code(
    system=NAMESPACES.EncounterClass,
    code='IMP',
    display='inpatient encounter')
""" Used for Encounter Class. """

home_health = Code(
    system=NAMESPACES.EncounterClass,
    code='HH',
    display='home health')
""" Used for Encounter Class. """

virtual = Code(
    system=NAMESPACES.EncounterClass,
    code='VR',
    display='virtual')
""" Used for Encounter Class. """

reason_for_visit = Code(
    system=NAMESPACES.EncounterReasonUse,
    code='RV',
    display='Reason for Visit')
""" Usesd for Encounter Reason Use. """

admitter = Code(
    system=NAMESPACES.ParticipationType,
    code='ADM',
    display='admitter')
""" Usesd for seating_staff. """

attender = Code(
    system=NAMESPACES.ParticipationType,
    code='ATND',
    display='attender')
""" Usesd for orthodontist_id. """

prov = Code(
    system=NAMESPACES.AppointmentCancellationReason,
    code='prov',
    display='Provider')
""" Used for cancellation_reason. """

pat = Code(
    system=NAMESPACES.AppointmentCancellationReason,
    code='pat',
    display='Patient')
""" Used for cancellation_reason. """

dental = Code(
    system=NAMESPACES.ServiceCategory,
    code='10',
    display='Dental')
""" Used for appointment service category. """

orthodontic = Code(
    system=NAMESPACES.ServiceType,
    code='91',
    display='Orthodontic')
""" Used for appointment service type. """

general_dental = Code(
    system=NAMESPACES.ServiceType,
    code='88',
    display='General Dental')
""" Used for appointment service type. """

endodontic = Code(
    system=NAMESPACES.ServiceType,
    code='87',
    display='Endodontic')
""" Used for appointment service type. """