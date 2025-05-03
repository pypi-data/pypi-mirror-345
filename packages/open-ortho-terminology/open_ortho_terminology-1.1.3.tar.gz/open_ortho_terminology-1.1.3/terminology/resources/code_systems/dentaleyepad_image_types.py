""" dentaleyepad: a collection of static codes as defined and found on https://dentaleyepad.de/en/dentaleyepad-image-types/

Used whenever a code is necessary, for various implementations.
"""

from terminology.resources.naming_systems import DentalEyePadNamingSystem
from terminology.resources import Code
from fhir.resources.codesystem import CodeSystem, CodeSystemConcept, CodeSystemConceptDesignation
from datetime import datetime

id = "dentaleyepad-image-types"
def make_code(s):
    return s

class DentalEyePadCodeSystem(CodeSystem):
    
    @classmethod
    def static_url(cls) -> str:
        ns = DentalEyePadNamingSystem()
        return f"{ns.url}/{id}"

    def __init__(self):
        DEP = DentalEyePadNamingSystem()
        
        def convert_to_concept(code: DentaleyepadCode) -> CodeSystemConcept:
            designations = []
            if code.synonyms:
                for synonym in code.synonyms:
                    designations.append(
                        CodeSystemConceptDesignation(
                            value=synonym,
                            use={
                                "system": "http://snomed.info/sct",
                                "code": "900000000000013009",
                                "display": "Synonym"
                            }
                        )
                    )
            return CodeSystemConcept(
                code=code.code,
                display=code.display,
                designation=designations
            )

        concepts = [
            convert_to_concept(value) 
            for name, value in globals().items() 
            if isinstance(value, DentaleyepadCode)
        ]

        super().__init__(
            id="dentaleyepad",
            identifier=DEP.identifier,
            url=self.static_url(),
            version="1.0.0",
            name="DentalEyePadCodeSystem",
            title="DentalEyePad Image Types",
            status="active",
            experimental=False,
            date=datetime.now().date().isoformat(),
            publisher="DentalEyePad",
            description="Collection of codes for dental photography as defined by DentalEyePad",
            caseSensitive=True,
            content="complete",
            concept=concepts
        )

class DentaleyepadCode(Code):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        DentalEyePad = DentalEyePadNamingSystem()
        self.prefix = DentalEyePad.name
        self.system = DentalEyePad.url
        self.contexts = [{'standard': 'DICOM', 'resource': 'ScheduledProtocol'}]

sf0 = DentaleyepadCode(
    code=f"{make_code('sf0')}",
    display='smile front closed',
    synonyms=['sf0', 'smile front closed'])
""" Lächeln von vorne geschlossen """

sf1 = DentaleyepadCode(
    code=f"{make_code('sf1')}",
    display='smile front slightly opened 1',
    synonyms=['sf1', 'smile front slightly opened 1'])
""" lächeln von vorne leicht geöffnet 1 """

sf2 = DentaleyepadCode(
    code=f"{make_code('sf2')}",
    display='smile front slightly opened 2',
    synonyms=['sf2', 'smile front slightly opened 2'])
""" Lächeln von vorne leicht geöffnet 2 """

sf3 = DentaleyepadCode(
    code=f"{make_code('sf3')}",
    display='smile front opened 3',
    synonyms=['sf3', 'smile front opened 3'])
""" Lächeln von vorne geöffnet 3 """

sf4 = DentaleyepadCode(
    code=f"{make_code('sf4')}",
    display='smile front opened 4',
    synonyms=['sf4', 'smile front opened 4'])
""" Lächeln von vorne geöffnet 4 """

sf5 = DentaleyepadCode(
    code=f"{make_code('sf5')}",
    display='smile front gap 5',
    synonyms=['sf5', 'smile front gap 5'])
""" Lächeln von vorne geöffnet 5 """

src = DentaleyepadCode(
    code=f"{make_code('src')}",
    display='smile right closed',
    synonyms=['src', 'smile right closed'])
""" Lächeln (geschlossen) von rechts """

