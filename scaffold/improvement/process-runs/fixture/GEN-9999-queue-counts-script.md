---
id: GEN-9999
title: Queue-counts script that prints work-queue totals as JSON
status: draft
priority: 3
touches: [improvement]
depends_on: []
source: Process-run fixture. Not a real item. Copied unchanged into a sandbox clone by /process-run.
created: {{creation_date}}
pull_request:
---

## 1. Summary

A small script prints how many work items sit in each queue folder, as JSON.

## 2. Problem or goal

Counting the files in `work/drafts/`, `work/backlog/`, `work/in-progress/` and `work/closed/`
by hand is slow. This item adds a script that prints them. It is a fixture: it exists to give
the process run a small code item that needs a build, a test where the team has a tester, and
a review, and nothing about it is meant to ship.

## 3. Scope

Create, inside the repository the item sits in:

- `tools/queue-counts/queue_counts.py`. It uses the Python standard library only (`json`,
  `pathlib`, `sys`). Run from the repository root, it prints one JSON object to standard output
  and exits 0. It takes one optional argument, the repository root to count in, defaulting to
  the current directory.
- `tools/queue-counts/test_queue_counts.py`, a stdlib `unittest` file that runs the script
  against a temporary directory tree and checks its output.
- `tools/queue-counts/README.md`, with the run command and one example output.

The script is a local command. It starts no service, opens no port, installs nothing, and
touches nothing outside the repository. It has no screen, page or dashboard view; the only
output is JSON.

## 4. Non-goals

- A service, a container, a scheduled job, or any install on a real machine.
- A web page or dashboard that reads the JSON.
- Counting anything except the four queue folders.

## 5. Acceptance criteria

1. `python3 tools/queue-counts/queue_counts.py`, run from the repository root, prints one JSON
   object whose keys are exactly `drafts`, `backlog`, `in-progress` and `closed`, and whose
   values are integers equal to the `*.md` file count directly inside each matching `work/`
   folder.
2. A missing queue folder counts as `0`; the script does not fail.
3. Given an argument that is not an existing directory, the script exits non-zero with a
   one-line message on standard error, and prints nothing on standard output.
4. `python3 -m unittest discover -s tools/queue-counts` passes.

## 6. Verification plan

- Criteria 1 to 3: run the script against the repository and against a temporary tree with a
  folder removed, and compare the counts with `ls` on each folder. The team's tester runs these
  where the route has one; otherwise the implementer records them in section 7.
- Criterion 4: run the unittest command and record the output.

## 7. Work log and write-back

## 8. Review record
