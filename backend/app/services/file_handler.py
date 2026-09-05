import os
import shutil
from pathlib import Path
from fastapi import UploadFile

from app.config import settings


class FileHandler:
    """Handle file uploads and storage."""

    ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4"}

    async def save_upload(self, file: UploadFile, meeting_id: str) -> str:
        """
        Save uploaded file to storage directory.

        Args:
            file: Uploaded file
            meeting_id: Unique meeting identifier

        Returns:
            Path to saved file

        Raises:
            ValueError: If file format invalid or size exceeded
        """
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # Create directory for meeting
        meeting_dir = Path(settings.upload_directory) / meeting_id
        meeting_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = meeting_dir / file.filename

        try:
            with open(file_path, "wb") as buffer:
                contents = await file.read()

                # Check file size
                if len(contents) > settings.max_file_size_bytes:
                    file_path.unlink()  # Delete the file
                    raise ValueError(
                        f"File exceeds maximum size of {settings.max_file_size_mb}MB"
                    )

                buffer.write(contents)

            return str(file_path)

        except Exception as e:
            # Clean up on error
            if file_path.exists():
                file_path.unlink()
            raise e

    def delete_meeting(self, meeting_id: str) -> None:
        """Delete meeting files."""
        meeting_dir = Path(settings.upload_directory) / meeting_id
        if meeting_dir.exists():
            shutil.rmtree(meeting_dir)