srr = DentaleyepadCode(
    code=f"{make_code('srr')}",
    display='smile right in repose',
    synonyms=['srr', 'smile right in repose'])
""" entspanntes Lächeln von rechts """

sro = DentaleyepadCode(
    code=f"{make_code('sro')}",
    display='smile right open',
    synonyms=['sro', 'smile right open'])
""" offenes Lächeln von rechts """

slc = DentaleyepadCode(
    code=f"{make_code('slc')}",
    display='smile left closed',
    synonyms=['slc', 'smile left closed'])
""" Lächeln (geschlossen) von links """

slr = DentaleyepadCode(
    code=f"{make_code('slr')}",
    display='smile left in repose',
    synonyms=['slr', 'smile left in repose'])
""" entspanntes Lächeln von links """

slo = DentaleyepadCode(
    code=f"{make_code('slo')}",
    display='smile left open',
    synonyms=['slo', 'smile left open'])
""" offenes Lächeln von links """

frc = DentaleyepadCode(
    code=f"{make_code('frc')}",
    display='front retracted closed',
    synonyms=['frc', 'front retracted closed'])
""" Frontaufnahme mit Wangenhalter geschlossen """

frg = DentaleyepadCode(
    code=f"{make_code('frg')}",
    display='front retracted with gap',
    synonyms=['frg', 'front retracted with gap'])
""" Front geöffnet mit Wangenhalter """

oua = DentaleyepadCode(
    code=f"{make_code('oua')}",
    display='occlusal upper arch mirrored',
    synonyms=['oua', 'occlusal upper arch mirrored'])
""" okklusal Oberkiefer gespiegelt """

ola = DentaleyepadCode(
    code=f"{make_code('ola')}",
    display='occlusal lower arch mirrored',
    synonyms=['ola', 'occlusal lower arch mirrored'])
""" okklusal Unterkiefer gespiegelt """

blr = DentaleyepadCode(
    code=f"{make_code('blr')}",
    display='buccal left retracted',
    synonyms=['blr', 'buccal left retracted'])
""" bukkal links abgehalten """

brr = DentaleyepadCode(
    code=f"{make_code('brr')}",
    display='buccal right retracted',
    synonyms=['brr', 'buccal right retracted'])
""" bukkal rechts abgehalten """

bls = DentaleyepadCode(
    code=f"{make_code('bls')}",
    display='buccal left gap retracted',
    synonyms=['bls', 'buccal left gap retracted'])
""" bukkal links geöffnet abgehalten """

brs = DentaleyepadCode(
    code=f"{make_code('brs')}",
    display='buccal right gap retracted',
    synonyms=['brs', 'buccal right gap retracted'])
""" bukkal rechts geöffnet abgehalten """

blc = DentaleyepadCode(
    code=f"{make_code('blc')}",
    display='buccal left closed mirrored',
    synonyms=['blc', 'buccal left closed mirrored'])
""" bukkal links geschlossen gespiegelt """

brc = DentaleyepadCode(
    code=f"{make_code('brc')}",
    display='buccal right closed mirrored',
    synonyms=['brc', 'buccal right closed mirrored'])
""" bukkal rechts geschlossen gespiegelt """

blg = DentaleyepadCode(
    code=f"{make_code('blg')}",
    display='buccal left gap mirrored',
    synonyms=['blg', 'buccal left gap mirrored'])
""" bukkal links geöffnet gespiegelt """

brg = DentaleyepadCode(
    code=f"{make_code('brg')}",
    display='buccal right gap mirrored',
    synonyms=['brg', 'buccal right gap mirrored'])
""" bukkal rechts geöffnet gespiegelt """

org = DentaleyepadCode(
    code=f"{make_code('org')}",
    display='oblique right gap',
    synonyms=['org', 'oblique right gap'])
""" schräg von rechts geöffnet """

olg = DentaleyepadCode(
    code=f"{make_code('olg')}",
    display='oblique left gap',
    synonyms=['olg', 'oblique left gap'])
