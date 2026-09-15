#!/usr/bin/env python3
"""Build the disposable governed project used to record the README GIF.

The project mirrors ``scripts/demo.py``: DocCanon is installed and a canonical
document is marked verified over ``src/**``. ``--drift`` then reproduces the
ordinary developer mistake DocCanon exists to catch -- covered code changes
while its canonical owner does not -- and stages it.

Usage:
    python3 demo/prepare.py [--path /tmp/doccanon-demo]
    python3 demo/prepare.py --drift [--path /tmp/doccanon-demo]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HELPER = REPO / "skills" / "doccanon" / "scripts" / "doccanon.py"
INSTALLER = REPO / "install.py"
CARD = Path(__file__).resolve().parent / "card.py"
DEFAULT_PATH = "/tmp/doccanon-demo"

ARCHITECTURE = (
    "# Session architecture\n\n"
    "## Current behavior\n\n"
    "Session recovery is implemented by `src/session.py`. The recovery boundary "
    "owns the observable return value and must be updated with any change to that "
    "module. The current implementation returns the stable v1 recovery marker and "
    "has no external dependency.\n\n"
    "## Verification\n\n"
    'Run `python3 -c "from src.session import recover; assert recover() == \'v1\'"`.\n'
)


def run(cwd: Path, *command: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def git(project: Path, *args: str) -> None:
    run(project, "git", *args)


def doccanon(project: Path, *args: str, check: bool = True) -> dict:
    result = run(
        project,
        sys.executable,
        str(HELPER),
        "--project",
        str(project),
        *args,
        "--json",
        check=False,
    )
    payload = json.loads(result.stdout)
    if check and result.returncode not in (0, 1):
        raise SystemExit(f"doccanon {' '.join(args)} failed: {result.stdout}{result.stderr}")
    return payload


def build(project: Path) -> None:
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)
    git(project, "init", "-q")
    git(project, "config", "user.email", "demo@doccanon.local")
    git(project, "config", "user.name", "DocCanon Demo")
    (project / "src").mkdir()
    (project / "src" / "session.py").write_text("def recover():\n    return 'v1'\n", encoding="utf-8")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "initial service")

    run(
        project,
        sys.executable,
        str(INSTALLER),
        "--agent",
        "universal",
        "--scope",
        "project",
        "--project",
        str(project),
    )
    for cache in project.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    git(project, "add", "-A")
    git(project, "commit", "-qm", "install DocCanon skill")

    doccanon(project, "enable")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "enable DocCanon")

    (project / "docs" / "architecture.md").write_text(ARCHITECTURE, encoding="utf-8")
    doccanon(project, "mark-verified", "docs/architecture.md", "--covers", "src/**", "--domain", "architecture")
    doccanon(project, "promote", "--domain", "architecture")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "govern session architecture")

    fresh = doccanon(project, "check")
    if fresh.get("status") != "synchronized":
        raise SystemExit(f"project is not synchronized: {fresh}")

    shutil.copyfile(CARD, project / ".card.py")


def drift(project: Path) -> None:
    """Change covered code without touching its canonical owner, then stage it."""
    (project / "src" / "session.py").write_text("def recover():\n    return 'v2'\n", encoding="utf-8")
    git(project, "add", "src/session.py")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=DEFAULT_PATH)
    parser.add_argument(
        "--drift",
        action="store_true",
        help="change covered code without updating its owner and stage it",
    )
    args = parser.parse_args()
    project = Path(args.path).resolve()
    if args.drift:
        drift(project)
    else:
        build(project)
    print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
