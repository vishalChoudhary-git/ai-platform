from abc import ABC, abstractmethod

from app.core.ingestion.types import RawDocument
from app.core.storage.models import StoredDocument


class StorageProvider(ABC):
    @abstractmethod
    async def upload_document(
        self,
        raw_document: RawDocument,
    ) -> StoredDocument:
        raise NotImplementedError

    @abstractmethod
    async def download_document(
        self,
        storage_key: str,
    ) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def delete_document(
        self,
        storage_key: str,
    ) -> None:
        raise NotImplementedError