""" schräg von links geöffnet """

orc = DentaleyepadCode(
    code=f"{make_code('orc')}",
    display='oblique right closed',
    synonyms=['orc', 'oblique right closed'])
""" schräg von rechts geschlossen """

olc = DentaleyepadCode(
    code=f"{make_code('olc')}",
    display='oblique left closed',
    synonyms=['olc', 'oblique left closed'])
""" schräg von links geschlossen """

_4uf = DentaleyepadCode(
    code=f"{make_code('4uf')}",
    display='upper jaw front',
    synonyms=['4uf', 'upper jaw front'])
""" Oberkiefer Front """

_4ul = DentaleyepadCode(
    code=f"{make_code('4ul')}",
    display='upper jaw anterior oblique left',
    synonyms=['4ul', 'upper jaw anterior oblique left'])
""" Oberkiefer schräg links """

_4ur = DentaleyepadCode(
    code=f"{make_code('4ur')}",
    display='upper jaw anterior oblique right',
    synonyms=['4ur', 'upper jaw anterior oblique right'])
""" Oberkiefer schräg rechts """

_4lf = DentaleyepadCode(
    code=f"{make_code('4lf')}",
    display='lower jaw front',
    synonyms=['4lf', 'lower jaw front'])
""" Unterkiefer Front """

_4ll = DentaleyepadCode(
    code=f"{make_code('4ll')}",
    display='lower jaw anterior oblique left',
    synonyms=['4ll', 'lower jaw anterior oblique left'])
""" Unterkiefer schräg links """

_4lr = DentaleyepadCode(
    code=f"{make_code('4lr')}",
    display='lower jaw anterior oblique right',
    synonyms=['4lr', 'lower jaw anterior oblique right'])
""" Unterkiefer schräg rechts """

_2uf = DentaleyepadCode(
    code=f"{make_code('2uf')}",
    display='detail upper jaw front',
    synonyms=['2uf', 'detail upper jaw front'])
""" Oberkiefer Front Detail """

_2ur = DentaleyepadCode(
    code=f"{make_code('2ur')}",
    display='detail upper jaw oblique right',
    synonyms=['2ur', 'detail upper jaw oblique right'])
""" Detail Oberkiefer schräg rechts """

_2ul = DentaleyepadCode(
    code=f"{make_code('2ul')}",
    display='detail upper jaw front',
    synonyms=['2ul', 'detail upper jaw front'])
""" Oberkiefer Front Detail """

pfr = DentaleyepadCode(
    code=f"{make_code('pfr')}",
    display='portrait front in repose',
    synonyms=['pfr', 'portrait front in repose'])
""" Portrait von vorne entspannt """

pfs = DentaleyepadCode(
    code=f"{make_code('pfs')}",
    display='portrait front smile',
    synonyms=['pfs', 'portrait front smile'])
""" Portrait von vorne lächelnd """

pfo = DentaleyepadCode(
    code=f"{make_code('pfo')}",
    display='portrait front own smile',
    synonyms=['pfo', 'portrait front own smile'])
""" Portrait von vorne offenes Lächeln """

po1 = DentaleyepadCode(
    code=f"{make_code('po1')}",
    display='portrait oblique right in repose',
    synonyms=['po1', 'portrait oblique right in repose'])
""" Portrait von schräg rechts entspannt """

po2 = DentaleyepadCode(
    code=f"{make_code('po2')}",
    display='portrait oblique right smile',
    synonyms=['po2', 'portrait oblique right smile'])
""" Portrait von schräg rechts lächelnd """

po5 = DentaleyepadCode(
    code=f"{make_code('po5')}",
    display='portrait oblique right open smile',
    synonyms=['po5', 'portrait oblique right open smile'])
""" Portrait von schräg rechts offenes Lächeln """

prr = DentaleyepadCode(
    code=f"{make_code('prr')}",
    display='profile right in repose',
    synonyms=['prr', 'profile right in repose'])
""" Profil von rechts entspannt """

