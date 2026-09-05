from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional
import uuid
import os
import asyncio

from app.config import settings
from app.models import (
    MeetingUploadResponse,
    MeetingResponse,
    DecisionItem,
    ActionItem,
    TranscriptSegment,
    SpeakerInsight,
)
from app.utils.error_handler import handle_error
from app.utils.validation import validate_transcript_segment
from app.utils.helpers import (
    merge_transcript_with_speakers,
    format_transcript_for_llm,
    estimate_meeting_duration,
)
from app.services.file_handler import FileHandler
from app.services.transcription import transcription_service
from app.services.diarization import diarization_service
from app.services.llm_analysis import llm_service
from app.services.speaker_stats import speaker_stats_service

router = APIRouter()
file_handler = FileHandler()

# In-memory storage for meeting states (replace with DB in production)
meetings_db = {}


@router.post("/meetings/upload", response_model=MeetingUploadResponse)
async def upload_meeting(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a meeting recording file.

    Supported formats: MP3, WAV, M4A, MP4

    Returns:
        MeetingUploadResponse with meeting_id for tracking
    """
    try:
        # Validate file
        if not file.filename:
            raise ValueError("No filename provided")

        # Generate unique meeting ID
        meeting_id = str(uuid.uuid4())

        # Save file
        file_path = await file_handler.save_upload(file, meeting_id)

        # Initialize meeting record
        meetings_db[meeting_id] = {
            "meeting_id": meeting_id,
            "filename": file.filename,
            "status": "processing",
            "file_path": file_path,
        }

        # Start background processing
        if background_tasks:
            background_tasks.add_task(process_meeting_background, meeting_id)
        else:
            # If no background tasks, start async processing
            asyncio.create_task(process_meeting_background(meeting_id))

        return MeetingUploadResponse(
            meeting_id=meeting_id, filename=file.filename, status="processing"
        )

    except Exception as e:
        raise handle_error(e, "File upload failed")


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str):
    """
    Get the results of a processed meeting.

    Returns current processing status or completed results.
    """
    try:
        if meeting_id not in meetings_db:
            raise ValueError(f"Meeting {meeting_id} not found")

        meeting = meetings_db[meeting_id]

        # Build response with all available data
        response_data = {
            "meeting_id": meeting_id,
            "filename": meeting["filename"],
            "status": meeting.get("status", "processing"),
            "duration_seconds": meeting.get("duration_seconds"),
            "summary": meeting.get("summary"),
            "decisions": meeting.get("decisions"),
            "action_items": meeting.get("action_items"),
            "open_questions": meeting.get("open_questions"),
            "speakers": meeting.get("speakers"),
            "transcript": meeting.get("transcript"),
            "error_message": meeting.get("error_message"),
        }

        return MeetingResponse(**response_data)

    except Exception as e:
        raise handle_error(e, "Failed to retrieve meeting")


@router.post("/meetings/{meeting_id}/process")
async def process_meeting_endpoint(meeting_id: str, background_tasks: BackgroundTasks):
    """
    Trigger processing of an uploaded meeting.

    This endpoint manually triggers the processing pipeline.
    """
    try:
        if meeting_id not in meetings_db:
            raise ValueError(f"Meeting {meeting_id} not found")

        meeting = meetings_db[meeting_id]

        if meeting["status"] != "processing":
            return {"status": meeting["status"], "meeting_id": meeting_id}

        # Start processing
        background_tasks.add_task(process_meeting_background, meeting_id)

        return {"status": "processing", "meeting_id": meeting_id}

    except Exception as e:
        raise handle_error(e, "Failed to start processing")


async def process_meeting_background(meeting_id: str):
    """
    Background processing pipeline for meeting analysis.

    Runs: Transcription → Diarization → Merge → LLM Analysis → Statistics
    """
    try:
        meeting = meetings_db[meeting_id]
        file_path = meeting["file_path"]

        # Step 1: Transcription
        print(f"[{meeting_id}] Starting transcription...")
        trans_result = await transcription_service.transcribe(file_path)

        if trans_result["status"] != "success":
            raise ValueError(
                f"Transcription failed: {trans_result.get('error', 'Unknown error')}"
            )

        transcript_segments = trans_result["segments"]
        transcript_text = trans_result["text"]

        # Step 2: Speaker Diarization
        print(f"[{meeting_id}] Starting speaker diarization...")
        diar_result = await diarization_service.diarize(file_path)

        if diar_result["status"] == "error":
            raise ValueError(f"Diarization failed: {diar_result.get('error')}")

        diarization_segments = diar_result.get("segments", [])

        # Step 3: Merge Transcript with Speakers
        print(f"[{meeting_id}] Merging transcript with speaker labels...")
        merged_transcript = merge_transcript_with_speakers(
            transcript_segments, diarization_segments
        )

        # Step 4: Format for LLM
        transcript_for_llm = format_transcript_for_llm(merged_transcript)

        # Step 5: LLM Analysis
        print(f"[{meeting_id}] Running LLM analysis...")
        llm_result = await llm_service.analyze_transcript(transcript_for_llm)

        if llm_result["status"] != "success":
            raise ValueError(f"LLM analysis failed: {llm_result.get('error')}")

        analysis = llm_result["analysis"]

        # Step 6: Calculate Speaker Statistics
        print(f"[{meeting_id}] Calculating speaker statistics...")
        speaker_insights = speaker_stats_service.calculate_stats(
            merged_transcript, diarization_segments
        )

        # Calculate meeting duration
        duration_seconds = max(
            estimate_meeting_duration(diarization_segments),
            estimate_meeting_duration(transcript_segments),
        )

        # Step 7: Update meeting record
        meetings_db[meeting_id].update({
            "status": "completed",
            "summary": analysis.get("summary"),
            "decisions": [
                DecisionItem(decision=d["decision"]).model_dump()
                for d in analysis.get("decisions", [])
            ],
            "action_items": [
                ActionItem(**item).model_dump()
                for item in analysis.get("action_items", [])
            ],
            "open_questions": analysis.get("open_questions", []),
            "speakers": [
                SpeakerInsight(**speaker).model_dump() for speaker in speaker_insights
            ],
            "transcript": [
                TranscriptSegment(**segment).model_dump() for segment in merged_transcript
            ],
            "duration_seconds": duration_seconds,
        })

        print(f"[{meeting_id}] Processing completed successfully")

    except Exception as e:
        print(f"[{meeting_id}] Processing failed: {str(e)}")
        meetings_db[meeting_id].update({
            "status": "failed",
            "error_message": str(e),
        })
