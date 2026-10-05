---
name: clear-stale-agents
description: Close stale agent characters in the local pixel-agents office. Use when the developer says the office shows too many agents, asks to close or clear unused agents, or invokes "/clear-stale-agents". Optional argument is the idle cutoff in minutes (default 30, minimum 10). Only talks to the running pixel-agents server. Never kills a Claude process.
---

# Clear stale pixel-agents characters

pixel-agents runs standalone on `127.0.0.1:3100` and removes a character when Claude Code's
`SessionEnd` hook fires. With hooks on, it runs no idle check of its own, and it restores
characters after a restart. So a missed `SessionEnd` leaves a character in the office
until someone closes it. This skill closes the idle ones, the same way the X button in the
office does.

Invoking the skill is the authorization. Do not ask before running it.

## Steps

1. **Cutoff.** If an argument was given, use it as the cutoff in minutes. Otherwise use 30.
   The script refuses anything below 10. A closed character stays gone while the server
   keeps running, but a server restart re-adopts every transcript modified in the last
   10 minutes, so a shorter cutoff would be undone by a restart.

2. **Run**, in one Bash call, from anywhere inside this repo:

   ```bash
   node "$(git rev-parse --show-toplevel)/.claude/skills/clear-stale-agents/clear-stale-agents.mjs" <minutes>
   ```

   Add `--port <n>` only if the server was started on a port other than 3100. Add
   `--dry-run` to list what would close without closing it.

   Needs Node 22 or later (the built-in WebSocket client).

   - Exit 2: pixel-agents is not running, so nothing was closed. Say so and stop. A team
     that does not run pixel-agents always gets this; it is not a failure, and a run skill
     that called this script goes on.
   - Exit 64: bad argument. Say why and stop.
   - Exit 1: report the error line.

3. **Report** in three lines or fewer. Give the before count, the closed count, the after
   count, and the live Claude process count, all printed by the script. If the after count
   is well above the process count, explain that those agents wrote to their transcripts
   inside the cutoff. They will close on a later run, or when their session ends.

## What a close does

- It sends `closeAgent` over the server's WebSocket, the same message as the office's X
  button. The character leaves every open browser tab.
- The Claude session itself is untouched. A closed character does not come back while
  the server keeps running: the server keeps the transcript on its known-files list, and
  only a new chat (a new session) or a server restart gives a character again. After a
  restart, a session modified in the last 10 minutes is re-adopted.
- Idle time is the later of two values: the server's last transcript read (`lastDataAt`)
  and the transcript file's modified time. A `lastDataAt` of 0 means the server has read
  no new line since it adopted or restored the agent. It does not mean the agent was idle
  forever, so the file time decides.
- If the transcript file is missing, the agent is closed. If an agent has no transcript
  path (a hooks-only provider), it is kept.

## Never

- Kill or signal any process. A session idle for 30 minutes may still be open in an editor
  tab.
- Edit, delete, or rewrite anything under `~/.pixel-agents/` or `~/.claude/`. The running
  server owns its state files and would overwrite a change, and open browser tabs would not
  see it. Always go through the server.
