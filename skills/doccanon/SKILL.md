---
name: doccanon
description: Keep coding agents from trusting stale project documentation by maintaining branch-aware, evidence-backed current-state contracts aligned with code and releases. Use for substantive repository work, brownfield knowledge migration, feature implementation, documentation freshness checks, commits, pull requests, and releases. Skip general Q&A, isolated snippets, and disposable prototypes.
license: MIT
metadata:
  version: "0.10.0"
---

# DocCanon

Treat the project's `CONTEXT.md` and `docs/` tree as durable project knowledge. Treat code and runtime evidence as the final proof of current implementation. Keep the two aligned without inventing decisions.

The skill must be self-contained. Never assume the user knows DocCanon's design or must restate migration, freshness, feature, branch, or logging rules in a project prompt. [references/operating-contract.md](references/operating-contract.md) is the complete product contract; read it before initialization, migration, governance reorganization, or changing DocCanon itself.

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
3. Run `context --intent "<task>" --json`. By default it excludes snapshots, plans, superseded material, and unclassified docs. Read returned canonical docs, then only the code needed to verify or implement the task. Use `--include-historical` only for archaeology.
4. Record confirmed new terminology and decisions before implementation. Use `CONTEXT.md` for canonical language, current-state docs for accepted behavior, and ADRs only for hard-to-reverse, surprising trade-offs. Keep `CONTEXT.md` current-only: update changed meanings and remove or replace retired terms instead of appending their history.
5. Implement and verify the code change.
6. Run `sync plan --json`. Review every affected feature, current-state owner, unmapped implementation file, and governed domain. Do not let an unmapped file silently pass. Create or update the owning feature and cross-cutting documents, or record a concrete file-level or domain-level exclusion receipt.
7. Rerun the plan until every implementation change is mapped or explicitly excluded. For a new cohesive user or operator capability, create its feature contract and manifest mapping even when no prior document predicted it.
8. Run `sync complete` with the actual verification and semantic review decisions. Let it enforce owner updates, domain coverage, unmapped-file receipts, freshness, automatic development or release history, and the generated agent entry projection. Do not ask the user to run DocCanon commands.
9. Before a PR or merge, run `preflight --target <integration-branch>`. Report stale or unresolved documents honestly. Claim synchronized only when `sync complete` and `check` pass.

`grill-with-docs` is an optional companion, not a dependency. When available, hand complex terminology or decision clarification to it. Consume the resulting `CONTEXT.md` or ADR changes afterward. Never copy, fork, or modify that skill.

Do not claim a token-savings percentage from the size of the selected context alone. When the user needs efficiency evidence, use `scripts/measure_context.py` only as a disclosed context-volume proxy and read [references/token-benchmark.md](references/token-benchmark.md) before making an empirical token or cost claim.

## Authority boundaries

- Current-state docs describe what is true now and may be synchronized from verified code evidence.
- Human-confirmed authority requires explicit user confirmation of the content or decision. Never assign it merely because an Agent created the file.
- ADRs describe why a confirmed choice was made. Never infer or fabricate them from implementation.
- Plans and drafts do not become current truth merely because they are newer.
- Session notes, progress lists, and handoffs are time-bounded evidence, not canonical truth.
- Preserve source attribution when consolidating existing material.

Read [references/synchronization.md](references/synchronization.md) for the mandatory end-to-end task protocol. Read [references/governance-contract.md](references/governance-contract.md) when creating or reorganizing canonical documents. Read [references/migration.md](references/migration.md) for a migration. Read [references/feature-library.md](references/feature-library.md) during initialization, migration, or feature inventory/reorganization. Read [references/branching.md](references/branching.md) before initialization, migration, PR, merge, or release work. Read [references/logs.md](references/logs.md) when recording development or release history.

## Branch awareness

Treat a current-state document on a feature branch as true for that branch, not yet for the integration or release branch. Compare feature work with the configured or inferred integration branch. Keep code and affected docs in the same branch and PR.

Do not create, switch, reset, stash, merge, delete, or push branches unless the user explicitly asks. Initialization and migration refuse a dirty feature branch by default; suggest a clean integration-based branch or isolated worktree instead. Override only with explicit user intent.

Verified revisions must be ancestors of the current branch. Existing commits from unrelated branches are not valid freshness anchors.

## Initialization

`enable` only records project admission and creates missing entry files. When the user asks to initialize DocCanon, continue through a real bootstrap:

1. Inspect repository entry points, routes, handlers, persistent data, permissions, jobs, integrations, and tests.
2. Establish applicable domains and reconstruct the current feature inventory from code plus accepted documentation.
3. Create cross-cutting domain owners and one contract per current feature. Do not stop at five category README files.
4. Leave uncertain intent and rationale unresolved; document code-proven mechanics and ask for decisions only where authority matters.
5. Run `features status` and `check`. Promote only after the complete trust gate passes.

If the current worktree is dirty or on a feature branch, stop before repository-wide bootstrap writes and explain the safe integration-branch or worktree option. Do not mix unrelated business work with the initial documentation migration without explicit approval.

## Migration

When the user asks to migrate or consolidate existing documentation:

