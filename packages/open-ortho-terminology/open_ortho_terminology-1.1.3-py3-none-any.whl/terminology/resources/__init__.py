""" Resources for the terminology module.

This module contains classes that represent resources used to define terminologies, value sets, code systems, and codes.

"""
import json
from fhir.resources.coding import Coding

class Code:
    """ A terminology code.
    
    prefix: 

    system:

    code:

    display:

    synonyms:

    expansion: This refers to the process of expanding a value set, which means fully enumerating the set of codes that it contains. This is done to ensure that a value set is clearly and comprehensively defined, making it useful for validation, selection, and display. The term comes from FHIR.

    compose: This term is used within the definition of a value set, where the "compose" element specifies the set of codes that are included or excluded from the value set based on filters and value set inclusions. The term comes from FHIR.

    contexts: defines which resource of which standard these codes are used for. a list of dicts() containing the keys: 'standard' and 'resource'
    
    """

    def __init__(self, **kwargs):
        self.prefix = None
        self.system = kwargs.get('system')
        self.code = kwargs.get('code')
        self.display = kwargs.get('display')
        self.synonyms = kwargs.get('synonyms')
        self.compose = kwargs.get('compose')
        self.expansion = kwargs.get('expansion')
        self.contexts = kwargs.get('contexts')

    def to_json(self):
        return json.dumps({
            'system': self.system,
            'code': self.code,
            'full_code': self.full_code,
            'display': self.display,
            'synonyms': self.synonyms
        }, indent=4)

    def to_fhir(self) -> Coding:
        return Coding(
            system=self.system,
            code=self.full_code,
            display=self.display
        )


    @property
    def full_code(self):
        """ The code with the prefix. E.g. 'OPOR-3412' """
        if self.prefix:
            return f"{self.prefix}-{self.code}"
        else:
            return self.code
