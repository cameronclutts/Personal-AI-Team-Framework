# Personal AI Team Framework

A scaffold for building small AI teams in [Claude Code](https://claude.com/claude-code).
Run `/team-init` and it walks you through plain-language questions, picks
the right specialists for the work you describe, and gives you a git repository with a team
ready for its first piece of work. The team can be for software, documentation, research,
operations, or anything else you name.

The process comes from a team used day to day. You hold one session, the **coordinator**.
It turns what you ask for into work items and starts them when you say so. Then it sends
every piece of design, build, test, and review work to a specialist subagent, on the
item's own git branch. You decide three things: what enters the queue, what ships, and
what the rules are.

## What it looks like

An abridged session, based on a real test run that built a small recipe app. Lines starting
`>` are you; the rest is the coordinator. Items in `[brackets]` are answers to its questions.

```
> I want a tiny local API for recipes: list them, get one by id, add one. JSON file, stdlib only.
Drafted API-0001 (6 acceptance criteria). Promote and start it?   [Promote and start]
Claimed API-0001 on branch API-0001-recipe-api.
Route: technical-designer → design check → implementer → backend-tester → review. Run it? [yes]
Design check passed. Built. Backend test: 6/6 criteria pass.
Review returned it: a POST with a lone surrogate character gets no response (criterion 4).
Sent back to the implementer → re-test 6/6 → review passed.
Read `git diff main...API-0001-recipe-api` and section 8, then tell me if it's done.
> looks good, it's done
Closed API-0001. WEB-0002 (the recipe page) is now unblocked. Start it?   [Start WEB-0002]
```

## Before you start

- **Claude Code** with subagents, skills, and `AskUserQuestion`. Roles pin `model: opus`
  (design and review) and `model: sonnet` (build, test, analyst), so your plan needs both.
- **git** 2.5 or later (worktrees) and **python3** (the `/process-run` report scripts).
- Optional: **`gh`**, logged in, for the GitHub pull-request flow, and **Playwright** if the
  team has a UI tester.
- **Cost:** every work item runs several subagents (design, build, test, review, and any
  rework), and `/process-run` runs a whole item end to end. Expect heavy token and Opus
  usage compared with a single chat.

Status: a personal project, built and used on macOS; untested on Linux and Windows. Issues and
pull requests are welcome.

## Quick start

1. Clone this repository and open it in Claude Code.
2. Run `/team-init`. It walks you through six parts:
   - **Where the team lives:** a folder, and whether it goes to GitHub.
   - **What it's for:** name, purpose, who uses it, and any existing projects it will
     work on.
   - **What kind of work it does:** the specialists, worked out from your purpose where
     it's clear and asked as yes/no questions where it isn't. Building
     screens adds a UI designer and UI tester. Writing runnable code adds a technical
     designer and backend tester. A database, a server process, or containers add an
     architect. Touching the network adds a network expert.
   - **How work is organized:** suggested work areas (id prefixes) and optional ground
     rules.
   - **Confirm:** a summary of the whole team, with why each specialist was added, before
     anything is created.
   - **Next steps:** what to type first, starting with giving your team context about
     your projects.
3. Open the generated directory in Claude Code and run `/coordinate`.
4. Tell it what you want and say yes to starting it. Answer any questions that come back,
   and rule the item done at the end.

## The five rules

1. **The work item is the unit of work.** Nothing is done except against a work item file.
2. **State is the filesystem.** An item's folder is its state; its `status:` field is a
   second check, never the only one.
3. **Roles are instructions, not people.** Your session runs as the coordinator, which
   dispatches every task to a subagent loaded with one role file. Adding a role is cheap.
4. **Review is adversarial and isolated.** A reviewer subagent, in its own context window,
   tries to fail the work against the item's acceptance criteria and the team's standards.
5. **Humans hold three decisions:** what enters the queue, what ships, and what the rules
   are. Agents draft, build, review, and propose. They never promote, close, or edit their
   own standards.

## How a piece of work flows

```
 you: "I want X"
   │  coordinator drafts it (/team-new) and asks ONE question: "promote and start?"
   ▼
 work/drafts/ ── yes ──▶ work/backlog/ (ready) ──▶ claim on main, plus a branch
                                                  │  and worktree .worktrees/<id>-<slug>
   coordinator picks the phases; asks you to      │
   approve only design work or a live system      ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ design roles ─▶ design check ─▶ implementer ─▶ testers ─▶ review             │
 │ (if needed)     (reviewer)      (/team-work)   (if needed) (/team-review)    │
 │                                      ▲                         │             │
 │                                      └── returned (up to 3x) ─◀┤             │
 └────────────────────────────────────────────────────────────────┼─────────────┘
                                                                  │ pass
                                                                  ▼
                in-review: /open-pr (GitHub) or git diff main...<branch>
                                                                  │
                        you say "it's done": /close-work merges, closes
                                                                  ▼
                                                             work/closed/
```

### Step by step

1. **Ask, and it's drafted.** A clear request ("I want X", "fix Y") becomes a draft at
   once; "let's look at X" starts a conversation first. A draft has 3 to 8 acceptance
   criteria that anyone can check on their own, and a `depends_on:` list for items it waits
   on. Right after drafting, the coordinator asks one question: promote and start it,
   promote only, or leave it as a draft. You never have to type a command to get going.
2. **Pick up work.** `/team-next` prints the queue in six blocks (Start Now, In flight,
   Queued, Ready-blocked, Recommend promoting, Not recommended), then claims the Start Now
   item without asking: running it is your confirmation. `/team-next <id>` claims that item
   instead, once everything it depends on is done. It asks one question only when a draft
   has to be promoted first, and one answer covers the promotion and the claim. Order is
   priority, then id number. Another session's item blocks a claim only if the claimed item
   depends on it. When a request leaves a point only you can settle, the draft carries an
   `Open question:` line, and it is never recommended or promoted until you answer it.
3. **Claim on `main`, work on a branch.** The claim is a commit on `main`. That commit is
   the lock. Everything after it happens on the item's branch, in
   `.worktrees/<id>-<slug>`, so you can run several coordinator sessions at once, one
   claim each. Sessions can share one clone safely: every commit on `main` names its own
   paths, carries a session marker, and runs a guard that refuses to act while another
   session's rebase is in progress. With a GitHub remote, the claim is pushed at once and
   a lost race is caught and dropped without touching another session's work.
4. **Route.** The coordinator matches the item against its routing table and phase table:
   which design roles run, whether a design check runs, which testers run, and why each
   skipped phase was skipped. It asks you to approve a route that has design work or
   touches a live system; any other route it prints and starts. A returned item re-runs its
   route without asking again. A documentation-only item skips design and testing.
5. **Design check before build.** For anything that adds, removes, or changes a service,
   host, container, or the network, the adversarial reviewer checks the design files
   against the item before the implementer starts.
6. **Build, test, review.** The implementer records evidence for each criterion in
   section 7. Testers run the work and append what they observed. `/team-review` spawns the
   reviewer in isolation, with only the item's path. The reviewer treats the work log as
   a claim and re-checks every criterion itself; anything it can't verify is returned, and
   there is no pass-with-notes. Testers record the commit they tested and count an
   untested criterion as a failure. A fail sends the item back to the implementer. After
   three returns, you decide what happens next.
7. **Hand-backs come to you.** No subagent asks you anything directly, starts another
   agent, or guesses. Each one ends its report with `Hand-back: question` (the coordinator
   asks you with `AskUserQuestion`, then resumes the same agent with your answer) or
   `Hand-back: agent step` (the coordinator starts that role, asking you first if it's
   outside the approved route).
8. **Ship.** At `in-review`, `/open-pr` opens a pull request so you can read the whole
   change as one diff. When you rule it done, in words, `/close-work` merges the pull
   request. Then, in one commit on `main`, it sets `done`, moves the file to
   `work/closed/`, and logs your ruling. It never infers `done` from a passing review.

### With or without GitHub

`/team-init` asks whether the team's repository will be pushed to GitHub.

- **Yes:** it adds `origin` (or creates a private repo with `gh`) and pushes. Drafts and
  claims are pushed to `origin/main` at once, so every session sees them. `/open-pr` opens
  pull requests, and `/close-work` merges them. An item whose deliverable lives in another
  repository gets a pull request there too. You merge that one yourself, and
  `/close-work` only checks that it's merged.
- **No:** nothing is pushed. Items still get their own branch and worktree. You read an
  item's change with `git diff main...<id>-<slug>`, and `/close-work` merges the branch
  locally. If you add `origin` later, the team switches to pull requests with no other
  change.

## What a generated team contains

| Path | What it is | Who writes it |
| --- | --- | --- |
| `team/` | Charter, vocabulary (id prefixes), decision log | You (agents append dictated decisions) |
| `standards/` | Process, quality rules, non-goals, writing conventions. This is what review enforces | You only; agents propose |
| `context/` | Durable facts about the subject, loaded per item | Agents and you |
| `work/` | Items in `drafts/`, `backlog/`, `in-progress/`, `closed/`; design notes in `designs/` | Agents, within the gates |
| `improvement/` | Signals (review log, promotion diffs), retro proposals, and `/process-run` results in `process-runs/` | Agents; you approve |
| `scripts/` | Report-only helpers for `/process-run`: agent and size figures, instruction-file drift | You, or a work item you promoted |
| `.worktrees/` | One worktree per claimed item (gitignored) | `/team-next` creates, `/close-work` removes |
| `.claude/agents/` | Role files | You, or a work item you promoted |
| `.claude/skills/` | The team's slash commands | You, or a work item you promoted |

### Skills

| Skill | Does |
| --- | --- |
| `/coordinate` | Loads the coordinator for your session. Start every session with it. |
| `/role` | Loads any other role for the session and states its limits. |
| `/team-new` | Drafts an item from a request, or re-drafts one from your notes. |
| `/run-what` | Read-only queue report: what can start, what's in flight, what's blocked and on what, which drafts to promote. |
| `/team-next` | The same report, then claims the top item (or `/team-next <id>`, a named one) and creates its branch and worktree. Asks one question only when a draft must be promoted first. |
| `/team-promote` | You move named drafts into the backlog. Records how you changed each one, as a drafting-quality signal. |
| `/team-work` | The implementer's procedure: build in the item worktree and record evidence for each criterion. |
| `/team-review` | Runs the adversarial reviewer in isolation and applies its verdict. |
| `/open-pr` | Pushes a reviewed item's branch and opens its pull request. Never merges. |
| `/close-work` | Carries out your `done` ruling: merge, then close in one commit. Asks for the ruling if you haven't given it. |
| `/team-retro` | Reads the signals and writes proposed rule changes for you to accept or reject. |
| `/process-run` | Takes a throwaway item from draft to done in a sandbox clone, through every gate agent for real, and reports time, tokens, and instruction-file growth against the last run. Removes the sandbox afterwards. |

### Roles

Every team starts with four:

| Role | Job |
| --- | --- |
| `coordinator` | Your session. Talks, drafts, claims, routes, dispatches, relays questions. Never builds. |
| `implementer` | Builds one claimed item in its worktree, following its designs. |
| `adversarial-reviewer` | Checks designs before build, and tries to fail the finished work. Never fixes it. |
| `analyst` | Read-only. Answers questions with evidence. |

The [`roles/`](roles/) library has more you can add at `/team-init` or later with
`/team-init --add-role <name>`. Each one has a `## Phase` section saying when it runs. That
section becomes its row in the coordinator's phase table.

| Role | Phase | Runs when |
| --- | --- | --- |
| `architect` | design | A service, host, or container is added or removed, or its technology, hosting, or data storage changes. |
| `network-expert` | design / consult | The item touches DNS, DHCP, VLANs, firewall or port rules, proxies, TLS, VPN, or exposes a service. |
| `ui-designer` | design | A screen, page, or dashboard view is added or changed. |
| `technical-designer` | design (last) | Any other design phase runs, or the item changes a system. |
| `backend-tester` | test | Code, scripts, config, a service, or a container is created or changed. |
| `ui-tester` | test | A screen, page, or dashboard view is added or changed. |

A role is one Markdown file: stance, phase and trigger, may read, may write, never, hand
back instead of acting, and skills used. Each one pins a model (`opus` for design and review
work, `sonnet` for building, testing, and the analyst) and a tool allowlist. No specialist
gets the `Agent` tool, and the analyst gets no file-writing tool. You can write your own in
the same shape.

## Gates

- **Entry:** only you promote a draft. Your answer to the one question after drafting
  counts.
- **Route:** for a route with design work or a live system, the coordinator dispatches
  nothing until you approve it. Your answers to handed-back questions are written into the
  item, so later roles read them from the file.
- **Ship:** only you rule an item done. `/close-work` carries out your ruling and never
  makes it.
- **Rules:** only you change `standards/`, `team/`, or `.claude/`. Agents write proposals,
  and your ruling goes in `team/decisions.md`. Agents change `.claude/` only as the scoped
  deliverable of an item you promoted.
- **Live systems:** before any subagent runs a command on a real machine, a production
  service, or a network device, the coordinator asks your go-ahead for that specific
  action.

## Self-improvement

The team collects two signals without you carrying them: how you edit drafts before you
promote them, and what the reviewer keeps returning. `/team-retro` groups recurring entries
into proposals that name the target file, the exact change, and the entries that justify
it. Nothing changes until you approve it.

`/process-run` measures the process itself. It runs a fixture item through the real route in
a sandbox clone with no remote, logs each stage's time and tokens, grades the previous run's
findings against what actually landed, and lists instruction files that grew. Run it after
changing how the team works, to see whether the change helped. It never drafts work items
itself: it asks you which findings should become one.

## This repository

- [`scaffold/`](scaffold/) is the template `/team-init` copies and fills.
- [`roles/`](roles/) holds the optional specialist roles.
- [`.claude/skills/team-init/`](.claude/skills/team-init/) is the bootstrap skill.
- [`.claude/agents/flow-tester.md`](.claude/agents/flow-tester.md) is a maintainer role
  for testing the scaffold itself. It plans an end-to-end run in a throwaway team, then
  audits the result against the scaffold's rules. It's never copied into a team.

## License

MIT. See [`LICENSE`](LICENSE).
