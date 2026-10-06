---
name: team-new
description: Draft a work item from a request into work/drafts/, or re-draft an existing draft from operator annotations. Use whenever a request, bug, idea, or finding needs to become a work item before any work happens on it.
---

# /team-new

Turns a request into a work item draft. Never does the work itself.

## Procedure

**Local mode.** If `git remote get-url origin` fails, follow `.claude/agents/coordinator.md` §7
**Local mode**: skip every `git push` (it counts as accepted), and read local `main` wherever
this skill says `origin/main`.

1. If re-drafting: read the existing draft and the operator's annotations on it. Otherwise,
   read the request.
2. If the request has no identifiable goal, ask one clarifying question and stop. Do not
   draft a guess. If it has a goal but leaves a point open that only the operator can
   settle, draft it anyway and add one line per point at the end of section 3,
   `Open question: <the question>`. `/run-what` and `/team-next` then hold the draft back
   until the line is answered and removed.
3. Pick an area prefix from `team/vocabulary.md` (use `GEN` if none fit; propose a new
   prefix to the operator rather than inventing one silently).
4. Work in the primary checkout, on `main`. Run a **Checked pull**
   (`.claude/agents/coordinator.md` §7) first, so drafts committed by other coordinator sessions count. Then allocate the next id per
   the rule in `standards/work-item-process.md` §ID allocation. Re-check for a collision
   immediately before writing. If there is no `origin` remote, follow **Local mode**
   (top of this procedure).
5. Copy `work/templates/work-item.md` to `work/drafts/<id>-<slug>.md`, filling the front
   matter (`id`, `title`, `status: draft`, `priority`, `touches`, `target_repo`, `source`, `created`) and
   sections 1 to 6. Leave sections 7 and 8 empty — they belong to the implementer and reviewer.
   Fill `target_repo` with `this-repo` or a repo name from `team/external-repos.md`, and list
   the paths the item will write in section 3 "Files written", relative to that repo. Tell the
   target from the request (the area prefix, a named repo, or the path of the thing to
   change). If it cannot be told, ask the operator one question naming the candidates, and
   stop without drafting until it is answered. Never leave `target_repo` as `REPO-NAME` or
   empty, and never guess it.
6. Write 3 to 8 acceptance criteria (hard cap 8), each independently checkable per
   `standards/work-item-process.md`.
7. Commit the draft by path and push it at once. A new file is unknown to git, so add it
   first: `git add work/drafts/<id>-<slug>.md`, then
   `git commit --only work/drafts/<id>-<slug>.md -m "Draft <id>: <title> [session <marker>]"`,
   then the **Pre-push check** and `git push origin main`. This follows §7, **Session
   marker**, **Commit by path** and **Pre-push check**; a failed `git add`, commit or
   check is a stop.
8. **Push rejected.** Note the draft commit's hash as `<own>`. Run a **Checked pull**
   (§7); if it stops, stop here too.
   - **The Checked pull reports `own commit conflicted, aborted`** (for example on
     `AA work/drafts/<id>-<slug>.md`, because another session drafted the same id and
     slug): it has already run the abort and its checks. **Drop the draft commit**, then
     **Re-draft under a new id**. Never run `git rebase --abort` separately.
   - **The Checked pull reports `clean`:** re-check the id against the live files. If no other
     file in `work/` holds the same id, push again. If one does, **Drop the draft commit**,
     then **Re-draft under a new id**.
   - **Drop the draft commit** is the **Guarded drop** in §7. If any of its checks fails,
     reset nothing, stop, and hand back to the operator.
   - **Re-draft under a new id.** Allocate the next id again from the live files, write
     `git show <own>:work/drafts/<id>-<slug>.md` to `work/drafts/<new id>-<slug>.md`, set
     its `id:` field to the new id, then add, commit, and push as in step 7.
   - Count every push. After the third rejected push, drop the draft commit as above, keep
     the draft text in the reply, and stop: `Not drafted: push rejected three times.`
   - A re-draft of an existing draft keeps its id. If its Checked pull reports
     `own commit conflicted, aborted`, drop the commit as above and hand back to the
     operator: another session edited the same draft.

   `main` ends with one draft per id. Never push with `--force`.

## Refuses when

The request has no identifiable goal, or the target repo cannot be told from the request.
Ask one question instead of drafting a guess.
