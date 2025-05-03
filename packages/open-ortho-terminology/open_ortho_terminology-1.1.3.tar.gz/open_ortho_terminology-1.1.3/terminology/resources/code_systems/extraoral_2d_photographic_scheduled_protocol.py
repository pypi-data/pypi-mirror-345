from fhir.resources.codesystem import CodeSystem, CodeSystemConcept, CodeSystemConceptDesignation
from datetime import datetime
from terminology.resources.naming_systems import OpenOrthoNamingSystem
from terminology.resources.code_systems import leave_code_as_is as make_code
from terminology.constants import CODE_SYSTEM_UIDS


id = "extraoral-2d-photographic-scheduled-protocol"


class Extraoral2DPhotographicScheduledProtocolCodeSystem(CodeSystem):

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
            version="1.2.2",
            name="Extraoral2DPhotographicScheduledProtocol",
            title="Extraoral 2D Photographic Scheduled Protocol",
            status="draft",
            experimental=False,
            date=datetime.now().date().isoformat(),
            publisher=OPOR.publisher,
            description="Common extraoral 2D photographic views used in an orthodontic provider's practice",
            caseSensitive=True,
            content="complete",
            concept=[value for name, value in globals(
            ).items() if isinstance(value, CodeSystemConcept)]
        )


EV01 = CodeSystemConcept(
    code=f"{make_code('EV01')}",
    display="Extraoral photo,right profile,lips relaxed,centric occlusion",
    definition="Extraoral, Right Profile (Subject is facing observer's right), Lips Relaxed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-01",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.LR.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV02 = CodeSystemConcept(
    code=f"{make_code('EV02')}",
    display="Extraoral photo,right profile,lips relaxed,centric relation",
    definition="Extraoral, Right Profile (Subject is facing observe right), Lips Relaxed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-02",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.LR.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV03 = CodeSystemConcept(
    code=f"{make_code('EV03')}",
    display="Extraoral photo,right profile,lips closed,centric occlusion",
    definition="Extraoral, Right Profile (Subject is facing observer's right), Lips Closed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-03",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.LC.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV04 = CodeSystemConcept(
    code=f"{make_code('EV04')}",
    display="Extraoral photo,right profile,lips closed,centric relation",
    definition="Extraoral, Right Profile (Patient is facing observer's right), Lips Closed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-04",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.LC.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV05 = CodeSystemConcept(
    code=f"{make_code('EV05')}",
    display="Extraoral photo,right profile,full smile,centric occlusion",
    definition="Extraoral, Right profile (Patient is facing observer's right), Full Smile, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-05",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.FS.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV06 = CodeSystemConcept(
    code=f"{make_code('EV06')}",
    display="Extraoral photo,right profile,full smile,centric relation",
    definition="Extraoral, Right Profile (Patient is facing observer's right), Full Smile, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-06",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.FS.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV07 = CodeSystemConcept(
    code=f"{make_code('EV07')}",
    display="Extraoral photo,right profile,mandible postured forward",
    definition="Extraoral, Right Profile (Patient is facing observer's right), Mandible Postured Forward",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-07",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.MD.PF",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV08 = CodeSystemConcept(
    code=f"{make_code('EV08')}",
    display="Extraoral photo,right profile 45,lips relaxed,centric occlusion",
    definition="Extraoral, 45° Right Profile (Patient turns toward observer's right), Lips Relaxed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-08",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.LR.CO.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV09 = CodeSystemConcept(
    code=f"{make_code('EV09')}",
    display="Extraoral photo,right profile 45,lips relaxed,centric relation",
    definition="Extraoral, 45° Right Profile (Patient turns toward observer's right), Lips Relaxed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-09",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.LR.CR.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV10 = CodeSystemConcept(
    code=f"{make_code('EV10')}",
    display="Extraoral photo,right profile 45,lips closed,centric occlusion",
    definition="Extraoral, 45° Right Profile (Patient turns toward observer's right), Lips Closed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-10",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.LC.CO.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV11 = CodeSystemConcept(
    code=f"{make_code('EV11')}",
    display="Extraoral photo,right profile 45,lips closed,centric relation",
    definition="Extraoral, 45° Right Profile (Patient turns toward observer's right), Lips Closed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-11",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.LC.CR.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV12 = CodeSystemConcept(
    code=f"{make_code('EV12')}",
    display="Extraoral photo,right profile 45,full smile,centric occlusion",
    definition="Extraoral, 45° Right Profile (Patient turns toward observer's right), Full Smile, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-12",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.FS.CO.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV13 = CodeSystemConcept(
    code=f"{make_code('EV13')}",
    display="Extraoral photo,right profile 45,full smile,centric relation",
    definition="Extraoral, 45° Right Profile (Patient turns toward observer's right), Full Smile, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-13",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.FS.CR.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV14 = CodeSystemConcept(
    code=f"{make_code('EV14')}",
    display="Extraoral photo,right profile 45,mandible postured forward",
    definition="Extraoral, 45° Right Profile (Patient turns toward observer's right), Mandible Postured Forward",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-14",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.RP.MD.PF.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV15 = CodeSystemConcept(
    code=f"{make_code('EV15')}",
    display="Extraoral photo,full face,lips relaxed,centric occlusion",
    definition="Extraoral, Full Face, Lips Relaxed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-15",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.LR.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV16 = CodeSystemConcept(
    code=f"{make_code('EV16')}",
    display="Extraoral photo,full face,lips relaxed,centric relation",
    definition="Extraoral, Full Face, Lips Relaxed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-16",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.LR.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV17 = CodeSystemConcept(
    code=f"{make_code('EV17')}",
    display="Extraoral photo,full face,lips closed,centric occlusion",
    definition="Extraoral, Full Face, Lips Closed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-17",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.LC.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV18 = CodeSystemConcept(
    code=f"{make_code('EV18')}",
    display="Extraoral photo,full face,lips closed,centric relation",
    definition="Extraoral, Full Face, Lips Closed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-18",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.LC.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV19 = CodeSystemConcept(
    code=f"{make_code('EV19')}",
    display="Extraoral photo,full face,full smile,centric occlusion",
    definition="Extraoral, Full Face, Full Smile, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-19",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.FS.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV20 = CodeSystemConcept(
    code=f"{make_code('EV20')}",
    display="Extraoral photo,full face,full smile,centric relation",
    definition="Extraoral, Full Face, Full Smile, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-20",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.FS.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV21 = CodeSystemConcept(
    code=f"{make_code('EV21')}",
    display="Extraoral photo,full face,mandible postured forward",
    definition="Extraoral, Full Face, Mandible Postured Forward",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-21",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.MD.PF",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV22 = CodeSystemConcept(
    code=f"{make_code('EV22')}",
    display="Extraoral photo,left profile,lips relaxed,centric occlusion",
    definition="Extraoral, Left Profile (Patient is facing observer's left), Lips Relaxed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-22",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.LR.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV23 = CodeSystemConcept(
    code=f"{make_code('EV23')}",
    display="Extraoral photo,left profile,lips relaxed,centric relation",
    definition="Extraoral, Left Profile (Patient is facing observer's left), Lips Relaxed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-23",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.LR.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV24 = CodeSystemConcept(
    code=f"{make_code('EV24')}",
    display="Extraoral photo,left profile,lips closed,centric occlusion",
    definition="Extraoral, Left Profile (Patient is facing observer's left), Lips Closed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-24",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.LC.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV25 = CodeSystemConcept(
    code=f"{make_code('EV25')}",
    display="Extraoral photo,left profile,lips closed,centric relation",
    definition="Extraoral, Left Profile (Patient is facing observer's left), Lips Closed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-25",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.LC.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV26 = CodeSystemConcept(
    code=f"{make_code('EV26')}",
    display="Extraoral photo,left profile,full smile,centric occlusion",
    definition="Extraoral, Left profile (Patient is facing observer's left), Full Smile, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-26",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.FS.CO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV27 = CodeSystemConcept(
    code=f"{make_code('EV27')}",
    display="Extraoral photo,left profile,full smile,centric relation",
    definition="Extraoral, Left Profile (Patient is facing observer's left), Full Smile, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-27",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.FS.CR",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV28 = CodeSystemConcept(
    code=f"{make_code('EV28')}",
    display="Extraoral photo,left profile,mandible postured forward",
    definition="Extraoral, Left Profile (Patient is facing observer's left), Mandible Postured Forward",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-28",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.MD.PF",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV29 = CodeSystemConcept(
    code=f"{make_code('EV29')}",
    display="Extraoral photo,left profile 45,lips relaxed,centric occlusion",
    definition="Extraoral, 45° Left Profile (Patient turns toward observer's left), Lips Relaxed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-29",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.LR.CO.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV30 = CodeSystemConcept(
    code=f"{make_code('EV30')}",
    display="Extraoral photo,left profile 45,lips relaxed,centric relation",
    definition="Extraoral, 45° Left Profile (Patient turns toward observer's left), Lips Relaxed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-30",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.LR.CR.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV31 = CodeSystemConcept(
    code=f"{make_code('EV31')}",
    display="Extraoral photo,left profile 45,lips closed,centric occlusion",
    definition="Extraoral, 45° Left Profile (Patient turns toward observer's left), Lips Closed, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-31",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.LC.CO.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV32 = CodeSystemConcept(
    code=f"{make_code('EV32')}",
    display="Extraoral photo,left profile 45,lips closed,centric relation",
    definition="Extraoral, 45° Left Profile (Patient turns toward observer's left), Lips Closed, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-32",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.LC.CR.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV33 = CodeSystemConcept(
    code=f"{make_code('EV33')}",
    display="Extraoral photo,left profile 45,full smile,centric occlusion",
    definition="Extraoral, 45° Left Profile (Patient turns toward observer's left), Full Smile, Centric Occlusion",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-33",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.FS.CO.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV34 = CodeSystemConcept(
    code=f"{make_code('EV34')}",
    display="Extraoral photo,left profile 45,full smile,centric relation",
    definition="Extraoral, 45° Left Profile (Patient turns toward observer's left, Full Smile, Centric Relation",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-34",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.FS.CR.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV35 = CodeSystemConcept(
    code=f"{make_code('EV35')}",
    display="Extraoral photo,left profile 45,mandible postured forward",
    definition="Extraoral, 45° Left Profile (Patient turns toward observer's left, Mandible Postured Forward",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-35",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.LP.MD.PF.45",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV36 = CodeSystemConcept(
    code=f"{make_code('EV36')}",
    display="Extraoral photo,other face,inferior view",
    definition="Extraoral, Other Face (head tipped back), Inferior View (showing lower border of mandible, nares, infraorbital rim contours, forehead contours)",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-36",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.OF.IV",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV37 = CodeSystemConcept(
    code=f"{make_code('EV37')}",
    display="Extraoral photo,other face,superior view",
    definition="Extraoral, Other Face (viewed from above), Superior View (showing forehead, infraorbital rim contour, dorsum of nose, upper lip, chin)",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-37",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.OF.SV",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV38 = CodeSystemConcept(
    code=f"{make_code('EV38')}",
    display="Extraoral photo,other face,close-up smile",
    definition="Extraoral, Other Face, Close-Up Smile (with lips)",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-38",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.OF.CS",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV39 = CodeSystemConcept(
    code=f"{make_code('EV39')}",
    display="Extraoral photo,other face,occlusal cant",
    definition="Extraoral, Other Face, Occlusal Cant (e.g., tongue depressor between the teeth)",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-39",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.OF.OC",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV40 = CodeSystemConcept(
    code=f"{make_code('EV40')}",
    display="Extraoral photo,other face,forensic interest",
    definition="Extraoral, Other Face, Forensic Interest (tattoos, jewelry, scars)",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-40",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.OF.FI",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV41 = CodeSystemConcept(
    code=f"{make_code('EV41')}",
    display="Extraoral photo,other face,anomalies",
    definition="Extraoral, Other Face, Anomalies (ears, skin tags, etc.)",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-41",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.OF.AN",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV42 = CodeSystemConcept(
    code=f"{make_code('EV42')}",
    display="Extraoral photo,full face,mouth open",
    definition="Extraoral, Full Face, Mouth Open",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-42",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.MO",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

EV43 = CodeSystemConcept(
    code=f"{make_code('EV43')}",
    display="Extraoral photo,full face,demonstrating nerve weakness",
    definition="Extraoral, Full Face, demonstrating Nerve Weakness",
    designation=[
        CodeSystemConceptDesignation(
            value="EV-43",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="EO.FF.NW",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)
