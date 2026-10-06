# Branch-aware governance

## Boundary

DocCanon observes Git state; it does not manage Git. Never switch, create, reset, stash, merge, delete, or push a branch unless the user explicitly requests that action.

Current-state authority is branch-relative:

- A feature branch documents the implementation that exists on that feature branch.
- The integration branch documents changes accepted for continued development.
- A release branch documents changes included in that release line.

Keep code and affected canonical docs in the same commit or pull request. Merging them together naturally promotes the branch-local state into the target branch.

## Baseline

Prefer `.doccanon.yml` `integration_branch`. Otherwise infer the closest existing ancestor among `develop`, `main`, and `master`. Use remote tracking refs when present. Report the selected ref; never hide the comparison base.

Before a PR or merge, run `preflight --target <target>`. Review affected features, stale feature contracts, changed canonical docs, and the underlying freshness check.

## Initialization and migration

Repository-wide initialization or migration on a dirty feature branch mixes unrelated histories and weakens review. Refuse by default and recommend one of:

1. Finish or preserve the current work, then bootstrap from the clean integration branch.
2. Create an isolated worktree based on the integration branch after user approval.
3. Continue on the feature branch only when the user explicitly accepts the mixed scope.

Never interpret permission to initialize DocCanon as permission to manipulate existing branches or dirty work.

## Verification ancestry

`doccanon_verified_at` must exist and be an ancestor of the current branch. A commit reachable only from another branch cannot prove the current branch's documentation. After conflict resolution or history rewriting, reverify affected documents against the new branch history.

## Complex repositories

Configure only when automatic inference is insufficient:

```yaml
integration_branch: develop
release_branches:
  - main
```

Do not force this topology on repositories that use a single `main` or `master` branch.
