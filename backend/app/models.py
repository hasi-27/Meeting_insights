from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Request Models
class MeetingUpload(BaseModel):
    """Request model for file upload."""

    pass  # File is handled separately by FastAPI


# Response Models
class TranscriptSegment(BaseModel):
    """Single segment of transcript with speaker and timestamp."""

    timestamp: str = Field(..., description="Timestamp in HH:MM:SS format")
    speaker: str = Field(..., description="Speaker label (e.g., Speaker 1)")
    text: str = Field(..., description="Spoken text")


class DecisionItem(BaseModel):
    """Decision extracted from meeting."""

    decision: str = Field(..., description="Clear decision statement")


class ActionItem(BaseModel):
    """Action item extracted from meeting."""

    task: str = Field(..., description="Task description")
    assignee: str = Field(..., description="Who the task is assigned to")
    deadline: str = Field(
        ..., description="Deadline (specific date or 'Not mentioned')"
    )
    status: str = Field(default="Pending", description="Task status")


class SpeakerInsight(BaseModel):
    """Speaker-level statistics and insights."""

    speaker: str = Field(..., description="Speaker label")
    talk_time_seconds: int = Field(..., description="Total talk time in seconds")
    talk_percentage: float = Field(..., description="Percentage of total meeting time")
    sentiment: str = Field(
        ..., description="Basic sentiment (positive, neutral, negative)"
    )


class MeetingResponse(BaseModel):
    """Complete meeting analysis response."""

    meeting_id: str = Field(..., description="Unique meeting identifier")
    filename: str = Field(..., description="Original filename")
    status: str = Field(
        ..., description="Processing status (processing, completed, failed)"
    )
    duration_seconds: Optional[int] = Field(
        None, description="Total duration of meeting in seconds"
    )
    summary: Optional[str] = Field(None, description="AI-generated meeting summary")
    decisions: Optional[List[DecisionItem]] = Field(None, description="List of decisions")
    action_items: Optional[List[ActionItem]] = Field(
        None, description="List of action items"
    )
    open_questions: Optional[List[str]] = Field(None, description="Unresolved questions")
    speakers: Optional[List[SpeakerInsight]] = Field(
        None, description="Speaker-level insights"
    )
    transcript: Optional[List[TranscriptSegment]] = Field(
        None, description="Full transcript with speaker labels"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")


class MeetingUploadResponse(BaseModel):
    """Response after uploading a meeting file."""

    meeting_id: str = Field(..., description="Unique meeting identifier")
    filename: str = Field(..., description="Uploaded filename")
    status: str = Field(default="processing", description="Processing status")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="ok", description="API status")
    version: str = Field(..., description="API version")
