"""
Evaluation runner for StoryForge.

Loads test cases, runs them through both prompt variants via the Claude API,
and saves raw outputs to the outputs/ directory for manual scoring.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.prompts import build_baseline_prompt, build_improved_prompt
from app.llm_client import call_baseline, call_improved
from app.parser import parse_output, parse_baseline_output

TEST_CASES_PATH = os.path.join(os.path.dirname(__file__), "test_cases.json")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def run_evaluation():
    with open(TEST_CASES_PATH) as f:
        test_cases = json.load(f)

    baseline_results = []
    improved_results = []

    for tc in test_cases:
        tc_id = tc["id"]
        feature_input = tc["feature_input"]
        print(f"Running {tc_id}...")

        # Baseline
        baseline_prompt = build_baseline_prompt(feature_input)
        baseline_raw = call_baseline(baseline_prompt)
        baseline_text = parse_baseline_output(baseline_raw)
        baseline_results.append({
            "test_case_id": tc_id,
            "category": tc["category"],
            "raw_output": baseline_text
        })

        # Improved
        system_prompt, user_message = build_improved_prompt(feature_input)
        improved_raw = call_improved(system_prompt, user_message)
        parsed = parse_output(improved_raw)
        improved_results.append({
            "test_case_id": tc_id,
            "category": tc["category"],
            "raw_output": improved_raw,
            "parsed": parsed.model_dump() if parsed else None,
            "parse_success": parsed is not None
        })

    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    baseline_path = os.path.join(OUTPUTS_DIR, "baseline_results.json")
    improved_path = os.path.join(OUTPUTS_DIR, "improved_results.json")

    with open(baseline_path, "w") as f:
        json.dump(baseline_results, f, indent=2)

    with open(improved_path, "w") as f:
        json.dump(improved_results, f, indent=2)

    print(f"\nDone. Results saved to outputs/")
    print(f"  Baseline: {baseline_path}")
    print(f"  Improved: {improved_path}")

    parse_failures = [r["test_case_id"] for r in improved_results if not r["parse_success"]]
    if parse_failures:
        print(f"\nParse failures (manual review needed): {parse_failures}")


if __name__ == "__main__":
    run_evaluation()
