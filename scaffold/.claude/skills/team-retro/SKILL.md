---
name: team-retro
description: Read the improvement signals (review log, promotion diffs, explicit corrections) and write a dated proposal file for the operator to apply. Use periodically or when the operator asks what the team should change about itself.
---

# /team-retro

Turns accumulated signals into proposals. Never edits a standard directly.

## Procedure

1. Read `improvement/signals/review-log.md` and `improvement/signals/promotion-diffs.md`.
   Count entries added since the last file in `improvement/proposals/` (or all entries, if
   no proposal has been written yet).
2. If fewer than 3 signal entries have accumulated since the last retro, refuse and say how
   many there are.
3. Otherwise, group recurring findings and edits by theme (e.g. a criterion type that keeps
   getting returned, a habit the operator keeps correcting in promotion diffs).
4. Write `improvement/proposals/YYYY-MM-DD-retro.md`. For each proposal: the target file
   (a specific file under `standards/` or `team/`), the exact change, and the signal
   entries (dates, item ids) that justify it.
5. Commit the proposal file on `main` in the primary checkout, under the shared-clone rules
   in `.claude/agents/coordinator.md` §7: add it, `git commit --only <its path>` with the
   session marker, the **Pre-push check**, and `git push origin main` (skipped in **Local
   mode**). Do not apply it — the operator applies or rejects each
   proposal and records the ruling in `team/decisions.md`.

## Refuses when

Fewer than 3 signal entries have accumulated since the last retro. State the count.
