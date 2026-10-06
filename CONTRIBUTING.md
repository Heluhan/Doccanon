# Contributing

DocCanon separates deterministic repository facts from semantic agent judgment. Changes must preserve that boundary: the helper may detect Git state, mappings, missing receipts, and freshness mechanically; it must not invent product intent or certify semantic truth on its own.

## Branching and versioning

Version numbers belong to the trunk. `main` owns the version fields in `.codex-plugin/plugin.json` and `skills/doccanon/SKILL.md`, the `CHANGELOG.md` release sections, and release tags.

- Feature branches are identified by name and commits, never by a version. Do not bump version fields or add a dated changelog section on a branch.
- Releases happen on `main` as a release commit (version fields plus changelog) followed by a tag `vX.Y.Z`. `gh skill` resolves installs and updates from the latest tag.
- If a branch needs to note pending work, use an `Unreleased` heading; never mint a version.
- CI rejects a pull request that changes the version relative to its base branch (`scripts/check_version_policy.py`).

Before opening a pull request:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q install.py scripts skills/doccanon/scripts
```

For behavior changes, add a test that exercises an observable outcome rather than matching only documentation wording. Keep distribution instructions English-first and keep the skill usable without an external service or API key.

Describe the user-visible outcome, affected trust boundary, and verification in the pull request. Do not claim deployment, compatibility, or token savings without direct evidence.
