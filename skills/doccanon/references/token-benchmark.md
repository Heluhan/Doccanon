# Token-efficiency benchmark

DocCanon is designed to reduce repeated repository exploration by routing an agent to a small, fresh canonical bundle. That mechanism is real; a universal percentage claim is not. Repository shape, task type, agent, model, cache behavior, and documentation quality all affect token use.

## Fast context-volume proxy

Run this inside a governed project:

```bash
python3 /path/to/doccanon/skills/doccanon/scripts/measure_context.py \
  --project . \
  --intent "change session recovery" \
  --baseline tracked-code \
  --json
```

`tracked-code` compares the selected canonical context with all Git-tracked code. It is an upper-bound corpus comparison, not observed agent behavior and not a model token count. For a fairer task-specific proxy, record the code files a control agent actually read and pass them through `--baseline file-list --baseline-file-list <path>`.

## Publishable A/B protocol

1. Select at least five representative brownfield tasks before running the benchmark. Include a localized change, a cross-cutting change, a bug investigation, an operations change, and an unfamiliar-feature question.
2. Use clean, equivalent worktrees. The control contains the same code but no DocCanon routing. The treatment contains synchronized DocCanon documentation.
3. Hold the model, agent version, system instructions, permissions, task wording, and cache state constant.
4. Run each task at least three times per variant. Randomize run order.
5. Capture actual provider- or agent-reported input tokens, output tokens, tool calls, elapsed time, completion status, and the final diff or answer.
6. Grade both variants with the same task-specific rubric. Token reduction is publishable only when treatment success is no worse than control success.
7. Report medians and ranges, not only the best run. Preserve failed runs.

Record every run with at least: task, variant, run number, input and output tokens, tool calls, elapsed seconds, success, and notes. Keep the raw rows and report medians, ranges, and failed runs. A result is reportable only after both variants have at least 15 runs across at least 5 paired tasks and the DocCanon success rate is no worse than the control. That is a minimum reporting gate, not proof that the result generalizes to other repositories or agents.

## Safe public wording before A/B results exist

> DocCanon routes coding agents to a small, branch-aware canonical context before targeted code verification. A reproducible token benchmark is in progress; no universal savings percentage is claimed yet.

After a valid benchmark, use bounded wording such as:

> In N paired runs across K pre-selected tasks on repository R, DocCanon reduced median reported input tokens by X% while maintaining Y% task success. Results vary by repository, task, model, and agent.
