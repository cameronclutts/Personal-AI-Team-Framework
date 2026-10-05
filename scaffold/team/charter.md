# Charter

## Purpose

{{team_purpose}}

## Customers

{{team_customers}}

## Projects

Where the work this team does lives, and what it already knows about each place.

{{projects_list}}

## Deliverable types

{{deliverable_types}}

## Out of scope

{{non_goals_list}}

## Operators and their authority

{{operator_name}} is the operator of this team. The operator alone may:

- Promote a draft to the backlog (`/team-promote`, or the operator's answer to the coordinator's question after drafting, or to `/team-next`'s one question).
- Rule an item done. `/close-work` carries the ruling out: it merges the item's branch and
  moves the item to `work/closed/`. It never makes the ruling.
- Approve or reject a proposal under `improvement/proposals/` and change anything under
  `standards/` or `team/` (other than a decision-log append the operator dictates).
- Change anything under `.claude/` (roles, skills, settings), except as the scoped
  deliverable of a work item the operator promoted.

All other actions in this repository are agent-executable within the limits set by
`standards/` and the role files in `.claude/agents/`.
