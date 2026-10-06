# Work item process

This is the file the reviewer treats as law for process questions.

## Lifecycle

| Status | Folder | Entered by | Exit |
| --- | --- | --- | --- |
| draft | `work/drafts/` | `/team-new` or any agent | Operator promotes: `/team-promote`, or an answer to the coordinator's or `/team-next`'s question |
| ready | `work/backlog/` | A promotion (human) | `/team-next` claims |
| claimed | `work/in-progress/` | `/team-next` | Coordinator dispatches design, build, test, then review |
| returned | `work/in-progress/` | `/team-review`, on the reviewer's Return | Coordinator re-dispatches the implementer |
| in-review | `work/in-progress/` | `/team-review`, on the reviewer's Pass | `/open-pr` opens the pull request; the operator rules `done` and `/close-work` merges |
| done | `work/closed/` | `/close-work`, on the operator's ruling only | Terminal |
| withdrawn | `work/closed/` | The coordinator, on the operator's word only (`coordinator.md` §7, **Withdraw**) | Terminal; never counts as a met dependency |

Folder and status must agree at all times. Any skill that changes one changes the other in
the same commit.

## Dependencies

An item lists the work items it waits on in `depends_on:`. A dependency is met only when
that item is in `work/closed/` with `status: done`. Unmet dependencies never stop a draft
being promoted to `ready`: an item blocked only by other work items belongs in the backlog.
Dependencies are checked when the item is pulled, not when it is promoted.

## Queue order

`/team-next` is deterministic: lowest `priority` number first, then lowest id number — the
`NNNN` part, compared numerically across all prefixes, so `ABC-0001` comes before
`GEN-0003` (ids share one counter, so a lower number is an older request). It never
claims from `work/drafts/`, and it skips any file whose status is not exactly `ready`.
Both checks are explicit in the skill, not assumed from a glob.

A `ready` item with an unmet dependency is blocked: `/team-next` reports it with the
unfinished items it waits on, leaves it `ready` in the backlog, and takes the next unblocked
item. An item never comes before one it depends on.

When nothing is startable, `/team-next` recommends drafts to promote, in queue order with a
one-line reason each, and promotes and claims on a single operator confirmation in the same
prompt. It never promotes without that confirmation.

## ID allocation

Next number = maximum `NNNN` found across `work/drafts/`, `work/backlog/`,
`work/in-progress/`, and `work/closed/`, plus one. Read from the live files at allocation
time, never from memory or a counter file. Re-check immediately before writing; on
collision, re-number.

## Claims

A claim is the move to `work/in-progress/` plus `status: claimed`. One item claimed per
session. A claimed item untouched for more than 7 days is reported by `/team-next` as
stale; it is never auto-released — the operator decides what happens to it.

Several coordinator sessions may run at once, each holding its own claim. Another session's
claim never blocks this one.

## Target repo

Every work item names the one repo its deliverable belongs in, in the `target_repo:` front-matter
field: `this-repo` (this team's own repo), or a repo name listed in `team/external-repos.md`.
The template starts the field as the placeholder `REPO-NAME`. Section 3 lists the files the
item writes under "Files written", each path relative to that repo.

- `/team-next` refuses to claim an item whose `target_repo` is empty, is still `REPO-NAME`, is
  not `this-repo` and not a listed repo, or whose local path is not a git repository.
- Deliverable files are written only in `target_repo`. When it is external, the only files this
  repo gets on the item branch are the item file and its designs.
- The reviewer runs `git diff --name-only main...<id>-<slug>` in this repo, and in `target_repo`
  when it is external. A changed file that "Files written" does not name is a Return, and so is a
  deliverable file in this repo's diff when `target_repo` is external. So is a git-ignored path
  there (`git check-ignore -q --no-index`).

## Branches and merges

- **The claim is the lock, and it lives on `main`.** `/team-next` commits the claim on
  `main` in the primary checkout. Drafts (`/team-new`), promotions (`/team-promote`),
  review-log lines (`/team-review`), and closes (`/close-work`) are also committed on `main`,
  each under the shared-clone rules in `.claude/agents/coordinator.md` §7 (commit by path,
  session marker, checked pull, pre-push check). The primary checkout is always on `main`;
  no branch is ever checked out there.
- **Everything after the claim happens on the item branch.** Each claimed item gets its own
  branch, `<id>-<slug>`, in its own worktree, `.worktrees/<id>-<slug>` (gitignored). Designs,
  the deliverable, sections 7 and 8, and the `returned` and `in-review` status changes are
  committed there, so the operator reads the item's whole change as one diff.
- **The deliverable reaches `main` only on the operator's `done` ruling**, through
  `/close-work`.
- **With an `origin` remote** (`git remote get-url origin` succeeds), drafts and claims are
  pushed to `origin/main` at once, so every session sees them; a rejected push means
  another session got there first, and the skill pulls and re-checks. `/open-pr` opens a
  pull request for the reviewed branch, and `/close-work` merges it. An item whose
  deliverable lives in another repository gets a pull request there too, which a human
  merges and `/close-work` only confirms.
- **Without an `origin` remote**, nothing is pushed and there are no pull requests.
  Concurrent sessions share one clone through worktrees, so they see each other's commits
  on `main` directly. The operator reads the item's change with
  `git diff main...<id>-<slug>`, and `/close-work` merges the branch locally. Adding
  `origin` later switches the team to the pull-request flow with no other change.

## Acceptance criteria

Every work item has 3 to 8 acceptance criteria (hard cap 8), numbered, each independently
checkable: a reader who was not there can tell, without asking anyone, whether a single
criterion passed. Criteria that can only be judged together should be split or merged until
each stands alone.

## Optional module: unattended intake

Disabled by default. When enabled, a scheduled run scans a configured source, filters by a
configured rule, and runs `/team-new` for each unconverted request. Output goes only to
`work/drafts/` — the entry gate in `standards/work-item-process.md` §Lifecycle is unchanged.
A request counts as converted if its source is annotated as converted OR any work item's
`source:` field cites it; the work item is written before the annotation. Each run appends
a one-line summary (scanned, converted, skipped) to its commit message. No scheduler is
included in this scaffold; enabling this module means wiring one externally.
