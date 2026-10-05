---
name: process-run
description: Re-run the measured work-item dry run in a disposable sandbox clone, grade the previous run's findings against what actually landed, and report what in the repository can be compacted. Use when the operator wants a fresh measured run of the team's workflow, including via "/process-run". Do not use to draft work items from the findings or to apply a compaction candidate; both stay for the operator and a later item.
---

# process-run

Run by the coordinator, in the operator's main session only. The run dispatches real gate
agents, and subagents cannot spawn subagents. Inside the sandbox clone this skill builds, and
nowhere else, the session gives instant operator rulings: promote, route approval and done. A question a gate agent hands back inside the clone is ruled instantly
too, on the reading the item's text best supports; record each such ruling and its reason
in the findings file's Method section. Outside the clone the real operator still holds every
gate.

This measures `.claude/agents/coordinator.md`, `.claude/skills/team-promote/SKILL.md`,
`.claude/skills/team-next/SKILL.md`, `.claude/skills/team-work/SKILL.md`,
`.claude/skills/team-review/SKILL.md` and `.claude/skills/close-work/SKILL.md` as they read
today, run against the fixture in `improvement/process-runs/fixture/`, never a copy of any of
them. A copy would drift from the process it measures, and the run would then measure the copy.

## 1. Build the sandbox

`SCRATCHPAD` is this session's scratchpad directory, the absolute path the coordinator reads from
its own system prompt ("Scratchpad directory"). It is not an environment variable. If the system
prompt names none, create one with `mktemp -d` outside the repository and use that path for
the whole run. Clone this
repository's checkout to exactly `<SCRATCHPAD>/process-run-clone`; that path is `CLONE`. If the clone has an `origin`,
remove it with `git remote remove origin`, then run `git remote -v` in the clone. Stop and report
if it prints anything. If the clone's checked-out branch is not `main`, rename it with
`git branch -m main`, so the **Shared-clone guard** holds there: the run proceeds only against a clone with no remote at all, so nothing
here can reach a real remote. Local mode (`.claude/agents/coordinator.md` §7) then applies in the
clone with no further setup.

## 2. Use the fixture unchanged

Copy `improvement/process-runs/fixture/GEN-9999-queue-counts-script.md` into the clone's
`work/drafts/`, then `git add` it and commit it on the clone's `main` as
`Draft GEN-9999 [session <marker>]`, so the promotion's `git mv` finds a tracked file. Read it
as written. Where something it names has since changed so a criterion no
longer holds as written, adapt only the words naming the changed thing, nothing else, and record
exactly what changed and why in the findings file's Method section.

## 3. Take the item from draft to done

Inside the clone, follow the six measured files named above exactly as they read there today,
from the promote through the claim, the route, the build, the review and the close. Never restate
their steps, their gate order, or any agent's prompt text, here or in the findings file; point at
the file instead. A pull request is never opened: `/open-pr` refuses in Local mode, and
`/close-work` merges the item branch locally.

Invoke each gate agent with the prompt `improvement/process-runs/fixture/agent-prompts.md` gives
it, copied word for word at invocation time and never pasted into this file, passing no model and
letting each agent's own `model:` line apply.

## 4. Log the timing

Keep the timing file at exactly `<SCRATCHPAD>/process-run-timing.tsv`; that path is `TIMING`. One row per stage, its start time, its end time, and, for
every agent invoked in that stage, the tokens, tool uses and duration it reports. This is the
file the next run's Timeline section reads against.

## 5. Close, then check, then report

After the close, confirm the real repository carries no GEN-9999 file outside
`improvement/process-runs/fixture/`, branch or worktree, and state that check's result in the
findings file. Then run `python3 scripts/process-run-report.py` in both its `agents` and `sizes`
modes, the first pointed at this session's own subagent transcript directory, the second run
against the real repository, and run `python3 scripts/context-check.py` once against the real
repository.

## 6. Write the findings

Write `improvement/process-runs/<date>-findings.md` with these sections, in this order: Method;
Timeline against the previous run; Scorecard; New slowdowns, ranked by cost; Compaction review;
What this run could not show. On the first run, Timeline and Scorecard say "baseline, no
previous run". Copy the timing file beside it. Append one row to
`improvement/process-runs/scoreboard.tsv`, one cell per column, empty where this run recorded
nothing.

## 7. Scorecard

List every finding the previous run's findings file names. For each, name the work item or
ruling filed against it and grade it landed, not landed, or unchanged by ruling. Every grade
carries the observation that supports it: a command run, a file read, or a ruling quoted, never
a bare assertion.

## 8. Compaction review

Report-only: this step changes nothing it measures, and drafts nothing itself. Carry the four
section counts `context-check.py` just printed. Then, from the `sizes` report, list every file
whose bytes grew since the last scoreboard row. For each growing file, name what grew and by how
much, name where its content would live afterwards, either a pointer target it could collapse to
or the source it could be regenerated from, and say whether acting on it is a tooling item or
direct operator work. A file with nowhere for its content to go is not a candidate; list it under
growth only, with no action named.

## 9. Separate like-for-like cost from loop cost

Report each stage's cost as it would have run on a single clean pass, separately from any extra
cost a Return or a must-fix added on top. A loop is partly chance; conflating the two makes runs
incomparable.

## 10. Ask what becomes an item

End by asking the operator, with `AskUserQuestion`, which findings become work items. Draft
nothing yourself; this skill's job stops at naming candidates.

## 11. Commit and reply

