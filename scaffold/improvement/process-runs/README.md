# Process runs

Measured dry runs of this team's work-item workflow: one synthetic code item taken from `draft`
to `done` in a sandbox clone with no remote, every gate agent run for real, rulings instant. The
point is to see where the time and tokens go and whether a process change helped. Nothing here is
a real work item. Run it with `/process-run` (`.claude/skills/process-run/SKILL.md`).

A summary of `scoreboard.tsv`, one row per run:

| Run (`date`) | Commit (`commit`) | Total time (`total_seconds`) | Subagent tokens (`subagent_tokens`) | Design passes (`design_passes`) | Returns (`returns`) | Findings |
| --- | --- | --- | --- | --- | --- | --- |

One run per row: gate agents are not deterministic, so read a row beside its findings file, which
separates like-for-like stage costs from the cost of a loop that happened to occur.

- `fixture/GEN-9999-queue-counts-script.md` is the item in its `draft` state. A new run reuses it
  unchanged, adapting it only where something it names has changed, and says so.
- `fixture/agent-prompts.md` holds the gate agent prompts, copied word for word at dispatch.
- `scoreboard.tsv` holds one row per run. The `sizes` columns are named by the keys that
  `scripts/process-run-report.py sizes` prints, so the next run can compute growth. Per-agent
  tokens are in each run's timing file, since which roles run depends on this team's routing.

## scripts/process-run-report.py

Report-only: writes nothing. Python 3, standard library only.

```
python3 scripts/process-run-report.py agents <transcript-dir> [--command <substring> ...]
python3 scripts/process-run-report.py sizes [--scoreboard <file>]
```

- `agents` reads the `agent-*.jsonl` files (and `.meta.json` beside each) in a subagent transcript
  directory under `~/.claude/projects/`. It prints, per agent, its type, the model asked and the
  model that ran, first-turn context, output tokens (or `NOT AVAILABLE` with a lower bound when
  the transcript never finalised its messages), all tool uses with a Read and Bash breakdown, its
  five largest reads, and a count per `--command` substring. It ends with a total line.
- `sizes` prints the byte size of `team/decisions.md`, `improvement/signals/review-log.md`,
  `improvement/signals/promotion-diffs.md`, the total of `work/designs/`, and
  `instruction-file-words`, with growth since the scoreboard's last row when there is one.

## scripts/context-check.py

Report-only: writes nothing, never fixes a finding. Run from anywhere.

```
python3 scripts/context-check.py
python3 scripts/context-check.py --strict
```

Instruction files are `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`,
`standards/*.md` and `team/*.md`. Plain mode always exits 0; `--strict` exits 1 when any section
is non-empty. Four sections, always printed in this order, each `none` when empty:

1. Files over their word budget. `BUDGETS` is seeded at each file's size when the team is
   created, so it flags growth only. Tighter budgets are the operator's call, as is a budget for
   a file added later. A budgeted file that is missing is reported here too.
2. Paragraphs of 12 or more words repeated across instruction files.
3. Backticked repository paths that do not exist.
4. Em dashes in instruction files, with line numbers.
