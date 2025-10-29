from typing import Optional
import re

def ultranormalize_name(value: Optional[str]) -> Optional[str]:
    """
    Pure-python equivalent of
    https://github.com/pypi/warehouse/blob/691680fa603cce2375505b3b265fe72c0e5ca451/warehouse/migrations/versions/d18d443f89f0_ultranormalize_name_function.py
    """
    if value is None:
        return None

    trans = str.maketrans({
        '.': None,
        '_': None,
        '-': None,
        'l': '1',
        'L': '1',
        'i': '1',
        'I': '1',
        'o': '0',
        'O': '0',
    })
    return value.translate(trans).lower()


_re_collapse = re.compile(r"[._-]+")

def normalize_pep426_name(value: Optional[str]) -> Optional[str]:
    """
    Pure-python equivalent of
    https://github.com/pypi/warehouse/blob/691680fa603cce2375505b3b265fe72c0e5ca451/warehouse/migrations/versions/3af8d0006ba_normalize_runs_of_characters_to_a_.py
    """

    if value is None:
        return None

    return _re_collapse.sub("-", value).lower()
