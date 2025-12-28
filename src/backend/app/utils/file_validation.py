"""File validation utilities for resume uploads."""
from pathlib import Path
from typing import BinaryIO

from fastapi import HTTPException, UploadFile, status


class FileValidator:
    """Validates uploaded files for resume processing."""

    # Allowed file types
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    # File size limits (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    # File signatures (magic numbers)
    FILE_SIGNATURES = {
        b"%PDF": "pdf",  # PDF signature
        b"PK\x03\x04": "docx",  # DOCX signature (ZIP format)
    }

    @classmethod
    async def validate_resume_file(cls, file: UploadFile) -> None:
        """Validate resume file for upload.

        Args:
            file: The uploaded file to validate.

        Raises:
            HTTPException: If validation fails.
        """
        # Check if file exists
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided",
            )

        # Check filename
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided",
            )

        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}",
            )

        # Validate MIME type
        if file.content_type not in cls.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type: {file.content_type}",
            )

        # Read first few bytes to check file signature
        content_start = await file.read(8)
        await file.seek(0)  # Reset file pointer

        # Validate file signature
        is_valid_signature = False
        for signature, file_type in cls.FILE_SIGNATURES.items():
            if content_start.startswith(signature):
                is_valid_signature = True
                # Verify signature matches extension
                if file_ext == f".{file_type}":
                    break
        else:
            if not is_valid_signature:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File signature does not match file type",
                )

        # Validate file size by reading content
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)  # Reset file pointer

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        if file_size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {cls.MAX_FILE_SIZE / (1024 * 1024):.0f}MB",
            )

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks.

        Args:
            filename: Original filename.

        Returns:
            Sanitized filename.
        """
        # Get just the filename, remove any path components
        filename = Path(filename).name

        # Remove any characters that aren't alphanumeric, dash, underscore, or dot
        safe_chars = []
        for char in filename:
            if char.isalnum() or char in "._-":
                safe_chars.append(char)
            else:
                safe_chars.append("_")

        return "".join(safe_chars)
