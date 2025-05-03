from fhir.resources.namingsystem import NamingSystem
from fhir.resources.identifier import Identifier
from terminology.constants import NAMING_SYSTEM_UIDS

class MedocoHealthNamingSystem(NamingSystem):
    def __init__(self):
        super().__init__(
            url="http://terminology.medoco.health/fhir",
            name="MDOC",
            title="medoco Health Naming System",
            description="""
## medoco Health Naming System by Dr. Marco Rosa 

A custom set of codes used by various medoco Health products, as reccommended by Dr. Marco Rosa.
""",
            status="draft",
            kind="codesystem",
            date="2025-01-01",
            publisher="medoco Health",
            responsible="medoco Health",
            uniqueId=[
                {
                    "type": "uri",
                    "value": "http://terminology.medoco.health/fhir",
                    "preferred": True
                },
                {
                    "type": "oid",
                    "value": NAMING_SYSTEM_UIDS["medoco-health"],
                    "preferred": False
                }
            ]
        )

class OpenOrthoNamingSystem(NamingSystem):
    def __init__(self):
        super().__init__(
            url="http://terminology.open-ortho.org/fhir",
            name="OpenOrtho",
            title="Open-Ortho",
            identifier=[Identifier(
                system="dicom",
                value="99OPOR"
            )],
            description="""
## OpenOrtho Naming System

A set of codes required to represent dental and orthodontic concepts for interoperability purposes, which are not yet available in other standard code systems.
""",
            status="draft",
            kind="codesystem",
            date="2025-01-01",
            publisher="OpenOrtho",
            responsible="OpenOrtho",
            contact=[
                {
                    "name": "Open-Ortho",
                    "telecom": [
                        {
                            "system": "url",
                            "value": "https://open-ortho.org"
                        }
                    ]
                }
            ],
            uniqueId=[
                {
                    "type": "uri",
                    "value": "http://terminology.open-ortho.org/fhir",
                    "preferred": False
                },
                {
                    "type": "oid",
                    "value": NAMING_SYSTEM_UIDS["open-ortho"],
                    "preferred": False
                },
                {
                    "type": "dicom",
                    "value": "99OPOR",
                    "preferred": True
                }
            ]
        )

class DentalEyePadNamingSystem(NamingSystem):
    def __init__(self):
        super().__init__(
            url="https://dentaleyepad.de/en",
            name="DentalEyePad",
            identifier=[Identifier(
                system="dicom",
                value="99DEYE"
            )],
            title="Dental Eyepad Naming System",
            description="""
# dentaleyepad image types

The dentaleyepad knows which images are to be taken and makes all the necessary image settings automatically. The photo assistant automatically displays the image types in the correct order.

This eliminates tedious intermediate steps such as connecting the camera, assigning patients and defining the image types.
""",
            status="draft",
            kind="codesystem",
            date="2024-12-30",
            publisher="doctorseyes GmbH",
            responsible="info@doctorseyes.de",
            uniqueId=[
                {
                    "type": "uri",
                    "value": "https://dentaleyepad.de/en",
                    "preferred": True
                },
                {
                    "type": "oid",
                    "value": NAMING_SYSTEM_UIDS["dental-eye-pad"],
                    "preferred": False
                }
            ]
        )