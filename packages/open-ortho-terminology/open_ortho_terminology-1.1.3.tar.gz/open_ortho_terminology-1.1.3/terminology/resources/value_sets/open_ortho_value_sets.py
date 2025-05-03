from fhir.resources.valueset import ValueSet
from terminology.resources.code_systems.extraoral_2d_photographic_scheduled_protocol import Extraoral2DPhotographicScheduledProtocolCodeSystem

class OrthodonticPhotographViewsValueSet(ValueSet):
    """ Set of codes allowed for orthodontic photographs to be used in DICOM's ScheduledProtocol attribute. """
    @classmethod
    def static_url(cls) -> str:
        return "http://terminology.open-ortho.org/fhir/ValueSet/OrthodonticPhotographViews"

    def __init__(self):
        url=self.static_url()
        super().__init__(
            url=url,
            identifier=[
                {
                    "system": "urn:ietf:rfc:3986",
                    "value": "urn:oid:1.2.840.10008.2.16.4"
                }
            ],
            version="0.1.0",
            name="Orthodontic Photographic Views",
            title="Orthodontic Photographic Views",
            status="active",
            experimental=False,
            date="2024-12-29",
            publisher="open-ortho",
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
            description="A set of codes that describe Orhodontic Photographic Views for DICOM ",
            compose={
                "include": [
                    {
                        "system": Extraoral2DPhotographicScheduledProtocolCodeSystem().url,
                    },
                    {
                        "system": "http://snomed.info/sct",
                        "filter": [
                            {
                                "property": "concept",
                                "op": "is-a",
                                "value": "723394009"
                            }
                        ]
                    }
                ]
            }
        )