prs = DentaleyepadCode(
    code=f"{make_code('prs')}",
    display='profile right smile',
    synonyms=['prs', 'profile right smile'])
""" Profil von rechts lächelnd """

pro = DentaleyepadCode(
    code=f"{make_code('pro')}",
    display='profile right open smile',
    synonyms=['pro', 'profile right open smile'])
""" Profil von rechts offenes Lächeln """

po3 = DentaleyepadCode(
    code=f"{make_code('po3')}",
    display='portrait oblique left in repose',
    synonyms=['po3', 'portrait oblique left in repose'])
""" Portrait von schräg links entspannt """

po4 = DentaleyepadCode(
    code=f"{make_code('po4')}",
    display='portrait oblique left smile',
    synonyms=['po4', 'portrait oblique left smile'])
""" Portrait von schräg links lächelnd """

po6 = DentaleyepadCode(
    code=f"{make_code('po6')}",
    display='portrait oblique right open smile',
    synonyms=['po6', 'portrait oblique right open smile'])
""" Portrait von schräg rechts offenes Lächeln """

plr = DentaleyepadCode(
    code=f"{make_code('plr')}",
    display='profile left in repose',
    synonyms=['plr', 'profile left in repose'])
""" Profil von links entspannt """

pls = DentaleyepadCode(
    code=f"{make_code('pls')}",
    display='profile left smile',
    synonyms=['pls', 'profile left smile'])
""" Profil von links lächelnd """

plo = DentaleyepadCode(
    code=f"{make_code('plo')}",
    display='profile left open smile',
    synonyms=['plo', 'profile left open smile'])
""" Profil von links offenes Lächeln """

fob = DentaleyepadCode(
    code=f"{make_code('fob')}",
    display='front oblique from below',
    synonyms=['fob', 'front oblique from below'])
""" Front schräg von unten """

s12 = DentaleyepadCode(
    code=f"{make_code('s12')}",
    display='smile from 12 o‘clock',
    synonyms=['s12', 'smile from 12 o‘clock'])
""" Lächeln von 12 Uhr """

u90 = DentaleyepadCode(
    code=f"{make_code('u90')}",
    display='upper arch from 90°',
    synonyms=['u90', 'upper arch from 90°'])
""" Oberkiefer aus 90° """

ir9 = DentaleyepadCode(
    code=f"{make_code('ir9')}",
    display='incisors right from 90°',
    synonyms=['ir9', 'incisors right from 90°'])
""" Front seitlich rechts von 90° """

il9 = DentaleyepadCode(
    code=f"{make_code('il9')}",
    display='incisors left from 90°',
    synonyms=['il9', 'incisors left from 90°'])
""" Front seitlich links von 90° """

ljd = DentaleyepadCode(
    code=f"{make_code('ljd')}",
    display='lower jaw direkt',
    synonyms=['ljd', 'lower jaw direkt'])
""" Unterkiefer direkt """

mls = DentaleyepadCode(
    code=f"{make_code('mls')}",
    display='model left side',
    synonyms=['mls', 'model left side'])
""" Modell von links """

mmm = DentaleyepadCode(
    code=f"{make_code('mmm')}",
    display='model maxilla and mandibular',
    synonyms=['mmm', 'model maxilla and mandibular'])
""" Modell Ober- und Unterkiefer """

muj = DentaleyepadCode(
    code=f"{make_code('muj')}",
    display='model upper jaw',
    synonyms=['muj', 'model upper jaw'])
""" Modell Oberkiefer """

mlj = DentaleyepadCode(
    code=f"{make_code('mlj')}",
    display='model lower jaw',
    synonyms=['mlj', 'model lower jaw'])
""" Modell Unterkiefer """

mfs = DentaleyepadCode(
    code=f"{make_code('mfs')}",
    display='model front side',
    synonyms=['mfs', 'model front side'])
""" Modell Vorderseite """

mbs = DentaleyepadCode(
    code=f"{make_code('mbs')}",
    display='model back side',
    synonyms=['mbs', 'model back side'])
""" Modell Rückseite """
