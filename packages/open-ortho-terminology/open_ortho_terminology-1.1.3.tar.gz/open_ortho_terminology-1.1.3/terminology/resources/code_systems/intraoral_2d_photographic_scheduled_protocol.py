from fhir.resources.codesystem import CodeSystem, CodeSystemConcept, CodeSystemConceptDesignation
from datetime import datetime
from terminology.resources.naming_systems import OpenOrthoNamingSystem
from terminology.resources.code_systems import leave_code_as_is as make_code
from terminology.resources.code_systems import add_meta_to_resource
from terminology.constants import CODE_SYSTEM_UIDS

id = "intraoral-2d-photographic-scheduled-protocol"

class Intraoral2DPhotographicScheduledProtocolCodeSystem(CodeSystem):

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
            version="1.3.1",
            name="Intraoral2DPhotographicScheduledProtocol",
            title="Intraoral 2D Photographic Scheduled Protocol",
            status="draft",
            experimental=False,
            date=datetime.now().date().isoformat(),
            publisher=OPOR.publisher,
            description="Common intraoral 2D photographic views used in an orthodontic provider's practice",
            caseSensitive=True,
            content="complete",
            concept=[value for name, value in globals(
            ).items() if isinstance(value, CodeSystemConcept)]
        )


IV01 = CodeSystemConcept(
    code=f"{make_code('IV01')}",
    display="Intraoral photo,right buccal,centric occl.,no mirror",
    definition="Intraoral, Right Buccal Segment, Centric Occlusion, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-01",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.RB.CO.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV02 = CodeSystemConcept(
    code=f"{make_code('IV02')}",
    display="Intraoral photo,right buccal,centric occl.,mirror",
    definition="Intraoral, Right Buccal Segment, Centric Occlusion, With Mirror",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-02",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.RB.CO.WM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV03 = CodeSystemConcept(
    code=f"{make_code('IV03')}",
    display="Intraoral photo,right buccal,centric occl.,mirror,corrected",
    definition="Intraoral, Right Buccal Segment, Centric Occlusion, With Mirror, But Corrected",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-03",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.RB.CO.WM.BC",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV04 = CodeSystemConcept(
    code=f"{make_code('IV04')}",
    display="Intraoral photo,right buccal,centric relation,no mirror",
    definition="Intraoral, Right Buccal Segment, Centric Relation, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-04",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.RB.CR.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV05 = CodeSystemConcept(
    code=f"{make_code('IV05')}",
    display="Intraoral photo,right buccal,centric relation,mirror",
    definition="Intraoral, Right Buccal Segment, Centric Relation, With Mirror",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-05",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.RB.CR.WM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV06 = CodeSystemConcept(
    code=f"{make_code('IV06')}",
    display="Intraoral photo,right buccal,centric relation,mirror,corrected",
    definition="Intraoral, Right Buccal Segment, Centric Relation, With Mirror, But Corrected",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-06",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.RB.CR.WM.BC",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV07 = CodeSystemConcept(
    code=f"{make_code('IV07')}",
    display="Intraoral photo,front ,centric occl.,no mirror",
    definition="Intraoral, Frontal View, Centric Occlusion, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-07",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.FV.CO.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV08 = CodeSystemConcept(
    code=f"{make_code('IV08')}",
    display="Intraoral photo,frontal,centric relation,no mirror",
    definition="Intraoral, Frontal View, Centric Relation, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-08",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.FV.CR.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV09 = CodeSystemConcept(
    code=f"{make_code('IV09')}",
    display="Intraoral photo,frontal,teeth apart,no mirror",
    definition="Intraoral, Frontal View, Teeth Apart, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-09",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.FV.TA.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV10 = CodeSystemConcept(
    code=f"{make_code('IV10')}",
    display="Intraoral photo,frontal,mouth open,no mirror",
    definition="Intraoral, Frontal View, Mouth Open, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-10",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.FV.MO.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV11 = CodeSystemConcept(
    code=f"{make_code('IV11')}",
    display="Intraoral photo,front view inferior,centric occl.,no mirror",
    definition="Intraoral, Frontal View Inferior (showing depth of bite and overjet), Centric Occlusion, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-11",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.FV.IV.CO.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV12 = CodeSystemConcept(
    code=f"{make_code('IV12')}",
    display="Intraoral photo,front view inferior,centric relation,no mirror",
    definition="Intraoral, Frontal View Inferior (showing depth of bite and overjet), Centric Relation, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-12",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.FV.IV.CR.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV13 = CodeSystemConcept(
    code=f"{make_code('IV13')}",
    display="Intraoral photo,frontal,tongue thrust,no mirror",
    definition="Intraoral, Frontal View, showing Tongue Thrust, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-13",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.FV.TT.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV14 = CodeSystemConcept(
    code=f"{make_code('IV14')}",
    display="Intraoral photo,right lateral,centric occl.,overjet,no mirror",
    definition="Intraoral, Right Lateral View, Centric Occlusion, showing Overjet, No Mirror (Direct View showing overjet from the side)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-14",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.RL.CO.OJ.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV15 = CodeSystemConcept(
    code=f"{make_code('IV15')}",
    display="Intraoral photo,right lateral,centric relation,overjet,no mirror",
    definition="Intraoral, Right Lateral View, Centric Relation, showing Overjet, No Mirror (Direct View showing overjet from the side)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-15",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.RL.CR.OJ.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV16 = CodeSystemConcept(
    code=f"{make_code('IV16')}",
    display="Intraoral photo,left lateral,centric occl.,overjet,no mirror",
    definition="Intraoral, Left Lateral View, Centric Occlusion, showing Overjet, No Mirror (Direct View showing overjet from the side)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-16",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.LL.CO.OJ.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV17 = CodeSystemConcept(
    code=f"{make_code('IV17')}",
    display="Intraoral photo,left lateral,centric relation,overjet,no mirror",
    definition="Intraoral, Left Lateral View, Centric Relation, showing Overjet, No Mirror (Direct View showing overjet from the side)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-17",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.LL.CR.OJ.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV18 = CodeSystemConcept(
    code=f"{make_code('IV18')}",
    display="Intraoral photo,left buccal,centric occl.,no mirror",
    definition="Intraoral, Left Buccal Segment, Centric Occlusion, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-18",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.LB.CO.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV19 = CodeSystemConcept(
    code=f"{make_code('IV19')}",
    display="Intraoral photo,left buccal,centric occl.,mirror",
    definition="Intraoral, Left Buccal Segment, Centric Occlusion, With Mirror",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-19",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.LB.CO.WM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV20 = CodeSystemConcept(
    code=f"{make_code('IV20')}",
    display="Intraoral photo,left buccal,centric occl.,mirror,corrected",
    definition="Intraoral, Left Buccal Segment, Centric Occlusion, With Mirror, But Corrected",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-20",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.LB.CO.WM.BC",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV21 = CodeSystemConcept(
    code=f"{make_code('IV21')}",
    display="Intraoral photo,left buccal,centric relation,no mirror",
    definition="Intraoral, Left Buccal Segment, Centric Relation, No Mirror (Direct View)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-21",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.LB.CR.NM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV22 = CodeSystemConcept(
    code=f"{make_code('IV22')}",
    display="Intraoral photo,left buccal,centric relation,mirror",
    definition="Intraoral, Left Buccal Segment, Centric Relation, With Mirror",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-22",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.LB.CR.WM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV23 = CodeSystemConcept(
    code=f"{make_code('IV23')}",
    display="Intraoral photo,left buccal,centric relation,mirror,corrected",
    definition="Intraoral, Left Buccal Segment, Centric Relation, With Mirror, But Corrected",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-23",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.LB.CR.WM.BC",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV24 = CodeSystemConcept(
    code=f"{make_code('IV24')}",
    display="Intraoral photo,maxillary,mouth open,occlusal,mirror",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-24",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.MX.MO.OV.WM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV25 = CodeSystemConcept(
    code=f"{make_code('IV25')}",
    display="Intraoral photo,maxillary,mouth open,occlusal,mirror,corrected",
    definition="Intraoral, Maxillary, Mouth Open, Occlusal View, With Mirror, But Corrected",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-25",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.MX.MO.OV.WM.BC",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV26 = CodeSystemConcept(
    code=f"{make_code('IV26')}",
    display="Intraoral photo,mandibular,mouth open,occlusal,mirror",
    definition="Intraoral, Mandibular, Mouth Open, Occlusal View, With Mirror",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-26",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.MD.MO.OV.WM",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV27 = CodeSystemConcept(
    code=f"{make_code('IV27')}",
    display="Intraoral photo,mandibular,mouth open,occlusal,mirror,corrected",
    definition="Intraoral, Mandibular, Mouth Open, Occlusal View, With Mirror, But Corrected",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-27",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.MD.MO.OV.WM.BC",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV28 = CodeSystemConcept(
    code=f"{make_code('IV28')}",
    display="Intraoral photo,gingival recession",
    definition="Intraoral, showing Gingival Recession. May include ISO tooth numbers of the affected teeth.",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-28",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.GR.[tooth number]",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV29 = CodeSystemConcept(
    code=f"{make_code('IV29')}",
    display="Intraoral photo,frenum",
    definition="Intraoral, showing Frenum. May include ISO tooth numbers designating frenum's location.",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-29",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.FR.[tooth number]",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)

IV30 = CodeSystemConcept(
    code=f"{make_code('IV30')}",
    display="Intraoral photo,photo accessory",
    definition="Intraoral, any view using a photo accessory device such as a contraster to provide a solid background or black mirror ([modifier] is any set of IO modifier as specified above)",
    designation=[
        CodeSystemConceptDesignation(
            value="IV-30",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
        CodeSystemConceptDesignation(
            value="IO.[modifier].PA",
            use={
                "system": "http://snomed.info/sct",
                "code": "900000000000013009",
                "display": "Synonym"
            }
        ),
    ]
)
