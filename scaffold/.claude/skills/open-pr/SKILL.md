---
name: open-pr
description: Push a reviewed item's branch and open its pull request against main, then record the URL in the item's pull_request field. Use when an item is in-review with a passing section 8 review and an empty pull_request field, or the operator asks to open the PR, including via "/open-pr <id>". Do not use to merge a pull request, to close an item, or to set done (that is /close-work).
---

# /open-pr

Opens the pull request for one reviewed item. It pushes and opens. It never merges and never
sets `done`; that stays with `/close-work` on the operator's ruling. The coordinator runs it
in the item's worktree, `.worktrees/<id>-<slug>`, on the item branch `<id>-<slug>`.

## Procedure

0. **Local mode.** If `git remote get-url origin` fails, stop and change nothing:
   `Not opened: this repo is local-only (no origin). Run /close-work <id>, which merges
   locally.` (`.claude/agents/coordinator.md` §7, **Local mode**.)
1. **Gate.** Read the item file in the item worktree. Stop, name the condition that failed,
   and change nothing unless all four hold:
   1. The file is in `work/in-progress/`. Otherwise stop: `Not opened: <id> is not in
      work/in-progress/.`
   2. Its front matter reads `status: in-review`. Otherwise stop: `Not opened: <id> is
      status: <status>, not in-review.`
   3. The latest review in section 8 is a pass (every criterion passed, as `/team-review`
      recorded it). Otherwise stop: `Not opened: <id>'s latest section 8 review is not a
      pass.`
   4. `pull_request:` is empty. If it is filled, run `gh pr view <url> --json
      state,url` for each URL, report each state, and stop: `Not opened: <id> already has
      pull request <url> (<state>).`
2. **Push and open.** This repo's item branch always gets a pull request, because it carries
   the item file and its evidence. From the item worktree:

   ```
   git push -u origin <id>-<slug>
   gh pr create --base main --head <id>-<slug> --title "<id>: <title>" --body "<id>"
   ```

   **External repo.** An item is external when its section 3 puts the deliverable in
   another repo. Section 3 then names that repo's local checkout path and its base branch;
   if it does not name both, stop: `Not opened: <id> names an external repo but not its
   checkout path and base branch.` The implementer built the deliverable there on its own
   `<id>-<slug>` branch (`/team-work` step 1). If that branch does not exist in the
   external checkout, stop: `Not opened: no <id>-<slug> branch in <path>.` Otherwise, in
   that checkout, also run:

   ```
   git push -u origin <id>-<slug>
   gh pr create --base <its base branch> --head <id>-<slug> --title "<id>: <title>" --body "<id>"
   ```

   so the item has two pull requests. Stop at the first command that fails and report its
   output. If
   `gh pr list --head <id>-<slug>` shows the operator already opened a pull request for a
   branch, record that one in step 3 instead of opening a second.
3. **Record it.** On the item branch, in the item worktree:
   - write every pull request URL into `pull_request:`, this repo's first, then the
     external repo's: `pull_request: [<this repo url>, <external repo url>]`. An item with
     only this repo's pull request holds one URL;
   - append one dated line to section 7: `<date>: pull request <n> opened, <url>.`, naming
     each pull request;
   - leave `status: in-review`.

   Commit the item file alone as `<id>: pull request <n> opened` (this repo's `<n>`), then
   `git push origin <id>-<slug>`.
4. **Reply** in under 100 words: the item in plain words, every pull request URL, and the
   next step, `/close-work <id>`, which asks for the operator's `done` ruling and merges.

## Never

- Run `gh pr merge`, or merge by any other means, in this repo or an external one.
- Push to `main` or to an external repo's base branch, or commit on `main`.
- Use `--force`, `--force-with-lease`, `--admin`, or `--no-verify`.
- Set `status: done`, or move the item file.
- Open a pull request for an item that failed the gate.

## Refuses when

Any of the four gate conditions fails. Name the failed condition and change nothing.
