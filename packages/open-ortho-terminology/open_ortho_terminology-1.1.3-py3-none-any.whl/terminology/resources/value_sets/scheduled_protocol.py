from datetime import datetime
from fhir.resources.valueset import ValueSet
from terminology.resources.naming_systems import OpenOrthoNamingSystem
from terminology.resources.code_systems.extraoral_2d_photographic_scheduled_protocol import Extraoral2DPhotographicScheduledProtocolCodeSystem
from terminology.resources.code_systems.intraoral_2d_photographic_scheduled_protocol import Intraoral2DPhotographicScheduledProtocolCodeSystem
from terminology.resources.code_systems.intraoral_3d_visible_light_scheduled_protocol import Intraoral3DVisibleLightScheduledProtocolCodeSystem
from terminology.resources.code_systems.extraoral_3d_visible_light_scheduled_protocol import Extraoral3DVisibleLightScheduledProtocolCodeSystem
from terminology.constants import VALUE_SET_UIDS


id = "scheduled-protocol"


class ScheduledProtocolValueSet(ValueSet):
    """ Set of codes allowed for orthodontic photographs to be used in DICOM's ScheduledProtocol attribute. """
    @classmethod
    def static_url(cls) -> str:
        ns = OpenOrthoNamingSystem()
        return f"{ns.url}/{id}"

    def __init__(self):
        url = self.static_url()
        OPOR = OpenOrthoNamingSystem()
        super().__init__(
            url=url,
            identifier=[
                {
                    "system": "urn:ietf:rfc:3986",
                    "value": f"urn:oid:{VALUE_SET_UIDS[id]}"
                }
            ],
            version="0.1.0",
            name="Orthodontic2Dand3DVisibleLightScheduledProtocols",
            title="Orthodontic 2D and 3D Visible Light Scheduled Protocols",
            status="active",
            experimental=False,
            date=datetime.now().date().isoformat(),
            publisher=OPOR.publisher,
            contact=[OPOR.contact[0]],
            description="Scheduled protocols for orthodontic photographs and intraoral scans according to ADA-1100.",
            compose={
                "include": [
                    {"system": Intraoral2DPhotographicScheduledProtocolCodeSystem().url,
                     },
                    {"system": Extraoral2DPhotographicScheduledProtocolCodeSystem().url,
                     },
                    {"system": Intraoral3DVisibleLightScheduledProtocolCodeSystem().url,
                     },
                    {"system": Extraoral3DVisibleLightScheduledProtocolCodeSystem().url,
                     },
                ]
            }
        )
