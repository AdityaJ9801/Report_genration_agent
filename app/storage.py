"""
Storage abstraction — local filesystem and S3.
Free mode: saves files locally, returns base64 in response.
Paid mode: uploads to S3, returns 7-day presigned download URL.
"""

import base64
import logging
import os
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class StorageBackend:
    """Base storage interface."""

    async def save(
        self, file_bytes: bytes, filename: str, content_type: str
    ) -> dict:
        """Save file and return access info."""
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Save files to local filesystem and return base64-encoded content."""

    def __init__(self):
        self.output_path = Path(settings.REPORT_OUTPUT_PATH)
        self.output_path.mkdir(parents=True, exist_ok=True)

    async def save(
        self, file_bytes: bytes, filename: str, content_type: str
    ) -> dict:
        file_path = self.output_path / filename
        file_path.write_bytes(file_bytes)
        logger.info(f"Saved report to {file_path}")

        content_b64 = base64.b64encode(file_bytes).decode("utf-8")
        return {
            "file_path": str(file_path),
            "content_base64": content_b64,
            "download_url": None,
        }


class S3Storage(StorageBackend):
    """Upload files to S3 and return presigned download URLs."""

    def __init__(self):
        import boto3

        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.S3_REPORTS_BUCKET
        self.expiry = settings.S3_PRESIGNED_EXPIRY

    async def save(
        self, file_bytes: bytes, filename: str, content_type: str
    ) -> dict:
        key = f"reports/{filename}"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
        logger.info(f"Uploaded report to s3://{self.bucket}/{key}")

        download_url = self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=self.expiry,
        )
        return {
            "file_path": f"s3://{self.bucket}/{key}",
            "content_base64": None,
            "download_url": download_url,
        }


def get_storage() -> StorageBackend:
    """Factory: return the configured storage backend."""
    if settings.USE_S3_STORAGE or settings.STORAGE_TYPE == "s3":
        return S3Storage()
    return LocalStorage()
