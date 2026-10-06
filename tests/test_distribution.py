from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.py"
DEMO = ROOT / "scripts" / "demo.py"
HELPER = ROOT / "skills" / "doccanon" / "scripts" / "doccanon.py"
MEASURE = ROOT / "skills" / "doccanon" / "scripts" / "measure_context.py"


def run(*command: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result


class DistributionTest(unittest.TestCase):
    def test_universal_install_update_and_uninstall_are_owned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            home = root / "home"
            project.mkdir()
            home.mkdir()
            command = (
                "python3", str(INSTALLER), "--agent", "universal", "--scope", "project",
                "--project", str(project), "--home", str(home), "--json",
            )
            installed = json.loads(run(*command).stdout)
            destination = project / ".agents" / "skills" / "doccanon"
            self.assertEqual("install", installed["results"][0]["action"])
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertTrue((destination / ".doccanon-install.json").is_file())

            updated = json.loads(run(*command).stdout)
            self.assertEqual("update", updated["results"][0]["action"])
            self.assertTrue(Path(updated["results"][0]["backup"]).is_dir())

            removed = json.loads(run(*command[:-1], "--uninstall", "--json").stdout)
            self.assertEqual("uninstall", removed["results"][0]["action"])
            self.assertFalse(destination.exists())

    def test_installer_refuses_unmanaged_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            destination = project / ".agents" / "skills" / "doccanon"
            destination.mkdir(parents=True)
            (destination / "SKILL.md").write_text("user owned\n", encoding="utf-8")
            result = run(
                "python3", str(INSTALLER), "--agent", "universal", "--scope", "project",
                "--project", str(project), check=False,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("refusing to overwrite unmanaged destination", result.stderr)
            self.assertEqual("user owned\n", (destination / "SKILL.md").read_text(encoding="utf-8"))

    def test_all_project_hosts_include_cursor_rule_without_duplicate_update(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            payload = json.loads(
                run(
                    "python3", str(INSTALLER), "--agent", "all", "--scope", "project",
                    "--project", str(project), "--json",
                ).stdout
            )
            paths = [item["path"] for item in payload["results"]]
            self.assertEqual(len(paths), len(set(paths)))
            self.assertTrue((project / ".cursor" / "rules" / "doccanon.mdc").is_file())
            self.assertTrue((project / ".cline" / "skills" / "doccanon" / "SKILL.md").is_file())
            self.assertTrue((project / ".github" / "skills" / "doccanon" / "SKILL.md").is_file())

    def test_demo_exposes_stale_gate(self) -> None:
        output = run("python3", str(DEMO)).stdout
        self.assertIn("Governed baseline: synchronized", output)
        self.assertIn("Code changed without its owner: stale", output)
        self.assertIn("stale-document", output)

    def test_installer_skips_local_python_caches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            (source / "scripts" / "__pycache__").mkdir(parents=True)
            (source / "SKILL.md").write_text("---\nname: doccanon\n---\n", encoding="utf-8")
            (source / "scripts" / "__pycache__" / "stale.pyc").write_bytes(b"stale")
            spec = importlib.util.spec_from_file_location("doccanon_install", INSTALLER)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.SOURCE = source
            destination = root / "installed"
            module.install_copy(destination, "universal", "project", dry_run=False)
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertFalse((destination / "scripts" / "__pycache__").exists())

    def test_context_measurement_labels_proxy_and_requires_fresh_docs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            run("git", "init", "-q", str(project))
            run("git", "-C", str(project), "config", "user.email", "test@example.com")
            run("git", "-C", str(project), "config", "user.name", "DocCanon Test")
            (project / "src").mkdir()
            (project / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
            run("git", "-C", str(project), "add", ".")
            run("git", "-C", str(project), "commit", "-qm", "initial")
            run("python3", str(HELPER), "--project", str(project), "enable")
            run("git", "-C", str(project), "add", ".")
            run("git", "-C", str(project), "commit", "-qm", "enable")
            architecture = project / "docs" / "architecture.md"
            architecture.write_text(
                "# Architecture\n\n## Current behavior\n\nThe application starts in `src/app.py`. "
                "This owner records the process boundary and the stable rule that changes to startup "
                "behavior must update this contract. The current implementation prints one marker and "
                "has no external service dependency.\n\n## Verification\n\nRun `python3 src/app.py`.\n",
                encoding="utf-8",
            )
            run(
                "python3", str(HELPER), "--project", str(project), "mark-verified",
                "docs/architecture.md", "--covers", "src/**", "--domain", "architecture",
            )
            run("python3", str(HELPER), "--project", str(project), "promote", "--domain", "architecture")
            run("git", "-C", str(project), "add", ".")
            run("git", "-C", str(project), "commit", "-qm", "govern docs")

            payload = json.loads(
                run(
                    "python3", str(MEASURE), "--project", str(project),
                    "--intent", "change startup behavior", "--json",
                ).stdout
            )
            self.assertEqual("lexical_proxy_units_v1", payload["metric"])
            self.assertIn("not actual model input tokens", payload["claim_boundary"])

            (project / "src" / "app.py").write_text("print('changed')\n", encoding="utf-8")
            run("git", "-C", str(project), "add", "src/app.py")
            refused = run(
                "python3", str(MEASURE), "--project", str(project),
                "--intent", "change startup behavior", "--json", check=False,
            )
            self.assertEqual(2, refused.returncode)
            self.assertIn("not synchronized", refused.stderr)


if __name__ == "__main__":
    unittest.main()
