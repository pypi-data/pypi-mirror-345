""" Code Systems pertaining to specific Naming Systems.

Import method as make_code to change coding algorithm. Should acutally never be changed.
"""
from datetime import datetime, timezone
from fhir.resources.meta import Meta

def make_numeric_code(s):
    """
    Convert a string of ASCII characters to a single string of their equivalent integer values concatenated together.

    Args:
    s (str): A string to convert.

    Returns:
    str: A string consisting of the ASCII integer values concatenated together without any spaces.
    """
    # Convert each character to its ASCII integer, then to a string, and concatenate
    return ''.join(str(ord(char)) for char in s)

def leave_code_as_is(s):
    """ Leave codes as is. """
    return s


def add_meta_to_resource(resource):
    """ Add metadata to a resource. """
    resource.meta = Meta(
        lastUpdated=datetime.now(timezone.utc).isoformat(), # For some reason, doesn't work, return cannot serialize datetime
    )
    return resource