1. Run `migrate scan --json` to create a path-agnostic, per-source migration manifest. Do not summarize hundreds of sources into a few globs.
2. Review every candidate source, but do not assume every source deserves absorption. Inspect content, Git history, referenced code, and current repository structure semantically; paths and recency are weak signals only.
3. Resolve claims by type. For current implementation behavior, prefer current code, tests, schema/migrations, and configuration over conflicting legacy prose. For deployed or external state, prefer direct runtime/provider evidence. Never infer product intent, rationale, or a human decision from code.
4. Complete every material manifest entry. Only a source that contributes verified, still-useful knowledge missing from the canonical library uses `adopt`, `move`, `merge`, or `split` with `status: integrated`. Record receipts only for the claims actually absorbed. Mark stale, conflicting, duplicate, historical, irrelevant, or false-positive sources with a terminal non-integrated disposition and concrete evidence.
5. Rewrite integrated knowledge in the project's canonical language and place the actual content in `CONTEXT.md` or the owning `docs/` contract. A target link, source inventory, or prose summary in the manifest is not integration.
6. Freeze absorbed legacy sources through their manifest disposition and default context exclusion. Add a superseded notice only to high-confusion legacy entry points; do not mass-edit every source and do not invent a project-specific freeze checker.
7. Stop on unresolved intent, rationale, or human-decision conflicts. Ask one focused question at a time, optionally using `grill-with-docs`.
8. Write and verify canonical current-state knowledge in `CONTEXT.md` and `docs/`. A migration that only creates an index or replacement links is still bootstrapping.
9. Build `docs/features/manifest.json`. Give every current feature its own `docs/features/<feature>.md`; use code and tests to reconstruct current behavior when old documents are absent or unreliable.
10. Run `migrate status`, `features status`, `check`, and link validation. Test realistic tasks using canonical context only. Ensure rerunning migration creates no duplicate entries, moves, or documents.

## Trust gate

Before promoting a project, identify every applicable domain from product, interaction, architecture, features, and operations. Record explicit exclusions with reasons in the documentation map. For each applicable non-feature domain, create at least one current-state owner containing stable entry points and verification commands.

A heading, file list, or generic summary is not a current-state owner. Each owner must contain substantive verified behavior, at least one real implementation reference, and a concrete verification command or executable scenario. Keep the project bootstrapping when this quality bar is absent.

If `features` applies, a single umbrella README is not sufficient. `docs/features/README.md` is only the registry and navigation surface. Discover shipped capabilities semantically and create one current-state contract per feature. Prefer a cohesive user capability or independently changeable subsystem over one document per component or endpoint. Code-inferred behavior is allowed during initialization and migration; inferred rationale, intent, and trade-offs are not.

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

The Skill owns history capture; the user must not have to remember or invoke a logging command. The bundled `log` operations are internal write primitives for the Skill, not required user workflow.

Automatically append a development record after a meaningful feature, architecture, data, operations, or product milestone has been implemented and verified. Include the outcome, affected features, branch-relative evidence, and concrete verification. Do not turn the log into a transcript.

When the task prepares or performs a release, automatically assemble the release record from the target-branch diff, development records, feature manifest, migrations and configuration changes, and actual release evidence. A merge, tag, or release branch may justify a draft, but finalize claims about deployment, migrations, or live behavior only after direct evidence. Never invent a version or imply that merged code is live. Automatic retries must be idempotent.

Development and release logs are historical snapshots, not current-state owners, and remain excluded from default task context. `check`, `preflight`, and Git hooks remain read-only; automatic capture occurs in the Agent task loop after verification, never as a hidden commit-time mutation.

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

The helper detects covered code changes that are not accompanied by a document update. Updating a document alongside code produces `pending-sync`; semantic verification is still the Agent's responsibility. The synchronization gate additionally blocks every unmapped implementation file and requires an explicit decision for every governed domain.

## Agent entry projection

The repository-root agent entry (`AGENTS.md`, plus configured adapters such as `CLAUDE.md`) is a generated view over the canonical library, not a canonical owner. Hosts load it at session start, so it must never become a second, hand-maintained source of truth.

- Render it from current-state owners only. Historical, retired, draft, and unclassified material never enters it by construction.
- Rendering is idempotent: unchanged canonical content means no write and no diff. Keep the user-owned custom section intact and never absorb it as truth.
- `check` and `preflight` are read-only and fail on a missing or out-of-date projection. Run `render` after canonical updates, and let `sync complete` refresh it before its final check.
- Pre-existing hand-written entry files are migration sources: absorb still-useful rules into canonical owners, then let the projection carry only routing, retrieval policy, and the preserved custom section.

## Plans and release readiness

`docs/plans/` owns intended future work: milestones, launch conditions, and known gaps. Plans declare `doccanon_authority: plan` with a `doccanon_status` (`active`, `ready`, `shipped`, or `abandoned`) and an optional `doccanon_target`. They route to agents when relevant and are never current truth.

- Keep an active plan current when a task advances it. Completed items link to their canonical owner instead of restating behavior.
- A plan targeting a release version must reach `ready` or `shipped` before `sync complete --release-version` can pass.
- When a goal ships or is abandoned, record the outcome in development or release history and retire the plan by changing its authority, not by leaving a stale checklist active.

## Completion

State branch and comparison base, project maturity, coverage domains, feature counts, changed canonical docs, verification, migration completeness, relevant log entries, and any authority conflict or stale area. Claim synchronized only when `check` literally returns `synchronized`; `enabled`, `clean`, and `bootstrap-incomplete` are not synonyms for trustworthy.
