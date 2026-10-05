---
name: team-next
description: Print the /run-what report, then claim - with no id, claim the Start Now item; with an id (/team-next <id>), claim that item if its dependencies are met. Asks one question only when a draft must be promoted first. Use when starting a work session, or when the operator asks what's next or names an item to start.
---

# /team-next

Shows where the queue stands, then claims one item and routes it. Run bare, it claims the
Start Now item. Run as `/team-next <id>`, it claims the named item if every dependency is
met. Running `/team-next` is the operator's confirmation for the claim, so a claim needs no
question. It asks one question only when a draft must be promoted first, because promotion
is a human decision. It follows `standards/work-item-process.md` §Dependencies, §Queue
order and §Claims.

## Procedure

**Local mode.** If `git remote get-url origin` fails, follow `.claude/agents/coordinator.md` §7
**Local mode**: skip every `git push` (it counts as accepted), and read local `main` wherever
this skill says `origin/main`.

1. **Report.** Run the `/run-what` procedure (`.claude/skills/run-what/SKILL.md`) exactly as
   written: same inputs, same rules, same six blocks. Print its report.
   - A file in `work/backlog/` whose status is not exactly `ready` is never claimed. It is
     one of the inconsistencies `/run-what` lists.
   - Never claim from `work/drafts/`. A draft is claimed only after it is promoted in step 4.
2. **Stale check.** For each in-flight item, read the date of the last commit on its item
   branch that touched its file:
   `git log -1 --format=%cI <id>-<slug> -- work/in-progress/<id>-<slug>.md`. Use
   `origin/<id>-<slug>` if the branch is not local. Never read `main` for this: on `main`
   the file is touched only by the claim. If it is more than 7 days old, print
   `Stale: <id>, <title> (last commit <date>)` after the report. Never move, release, or
   change a stale item. The operator decides what happens to it.
3. **Decide.** Pick exactly one action, using 3.1 and then 3.2 (no id) or 3.3 (an id).
   Make at most one `AskUserQuestion` call in this run, with the recommended option first,
   and only where a rule below says to ask. A claim alone is never asked about.
   In-flight items held by other sessions never block a claim. An in-flight item blocks a
   claim only when the item being claimed depends on it, through `/run-what` rule 1.
   1. **This session already holds a claim:** ask nothing, claim and promote nothing. Say
      that this session's claimed item comes first, then stop. This applies with or
      without an id. This session holds a claim when it claimed an item earlier in the
      session, or is working an item in its worktree, and that item is still in flight.
      Items other sessions have in flight never count here. A restarted session holds no
      claim from memory: if it resumes an item, the operator names the item and its
      worktree, and that is its claim.
   2. **No id (`/team-next`).**
      - **An item is in Start Now:** claim it, without asking. Go to step 4 with that id.
      - **Nothing is startable, but drafts are recommended:** work out the top item that
        would be startable if every recommended draft were `ready`, using `/run-what`
        rules 1, 3 and 4. Promotion closes nothing, so it is a recommended draft whose
        dependencies are all already met.
        - If there is one, ask once. The options are `Promote <ids> and claim <top id>`
          (recommended), then `Promote <ids> only`.
        - If there is none, every recommended draft waits on unfinished work. Ask once;
          the only option is `Promote <ids> only`.
        - `<ids>` is every draft under Recommend promoting. If the operator answers by
          naming a subset, promote only the drafts named.
      - **Nothing is startable and no draft is recommended:** ask nothing, claim nothing.
        Say plainly that nothing can start and why: everything is blocked, every draft has
        an open question, or the queue is empty.
   3. **An id (`/team-next <id>`).** Find the named id among the files `/run-what` read,
      plus the listing of `work/closed/`. Match it against each file's `id:` front-matter
      field, not the filename. Then apply the first of these rules that fits. Other items
      in flight, or ranked above it, matter only when the named id depends on them.
      - **3.3a Inconsistent or not found.** The id is on `/run-what`'s inconsistency list,
        or matches no file: claim nothing. Say so: `<id> is listed as an inconsistency`
        or `<id> matches no work item`.
      - **3.3b Ready, dependencies met.** The id is `ready` in `work/backlog/` and every
        dependency is met (rule 1): claim it, without asking, even if it is not the
        Start Now item and other items are in flight. Go to step 4 with that id.
      - **3.3c Ready, a dependency unmet.** The id is `ready` in `work/backlog/` and at
        least one dependency is unfinished: claim nothing. List each unfinished
        dependency with its folder and status, for example
        `GEN-0008 (in-progress, claimed)`. An id that matches no file is listed as
        `GEN-NNNN (no file)`.
      - **3.3d Draft, no open question, dependencies met.** The id is in `work/drafts/`
        with no `Open question:` line and every dependency is met: ask once. The options
        are `Promote and claim <id>` (recommended), then `Don't promote`. Act per step 4.
        If the operator already chose `Promote and start <id>` in the coordinator's
        question after drafting (`.claude/agents/coordinator.md` §5), that answer is this
        question's answer: ask nothing and act per step 4.
      - **3.3e Draft, no open question, a dependency unmet.** The id is in
        `work/drafts/` with no `Open question:` line and at least one dependency is
        unfinished: ask once. The options are `Promote <id> only`, then `Don't promote`.
        Never claim it in this run. Name each unfinished dependency as in 3.3c.
      - **3.3f Draft with an open question.** The id is in `work/drafts/` with at least
        one `Open question:` line: ask nothing, claim and promote nothing. Quote each
        `Open question:` line in full.
      - **3.3g In progress or closed.** The id is in `work/in-progress/` or
        `work/closed/`: claim nothing. Say where it is and its status, for example
        `GEN-0008 is in work/closed/ with status: done`.
