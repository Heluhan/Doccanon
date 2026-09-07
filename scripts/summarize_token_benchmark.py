#!/usr/bin/env python3
"""Summarize paired DocCanon/no-DocCanon benchmark runs from CSV."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


REQUIRED = {
    "task", "variant", "run", "input_tokens", "output_tokens", "tool_calls", "elapsed_seconds", "success"
}


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "pass", "passed"}


def median(values: list[int]) -> float | None:
    return statistics.median(values) if values else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a paired DocCanon token benchmark")
    parser.add_argument("csv_file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.csv_file)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            parser.error("missing columns: " + ", ".join(sorted(missing)))
        rows = list(reader)

    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        variant = row["variant"].strip().lower()
        if variant not in {"control", "doccanon"}:
            parser.error(f"unknown variant {variant!r}; use control or doccanon")
        groups[variant].append(
            {
                "task": row["task"].strip(),
                "input_tokens": int(row["input_tokens"]),
                "output_tokens": int(row["output_tokens"]),
                "tool_calls": int(row["tool_calls"]),
                "success": truthy(row["success"]),
            }
        )

    if not groups["control"] or not groups["doccanon"]:
        parser.error("the CSV must contain both control and doccanon rows")

    summary: dict[str, dict[str, object]] = {}
    for variant in ("control", "doccanon"):
        values = groups[variant]
        summary[variant] = {
            "runs": len(values),
            "tasks": len({str(item["task"]) for item in values}),
            "median_input_tokens": median([int(item["input_tokens"]) for item in values]),
            "input_token_range": [
                min(int(item["input_tokens"]) for item in values),
                max(int(item["input_tokens"]) for item in values),
            ],
            "median_output_tokens": median([int(item["output_tokens"]) for item in values]),
            "median_tool_calls": median([int(item["tool_calls"]) for item in values]),
            "success_rate_percent": round(100 * sum(bool(item["success"]) for item in values) / len(values), 1),
        }
    control = summary["control"]["median_input_tokens"]
    treatment = summary["doccanon"]["median_input_tokens"]
    reduction = round(100 * (1 - float(treatment) / float(control)), 1) if control else None
    control_tasks = {str(item["task"]) for item in groups["control"]}
    doccanon_tasks = {str(item["task"]) for item in groups["doccanon"]}
    paired_tasks = control_tasks == doccanon_tasks
    payload = {
        "status": "summarized",
        "source": str(path),
        "variants": summary,
        "median_input_token_reduction_percent": reduction,
        "paired_task_set": paired_tasks,
        "claim_ready": (
            summary["doccanon"]["success_rate_percent"] >= summary["control"]["success_rate_percent"]
            and len(groups["control"]) >= 15
            and len(groups["doccanon"]) >= 15
            and len(control_tasks) >= 5
            and paired_tasks
        ),
        "claim_boundary": "Report model, agent version, task set, run count, success rubric, median, and range.",
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
