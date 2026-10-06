# Approved external repos

Repositories outside this one that the team builds in. An item's `target_repo` is either
`this-repo` or a Repo name in the table below. A repo not listed here is refused at claim time
by `/team-next`. Only the operator adds, removes, or changes a row.

Paths are relative to this repo's root. The row marked as an example is not a real repo and is
never listed; replace it with your own rows.

| Repo | Local path | Base branch | Remote | Push on merge | Notes |
| --- | --- | --- | --- | --- | --- |
| EXAMPLE-ONLY example-repo | `../example-repo` | `main` | `origin` | yes, `git push origin main` | Example row. Delete it and add one row per repo this team builds in. |
