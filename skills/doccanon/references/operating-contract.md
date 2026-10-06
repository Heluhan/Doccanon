# DocCanon operating contract

This contract is the self-contained product definition. Do not rely on a user's prior knowledge, an earlier conversation, or a project-specific prompt to supply these rules.

## Purpose

Maintain a governed, project-local knowledge library that lets an Agent understand and change a codebase by reading a small canonical context before broad code exploration. Canonical docs reduce repeated code reading and token use; code, tests, schemas, configuration, and runtime evidence remain the proof of implementation truth.

Treat context-size comparisons as mechanism evidence, not measured model savings. Publish a token or cost percentage only from paired runs that hold the task, model, agent, permissions, and cache state constant and preserve quality outcomes and failed runs.

## Non-negotiable loop

1. Record confirmed terminology and decisions in the canonical library.
2. Before substantive work, check branch-relative freshness and synchronize stale relevant docs before trusting them.
3. Route the task to the smallest relevant canonical bundle, then inspect only the code needed to verify or implement it.
4. Update every semantically affected feature and cross-cutting owner in the same change as code.
5. Verify code and docs together before commit, PR, or merge.
6. Generate an impact plan covering every changed implementation file and governed domain. Resolve every item through a canonical update or an evidence-backed exclusion.
7. Pass the synchronization completion gate and automatically capture meaningful development and release history; never require the user to remember a DocCanon command.

Never call enabled, indexed, clean, or mapped documentation synchronized unless the trust gate literally passes.

## Project-local information architecture

- Store durable knowledge in the owning repository: `CONTEXT.md` and `docs/`.
- Let `CONTEXT.md` own confirmed terminology and domain boundaries, kept current-only; retired terms are removed or replaced, never accumulated as history.
- Separate product, interaction, architecture, per-feature, decision, plan, operations, development, and release responsibilities.
- Give each shipped cohesive capability its own feature contract. A registry or category README is navigation, not feature documentation.
- Keep one canonical owner per fact. Link between canonical owners instead of duplicating truth.
- Keep development and release logs as historical snapshots, never current-state authority.
- Keep intended future work in `plans/`: routable when relevant, but never current truth.
- Treat the repository-root agent entry (`AGENTS.md`) and its adapters as generated projections of the canonical library, not canonical owners.

## Admission

- Ask once before enabling DocCanon for an unconfigured substantive project.
- Recommend disabling it for a scratch project, disposable prototype, or one-off static page.
- Persist both acceptance and refusal in `.doccanon.yml`. A disabled project stays silent until explicitly reconsidered.
- Separate `enabled` from `governed`; bootstrap output is not automatically trustworthy.

## Distribution language

Write all bundled skill instructions, references, templates, tests, CLI messages, and marketplace metadata in English for global distribution. Do not embed language-specific routing rules or stop-word lists. Generated project documentation should follow the language explicitly chosen by that project; otherwise preserve the project's established documentation language.

## Knowledge quality

Canonical current-state documents must be useful change contracts, not inventories or generated prose. They must state the owned behavior, boundaries, states or failures when applicable, durable invariants, coupled change surfaces, stable implementation entry points, and concrete verification. Reconstruct missing behavior from current code and tests during initialization or migration, but never invent intent or rationale.

## Migration

- Discover document-like knowledge regardless of folder name or format; do not special-case a legacy convention such as Memory Bank.
- Review every candidate source. Review does not imply absorption.
- Rewrite only verified, still-useful, missing knowledge into the canonical library using the project's current language.
- Reject stale implementation claims against current implementation evidence. Preserve unresolved intent or rationale for human review.
- Record claim-level receipts only for absorbed knowledge; give every other source an evidence-backed terminal disposition.
- Freeze legacy sources through manifest disposition and default context exclusion. Do not maintain a parallel legacy library, mass-edit every old source, or invent a project-specific freeze system.
- After migration, normal work must be possible from canonical docs alone; use legacy sources only for archaeology.

## Branches and history

- Observe Git but do not manage it without explicit authorization.
- Treat current-state authority as branch-relative and compare feature work to the integration branch.
- Keep code and affected canonical docs in the same branch and PR.
- Refuse repository-wide bootstrap on a dirty feature branch by default.
- Automatically record meaningful development milestones and evidence-backed releases without turning logs into transcripts.

## Automatic history capture

- The Agent task loop owns capture. Helper logging commands are internal write primitives, not user workflow.
- Append a development record after a verified, meaningful product, feature, architecture, data, or operations milestone. Derive it from the actual diff, affected features, branch and base, commit evidence when available, and verification performed.
- Skip formatting-only edits, typo fixes, failed experiments, temporary plans, command transcripts, and conversational progress.
- During release work, synthesize a release draft from the target-branch diff, development records, feature manifest, migrations, configuration changes, and verification. Finalize deployment or live-state claims only after direct evidence; a merge or tag alone is insufficient.
- Capture must be idempotent. Re-running a completion or release pass must not duplicate an equivalent record.
- Freshness checks, preflight, CI, and Git hooks are read-only. They may report missing history, but must never mutate documentation during a commit.

## Synchronization closure

- Treat every changed implementation file as review-required until it maps to a feature or current-state owner, or receives a concrete file-level exclusion receipt.
- Review every governed domain for every substantive task. Require an updated current-state owner for affected domains and a reason for excluded domains.
- Discover new features from the implemented capability, not only from the existing manifest. Create a feature contract and code mapping when a change introduces a cohesive user or operator capability.
- Refuse completion when an owner is stale, an implementation file is unaccounted for, a domain is unreviewed, verification is absent, or freshness checks fail.
- Persist the resulting impact receipt in the automatic development record so later maintainers can audit why documents changed or did not change.

## Agent entry projection

- The repository-root agent entry (`AGENTS.md`, plus configured adapters such as `CLAUDE.md`) is a generated view over canonical owners. It owns no facts.
- Render it from current-state, human-confirmed, append-only, and generated owners only. Retired, historical, draft, and unclassified material never enters it by construction.
- Keep the declared user-owned custom section verbatim. Never absorb it as canonical truth; move durable knowledge into owning canonical documents.
- Write only when the projection actually changed; unchanged canonical content must produce no write, no diff, and no churn.
- `check`, `preflight`, and Git hooks are read-only and must fail on a missing or stale projection. Refresh happens in the Agent task loop at the completion boundary, never in a commit hook.
- Pre-existing hand-written agent instruction files are migration sources, not a parallel documentation system.

## Optional Grill with Docs relationship

DocCanon is self-contained. `grill-with-docs` may clarify terminology or decisions, but DocCanon must work without it. Depend on its outputs when available; never copy, fork, or modify that skill.

## Non-goals

DocCanon is not a Git branch manager, a transcript store, a replacement for runtime verification, an excuse to document every component, or an authority for inferred product intent. It does not force governance on trivial projects and does not preserve obsolete prose as current truth. It does not preserve a hand-maintained agent instruction dump as truth.
