---
name: team-promote
description: Operator-invoked - move one or more named drafts to the backlog and mark them ready. Use only when the operator names the specific drafts to promote (directly, or by confirming them in /team-next); never on agent judgment.
---

# /team-promote

Moves one or more drafts into the backlog. This is an entry-gate action. Only the operator
invokes it, and only for items they name explicitly. `/team-next` reuses this procedure when
the operator confirms a promotion in its one question. That confirmation counts as naming
the drafts.

## Procedure

**Local mode.** If `git remote get-url origin` fails, follow `.claude/agents/coordinator.md` §7
**Local mode**: skip every `git push` (it counts as accepted), and read local `main` wherever
this skill says `origin/main`.

1. Confirm the operator named one or more specific drafts, by id or file. If none are
   named, refuse. Promote only the drafts named, never a draft the operator did not name.
2. Check each named id. It must be a file in `work/drafts/` with `status: draft` and no
   `Open question:` line. Drop any id that fails, say which ids were dropped and why, and promote the rest. Ask no
   further question. This matters when `/team-next` reuses this procedure, because its
   one confirmation already covers the promotion.
   Unmet `depends_on:` entries never block a promotion. They are checked when the item is
   pulled (`standards/work-item-process.md` §Dependencies).
3. For each draft, before moving it, snapshot a diff of the draft as it stands against the
   version that will be promoted. The operator may have edited it first. Prepare one entry
   per item for `improvement/signals/promotion-diffs.md` (step 6 appends it), headed `## <date> <id>`, with the
   diff, or a note that there were no operator edits. Every operator edit here is an
   implicit correction to how drafts get written.
4. Before any move or edit, in the primary checkout on `main`: run a **Checked pull**,
   then check `improvement/signals/promotion-diffs.md` has no uncommitted change
   (`.claude/agents/coordinator.md` §7, **Shared-log write** rules 1 and 2). A stop here
   changes nothing.
5. Move each file from `work/drafts/` to `work/backlog/` and set `status: ready`.
6. Commit all the moves and promotion-diffs entries together on `main`, in the primary
   checkout, never on an item branch, finishing the **Shared-log write** that step 4
   began: check the log again; then, in one command, append
   the entries, `git commit --only <paths> -m "Promote <ids> [session <marker>]"`
   (first and last path of each move, and the promotion-diffs file, per **Commit by
   path**), a check that the commit adds only these entries, the **Pre-push check**, and
   `git push origin main`, each run only if the one before succeeded. When
   `/team-next` is promoting and claiming in one step, its claim goes in the same commit,
   and `/team-next` step 4 handles the push and its count (see
   `.claude/skills/team-next/SKILL.md`). A rejected push runs a Checked pull and pushes
   again. If the Checked pull reports `own commit conflicted, aborted`, it has already run
   the abort and its checks: run the **Guarded drop** and redo from step 4. Never run
   `git rebase --abort` separately. Count every push. After the third rejected push, run
   the **Guarded drop** and stop: `Not promoted: <ids>, push rejected three times. Run /team-promote again.` Any §7
   stop is a stop here.

## Refuses when

Invoked without the operator naming any item. An id that is not a draft is dropped in step 2,
which does not stop the other ids from being promoted.
