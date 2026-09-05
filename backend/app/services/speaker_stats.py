from typing import List, Dict, Any
from collections import defaultdict


class SpeakerStatsService:
    """Calculate speaker statistics from transcript."""

    @staticmethod
    def calculate_stats(
        transcript: List[Dict[str, Any]], diarization_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate statistics for each speaker.

        Args:
            transcript: List of transcript segments
            diarization_segments: List of diarization segments with speaker info

        Returns:
            List of speaker insights with stats
        """
        # Build speaker time mapping
        speaker_times = defaultdict(float)

        transcript_segments = [
            segment
            for segment in transcript
            if segment.get("speaker")
            and float(segment.get("end", 0)) > float(segment.get("start", 0))
        ]
        source_segments = transcript_segments or diarization_segments

        for segment in source_segments:
            speaker = segment.get("speaker", "Unknown")
            duration = max(
                0.0,
                float(segment.get("end", 0)) - float(segment.get("start", 0)),
            )
            speaker_times[speaker] += duration

        # Keep speakers visible even when timestamps are unavailable.
        for segment in transcript:
            speaker = segment.get("speaker")
            if speaker:
                speaker_times.setdefault(speaker, 0.0)

        # Calculate total duration
        total_duration = sum(speaker_times.values()) or 1

        # Build speaker insights
        speakers = []
        for speaker, talk_time in sorted(speaker_times.items()):
            speakers.append({
                "speaker": speaker,
                "talk_time_seconds": max(1, round(talk_time)) if talk_time > 0 else 0,
                "talk_percentage": round((talk_time / total_duration) * 100, 1),
                "sentiment": SpeakerStatsService._analyze_sentiment(
                    transcript, speaker
                ),
            })

        return speakers

    @staticmethod
    def _analyze_sentiment(transcript: List[Dict[str, Any]], speaker: str) -> str:
        """
        Analyze basic sentiment for speaker.

        Args:
            transcript: Full transcript
            speaker: Speaker label

        Returns:
            Sentiment classification (positive, neutral, negative)
        """
        # Get speaker's utterances
        utterances = [
            item.get("text", "").lower()
            for item in transcript
            if item.get("speaker") == speaker
        ]

        if not utterances:
            return "neutral"

        # Simple keyword-based sentiment
        positive_words = {
            "good", "great", "excellent", "perfect", "awesome", "amazing",
            "fantastic", "wonderful", "love", "happy", "yes", "sure", "agree"
        }
        negative_words = {
            "bad", "terrible", "awful", "poor", "hate", "problem", "issue",
            "wrong", "no", "disagree", "concerned", "worried", "risk"
        }

        positive_count = 0
        negative_count = 0

        for utterance in utterances:
            words = set(utterance.split())
            positive_count += len(words & positive_words)
            negative_count += len(words & negative_words)

        # Determine sentiment
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds to readable time string."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


# Create singleton instance
speaker_stats_service = SpeakerStatsService()
