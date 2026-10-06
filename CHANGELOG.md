# Changelog

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
