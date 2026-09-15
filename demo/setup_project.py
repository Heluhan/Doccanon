#!/usr/bin/env python3
"""Build the throwaway governed project used by the opencode README recording.

The project is created from ``demo/fixture`` and then brought to a governed,
synchronized DocCanon state with the real helper. The recording runs opencode
inside the generated project.

Usage:
    python3 demo/setup_project.py [--path /tmp/doccanon-demo-project]
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
FIXTURE = Path(__file__).resolve().parent / "fixture"


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


def build(project: Path, stale: bool = False) -> None:
    if project.exists():
        shutil.rmtree(project)
    shutil.copytree(FIXTURE, project)
    git(project, "init", "-q")
    git(project, "config", "user.email", "demo@doccanon.local")
    git(project, "config", "user.name", "DocCanon Demo")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "initial session service")

    doccanon(project, "enable")
    doccanon(
        project,
        "mark-verified",
        "docs/features/session.md",
        "--covers",
        "src/auth/session.py",
        "--domain",
        "features",
        "--feature",
        "session-recovery",
    )
    promoted = doccanon(project, "promote", "--domain", "features")
    if promoted.get("status") != "governed":
        raise SystemExit(f"project did not reach governed status: {promoted}")
    git(project, "add", "-A")
    git(project, "commit", "-qm", "govern session recovery")

    fresh = doccanon(project, "check")
    if fresh.get("status") != "synchronized":
        raise SystemExit(f"project is not synchronized: {fresh}")

    if stale:
        make_stale(project)


def make_stale(project: Path) -> None:
    """Change governed code without touching its canonical owner.

    This is the ordinary developer mistake DocCanon is designed to catch:
    ``src/auth/session.py`` gains an empty-state guard, while
    ``docs/features/session.md`` still describes the previous behavior.
    """
    session = project / "src" / "auth" / "session.py"
    text = session.read_text(encoding="utf-8")
    text = text.replace(
        '    if not record or record.get("user_id") != user_id:\n'
        "        return Session(user_id=user_id)\n"
        '    return Session(user_id=user_id, state=dict(record["state"]))\n',
        '    if not record or record.get("user_id") != user_id:\n'
        "        return Session(user_id=user_id)\n"
        '    state = dict(record.get("state") or {})\n'
        "    if not state:\n"
        "        return Session(user_id=user_id)\n"
        "    return Session(user_id=user_id, state=state)\n",
    )
    session.write_text(text, encoding="utf-8")

    tests = project / "tests" / "test_session.py"
    tests.write_text(
        tests.read_text(encoding="utf-8")
        + "\n\ndef test_empty_state_starts_clean():\n"
        '    store = MemoryStore({"u1": {"user_id": "u1", "state": {}}})\n'
        '    assert recover_session(store, "u1").state == {}\n',
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default="/tmp/doccanon-demo-project")
    parser.add_argument(
        "--stale",
        action="store_true",
        help="after governing, change covered code without updating its owner",
    )
    args = parser.parse_args()
    project = Path(args.path).resolve()
    build(project, stale=args.stale)
    print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
