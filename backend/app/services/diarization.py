
import re
from pathlib import Path

from app.config import settings


class DiarizationService:
    """Handle speaker diarization using pyannote.audio."""

    def __init__(self):
        # Do not load heavy ML libraries during application startup.
        self.device = None
        self.pipeline = None
        self._initialization_attempted = False

    def _initialize_pipeline(self):
        """Load the diarization model only when required."""

        if self._initialization_attempted:
            return

        # Prevent repeated initialization attempts in this process.
        self._initialization_attempted = True

        try:
            import torch
            from pyannote.audio import Pipeline

            self.device = "cuda" if torch.cuda.is_available() else "cpu"

            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=settings.hugging_face_token,
            )

            if self.pipeline is None:
                raise RuntimeError("Could not load the diarization pipeline.")

            self.pipeline.to(torch.device(self.device))

            print(f"✅ Diarization model loaded successfully on {self.device}.")

        except Exception as e:
            print(f"Warning: Could not load diarization model: {e}")
            self.pipeline = None

    async def diarize(self, file_path: str) -> dict:
        """
        Perform speaker diarization on an audio file.

        Args:
            file_path: Path to the audio file.

        Returns:
            Dictionary containing speaker segments.
        """

        try:
            # Validate file existence.
            if not Path(file_path).exists():
                raise ValueError(f"File not found: {file_path}")

            # Load the model on the first diarization request.
            if not self._initialization_attempted:
                self._initialize_pipeline()

            # Use fallback if model initialization failed.
            if self.pipeline is None:
                return self._get_fallback_diarization()

            # Perform speaker diarization.
            diarization = self.pipeline(file_path)

            segments = []

            for turn, _, speaker in diarization.itertracks(
                yield_label=True
            ):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": self._normalize_speaker_label(speaker),
                })

            return {
                "status": "success",
                "segments": segments,
                "num_speakers": len(
                    set(segment["speaker"] for segment in segments)
                ),
            }

        except Exception as e:
            return self._get_fallback_diarization_error(str(e))

    @staticmethod
    def _normalize_speaker_label(label: str) -> str:
        """Convert speaker labels into a generic format."""

        match = re.search(
            r"(?:spk|speaker)\s*[:_-]?\s*(\d+)",
            str(label),
            re.IGNORECASE,
        )

        if match:
            number = int(match.group(1))

            if ":" in match.group(0) or number == 0:
                number += 1

            return f"Speaker {number}"

        try:
            speaker_num = int(label.split("_")[-1]) + 1
            return f"Speaker {speaker_num}"

        except (ValueError, IndexError):
            return label

    @staticmethod
    def _get_fallback_diarization() -> dict:
        """Return fallback when the model is unavailable."""

        return {
            "status": "warning",
            "message": "Diarization model not available. Using fallback.",
            "segments": [],
            "num_speakers": 1,
        }

    @staticmethod
    def _get_fallback_diarization_error(error: str) -> dict:
        """Return an error response."""

        return {
            "status": "error",
            "error": error,
            "segments": [],
            "num_speakers": 0,
        }


# Create the service without loading the ML model at startup.
diarization_service = DiarizationService()
