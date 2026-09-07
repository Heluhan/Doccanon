#!/usr/bin/env python3
"""Measure DocCanon context size without pretending it is an A/B token result."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


CODE_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cs", ".css", ".go", ".h", ".hpp", ".html", ".java",
    ".js", ".jsx", ".kt", ".kts", ".php", ".py", ".rb", ".rs", ".scala", ".sh",
    ".sql", ".svelte", ".swift", ".ts", ".tsx", ".vue",
}


def load_doccanon():
    path = Path(__file__).with_name("doccanon.py")
    spec = importlib.util.spec_from_file_location("doccanon_helper", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def tracked_code(project: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=project, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    paths = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = Path(raw.decode("utf-8", errors="surrogateescape"))
        if relative.suffix.lower() in CODE_SUFFIXES and (project / relative).is_file():
            paths.append(relative)
    return sorted(paths)


def proxy_units(text: str) -> int:
    # Language-neutral, dependency-free comparison unit. This is deliberately
    # not called a model token count.
    return len(re.findall(r"[A-Za-z0-9_]+|[\u3400-\u9fff]|[^\s]", text))


def size(paths: list[Path], project: Path) -> dict[str, int]:
    characters = 0
    units = 0
    for relative in paths:
        text = (project / relative).read_text(encoding="utf-8", errors="replace")
        characters += len(text)
        units += proxy_units(text)
    return {"files": len(paths), "characters": characters, "proxy_units": units}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare a DocCanon task bundle with an explicitly defined code-reading baseline"
    )
    parser.add_argument("--project", default=".")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument(
        "--baseline",
        choices=["tracked-code", "file-list"],
        default="tracked-code",
        help="tracked-code is an upper-bound corpus proxy, not observed agent behavior",
    )
    parser.add_argument("--baseline-file-list", help="newline-delimited project-relative paths")
    parser.add_argument(
        "--allow-stale",
        action="store_true",
        help="measure a stale bundle for diagnosis; never use it for a public savings claim",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project = Path(args.project).expanduser().resolve()
    helper = load_doccanon()
    bundle = helper.context_bundle(project, args.intent, args.limit, include_historical=False)
    if bundle.get("status") != "synchronized" and not args.allow_stale:
        print(
            f"DocCanon context is {bundle.get('status')}, not synchronized; repair freshness before benchmarking. "
            "Use --allow-stale only for diagnosis.",
            file=sys.stderr,
        )
        return 2
    if not bundle.get("documents"):
        print(f"No DocCanon context documents selected (status: {bundle.get('status')}).", file=sys.stderr)
        return 2
    context_paths = [Path(item["path"]) for item in bundle["documents"]]

    if args.baseline == "file-list":
        if not args.baseline_file_list:
            print("--baseline file-list requires --baseline-file-list", file=sys.stderr)
            return 2
        list_path = Path(args.baseline_file_list).expanduser()
        baseline_paths = [Path(line.strip()) for line in list_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        baseline_definition = f"explicit file list: {list_path}"
    else:
        baseline_paths = tracked_code(project)
        baseline_definition = "all Git-tracked files with recognized code suffixes (upper-bound corpus proxy)"

    missing = [str(path) for path in baseline_paths if not (project / path).is_file()]
    if missing:
        print("Missing baseline files: " + ", ".join(missing[:10]), file=sys.stderr)
        return 2

    context_size = size(context_paths, project)
    baseline_size = size(baseline_paths, project)
    reduction = None
    if baseline_size["proxy_units"]:
        reduction = round(100 * (1 - context_size["proxy_units"] / baseline_size["proxy_units"]), 1)
    payload = {
        "status": "measured",
        "project": str(project),
        "intent": args.intent,
        "doccanon_status": bundle.get("status"),
        "metric": "lexical_proxy_units_v1",
        "doccanon_context": {**context_size, "paths": [str(path) for path in context_paths]},
        "baseline": {**baseline_size, "definition": baseline_definition},
        "context_reduction_proxy_percent": reduction,
        "claim_boundary": (
            "This compares text volume, not actual model input tokens, cost, task quality, or latency. "
            "Use the A/B protocol in references/token-benchmark.md before publishing a token-savings claim."
        ),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"DocCanon context: {context_size['files']} files / {context_size['proxy_units']} proxy units")
        print(f"Baseline: {baseline_size['files']} files / {baseline_size['proxy_units']} proxy units")
        print(f"Context reduction proxy: {reduction}%")
        print(payload["claim_boundary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
