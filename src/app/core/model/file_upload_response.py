from pydantic import BaseModel, Field
from datetime import datetime


class FileUploadResponse(BaseModel):
    """Response model for file upload operations.

    Represents metadata returned after a successful file upload.

    Attributes:
        filename (str): The name of the stored file (typically a UUID plus extension).
        original_filename (str): The original filename provided by the client.
        file_path (str): The relative or absolute path where the file is stored.
        content_type (str): The MIME type of the uploaded file (e.g. "image/png").
        size (int): Size of the uploaded file in bytes.
        upload_time (datetime): UTC timestamp when the file was uploaded.
    """

    filename: str = Field(
        ...,
        description="The name of the uploaded file",
        example="555e3b8f4-3f2b-4c9e-8f1d-2c3b4e5f6a7b.png",
    )
    original_filename: str = Field(
        ...,
        description="The original name of the uploaded file",
        example="profile_picture.png",
    )
    file_path: str = Field(
        ...,
        description="The path where the file is stored",
        example="storage/photos/555e3b8f4-3f2b-4c9e-8f1d-2c3b4e5f6a7b.png",
    )
    content_type: str = Field(
        ..., description="The MIME type of the uploaded file", example="image/png"
    )
    size: int = Field(
        ..., description="The size of the uploaded file in bytes", example=204800
    )
    upload_time: datetime = Field(
        ...,
        description="The timestamp when the file was uploaded",
        example="2023-10-05T14:48:00.000Z",
    )
