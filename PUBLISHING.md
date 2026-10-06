# Publishing checklist

DocCanon 0.10.0 is structured as a GitHub Agent Skills repository. Before the first public release:

1. Publish from the canonical repository at `https://github.com/Heluhan/Doccanon`.
2. Keep the public maintainer identity `Heluhan` and security contact `contact@planana.xyz` current.
3. Run `python3 -m unittest discover -s tests -v` on Linux, macOS, and Windows through GitHub Actions.
4. With GitHub CLI 2.90 or later, run `gh skill publish --dry-run` and inspect every warning. Preview the repository from a separate checkout before installing it.
5. Tag `v0.10.0`; install the pinned tag into a disposable project for each advertised native host and verify that a fresh session discovers `doccanon`.
6. Record one real brownfield setup walkthrough. Show the repository state before initialization, the trust gate, one stale-code failure, the corrected owner, and the final `synchronized` output.
7. Do not publish a token-savings percentage until the paired protocol in `skills/doccanon/references/token-benchmark.md` reaches its reporting gate. Publish the task set and raw anonymized run table with the summary.

Recommended launch sentence:

> OpenSpec tells coding agents what to build. DocCanon proves what the codebase is now.

Recommended 30-second demo sequence:

```bash
python3 scripts/demo.py
python3 install.py --agent universal --scope project --project /path/to/demo-project
```
