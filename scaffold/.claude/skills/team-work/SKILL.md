---
name: team-work
description: Implementer procedure for a claimed work item - load it, load matching context, do the work, fill in evidence per criterion, and hand back for testing and review. Run by the implementer subagent the coordinator dispatches, once an item has been claimed via /team-next.
---

# /team-work

Does the work of the one claimed item the coordinator names in its dispatch.

## Procedure

1. Work only in the item worktree the dispatch names, `.worktrees/<id>-<slug>`, on the
   item branch `<id>-<slug>`. If the dispatch names no worktree, or `git branch
   --show-current` there is not `<id>-<slug>`, refuse. Never commit on `main`.
   If section 3 puts the deliverable in an external repo, it names that repo's local
   checkout path and base branch; if it does not, hand back a question. Build the
   deliverable there on a branch `<id>-<slug>` created from that base branch (a worktree
   in that repo if others share its checkout), never on the base branch itself. The item
   file and its evidence stay in this repo's item worktree.
2. Confirm the item named in the dispatch is claimed (`work/in-progress/`,
   `status: claimed` or `status: returned`). If none, refuse — never work from a raw
   request; that belongs to `/team-new` and `/team-next` first.
3. Load the claimed item in full, the context file(s) named in its `touches:` field, if
   they exist, per `context/README.md`, and every `work/designs/<id>-*.md` for the item.
4. If `status: returned`, read section 8's findings and any failed tester evidence in
   section 7 first, and address every one of them.
5. Do the work described in section 3 (scope), staying inside section 4 (non-goals) and
   `standards/non-goals.md`.
6. Fill section 7 (work log and write-back): what was done, and for each acceptance
   criterion in section 5, the specific evidence that it passed, matching the verification
   plan in section 6. A criterion with no evidence is not ready for review.
7. Propose any durable additions to the relevant context file inside section 7 — do not
   edit the context file directly, unless section 3 makes it the deliverable.
8. Commit the deliverable and the updated item together, in the item worktree on the item
   branch, then report back to the coordinator, which dispatches the testers and then runs `/team-review`.

## Refuses when

The dispatch names no item or no item worktree, the worktree is not on the item branch, or
the named item is not claimed.
