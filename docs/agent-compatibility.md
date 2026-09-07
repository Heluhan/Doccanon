# Agent compatibility

DocCanon follows the directory-based Agent Skills format: a `SKILL.md` entrypoint plus local references, scripts, and assets. The deterministic helper behaves the same on every host; discovery and automatic activation are host responsibilities.

| Host | Project install | User install | Notes |
| --- | --- | --- | --- |
| Codex | `.agents/skills/doccanon` | `~/.codex/skills/doccanon` | Native skill directory |
| GitHub Copilot | `.agents/skills/doccanon` or `.github/skills/doccanon` | `~/.copilot/skills/doccanon` | GitHub CLI can manage published skills |
| Gemini CLI | `.agents/skills/doccanon` or `.gemini/skills/doccanon` | `~/.gemini/skills/doccanon` | Native skill directory |
| OpenCode | `.agents/skills/doccanon` or `.opencode/skills/doccanon` | `~/.config/opencode/skills/doccanon` | Native skill directory |
| Claude Code | `.claude/skills/doccanon` | `~/.claude/skills/doccanon` | Native skill directory |
| Cline | `.cline/skills/doccanon` | `~/.cline/skills/doccanon` | Skills may need enabling in Cline settings |
| Cursor | `.agents/skills/doccanon` plus `.cursor/rules/doccanon.mdc` | Not automated | Uses an agent-requested project rule adapter |

`python3 install.py --agent universal --scope project` is the lowest-duplication default for hosts that recognize `.agents/skills`. Use host-specific targets only when the host requires or prefers its own directory.

Run `python3 install.py --dry-run ...` to inspect paths before writing. Start or refresh the agent session after installing so discovery runs again.
