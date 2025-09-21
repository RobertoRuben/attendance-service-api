from enum import Enum


class StorageType(Enum):
    """Enumeration of available storage types."""

    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"
