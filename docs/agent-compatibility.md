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

## Generated entry files

Hosts load a repository-root instruction file at session start. DocCanon generates that file from the canonical library instead of leaving it hand-maintained:

- `AGENTS.md` is the shared entry for hosts that read the AGENTS.md standard, including Codex, Cursor, GitHub Copilot, and OpenCode.
- The Claude adapter is a thin `CLAUDE.md` that imports the shared entry with `@AGENTS.md`. Configure adapters with `agent_adapters` in `.doccanon.yml`; set `agent_entry: ""` to opt out of generation.
- The entry is refreshed only when canonical content changes. Its user-owned custom section is preserved verbatim and never treated as current truth.
- `check` and `preflight` are read-only and fail when the projection is missing or stale.

## Search exclusion for retired material

Retirement relocates obsolete documents into the configured archive root and records the pattern in `.ignore`. Ripgrep-based hosts (including Codex, Claude Code, and OpenCode search) skip that tree by default, and a hidden archive directory is skipped by default ripgrep behavior even without the pattern. Hosts with their own ignore conventions may need an additional mapping; keep the archive out of any host-specific index when the host documents one.
