# Publishing checklist

DocCanon 0.14.2 is structured as a GitHub Agent Skills repository. Before the first public release:

1. Publish from the canonical repository at `https://github.com/Heluhan/Doccanon`.
2. Keep the public maintainer identity `Heluhan` and security contact `contact@planana.xyz` current.
3. Run `python3 -m unittest discover -s tests -v` on Linux, macOS, and Windows through GitHub Actions.
4. With GitHub CLI 2.90 or later, run `gh skill publish --dry-run` and inspect every warning. Preview the repository with `gh skill preview Heluhan/Doccanon doccanon` before installing it.
5. Bump the version only in the release commit on `main`, then tag `vX.Y.Z`. Branches never carry version bumps; `main` and the tag are the single version source.
6. Create the GitHub Release for the tag: `gh release create vX.Y.Z --title "DocCanon X.Y.Z" --notes-file <notes>`. `gh skill` resolves the latest GitHub Release, not merely the newest git tag, so a tag without a Release is not installable by default.
7. Verify the published path end to end: `gh skill preview Heluhan/Doccanon doccanon` shows the new tree, `gh skill install ... --scope project` reports the new ref, and `gh skill update --dry-run` lists no pending update for `doccanon`.
8. Record one real brownfield setup walkthrough. Show the repository state before initialization, the trust gate, one stale-code failure, the corrected owner, and the final `synchronized` output.
9. Do not publish a token-savings percentage until the paired protocol in `skills/doccanon/references/token-benchmark.md` reaches its reporting gate. Publish the task set and raw anonymized run table with the summary.

Recommended launch sentence:

> OpenSpec tells coding agents what to build. DocCanon proves what the codebase is now.

Recommended 30-second demo sequence:

```bash
python3 scripts/demo.py
python3 install.py --agent universal --scope project --project /path/to/demo-project
```
