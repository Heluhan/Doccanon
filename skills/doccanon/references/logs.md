# Automatic development and release history

## Automation boundary

The DocCanon task loop, not the user, owns history capture. Never ask the user to remember or run a logging command. The helper's `log development` and `log release` operations are internal deterministic write primitives that the Skill may invoke after it has assembled evidence.

`check`, `preflight`, CI, and Git hooks remain read-only. They may detect missing or stale documentation, but must not modify a worktree during commit or validation.

## Development capture

Automatically append a development record after a meaningful milestone has been implemented and verified. A milestone includes a shipped or materially changed user or operator behavior, a completed feature increment, or a consequential architecture, data, operations, or confirmed product-decision change. Derive the record from:

- the outcome, not a transcript of work;
- affected feature IDs;
- branch, base, and commit evidence;
- tests, builds, runtime probes, or review performed;
- an unresolved risk only when it remains relevant.

Do not record formatting-only edits, typo fixes, every commit, commands, failed experiments, temporary plans, or conversational progress. The monthly file under `docs/development/` is append-only historical evidence. Automatic retries must recognize an equivalent milestone and leave the file unchanged.

## Release capture

When the user's task prepares or performs a release, automatically synthesize a release draft from the target-branch diff, feature manifest, development records, migrations, configuration changes, and available runtime evidence. Include:

- shipped user or operator outcomes;
- affected feature IDs;
- schema, configuration, deployment, or recovery actions;
- verification actually performed;
- known limitations and deferred work.

Do not invent a release version. A merge, tag, version change, or release branch may support a draft, but do not claim a deployment, applied migration, or live endpoint without direct evidence. If release evidence is incomplete, label the record as a draft or candidate instead of finalizing it. Repeated release completion must be idempotent; conflicting content for an existing version requires review.

Release files under `docs/releases/` are versioned snapshots and must not replace current-state feature or operations documents.

## Context policy

Both log types use snapshot authority, so normal `context` routing excludes them. Use `--include-historical` for archaeology, release preparation, regression investigation, or explaining how the current state evolved.
