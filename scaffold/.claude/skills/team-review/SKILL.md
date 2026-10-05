---
name: team-review
description: Spawn the reviewer in an isolated subagent to check a claimed item's work against its acceptance criteria and the team's standards. Run by the coordinator after the implementer and testers finish, once section 7 is filled in.
---

# /team-review

Spawns the reviewer subagent, isolated from the coordinator's and implementer's context, and applies its verdict.

## Procedure

**Local mode.** If `git remote get-url origin` fails, follow `.claude/agents/coordinator.md` §7
**Local mode**: skip every `git push` (it counts as accepted), and read local `main` wherever
this skill says `origin/main`.

1. Work in the item worktree, `.worktrees/<id>-<slug>`, on the item branch `<id>-<slug>`.
   Read and write the item file there, never the copy on `main`, which holds only the
   claim.
2. Confirm the claimed item's section 7 is non-empty. If it is empty, refuse — there is
   nothing to review yet.
3. Spawn a subagent loaded with the `adversarial-reviewer` role
   (`.claude/agents/adversarial-reviewer.md`) and
   nothing else from this session's context. Give it only the item's file path in the
   item worktree.
4. The reviewer follows its review order: criteria and verification plan first, then
   section 7 evidence, then `standards/non-goals.md` and `standards/quality.md`, then it
   writes a new numbered pass in section 8 with a verdict. It does not set `status:`.
5. This step is the only place that sets the item's `status:` to `returned` or `in-review`. Apply the verdict
   from the latest section 8 pass:
   - Any criterion failed, or a standard was violated → `status: returned`. The item stays
     in `work/in-progress/`.
   - Every criterion passed and no standard was violated → `status: in-review`. The item
     stays in `work/in-progress/`; only the operator can move it to `work/closed/`.
6. Commit the reviewed item file alone, in the item worktree on the item branch. The review
   log never goes on the item branch.
7. Append the review-log line on `main`, in the primary checkout, as a **Shared-log write**
   (`.claude/agents/coordinator.md` §7): Checked pull; check
   `improvement/signals/review-log.md` has no uncommitted change; then, in one command,
   append one line (date, item id, verdict, criteria that failed, if any, finding
   category),
   `git commit --only improvement/signals/review-log.md -m "Review log: <id> <verdict> [session <marker>]"`,
   a check that the commit adds only this line, the **Pre-push check**, and
   `git push origin main`, each run only if the one before succeeded (§7, Shared-log write
   rule 3).
   - **Push rejected:** Checked pull, then push again. If the Checked pull reports
     `own commit conflicted, aborted` (two sessions appended at once), it has already run
     the abort and its checks: run the **Guarded drop**, then redo this step from the
     start. Never run `git rebase --abort` separately. Count every push.
     After the third rejected push, run the **Guarded drop**, so the line's commit does
     not stay unpushed on the shared `main`, then stop and hand the line back to the
     operator: `Review log line for <id> not written: push rejected three times.` If the
     Guarded drop itself stops, say that the commit is still on local `main` and
     unpushed.
   - Any stop in §7 leaves the item's verdict on the branch and the line unwritten; hand
     the line back to the operator with the stop.

   On a pass, the next step is `/open-pr <id>`, or, in **Local mode**, the operator's `done`
   ruling and `/close-work <id>`.

## Refuses when

The claimed item's section 7 is empty.
