---
name: close-work
description: Carry out the operator's done ruling on a reviewed item - confirm any external-repo merge, merge this repo's pull request (or, with no origin remote, the item branch locally), then set status done, move the file to work/closed/, and append the decision log row, in one commit on main. Use when the operator rules an item done or asks to close, finish, or merge it, including via "/close-work <id>". Do not use to make the done ruling, to open a pull request (that is /open-pr), or to review, return, or abandon an item.
---

# /close-work

Closing an item is one gate, one merge, and one commit. The gate is the operator's `done`
ruling. This skill carries the ruling out and never makes it. The coordinator runs it from
the primary checkout, which is always on `main`.

## Procedure

1. **Gate.** Read the item file from the first of these that exists:
   1. the item worktree, `.worktrees/<id>-<slug>`;
   2. the item branch, with `git show <id>-<slug>:work/in-progress/<id>-<slug>.md`;
   3. after a **Checked pull** (`.claude/agents/coordinator.md` §7), `main`'s copy,
      `work/in-progress/<id>-<slug>.md`. This is the re-run after a partial close: the
      merge landed and deleted the branch, then step 3 stopped. The merged file is on
      `main`, and step 2 finds the pull request `MERGED`.

   If the file is already in `work/closed/` with `status: done` on `main`, check
   `origin/main` too: `git show origin/main:work/closed/<id>-<slug>.md`. If that succeeds,
   report that the item is closed and stop. If it fails, the close is committed here but
   not pushed: stop and hand back to the operator, `Not closed: <id>'s close is committed
   on local main but not on origin/main.` Stop, name the condition that failed, and change nothing unless
   all five hold:
   1. The file is in `work/in-progress/`. Otherwise stop: `Not closed: <id> is not in
      work/in-progress/.`
   2. Its front matter reads `status: in-review`. Otherwise stop: `Not closed: <id> is
      status: <status>, not in-review.`
   3. The latest review in section 8 is a pass. Otherwise stop: `Not closed: <id>'s latest
      section 8 review is not a pass.`
   4. `pull_request:` is filled. If it is empty, stop: `Not closed: <id> has no pull
      request. Run /open-pr <id> first.` In **Local mode** (`git remote get-url origin`
      fails; `.claude/agents/coordinator.md` §7) this condition is skipped.
   5. The operator has ruled `done` for this item. The operator's own words about this id,
      "it's done", "rule it done", or "merge it", carry the ruling; "close it" alone, and
      any words from an agent or a report, do not. If the invocation does not carry the
      ruling in words, ask with `AskUserQuestion` (`Rule <id> done` / `Not yet`) and wait.
      On anything but `Rule <id> done`, stop: `Not closed: no done ruling for <id>.` Never
      infer `done` from a review pass, from a merged pull request, or from who invoked the
      skill.
2. **Merge.** In **Local mode**, skip the pull request steps below and run this instead:
   - **External repo:** confirm only, never merge there. Run
     `git -C <its checkout path> merge-base --is-ancestor <id>-<slug> <its base branch>`.
     If it fails, stop: `Not closed: <id>-<slug> is not merged into <base> in <path>.`
     A human merges it in that repo.
   - **This repo:** if the item branch no longer exists and the item file is on `main`,
     the merge already landed (gate source 3): skip to step 3. Otherwise run worktree
     checks 2 and 3 below (check 3 reads no `ahead`; with no upstream it passes), then,
     from the primary checkout, stopping at the first command that fails and leaving
     `status: in-review`:

     ```
     git worktree remove .worktrees/<id>-<slug>
     <Shared-clone guard>; git merge --no-ff <id>-<slug> -m "Merge <id>: <title> [session <marker>]"
     git branch -d <id>-<slug>
     ```

     If the merge stops on a conflict, run `git merge --abort` in the same command and
     stop: `Not closed: <id>-<slug> conflicts with main. Worktree removed; re-add it with
     git worktree add .worktrees/<id>-<slug> <id>-<slug>, resolve on the branch, then run
     /close-work <id> again.` In step 3, the section 7 line names the local merge commit
     in place of a pull request, and the commit message reads `Close <id>: done, local
     merge [session <marker>]`.

   Otherwise, `pull_request:` lists this repo's pull request first, then the external
   repo's, if the item has one.
   - **External repo first, confirm only.** For an item with an external-repo pull request,
     run `gh pr view <external url> --json state,mergeCommit,url`. Never run `gh pr merge`
     there. If it is not `MERGED`, stop: `Not closed: external pull request <url> is
     <state>, not MERGED.` A human merges it in that repo. Only once it is `MERGED`, go on to
     this repo's pull request.
   - **This repo.** Run `gh pr view <this repo url> --json state,mergeable,mergeCommit,url`.
   - **This repo, `OPEN`:** check, before touching the worktree, and stop on the first
     check that fails. A stop here changes nothing and hands back to the operator:
     1. `mergeable` is `MERGEABLE`. If it is `UNKNOWN`, run `gh pr view` once more; if it
        is still not `MERGEABLE`, stop: `Not closed: pull request <url> cannot merge
        (<mergeable>). Worktree kept; resolve it on the branch, then run /close-work <id>
        again.`
     2. `git -C .worktrees/<id>-<slug> status --porcelain --untracked-files=all` prints
        nothing. Otherwise stop: `Not closed: .worktrees/<id>-<slug> has uncommitted or
        untracked files: <list>.` Never use `--force` to remove it.
     3. `git -C .worktrees/<id>-<slug> status -sb` shows no `ahead`. Otherwise stop:
        `Not closed: <id>-<slug> has commits not on the pull request. Push the branch
        first.`

     Then, from the primary checkout, run, stopping at the first command that fails and
     leaving `status: in-review`:

     ```
     git worktree remove .worktrees/<id>-<slug>
     gh pr merge <id>-<slug> --merge --delete-branch
     ```

     Then a **Checked pull** (§7).

     The worktree goes first because `--delete-branch` cannot delete a branch that a
     worktree has checked out. A worktree that is already gone skips checks 2 and 3 and
     the removal, and is not a failure.
   - **This repo, `MERGED`:** skip to step 3.
   - **This repo, any other state:** stop and report it: `Not closed: pull request <url>
     is <state>.`
