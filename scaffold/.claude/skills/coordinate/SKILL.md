---
name: coordinate
description: Load the coordinator role for this session - shortcut for /role coordinator. Use at the start of a session.
---

# /coordinate

Shortcut for `/role coordinator`.

## Procedure

1. Load `.claude/agents/coordinator.md` and adopt its stance for the rest of the session.
2. For every job, follow these rules in `coordinator.md`:
   - **Route:** match the job to the §1 routing table. For a claimed item, pick its phases
     with the §2 phase-selection table. A job that matches no row goes back to the
     operator unrouted.
   - **Approve:** print the route; ask for approval with `AskUserQuestion` before the first
     dispatch only when §3 says to (a design phase, a live system, or a changed route).
     A role added outside the approved route needs approval first.
   - **Hand back:** relay every question a role hands back to the operator with
     `AskUserQuestion`, then `SendMessage` the answer to the same agent (§6). Never answer
     it yourself.
3. State in one line what the role may write and what it never does, so the operator can
   see the limits before proceeding.

To load any other role, use `/role {role}`.
