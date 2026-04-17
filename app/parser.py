import json
import logging
import os
from pydantic import BaseModel, field_validator
from typing import List

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "parse_errors.log")
logging.basicConfig(filename=LOG_PATH, level=logging.ERROR, format="%(asctime)s %(message)s")


class DefinitionOfReady(BaseModel):
    is_ready: bool
    criteria_met: List[str]
    criteria_missing: List[str]


class StoryPackage(BaseModel):
    user_story: str
    acceptance_criteria: List[str]
    definition_of_ready: DefinitionOfReady
    missing_information: List[str]
    assumptions: List[str]
    confidence: str
    escalation_flag: bool

    @field_validator("confidence")
    @classmethod
    def confidence_must_be_valid(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("confidence must be low, medium, or high")
        return v


def parse_output(raw: str) -> StoryPackage | None:
    """
    Parse raw model output into a validated StoryPackage.
    Returns None if the output cannot be parsed or validated.
    """
    try:
        # Strip markdown code fences if present
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        data = json.loads(text.strip())
        return StoryPackage(**data)

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logging.error(f"Parse failed: {e}\nRaw output:\n{raw}")
        return None


def parse_fanout_output(raw: str) -> list[StoryPackage] | None:
    """Parse raw model output into a validated list of StoryPackage objects."""
    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Expected a non-empty JSON array")
        return [StoryPackage(**item) for item in data]
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logging.error(f"Fan-out parse failed: {e}\nRaw output:\n{raw}")
        return None


def parse_baseline_output(raw: str) -> str:
    """
    Baseline output is unstructured text — return as-is for display.
    """
    return raw.strip()
