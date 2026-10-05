---
name: role
description: Load a role (coordinator, or any specialist in .claude/agents/) for this session and state its limits. Use at the start of a session, or when switching what kind of work you're doing.
---

# /role

Loads one role file for the session.

## Procedure

1. Match the requested role name against `.claude/agents/*.md`.
2. If no match, refuse and list the available role names (the file names under
   `.claude/agents/`, minus the extension).
3. Otherwise, load that role file and adopt its stance for the rest of the session.
4. State in one line what the role may write and what it never does, so the operator can
   see the limits before proceeding.

## Refuses when

The named role has no matching file under `.claude/agents/`. List the roles that do exist.
