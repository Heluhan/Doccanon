from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "doccanon" / "scripts" / "doccanon.py"
SKILL_ROOT = Path(__file__).resolve().parents[1] / "skills" / "doccanon"


def run(command: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result


def git(root: Path, *args: str) -> str:
    return run(["git", *args], root).stdout.strip()


class DocCanonCLITest(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        git(root, "init", "-q")
        git(root, "config", "user.email", "test@example.com")
        git(root, "config", "user.name", "DocCanon Test")
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("print('v1')\n", encoding="utf-8")
        git(root, "add", ".")
        git(root, "commit", "-qm", "initial")
        return temp, root

    def cli(self, root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run(["python3", str(SCRIPT), "--project", str(root), *args], root, check=check)

    def write_architecture(self, path: Path) -> None:
        path.write_text(
            "# Architecture\n\n"
            "## Current behavior\n\n"
            "The application executes through `src/app.py`. This document owns the current process "
            "boundary, the observable startup behavior, and the rule that later changes must preserve "
            "the repository entry point unless the architecture contract changes in the same commit.\n\n"
            "## Verification\n\n"
            "Run `python3 src/app.py` from the repository root and verify that the process exits successfully.\n",
            encoding="utf-8",
        )

    def test_skill_links_self_contained_operating_contract(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (SKILL_ROOT / "references" / "operating-contract.md").read_text(encoding="utf-8")
        self.assertIn("references/operating-contract.md", skill)
        for phrase in (
            "Non-negotiable loop",
            "Project-local information architecture",
            "Admission",
            "Distribution language",
            "Knowledge quality",
            "Migration",
            "Branches and history",
            "Optional Grill with Docs relationship",
        ):
            self.assertIn(phrase, contract)

    def test_enable_and_disable_are_project_local(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)

        enabled = json.loads(self.cli(root, "enable", "--json").stdout)
        self.assertEqual("enabled", enabled["status"])
        self.assertTrue((root / ".doccanon.yml").exists())
        self.assertTrue((root / "CONTEXT.md").exists())
        self.assertTrue((root / "docs" / "README.md").exists())
        bootstrapping = self.cli(root, "check", "--json", check=False)
        self.assertEqual(1, bootstrapping.returncode)
        self.assertEqual("bootstrap-incomplete", json.loads(bootstrapping.stdout)["status"])

        disabled = json.loads(self.cli(root, "disable", "--reason", "one-off page", "--json").stdout)
        self.assertEqual("disabled", disabled["status"])
        self.assertIn('status: "disabled"', (root / ".doccanon.yml").read_text(encoding="utf-8"))
        self.assertTrue((root / "docs" / "README.md").exists())
        checked = json.loads(self.cli(root, "check", "--json").stdout)
        self.assertEqual("disabled", checked["status"])

    def test_staged_covered_code_requires_doc_update(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        git(root, "add", ".")
        git(root, "commit", "-qm", "enable doccanon")
        anchor = git(root, "rev-parse", "HEAD")
        architecture = root / "docs" / "architecture.md"
        self.write_architecture(architecture)
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        self.cli(root, "promote", "--domain", "architecture")
        git(root, "add", ".")
        git(root, "commit", "-qm", "document architecture")

        (root / "src" / "app.py").write_text("print('v2')\n", encoding="utf-8")
        git(root, "add", "src/app.py")
        stale = self.cli(root, "check", "--staged", "--json", check=False)
        self.assertEqual(1, stale.returncode)
        payload = json.loads(stale.stdout)
        self.assertEqual("stale", payload["status"])
        self.assertEqual("stale-document", payload["findings"][0]["code"])

        git(root, "commit", "-qm", "change covered code without docs")
        committed_stale = self.cli(root, "check", "--json", check=False)
        self.assertEqual(1, committed_stale.returncode)
        self.assertEqual("stale", json.loads(committed_stale.stdout)["status"])

        architecture.write_text(architecture.read_text(encoding="utf-8") + "Updated for v2.\n", encoding="utf-8")
        git(root, "add", "docs/architecture.md")
        synchronized = json.loads(self.cli(root, "check", "--json").stdout)
        self.assertEqual("synchronized", synchronized["status"])
        self.assertEqual("pending-sync", synchronized["findings"][0]["code"])

    def test_enable_renders_agent_entry_projection(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        enabled = json.loads(self.cli(root, "enable", "--json").stdout)
        created = set(enabled["created"])
        self.assertIn("AGENTS.md", created)
        self.assertIn("CLAUDE.md", created)
        entry = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Generated by DocCanon", entry)
        self.assertIn("`CONTEXT.md`", entry)
        self.assertIn("<!-- doccanon:custom:start -->", entry)
        self.assertIn("<!-- doccanon:custom:end -->", entry)
        adapter = (root / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("@AGENTS.md", adapter)
        checked = json.loads(self.cli(root, "check", "--json", check=False).stdout)
        codes = {item["code"] for item in checked["findings"]}
        self.assertNotIn("missing-agent-entry", codes)
        self.assertNotIn("stale-agent-entry", codes)

    def test_render_is_idempotent_and_preserves_custom_section(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        entry_path = root / "AGENTS.md"
        original = entry_path.read_text(encoding="utf-8")
        entry_path.write_text(
            original.replace(
                "<!-- Add project- or tool-specific notes here.",
                "## Local notes\n\nKeep the deploy token in 1Password.\n\n"
                "<!-- Add project- or tool-specific notes here.",
            ),
            encoding="utf-8",
        )
        current = json.loads(self.cli(root, "render", "--json").stdout)
        self.assertEqual("current", current["status"])
        self.assertTrue(all(not item["changed"] for item in current["files"]))
        self.assertIn("Keep the deploy token in 1Password.", entry_path.read_text(encoding="utf-8"))
        checked = json.loads(self.cli(root, "render", "--check", "--json").stdout)
        self.assertEqual("current", checked["status"])

    def test_entry_tracks_current_docs_and_excludes_history(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        architecture = root / "docs" / "architecture.md"
        self.write_architecture(architecture)
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        (root / "docs" / "old-plan.md").write_text(
            "---\ndoccanon_authority: snapshot\n---\n# Old plan\n\nRetired material.\n",
            encoding="utf-8",
        )
        self.cli(root, "promote", "--domain", "architecture")
        entry = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("`docs/architecture.md`", entry)
        self.assertNotIn("old-plan", entry)
        checked = json.loads(self.cli(root, "check", "--json").stdout)
        self.assertEqual("synchronized", checked["status"])

        git(root, "add", ".")
        git(root, "commit", "-qm", "govern architecture")
        operations = root / "docs" / "operations" / "runbook.md"
        operations.parent.mkdir()
        operations.write_text(
            "# Operations\n\n## Current behavior\n\n"
            "The runbook owns deployment checks for `src/app.py`. It states the startup command, the "
            "expected exit status, and the rule that later operational changes update this owner in the "
            "same commit as the code they affect.\n\n"
            "## Verification\n\nRun `python3 src/app.py` from the repository root.\n",
            encoding="utf-8",
        )
        self.cli(
            root,
            "mark-verified",
            "docs/operations/runbook.md",
            "--covers",
            "src/**",
            "--domain",
            "operations",
        )
        stale = json.loads(self.cli(root, "check", "--json", check=False).stdout)
        self.assertEqual("stale", stale["status"])
        self.assertIn("stale-agent-entry", {item["code"] for item in stale["findings"]})
        self.cli(root, "render")
        ready = json.loads(self.cli(root, "check", "--json").stdout)
        self.assertEqual("synchronized", ready["status"])

    def test_legacy_agent_files_are_adopted_into_custom_section(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "AGENTS.md").write_text("# House rules\n\nUse pnpm.\n", encoding="utf-8")
        (root / "CLAUDE.md").write_text("# Claude notes\n\nPrefer plan mode.\n", encoding="utf-8")
        git(root, "add", ".")
        git(root, "commit", "-qm", "legacy agent files")
        self.cli(root, "enable")
        entry = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Generated by DocCanon", entry)
        self.assertIn("Use pnpm.", entry)
        self.assertIn("<!-- doccanon:custom:start -->", entry)
        adapter = (root / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("@AGENTS.md", adapter)
        self.assertIn("Prefer plan mode.", adapter)
        rendered = json.loads(self.cli(root, "render", "--json").stdout)
        self.assertEqual("current", rendered["status"])

    def test_context_file_is_routable_canonical_terminology(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        context = root / "CONTEXT.md"
        text = context.read_text(encoding="utf-8")
        self.assertIn("doccanon_authority: human-confirmed", text)
        context.write_text(
            text + "\n### Ledger seal\n\nThe ledger seal is the canonical name for the per-account "
            "integrity token; do not call it a balance hash.\n",
            encoding="utf-8",
        )
        payload = json.loads(
            self.cli(
                root,
                "context",
                "--intent",
                "explain the ledger seal integrity token",
                "--json",
                check=False,
            ).stdout
        )
        authorities = {item["path"]: item["authority"] for item in payload["documents"]}
        self.assertEqual("human-confirmed", authorities.get("CONTEXT.md"))

    def test_unconfirmed_context_file_warns(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        context = root / "CONTEXT.md"
        body = context.read_text(encoding="utf-8").split("\n---\n", 1)[1]
        context.write_text(body.lstrip("\n"), encoding="utf-8")
        checked = json.loads(self.cli(root, "check", "--json", check=False).stdout)
        warnings = [item for item in checked["findings"] if item["code"] == "unconfirmed-context-file"]
        self.assertEqual(1, len(warnings))
        self.assertEqual("warning", warnings[0]["level"])

    def test_plan_authority_routes_and_renders_in_entry(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        plans = root / "docs" / "plans"
        plans.mkdir()
        (plans / "v1-launch.md").write_text(
            "---\ndoccanon_authority: plan\ndoccanon_plan: v1-launch\n"
            "doccanon_status: active\ndoccanon_target: v1.0.0\n---\n\n"
            "# v1 launch\n\n## Goal\n\nShip the ledger seal to production with a verified rollback path.\n\n"
            "## Release conditions\n\n- [ ] Load test passes\n",
            encoding="utf-8",
        )
        rendered = json.loads(self.cli(root, "render", "--json").stdout)
        self.assertEqual("rendered", rendered["status"])
        entry = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Plans (future work)", entry)
        self.assertIn("`docs/plans/v1-launch.md`", entry)
        payload = json.loads(
            self.cli(
                root,
                "context",
                "--intent",
                "check ledger seal launch readiness",
                "--json",
                check=False,
            ).stdout
        )
        authorities = {item["path"]: item["authority"] for item in payload["documents"]}
        self.assertEqual("plan", authorities.get("docs/plans/v1-launch.md"))

    def test_plan_warnings_for_inactive_and_unclassified_documents(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        plans = root / "docs" / "plans"
        plans.mkdir()
        (plans / "done.md").write_text(
            "---\ndoccanon_authority: plan\ndoccanon_plan: done\ndoccanon_status: shipped\n---\n\n"
            "# Shipped plan\n\n## Goal\n\nAlready shipped.\n",
            encoding="utf-8",
        )
        (plans / "drafty.md").write_text("# Drafty plan\n\nNo authority yet.\n", encoding="utf-8")
        checked = json.loads(self.cli(root, "check", "--json", check=False).stdout)
        by_code = {item["code"]: item for item in checked["findings"]}
        self.assertEqual("warning", by_code["inactive-plan-not-retired"]["level"])
        self.assertEqual("warning", by_code["unclassified-plan-document"]["level"])

    def test_release_gate_requires_a_ready_plan(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        architecture = root / "docs" / "architecture.md"
        self.write_architecture(architecture)
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        self.cli(root, "promote", "--domain", "architecture")
        git(root, "add", ".")
        git(root, "commit", "-qm", "govern architecture")

        (root / "src" / "app.py").write_text("print('v2')\n", encoding="utf-8")
        architecture.write_text(
            architecture.read_text(encoding="utf-8") + "\nThe v2 behavior is now current.\n",
            encoding="utf-8",
        )
        plans = root / "docs" / "plans"
        plans.mkdir()
        plan = plans / "v1-launch.md"
        plan.write_text(
            "---\ndoccanon_authority: plan\ndoccanon_plan: v1-launch\n"
            "doccanon_status: active\ndoccanon_target: v1.0.0\n---\n\n"
            "# v1 launch\n\n## Goal\n\nShip the ledger seal to production.\n\n"
            "## Release conditions\n\n- [ ] Load test passes\n",
            encoding="utf-8",
        )
        blocked = self.cli(
            root,
            "sync",
            "complete",
            "--title",
            "Ledger seal v1",
            "--summary",
            "Prepared the ledger seal release.",
            "--verification",
            "python3 src/app.py passed",
            "--release-version",
            "v1.0.0",
            "--release-evidence",
            "staging deploy smoke passed",
            "--json",
            check=False,
        )
        self.assertEqual(1, blocked.returncode)
        blocked_payload = json.loads(blocked.stdout)
        codes = {item["code"] for item in blocked_payload["blockers"]}
        self.assertIn("plan-not-ready-for-release", codes)
        self.assertEqual(
            [{"plan": "docs/plans/v1-launch.md", "status": "active", "target": "v1.0.0"}],
            blocked_payload["release_readiness"],
        )

        plan.write_text(
            plan.read_text(encoding="utf-8").replace("doccanon_status: active", "doccanon_status: ready"),
            encoding="utf-8",
        )
        completed = json.loads(
            self.cli(
                root,
                "sync",
                "complete",
                "--title",
                "Ledger seal v1",
                "--summary",
                "Prepared the ledger seal release.",
                "--verification",
                "python3 src/app.py passed",
                "--release-version",
                "v1.0.0",
                "--release-evidence",
                "staging deploy smoke passed",
                "--json",
            ).stdout
        )
        self.assertEqual("synchronized", completed["status"])
        self.assertEqual(
            [{"plan": "docs/plans/v1-launch.md", "status": "ready", "target": "v1.0.0"}],
            completed["release_readiness"],
        )

    def test_retire_relocates_stamps_and_excludes_from_search(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        notes = root / "notes"
        notes.mkdir()
        (notes / "legacy.md").write_text("# Legacy notes\n\nOld architecture plan from 2024.\n", encoding="utf-8")
        retired = json.loads(
            self.cli(
                root,
                "retire",
                "notes/legacy.md",
                "--reason",
                "Superseded by the documented architecture owner.",
                "--owner",
                "docs/architecture.md",
                "--json",
            ).stdout
        )
        self.assertEqual("retired", retired["status"])
        self.assertEqual(".doccanon/archive/notes/legacy.md", retired["archived_to"])
        self.assertFalse((root / "notes" / "legacy.md").exists())
        archived = (root / ".doccanon" / "archive" / "notes" / "legacy.md").read_text(encoding="utf-8")
        self.assertIn("doccanon_authority: historical", archived)
        self.assertIn("Retired by DocCanon", archived)
        self.assertIn("docs/architecture.md", archived)
        ignore = (root / ".ignore").read_text(encoding="utf-8")
        self.assertIn(".doccanon/archive/", ignore)
        self.assertTrue(retired["search_ignore"]["updated"])

        scanned = json.loads(self.cli(root, "inventory", "--json").stdout)
        self.assertNotIn(
            ".doccanon/archive/notes/legacy.md",
            {item["path"] for item in scanned["candidates"]},
        )

    def test_retire_pointer_and_active_authority_protection(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        legacy = root / "OLD_GUIDE.md"
        legacy.write_text("# Old guide\n\nHistoric guidance.\n", encoding="utf-8")
        pointer = json.loads(
            self.cli(
                root,
                "retire",
                "OLD_GUIDE.md",
                "--owner",
                "CONTEXT.md",
                "--pointer",
                "--json",
            ).stdout
        )
        self.assertEqual("OLD_GUIDE.md", pointer["pointer"])
        stub = legacy.read_text(encoding="utf-8")
        self.assertIn(".doccanon/archive/OLD_GUIDE.md", stub)
        self.assertIn("not current truth", stub)
        self.assertTrue((root / ".doccanon" / "archive" / "OLD_GUIDE.md").exists())

        refused = self.cli(root, "retire", "CONTEXT.md", "--json", check=False)
        self.assertEqual(2, refused.returncode)
        self.assertEqual("error", json.loads(refused.stdout)["status"])

        active = root / "notes"
        active.mkdir()
        (active / "active.md").write_text(
            "---\ndoccanon_authority: human-confirmed\n---\n\n# Active notes\n", encoding="utf-8"
        )
        refused_active = self.cli(root, "retire", "notes/active.md", "--json", check=False)
        self.assertEqual(2, refused_active.returncode)
        self.assertIn("active authority", json.loads(refused_active.stdout)["error"])

    def test_archive_without_search_ignore_warns(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        archived = root / ".doccanon" / "archive"
        archived.mkdir(parents=True)
        (archived / "old.md").write_text("old\n", encoding="utf-8")
        checked = json.loads(self.cli(root, "check", "--json", check=False).stdout)
        self.assertIn("archive-not-search-excluded", {item["code"] for item in checked["findings"]})
        (root / ".ignore").write_text(".doccanon/archive/\n", encoding="utf-8")
        checked_again = json.loads(self.cli(root, "check", "--json", check=False).stdout)
        self.assertNotIn("archive-not-search-excluded", {item["code"] for item in checked_again["findings"]})

    def test_context_prefers_governed_docs_and_excludes_history(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        current = root / "docs" / "session-recovery.md"
        current.write_text(
            "# Session recovery\n\n"
            "## Current behavior\n\n"
            "The recovery path is owned by `src/app.py`. It restores only the current user's saved "
            "state, rejects foreign state, and starts cleanly when no durable recovery record exists. "
            "Changes must preserve ownership checks and explicit fallback behavior.\n\n"
            "## Verification\n\nRun `python3 src/app.py` and verify the recovery path completes.\n",
            encoding="utf-8",
        )
        historical = root / "docs" / "session-recovery-plan.md"
        historical.write_text(
            "---\ndoccanon_authority: snapshot\n---\n# Session recovery plan\n\nOld proposal.\n",
            encoding="utf-8",
        )
        self.cli(
            root,
            "mark-verified",
            "docs/session-recovery.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        self.cli(root, "promote", "--domain", "architecture")
        payload = json.loads(self.cli(root, "context", "--intent", "session recovery", "--json").stdout)
        self.assertEqual("docs/session-recovery.md", payload["documents"][0]["path"])
        self.assertEqual("current-state", payload["documents"][0]["authority"])
        self.assertEqual(["src/app.py"], payload["documents"][0]["code_references"])
        self.assertNotIn("docs/session-recovery-plan.md", {item["path"] for item in payload["documents"]})

        with_history = json.loads(
            self.cli(root, "context", "--intent", "session recovery", "--include-historical", "--json").stdout
        )
        self.assertIn("docs/session-recovery-plan.md", {item["path"] for item in with_history["documents"]})

    def test_context_filters_generic_terms(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        billing = root / "docs" / "billing.md"
        billing.write_text(
            "---\ndoccanon_authority: human-confirmed\n---\n"
            "# Free chapter boundary\n\nFree access covers two complete chapters; later chapters require entitlement.\n",
            encoding="utf-8",
        )
        unrelated = root / "docs" / "generic.md"
        unrelated.write_text(
            "---\ndoccanon_authority: human-confirmed\n---\n"
            "# Generic feature update\n\nThis document describes ordinary feature changes and updates.\n",
            encoding="utf-8",
        )
        payload = json.loads(
            self.cli(root, "context", "--intent", "Please change the free chapter boundary feature", "--json", check=False).stdout
        )
        self.assertEqual("docs/billing.md", payload["documents"][0]["path"])
        self.assertNotIn("please", payload["query_terms"])
        self.assertNotIn("change", payload["query_terms"])
        self.assertNotIn("feature", payload["query_terms"])

    def test_thin_current_state_document_cannot_pass_trust_gate(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        architecture = root / "docs" / "architecture.md"
        architecture.write_text("# Architecture\n", encoding="utf-8")
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        checked = self.cli(root, "check", "--json", check=False)
        findings = json.loads(checked.stdout)["findings"]
        self.assertIn("thin-current-state-document", {item["code"] for item in findings})
        promoted = self.cli(root, "promote", "--domain", "architecture", "--json", check=False)
        self.assertEqual(2, promoted.returncode)

    def test_inventory_is_path_agnostic(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        odd = root / "misc" / "final-thoughts.xyz"
        odd.parent.mkdir()
        odd.write_text("# Architecture Decision\n\nContext: keep one process.\nDecision: accepted.\n", encoding="utf-8")
        payload = json.loads(self.cli(root, "inventory", "--json").stdout)
        paths = {item["path"] for item in payload["candidates"]}
        self.assertIn("misc/final-thoughts.xyz", paths)

    def test_migration_manifest_blocks_promotion_until_resolved(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        current = root / "docs" / "architecture.md"
        self.write_architecture(current)
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        created = json.loads(self.cli(root, "migrate", "scan", "--allow-dirty", "--json").stdout)
        self.assertTrue(created["created"])
        self.assertEqual("incomplete", created["status"])
        blocked = self.cli(
            root,
            "promote",
            "--domain",
            "architecture",
            "--manifest",
            "docs/operations/doccanon-migration.json",
            check=False,
        )
        self.assertEqual(2, blocked.returncode)

        manifest = root / "docs" / "operations" / "doccanon-migration.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        for entry in payload["entries"]:
            entry.update(
                {
                    "classification": "historical",
                    "action": "archive",
                    "status": "historical",
                    "disposition_reason": "No current durable knowledge remains after review.",
                    "requires_review": False,
                    "conflicts": [],
                }
            )
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        no_absorption = json.loads(self.cli(root, "migrate", "status", "--json").stdout)
        self.assertEqual("complete", no_absorption["status"])
        self.assertEqual(0, no_absorption["integrated_count"])

        first = payload["entries"][0]
        first.update(
            {
                "classification": "current-architecture",
                "action": "merge",
                "status": "integrated",
                "integrations": [
                    {
                        "target": "docs/architecture.md",
                        "sections": ["Architecture"],
                        "absorbed_claims": ["The application entry point is src/app.py."],
                    }
                ],
                "verification": ["src/app.py"],
                "residual_claims": [],
                "source_disposition": "superseded",
            }
        )
        first.pop("disposition_reason", None)
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        migration = json.loads(self.cli(root, "migrate", "status", "--json").stdout)
        self.assertEqual("complete", migration["status"])
        self.assertEqual(1, migration["integrated_count"])
        self.assertEqual(0, migration["residual_claim_count"])
        promoted = json.loads(
            self.cli(
                root,
                "promote",
                "--domain",
                "architecture",
                "--manifest",
                "docs/operations/doccanon-migration.json",
                "--json",
            ).stdout
        )
        self.assertEqual("governed", promoted["status"])

    def test_non_integrated_disposition_requires_evidence(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        manifest = root / "docs" / "operations" / "doccanon-migration.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 2,
            "candidate_count": 1,
            "entries": [
                {
                    "source": "old-plan.md",
                    "classification": "future-plan-or-draft",
                    "action": "archive",
                    "status": "historical",
                    "confidence": "high",
                    "evidence": [],
                    "conflicts": [],
                    "requires_review": False,
                    "disposition_reason": "The proposal was never implemented.",
                }
            ],
        }
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        blocked = self.cli(root, "migrate", "status", "--json", check=False)
        self.assertEqual(1, blocked.returncode)
        self.assertIn("record evidence", " ".join(json.loads(blocked.stdout)["findings"]))

        payload["entries"][0]["evidence"] = ["Git history and current routes contain no implementation"]
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        complete = json.loads(self.cli(root, "migrate", "status", "--json").stdout)
        self.assertEqual("complete", complete["status"])
        self.assertEqual(0, complete["integrated_count"])

    def test_rejected_claims_require_reason_and_evidence(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        target = root / "docs" / "architecture.md"
        target.write_text("# Architecture\n\n## Runtime topology\n\nCurrent service.\n", encoding="utf-8")
        manifest = root / "docs" / "operations" / "doccanon-migration.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 2,
            "candidate_count": 1,
            "entries": [
                {
                    "source": "legacy-architecture.md",
                    "classification": "mixed-current-and-stale",
                    "action": "merge",
                    "status": "integrated",
                    "confidence": "high",
                    "integrations": [
                        {
                            "target": "docs/architecture.md",
                            "sections": ["Runtime topology"],
                            "absorbed_claims": ["The current service owns the API."],
                        }
                    ],
                    "verification": ["src/app.py"],
                    "residual_claims": [],
                    "rejected_claims": [
                        {
                            "claim": "The legacy worker owns the API.",
                            "reason": "",
                            "evidence": [],
                        }
                    ],
                    "source_disposition": "superseded",
                    "evidence": ["src/app.py"],
                    "conflicts": [],
                    "requires_review": False,
                }
            ],
        }
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        blocked = self.cli(root, "migrate", "status", "--json", check=False)
        self.assertEqual(1, blocked.returncode)
        findings = " ".join(json.loads(blocked.stdout)["findings"])
        self.assertIn("record a reason", findings)
        self.assertIn("record evidence", findings)

    def test_legacy_manifest_and_link_only_receipts_do_not_prove_integration(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        target = root / "docs" / "architecture.md"
        target.write_text("# Architecture\n\n## Runtime topology\n\nCurrent service.\n", encoding="utf-8")
        manifest = root / "docs" / "operations" / "doccanon-migration.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "candidate_count": 1,
            "entries": [
                {
                    "source": "notes.md",
                    "classification": "current-architecture",
                    "target": "docs/architecture.md",
                    "action": "merge",
                    "status": "verified",
                    "confidence": "high",
                    "evidence": ["link created"],
                    "conflicts": [],
                    "requires_review": False,
                }
            ],
        }
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        legacy = self.cli(root, "migrate", "status", "--json", check=False)
        self.assertEqual(1, legacy.returncode)
        legacy_findings = " ".join(json.loads(legacy.stdout)["findings"])
        self.assertIn("schema_version must be 2", legacy_findings)

        payload["schema_version"] = 2
        payload["entries"][0]["status"] = "integrated"
        payload["entries"][0]["source_disposition"] = "superseded"
        payload["entries"][0]["verification"] = ["src/app.py"]
        payload["entries"][0]["residual_claims"] = []
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        link_only = self.cli(root, "migrate", "status", "--json", check=False)
        self.assertEqual(1, link_only.returncode)
        self.assertIn(
            "canonical integration receipt",
            " ".join(json.loads(link_only.stdout)["findings"]),
        )

    def test_migration_requires_existing_target_sections_and_zero_residual_claims(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        target = root / "docs" / "architecture.md"
        target.write_text("# Architecture\n\n## Runtime topology\n\nCurrent service.\n", encoding="utf-8")
        manifest = root / "docs" / "operations" / "doccanon-migration.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 2,
            "candidate_count": 1,
            "entries": [
                {
                    "source": "notes.md",
                    "classification": "current-architecture",
                    "action": "merge",
                    "status": "integrated",
                    "confidence": "high",
                    "integrations": [
                        {
                            "target": "docs/architecture.md",
                            "sections": ["Missing section"],
                            "absorbed_claims": ["The service owns the API."],
                        }
                    ],
                    "verification": ["src/app.py"],
                    "residual_claims": ["Unresolved ownership rationale"],
                    "source_disposition": "superseded",
                    "evidence": ["src/app.py"],
                    "conflicts": [],
                    "requires_review": False,
                }
            ],
        }
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        blocked = self.cli(root, "migrate", "status", "--json", check=False)
        self.assertEqual(1, blocked.returncode)
        report = json.loads(blocked.stdout)
        self.assertEqual(1, report["residual_claim_count"])
        self.assertIn("missing sections", " ".join(report["findings"]))

    def test_hook_install_and_uninstall(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        blocked = self.cli(root, "hook", "install", "--json", check=False)
        self.assertEqual(2, blocked.returncode)
        architecture = root / "docs" / "architecture.md"
        self.write_architecture(architecture)
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        self.cli(root, "promote", "--domain", "architecture")
        installed = json.loads(self.cli(root, "hook", "install", "--json").stdout)
        hook = Path(installed["path"])
        self.assertTrue(hook.exists())
        self.assertIn("doccanon managed block", hook.read_text(encoding="utf-8"))
        removed = json.loads(self.cli(root, "hook", "uninstall", "--json").stdout)
        self.assertEqual("uninstalled", removed["status"])
        self.assertFalse(hook.exists())

    def test_features_domain_requires_one_contract_per_current_feature(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        features_dir = root / "docs" / "features"
        features_dir.mkdir()
        contract = features_dir / "session-recovery.md"
        contract.write_text(
            "# Session recovery\n\n"
            "## User outcome\nResume interrupted work without losing the current session.\n\n"
            "## Scope\nOwn authenticated recovery for the current user's active session only.\n\n"
            "## Behavior\nLoad a valid saved session, otherwise start a clean recoverable session.\n\n"
            "## States and failure modes\nSaved, missing, invalid, and foreign session states have explicit outcomes.\n\n"
            "## Data and dependencies\nDurable session state is read by the application entry process.\n\n"
            "## Invariants\nNever restore another user's state or infer completion from navigation.\n\n"
            "## Change guidance\nPreserve ownership and fallback checks when adding restore sources; update persistence, recovery, error handling, and tests together.\n\n"
            "## Implementation\nThe stable entry point is `src/app.py` and owns recovery dispatch.\n\n"
            "## Verification\nRun `python3 src/app.py` and exercise saved and missing state.\n",
            encoding="utf-8",
        )
        self.cli(
            root,
            "mark-verified",
            "docs/features/session-recovery.md",
            "--covers",
            "src/**",
            "--domain",
            "features",
            "--feature",
            "session-recovery",
        )
        manifest = {
            "schema_version": 1,
            "features": [
                {
                    "id": "session-recovery",
                    "name": "Session recovery",
                    "status": "current",
                    "document": "docs/features/session-recovery.md",
                    "code_patterns": ["src/**"],
                }
            ],
        }
        (features_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        feature_status = json.loads(self.cli(root, "features", "status", "--json").stdout)
        self.assertEqual("complete", feature_status["status"])
        promoted = json.loads(self.cli(root, "promote", "--domain", "features", "--json").stdout)
        self.assertEqual("governed", promoted["status"])

        contract.write_text("# Session recovery\n\nToo short.\n", encoding="utf-8")
        incomplete = self.cli(root, "features", "status", "--json", check=False)
        self.assertEqual(1, incomplete.returncode)
        self.assertEqual("incomplete", json.loads(incomplete.stdout)["status"])

    def test_legacy_enabled_config_is_bootstrapping_not_synchronized(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / ".doccanon.yml").write_text(
            'schema_version: 1\nstatus: "enabled"\ndocs_root: "docs"\ncontext_file: "CONTEXT.md"\n',
            encoding="utf-8",
        )
        (root / "docs").mkdir()
        (root / "docs" / "README.md").write_text("# Docs\n", encoding="utf-8")
        (root / "CONTEXT.md").write_text("# Context\n", encoding="utf-8")
        checked = self.cli(root, "check", "--json", check=False)
        payload = json.loads(checked.stdout)
        self.assertEqual(1, checked.returncode)
        self.assertEqual("bootstrap-incomplete", payload["status"])
        self.assertEqual(0, payload["coverage"]["current_state_documents"])

    def test_feature_branch_initialization_requires_explicit_override(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        git(root, "checkout", "-qb", "feature/session-recovery")
        blocked = self.cli(root, "enable", "--json", check=False)
        self.assertEqual(2, blocked.returncode)
        self.assertIn("feature branch", json.loads(blocked.stdout)["error"])
        enabled = json.loads(self.cli(root, "enable", "--allow-feature-branch", "--json").stdout)
        self.assertEqual("feature/session-recovery", enabled["branch"]["current_branch"])

    def test_branch_preflight_requires_affected_document_update(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        integration = git(root, "branch", "--show-current")
        self.cli(root, "enable")
        architecture = root / "docs" / "architecture.md"
        self.write_architecture(architecture)
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        self.cli(root, "promote", "--domain", "architecture")
        git(root, "add", ".")
        git(root, "commit", "-qm", "govern docs")
        git(root, "checkout", "-qb", "feature/change-app")
        (root / "src" / "app.py").write_text("print('v2')\n", encoding="utf-8")
        git(root, "add", "src/app.py")
        git(root, "commit", "-qm", "change app without docs")
        blocked = self.cli(root, "preflight", "--target", integration, "--json", check=False)
        self.assertEqual(1, blocked.returncode)
        self.assertEqual("blocked", json.loads(blocked.stdout)["status"])
        architecture.write_text(architecture.read_text(encoding="utf-8") + "Updated behavior.\n", encoding="utf-8")
        git(root, "add", "docs/architecture.md")
        git(root, "commit", "-qm", "update architecture docs")
        ready = json.loads(self.cli(root, "preflight", "--target", integration, "--json").stdout)
        self.assertEqual("ready", ready["status"])
        self.assertEqual("feature", ready["branch"]["kind"])

    def test_sync_closes_loop_and_records_documentation_impact(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        architecture = root / "docs" / "architecture.md"
        self.write_architecture(architecture)
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        self.cli(root, "promote", "--domain", "architecture")
        git(root, "add", ".")
        git(root, "commit", "-qm", "govern architecture")

        (root / "src" / "app.py").write_text("print('v2')\n", encoding="utf-8")
        plan = json.loads(self.cli(root, "sync", "plan", "--json").stdout)
        self.assertEqual(["docs/architecture.md"], plan["stale_owner_docs"])
        blocked = self.cli(
            root,
            "sync",
            "complete",
            "--title",
            "Application behavior",
            "--summary",
            "Changed the application behavior.",
            "--verification",
            "python3 src/app.py passed",
            "--json",
            check=False,
        )
        self.assertEqual(1, blocked.returncode)
        self.assertIn(
            "stale-current-state-owner",
            {item["code"] for item in json.loads(blocked.stdout)["blockers"]},
        )

        architecture.write_text(architecture.read_text(encoding="utf-8") + "\nThe v2 behavior is now current.\n", encoding="utf-8")
        completed = json.loads(
            self.cli(
                root,
                "sync",
                "complete",
                "--title",
                "Application behavior",
                "--summary",
                "Changed the application behavior.",
                "--verification",
                "python3 src/app.py passed",
                "--json",
            ).stdout
        )
        self.assertEqual("synchronized", completed["status"])
        self.assertEqual(["architecture"], completed["impact_receipt"]["affected_domains"])
        development_path = root / completed["development_log"]["path"]
        development_text = development_path.read_text(encoding="utf-8")
        self.assertIn("Affected domain: `architecture`", development_text)
        self.assertIn("Updated owner: `docs/architecture.md`", development_text)

    def test_sync_requires_receipts_for_every_unmapped_file_and_domain(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        architecture = root / "docs" / "architecture.md"
        self.write_architecture(architecture)
        self.cli(
            root,
            "mark-verified",
            "docs/architecture.md",
            "--covers",
            "src/**",
            "--domain",
            "architecture",
        )
        self.cli(root, "promote", "--domain", "architecture")
        git(root, "add", ".")
        git(root, "commit", "-qm", "govern architecture")

        scripts = root / "scripts"
        scripts.mkdir()
        (scripts / "fixture.py").write_text("print('fixture')\n", encoding="utf-8")
        plan = json.loads(self.cli(root, "sync", "plan", "--json").stdout)
        self.assertEqual(["scripts/fixture.py"], plan["unmapped_implementation_files"])
        blocked = self.cli(
            root,
            "sync",
            "complete",
            "--title",
            "Test fixture",
            "--summary",
            "Added a non-product test fixture.",
            "--verification",
            "python3 scripts/fixture.py passed",
            "--json",
            check=False,
        )
        blocker_codes = {item["code"] for item in json.loads(blocked.stdout)["blockers"]}
        self.assertIn("unmapped-implementation-file", blocker_codes)
        self.assertIn("unreviewed-domain", blocker_codes)

        completed = json.loads(
            self.cli(
                root,
                "sync",
                "complete",
                "--exclude-domain",
                "architecture=No architecture behavior or boundary changed.",
                "--exclude-file",
                "scripts/fixture.py=Non-product test fixture with no governed behavior.",
                "--title",
                "Test fixture",
                "--summary",
                "Added a non-product test fixture.",
                "--verification",
                "python3 scripts/fixture.py passed",
                "--json",
            ).stdout
        )
        self.assertEqual("synchronized", completed["status"])
        self.assertIn("architecture", completed["impact_receipt"]["excluded_domains"])
        self.assertIn("scripts/fixture.py", completed["impact_receipt"]["excluded_unmapped_files"])

    def test_development_and_release_logs_are_historical_context(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.cli(root, "enable")
        development = json.loads(
            self.cli(
                root,
                "log",
                "development",
                "--title",
                "Recovery milestone",
                "--summary",
                "Implemented the durable recovery seam.",
                "--feature",
                "session-recovery",
                "--verification",
                "unit tests passed",
                "--json",
            ).stdout
        )
        release = json.loads(
            self.cli(
                root,
                "log",
                "release",
                "--version",
                "v1.2.0",
                "--summary",
                "Released session recovery.",
                "--feature",
                "session-recovery",
                "--limitation",
                "Offline recovery is not supported.",
                "--json",
            ).stdout
        )
        self.assertTrue((root / development["path"]).exists())
        self.assertTrue((root / release["path"]).exists())
        development_text = (root / development["path"]).read_text(encoding="utf-8")
        repeated_development = json.loads(
            self.cli(
                root,
                "log",
                "development",
                "--title",
                "Recovery milestone",
                "--summary",
                "Implemented the durable recovery seam.",
                "--feature",
                "session-recovery",
                "--verification",
                "unit tests passed",
                "--json",
            ).stdout
        )
        repeated_release = json.loads(
            self.cli(
                root,
                "log",
                "release",
                "--version",
                "v1.2.0",
                "--summary",
                "Released session recovery.",
                "--feature",
                "session-recovery",
                "--limitation",
                "Offline recovery is not supported.",
                "--json",
            ).stdout
        )
        self.assertEqual("already-recorded", repeated_development["status"])
        self.assertEqual("already-recorded", repeated_release["status"])
        self.assertEqual(
            development_text,
            (root / development["path"]).read_text(encoding="utf-8"),
        )
        context = self.cli(root, "context", "--intent", "durable recovery seam", "--json", check=False)
        paths = {item["path"] for item in json.loads(context.stdout)["documents"]}
        self.assertNotIn(development["path"], paths)
        self.assertNotIn(release["path"], paths)

    def test_skill_contract_requires_automatic_read_only_history_capture(self) -> None:
        skill_root = Path(__file__).resolve().parents[1] / "skills" / "doccanon"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        logs = (skill_root / "references" / "logs.md").read_text(encoding="utf-8")
        self.assertIn("Run `sync complete`", skill)
        self.assertIn("Do not ask the user to run DocCanon commands", skill)
        self.assertIn("Git hooks remain read-only", skill)
        self.assertIn("Do not let an unmapped file silently pass", skill)
        self.assertIn("references/synchronization.md", skill)
        self.assertIn("not the user, owns history capture", logs)
        self.assertIn("Automatic retries", logs)

    def test_verified_revision_from_unrelated_branch_is_rejected(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        integration = git(root, "branch", "--show-current")
        git(root, "checkout", "-qb", "other-history")
        (root / "other.txt").write_text("other branch\n", encoding="utf-8")
        git(root, "add", "other.txt")
        git(root, "commit", "-qm", "other branch commit")
        foreign = git(root, "rev-parse", "HEAD")
        git(root, "checkout", "-q", integration)
        self.cli(root, "enable")
        (root / "docs" / "architecture.md").write_text(
            "---\n"
            "doccanon_authority: current-state\n"
            f"doccanon_verified_at: {foreign}\n"
            "doccanon_covers:\n  - \"src/**\"\n"
            "doccanon_domains:\n  - \"architecture\"\n"
            "---\n# Architecture\n",
            encoding="utf-8",
        )
        checked = self.cli(root, "check", "--json", check=False)
        codes = {item["code"] for item in json.loads(checked.stdout)["findings"]}
        self.assertIn("foreign-branch-anchor", codes)


if __name__ == "__main__":
    unittest.main()