Commit the findings file, its timing copy and the scoreboard row together, on `main` in the
primary checkout (or, when the run is itself a work item's verification, on that item's
branch in its worktree, saying so in Method), following the shared-clone rules in `.claude/agents/coordinator.md` §7 and
`standards/writing.md`. Reply with the findings file's path, the run's total time and tokens
against the previous row, and the count of compaction candidates found, nothing longer.

## 12. Clear stale agents

After the reply, run `/clear-stale-agents` with a cutoff of 10 minutes, the shortest it
accepts, to close the idle pixel-agents characters this run's agents left. Run this one Bash
call, replacing the quoted path with the primary checkout's absolute path:

```
node "<the primary checkout's absolute path>/.claude/skills/clear-stale-agents/clear-stale-agents.mjs" 10; echo "clear-stale-agents exit $?"
```

Report the result in one line, then go on to step 13 whatever it printed. Exit 0: give the
closed and after counts. Exit 2: pixel-agents is not reachable, so nothing was closed; say
so. Any other exit: quote the error line. This step asks the operator nothing and never
stops the run. Agents that finished less than 10 minutes ago stay; they close when their
session ends or on a later `/clear-stale-agents`. The cutoff also closes any other session's
character idle past 10 minutes; the session itself is untouched.

## 13. Remove the sandbox

After the reply, remove only what this run created: `CLONE`, the clone directory step 1 built, and
`TIMING`, the timing file step 4 kept. Never touch the real repository, and never run
`git worktree remove --force` there. Shell variables do not persist between Bash calls, so this
step assigns every variable itself, in one block. Replace the two quoted paths with the values
the coordinator knows: its scratchpad directory (system prompt) and the primary checkout's
absolute path. `CLONE` and `TIMING` are the fixed names from steps 1 and 4. Every `git` command
names the clone with `-C "$CC"`, the canonical `CLONE`, and nothing outside the clone is forced.

The guard refuses and exits, removing nothing, when any of `SCRATCHPAD`, `REPO`, `CLONE` or
`TIMING` is empty; when `SCRATCHPAD` is not an existing directory; when `CLONE` or `TIMING`,
resolved to a canonical path (symlinks and `..` followed, portable to macOS where `/tmp` is
`/private/tmp` and `realpath -m` is absent), is not strictly inside the canonical `SCRATCHPAD`;
when `CLONE` equals `SCRATCHPAD`; when `CLONE` is, or contains, the real repository; when
`SCRATCHPAD` equals, contains or is inside `REPO`; when `CLONE` is not the toplevel of its own git
checkout; or when `CLONE` is a linked worktree (its common git dir is not `CLONE/.git`).

```
SCRATCHPAD="<this session's scratchpad directory>"
REPO="<the primary checkout's absolute path>"
CLONE="$SCRATCHPAD/process-run-clone"
TIMING="$SCRATCHPAD/process-run-timing.tsv"
refuse() { echo "refusing: $1; nothing removed"; exit 1; }
canon() { # absolute canonical path; the last part need not exist
  case "$1" in /*) ;; *) return 1 ;; esac
  b=$(basename -- "$1"); case "$b" in .|..|/) return 1 ;; esac
  d=$(cd "$(dirname -- "$1")" 2>/dev/null && pwd -P) || return 1
  if [ "$d" = / ]; then printf '/%s\n' "$b"; else printf '%s/%s\n' "$d" "$b"; fi
}
[ -n "$SCRATCHPAD" ] && [ -n "$REPO" ] && [ -n "$CLONE" ] && [ -n "$TIMING" ] || refuse "a path is empty"
SP=$(cd "$SCRATCHPAD" 2>/dev/null && pwd -P) || refuse "SCRATCHPAD is not a directory"
RP=$(cd "$REPO" 2>/dev/null && pwd -P) || refuse "REPO is not a directory"
case "$SP/" in "$RP"/*) refuse "SCRATCHPAD is or is inside the real repository" ;; esac
case "$RP/" in "$SP"/*) refuse "SCRATCHPAD contains the real repository" ;; esac
CC=$(canon "$CLONE") || refuse "CLONE does not resolve"
TC=$(canon "$TIMING") || refuse "TIMING does not resolve"
[ "$CC" != "$SP" ] || refuse "CLONE is SCRATCHPAD"
case "$CC" in "$SP"/?*) ;; *) refuse "CLONE is not inside SCRATCHPAD" ;; esac
case "$TC" in "$SP"/?*) ;; *) refuse "TIMING is not inside SCRATCHPAD" ;; esac
case "$RP/" in "$CC"/*) refuse "CLONE is or contains the real repository" ;; esac
[ "$(git -C "$CC" rev-parse --show-toplevel 2>/dev/null)" = "$CC" ] || refuse "CLONE is not a git checkout root"
GD=$(cd "$CC" && cd "$(git rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd -P)
[ "$GD" = "$CC/.git" ] || refuse "CLONE is a linked worktree, not a standalone clone"
git -C "$CC" worktree list --porcelain | sed -n 's/^worktree //p' | tail -n +2 |
  while IFS= read -r wt; do git -C "$CC" worktree remove --force "$wt"; done
rm -rf "$CC" "$TC"
test ! -e "$CC" && echo "Sandbox removed: $CC no longer exists."
```

The first `worktree` line `git worktree list` prints is the clone itself, so `tail -n +2` leaves
only the worktrees added inside it. If the final `test` prints nothing, or the guard printed
"refusing", say so and stop; do not retry with other paths.
