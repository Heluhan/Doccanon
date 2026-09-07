# DocCanon

**Verified project memory for coding agents.**

[GitHub](https://github.com/Heluhan/Doccanon) · [Security contact](mailto:contact@planana.xyz)

DocCanon stops coding agents from trusting stale documentation. It keeps a small, branch-aware knowledge library beside the code, routes each task to the relevant current-state contracts, and blocks “synchronized” claims until every implementation change has been accounted for.

Spec-driven tools tell an agent what to build. DocCanon proves what the codebase is now.

## Why use it

Without governed project memory, every new agent session must rediscover the repository or risk coding against an obsolete README. DocCanon gives the agent a safer loop:

1. Check whether the canonical docs are fresh on the current branch.
2. Load only the documents relevant to the task.
3. Verify targeted implementation details in code or runtime evidence.
4. Update every affected feature and cross-cutting contract with the code.
5. Refuse completion while a changed implementation file or governed domain is unaccounted for.

“Enabled,” “indexed,” and “clean” do not mean trustworthy. A project becomes `governed` only after verified current-state coverage passes the trust gate, and it is `synchronized` only when the branch-relative checks literally pass.

## Install

DocCanon is an Agent Skills-compatible directory with no runtime service, API key, or model dependency. Python 3.10+ and Git are the only helper requirements.

With GitHub CLI 2.90 or later, preview and install the published skill:

```bash
gh skill preview Heluhan/Doccanon doccanon
gh skill install Heluhan/Doccanon doccanon
```

For explicit multi-host placement, clone the repository and use the safe installer:

```bash
git clone https://github.com/Heluhan/Doccanon.git
cd Doccanon
python3 install.py --agent universal --scope project --project /path/to/project
```

The universal project install writes `.agents/skills/doccanon`, which is recognized by Codex, GitHub Copilot, Gemini CLI, and OpenCode. See the [agent compatibility matrix](docs/agent-compatibility.md), or use a host-specific target when preferred:

```bash
python3 install.py --agent codex --scope user
python3 install.py --agent claude --scope user
python3 install.py --agent copilot --scope project --project /path/to/project
python3 install.py --agent gemini --scope user
python3 install.py --agent opencode --scope user
python3 install.py --agent cline --scope user
python3 install.py --agent cursor --scope project --project /path/to/project
```

Install several hosts by repeating `--agent`, or use `--agent all --scope project`. Preview any operation with `--dry-run`; remove only installer-owned copies with `--uninstall`. Existing unmanaged skill directories are never overwritten. Updates preserve a versioned `doccanon.previous-*` copy for review.

Start a new agent session after installation so the host discovers the skill.

Want to see the enforcement boundary before installing anything?

```bash
python3 scripts/demo.py
```

The demo creates a disposable Git repository, establishes a governed baseline, changes covered code without its canonical owner, and shows DocCanon blocking the stale state.

## Start using it

Tell the agent:

> Set up DocCanon for this project.

DocCanon asks once before governing an unconfigured repository. It recommends staying disabled for scratch projects and disposable prototypes. For an existing codebase, setup continues past file generation: the agent inventories shipped capabilities, creates one current-state contract per feature, records source-by-source migration dispositions when needed, verifies the owners against code, and promotes only when the library is trustworthy.

Once governed, use the coding agent normally. The user does not need to remember DocCanon commands.

## What makes it different

- **Trust before retrieval:** stale or incomplete docs cannot silently become agent context.
- **Brownfield migration:** every candidate source gets an evidence-backed disposition; only verified, still-useful knowledge is absorbed.
- **Implementation-wide closure:** every changed implementation file maps to a feature/current-state owner or receives a concrete exclusion receipt.
- **Branch-aware truth:** current-state authority is verified against a Git revision reachable from the current branch.
- **Human authority stays human:** code may prove mechanics, but it cannot invent product intent or rationale.
- **Auditable history:** meaningful development and evidence-backed release records are captured automatically after verification.
- **Local and portable:** canonical knowledge remains plain Markdown in `CONTEXT.md` and `docs/`, beside the code.

## Token efficiency, measured honestly

DocCanon is designed to replace broad repeated exploration with a small canonical context followed by targeted code verification. That should reduce input tokens on many brownfield tasks, but there is no honest universal percentage: repository shape, task, model, agent, cache behavior, and documentation quality all matter.

Measure the text-volume mechanism in a governed project:

```bash
python3 /path/to/doccanon/skills/doccanon/scripts/measure_context.py \
  --project . \
  --intent "change session recovery" \
  --baseline tracked-code \
  --json
```

This reports a **context-reduction proxy**, not model tokens or cost. For a publishable claim, run the paired control/treatment protocol in [the token benchmark guide](skills/doccanon/references/token-benchmark.md) and summarize provider-reported usage with:

```bash
python3 scripts/summarize_token_benchmark.py benchmarks/runs.csv --json
```

Until that benchmark exists, the accurate claim is: _DocCanon routes agents to a small, fresh canonical bundle before targeted code verification; no universal token-savings percentage is claimed yet._

## Deterministic helper

The skill runs `skills/doccanon/scripts/doccanon.py` internally. Useful diagnostics include:

```bash
python3 skills/doccanon/scripts/doccanon.py --project /path/to/repo status --json
python3 skills/doccanon/scripts/doccanon.py --project /path/to/repo check --json
python3 skills/doccanon/scripts/doccanon.py --project /path/to/repo context --intent "add session recovery" --json
python3 skills/doccanon/scripts/doccanon.py --project /path/to/repo sync plan --json
python3 skills/doccanon/scripts/doccanon.py --project /path/to/repo preflight --target main --json
```

The agent, not the user, owns the full `sync plan` → semantic documentation update → `sync complete` loop. Read-only checks and Git hooks never mutate documentation.

## Development

Run the complete local suite:

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/doccanon
```

The repository is MIT licensed. Contributions should preserve the boundary between deterministic repository facts and semantic agent judgment. Security reports can be sent to [contact@planana.xyz](mailto:contact@planana.xyz).
