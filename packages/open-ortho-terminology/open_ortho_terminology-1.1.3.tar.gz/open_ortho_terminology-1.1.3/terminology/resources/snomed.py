""" snomed: a collection of static SNOMED-CT codes.

Used whenever a code is necessary, for various implementations.

"""
from terminology.resources import Code

PREFIX = "SCT"
SYSTEM = "http://snomed.info/sct"


class SnomedCode(Code):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefix = PREFIX
        self.system = SYSTEM


dental_chair = SnomedCode(
    code='706356006',
    contexts=[{'standard': 'FHIR', 'resource': 'Location'}],
    display='Dental examination/treatment chair')

orthod_treatment_perm_class1 = SnomedCode(
    code='3891000',
    display='Comprehensive orthodontic treatment, permanent dentition, for class I malocclusion')

ortho_treatment = SnomedCode(
    code='122452007',
    display='Comprehensive orthodontic treatment')

orthodontist = SnomedCode(
    code='37504001',
    display='Orthodontist')

clinical_staff = SnomedCode(
    code='4162009',
    display='Dental assistant')

admin_staff = SnomedCode(
    code='224608005',
    display='Administrative healthcare staff')

tech_support = SnomedCode(
    code='159324001',
    display='Technical assistant')

EV01 = SnomedCode(
    code='1306623000',
    display="Photographic extraoral image of right half of face with lips relaxed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-01', 'EO.RP.LR.CO'])

EV02 = SnomedCode(
    code='1306622005',
    display="Photographic extraoral image of right half of face with lips relaxed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-02', 'EO.RP.LR.CR'])

EV03 = SnomedCode(
    code='1306621003',
    display="Photographic extraoral image of right half of face with lips closed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-03', 'EO.RP.LC.CO', 'po1'])

EV04 = SnomedCode(
    code='1306620002',
    display="Photographic extraoral image of right half of face with lips closed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-04', 'EO.RP.LC.CR'])

EV05 = SnomedCode(
    code='1306628009',
    display="Photographic extraoral image of right half of face with full smile and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-05', 'EO.RP.FS.CO', 'prs'])

EV06 = SnomedCode(
    code='1306626008',
    display="Photographic extraoral image of right half of face with full smile and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-06', 'EO.RP.FS.CR'])

EV08 = SnomedCode(
    code='1306627004',
    display="Photographic extraoral image of 45 degree view of right half of face with lips relaxed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-08', 'EO.RP.LR.CO.45'])

EV09 = SnomedCode(
    code='1306625007',
    display="Photographic extraoral image of 45 degree view of right half of face with lips relaxed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-09', 'EO.RP.LR.CR.45'])

EV10 = SnomedCode(
    code='1306629001',
    display="Photographic extraoral image of 45 degree view of right half of face with lips closed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-10', 'EO.RP.LC.CO.45'])

EV11 = SnomedCode(
    code='1306631005',
    display="Photographic extraoral image of 45 degree view of right half of face with lips closed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-11', 'EO.RP.LC.CR.45'])

EV12 = SnomedCode(
    code='1306632003',
    display="Photographic extraoral image of 45 degree view of right half of face with full smile and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-12', 'EO.RP.FS.CO.45'])

EV13 = SnomedCode(
    code='1306633008',
    display="Photographic extraoral image of 45 degree view of right half of face with full smile and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-13', 'EO.RP.FS.CR.45'])

EV14 = SnomedCode(
    code='1306634002',
    display="Photographic extraoral image of 45 degree view of right half of face with mandible postured forward (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-14', 'EO.RP.MD.PF.45'])

EV15 = SnomedCode(
    code='1306630006',
    display="Photographic extraoral image of full face with lips relaxed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-15', 'EO.FF.LR.CO'])

EV16 = SnomedCode(
    code='1306663004',
    display="Photographic extraoral image of full face with lips relaxed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-16', 'EO.FF.LR.CR'])

EV17 = SnomedCode(
    code='1306624006',
    display="Photographic extraoral image of full face with lips closed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-17', 'EO.FF.LC.CO', 'pfr'])

EV18 = SnomedCode(
    code='1306662009',
    display="Photographic extraoral image of full face with lips closed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-18', 'EO.FF.LC.CR'])

EV19 = SnomedCode(
    code='1306664005',
    display="Photographic extraoral image of full face with full smile and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-19', 'EO.FF.FS.CO', 'pfs'])

EV20 = SnomedCode(
    code='1306665006',
    display="Photographic extraoral image of full face with full smile and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-20', 'EO.FF.FS.CR'])

EV21 = SnomedCode(
    code='787611004',
    display="Photographic image extraoral with mandible postured forward (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-21', 'EO.FF.MD.PF'])

EV22 = SnomedCode(
    code='1306656004',
    display="Photographic extraoral image of left half of face with lips relaxed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-22', 'EO.LP.LR.CO'])

EV23 = SnomedCode(
    code='1306648002',
    display="Photographic extraoral image of left half of face with lips relaxed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-23', 'EO.LP.LR.CR'])

EV24 = SnomedCode(
    code='1306649005',
    display="Photographic extraoral image of left half of face with lips closed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-24', 'EO.LP.LC.CO'])

EV25 = SnomedCode(
    code='1306650005',
    display="Photographic extraoral image of left half of face with lips closed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-25', 'EO.LP.LC.CR'])

EV26 = SnomedCode(
    code='1306651009',
    display="Photographic extraoral image of left half of face with full smile and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-26', 'EO.LP.FS.CO'])

EV27 = SnomedCode(
    code='1306652002',
    display="Photographic extraoral image of left half of face with full smile and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-27', 'EO.LP.FS.CR'])

EV29 = SnomedCode(
    code='1306644000',
    display="Photographic extraoral image of 45 degree view of left half of face with lips relaxed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-29', 'EO.LP.LR.CO.45'])

EV30 = SnomedCode(
    code='1306645004',
    display="Photographic extraoral image of 45 degree view of left half of face with lips relaxed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-30', 'EO.LP.LR.CR.45'])

EV31 = SnomedCode(
    code='1306646003',
    display="Photographic extraoral image of 45 degree view of left half of face with lips closed and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-31', 'EO.LP.LC.CO.45'])

EV32 = SnomedCode(
    code='1306647007',
    display="Photographic extraoral image of 45 degree view of left half of face with lips closed and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-32', 'EO.LP.LC.CR.45'])

EV33 = SnomedCode(
    code='1306643006',
    display="Photographic extraoral image of 45 degree view of left half of face with full smile and teeth in centric occlusion (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-33', 'EO.LP.FS.CO.45'])

EV34 = SnomedCode(
    code='1306654001',
    display="Photographic extraoral image of 45 degree view of left half of face with full smile and jaws in centric relation (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-34', 'EO.LP.FS.CR.45'])

EV35 = SnomedCode(
    code='1306655000',
    display="Photographic extraoral image of 45 degree view of left half of face with mandible postured forward (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-35', 'EO.LP.MD.PF.45'])

EV36 = SnomedCode(
    code='1306653007',
    display="Photographic extraoral image of inferior view of face (record artifact)",
    contexts=[{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}],
    synonyms=['EV-36', 'EO.OF.IV'])
