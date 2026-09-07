# Security policy

DocCanon is local software that reads repository content and may write project documentation when an agent follows the skill. It does not require network access, credentials, or telemetry.

Review the skill and bundled Python scripts before installation. The installer refuses to overwrite or remove directories it did not create. Git hooks installed by DocCanon are read-only checks and never rewrite documentation during a commit.

Report suspected command injection, unsafe path handling, destructive installation behavior, or trust-gate bypass privately to [contact@planana.xyz](mailto:contact@planana.xyz). Do not include secrets or private repository content in a public issue.
