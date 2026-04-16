"""
Evaluation runner for StoryForge.

Loads test cases, runs them through both prompt variants via the Claude API
in parallel, and saves raw outputs to the outputs/ directory for manual scoring.
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.prompts import build_baseline_prompt, build_improved_prompt
from app.llm_client import call_baseline, call_improved
from app.parser import parse_output, parse_baseline_output

TEST_CASES_PATH = os.path.join(os.path.dirname(__file__), "test_cases.json")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
MAX_WORKERS = 4


def _run_case(tc: dict) -> tuple[dict, dict]:
    tc_id = tc["id"]
    feature_input = tc["feature_input"]
    category = tc["category"]

    baseline_prompt = build_baseline_prompt(feature_input)
    system_prompt, user_message = build_improved_prompt(feature_input)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_baseline = executor.submit(call_baseline, baseline_prompt)
        future_improved = executor.submit(call_improved, system_prompt, user_message)
        baseline_raw = future_baseline.result()
        improved_raw = future_improved.result()

    baseline_text = parse_baseline_output(baseline_raw) if baseline_raw else ""
    parsed = parse_output(improved_raw) if improved_raw else None

    baseline_result = {
        "test_case_id": tc_id,
        "category": category,
        "raw_output": baseline_text
    }

    improved_result = {
        "test_case_id": tc_id,
        "category": category,
        "raw_output": improved_raw or "",
        "parsed": parsed.model_dump() if parsed else None,
        "parse_success": parsed is not None
    }

    return baseline_result, improved_result


def run_evaluation():
    with open(TEST_CASES_PATH) as f:
        test_cases = json.load(f)

    baseline_results = [None] * len(test_cases)
    improved_results = [None] * len(test_cases)

    print(f"Running {len(test_cases)} test cases with up to {MAX_WORKERS} parallel workers...\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_run_case, tc): i for i, tc in enumerate(test_cases)}
        for future in as_completed(futures):
            i = futures[future]
            tc_id = test_cases[i]["id"]
            try:
                baseline_result, improved_result = future.result()
                baseline_results[i] = baseline_result
                improved_results[i] = improved_result
                print(f"  {tc_id} complete — parse success: {improved_result['parse_success']}")
            except Exception as e:
                print(f"  {tc_id} failed: {e}")

    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    baseline_path = os.path.join(OUTPUTS_DIR, "baseline_results.json")
    improved_path = os.path.join(OUTPUTS_DIR, "improved_results.json")

    with open(baseline_path, "w") as f:
        json.dump([r for r in baseline_results if r], f, indent=2)

    with open(improved_path, "w") as f:
        json.dump([r for r in improved_results if r], f, indent=2)

    print(f"\nDone. Results saved to outputs/")
    print(f"  Baseline: {baseline_path}")
    print(f"  Improved: {improved_path}")

    parse_failures = [r["test_case_id"] for r in improved_results if r and not r["parse_success"]]
    if parse_failures:
        print(f"\nParse failures (manual review needed): {parse_failures}")


if __name__ == "__main__":
    run_evaluation()
