from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StoredDocument:
    """
    Result returned after storing a document.
    """

    storage_key: str

    etag: str | None = None

    size: int | None = None