4. **Act.** Do only what step 3 chose, and only for the ids it names: the claim from 3.2 or
   3.3b, or the operator's answer to the one question. On `Don't promote`, do nothing. Before
   4.1 makes any move, run the pull and re-check in "Before 4.1" below. When the action
   promotes, also check `improvement/signals/promotion-diffs.md` has no uncommitted change
   (§7, **Shared-log write** rule 2) at that point; a stop there changes nothing.
   1. Promote each named draft by the `/team-promote` procedure
      (`.claude/skills/team-promote/SKILL.md`), steps 1 to 5; its step 4 pull and log
      check are the ones just run. That includes one
      `improvement/signals/promotion-diffs.md` entry per draft.
   2. If the action includes a claim, claim one item. With no id (3.2), it is only ever
      the `<top id>` named in the chosen option, or the Start Now item when no question
      was asked, provided it is `ready` in `work/backlog/` with every dependency met. It
      is never another item, even one the promotions made startable. If the operator's
      answer names a subset of drafts that leaves that `<top id>` out, or `/team-promote`
      drops it, claim nothing, say `Not claimed: <top id> was not promoted`, and print the
      report again (step 5). With an id (3.3b or 3.3d), it is the named
      id, provided every dependency is still met. Move its file from `work/backlog/` to `work/in-progress/` and set `status: claimed`.
      A draft promoted in 4.1 follows the same two moves: `/team-promote` takes it from
      `work/drafts/` to `work/backlog/` as `ready`, then the claim takes it to
      `work/in-progress/` as `claimed`. Its promotion-diffs entry records the promotion
      (`status: draft` -> `status: ready`). If the item to claim is not `ready` with its
      dependencies met after 4.1, claim nothing and say so.
   3. Make one commit holding all the promotions, the promotion-diffs entries, and the
      claim. The claim follows the promotion in that same commit. Follow
      `.claude/agents/coordinator.md` §7, **Commit by path** (first and last path of each
      moved file), with the message `Claim <id> [session <marker>]` (or
      `Promote <ids> and claim <id> [session <marker>]`, or `Promote <ids> [session
      <marker>]` when nothing is claimed). The marker makes two sessions'
      claim commits differ even when made in the same second, so the second push is
      rejected. When the commit carries promotion-diffs entries, it is a **Shared-log
      write** (§7): its first log check ran before 4.1, so check the log again now, then
      append the entries, commit, run the rule 5 check
      and the **Pre-push check**, and push, in one command.

   **The claim is the lock, and it lives on `main`.** Do 4.1 to 4.3 in the primary
   checkout, which is always on `main`, in this order. If there is no `origin` remote,
   follow **Local mode** (top of this procedure): the claim commit on local `main` is the
   lock, the push and its verify are skipped, and 4.4 runs from the claim commit.
   - Before 4.1, run a **Checked pull** (§7), then re-check that the item is still `ready`
     in `work/backlog/`, or still a draft if it is being promoted. For a named id (3.3b,
     3.3d), also re-check that every dependency is still met; if one is not, claim
     nothing and list it as in 3.3c. A draft this run was
     promoting that another session has since promoted to `ready` is still available:
     claim it without promoting it. If the item is in neither place, another session took
     it: claim nothing, name the next startable item, if any,
     and stop. The operator runs `/team-next` again to claim it; this is not a second
     question.
   - After 4.3, push at once: the **Pre-push check** (§7), then `git push origin main`
     (inside the 4.3 command when it is a shared-log write). Whatever the push prints, including
     `Everything up-to-date`, then **verify**: `git fetch -q origin`, then
     `git log -1 --format=%s origin/main -- work/in-progress/<id>-<slug>.md`. The claim
     holds only if that subject carries this session's `[session <marker>]`. If it carries
     another marker, the claim was lost: go to **Drop the claim**.
   - **Push rejected:** run a **Checked pull** (§7). If it stops, stop here too.
     - **The Checked pull reports `own commit conflicted, aborted`:** it has already run
       the abort and its checks. **Drop the claim**, then go back to "Before 4.1" and redo
       the claim from the pull. Never run `git rebase --abort` separately.
     - **The Checked pull reports `clean`:** re-check the item on `origin/main`:
       - still `ready` in `work/backlog/`, or still in `work/drafts/` when this run is
         promoting it: the rejection was for unrelated commits. Push again, then verify.
       - in `work/in-progress/` and the last commit there carries another marker, or none:
         another session claimed it first. **Drop the claim**, say which item was lost,
         name the next startable item, if any, and stop, as above.
       - in `work/in-progress/` and the last commit there carries this session's marker: an
         earlier push landed. The claim holds; go to 4.4.
       - anywhere else (closed, or removed): **Drop the claim**, say so, and stop.
     - Count every push, including a redo after a conflict. After the third rejected
       push, **Drop the claim** and stop: `Not claimed: <id>, push rejected three times.
       Run /team-next again.`
   - **Drop the claim** is the **Guarded drop** in §7. If any of its checks fails, reset
     nothing, stop, and hand back to the operator.
   4. **Branch and worktree.** Once the claim is verified on `origin/main`, create the
      item branch and its worktree from the claim commit:
      `git worktree add .worktrees/<id>-<slug> -b <id>-<slug> <claim commit>`. `<id>-<slug>`
      is the item file's name without `.md`. Before running it, check what already exists,
      in this order, and act on the first case that matches:
      1. The branch exists and `git worktree list` shows it checked out at
         `.worktrees/<id>-<slug>`: use that worktree.
      2. The path `.worktrees/<id>-<slug>` exists but is not a registered worktree, with or
         without the branch: stop and hand back to the operator. Never delete it.
      3. The branch exists with no worktree and no path (a failed `add -b` still creates
         the branch): `git worktree add .worktrees/<id>-<slug> <id>-<slug>`, without
         `-b`.

      Print the worktree path. Everything after the claim happens there: designs, the
      deliverable, sections 7 and 8, the `returned` and `in-review` status changes, and
      `pull_request:`. The shared logs (`review-log.md`, `promotion-diffs.md`,
      `team/decisions.md`) never go on the item branch; they are committed on `main`. The
      primary checkout stays on `main`; never check out a branch there.
5. **Report again.** After acting, print the `/run-what` report once more, run against
   the files as they now stand, so the operator sees what moved. If nothing was claimed or
   promoted (the answer was `Don't promote`, or step 3 claimed nothing), print it unchanged.
