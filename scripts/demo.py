#!/usr/bin/env python3
"""Run a disposable DocCanon stale-document demonstration."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills" / "doccanon" / "scripts" / "doccanon.py"


def run(cwd: Path, *command: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git(cwd: Path, *args: str) -> None:
    run(cwd, "git", *args)


def doccanon(cwd: Path, *args: str, check: bool = True) -> dict:
    result = run(cwd, "python3", str(HELPER), "--project", str(cwd), *args, "--json", check=check)
    return json.loads(result.stdout)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="doccanon-demo-") as directory:
        project = Path(directory)
        git(project, "init", "-q")
        git(project, "config", "user.email", "demo@doccanon.local")
        git(project, "config", "user.name", "DocCanon Demo")
        (project / "src").mkdir()
        (project / "src" / "session.py").write_text("def recover():\n    return 'v1'\n", encoding="utf-8")
        git(project, "add", ".")
        git(project, "commit", "-qm", "initial service")

        doccanon(project, "enable")
        git(project, "add", ".")
        git(project, "commit", "-qm", "enable DocCanon")
        architecture = project / "docs" / "architecture.md"
        architecture.write_text(
            "# Session architecture\n\n"
            "## Current behavior\n\n"
            "Session recovery is implemented by `src/session.py`. The recovery boundary owns the "
            "observable return value and must be updated with any change to that module. The current "
            "implementation returns the stable v1 recovery marker and has no external dependency.\n\n"
            "## Verification\n\n"
            "Run `python3 -c \"from src.session import recover; assert recover() == 'v1'\"`.\n",
            encoding="utf-8",
        )
        doccanon(project, "mark-verified", "docs/architecture.md", "--covers", "src/**", "--domain", "architecture")
        doccanon(project, "promote", "--domain", "architecture")
        git(project, "add", ".")
        git(project, "commit", "-qm", "govern session architecture")
        healthy = doccanon(project, "check")

        (project / "src" / "session.py").write_text("def recover():\n    return 'v2'\n", encoding="utf-8")
        git(project, "add", "src/session.py")
        stale = doccanon(project, "check", "--staged", check=False)

        print("1. Governed baseline:", healthy["status"])
        print("2. Code changed without its owner:", stale["status"])
        for finding in stale.get("findings", []):
            print(f"   - {finding['code']}: {finding['message']}")
        print("3. DocCanon blocked the stale documentation before commit.")
        print("Demo project was disposable; no files were written to your repository.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
