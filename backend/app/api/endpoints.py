
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import uuid

from app.models import (
    MeetingUploadResponse,
    MeetingResponse,
    DecisionItem,
    ActionItem,
    TranscriptSegment,
    SpeakerInsight,
)
from app.utils.error_handler import handle_error
from app.utils.helpers import (
    merge_transcript_with_speakers,
    format_transcript_for_llm,
    estimate_meeting_duration,
)
from app.services.file_handler import FileHandler
from app.services.transcription import transcription_service
from app.services.llm_analysis import llm_service
from app.services.speaker_stats import speaker_stats_service

router = APIRouter()
file_handler = FileHandler()

# Temporary in-memory storage for meeting records.
meetings_db = {}


@router.post("/meetings/upload", response_model=MeetingUploadResponse)
async def upload_meeting(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    """Upload a meeting recording and start processing."""

    try:
        if not file.filename:
            raise ValueError("No filename provided")

        meeting_id = str(uuid.uuid4())

        file_path = await file_handler.save_upload(file, meeting_id)

        meetings_db[meeting_id] = {
            "meeting_id": meeting_id,
            "filename": file.filename,
            "status": "processing",
            "file_path": file_path,
        }

        if background_tasks:
            background_tasks.add_task(
                process_meeting_background, meeting_id
            )
        else:
            raise RuntimeError("Background task manager unavailable")

        return MeetingUploadResponse(
            meeting_id=meeting_id,
            filename=file.filename,
            status="processing",
        )

    except Exception as e:
        raise handle_error(e, "File upload failed")


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str):
    """Retrieve meeting processing status and results."""

    try:
        meeting = meetings_db.get(meeting_id)

        if meeting is None:
            raise HTTPException(
                status_code=404,
                detail=f"Meeting {meeting_id} not found",
            )

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

    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e, "Failed to retrieve meeting")


@router.post("/meetings/{meeting_id}/process")
async def process_meeting_endpoint(
    meeting_id: str,
    background_tasks: BackgroundTasks,
):
    """Manually trigger meeting processing."""

    try:
        meeting = meetings_db.get(meeting_id)

        if meeting is None:
            raise HTTPException(
                status_code=404,
                detail=f"Meeting {meeting_id} not found",
            )

        if meeting["status"] != "processing":
            return {
                "status": meeting["status"],
                "meeting_id": meeting_id,
            }

        background_tasks.add_task(
            process_meeting_background, meeting_id
        )

        return {
            "status": "processing",
            "meeting_id": meeting_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e, "Failed to start processing")


async def process_meeting_background(meeting_id: str):
    """
    Pipeline:
    Gemini Transcription + Diarization
    → Transcript formatting
    → Gemini LLM analysis
    → Speaker statistics
    """

    try:
        meeting = meetings_db.get(meeting_id)

        if meeting is None:
            raise ValueError(f"Meeting {meeting_id} not found")

        file_path = meeting["file_path"]

        # Step 1: Transcription and speaker diarization
        # Gemini provides text, speaker labels and timestamps.
        print(f"[{meeting_id}] Starting Gemini transcription...")

        trans_result = await transcription_service.transcribe(
            file_path
        )

        if trans_result["status"] != "success":
            raise ValueError(
                f"Transcription failed: "
                f"{trans_result.get('error', 'Unknown error')}"
            )

        transcript_segments = trans_result.get("segments", [])
        transcript_text = trans_result.get("text", "")

        # Step 2: Use Gemini speaker labels.
        # No separate pyannote model is loaded.
        print(
            f"[{meeting_id}] Using Gemini speaker diarization..."
        )

        diarization_segments = []

        # Step 3: Merge transcript and speaker information.
        print(f"[{meeting_id}] Formatting speaker transcript...")

        merged_transcript = merge_transcript_with_speakers(
            transcript_segments,
            diarization_segments,
        )

        # Step 4: Format transcript for LLM.
        transcript_for_llm = format_transcript_for_llm(
            merged_transcript
        )

        # Step 5: Meeting analysis.
        print(f"[{meeting_id}] Running Gemini meeting analysis...")

        llm_result = await llm_service.analyze_transcript(
            transcript_for_llm
        )

        if llm_result["status"] != "success":
            raise ValueError(
                f"LLM analysis failed: "
                f"{llm_result.get('error')}"
            )

        analysis = llm_result["analysis"]

        # Step 6: Calculate speaker statistics.
        print(f"[{meeting_id}] Calculating speaker statistics...")

        speaker_insights = speaker_stats_service.calculate_stats(
            merged_transcript,
            diarization_segments,
        )

        # Step 7: Calculate meeting duration.
        duration_seconds = estimate_meeting_duration(
            transcript_segments
        )

        # Step 8: Save results in meeting record.
        meetings_db[meeting_id].update({
            "status": "completed",
            "summary": analysis.get("summary"),
            "decisions": [
                DecisionItem(
                    decision=d["decision"]
                ).model_dump()
                for d in analysis.get("decisions", [])
            ],
            "action_items": [
                ActionItem(**item).model_dump()
                for item in analysis.get("action_items", [])
            ],
            "open_questions": analysis.get(
                "open_questions", []
            ),
            "speakers": [
                SpeakerInsight(**speaker).model_dump()
                for speaker in speaker_insights
            ],
            "transcript": [
                TranscriptSegment(**segment).model_dump()
                for segment in merged_transcript
            ],
            "duration_seconds": duration_seconds,
        })

        print(
            f"[{meeting_id}] Processing completed successfully"
        )

    except Exception as e:
        print(f"[{meeting_id}] Processing failed: {str(e)}")

        meeting = meetings_db.get(meeting_id)

        if meeting is not None:
            meeting.update({
                "status": "failed",
                "error_message": str(e),
            })
