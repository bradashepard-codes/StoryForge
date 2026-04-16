"""
Rubric scoring for StoryForge evaluation.

Each dimension is scored 1 (Poor), 3 (Moderate), or 5 (Strong).
Scoring is performed manually by the evaluator using these definitions.
This module provides the rubric definitions and a structure for recording scores.
"""

RUBRIC = {
    "clarity": {
        1: "User story or criteria are unclear or vague",
        3: "Partially clear but contains ambiguous language",
        5: "Precise, unambiguous, and well-structured"
    },
    "completeness": {
        1: "Missing key elements (persona, goal, or business value)",
        3: "Mostly complete with minor gaps",
        5: "All required elements present and fully articulated"
    },
    "testability": {
        1: "Acceptance criteria are not testable",
        3: "Some criteria are testable, others are vague",
        5: "All criteria are specific, measurable, and testable"
    },
    "dor_compliance": {
        1: "Fails most Definition of Ready criteria",
        3: "Meets some DoR criteria but has notable gaps",
        5: "Fully meets all Definition of Ready criteria"
    },
    "escalation_accuracy": {
        1: "Fails to flag ambiguity when it should, or flags incorrectly",
        3: "Partially identifies issues but misses some",
        5: "Correctly flags ambiguity and provides clear missing information"
    }
}

DIMENSIONS = list(RUBRIC.keys())
VALID_SCORES = (1, 3, 5)


def score_output(test_case_id: str, variant: str, scores: dict) -> dict:
    """
    Record a manual rubric score for a single output.

    Args:
        test_case_id: e.g. "TC001"
        variant: "baseline" or "improved"
        scores: dict of dimension -> score, e.g. {"clarity": 3, "completeness": 5, ...}

    Returns:
        Validated score record with total and average.
    """
    if variant not in ("baseline", "improved"):
        raise ValueError("variant must be 'baseline' or 'improved'")

    for dim in DIMENSIONS:
        if dim not in scores:
            raise ValueError(f"Missing score for dimension: {dim}")
        if scores[dim] not in VALID_SCORES:
            raise ValueError(f"Score for '{dim}' must be 1, 3, or 5. Got: {scores[dim]}")

    total = sum(scores[dim] for dim in DIMENSIONS)
    average = round(total / len(DIMENSIONS), 2)

    return {
        "test_case_id": test_case_id,
        "variant": variant,
        "scores": scores,
        "total": total,
        "average": average
    }


def print_rubric():
    """Print rubric definitions for reference during manual scoring."""
    print("\n=== StoryForge Evaluation Rubric ===\n")
    for dimension, levels in RUBRIC.items():
        print(f"  {dimension.upper().replace('_', ' ')}")
        for score, description in levels.items():
            print(f"    {score} — {description}")
        print()
