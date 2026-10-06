---
name: doccanon
description: Keep coding agents from trusting stale project documentation by maintaining branch-aware, evidence-backed current-state contracts aligned with code and releases. Use for substantive repository work, brownfield knowledge migration, feature implementation, documentation freshness checks, commits, pull requests, and releases. Skip general Q&A, isolated snippets, and disposable prototypes.
license: MIT
metadata:
  version: "0.13.1"
---

# DocCanon

Treat the project's `CONTEXT.md` and `docs/` tree as durable project knowledge. Treat code and runtime evidence as the final proof of current implementation. Keep the two aligned without inventing decisions.

The skill must be self-contained. Never assume the user knows DocCanon's design or must restate migration, freshness, feature, branch, or logging rules in a project prompt. [references/operating-contract.md](references/operating-contract.md) is the complete product contract; read it before initialization, migration, governance reorganization, or changing DocCanon itself. The references own the detailed rules; this file owns the operating loop and decides which reference to load.

Resolve the project root first. Run the bundled helper as:

```bash
python3 <skill-directory>/scripts/doccanon.py --project <project-root> <command>
```

## Project admission

Read `.doccanon.yml` before doing DocCanon work.

- `status: enabled`: follow the task loop below.
- `status: disabled`: remain silent about DocCanon and continue the user's task. Reconsider only when the user explicitly asks.
- no config: offer DocCanon once when substantive project development begins. Recommend skipping it for a one-off page, scratch project, or disposable prototype. Do not initialize without consent. If the user declines, run `disable --reason <reason>` so other agents do not ask again.

Do not block work while waiting for an answer. Do not prompt during general Q&A or isolated snippets.

Enabled projects have a separate maturity:

- `bootstrapping`: DocCanon is admitted, but the documentation library is not yet trustworthy. Never call it synchronized.
- `governed`: applicable knowledge domains have verified current-state owners and any declared migration manifest is complete.

Treat missing maturity in a legacy config as `bootstrapping`.

## Task loop

For every substantive task in an enabled project:

1. Run `branch status --json`, then `check --json`, before trusting project docs. Treat synchronization as relative to the reported branch and base. `bootstrap-incomplete` means the library is not a trusted substitute for code inspection.
2. If relevant docs are stale, synchronize them against code and Git evidence before planning the new change. Resolve authority conflicts with the user; never silently select a winner.
3. Run `context --intent "<task>" --json`. By default it returns current-state owners and matching plans, and excludes snapshots, superseded, draft, and unclassified material. Read returned canonical docs, then only the code needed to verify or implement the task. Use `--include-historical` only for archaeology.
4. Record confirmed new terminology and decisions before implementation. Use `CONTEXT.md` for canonical language, current-state docs for accepted behavior, and ADRs only for hard-to-reverse, surprising trade-offs. Keep `CONTEXT.md` current-only: update changed meanings and remove or replace retired terms instead of appending their history.
5. Implement and verify the code change.
6. Run `sync plan --json`. Review every affected feature, current-state owner, unmapped implementation file, and governed domain. Do not let an unmapped file silently pass. Create or update the owning feature and cross-cutting documents, or record a concrete file-level or domain-level exclusion receipt.
7. Rerun the plan until every implementation change is mapped or explicitly excluded. For a new cohesive user or operator capability, create its feature contract and manifest mapping even when no prior document predicted it.
8. Run `sync complete` with the actual verification and semantic review decisions. Let it enforce owner updates, domain coverage, unmapped-file receipts, freshness, automatic development or release history, and the generated agent entry projection. Do not ask the user to run DocCanon commands.
9. Before a PR or merge, run `preflight --target <integration-branch>`. Report stale or unresolved documents honestly. Claim synchronized only when `sync complete` and `check` pass.

[references/synchronization.md](references/synchronization.md) owns the impact plan, domain review, completion gate, and read-only boundaries. `grill-with-docs` is an optional companion, not a dependency. When available, hand complex terminology or decision clarification to it. Consume the resulting `CONTEXT.md` or ADR changes afterward. Never copy, fork, or modify that skill.

Do not claim a token-savings percentage from the size of the selected context alone. When the user needs efficiency evidence, use `scripts/measure_context.py` only as a disclosed context-volume proxy and read [references/token-benchmark.md](references/token-benchmark.md) before making an empirical token or cost claim.

## Authority boundaries

- Human-confirmed authority requires explicit user confirmation of the content or decision. Never assign it merely because an Agent created the file.
- ADRs describe why a confirmed choice was made. Never infer or fabricate them from implementation.
- Plans and drafts do not become current truth merely because they are newer.
- Session notes, progress lists, and handoffs are time-bounded evidence, not canonical truth.
- Preserve source attribution when consolidating existing material.

[references/governance-contract.md](references/governance-contract.md) owns canonical locations, maturity, authority semantics, and writing rules. Read it when creating or reorganizing canonical documents.

## Branch awareness

Treat a current-state document on a feature branch as true for that branch, not yet for the integration or release branch; keep code and affected docs in the same branch and PR. Never create, switch, reset, stash, merge, delete, or push branches unless the user explicitly asks, and refuse repository-wide bootstrap work in a dirty or feature-branch worktree by default. Read [references/branching.md](references/branching.md) for baseline selection, verification ancestry, and safe alternatives.

## Initialization

