# Changelog

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