6. **Route.** If an item was claimed, hand it to the coordinator's route approval
   (`.claude/agents/coordinator.md` §3). Dispatch nothing from this skill.

## Confirmation rule

Running `/team-next`, bare or with an id, is the operator's confirmation for one claim.
A claim made under 3.2 or 3.3b needs no question. `/team-next` promotes **only** on the
operator's answer to the one `AskUserQuestion` from step 3. A choice of
`Promote ... and claim ...`, `Promote and claim <id>`, `Promote ... only` or
`Promote <id> only` counts as the operator naming those drafts for `/team-promote`, and so
does `Promote and start <id>` from the coordinator's §5 question. Without
that answer, it promotes nothing, and claims nothing that would need a promotion first. It
never asks a second question.

## Never

- Promote without the operator's answer to the one question.
- Claim while this session already holds a claim. One item is claimed per session. Another
  session's claim never blocks this one, and an in-flight item blocks a claim only when the
  item being claimed depends on it. The push race check in step 4 stops two sessions
  taking the same item.
- Commit a claim anywhere but `main`, leave it unpushed, or commit without `--only`.
- Reset `main` past a commit that does not carry this session's marker.
- Push with `--force`, `--force-with-lease`, or `--no-verify`.
- Claim an item whose dependencies are not all met, a draft that has not been promoted,
  or, with no id, any item but the Start Now item (or, after promotion, the top startable
  item).
- Ask more than one question, or stop without printing the report again.
- Reorder, re-prioritise, or edit an item's content.

## Refuses when

Nothing can start and nothing can be recommended for promotion, or the named id is not
claimable under 3.3. Print the report, say why, and claim nothing.
