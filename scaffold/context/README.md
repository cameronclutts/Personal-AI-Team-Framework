# Context

Durable facts about the subject area, one file per area, loaded on demand rather than kept
in every agent's head.

## Rule

Before working an item, load the context file(s) matching the item's `touches:` field, if
they exist. While working an item, the implementer proposes additions to that context file in
the item's section 7 write-back — it does not edit the context file directly, unless the
item's section 3 makes that file its deliverable.

New area files start from `context/_template.md`.
