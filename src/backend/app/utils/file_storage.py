"""File storage utilities for resume uploads."""
import uuid
from pathlib import Path
from typing import BinaryIO

import aiofiles
from fastapi import UploadFile

from app.config import settings


class FileStorage:
    """Handles file storage operations for resume files."""

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename while preserving extension.

        Args:
            original_filename: Original file name.

        Returns:
            Unique filename with UUID prefix.
        """
        file_path = Path(original_filename)
        unique_id = uuid.uuid4().hex[:12]
        return f"{unique_id}_{file_path.stem}{file_path.suffix}"

    @staticmethod
    async def save_upload_file(
        file: UploadFile,
        destination_dir: Path,
        filename: str,
    ) -> Path:
        """Save uploaded file to disk asynchronously.

        Args:
            file: The uploaded file.
            destination_dir: Directory to save file to.
            filename: Name to save file as.

        Returns:
            Path to saved file.
        """
        # Ensure destination directory exists
        destination_dir.mkdir(parents=True, exist_ok=True)

        # Full path to save file
        file_path = destination_dir / filename

        # Save file asynchronously
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        return file_path

    @staticmethod
    async def delete_file(file_path: Path) -> None:
        """Delete a file from disk.

        Args:
            file_path: Path to file to delete.
        """
        if file_path.exists():
            file_path.unlink()

    @staticmethod
    def get_upload_directory(user_id: str) -> Path:
        """Get upload directory for a specific user.

        Args:
            user_id: UUID of the user.

        Returns:
            Path to user's upload directory.
        """
        # Create user-specific directory
        upload_dir = Path(settings.upload_dir) / user_id / "resumes"
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir
