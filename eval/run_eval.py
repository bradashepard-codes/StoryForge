"""
Evaluation runner for StoryForge.

Loads test cases, runs them through both prompt variants via the Claude API
in parallel, and saves raw outputs to the outputs/ directory for manual scoring.

Usage:
  python eval/run_eval.py                   # single run (default)
  python eval/run_eval.py --runs 3          # reliability pass — 3 runs per case
  python eval/run_eval.py --runs 3 --ids TC001 TC002 TC003 TC004  # reliability subset
"""

import argparse
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


def _run_single_pass(test_cases: list, run_index: int, total_runs: int) -> tuple[list, list]:
    """Execute one full pass over all test cases. Returns (baseline_results, improved_results)."""
    run_label = f"run {run_index} of {total_runs}" if total_runs > 1 else "single run"
    baseline_results = [None] * len(test_cases)
    improved_results = [None] * len(test_cases)

    print(f"\n--- {run_label} ({len(test_cases)} cases, up to {MAX_WORKERS} parallel workers) ---\n")

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

    return baseline_results, improved_results


def run_evaluation(runs: int = 1, ids: list[str] | None = None):
    with open(TEST_CASES_PATH) as f:
        all_cases = json.load(f)

    test_cases = [tc for tc in all_cases if ids is None or tc["id"] in ids]

    if not test_cases:
        print(f"No matching test cases for ids: {ids}")
        return

    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    for run_index in range(1, runs + 1):
        baseline_results, improved_results = _run_single_pass(test_cases, run_index, runs)

        suffix = f"_run{run_index}" if runs > 1 else ""
        baseline_path = os.path.join(OUTPUTS_DIR, f"baseline_results{suffix}.json")
        improved_path = os.path.join(OUTPUTS_DIR, f"improved_results{suffix}.json")

        with open(baseline_path, "w") as f:
            json.dump([r for r in baseline_results if r], f, indent=2)

        with open(improved_path, "w") as f:
            json.dump([r for r in improved_results if r], f, indent=2)

        print(f"\n  Saved: {baseline_path}")
        print(f"  Saved: {improved_path}")

        parse_failures = [r["test_case_id"] for r in improved_results if r and not r["parse_success"]]
        if parse_failures:
            print(f"  Parse failures (manual review needed): {parse_failures}")

    if runs > 1:
        print(f"\nReliability pass complete — {runs} runs saved to outputs/.")
        print("Score each run independently, then compare dimension scores across runs.")
        print("Flag any case where a dimension varies by ≥ 1 point across runs as unstable.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StoryForge evaluation runner")
    parser.add_argument(
        "--runs", type=int, default=1,
        help="Number of times to run each test case (default: 1; use 3 for reliability pass)"
    )
    parser.add_argument(
        "--ids", nargs="+", default=None,
        help="Optional list of test case IDs to run (e.g. --ids TC001 TC002). Runs all if omitted."
    )
    args = parser.parse_args()
    run_evaluation(runs=args.runs, ids=args.ids)
