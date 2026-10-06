#!/usr/bin/env python3
"""Reject branch-local version bumps: versions belong to release commits on the trunk."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def git(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(project), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def resolve_base(project: Path, requested: str | None) -> str | None:
    candidates = [requested] if requested else ["origin/main", "main", "origin/master", "master"]
    for candidate in candidates:
        if candidate and git(project, "rev-parse", "--verify", f"{candidate}^{{commit}}").returncode == 0:
            return candidate
    return None


def read_version(project: Path, revision: str | None = None) -> str | None:
    if revision is None:
        text = (project / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    else:
        result = git(project, "show", f"{revision}:.codex-plugin/plugin.json")
        if result.returncode != 0:
            return None
        text = result.stdout
    try:
        return str(json.loads(text)["version"])
    except (KeyError, json.JSONDecodeError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", help="Base ref to compare against; inferred when omitted")
    parser.add_argument("--project", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args(argv)
    project = Path(args.project).resolve()
    base = resolve_base(project, args.base)
    if base is None:
        print("version policy: no base ref found; skipped")
        return 0
    merge_base = git(project, "merge-base", base, "HEAD")
    if merge_base.returncode != 0 or not merge_base.stdout.strip():
        print("version policy: no merge base with the base ref; skipped")
        return 0
    ancestor = merge_base.stdout.strip()
    head = git(project, "rev-parse", "HEAD").stdout.strip()
    if ancestor == head:
        print("version policy: HEAD is the base commit; on the trunk")
        return 0
    head_version = read_version(project)
    base_version = read_version(project, ancestor)
    if head_version and base_version and head_version != base_version:
        print(
            f"version policy: version changed on a branch ({base_version} -> {head_version}); "
            "version bumps and changelog releases belong to release commits on the trunk",
            file=sys.stderr,
        )
        return 1
    print(f"version policy: ok ({head_version or 'unknown'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