`enable` only records project admission and creates missing entry files. When the user asks to initialize DocCanon, continue through a real bootstrap: inspect repository entry points, establish applicable domains, reconstruct the current feature inventory, create cross-cutting owners and one contract per current feature, then run `features status` and `check` and promote only when the trust gate passes. Leave uncertain intent and rationale unresolved. Read [references/feature-library.md](references/feature-library.md) for the discovery method and quality bar, and stop before repository-wide writes if the worktree is dirty or on a feature branch (see references/branching.md).

## Upgrading

When the skill is newer than the project's recorded `doccanon_version`, run `upgrade status --json` and follow [references/upgrading.md](references/upgrading.md). Skill updates are host-level actions performed by the user or the host's package manager; never fetch, pull, or overwrite the skill from inside a project. Mechanical cleanup is idempotent; semantic steps are reviewed and never resolved by disabling checks. `upgrade apply` stamps the version only when no semantic step remains. A `project-upgrade-required` warning in `check` is a prompt, not a blocker.

## Migration

When the user asks to migrate or consolidate existing documentation, read [references/migration.md](references/migration.md) and follow it end to end.

1. Run `migrate scan --json`; never summarize hundreds of sources into a few globs. Review every candidate semantically; review is an evidence-backed terminal decision, not a requirement to absorb.
2. Resolve claims by evidence type. Code wins over obsolete prose only for implementation claims code can prove; never infer intent, rationale, or human decisions. Stop and ask one focused question at a time on unresolved authority conflicts.
3. Absorb only verified, still-useful knowledge missing from the canonical library, rewritten in the project's language into its owning canonical document. A link, inventory, or summary is not integration.
4. Freeze and retire absorbed or obsolete sources through their manifest disposition; do not invent a project-specific freeze system. A migration that only creates an index is still bootstrapping. Finish only when `migrate status`, `features status`, and `check` pass and realistic tasks work from canonical docs alone.

## Trust gate

Before promoting, every applicable domain needs a verified current-state owner with stable implementation entry points and a concrete verification command. A heading, file list, or generic summary is not an owner. When `features` applies, a registry alone is not coverage: discover shipped capabilities semantically and give each one a contract. Code-inferred behavior is allowed during initialization and migration; inferred rationale is not.

Mark a document only after checking it against code at the recorded revision:

```bash
python3 <skill-directory>/scripts/doccanon.py --project <project-root> mark-verified \
  docs/architecture/README.md --domain architecture --covers "src/**"
```

For a migrated project, require a complete manifest during promotion:

```bash
python3 <skill-directory>/scripts/doccanon.py --project <project-root> promote \
  --domain product --domain interaction --domain architecture --domain features --domain operations \
  --manifest docs/operations/doccanon-migration.json \
  --feature-manifest docs/features/manifest.json
```

Choose domains to match the project; do not force irrelevant categories. Install the pre-commit hook only after promotion succeeds.

## Development and release history

History capture belongs to the Agent task loop; the user must never have to remember or invoke a logging command. After a meaningful verified milestone, `sync complete` appends the development record automatically, and release work adds an evidence-backed release record. Never record transcripts, never invent a version, and never finalize deployment claims without direct evidence. `check`, `preflight`, and Git hooks remain read-only. Read [references/logs.md](references/logs.md) for capture rules and idempotency.

## Freshness metadata

Add flattened frontmatter to current-state documents whose code coverage is known:

```yaml
---
doccanon_authority: current-state
doccanon_verified_at: <git-sha>
doccanon_covers:
  - "src/session/**"
  - "server/session/**"
doccanon_domains:
  - "architecture"
---
```

The helper detects covered code changes that are not accompanied by a document update. Updating a document alongside code produces `pending-sync`; semantic verification is still the Agent's responsibility. The synchronization gate additionally blocks every unmapped implementation file and requires an explicit decision for every governed domain. Repository-meta files such as the root README, LICENSE, or `.gitignore` are not implementation files.

## Agent entry projection

The repository-root agent entry (`AGENTS.md`, plus configured adapters such as `CLAUDE.md`) is a generated view over the canonical library, not a canonical owner. Render it from current-state owners only; retired, historical, draft, and unclassified material never enters it by construction. Rendering is idempotent, preserves the user-owned custom section verbatim, and writes only when content changed. `check` and `preflight` are read-only and fail on a missing or stale projection; `sync complete` refreshes it. Pre-existing hand-written entry files are migration sources. Read [references/operating-contract.md](references/operating-contract.md) for the full projection rules.

## Plans and release readiness

`docs/plans/` owns intended future work: milestones, launch conditions, and known gaps. Plans declare `doccanon_authority: plan` with a required `doccanon_status` (`active`, `ready`, `shipped`, or `abandoned`) and an optional `doccanon_target`. They route to agents when relevant and are never current truth. Keep an active plan current as work advances, link shipped items to their canonical owner, and retire a plan by changing its authority when the goal ships or is abandoned. `sync complete --release-version` fails while a plan targeting that version is not ready or shipped.

## Completion

State branch and comparison base, project maturity, coverage domains, feature counts, changed canonical docs, verification, migration completeness, relevant log entries, and any authority conflict or stale area. Claim synchronized only when `check` literally returns `synchronized`; `enabled`, `clean`, and `bootstrap-incomplete` are not synonyms for trustworthy.
