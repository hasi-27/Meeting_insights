import json
from typing import List, Dict, Any
from google import genai

from app.config import settings
from app.utils.validation import validate_llm_output


class LLMAnalysisService:
    """Handle LLM-based analysis of meeting transcripts."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    async def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze transcript using LLM.

        Args:
            transcript: Speaker-labeled transcript text

        Returns:
            Dictionary with extracted insights

        Raises:
            ValueError: If analysis fails
        """
        try:
            # Create structured prompt
            prompt = self._create_prompt(transcript)

            # Call LLM
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "system_instruction": "You are an AI assistant analyzing meeting transcripts. Extract grounded information in JSON format.",
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"},
                            "decisions": {"type": "array", "items": {"type": "object", "properties": {"decision": {"type": "string"}}, "required": ["decision"]}},
                            "action_items": {"type": "array", "items": {"type": "object", "properties": {"task": {"type": "string"}, "assignee": {"type": "string"}, "deadline": {"type": "string"}, "status": {"type": "string"}}, "required": ["task", "assignee", "deadline", "status"]}},
                            "open_questions": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["summary", "decisions", "action_items", "open_questions"],
                    },
                },
            )

            # Parse response
            content = response.text
            analysis = json.loads(content)

            # Validate and clean
            validated = validate_llm_output(analysis)

            return {
                "status": "success",
                "analysis": validated,
            }

        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "error": f"Failed to parse LLM response: {str(e)}",
                "analysis": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "analysis": None,
            }

    @staticmethod
    def _create_prompt(transcript: str) -> str:
        """Create structured prompt for LLM."""
        return f"""Analyze this meeting transcript and extract the following information in JSON format:

1. Summary: A concise 2-3 sentence summary of the meeting
2. Decisions: List of clear decisions made (if none, return empty list)
3. Action Items: List with task, assignee, deadline, and status
4. Open Questions: List of unresolved questions (if none, return empty list)

IMPORTANT RULES:
- Do NOT invent names, deadlines, or facts
- Base everything on the transcript content
- If a deadline is not mentioned, use "Not mentioned"
- If there are no decisions/questions, use empty lists
- Extract explicit question-form statements that remain unresolved, including
    questions introduced by phrases such as "one open question" or "are we
    still targeting...". Preserve the question faithfully and do not infer
    questions that are not stated or supported by the transcript.
- For assignees, use the speaker labels from transcript
- Keep summaries factual and grounded

Return JSON in this format:
{{
  "summary": "...",
  "decisions": [
    {{"decision": "..."}}
  ],
  "action_items": [
    {{
      "task": "...",
      "assignee": "...",
      "deadline": "...",
      "status": "Pending"
    }}
  ],
  "open_questions": ["..."]
}}

TRANSCRIPT:
{transcript}"""

    @staticmethod
    def _extract_speaker_label(text: str) -> str:
        """Extract speaker label from transcript line."""
        # Assumes format like "[00:00:00] Speaker 1: text"
        if "]" in text:
            try:
                speaker_part = text.split("]")[1].strip().split(":")[0].strip()
                return speaker_part
            except (IndexError, ValueError):
                return "Unknown"
        return "Unknown"


# Create singleton instance
llm_service = LLMAnalysisService()
