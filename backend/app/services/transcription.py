
from pathlib import Path
import asyncio
import re
import soundfile as sf
from google import genai

from app.config import settings


class TranscriptionService:
    """Handle audio transcription using Gemini 3.5 Transcribe."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_transcribe_model

    @staticmethod
    def _is_retryable_error(error: Exception) -> bool:
        """Identify temporary Gemini service errors."""

        status_values = [
            getattr(error, "code", None),
            getattr(error, "status_code", None),
        ]

        retryable_statuses = {"500", "502", "503", "504"}

        if any(str(status) in retryable_statuses for status in status_values):
            return True

        message = str(error).lower()

        retryable_messages = (
            "503",
            "500",
            "502",
            "504",
            "service_unavailable",
            "high demand",
            "temporarily unavailable",
            "internal server error",
            "bad gateway",
            "gateway timeout",
        )

        return any(term in message for term in retryable_messages)

    async def _create_transcription_with_retry(self, audio_file):
        """Call Gemini with retries for temporary service failures."""

        retry_delays = [2, 4, 8]

        for attempt in range(len(retry_delays) + 1):
            try:
                return await asyncio.to_thread(
                    self.client.interactions.create,
                    model=self.model,
                    input=[{
                        "type": "audio",
                        "uri": audio_file.uri,
                        "mime_type": audio_file.mime_type,
                    }],
                    generation_config={
                        "transcription_config": {
                            "mode": {
                                "type": "verbatim",
                                "diarization_mode": "speaker",
                                "timestamp_granularities": ["word"],
                            }
                        }
                    },
                )

            except Exception as error:
                if (
                    not self._is_retryable_error(error)
                    or attempt == len(retry_delays)
                ):
                    raise

                delay = retry_delays[attempt]

                print(
                    f"Gemini transcription temporarily unavailable. "
                    f"Attempt {attempt + 1}/4 failed. "
                    f"Retrying in {delay} seconds. Error: {error}"
                )

                await asyncio.sleep(delay)

        raise RuntimeError("Gemini transcription failed after retries.")

    async def transcribe(self, file_path: str) -> dict:
        """
        Transcribe audio using Gemini 3.5 Transcribe.

        Returns:
            Dictionary containing:
            - status
            - text
            - segments
            - language
        """

        try:
            path = Path(file_path)

            if not path.exists():
                raise ValueError(f"File not found: {file_path}")

            # Upload audio using Gemini Files API.
            audio_file = await asyncio.to_thread(
                self.client.files.upload,
                file=str(path),
            )

            # Transcription with automatic retries.
            print(f"Starting Gemini transcription using {self.model}...")

            response = await self._create_transcription_with_retry(
                audio_file
            )

            transcript_text = (
                getattr(response, "output_text", None)
                or getattr(response, "text", None)
                or ""
            ).strip()

            if not transcript_text:
                raise ValueError("Gemini returned an empty transcription.")

            segments = self._extract_word_segments(response)

            # Compatibility with older SDK response structures.
            if not segments:
                for candidate in getattr(response, "candidates", []) or []:
                    content = getattr(candidate, "content", None)

                    for part in getattr(content, "parts", []) or []:
                        transcription = getattr(
                            part, "audio_transcription", None
                        )

                        if not transcription:
                            continue

                        speaker = self._normalize_speaker_label(
                            getattr(
                                transcription, "speaker_label", ""
                            ) or ""
                        )

                        for word_info in getattr(
                            transcription, "words", []
                        ) or []:

                            word = getattr(word_info, "word", "")

                            word_speaker = self._normalize_speaker_label(
                                getattr(
                                    word_info, "speaker_label", ""
                                ) or speaker
                            )

                            start = self._offset_to_seconds(
                                getattr(word_info, "start_offset", None)
                            )

                            end = self._offset_to_seconds(
                                getattr(word_info, "end_offset", None)
                            )

                            if not word or start is None or end is None:
                                continue

                            segments.append({
                                "timestamp": self._format_timestamp(start),
                                "text": word.strip(),
                                "speaker": word_speaker,
                                "start": start,
                                "end": end,
                            })

            # Try parsing tagged transcript if word annotations are absent.
            if not segments:
                segments = self._parse_tagged_transcript(transcript_text)

            segments = self._group_segments(segments)

            # Keep segments chronological.
            segments.sort(key=lambda item: item["start"])

            # Fallback if Gemini doesn't expose word annotations.
            if not segments:
                segments = [{
                    "timestamp": "00:00:00",
                    "text": transcript_text,
                    "speaker": "Unknown",
                    "start": 0.0,
                    "end": self._audio_duration(path),
                }]

            print(
                f"Gemini transcription completed. "
                f"Extracted {len(segments)} transcript segments."
            )

            return {
                "status": "success",
                "text": transcript_text,
                "segments": segments,
                "language": "en",
            }

        except Exception as e:
            print(f"Transcription failed: {str(e)}")

            return {
                "status": "error",
                "error": str(e),
                "text": None,
                "segments": [],
            }

    @staticmethod
    def _offset_to_seconds(offset):
        """Convert Gemini time offsets to seconds."""

        if offset is None:
            return None

        try:
            if isinstance(offset, (int, float)):
                return float(offset)

            value = str(offset).strip().lower()

            if value.endswith("ms"):
                return float(value[:-2]) / 1000.0

            if value.endswith("s"):
                return float(value[:-1])

            return float(value)

        except (TypeError, ValueError):
            return None

    @classmethod
    def _extract_word_segments(cls, response) -> list[dict]:
        """Extract word_info annotations from the Gemini response."""

        segments = []

        def visit(value):
            if isinstance(value, dict):

                if value.get("type") == "word_info":
                    start = cls._offset_to_seconds(
                        value.get("start_offset", value.get("start"))
                    )

                    end = cls._offset_to_seconds(
                        value.get("end_offset", value.get("end"))
                    )

                    word = value.get("text", value.get("word", ""))

                    if word and start is not None and end is not None:
                        segments.append({
                            "timestamp": cls._format_timestamp(start),
                            "text": str(word).strip(),
                            "speaker": cls._normalize_speaker_label(
                                value.get(
                                    "speaker", value.get("speaker_label", "")
                                )
                            ),
                            "start": start,
                            "end": end,
                        })

                for child in value.values():
                    visit(child)

            elif isinstance(value, (list, tuple)):
                for child in value:
                    visit(child)

        if hasattr(response, "model_dump"):
            visit(response.model_dump())
        else:
            visit(response)

        return segments

    @staticmethod
    def _audio_duration(path: Path) -> float:
        """Return source audio duration."""

        try:
            return float(sf.info(str(path)).duration)
        except Exception:
            return 0.0

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format seconds as HH:MM:SS."""

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def _normalize_speaker_label(label: str) -> str:
        """Normalize Gemini speaker labels."""

        label_text = str(label)

        match = re.search(
            r"(?P<prefix>spk|speaker)\s*"
            r"(?P<separator>[:_-]?)\s*"
            r"(?P<number>\d+)",
            label_text,
            re.IGNORECASE,
        )

        if match:
            number = int(match.group("number"))
            separator = match.group("separator")

            display_number = (
                number + 1
                if separator == ":" or number == 0
                else number
            )

            return f"Speaker {display_number}"

        return label_text.strip() if label else "Unknown"

    @classmethod
    def _parse_tagged_transcript(cls, text: str) -> list[dict]:
        """Parse speaker-tagged text when word annotations are unavailable."""

        parsed = []

        pattern = re.compile(
            r"^\s*(?:(?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?)\s+)?"
            r"(?P<speaker>spk\s*[:_-]?\s*\d+|speaker\s*\d+)"
            r"\s*:\s*(?P<text>.+?)\s*$",
            re.IGNORECASE,
        )

        for line in text.splitlines():
            match = pattern.match(line)

            if not match:
                continue

            timestamp = match.group("timestamp") or "00:00:00"
            start = cls._timestamp_to_seconds(timestamp)

            parsed.append({
                "timestamp": cls._format_timestamp(start),
                "text": match.group("text").strip(),
                "speaker": cls._normalize_speaker_label(
                    match.group("speaker")
                ),
                "start": start,
                "end": start,
            })

        return parsed

    @staticmethod
    def _timestamp_to_seconds(timestamp: str) -> float:
        """Convert timestamp to seconds."""

        parts = [int(part) for part in timestamp.split(":")]

        if len(parts) == 2:
            return float(parts[0] * 60 + parts[1])

        return float(
            parts[0] * 3600 + parts[1] * 60 + parts[2]
        )

    @classmethod
    def _group_segments(cls, segments: list[dict]) -> list[dict]:
        """Join adjacent words from the same speaker into utterances."""

        grouped = []

        for segment in sorted(segments, key=lambda item: item["start"]):

            if not segment.get("text", "").strip():
                continue

            speaker = segment.get("speaker") or "Unknown"
            previous = grouped[-1] if grouped else None

            gap = (
                segment["start"] - previous["end"]
                if previous
                else 0
            )

            can_join = (
                previous
                and previous["speaker"] == speaker
                and gap <= 1.5
            )

            if can_join:
                previous["text"] = (
                    f"{previous['text']} {segment['text']}"
                ).strip()

                previous["end"] = max(
                    previous["end"], segment["end"]
                )

            else:
                grouped.append({
                    "timestamp": cls._format_timestamp(segment["start"]),
                    "text": segment["text"].strip(),
                    "speaker": speaker,
                    "start": segment["start"],
                    "end": segment["end"],
                })

        return grouped


# Create transcription service.
transcription_service = TranscriptionService()
