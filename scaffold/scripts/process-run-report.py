#!/usr/bin/env python3
"""Report per-agent transcript figures and repository size growth for a process-run.
Writes nothing. See improvement/process-runs/README.md."""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
from typing import Mapping, NamedTuple, Optional, Sequence, TextIO

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

STABLE_SIZE_KEYS = (
    "team/decisions.md",
    "improvement/signals/review-log.md",
    "improvement/signals/promotion-diffs.md",
    "work/designs/",
    "instruction-file-words",
)


class AgentFigures(NamedTuple):
    agent_id: str
    agent_type: str
    description: str
    model_asked: str
    model_ran: str
    first_turn_context: int
    output_tokens: int
    messages: int
    unfinalised: int
    read_count: int
    bash_count: int
    tool_count: int
    largest_reads: tuple
    command_counts: dict
    skipped_lines: int


class SizeRow(NamedTuple):
    key: str
    value: int
    growth: Optional[int]


def transcripts(directory: pathlib.Path) -> list[tuple[pathlib.Path, pathlib.Path | None]]:
    """Return (jsonl, meta_or_None) pairs, ordered by each transcript's first timestamp."""
    pairs = []
    for jsonl in directory.glob("agent-*.jsonl"):
        meta = jsonl.with_name(jsonl.stem + ".meta.json")
        pairs.append((jsonl, meta if meta.is_file() else None))

    def first_timestamp(pair):
        jsonl, _meta = pair
        try:
            with jsonl.open(encoding="utf-8") as handle:
                first_line = handle.readline()
            first = json.loads(first_line)
            return first.get("timestamp", "") if isinstance(first, dict) else ""
        except (OSError, json.JSONDecodeError):
            return ""

    return sorted(pairs, key=first_timestamp)


def _read_text_size(content) -> int:
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(len(block.get("text", "")) for block in content if isinstance(block, dict))
    return 0


def agent_figures(
    jsonl: pathlib.Path, meta: pathlib.Path | None, commands: Sequence[str]
) -> AgentFigures:
    meta_data = {}
    if meta is not None:
        try:
            meta_data = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            meta_data = {}

    model_ran = ""
    first_turn_context = 0
    output_tokens = 0
    read_count = 0
    bash_count = 0
    tool_count = 0
    seen_tool_ids = set()
    output_by_message = {}
    final_ids = set()
    all_ids = set()
    anonymous_messages = 0
    anonymous_final = 0
    reads = []
    command_counts = {command: 0 for command in commands}
    skipped_lines = 0
    read_paths_by_id = {}
    seen_first_usage = False

    with jsonl.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                skipped_lines += 1
                continue

            if not isinstance(row, dict) or not isinstance(row.get("message", {}), dict):
                skipped_lines += 1
                continue

            row_type = row.get("type")
            message = row.get("message", {})

            if row_type == "assistant":
                if not model_ran:
                    model_ran = message.get("model", "")
                usage = message.get("usage")
                message_id = message.get("id")
                # One API message is written as several entries that share its id. Their
                # output_tokens are streaming snapshots, so the largest is the final figure.
                if usage:
                    out_now = usage.get("output_tokens", 0) or 0
                    # stop_reason stays None until the harness records the finished message.
                    # Without it, output_tokens is only a snapshot taken while the message
                    # streamed, and can be far below the real figure.
                    finished = message.get("stop_reason") is not None
                    if message_id is None:
                        output_tokens += out_now
                        anonymous_messages += 1
                        anonymous_final += 1 if finished else 0
                    else:
                        all_ids.add(message_id)
                        if finished:
                            final_ids.add(message_id)
                        output_by_message[message_id] = max(
                            output_by_message.get(message_id, 0), out_now
                        )
                    if not seen_first_usage:
                        first_turn_context = (
                            (usage.get("input_tokens", 0) or 0)
                            + (usage.get("cache_creation_input_tokens", 0) or 0)
                            + (usage.get("cache_read_input_tokens", 0) or 0)
                        )
                        seen_first_usage = True
                for block in message.get("content", []) or []:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    tool_id = block.get("id")
                    if tool_id is None or tool_id not in seen_tool_ids:
                        tool_count += 1
                        seen_tool_ids.add(tool_id)
                    name = block.get("name")
                    block_input = block.get("input") or {}
                    if name == "Read":
                        read_count += 1
                        read_paths_by_id[block.get("id")] = block_input.get("file_path", "")
                    elif name == "Bash":
                        bash_count += 1
                        command = block_input.get("command", "") or ""
                        for substring in commands:
                            if substring in command:
                                command_counts[substring] += 1

            elif row_type == "user":
                content = message.get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_result":
                        continue
                    tool_use_id = block.get("tool_use_id")
                    if tool_use_id in read_paths_by_id:
                        size = _read_text_size(block.get("content"))
                        reads.append((size, read_paths_by_id[tool_use_id]))

    output_tokens += sum(output_by_message.values())
    reads.sort(key=lambda pair: pair[0], reverse=True)

    return AgentFigures(
        agent_id=jsonl.stem,
        agent_type=meta_data.get("agentType", "unknown"),
        description=meta_data.get("description", ""),
        model_asked=meta_data.get("model", ""),
        model_ran=model_ran,
        first_turn_context=first_turn_context,
        output_tokens=output_tokens,
        messages=len(all_ids) + anonymous_messages,
        unfinalised=(len(all_ids) - len(final_ids)) + (anonymous_messages - anonymous_final),
        read_count=read_count,
        bash_count=bash_count,
        tool_count=tool_count,
        largest_reads=tuple(reads[:5]),
        command_counts=command_counts,
        skipped_lines=skipped_lines,
    )


