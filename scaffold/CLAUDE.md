# {{team_name}}

{{team_purpose}}

Read this first, then `team/charter.md`. Do not read the whole repository up front.

## The five rules

1. **The work item is the unit of work.** Nothing is done except against a work item file.
   Requests, bugs, and ideas become work items first; work happens second.
2. **State is the filesystem.** A work item's folder is its state. A `status:` field in the
   file is a second fence, never the only one.
3. **Roles are instructions, not people.** The operator's session runs as the coordinator,
   which dispatches every task to a specialist subagent loaded with one role file. Roles
   are cheap to add and are the main extension point.
4. **Review is adversarial and isolated.** A reviewer subagent, in its own context window,
   tries to fail the work against the item's acceptance criteria and the team's standards.
5. **Humans hold three decisions: what enters the queue, what ships, and what the rules
   are.** Agents draft, build, review, and propose. They never promote a draft, mark an item
   done, or edit their own standards.

## Where things are

- `team/` — charter, vocabulary, decision log. What this team is and who it serves.
- `standards/` — process, quality, non-goals, writing conventions. What the reviewer checks.
- `context/` — durable facts about the subject area, loaded per work item.
- `work/` — work items moving through drafts, backlog, in-progress, and closed; design
  notes for claimed items in `work/designs/`.
- `improvement/` — signals collected from review and promotion, retro proposals, and
  measured dry runs of the workflow (`improvement/process-runs/`).
- `scripts/` — report-only helpers for `/process-run`: `process-run-report.py` (agent and
  size figures) and `context-check.py` (instruction-file drift).
- `.worktrees/` — one git worktree per claimed item, on its own branch (gitignored).
- `.claude/agents/` — the roles. `coordinator` runs in the main session; the rest are
  subagents it dispatches: {{subagent_role_list}}.
- `.claude/skills/` — the team skills (`/coordinate`, `/role`, `/team-new`, `/run-what`,
  `/team-next`, `/team-work`, `/team-review`, `/open-pr`, `/close-work`, `/team-promote`,
  `/team-retro`, `/process-run`).

## Branches

{{git_hosting}} The primary checkout always stays on `main`. Drafts, promotions, claims,
review-log lines, and closes are committed there, under the shared-clone rules in
`.claude/agents/coordinator.md` §7; everything else for an item happens on its own branch,
in its own worktree. See `standards/work-item-process.md` §Branches and merges.

## ID allocation

Next number = maximum `NNNN` found across `work/drafts/`, `work/backlog/`,
`work/in-progress/`, and `work/closed/`, plus one. Read from the live files at allocation
time, never from memory or a counter file. Re-check immediately before writing; on
collision, re-number.

## Human-only actions

- Promoting a draft to the backlog (`/team-promote`, or the operator's answer to the coordinator's question after drafting, or to `/team-next`'s one question).
- Ruling an item done. `/close-work` carries out the ruling (merge, then move to
  `work/closed/`); it never makes it.
- Approving or rejecting a proposal in `improvement/proposals/` and changing anything under
  `standards/` or `team/` (other than a decision-log append the operator dictates).
- Changing anything under `.claude/` (roles, skills, settings), except as the scoped
  deliverable of a work item the operator promoted.

## Output conventions

- Tag claims by confidence: `[Certain]` with evidence, `[Likely]` with the inference stated,
  `[Guessing]` with what would settle it.
- Follow the additional conventions in `standards/writing.md`.
- Every deliverable needs a verification step; unverifiable claims don't ship.
