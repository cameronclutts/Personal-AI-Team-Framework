---
name: team-init
description: Bootstrap a new AI team from the scaffold. A guided walkthrough - welcomes the operator, asks plain-language questions about the work that pick the specialist roles, confirms a summary, then generates a working team repository at a target directory and suggests next steps, wired for the coordinator-led flow (routing table, branch and worktree per item, /open-pr and /close-work). Use when the operator wants to stand up a new team for any purpose. Also supports --add-role <name> to add a role to an already-generated team.
---

# /team-init

Walks the operator through building a team, then copies `scaffold/` into a target directory
and fills it in. Lives in the scaffold source repository, never in a generated team.

The operator may never have set up a team before. Hold their hand: say what each step is
for before asking it, offer a suggested answer wherever one can be worked out from what
they've already said, and never ask them to know scaffold vocabulary (roles, phases,
prefixes) before it has been explained in one plain sentence.

## Interview

### Rules for asking

- One question at a time. Use `AskUserQuestion` wherever the answer is a choice, with the
  suggested option first and marked `(Recommended)`. Free-text questions are asked in plain
  chat.
- Before each part, print its heading and one line saying why it matters.
- Never show the operator a placeholder name, a file path inside the scaffold, or a role
  file's front matter.
- If an answer is unclear, ask one follow-up, then move on with the clearest reading and
  say what you assumed. The summary in part 5 lets them fix it.

### Welcome

Print this, then start part 1:

```
Welcome to the Personal AI Team Framework.

We're going to build your own ready-made AI team: a git repository where
one Claude session (the coordinator) takes your requests, plans them, and hands the
design, building, testing, and review to specialist AI roles. You stay in charge of
what gets worked on, what ships, and what the rules are.

I'll ask about where the team lives, what it's for, and
what kind of work it will do, then pick the right specialists for you. You'll see the
whole team before anything is created.
```

### Part 1: Where the team lives

1. **Folder.** "Where should I create the team? Give a folder path. It must be empty or not
   exist yet." If it exists and isn't empty, say so and ask again.
2. **GitHub.** Explain: "Each piece of work gets its own git branch. With GitHub, you review
   each one as a pull request; without it, everything stays on this machine and you review
   with `git diff`. You can add GitHub later." Then ask with `AskUserQuestion`:
   `Yes, I have an empty repo` / `Yes, create a private one with gh` / `No, keep it local`.
   - First option: ask for the repository's URL.
   - Second: ask for the repository name, suggesting the folder's name.
   - Third: nothing more.

   For either GitHub option, run `gh auth status`. If it fails, say the pull-request flow
   needs the GitHub CLI logged in, and add an install-and-login step to part 6
   (`gh auth login`). The team still works local-only until then.

### Part 2: What the team is for

3. **Name.** Don't ask. Take it from the folder name (hyphens and underscores to spaces,
   title case: `recipe-box-team` → "Recipe Box Team"). The part 5 summary shows it, and the
   operator changes it there if they want.
4. **Purpose.** "In a sentence or two, what will this team help you do?" Offer an example:
   "Builds and maintains a small web app for my book club."
5. **Who it's for.** "Who uses what the team produces?" Suggest "Just me" first.
6. **Projects.** "Will the team work on things that already exist, such as a codebase,
   a server, or a set of documents? List each one with its path or URL, or say `starting
   fresh`." For each one, ask nothing more now; part 6 turns them into context.

### Part 3: What kind of work it does

Explain: "Your team always has a coordinator, an implementer who does the work, a
reviewer who tries to find what's wrong with it, and an analyst who answers questions.
I'll work out which specialists to add from what you've told me, and ask only about what I
can't tell."

First infer each answer from the purpose (answer 4) and projects (answer 6). It is `Yes`
when they plainly describe it (an app, site, or dashboard people look at → 7; an app, tool,
script, or anything that runs → 8), and `No` when they plainly rule it out (for example a
research or writing team → 7 to 10). Don't ask an inferred question. The part 5 summary
shows each inferred answer's roles marked "(from your purpose)", so the operator corrects
them there.

Ask only the questions you cannot infer, each with `AskUserQuestion`, options `Yes` / `No` /
`Not sure`. Each option's description names the roles it adds, in plain words. `Not sure`
adds the roles; say they only run on work that needs them, so an unused specialist costs
nothing.

