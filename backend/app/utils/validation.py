from typing import Any, Dict, List


def validate_llm_output(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean LLM output to ensure schema compliance.

    Args:
        analysis: Raw output from LLM

    Returns:
        Validated and cleaned analysis dictionary

    Raises:
        ValueError: If validation fails
    """
    validated = {
        "summary": _validate_string(analysis.get("summary"), "No summary available"),
        "decisions": _validate_decisions(analysis.get("decisions", [])),
        "action_items": _validate_action_items(analysis.get("action_items", [])),
        "open_questions": _validate_questions(analysis.get("open_questions", [])),
    }

    return validated


def _validate_string(value: Any, default: str) -> str:
    """Validate and return string value."""
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _validate_decisions(decisions: Any) -> List[Dict[str, str]]:
    """Validate decisions list."""
    if not isinstance(decisions, list):
        return []

    validated = []
    for item in decisions:
        if isinstance(item, dict) and "decision" in item:
            decision_text = str(item["decision"]).strip()
            if decision_text:
                validated.append({"decision": decision_text})

    return validated


def _validate_action_items(items: Any) -> List[Dict[str, str]]:
    """Validate action items list."""
    if not isinstance(items, list):
        return []

    validated = []
    for item in items:
        if not isinstance(item, dict):
            continue

        task = str(item.get("task", "")).strip()
        assignee = str(item.get("assignee", "")).strip()
        deadline = str(item.get("deadline", "")).strip()
        status = str(item.get("status", "Pending")).strip()

        if task and assignee:
            if not deadline:
                deadline = "Not mentioned"
            if not status:
                status = "Pending"

            validated.append({
                "task": task,
                "assignee": assignee,
                "deadline": deadline,
                "status": status,
            })

    return validated


def _validate_questions(questions: Any) -> List[str]:
    """Validate open questions list."""
    if not isinstance(questions, list):
        return []

    validated = []
    for item in questions:
        question_text = str(item).strip() if item else ""
        if question_text:
            validated.append(question_text)

    return validated


def validate_transcript_segment(segment: Dict[str, Any]) -> bool:
    """
    Validate a single transcript segment.

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["timestamp", "speaker", "text"]
    return all(field in segment and segment[field] for field in required_fields)
