"""
Superset of built-in `mimetypes` library.
"""

from mimetypes import *
from typing import Optional

# Make all 154 mime types available in this module
for _v in types_map.values():
    globals()[_v.replace("/", "_").upper()] = _v

def lookup(media_type: str) -> Optional[str]:
    """Lookup for a media type"""
    def guess_type_from_map(_media_type: str) -> Optional[str]:
        return types_map[_media_type.lower()] if _media_type.startswith(".") else types_map[f".{_media_type.lower()}"]

    mimetype: Optional[str] = None
    operations: list = [guess_type_from_map, guess_type, guess_file_type]

    while (not mimetype) and operations and (operation := operations.pop()):
        result = operation(media_type)
        mimetype = result[0] if (type(result) in [tuple, list]) else result

    return mimetype
