from fhir.resources.codesystem import CodeSystem, CodeSystemConcept, CodeSystemConceptDesignation
from datetime import datetime
from terminology.resources.naming_systems import OpenOrthoNamingSystem
from terminology.resources.code_systems import leave_code_as_is as make_code
from terminology.constants import CODE_SYSTEM_UIDS

id = "extraoral-3d-visible-light-scheduled-protocol"

class Extraoral3DVisibleLightScheduledProtocolCodeSystem(CodeSystem):

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
            version="1.2.1",
            name="Extraoral3DVisibleLightScheduledProtocol",
            title="Extraoral 3D Visible Light Scheduled Protocol",
            status="draft",
            experimental=True,
            date=datetime.now().date().isoformat(),
            publisher=OPOR.publisher,
            description="Common extraoral 3D visible light views used in an orthodontic provider's practice, producing a 3D surface of the head and neck",
            caseSensitive=True,
            content="complete",
            concept=[value for name, value in globals(
            ).items() if isinstance(value, CodeSystemConcept)]
        )


EV3D01 = CodeSystemConcept(
    code=f"{make_code('EV3D01')}",
    display="Extraoral 3D surface,whole head,lips closed,centric occlusion",
    definition="Extraoral Whole head - lips closed, CO",
    designation=[
        CodeSystemConceptDesignation(
            value="EV3D-01",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.WH.LC.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV3D02 = CodeSystemConcept(
    code=f"{make_code('EV3D02')}",
    display="Extraoral 3D surface,whole head,lips closed,centric relation",
    definition="Extraoral Whole head - lips closed, CR",
    designation=[
        CodeSystemConceptDesignation(
            value="EV3D-02",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.WH.LC.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV3D03 = CodeSystemConcept(
    code=f"{make_code('EV3D03')}",
    display="Extraoral 3D surface,whole head,lips relaxed,centric occlusion",
    definition="Extraoral Whole head - lips relaxed, CO",
    designation=[
        CodeSystemConceptDesignation(
            value="EV3D-03",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.WH.LR.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV3D04 = CodeSystemConcept(
    code=f"{make_code('EV3D04')}",
    display="Extraoral 3D surface,whole head,lips relaxed,centric relation",
    definition="Extraoral Whole head - lips relaxed, CR",
    designation=[
        CodeSystemConceptDesignation(
            value="EV3D-04",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.WH.LR.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV3D05 = CodeSystemConcept(
    code=f"{make_code('EV3D05')}",
    display="Extraoral 3D surface,whole head,full smile,centric occlusion",
    definition="Extraoral Whole head - smile, CO",
    designation=[
        CodeSystemConceptDesignation(
            value="EV3D-05",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.WH.FS.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV3D06 = CodeSystemConcept(
    code=f"{make_code('EV3D06')}",
    display="Extraoral 3D surface,whole head,full smile,centric relation",
    definition="Extraoral Whole head - smile, CR",
    designation=[
        CodeSystemConceptDesignation(
            value="EV3D-06",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.WH.FS.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)
