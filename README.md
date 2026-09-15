# DocCanon

### Stop making every coding agent rediscover your codebase.

**DocCanon is a verified context layer for coding agents.**

It turns durable codebase knowledge into a small, project-local source of truth that agents can reuse across tasks and tools — instead of repeatedly scanning the repository and rebuilding the same understanding from scratch.

```text
Without DocCanon

New task
   ↓
Explore repository
   ↓
Find relevant files
   ↓
Reconstruct architecture
   ↓
Infer how the system works
   ↓
Start the actual task


With DocCanon

New task
   ↓
Load verified project context
   ↓
Inspect relevant code
   ↓
Start the actual task
```

**Less repeated context. Less drift. Less agent lock-in.**

DocCanon keeps canonical knowledge beside your code, checks whether it is still trustworthy on the current branch, routes agents to only the context relevant to the task, and requires affected documentation to move with the implementation.

> **Read the map first. Verify against the territory.**

[GitHub](https://github.com/Heluhan/Doccanon) · [Security contact](mailto:contact@planana.xyz)

---

## Why DocCanon?

Coding agents are getting better at reading large repositories.

But we keep making them solve the same problem again and again.

A new session starts. A new agent joins. You switch from Codex to Claude Code, Cursor, OpenCode, Copilot, or Gemini. The agent searches the repository, reads entry points, traces dependencies, reconstructs architecture, and builds a temporary mental model of the project.

Much of that understanding already existed in the previous session.

It just was not reusable.

DocCanon makes that understanding part of the project.

### Reuse codebase understanding

Stable knowledge about your system should not have to be rediscovered from raw code for every task.

DocCanon maintains a compact canonical knowledge layer so an agent can first understand:

* what the system does,
* where responsibilities live,
* which invariants matter,
* which features and domains are affected,
* and where to verify the relevant implementation.

The agent still reads code when code is needed.

It just does not need to begin every task by treating the entire repository as unknown territory.

### Share context across agents

Your project's memory should belong to the project — not to one model, session, or coding tool.

DocCanon stores canonical knowledge in plain Markdown inside the repository:

```text
CONTEXT.md
docs/
```

That means different coding agents can work from the same project understanding.

```text
Codex ──────────┐
Claude Code ────┤
Cursor ─────────┼──→ Canonical project context ──→ Code
OpenCode ───────┤
Copilot ────────┤
Gemini CLI ─────┘
```

Switch agents without rebuilding the project's context from zero.

### Keep reusable context from becoming stale

Reusable context is only useful if it is trustworthy.

A normal README, `AGENTS.md`, `CLAUDE.md`, rules file, or architecture document can silently drift away from the implementation.

DocCanon treats that as a first-class problem.

Before canonical project knowledge is trusted, DocCanon checks its branch-relative freshness. After implementation changes, it determines which current-state owners are affected and refuses to call the project synchronized while relevant implementation changes remain unaccounted for.

So DocCanon is not just persistent context.

It is **governed persistent context**.

---

## The core loop

For substantive work in a governed project, DocCanon gives the agent a repeatable workflow:

```text
                  ┌─────────────────────┐
                  │   New coding task   │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Check context trust │
                  │ on current branch   │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Load the smallest   │
                  │ relevant context    │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Verify / inspect    │
                  │ relevant code       │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Implement change    │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Update affected     │
                  │ canonical owners    │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Verify code + docs  │
                  │ together            │
                  └─────────────────────┘
```

The user does not need to remember this workflow.

The skill owns it.

---

## A concrete example

Imagine an agent spends time discovering that:

* session recovery is owned by a particular service,
* authentication state crosses two specific boundaries,
* refresh tokens must never be written through a certain path,
* failures follow an established recovery state machine,
* and several tests define the expected behavior.

Tomorrow, another agent receives:

> Add a new session recovery path.

Without durable project context, that agent may search through the same repository and reconstruct much of the same understanding again.

With DocCanon, the agent first receives the relevant canonical feature and architecture context, then inspects the implementation needed to verify and make the change.

Afterward, DocCanon checks whether the implementation affected any governed feature or cross-cutting contract and requires those owners to remain aligned.

The expensive part — understanding the shape of the system — becomes reusable.

---

## Why not just use `AGENTS.md`, `CLAUDE.md`, or normal docs?

Those files can be useful. DocCanon solves a different problem.

| Approach                          | Persistent | Cross-agent | Task-routed | Freshness checked | Change coverage |
| --------------------------------- | :--------: | :---------: | :---------: | :---------------: | :-------------: |
| Agent scans repository            |      ✗     |      ✓      |      —      |         ✓         |        —        |
| Session / provider memory         |      ✓     |      ✗      |    varies   |         ✗         |        ✗        |
| `CLAUDE.md` / tool-specific rules |      ✓     |      ✗      |   limited   |         ✗         |        ✗        |
| Ordinary project docs             |      ✓     |      ✓      |   limited   |     usually ✗     |    usually ✗    |
| **DocCanon**                      |    **✓**   |    **✓**    |    **✓**    |       **✓**       |      **✓**      |

DocCanon does not try to replace code inspection.

It changes where the agent starts.

Instead of:

> **raw repository → reconstruct project model → work**

the intended path becomes:

> **canonical project model → targeted verification → work**

---

## Project knowledge that lives with the code

DocCanon keeps durable knowledge in the repository itself.

`CONTEXT.md` owns confirmed terminology and domain boundaries.

`docs/` holds current-state knowledge such as feature contracts, architecture, product behavior, operations, decisions, and other durable project knowledge.

Current-state documents describe what is true **now**.

Historical logs, plans, drafts, session notes, and superseded documentation are not allowed to silently become current authority.

One fact should have one canonical owner.

---

## Trust before retrieval

Having documentation does not mean the documentation is trustworthy.

DocCanon distinguishes between a project that has merely enabled the skill and a project whose canonical knowledge has actually passed its trust requirements.

A project can be:

```text
enabled
   ↓
bootstrapping
   ↓
governed
```

A governed project has verified current-state owners for applicable knowledge domains and completed migration requirements where relevant.

Only then can canonical context safely substitute for broad repository exploration.

Likewise:

> **enabled ≠ governed**
> **indexed ≠ fresh**
> **clean ≠ synchronized**

DocCanon only claims synchronization when its branch-relative checks actually pass.

---

## Branch-aware truth

Codebase truth is branch-relative.

A feature document updated on a feature branch may accurately describe that branch while being wrong for `main`.

DocCanon therefore ties freshness to Git history and requires verified revisions to be reachable from the current branch.

Affected code and canonical documentation stay together in the same branch and PR.

DocCanon observes Git state, but it does not create, switch, reset, merge, delete, stash, or push branches without explicit authorization.

---

## Change coverage

One of the easiest ways for documentation systems to fail is simple:

the implementation changes, but nobody realizes which documents also became stale.

DocCanon treats every changed implementation file as review-required.

After a substantive change, it builds an impact plan that asks:

```text
Which feature owns this change?

Which current-state contracts are affected?

Did this change introduce a new capability?

Are any governed domains affected?

Is any changed implementation file still unaccounted for?
```

Each relevant change must either map to a canonical owner or receive a concrete evidence-backed exclusion.

DocCanon refuses completion while required owners are stale, governed domains remain unreviewed, implementation files remain unexplained, or verification is missing.

---

## Brownfield projects

DocCanon is designed for existing repositories, not only greenfield projects.

Existing documentation is not automatically trusted just because it already exists.

During migration, DocCanon reviews candidate knowledge sources and decides whether their useful claims should be:

* adopted,
* merged,
* moved,
* split,
* superseded,
* rejected as stale,
* preserved only as history,
* or excluded as irrelevant.

Implementation behavior is checked against code, tests, schemas, configuration, Git evidence, or runtime evidence where appropriate.

Human intent is different.

DocCanon will not invent product intent, rationale, or historical decisions merely because the current code appears to imply them.

After migration, normal work should be possible from the canonical library without repeatedly reopening legacy documentation.

---

## Token efficiency

DocCanon is designed to reduce **repeated repository exploration**.

Instead of broadly searching the codebase before every task, the agent first receives a small relevant canonical bundle and then performs targeted code verification.

Conceptually:

```text
Broad exploration

Task
 ↓
large repository search
 ↓
many files
 ↓
reconstruct context
 ↓
target code


DocCanon routing

Task
 ↓
small canonical context
 ↓
target code
```

This can reduce the amount of context an agent needs to consume on many brownfield tasks.

But DocCanon does **not** claim a universal token-savings percentage.

Token use depends on repository shape, task type, model, agent implementation, cache behavior, and documentation quality.

You can measure the context-volume mechanism locally:

```bash
python3 /path/to/doccanon/skills/doccanon/scripts/measure_context.py \
  --project . \
  --intent "change session recovery" \
  --baseline tracked-code \
  --json
```

This is a **context-reduction proxy**, not observed model token usage or cost.

For publishable token claims, use the paired control/treatment protocol in [`skills/doccanon/references/token-benchmark.md`](skills/doccanon/references/token-benchmark.md) and summarize provider-reported usage with:

```bash
python3 scripts/summarize_token_benchmark.py benchmarks/runs.csv --json
```

Until controlled results exist, the accurate claim is:

> **DocCanon routes coding agents to a small, fresh canonical context before targeted code verification.**

---

## Install

DocCanon is an Agent Skills-compatible directory.

It requires:

* Git
* Python 3.10+

There is no runtime service, API key, vector database, or model dependency.

### GitHub CLI

With GitHub CLI 2.90 or later:

```bash
gh skill preview Heluhan/Doccanon doccanon
gh skill install Heluhan/Doccanon doccanon
```

### Project install

For a portable project-level install:

```bash
git clone https://github.com/Heluhan/Doccanon.git
cd Doccanon

python3 install.py \
  --agent universal \
  --scope project \
  --project /path/to/project
```

The universal project target installs:

```text
.agents/skills/doccanon
```

This location is recognized by Codex, GitHub Copilot, Gemini CLI, and OpenCode.

For host-specific placement:

```bash
python3 install.py --agent codex --scope user
python3 install.py --agent claude --scope user
python3 install.py --agent copilot --scope project --project /path/to/project
python3 install.py --agent gemini --scope user
python3 install.py --agent opencode --scope user
python3 install.py --agent cline --scope user
python3 install.py --agent cursor --scope project --project /path/to/project
```

See the full [agent compatibility matrix](docs/agent-compatibility.md).

You can install for multiple hosts by repeating `--agent`, or use:

```bash
python3 install.py --agent all --scope project --project /path/to/project
```

Preview any installation before writing:

```bash
python3 install.py --dry-run ...
```

The installer does not overwrite unmanaged existing skill directories. Updates preserve a versioned `doccanon.previous-*` copy for review.

Start or refresh the coding-agent session after installation so the host can discover the skill.

---

## Quick start

After installation, open your coding agent and say:

> **Set up DocCanon for this project.**

That is the only DocCanon-specific workflow the user needs to learn.

For an unconfigured substantive repository, DocCanon asks before enabling governance.

It recommends staying disabled for disposable prototypes, scratch projects, isolated snippets, and other cases where maintaining durable project knowledge would cost more than it saves.

For an existing project, initialization does more than generate files.

DocCanon inventories the implemented system, reconstructs shipped capabilities, establishes current-state owners, verifies them against implementation evidence, and promotes the project to governed status only after the trust gate passes.

After that, use your coding agent normally.

---

## Try the failure mode

Want to see why the trust boundary exists before installing anything?

Run:

```bash
python3 scripts/demo.py
```

The demo creates a disposable Git repository, establishes a governed baseline, changes covered code without updating its canonical owner, and demonstrates DocCanon refusing to treat the resulting state as synchronized.

---

## Agent compatibility

| Agent          | Project support                                          | User support                         |
| -------------- | -------------------------------------------------------- | ------------------------------------ |
| Codex          | `.agents/skills/doccanon`                                | `~/.codex/skills/doccanon`           |
| GitHub Copilot | `.agents/skills/doccanon` or `.github/skills/doccanon`   | `~/.copilot/skills/doccanon`         |
| Gemini CLI     | `.agents/skills/doccanon` or `.gemini/skills/doccanon`   | `~/.gemini/skills/doccanon`          |
| OpenCode       | `.agents/skills/doccanon` or `.opencode/skills/doccanon` | `~/.config/opencode/skills/doccanon` |
| Claude Code    | `.claude/skills/doccanon`                                | `~/.claude/skills/doccanon`          |
| Cline          | `.cline/skills/doccanon`                                 | `~/.cline/skills/doccanon`           |
| Cursor         | `.agents/skills/doccanon` + rule adapter                 | —                                    |

Host discovery and activation behavior belongs to the host. DocCanon's deterministic helper behaves consistently across supported placements.

---

## What DocCanon is not

DocCanon is not:

* a replacement for source code,
* a codebase RAG service,
* a vector database,
* a transcript or session-memory store,
* a Git branch manager,
* a spec generator,
* an excuse to document every implementation detail,
* or an authority that invents product decisions from code.

Code, tests, schemas, configuration, and direct runtime evidence remain the final proof of implementation behavior.

DocCanon gives agents a better starting point and keeps that starting point accountable to the implementation.

---

## Deterministic helper

The skill uses:

```text
skills/doccanon/scripts/doccanon.py
```

internally.

Useful diagnostics include:

```bash
python3 skills/doccanon/scripts/doccanon.py \
  --project /path/to/repo status --json

python3 skills/doccanon/scripts/doccanon.py \
  --project /path/to/repo check --json

python3 skills/doccanon/scripts/doccanon.py \
  --project /path/to/repo context \
  --intent "add session recovery" \
  --json

python3 skills/doccanon/scripts/doccanon.py \
  --project /path/to/repo sync plan --json

python3 skills/doccanon/scripts/doccanon.py \
  --project /path/to/repo preflight \
  --target main \
  --json
```

The agent — not the user — owns the full:

```text
sync plan
   ↓
semantic documentation update
   ↓
verification
   ↓
sync complete
```

workflow.

Read-only checks and Git hooks never mutate project documentation.

---

## Design principles

### Project memory belongs to the project

Canonical knowledge should survive model changes, agent changes, sessions, and tooling choices.

### Context should be smaller than the codebase

Agents should begin with compressed project understanding, then inspect source code where evidence is required.

### Persistent context must be verifiable

Making stale knowledge easier to retrieve makes the problem worse, not better.

### Code proves mechanics; humans own intent

Implementation can establish what the system currently does. It cannot reliably establish why a product decision was made or what a human intended.

### Documentation changes with implementation

Canonical current-state knowledge is part of the change surface, not a cleanup task for later.

---

## Development

Run the local test suite:

```bash
python3 -m unittest discover -s tests -v
```

Validate the skill:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py skills/doccanon
```

Contributions should preserve the boundary between deterministic repository facts and semantic agent judgment.

Security reports can be sent to [contact@planana.xyz](mailto:contact@planana.xyz).

---

## License

MIT.

---

**DocCanon turns codebase understanding from something every agent repeatedly reconstructs into something the project can preserve, verify, and reuse.**
