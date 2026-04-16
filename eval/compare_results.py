"""
Comparison module for StoryForge evaluation.

Reads scored results and produces a summary table comparing
baseline vs improved across all rubric dimensions.
"""

import json
import os
import pandas as pd

OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
SCORES_PATH = os.path.join(OUTPUTS_DIR, "eval_scores.csv")


def load_scores() -> pd.DataFrame:
    if not os.path.exists(SCORES_PATH):
        raise FileNotFoundError(
            f"No scores file found at {SCORES_PATH}. "
            "Run manual scoring and save results to outputs/eval_scores.csv first."
        )
    return pd.read_csv(SCORES_PATH)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Return average score per dimension per variant."""
    dimensions = ["clarity", "completeness", "testability", "dor_compliance", "escalation_accuracy"]
    return df.groupby("variant")[dimensions].mean().round(2)


def print_comparison():
    df = load_scores()
    summary = summarize(df)

    print("\n=== StoryForge Evaluation Summary ===\n")
    print(summary.to_string())

    if "baseline" in summary.index and "improved" in summary.index:
        delta = summary.loc["improved"] - summary.loc["baseline"]
        print("\n=== Improvement Delta (Improved - Baseline) ===\n")
        print(delta.to_string())

    print()


def export_summary(output_path: str = None):
    df = load_scores()
    summary = summarize(df)
    path = output_path or os.path.join(OUTPUTS_DIR, "eval_summary.csv")
    summary.to_csv(path)
    print(f"Summary exported to {path}")


if __name__ == "__main__":
    print_comparison()
