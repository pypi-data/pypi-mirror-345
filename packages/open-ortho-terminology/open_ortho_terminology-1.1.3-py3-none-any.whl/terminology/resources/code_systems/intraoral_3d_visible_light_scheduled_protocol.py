from fhir.resources.codesystem import CodeSystem, CodeSystemConcept, CodeSystemConceptDesignation
from datetime import datetime
from terminology.resources.naming_systems import OpenOrthoNamingSystem
from terminology.resources.code_systems import leave_code_as_is as make_code
from terminology.constants import CODE_SYSTEM_UIDS

id = "intraoral-3d-visible-light-scheduled-protocol"

class Intraoral3DVisibleLightScheduledProtocolCodeSystem(CodeSystem):

    @classmethod
    def static_url(cls) -> str:
        ns = OpenOrthoNamingSystem()
        return f"{ns.url}/{id}"

    def __init__(self):
        OPOR = OpenOrthoNamingSystem()
        super().__init__(
            id=id,
            identifier=[
                {
                    "system": "urn:ietf:rfc:3986",
                    "value": f"urn:oid:{CODE_SYSTEM_UIDS[id]}"
                }
            ],
            url=self.static_url(),
            version="1.1.1",
            name="Intraoral3DVisibleLightScheduledProtocol",
            title="Intraoral 3D Visible Light Scheduled Protocol",
            status="draft",
            experimental=True,
            date=datetime.now().date().isoformat(),
            publisher=OPOR.publisher,
            description="Common intraoral 3D visible light views used in an orthodontic provider's practice, producing a 3D surface of the dentition",
            caseSensitive=True,
            content="complete",
            concept=[value for name, value in globals(
            ).items() if isinstance(value, CodeSystemConcept)]
        )


IV3D01 = CodeSystemConcept(
    code=f"{make_code('IV3D01')}",
    display="Intraoral 3D surface,maxillary dentition",
    definition="Intraoral 3D Surface of the Maxillary Dentition",
    designation=[
        CodeSystemConceptDesignation(
            value="IV3D-01",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.MX",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV3D02 = CodeSystemConcept(
    code=f"{make_code('IV3D02')}",
    display="Intraoral 3D surface,mandibular dentition",
    definition="Intraoral 3D Surface of the Mandibular Dentition",
    designation=[
        CodeSystemConceptDesignation(
            value="IV3D-02",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.MD",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV3D03 = CodeSystemConcept(
    code=f"{make_code('IV3D03')}",
    display="Intraoral 3D surface,occluding maxillary and mandibular teeth",
    definition="Intraoral 3D Surface of Occluding Maxillary and Mandibular Teeth (showing how the teeth fit together, i.e. the bite)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV3D-03",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.BT",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)
