import torch
import re
from pathlib import Path
from pyannote.audio import Pipeline

from app.config import settings


class DiarizationService:
    """Handle speaker diarization using pyannote.audio."""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline = None
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initialize the diarization pipeline."""
        try:
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=settings.hugging_face_token,
            )
            self.pipeline.to(torch.device(self.device))
        except Exception as e:
            print(f"Warning: Could not load diarization model: {e}")
            self.pipeline = None

    async def diarize(self, file_path: str) -> dict:
        """
        Perform speaker diarization on audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with speaker segments

        Raises:
            ValueError: If diarization fails
        """
        try:
            # Validate file exists
            if not Path(file_path).exists():
                raise ValueError(f"File not found: {file_path}")

            # Check if pipeline loaded
            if self.pipeline is None:
                return self._get_fallback_diarization()

            # Run diarization
            diarization = self.pipeline(file_path)

            # Extract speaker segments
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": self._normalize_speaker_label(speaker),
                })

            return {
                "status": "success",
                "segments": segments,
                "num_speakers": len(set(s["speaker"] for s in segments)),
            }

        except Exception as e:
            return self._get_fallback_diarization_error(str(e))

    @staticmethod
    def _normalize_speaker_label(label: str) -> str:
        """Convert speaker label to generic format."""
        match = re.search(
            r"(?:spk|speaker)\s*[:_-]?\s*(\d+)", str(label), re.IGNORECASE
        )
        if match:
            number = int(match.group(1))
            if ":" in match.group(0) or number == 0:
                number += 1
            return f"Speaker {number}"

        # Extract speaker number if available
        try:
            speaker_num = int(label.split("_")[-1]) + 1
            return f"Speaker {speaker_num}"
        except (ValueError, IndexError):
            return label

    @staticmethod
    def _get_fallback_diarization() -> dict:
        """Return fallback when model not available."""
        return {
            "status": "warning",
            "message": "Diarization model not available. Using fallback.",
            "segments": [],
            "num_speakers": 1,
        }

    @staticmethod
    def _get_fallback_diarization_error(error: str) -> dict:
        """Return error response."""
        return {
            "status": "error",
            "error": error,
            "segments": [],
            "num_speakers": 0,
        }


# Create singleton instance
diarization_service = DiarizationService()
