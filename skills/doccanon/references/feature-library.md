# Feature library

## Quality bar

A feature contract must let a future Agent answer four questions before opening broad areas of code:

1. What outcome does the user or operator get?
2. What behavior, states, failures, permissions, and invariants must remain true?
3. Which implementation and data boundaries own it?
4. How is a change verified?

The contract must provide enough guidance to plan a normal change without first scanning the whole implementation. Link focused ADRs, designs, or runbooks when detail is durable and still current; do not bloat the contract or require historical plans for routine work.

`docs/features/README.md` is navigation only. Store each current feature in `docs/features/<slug>.md` and list it in `docs/features/manifest.json`.

## Discover features during init or migration

Start from existing product documents, but do not stop when they are incomplete. Reconstruct the shipped surface from code:

1. Inventory user and operator entry points: routes, screens, commands, public APIs, webhooks, scheduled jobs, and background workers.
2. Trace each entry point through handlers, services, durable entities, migrations, permissions, entitlements, external dependencies, and tests.
3. Cluster files by cohesive capability. A feature should have an independently meaningful outcome or change contract.
4. Split a feature when its lifecycle, permissions, data owner, or verification boundary can change independently. Merge items that are merely components or endpoints of one behavior.
5. Compare reconstructed behavior with existing docs and Git history. Code proves current mechanics; accepted docs and explicit user decisions prove intent and rationale.

Do not infer why a choice was made from code. Mark unresolved intent or conflicting authority for review without blocking documentation of observable current behavior.

## Required feature contract

Use these exact second-level headings so `features status` can validate the library:

- `## User outcome`
- `## Scope`
- `## Behavior`
- `## States and failure modes`
- `## Data and dependencies`
- `## Invariants`
- `## Change guidance`
- `## Implementation`
- `## Verification`

The frontmatter must include `doccanon_feature`, `current-state` authority, verified revision, `features` domain, and code coverage. The body must reference real implementation files.

Describe observed behavior compactly. Include access conditions, state transitions, negative paths, cross-service effects, and durable invariants when relevant. In Change guidance, identify extension points, coupled surfaces, migration needs, and failure-prone assumptions that a future change must account for. Avoid speculative improvements, generic product prose, component inventories, and line-by-line code narration.

Verification must name focused commands and any required runtime/browser scenario. “Run relevant tests” is not sufficient.

## Feature manifest

Use this shape:

```json
{
  "schema_version": 1,
  "features": [
    {
      "id": "session-recovery",
      "name": "Session recovery",
      "status": "current",
      "document": "docs/features/session-recovery.md",
      "code_patterns": ["src/session/**", "server/session/**"]
    },
    {
      "id": "admin-console",
      "name": "Admin console",
      "status": "excluded",
      "reason": "No admin surface exists in this project"
    }
  ]
}
```

Allowed resolved statuses are `current`, `excluded`, and `retired`. Candidate or review states remain unresolved. Every current entry must pass `features status`; every exclusion needs a reason.

## Maintenance

For every semantic code change, identify the owning feature before implementation. Update its contract in the same change. Add a manifest entry and new contract when shipping a new independently meaningful capability. Retire rather than erase removed features when the history still explains durable decisions or migrations. A retired feature must not keep an active contract: the helper fails `features status` until the contract is archived, and the upgrade pass archives leftovers.
