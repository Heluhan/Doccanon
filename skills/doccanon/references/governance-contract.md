# Governance contract

## Canonical locations

Keep durable knowledge in the project that owns it:

```text
CONTEXT.md
docs/
  README.md
  product/
  interaction/
  architecture/
  features/
  adr/
  operations/
  development/
  releases/
```

Create category files lazily. `docs/README.md` is the map, not a second copy of every fact.

## Maturity

- `bootstrapping`: admission and discovery may be complete, but current-state coverage is absent, partial, or unresolved.
- `governed`: every declared applicable domain has a verified current-state owner, and any migration manifest is complete.

Only `governed` projects can be synchronized. Small projects may declare fewer applicable domains, but the map must say why omitted domains do not apply.

When `features` applies, domain coverage requires a complete `docs/features/manifest.json`; a `features/README.md` alone cannot satisfy the trust gate.

## Responsibilities

| Area | Owns | Does not own |
|---|---|---|
| `CONTEXT.md` | Canonical terms and domain boundaries, kept current-only | Implementation detail, history, or retired definitions |
| `product/` | Users, capabilities, product boundaries | Component structure |
| `interaction/` | Journeys, states, transitions, failure paths | Backend internals |
| `architecture/` | Modules, data, integrations, deployment topology | Product rationale |
| `features/` | One current-state contract per shipped feature plus a registry | Temporary plans or one giant product summary |
| `adr/` | Confirmed decision context, choice, trade-offs, consequences | Current-state summaries |
| `operations/` | Deployment, migration, monitoring, recovery | Product behavior |
| `development/` | Time-bounded development milestones and verification | Current product truth |
| `releases/` | Versioned shipped-change snapshots and known limitations | Future plans or branch-local claims |

One fact has one canonical owner. Other canonical documents link to it. Migrated legacy sources are frozen provenance and are not maintained in parallel. Freezing is a DocCanon manifest/context behavior; do not add a custom enforcement system to each project. The repository-root agent entry (`AGENTS.md`) and its adapters are generated projections of these owners; they are not canonical locations and must not become a hand-maintained second source of truth.

## Authority

- `current-state`: synchronize when covered implementation changes.
- `append-only`: preserve history; supersede rather than rewrite.
- `human-confirmed`: change only after explicit agreement.
- `generated`: regenerate from its declared source.
- `snapshot`: time-bounded reference; never treat as current without verification.

`human-confirmed` may be assigned only after the user explicitly confirms the content. Agent authorship, file age, and Git history do not establish human confirmation.

The project context file (`CONTEXT.md`) is `human-confirmed` canonical language. Agents add or change entries only after the user confirms the term or decision. Keep it current-only: update changed meanings and remove retired terms; a one-line replacement mapping may remain while legacy references still need decoding, but a retired definition may not.

## Current-state contract

Every current-state document must declare:

```yaml
doccanon_authority: current-state
doccanon_verified_at: <git-sha>
doccanon_covers:
  - "path/to/code/**"
doccanon_domains:
  - "architecture"
```

It must also name stable implementation entry points and concrete verification commands in its body.

## Writing rules

- Prefer compact contracts over exhaustive code narration.
- Include stable code entry points and verification commands.
- Distinguish current behavior from future work.
- Preserve provenance for migrated claims.
- Make canonical documents self-sufficient: never require a legacy source for normal current-state work after migration.
- Keep future work, historical evidence, and unresolved claims out of current-state sections.
- Do not record secrets or private credentials.
- Use the project's language unless the project explicitly requires another language.
