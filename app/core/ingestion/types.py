from dataclasses import dataclass
from typing import Any


@dataclass
class RawDocument:
    content: bytes
    filename: str
    mime_type: str
    source: str
    metadata: dict[str, Any]