def run_agents(directory: pathlib.Path, commands: Sequence[str], out: TextIO) -> int:
    if not directory.is_dir():
        print(f"process-run-report: no such directory: {directory}", file=sys.stderr)
        return 2

    pairs = transcripts(directory)
    if not pairs:
        print(f"process-run-report: no agent-*.jsonl files in {directory}", file=sys.stderr)
        return 2

    total_output = 0
    total_unfinalised = 0
    total_tools = 0
    for jsonl, meta in pairs:
        figures = agent_figures(jsonl, meta, commands)
        asked = figures.model_asked or "unknown"
        ran = figures.model_ran or "unknown"
        print(f"{figures.agent_id}  {figures.agent_type}  asked {asked}  ran {ran}", file=out)
        if figures.unfinalised:
            output_text = (
                f"output NOT AVAILABLE (transcript holds only a partial snapshot: at least "
                f"{figures.output_tokens}; {figures.unfinalised} of {figures.messages} messages "
                f"never finalised)"
            )
        else:
            output_text = f"output {figures.output_tokens}"
        print(f"  first-turn context {figures.first_turn_context}, {output_text}", file=out)
        tool_total = figures.tool_count
        print(f"  {tool_total} tool uses (all tools): {figures.read_count} Read, {figures.bash_count} Bash", file=out)
        if figures.largest_reads:
            print("  largest reads:", file=out)
            for size, path in figures.largest_reads:
                print(f"    {size}  {path}", file=out)
        for substring in commands:
            print(f'  command "{substring}": {figures.command_counts.get(substring, 0)}', file=out)
        if figures.skipped_lines:
            print(f"  skipped {figures.skipped_lines} unparseable lines", file=out)
        print(file=out)
        total_output += figures.output_tokens
        total_unfinalised += figures.unfinalised
        total_tools += tool_total

    if total_unfinalised:
        output_total = (
            f"output tokens NOT AVAILABLE (lower bound only: at least {total_output}; "
            f"{total_unfinalised} messages never finalised in the transcripts)"
        )
    else:
        output_total = f"{total_output} output tokens"
    print(f"total: {len(pairs)} agents, {output_total}, {total_tools} tool uses", file=out)
    return 0


def _load_context_check():
    script = pathlib.Path(__file__).resolve().parent / "context-check.py"
    spec = importlib.util.spec_from_file_location("context_check_for_process_run", script)
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    return module


def _instruction_file_words(repo_root: pathlib.Path) -> int:
    context_check = _load_context_check()
    files = context_check.instruction_files(repo_root)
    return sum(context_check.word_count(path) for path in files)


def last_row(scoreboard: pathlib.Path) -> dict[str, str]:
    if not scoreboard.is_file():
        return {}
    lines = scoreboard.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        return {}
    header = lines[0].split("\t")
    last = lines[-1].split("\t")
    return {name: value for name, value in zip(header, last) if value}


def size_rows(repo_root: pathlib.Path, previous: Mapping[str, str]) -> list[SizeRow]:
    rows = []

    def add(key: str, value: int) -> None:
        prior = previous.get(key)
        growth = None
        if prior is not None:
            try:
                growth = value - int(prior)
            except ValueError:
                growth = None
        rows.append(SizeRow(key=key, value=value, growth=growth))

    for key in STABLE_SIZE_KEYS:
        if key == "work/designs/":
            directory = repo_root / key
            total = 0
            if directory.is_dir():
                total = sum(p.stat().st_size for p in directory.rglob("*") if p.is_file())
            add(key, total)
        elif key != "instruction-file-words":
            path = repo_root / key
            add(key, path.stat().st_size if path.is_file() else 0)

    add("instruction-file-words", _instruction_file_words(repo_root))

    return rows


def _format_growth(growth: int | None) -> str | None:
    if growth is None:
        return None
    if growth > 0:
        return f"+{growth}"
    if growth < 0:
        return str(growth)
    return "same"


def run_sizes(repo_root: pathlib.Path, scoreboard: pathlib.Path, out: TextIO) -> int:
    previous = last_row(scoreboard)
    for row in size_rows(repo_root, previous):
        fields = [row.key, str(row.value)]
        growth = _format_growth(row.growth)
        if growth is not None:
            fields.append(growth)
        print("\t".join(fields), file=out)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)

    agents_parser = subparsers.add_parser("agents")
    agents_parser.add_argument("directory", type=pathlib.Path)
    agents_parser.add_argument("--command", action="append", default=[], dest="commands")

    sizes_parser = subparsers.add_parser("sizes")
    sizes_parser.add_argument("--scoreboard", type=pathlib.Path, default=None)

    args = parser.parse_args(argv)

    if args.mode == "agents":
        return run_agents(args.directory, args.commands, sys.stdout)

    scoreboard = args.scoreboard or (REPO_ROOT / "improvement" / "process-runs" / "scoreboard.tsv")
    return run_sizes(REPO_ROOT, scoreboard, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
