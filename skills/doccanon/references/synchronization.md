# End-to-end synchronization

Use this protocol for every substantive task in a governed project. The user describes the development outcome; the Agent owns all DocCanon operations.

## Impact plan

After implementing and verifying code, run `sync plan --json`. Treat its output as a mandatory review queue:

- `affected_features` maps changed implementation files to existing feature contracts.
- `affected_current_state_owners` maps them to product, interaction, architecture, feature, or operations owners through `doccanon_covers`.
- `unmapped_implementation_files` contains every changed implementation file claimed by neither a feature nor a current-state owner.
- `review_domains` contains every governed domain that must receive an affected or excluded decision.

Do not interpret an unmapped file as having no documentation impact. Review it semantically:

- If it introduces or materially changes a cohesive user or operator capability, create or update its feature contract and feature-manifest entry. Add accurate code patterns so rerunning the plan maps the file.
- If it changes a shared interaction, architecture, product, or operations boundary, update the corresponding current-state owner and its coverage metadata.
- Exclude it only when it has no durable semantic effect, such as a fixture, formatting-only change, or generated artifact. Record a concrete file-level reason.
- Repository-meta files (root README, LICENSE, CHANGELOG, and VCS or editor dotfiles) are not implementation files.
- Generated agent entry files (`AGENTS.md` and configured adapters) are projections rather than implementation. The helper keeps them out of the implementation map; the user-owned custom section is never treated as current truth.

## Domain review

Review every configured domain even when path coverage did not infer an impact. Mark a domain affected when behavior, boundaries, states, failure modes, invariants, dependencies, operations, or user experience changed. Update at least one current-state owner for every affected domain.

Exclude an unaffected domain with a concrete reason. A generic statement such as "not applicable" is not a review. Inferred affected domains cannot be excluded while their covered implementation changed. Plans and generated entries are not current-state owners; updating them does not satisfy a domain review.

## Completion gate

Run `sync complete` only after the impact plan has been resolved. Supply affected-domain decisions, domain exclusions, exact file exclusions, actual verification, and the meaningful development outcome. During release work, also supply the explicit version and direct release evidence.

Completion must fail when any of these remain:

- an affected feature contract or current-state owner was not updated;
- an implementation file is unmapped and has no file-level exclusion receipt;
- a governed domain has no affected or excluded decision;
- an affected domain has no changed current-state owner;
- the generated agent entry projection is missing or stale;
- for a release, a plan targeting the release version is not `ready` or `shipped`;
- code and canonical freshness checks do not pass;
- verification evidence is absent;
- a meaningful milestone has no development record or justified history exclusion;
- a release claim lacks direct release evidence.

On success, append the development record automatically with its documentation-impact receipt and refresh the agent entry projection when its content changed. If the task is a verified release, also write the release record. Repeated completion is idempotent.

## Read-only boundaries

`sync plan`, `check`, `preflight`, CI, and Git hooks are read-only. `sync complete` is the explicit Agent-owned write boundary for historical records after canonical documents have already been updated. Never mutate documentation from a commit hook.