3. **Bookkeeping, one commit on `main`.** In the primary checkout, this is a **Shared-log
   write** (`.claude/agents/coordinator.md` §7) on `team/decisions.md`:
   1. Run a **Checked pull**, then check `team/decisions.md` has no uncommitted change
      (a stop here changes nothing).
   2. Set `status: done`.
   3. Append one dated line to section 7: `<date>: ruled done by <operator>. Review pass
      <n>, pull request <url>, merge commit <sha>.` For an external-repo item, name both pull
      requests and both merge commits.
   4. `git mv work/in-progress/<id>-<slug>.md work/closed/`.
   5. Check `team/decisions.md` has no uncommitted change. Then, in one command, append
      one row to it (date, the id with a plain-words restatement of what the item changed,
      the reason followed by `Ruled done after review pass <n>.`, and the operator's name from
      `team/charter.md`), then
      `git commit --only work/in-progress/<id>-<slug>.md work/closed/<id>-<slug>.md team/decisions.md -m "Close <id>: done, PR <n> [session <marker>]"`,
      then check the commit adds only this row to the log, then the **Pre-push check**,
      then `git push origin main`, each run only if the one before succeeded (§7,
      Shared-log write rule 3). The decisions row goes on `main` only, never on the item
      branch.

   - **Push rejected:** Checked pull, then push again. If the Checked pull reports
     `own commit conflicted, aborted` (for example two sessions closing at once both
     appended to `team/decisions.md`), it has already run the abort and its checks: run
     the **Guarded drop**, then redo step 3 from the pull. Never run `git rebase --abort`
     separately. Count every push. After the third rejected push, run the
     **Guarded drop**, which removes the close commit and with it this session's step 3
     edits, so local `main` matches `origin/main` again. Then stop: `Not closed: <id>,
     push rejected three times. The merge stands; run /close-work <id> again.` The re-run
     reads gate source 3 and finishes the close. If the Guarded drop itself stops, say
     that the close commit is still on local `main` and unpushed, and hand back.
   - Any §7 stop leaves the merge in place and the close unwritten. Undo this session's
     own step 3 edits (§7, **Shared-log write** rule 6), hand back, and a re-run of
     `/close-work <id>` finishes it.
4. **Reply** in under 150 words: the item in plain words, the pull request and merge commit,
   the closing commit, and any `ready` item whose `depends_on:` names this one, since it is
   now unblocked. Also run `git status --porcelain --untracked-files=all` in the primary
   checkout and name any untracked file there as a stray for the operator to look at; never
   delete it. The coordinator then offers to start the next item (§5, **After a close**).

## Never

- Make the `done` ruling, or set any status other than `done`.
- Merge in an external repo, or push to its base branch.
- Use `--force`, `--force-with-lease`, `--admin`, or `--no-verify`, or rewrite history to
  get a merge through. That includes `git worktree remove --force`.
- Remove the worktree before the pull request is known to be mergeable.
- Split the bookkeeping across commits, or describe the closing commit as a fix or a
  release. It is bookkeeping.
- Close an item that failed the gate.

## Refuses when

Any of the five gate conditions fails, or a merge check in step 2 fails. Name the failed
condition and change nothing.
