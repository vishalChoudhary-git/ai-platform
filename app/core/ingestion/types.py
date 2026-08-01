from dataclasses import dataclass
from typing import Any

from app.features.documents.models.enums import DocumentSource


@dataclass(slots=True)  # Instead of storing attributes in a dictionary, Python creates fixed slots.
class RawDocument:
    content: bytes
    filename: str
    mime_type: str
    source: DocumentSource
    metadata: dict[str, Any]
