#!/usr/bin/env python3
"""Install DocCanon for one or more coding-agent hosts.

The installer copies the complete skill directory so bundled references, assets,
and deterministic helpers remain available. Existing unowned directories are
never overwritten. Updates of installer-owned copies create a backup first.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
SOURCE = REPO_ROOT / "skills" / "doccanon"
MANIFEST = REPO_ROOT / ".codex-plugin" / "plugin.json"
MARKER = ".doccanon-install.json"

PROJECT_TARGETS = {
    "universal": Path(".agents/skills/doccanon"),
    "codex": Path(".agents/skills/doccanon"),
    "copilot": Path(".github/skills/doccanon"),
    "claude": Path(".claude/skills/doccanon"),
    "gemini": Path(".gemini/skills/doccanon"),
    "opencode": Path(".opencode/skills/doccanon"),
    "cline": Path(".cline/skills/doccanon"),
}

USER_TARGETS = {
    "universal": Path(".agents/skills/doccanon"),
    "codex": Path(".codex/skills/doccanon"),
    "copilot": Path(".copilot/skills/doccanon"),
    "claude": Path(".claude/skills/doccanon"),
    "gemini": Path(".gemini/skills/doccanon"),
    "opencode": Path(".config/opencode/skills/doccanon"),
    "cline": Path(".cline/skills/doccanon"),
}


class InstallError(RuntimeError):
    pass


def version() -> str:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["version"]


def target_path(agent: str, scope: str, project: Path, home: Path) -> Path:
    table = PROJECT_TARGETS if scope == "project" else USER_TARGETS
    base = project if scope == "project" else home
    return (base / table[agent]).resolve()


def owned_install(path: Path) -> bool:
    marker = path / MARKER
    if not marker.is_file():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return payload.get("product") == "doccanon" and payload.get("managed_by") == "install.py"


def installed_version(path: Path) -> str:
    try:
        payload = json.loads((path / MARKER).read_text(encoding="utf-8"))
        return str(payload.get("version", "unknown")).replace(os.sep, "-")
    except (OSError, json.JSONDecodeError):
        return "unknown"


def next_backup_path(destination: Path) -> Path:
    base = destination.with_name(destination.name + f".previous-{installed_version(destination)}")
    candidate = base
    index = 2
    while candidate.exists():
        candidate = destination.with_name(base.name + f"-{index}")
        index += 1
    return candidate


def cursor_rule_path(project: Path) -> Path:
    return project / ".cursor" / "rules" / "doccanon.mdc"


def cursor_rule(skill_path: Path, rule_path: Path) -> str:
    reference = os.path.relpath(skill_path / "SKILL.md", rule_path.parent).replace(os.sep, "/")
    return (
        "---\n"
        "description: Keep project documentation branch-aware, evidence-backed, and synchronized with code\n"
        "globs:\n"
        "alwaysApply: false\n"
        "---\n\n"
        "For substantive repository work, follow the complete DocCanon workflow in "
        f"@{reference}. Load only the referenced DocCanon resources needed for the current task.\n"
    )


def install_copy(destination: Path, agent: str, scope: str, dry_run: bool) -> dict[str, str]:
    action = "install"
    backup = ""
    if destination.exists():
        if not owned_install(destination):
            raise InstallError(
                f"refusing to overwrite unmanaged destination: {destination}\n"
                "Move it yourself or choose another agent/scope."
            )
        action = "update"
        backup_path = next_backup_path(destination)
        backup = str(backup_path)
        if not dry_run:
            destination.rename(backup_path)

    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_parent = Path(tempfile.mkdtemp(prefix=".doccanon-install-", dir=destination.parent))
        staged = temporary_parent / "doccanon"
        try:
            shutil.copytree(
                SOURCE,
                staged,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
            (staged / MARKER).write_text(
                json.dumps(
                    {
                        "product": "doccanon",
                        "version": version(),
                        "managed_by": "install.py",
                        "agent": agent,
                        "scope": scope,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            staged.rename(destination)
        except Exception:
            if not destination.exists() and backup:
                Path(backup).rename(destination)
            raise
        finally:
            shutil.rmtree(temporary_parent, ignore_errors=True)

    return {"agent": agent, "scope": scope, "action": action, "path": str(destination), "backup": backup}


def install_cursor(project: Path, dry_run: bool, install_skill: bool = True) -> list[dict[str, str]]:
    skill_path = target_path("universal", "project", project, Path.home())
    results = [install_copy(skill_path, "cursor", "project", dry_run)] if install_skill else []
    rule_path = cursor_rule_path(project)
    if rule_path.exists() and "DocCanon" not in rule_path.read_text(encoding="utf-8", errors="replace"):
        raise InstallError(f"refusing to overwrite unmanaged Cursor rule: {rule_path}")
    if not dry_run:
        rule_path.parent.mkdir(parents=True, exist_ok=True)
        rule_path.write_text(cursor_rule(skill_path, rule_path), encoding="utf-8")
    results.append(
        {"agent": "cursor", "scope": "project", "action": "write-rule", "path": str(rule_path), "backup": ""}
    )
    return results


def uninstall(destination: Path, dry_run: bool) -> dict[str, str]:
    if not destination.exists():
        return {"action": "already-absent", "path": str(destination)}
    if not owned_install(destination):
        raise InstallError(f"refusing to remove unmanaged destination: {destination}")
    if not dry_run:
        shutil.rmtree(destination)
    return {"action": "uninstall", "path": str(destination)}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the DocCanon agent skill")
    parser.add_argument(
        "--agent",
        action="append",
        choices=[*PROJECT_TARGETS, "cursor", "all"],
        help="Agent host. Repeat for several; default: universal.",
    )
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument("--project", default=".", help="Project root for project-scoped installs")
    parser.add_argument("--home", help=argparse.SUPPRESS)
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    agents = args.agent or ["universal"]
    if "all" in agents:
        agents = ["universal", "claude", "copilot", "gemini", "opencode", "cline", "cursor"]
    agents = list(dict.fromkeys(agents))
    if args.scope == "user" and "cursor" in agents:
        raise InstallError("Cursor compatibility uses a project rule; install it with --scope project")

    project = Path(args.project).expanduser().resolve()
    home = Path(args.home).expanduser().resolve() if args.home else Path.home()
    results: list[dict[str, str]] = []
    installed_destinations: set[Path] = set()
    for agent in agents:
        if agent == "cursor":
            if args.uninstall:
                results.append(uninstall(target_path("universal", "project", project, home), args.dry_run))
                rule = cursor_rule_path(project)
                if rule.exists() and "DocCanon" in rule.read_text(encoding="utf-8", errors="replace"):
                    if not args.dry_run:
                        rule.unlink()
                    results.append({"action": "uninstall-rule", "path": str(rule)})
            else:
                skill_path = target_path("universal", "project", project, home)
                results.extend(install_cursor(project, args.dry_run, install_skill=skill_path not in installed_destinations))
                installed_destinations.add(skill_path)
            continue
        destination = target_path(agent, args.scope, project, home)
        if destination in installed_destinations:
            continue
        if args.uninstall:
            results.append(uninstall(destination, args.dry_run))
        else:
            results.append(install_copy(destination, agent, args.scope, args.dry_run))
        installed_destinations.add(destination)

    payload = {"status": "ok", "version": version(), "dry_run": args.dry_run, "results": results}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"DocCanon {payload['version']}: {'dry run' if args.dry_run else 'done'}")
        for item in results:
            print(f"- {item['action']}: {item['path']}")
            if item.get("backup"):
                print(f"  previous copy: {item['backup']}")
        if not args.uninstall:
            print("Start a new agent session so the host discovers the skill.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InstallError as error:
        print(f"DocCanon install error: {error}", file=sys.stderr)
        raise SystemExit(2)
