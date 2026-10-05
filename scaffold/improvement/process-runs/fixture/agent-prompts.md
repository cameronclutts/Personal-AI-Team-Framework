# Gate agent prompts for the process run

Copied word for word at dispatch by `/process-run`, with `<SANDBOX>` replaced by the absolute
path of the sandbox clone, `<WORKTREE>` by the absolute path of the item worktree
(`<SANDBOX>/.worktrees/GEN-9999-queue-counts-script`), and `<ROLE>` by the role being
dispatched. No model is passed at invocation; each agent runs on its own file's `model:` line,
and the resolved model is read from the transcripts by `scripts/process-run-report.py agents`.

Which roles run is decided by the coordinator's routing (`.claude/agents/coordinator.md` §1 and
§2) inside the clone, exactly as for a real item. A team without a design or test role for this
fixture simply skips that prompt.

Every prompt opens with the same environment note:

```
IMPORTANT ENVIRONMENT NOTE: this session operates on a sandbox clone of this team's repository, not the usual path. Treat this directory as the primary checkout, and ignore any other path you were told about, except the item worktree named below, where you do all item work:

<SANDBOX>
```

The item is GEN-9999, the queue-counts script. Its file is
`work/in-progress/GEN-9999-queue-counts-script.md` inside the sandbox, and inside the item
worktree once the item is claimed. Role dispatch follows `.claude/agents/coordinator.md` §7.

## Any design role

```
GEN-9999, the queue-counts script.

<environment note>

The item worktree is <WORKTREE>, on branch GEN-9999-queue-counts-script. The item file is work/in-progress/GEN-9999-queue-counts-script.md inside it; earlier design files for this item, if any, are work/designs/GEN-9999-*.md there. Write your design as <ROLE> per your role file. Do not write code and do not change the item's status.
```

On a Return, the same prompt with this in place of the last two sentences: the design check
returned your design, its findings are in the reply below, revise it for them per your role file.

## adversarial-reviewer (design check)

```
GEN-9999, the queue-counts script.

<environment note>

The item worktree is <WORKTREE>, on branch GEN-9999-queue-counts-script. Check the design files work/designs/GEN-9999-*.md there against the item's sections 3 to 5 and the standards, per the design check in .claude/agents/coordinator.md §4. Return Pass or Return in your reply. Do not change the item's status.
```

## implementer

```
GEN-9999, the queue-counts script.

<environment note>

The item worktree is <WORKTREE>, on branch GEN-9999-queue-counts-script. The item file is work/in-progress/GEN-9999-queue-counts-script.md inside it. The item is claimed. Run /team-work for it. Run the script only inside this sandbox.
```

## Any test role

```
GEN-9999, the queue-counts script.

<environment note>

The item worktree is <WORKTREE>, on branch GEN-9999-queue-counts-script. The item file is work/in-progress/GEN-9999-queue-counts-script.md inside it, and the implementer has filled section 7. Test it as <ROLE> per your role file. Run everything only inside this sandbox.
```

## adversarial-reviewer (review)

Spawned by `/team-review`, which gives the reviewer only the item file path. Add nothing but the
environment note and that path.

```
<environment note>

The item file is <WORKTREE>/work/in-progress/GEN-9999-queue-counts-script.md.
```
