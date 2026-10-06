# Migration workflow

## Goal

Compile scattered project knowledge into a self-sufficient canonical library without requiring known legacy folder names or formats. After migration, normal work reads and maintains `CONTEXT.md` and `docs/`; legacy sources are provenance, not a second documentation system.

## Classification

Classify content semantically as one or more of:

- canonical terminology
- product boundary
- interaction behavior
- current architecture
- feature contract
- decision history
- operational procedure
- future plan or draft
- time-bounded snapshot or handoff
- agent instruction or host-specific memory rules
- duplicate, stale, conflicting, or unknown

Review every candidate. Review is an evidence-backed terminal decision, not a requirement to copy its content. A migration may legitimately absorb none of the candidates when all are stale, historical, duplicate, irrelevant, or scanner false positives.

## Truth resolution

Resolve each claim according to what kind of fact it asserts:

| Claim | Governing evidence | Conflict behavior |
|---|---|---|
| Current implementation behavior | Current code, tests, schema/migrations, and configuration | Reject conflicting legacy prose as stale; document the verified current behavior |
| Deployed system or external provider state | Direct runtime, database, deployment, or provider evidence | Do not claim live state from repository evidence alone |
| Canonical terminology or explicit product decision | Human-confirmed context or accepted decision record | Do not infer intent or rationale from code; ask or retain as unresolved/history |
| Historical event | Versioned Git or release evidence | Preserve as historical; never promote it into current state automatically |
| Future plan or draft | Its explicit proposal status | Keep outside current-state documents. Absorb still-intended work into `docs/plans/` with `doccanon_authority: plan`; retire obsolete plans as historical |

Code wins over obsolete prose only for implementation claims that code can prove. Code does not prove why a decision was made, whether it remains intended, or what is deployed externally.

## Disposition decision table

| Source result after review | Action and status | Canonical effect |
|---|---|---|
| Fully current, useful, and already canonical | `adopt` + `integrated` | Keep as canonical owner |
| Fully current and should become a canonical owner | `move` + `integrated` | Move into the canonical tree |
| Contains verified current knowledge missing from canonical docs | `merge` or `split` + `integrated` | Rewrite only accepted claims into owning canonical sections |
| Mixes current and stale claims | `merge` or `split` + `integrated` | Absorb verified claims; record stale claims as rejected, never residual |
| Still-intended future plan or roadmap | `merge` or `move` + `integrated` | Rewrite into `docs/plans/` with `doccanon_authority: plan`; never into current-state owners |
| Conflicts with current implementation evidence | `supersede` + `superseded` | Absorb nothing from the conflict; canonical docs state verified current behavior |
| Historical plan, snapshot, handoff, or obsolete decision record | `archive` + `historical` or `archived` | Retain only as provenance, excluded from normal context |
| Duplicate of an existing canonical owner | `supersede` + `superseded` | No duplicate canonical content |
| Irrelevant material or scanner false positive | `ignore` + `ignored` | No canonical effect |

Do not use `integrated` merely because a source has a target link. Do not use `historical`, `superseded`, or `ignored` as a shortcut without reading the candidate and recording a concrete disposition reason plus evidence.

## Machine-readable manifest

Run `migrate scan` to create `docs/operations/doccanon-migration.json`. Schema 2 distinguishes discovery from actual knowledge integration. For every source containing current durable knowledge, complete an integrated entry:

```json
{
  "source": "path/to/source.md",
  "classification": "current-architecture",
  "action": "merge",
  "status": "integrated",
  "confidence": "high",
  "integrations": [
    {
      "target": "docs/architecture/README.md",
      "sections": ["Runtime topology", "Source-of-truth boundaries"],
      "absorbed_claims": [
        "The Node service owns authenticated application APIs",
        "Supabase owns durable state and ordered migrations"
      ]
    }
  ],
  "verification": ["server/src/index.ts", "supabase/migrations/"],
  "residual_claims": [],
  "source_disposition": "superseded",
  "evidence": ["Claims checked against the current service entry point"],
  "conflicts": [],
  "requires_review": false
}
```

`integrations` is a claim-level receipt, not a pointer. The target must exist, every named section must exist, and `absorbed_claims` must describe the substantive knowledge rewritten into that section. `residual_claims` must be empty before promotion. `verification` records the code, tests, configuration, runtime evidence, or human confirmation used to establish authority.

For a partially useful source, optionally record rejected material without promoting it:

```json
"rejected_claims": [
  {
    "claim": "The Cloudflare Worker is the governing API",
    "reason": "Current Node service replaced this path",
    "evidence": ["server/src/index.ts", "server/railway.toml"]
  }
]
```

Rejected claims are resolved stale material, not `residual_claims`. Residual claims are potentially current knowledge whose authority or destination remains unresolved; any residual claim blocks promotion.

Use these paths:

- `adopt`: the source is already a canonical owner; use `source_disposition: canonical`.
- `move`: the complete source becomes a canonical owner at a new path; use `source_disposition: canonical`.
- `merge` or `split`: rewrite current durable claims into one or more canonical owners; use `source_disposition: superseded` or `archived`.
- `archive`, `supersede`, or `ignore`: the source contributes no current durable knowledge. Supply a concrete `disposition_reason`; these actions must not conceal unabsorbed current claims.

Terminal statuses are `integrated`, `historical`, `superseded`, `ignored`, and `archived`. Only `integrated` means that source contributed knowledge to DocCanon; zero integrated sources is valid when every candidate has an evidence-backed non-integrated disposition. `review`, legacy schema 1 manifests, missing receipts for integrated sources, nonempty residual claims, and unresolved conflicts keep the project in bootstrapping. Directory globs may describe a repeated policy, but they do not replace per-source manifest entries.

## Canonical-only handoff

Before promotion:

1. Read each material source completely enough to decide whether it contains durable current knowledge. Do not deeply analyze executable scanner false positives after confirming their type.
2. Resolve duplicates and conflicts against current code and human-confirmed decisions.
3. Rewrite accepted claims into the owning canonical contracts using the project's terminology. Do not paste incompatible legacy vocabulary verbatim. Rewrite `CONTEXT.md` current-only: absorbed terminology replaces legacy definitions, and retired vocabulary becomes at most a one-line replacement mapping.
4. Record claim-level integration receipts in the manifest.
5. Freeze absorbed legacy documents in the manifest. Add a short replacement notice only to misleading high-traffic legacy entry points; do not rewrite every old source and do not add a repository-specific freeze script.
6. Test a realistic task using only `context --intent` and canonical documents. If the task still requires a legacy source to understand normal current behavior, migration is incomplete.
7. Treat pre-existing repository-root agent instruction files (`AGENTS.md`, `CLAUDE.md`, and host-specific memory rules) as migration sources. Absorb still-useful rules into canonical owners; the generated projection preserves the remainder in its user-owned custom section and never treats it as current truth.

## Safety

- Treat file paths and modification dates as weak evidence.
- Verify current-state claims against code, tests, configuration, and runtime evidence when available.
- Never promote a plan into current truth solely because it is recent.
- Never generate decision rationale from current code.
- Prefer non-destructive absorption plus freezing over deletion. Pointers may retire old sources, but cannot substitute for canonical content.
- Keep unresolved material in place.
- Make the final mapping auditable and idempotent.
- Do not label conflicting rationale as current-state. Put confirmed decisions in ADRs or leave them unresolved.
- Do not promote until `migrate status` reports every candidate reviewed into a terminal disposition and zero unresolved or residual claims.
