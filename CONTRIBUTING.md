# Contributing

DocCanon separates deterministic repository facts from semantic agent judgment. Changes must preserve that boundary: the helper may detect Git state, mappings, missing receipts, and freshness mechanically; it must not invent product intent or certify semantic truth on its own.

Before opening a pull request:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q install.py scripts skills/doccanon/scripts
```

For behavior changes, add a test that exercises an observable outcome rather than matching only documentation wording. Keep distribution instructions English-first and keep the skill usable without an external service or API key.

Describe the user-visible outcome, affected trust boundary, and verification in the pull request. Do not claim deployment, compatibility, or token savings without direct evidence.