| # | Question | Yes adds |
| --- | --- | --- |
| 7 | Will this team build or change something people look at, such as web pages, dashboards, or app screens? | `ui-designer` (designs every screen and state before it's built) and `ui-tester` (uses it in a real browser and takes screenshots as proof) |
| 8 | Will it write code, scripts, or configuration that can be run? | `technical-designer` (writes the build spec) and `backend-tester` (runs the work and tries to break it) |
| 9 | Will it set up or change a database, a server process that runs on its own, or containers? (A data file inside the project doesn't count.) | `architect` (decides how the pieces fit together, with trade-offs) and `technical-designer` |
| 10 | Will it touch networking, such as DNS, firewalls, VPNs, reverse proxies, or exposing anything to the internet? | `network-expert` (designs network changes with rollback steps) |

If all four are `No`, say: "That's a writing or research team. Documents go straight from
the implementer to the reviewer, with no design or test phase."

11. **Anything else?** "Is there a kind of expertise the team needs that isn't covered,
    for example a security reviewer or a data analyst?" If yes, for each one ask in plain
    words: what it should do (its stance), whether it works before the building (design)
    or checks the work after (test), and when it should be called in (one sentence the
    coordinator can check against a work item).

### Part 4: How the team organizes its work

12. **Work areas.** Explain: "Every piece of work gets an id like `WEB-0001`. The letters
    say which area it belongs to." Suggest two to five areas worked out from the purpose,
    the projects, and part 3, as `PREFIX: meaning` lines with three- or four-letter
    prefixes. Ask with `AskUserQuestion`: `Use these (Recommended)` / `Let me edit them`.
    `GEN` (anything that doesn't fit) is always added; don't list it.
13. **Ground rules.** Explain: "Every team already refuses to touch real machines without
    your OK, commit secrets, or weaken tests to make work pass." Then ask, in one
    message, for three optional lists and say "skip" is fine for any:
    - things this team must never do;
    - quality rules its work must meet;
    - tone or format rules for what it writes.

Do not ask for the operator's name. Derive it from `git config user.name` (fall back to the
literal string "the operator" if unset).

### Part 5: Confirm

Print a summary before creating anything:

```
Here's your team, <name>:

  Lives in:   <folder>   (<GitHub: url | GitHub: will create <name> | Local only>)
  Purpose:    <purpose>
  For:        <who>
  Projects:   <list, or "starting fresh">

  Roles
    coordinator           your session; plans, routes, and asks you
    implementer           does the work
    adversarial-reviewer  checks designs before building and tries to fail the result
    analyst               answers questions, read-only
    <each added role>     <one plain line>   (added because: <the answer that added it>, or "from your purpose")

  Work areas:  <PREFIX: meaning, ...>, GEN
  Rules:       <count of extra rules, or "defaults only">
```

Derive the deliverable types for the charter from part 3 rather than asking: "Code" if 7,
8, or 9 is yes; then "Documents and decisions" always. Show them on a `Produces:` line.

Ask with `AskUserQuestion`: `Build it (Recommended)` / `Change something`. On a change, ask
what, update the answer, and show the summary again.

### Part 6: Next steps

After generation (step 10 below), print a short, numbered "What to do next" list, built from
the answers, in this order. Each step has the exact thing to type or paste.

1. **Open your team.** "Open `<folder>` in Claude Code and run `/coordinate`."
2. **Give your team context.** Explain: "Your team only knows what's written in its
   `context/` folder. The first thing to do is have it learn your projects." For each
   project from answer 6, give a request to paste to the coordinator:
   `Draft a work item to document <project> at <path or URL>: what it is, how it's built,
   how to run it, and what's unfinished, as context files.` If the operator is starting
   fresh, suggest instead: `Draft a work item to write context/<area>.md for each work area:
   what we're building, decisions so far, and what to watch out for.`
3. **Run your first item.** "Tell the coordinator what you want, in plain words. It drafts a
   work item and asks once whether to start it; say yes. It then runs the work and asks you
   only what it can't decide: a route with design work, questions from the specialists, and
   whether the result is done."
4. **Ship it.** With GitHub: "When the item is `in-review`, run `/open-pr`, read the pull
   request, and tell the coordinator "it's done" to merge it with `/close-work`." Local:
   "When the item is `in-review`, read `git diff main...<branch>`, then tell the coordinator
   "it's done"."
5. **Keep going.** "Run several coordinators at once if you like, one item each. Use
   `/run-what` any time to see the queue without changing anything, `/team-retro`
   after a few items to see what the team should change about itself, and `/process-run`
   after changing how it works, to measure whether the change helped."

If `ui-tester` was added, add a step: "The UI tester drives a real browser through
Playwright. Run once on this machine: `npm install -g playwright && npx playwright install
chromium`." Check first with `npx --no-install playwright --version`; if it already prints a
version, leave the step out. If a GitHub step failed in step 9, add a step saying how to add
`origin` later. If any
role came from a `Not sure`, end with one line: "I added <roles> because you weren't sure.
They only run when an item needs them."

## Generation procedure

1. **Target.** Create the target directory if missing; refuse if it exists and is not empty.
2. **Copy** `scaffold/` to the target, preserving structure, dotfiles (`.gitignore`), and
   empty directories (their `.gitkeep` files). `context/_template.md` and
   `work/templates/work-item.md` keep their placeholder-style text on purpose; fill nothing
   in them.
3. **Roles.** For each role added in part 3 (answers 7 to 11), once each: if
   `roles/<name>.md` exists, copy it to `.claude/agents/<name>.md` unchanged. Otherwise
   (answer 11) write one in the same shape as the library roles: front matter (`name`,
   `description`, `model:` — `opus` for a design role, `sonnet` for a test role — and
   `tools: Read, Grep, Glob, Bash, Write, Edit`, never `Agent`), a stance paragraph,
   `## Phase` (the phase, an order of 50 for design or 30 for test, and `Runs when:` from
   the operator's answer), `## May read`, `## May write` (designs go to
   `work/designs/<id>-<kind>.md`; testers append a subsection to section 7), `## Never`,
   `## Hand back instead of acting`, and `## Skills used`, copying the hand-back wording
   from `roles/architect.md` word for word. Copy the matching habits word for word too: for
   a design role, the 150-line `## Never` bullet and the wrong-criterion hand-back from
   `roles/architect.md`; for a test role, the `Tested at commit:` bullet under
   `## May write` and the `## Gaps are failures` section from `roles/backend-tester.md`.
4. **Phase table.** Build `{{phase_table_rows}}` in `.claude/agents/coordinator.md`, one
   row per phase, numbered from 1, in this order:
   1. Each design role in `.claude/agents/`, by its `## Phase` order: `Design: \`<name>\``,
      and its `Runs when:` text.
   2. If there is at least one design role: `Design check: \`adversarial-reviewer\` over
      \`work/designs/<id>-*.md\` (§4)` | `Condition S holds and a design phase ran.`
   3. `Build: \`implementer\`, running \`/team-work\`` | `Always.`
   4. Each test role, by its order: `Test: \`<name>\``, and its `Runs when:` text.
   5. `Review: \`/team-review\`, which spawns \`adversarial-reviewer\` in isolation` |
      `Always.`
5. **Placeholders.** Fill every other placeholder in the copied tree:
   - `{{team_name}}` → answer 3, in `CLAUDE.md` and `README.md`.
   - `{{team_purpose}}` → answer 4, in `CLAUDE.md`, `README.md`, `team/charter.md`.
   - `{{team_customers}}` → answer 5, in `team/charter.md`.
   - `{{projects_list}}` → answer 6 as a bullet list, each with its path or URL and
     "No context written yet." (or "Starting fresh; nothing exists yet."), in
     `team/charter.md`.
   - `{{deliverable_types}}` → the `Produces:` line from part 5, in `team/charter.md`.
   - `{{non_goals_list}}` → answer 13's never-do list as a bullet list (or "None stated."
     if empty), in
     `team/charter.md`.
   - `{{operator_name}}` → the derived operator name, in `team/charter.md` and
     `team/decisions.md`.
   - `{{EXAMPLE_PREFIX}}` → the first prefix from answer 12, in `team/vocabulary.md`.
   - `{{prefix_table_rows}}` → one table row per `PREFIX: meaning` line from answer 12, in
     `team/vocabulary.md`.
   - `{{creation_date}}` → today's date (`YYYY-MM-DD`), in `team/decisions.md` and
     `improvement/process-runs/fixture/GEN-9999-queue-counts-script.md`.
   - `{{quality_rules_list}}` → a bullet list, in `standards/quality.md`: first one line per
     library role chosen from the list below, then answer 13's quality rules. If both are
     empty, "None beyond the defaults above."
     - `backend-tester`: "Code, services, scripts, and config are verified by the
       `backend-tester` actually running them, with commands and output recorded in
       section 7, before review."
     - `ui-tester`: "Anything with a screen is verified by the `ui-tester` in a real
       browser, with screenshots recorded in section 7, before review."
     - `network-expert`: "Every network or machine-config change ships with written
       rollback steps and a way to verify it worked."
   - `{{team_non_goals_list}}` → answer 13's never-do list as a bullet list (or "None
     beyond the universal rules above." if empty), in `standards/non-goals.md`.
   - `{{writing_rules_list}}` → answer 13's tone rules as a bullet list (or "None beyond
     the certainty tags above." if empty), in `standards/writing.md`.
   - `{{subagent_role_list}}` → every file in `.claude/agents/` except `coordinator.md`, as
     backticked names separated by commas, with the read-only `analyst` last ("..., and the
     read-only `analyst`"), in `CLAUDE.md`.
   - `{{git_hosting}}` → in `CLAUDE.md`. With GitHub: "This repository is pushed to GitHub as
     `origin`. Drafts and claims are pushed to `origin/main` at once, each reviewed item gets
     a pull request (`/open-pr`), and `/close-work` merges it." Local: "This repository has
     no `origin` remote. Nothing is pushed and there are no pull requests: `/close-work`
     merges each item's branch locally. Adding an `origin` remote later switches the team
     to pull requests with no other change."
   - `{{review_step}}` → in `README.md`. With GitHub: "`/open-pr` opens its pull request.
     Read the diff and section 8." Local: "read its change with
     `git diff main...<id>-<slug>` and its section 8 review."
6. **Decisions.** Append one row to `team/decisions.md` per extra role ("Added role
   `<name>`: <its one-line stance>." | "Added at team creation: <the question it answered
   yes or not sure to, or 'requested by the operator'>."), and
   one for hosting ("Pushed to GitHub as `origin`; items reach `main` through pull requests."
   or "Local-only: no remote; items reach `main` through a local merge by `/close-work`.").
7. **Word budgets.** Seed `BUDGETS` in the target's `scripts/context-check.py` at each
   instruction file's current word count, so `/process-run` flags growth from here on. Run
   this from the target:

   ```
   python3 - <<'PY'
   import pathlib
   globs = ("CLAUDE.md", ".claude/agents/*.md", ".claude/skills/*/SKILL.md",
            "standards/*.md", "team/*.md")
   files = sorted({p for g in globs for p in pathlib.Path(".").glob(g) if p.is_file()})
   body = "".join(f'    "{p.as_posix()}": {len(p.read_text().split())},\n' for p in files)
   script = pathlib.Path("scripts/context-check.py")
   text = script.read_text()
   assert "BUDGETS = {\n}\n" in text
   script.write_text(text.replace("BUDGETS = {\n}\n", "BUDGETS = {\n" + body + "}\n", 1))
   PY
   python3 scripts/context-check.py
   ```

   The first section of the check's output must read `none`.
8. **Check.** No `{{` may remain anywhere in the target except inside
   `context/_template.md` and `work/templates/work-item.md`. If any other file still has
   one, fix it before continuing. Every skill directory in `scaffold/.claude/skills/` must
   also be in the target's `.claude/skills/`, including `run-what` and `process-run`, and
   both files in `scaffold/scripts/` must be in the target's
   `scripts/`; copy any that is missing.
9. **Git.** In the target, run `git init -b main` and make one initial commit of the whole
   tree. Then, per answer 2:
   - **Existing repo:** `git remote add origin <url>`, then `git push -u origin main`.
   - **Create with gh:** `gh repo create <name> --private --source . --remote origin
     --push`.
   - **If either fails:** report the error and never retry with force. Then switch the team
     to local-only, because its skills treat any `origin` as live: `git remote remove
     origin` (if it was added), replace the `{{git_hosting}}` and `{{review_step}}` text and
     the hosting decisions row with their Local wording, and amend the initial commit. Say
     the team works local-only, and how to add `origin` later.
   - **Local:** nothing more.
10. **Next steps.** Print the part 6 list.

## `--add-role <name>`

Adds a role to an already-generated team. Ask for the team's path, and refuse unless it
contains `.claude/agents/coordinator.md`. In that team's primary checkout, on `main`:

1. If `roles/<name>.md` exists in this repository, copy it to the team's
   `.claude/agents/<name>.md`. Otherwise ask for the stance, phase, and runs-when sentence,
   and write it as in Generation step 3.
2. Insert the role's row into the coordinator's §2 phase table at the place Generation step
   4 would put it, and renumber the rows. If it is the team's first design role, add the
   design-check row too.
3. Add the role to the subagent list in the team's `CLAUDE.md`, and, for `backend-tester`,
   `ui-tester`, or `network-expert`, its line in `standards/quality.md`.
4. Add the role file to `BUDGETS` in the team's `scripts/context-check.py`, at its word
   count, and raise the budgets of `CLAUDE.md`, `.claude/agents/coordinator.md` and
   `standards/quality.md` by the words this addition gave them.
5. Append a row to the team's `team/decisions.md` recording the addition.
6. Commit those files on the team's `main` under its shared-clone rules
   (`.claude/agents/coordinator.md` §7 in that team): a **Checked pull** first, then add the
   new role file, `git commit --only <paths> -m "Add role <name> [session <marker>]"`, the
   **Pre-push check**, and `git push origin main`, skipped in **Local mode**.

Never touches `scaffold/` or `roles/` in this repository.
