"""

"""

from fhir.resources.codesystem import CodeSystem, CodeSystemConcept
from datetime import datetime
from terminology.resources.naming_systems import OpenOrthoNamingSystem

id = "ada-1100-enumerated-terms"

class ADA1100EnumeratedTermsCodeSystem(CodeSystem):

    @classmethod
    def static_url(cls) -> str:
        return f"http://terminology.open-ortho.org/fhir/{id}"

    def __init__(self):
        OPOR = OpenOrthoNamingSystem()
        super().__init__(
            id=id,
            identifier=OPOR.identifier,
            url=self.static_url(),
            version="1.0.0",
            name="ADA1100EnumeratedTerms",
            title="ADA 1100 Enumerated Terms",
            copyright="MIT License",
            status="draft",
            experimental=False,
            date=datetime.now().date().isoformat(),
            publisher="Open Ortho",
            description="Enumerated terms used in ADA 1100.",
            caseSensitive=True,
            content="complete",
            concept=[
                CodeSystemConcept(
                    code="IO",
                    display="IntraOral",
                    definition="IV - intraoral view"
                ),
                CodeSystemConcept(
                    code="EO",
                    display="ExtraOral",
                    definition="EV - extraoral view"
                ),
                CodeSystemConcept(
                    code="MD",
                    display="ManDibular",
                    definition="used to reference lower jaw or lower dental arch"
                ),
                CodeSystemConcept(
                    code="MX",
                    display="MaXillary",
                    definition="used to reference upper jaw or upper dental arch"
                ),
                CodeSystemConcept(
                    code="MO",
                    display="Mouth Open",
                    definition="used to document views taken with mouth wide open"
                ),
                CodeSystemConcept(
                    code="MC",
                    display="Mouth Closed",
                    definition="teeth together. DON'T USE; instead, use LC, CO or CR (see below)"
                ),
                CodeSystemConcept(
                    code="TA",
                    display="Teeth Apart",
                    definition="used to document intraoral views with teeth slightly apart"
                ),
                CodeSystemConcept(
                    code="CO",
                    display="Centric Occlusion",
                    definition="maximum intercuspation of teeth"
                ),
                CodeSystemConcept(
                    code="CR",
                    display="Centric Relation",
                    definition="the joint determined position of the mandible"
                ),
                CodeSystemConcept(
                    code="OJ",
                    display="showing OverJet",
                    definition="horizontal distance between maxillary and mandibular incisors"
                ),
                CodeSystemConcept(
                    code="RP",
                    display="Right Profile",
                    definition="used to document extraoral photographs of the subject's right profile"
                ),
                CodeSystemConcept(
                    code="LP",
                    display="Left Profile",
                    definition="used to document extraoral photographs of the subject's left profile"
                ),
                CodeSystemConcept(
                    code="FF",
                    display="Full Face",
                    definition="used to document extraoral views of the subject’s frontal view"
                ),
                CodeSystemConcept(
                    code="LR",
                    display="Lips Relaxed",
                    definition="perioral muscles are relaxed, lips may or may not be touching"
                ),
                CodeSystemConcept(
                    code="LC",
                    display="Lips Closed",
                    definition="perioral muscles may or may not be relaxed, but lips are touching"
                ),
                CodeSystemConcept(
                    code="FS",
                    display="Full Smile",
                    definition="used to document extraoral views of the subject smiling"
                ),
                CodeSystemConcept(
                    code="PF",
                    display="mandible Postured Forward",
                    definition="used to document extraoral views of the subject with mandible protruding"
                ),
                CodeSystemConcept(
                    code="OF",
                    display="Other Face",
                    definition="some otherwise uncoded view of the face; e.g., with the face tipped back, or from above"
                ),
                CodeSystemConcept(
                    code="NM",
                    display="No Mirror",
                    definition="Used for intraoral views only. Image was acquired directly without the use of a mirror"
                ),
                CodeSystemConcept(
                    code="WM",
                    display="With Mirror",
                    definition="used for intraoral photographs only. Does not apply to extraoral photographs"
                ),
                CodeSystemConcept(
                    code="WM.BC",
                    display="With Mirror, But Corrected",
                    definition="image is flipped and/or rotated to appear as if it has been taken directly without a mirror. Used for intraoral photographs only. Does not apply to extraoral photographs"
                ),
                CodeSystemConcept(
                    code="RB",
                    display="Right Buccal",
                    definition="used to document posterior dental occlusion on the subject's right side"
                ),
                CodeSystemConcept(
                    code="LB",
                    display="Left Buccal",
                    definition="used to document posterior dental occlusion on the subject's left side"
                ),
                CodeSystemConcept(
                    code="RL",
                    display="Right Lateral",
                    definition="used to document the dental occlusion from the subject's right side"
                ),
                CodeSystemConcept(
                    code="LL",
                    display="Left Lateral",
                    definition="used to document the dental occlusion from the subject's left side"
                ),
                CodeSystemConcept(
                    code="FV",
                    display="Frontal View",
                    definition="Used to document intraoral view of the subject from the front"
                ),
                CodeSystemConcept(
                    code="IV",
                    display="Inferior View",
                    definition="use IO.IV to show depth of bite (vertical distance) and overjet (horizontal distance) from below. Use EO.IV to show lower border of mandible, nares, infraorbital rim contours, forehead contours from below."
                ),
                CodeSystemConcept(
                    code="SV",
                    display="Superior View",
                    definition="use EO.SV to show forehead, infraorbital rim contour, dorsum of nose, upper lip, chin taken from above"
                ),
                CodeSystemConcept(
                    code="45",
                    display="45º view",
                    definition="used to document extraoral view of the subject taken halfway between frontal and profile views"
                ),
                CodeSystemConcept(
                    code="OV",
                    display="Occlusal View",
                    definition="used to document intraoral views taken to show the subject’s occlusal table either maxillary or mandibular"
                ),
                CodeSystemConcept(
                    code="CS",
                    display="Close-up Smile",
                    definition="extraoral view of the subject’s frontal perioral area showing smile"
                ),
                CodeSystemConcept(
                    code="FW",
                    display="Frown",
                    definition="functional conditions for video or still images."
                ),
                CodeSystemConcept(
                    code="PK",
                    display="Pucker",
                    definition="functional conditions for video or still images."
                ),
                CodeSystemConcept(
                    code="CE",
                    display="Close Eyes",
                    definition="functional conditions for video or still images."
                ),
                CodeSystemConcept(
                    code="RE",
                    display="Raise eyebrows",
                    definition="functional conditions for video or still images."
                ),
                CodeSystemConcept(
                    code="JM",
                    display="Track jaw movements",
                    definition="functional conditions for video or still images."
                ),
                CodeSystemConcept(
                    code="SP",
                    display="Document speech",
                    definition="functional conditions for video or still images."
                ),
                CodeSystemConcept(
                    code="WH",
                    display="Whole Head",
                    definition="used for 3D Photographic (visible light) Image"
                ),
                CodeSystemConcept(
                    code="OC",
                    display="Occlusal Cant",
                    definition="used to document extraoral view showing occlusal cant, may utilize tongue depressor to help visualize the cant"
                ),
                CodeSystemConcept(
                    code="FI",
                    display="Forensic Interest",
                    definition="used to document extraoral view of the subject’s unique features such as tattoos, jewelry, scars"
                ),
                CodeSystemConcept(
                    code="NW",
                    display="Nerve Weakness",
                    definition="Used to document extraoral view of the subject’s signs of nerve abnormalities such as asymmetric muscle function or drooping"
                ),
                CodeSystemConcept(
                    code="AN",
                    display="Anomalies",
                    definition="used to document extraoral view of the subject’s unusual anatomy or pathology"
                ),
                CodeSystemConcept(
                    code="FR",
                    display="Frenum",
                    definition="Used to document intraoral view of the subject’s frenum and may include tooth numbers"
                ),
                CodeSystemConcept(
                    code="PA",
                    display="using Photo Accessory",
                    definition="such as a photo contraster providing a solid background or black mirror. Can be appended to any intraoral (IO) view code as needed"
                ),
                CodeSystemConcept(
                    code="TT",
                    display="Tongue Thrust",
                    definition="Used to document intraoral view of the subject with evidence of tongue thrust"
                ),
                CodeSystemConcept(
                    code="FTO",
                    display="First Time Observation",
                    definition="Patient has just registered with the practice for the first time and has not agreed any treatment yet. The provider collects first time records."
                ),
                CodeSystemConcept(
                    code="OBS",
                    display="Observation",
                    definition="Patient comes back for regular visits. The provider collects observation records."
                ),
                CodeSystemConcept(
                    code="PRT",
                    display="Pretreatment",
                    definition="Images acquired before treatment starts. Only used when the patient and doctor have agreed to start a treatment. This should be treated as Observation above."
                ),
                CodeSystemConcept(
                    code="IN",
                    display="Initial",
                    definition="Patient and provider agreed to start treatment. Records are taken to mark the Baseline for comparison with treatment progress."
                ),
                CodeSystemConcept(
                    code="P",
                    display="Progress",
                    definition="Images taken during treatment."
                ),
                CodeSystemConcept(
                    code="F",
                    display="Final",
                    definition="Image taken at the end of active treatment (after appliance removal, if applicable). Sequence number is not required."
                ),
                CodeSystemConcept(
                    code="FU",
                    display="Follow-Up",
                    definition="refers to Follow-Up time point, generally taken to show post-treatment changes"
                ),
                CodeSystemConcept(
                    code="PST",
                    display="Posttreatment",
                    definition="Image acquired after treatment."
                )
            ]
        )
