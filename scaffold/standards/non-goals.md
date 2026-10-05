# Non-goals

The standing list of things this team never does. Checked on every review.

## Universal (never remove these)

- Deleting or weakening verification (tests, checks, citations) to make work pass.
- Expanding scope beyond the work item without a new or amended item.
- Editing any file under `standards/` or `team/` except `team/decisions.md` appends
  recorded on operator instruction, or the close row `/close-work` writes on the
  operator's `done` ruling.
- Editing any file under `.claude/` (roles, skills, settings) except as the scoped
  deliverable of a work item the operator promoted.
- Running commands on, installing on, or changing the configuration of a live system (a
  real machine, a production service, a network device, anything outside the repository)
  without the operator's explicit approval for that specific action.
- Committing secrets (passwords, API keys, tokens, private keys) to the repository.
  Secrets live in gitignored `.env` files or a secrets manager; commit a `.env.example`
  instead.

## Team-specific

{{team_non_goals_list}}

Grows or shrinks only through an approved proposal in `improvement/proposals/`, applied by
the operator and recorded in `team/decisions.md`.
