# Changelog

## 0.13.1

- Documented the two upgrade layers: host-side skill updates and project-side reconciliation; a project agent never fetches the skill.
- `upgrade status` now reports install provenance (symlink, install.py marker, git checkout, or unknown) with an update hint.
- Added `install.py --check` to report installed versus source skill versions without writing, exiting 1 when updates are available.

## 0.13.0

- Added an explicit upgrade mechanism: `.doccanon.yml` records `doccanon_version`, `upgrade status` reports a read-only reconciliation checklist, and `upgrade apply` performs idempotent mechanical cleanup and stamps the version only when no semantic step remains.
- Completion and promotion passes no longer rewrite hand-written agent entries; they block with `unreconciled-agent-entry` until the entry is reconciled via `render` or explicitly opted out.
- Migration manifests now report frozen sources still in the tree and sources that no longer exist, with `legacy-sources-in-tree` and `migration-source-missing` check warnings.
- Added `invalid-authority` and `unclassified-decision-record` warnings; accepted ADRs are documented as `append-only`.
- Added a Gemini adapter (`GEMINI.md`) alongside the Claude adapter.
- Context routing now matches CJK content through character bigrams, weights matched terms by inverse document frequency, and no longer emits a zero-match `CONTEXT.md` result.
- Added `references/upgrading.md` with legacy categories, dispositions, and version notes.

## 0.12.0

- Removed dead configuration and metadata: `.doccanon.yml` `schema_version`, `branch_policy`, and `reconsider` fields, the unused historical-authorities constant, and the unused `doccanon_plan` frontmatter field.
- Converged retirement semantics: `retire --disposition` now accepts only `historical` or `superseded`, stamps exactly that authority, reports which search-ignore file already covers the archive, and writes YAML frontmatter only for Markdown documents.
- Added a `missing-plan-status` warning and documented the `superseded` authority in the governance contract.
- Repository-meta files (root README, LICENSE, CHANGELOG, VCS/editor dotfiles) are no longer treated as implementation files during sync or freshness checks.
- Deduplicated `SKILL.md` against the references so workflow rules have a single owner; replaced documentation-wording tests with package-integrity and behavior tests.
- Removed the speculative benchmark CSV and summarizer tooling; the context-volume proxy and A/B protocol documentation remain.
- The installer no longer copies local `__pycache__` artifacts into destinations.

## 0.11.0

- Added retirement relocation: `retire` moves obsolete documents into a configurable archive root (default `.doccanon/archive/`), stamps a non-active authority with a retirement notice, and records search exclusion.
- Added `.ignore` management and an `archive-not-search-excluded` check warning, so ripgrep-based agents skip retired material by default while archaeology remains possible.
- `migrate scan` now skips the archive root, and generated agent entries document the archive policy.
- Added pointer stubs for high-traffic legacy entry points and protections against retiring active canonical documents.
- Added tests for relocation, stamping, search exclusion, pointers, and warnings (40 passing).

## 0.10.0

- Added a governed plans layer (`docs/plans/`) with the `plan` authority for milestones, launch readiness, and open gaps: routable in context, never current truth.
- Added plan lifecycle metadata (`doccanon_status`, optional `doccanon_target`) with warnings for inactive or unclassified plans.
- Added a release gate: `sync complete --release-version` fails while a plan targeting that version is not `ready` or `shipped`.
- Added the plan template, docs map entry, agent entry retrieval policy and routing updates, and migration guidance for roadmaps.
- Added tests for plan routing, rendering, warnings, and the release gate (37 passing).

## 0.9.0

- Added a generated agent entry projection: `AGENTS.md`, plus a thin `CLAUDE.md` adapter, rendered from current-state owners only.
- Added idempotent rendering that preserves a user-owned custom section and writes only when the projection actually changed.
- Added read-only entry drift checks to `check` and `preflight`, with automatic refresh at the sync completion boundary.
- Marked `CONTEXT.md` as `human-confirmed` canonical terminology, kept current-only, so `context` routing returns confirmed glossary terms.
- Added a warning when a legacy context file has no confirmed authority.

## 0.8.0

- Reframed DocCanon as verified project memory for coding agents.
- Added safe project- and user-scoped installation for Codex, GitHub Copilot, Gemini CLI, OpenCode, Claude Code, Cline, and Cursor.
- Added a disposable stale-document demo.
- Added a context-volume proxy and a paired A/B protocol for honest token-efficiency claims.
- Expanded CI across Python 3.10/3.12 and Linux, macOS, and Windows.

## 0.7.0

- Added implementation-wide `sync plan` and gated `sync complete` closure.
- Added automatic auditable development and evidence-backed release history.
