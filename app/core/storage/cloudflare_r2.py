import asyncio
from uuid import uuid4

import boto3

from app.core.config import app_settings
from app.core.ingestion.types import RawDocument
from app.core.storage.base import StorageProvider
from app.core.storage.models import StoredDocument


class CloudflareR2StorageProvider(StorageProvider):
    def __init__(self):
        self.bucket = app_settings.r2_bucket_name

        self.client = boto3.client(
            "s3",
            endpoint_url=app_settings.r2_endpoint_url,
            aws_access_key_id=app_settings.r2_access_key_id,
            aws_secret_access_key=app_settings.r2_secret_access_key,
            region_name="auto",
        )

    async def upload_document(
        self,
        raw_document: RawDocument,
    ) -> StoredDocument:
        extension = raw_document.filename.split(".")[-1]

        storage_key = f"uploads/{uuid4()}.{extension}"

        response = await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=storage_key,
            Body=raw_document.content,
            ContentType=raw_document.mime_type,
        )

        return StoredDocument(
            storage_key=storage_key,
            etag=response.get("ETag"),
            size=len(raw_document.content),
        )

    async def download_document(
        self,
        storage_key: str,
    ) -> bytes:
        response = await asyncio.to_thread(
            self.client.get_object,
            Bucket=self.bucket,
            Key=storage_key,
        )

        return response["Body"].read()

    async def delete_document(
        self,
        storage_key: str,
    ) -> None:
        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=self.bucket,
            Key=storage_key,
        )
