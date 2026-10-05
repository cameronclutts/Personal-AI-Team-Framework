---
name: run-what
description: Report, in chat only, which work item can start now, what is in flight, what is queued, what is blocked and on what, and which drafts to promote. Use when the operator asks what to work on, what's next, or what can start. Read-only - it never claims, promotes, or commits; /team-next does that on top of this report.
---

# /run-what

A chat-only report of where every open work item stands. It writes no file and makes no
commit. `/team-next` runs this same procedure and then acts on it.

The rules here are the ones in `standards/work-item-process.md` §Dependencies and
§Queue order. If the two ever disagree, the standard wins. Report the disagreement.

## Inputs

Read only these, once each:

- The front matter of every file in `work/drafts/`, `work/backlog/` and
  `work/in-progress/`. Use `id`, `title`, `status`, `priority` and `depends_on`.
- For **drafts only**, the body as well. Any line that starts `Open question:` is an open
  question for the operator. Never read the body of a backlog or in-progress file.
- A listing of `work/closed/` and each closed file's `status:` line, to check whether a
  dependency is done.

Read nothing else. That means no designs, no standards beyond the rules below, no git
history, and no other repository.

Skip `.gitkeep`. A file whose `status:` disagrees with its folder (see
`standards/work-item-process.md` §Lifecycle) is left out of every block. List it after the
report as an inconsistency, one line each. Never fix it.

## Rules

1. **Dependency met.** A dependency is met only when that item is in `work/closed/` with
   `status: done`. Anything else is unfinished: a draft, a ready, claimed, returned or
   in-review item, a closed file with another status, or an id that matches no file. A
   missing `depends_on:` field means no dependencies.
2. **In flight.** An item is in flight when it is in `work/in-progress/` with status
   `claimed`, `returned`, or `in-review`.
3. **Startable.** An item is startable when it is `ready` in `work/backlog/` and every
   dependency is met. Items in flight do not stop it: several coordinator sessions may run
   at once, each holding one claim of its own.
4. **Order.** An item never comes before one it depends on. After that, lowest `priority`
   number first, then lowest id number: the `NNNN` part, compared numerically across all
   prefixes, so `ABC-0001` comes before `GEN-0003`. Ids share one counter, so a lower
   number is an older request. Every list in the report uses this order.

## Report

Print the six blocks in this order. Add no preamble, and nothing after them except the
inconsistency lines. Every id carries its title on the same line, as `GEN-0004, <title>`.
A block with no entries prints its heading and `none` on one line, as `Queued: none`.

```
Start Now:
GEN-AAAA, title

In flight:
GEN-BBBB, title (claimed)

Queued:
GEN-CCCC, title

Ready, blocked:
GEN-DDDD, title: waits on GEN-EEEE

Recommend promoting:
GEN-FFFF, title: reason

Not recommended:
GEN-GGGG, title: "Open question: ..."
```

- **Start Now:** the single top startable item (rules 3 and 4), with no reason clause. It
  shows even while other items are in flight, because another session's claim does not
  block this one.
- **In flight:** each in-flight item, with its status in parentheses.
- **Queued:** every `ready` item whose dependencies are all met and that is not in Start Now,
  in rule 4 order.
- **Ready, blocked:** every `ready` item with at least one unmet dependency, followed by
  `: waits on` and every unfinished id it depends on. Such an item is never in Start Now or
  Queued. It stays `ready` in the backlog. Nothing here demotes it.
- **Recommend promoting:** every draft with no `Open question:` line, in rule 4 order, with
  a reason of at most 12 words. A draft whose only blocker is another work item is still
  recommended. Its reason names what it waits on, for example `waits on GEN-0005; promote
  now, checked when pulled`. Unmet dependencies never stop a promotion.
- **Not recommended:** every draft with at least one `Open question:` line, quoting each such
  line in full.

## Never

- Write, move, or edit any file, or run `git add`, `commit` or `push`.
- Claim, promote, or change a `status:`, `priority:` or `depends_on:` value.
- Reorder or re-prioritise items beyond rule 4. Priority belongs to the operator.
- Ask the operator a question. `/run-what` only reports. `/team-next` asks the one question.
- Group items to run in parallel within one session. Each session claims one item; several
  sessions may each hold one.
