# Upgrading an existing DocCanon project

DocCanon evolves with the skill, while projects keep the state written by older versions. An upgrade is a review pass over that legacy state: deterministic detection, idempotent mechanical cleanup, and explicit semantic decisions. It is not a fresh migration and never a silent rewrite.

## Version anchor

`.doccanon.yml` records `doccanon_version`: the skill version the project has been reconciled with. A missing value means the project predates the upgrade mechanism (legacy). Only a completed reconciliation pass stamps the version; ordinary task work never moves it.

## Detect and apply

```bash
doccanon upgrade status --json   # read-only checklist
doccanon upgrade apply --json    # mechanical cleanup, stamp only when clear
```

- `config-cleanup` (mechanical): removes fields retired by newer versions.
- `version-stamp` (mechanical): written only when no semantic step remains.
- Semantic steps require judgment and evidence; resolve them with the owning command or skill step.
- `upgrade apply` is idempotent and resumable; a blocked pass reports `in-progress` and lists the pending steps.

Never resolve a semantic step by disabling a check, deleting history, or editing the manifest to hide a discrepancy.

## Version notes

- 0.9 introduced the generated agent entry; entries written before it are hand-written.
- 0.10 introduced the plan authority; roadmaps or proposals stored elsewhere need classification.
- 0.11 made retirement a relocation with default search exclusion; earlier migrations froze sources in place.
- 0.12 removed retired configuration fields and stopped treating repository-meta files as implementation.
- 0.13 added authority validation, mixed-language tokenization, and this upgrade mechanism.

## Structural legacy

| Artifact | Detection | Resolution |
|---|---|---|
| Hand-written agent entry (pre-0.9) | entry file without the generated marker | Absorb durable rules into canonical owners, then run `render`; the remainder is preserved as the user-owned custom section. Or opt out with `agent_entry: ""`. |
| In-place frozen sources (pre-0.11) | non-integrated migration sources still in the tree | Review each source: `retire` it into the archive, absorb it into a canonical owner, or keep it as a canonical document. Give `ignored` sources the closest review; they may be active knowledge that migration only set aside. |
| Hand-written adapter for an unconfigured host | known adapter file exists without the generated marker | Add the adapter to `agent_adapters` and reconcile, or remove the file. |
| Retired configuration fields | `config-cleanup` step | `upgrade apply`. |

## Semantic legacy

| Artifact | Detection | Resolution |
|---|---|---|
| Unknown authority values (`proposal`, `decision`, ...) | `invalid-authority` warning | Classify into the declared vocabulary. Accepted decisions use `append-only`; future work uses `plan`; current behavior uses `current-state` with code coverage. |
| Unclassified decision records | `unclassified-decision-record` warning | Accepted ADRs declare `doccanon_authority: append-only`. |

## Provenance legacy

Missing manifest sources cannot be restored. `upgrade status` reports their count; provenance relies on Git history or removed material. Do not rewrite the manifest to hide the gap.

## Completion

The pass is complete when `upgrade status` reports `current` and `check` no longer reports `project-upgrade-required`. Record the reconciliation in development history like any other meaningful milestone.
