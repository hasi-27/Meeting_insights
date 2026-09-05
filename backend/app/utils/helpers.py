from typing import List, Dict, Any
import re


def merge_transcript_with_speakers(
    transcript_segments: List[Dict[str, Any]],
    diarization_segments: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """
    Merge transcript segments with speaker labels from diarization.

    Args:
        transcript_segments: Segments from speech-to-text
        diarization_segments: Speaker segments from diarization

    Returns:
        Merged transcript with speaker labels
    """
    merged = []

    for trans_segment in transcript_segments:
        trans_start = trans_segment.get("start", 0)
        trans_end = trans_segment.get("end", 0)
        text = trans_segment.get("text", "")
        timestamp = trans_segment.get("timestamp", "00:00:00")

        # Prefer a speaker supplied by Gemini when diarization has no overlap.
        speaker = trans_segment.get("speaker", "Unknown") or "Unknown"
        for diar_segment in diarization_segments:
            diar_start = diar_segment.get("start", 0)
            diar_end = diar_segment.get("end", 0)

            # Check if segments overlap
            if trans_start < diar_end and trans_end > diar_start:
                speaker = diar_segment.get("speaker", "Unknown")
                break

        speaker_match = re.search(
            r"(?:spk|speaker)\s*(?P<separator>[:_-]?)\s*(?P<number>\d+)",
            speaker,
            re.IGNORECASE,
        )
        if speaker_match:
            number = int(speaker_match.group("number"))
            if speaker_match.group("separator") == ":" or number == 0:
                number += 1
            speaker = f"Speaker {number}"

        merged.append({
            "timestamp": timestamp,
            "speaker": speaker,
            "text": text,
            "start": trans_start,
            "end": trans_end,
        })

    return merged


def format_transcript_for_llm(transcript: List[Dict[str, str]]) -> str:
    """
    Format transcript for LLM analysis.

    Args:
        transcript: Merged transcript with speakers

    Returns:
        Formatted transcript string
    """
    lines = []
    for segment in transcript:
        timestamp = segment.get("timestamp", "00:00:00")
        speaker = segment.get("speaker", "Unknown")
        text = segment.get("text", "")
        lines.append(f"[{timestamp}] {speaker}: {text}")

    return "\n".join(lines)


def extract_unique_speakers(transcript: List[Dict[str, str]]) -> List[str]:
    """
    Extract unique speaker labels from transcript.

    Args:
        transcript: Merged transcript

    Returns:
        List of unique speaker labels
    """
    speakers = set()
    for segment in transcript:
        speaker = segment.get("speaker", "Unknown")
        if speaker:
            speakers.add(speaker)

    return sorted(list(speakers))


def clean_text(text: str) -> str:
    """
    Clean and normalize text.

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Strip whitespace
    text = text.strip()

    return text


def estimate_meeting_duration(segments: List[Dict[str, Any]]) -> int:
    """
    Estimate meeting duration from segments.

    Args:
        segments: List of transcript or diarization segments

    Returns:
        Duration in seconds
    """
    if not segments:
        return 0

    # Find max end time
    max_end = 0
    for segment in segments:
        end = segment.get("end", 0)
        if end > max_end:
            max_end = end

    return int(max_end)
