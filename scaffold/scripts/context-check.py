#!/usr/bin/env python3
"""Report drift in the instruction files: word budgets, repeated paragraphs, dead paths, em dashes.
Writes nothing. See improvement/process-runs/README.md."""

import argparse
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

INSTRUCTION_GLOBS = (
    "CLAUDE.md",
    ".claude/agents/*.md",
    ".claude/skills/*/SKILL.md",
    "standards/*.md",
    "team/*.md",
)

# Edited by hand when a file is deliberately resized, with the reason in the commit message.
# Seeded by /team-init at each instruction file's word count when the team was created, so
# it flags growth only; tighter budgets, and budgets for files added later, are operator calls.
BUDGETS = {
}

# (normalised paragraph, reason). Only for a paragraph a requirement mandates repeating.
ALLOWED_DUPLICATES = ()

MIN_DUPLICATE_WORDS = 12
PATH_SUFFIXES = (".md", ".py", ".json", ".html", ".yml", ".yaml", ".sh", ".txt")
PATTERN_CHARS = set("*?#<>{}")
HEADINGS = (
    "== Files over their word budget ==",
    "== Paragraphs repeated across instruction files ==",
    "== Backticked repository paths that do not exist ==",
    "== Em dashes in instruction files ==",
)
EM_DASH = "—"
FENCE = re.compile(r"^\s*(```|~~~)")
SPAN = re.compile(r"`([^`\s]+)`")


def instruction_files(repo_root):
    found = set()
    for pattern in INSTRUCTION_GLOBS:
        found.update(p for p in repo_root.glob(pattern) if p.is_file())
    return sorted(found)


def rel(path, repo_root):
    return path.relative_to(repo_root).as_posix()


def word_count(path):
    return len(path.read_text(encoding="utf-8").split())


def over_budget(repo_root, budgets):
    """Return (over, missing): (rel_path, words, budget) tuples and budgeted paths that are absent."""
    over, missing = [], []
    for name, budget in sorted(budgets.items()):
        path = repo_root / name
        if not path.is_file():
            missing.append(name)
            continue
        words = word_count(path)
        if words > budget:
            over.append((name, words, budget))
    return over, missing


def unfenced_lines(text):
    """Yield (line_number, line) for every line outside a fenced code block."""
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def paragraphs(text):
    """Yield (first_line_number, joined_text) for each run of contiguous non-blank lines."""
    run, start = [], 0
    for number, line in unfenced_lines(text):
        if line.strip():
            if not run:
                start = number
            run.append(line.strip())
        elif run:
            yield start, " ".join(run)
            run = []
    if run:
        yield start, " ".join(run)


def normalise(paragraph):
    text = re.sub(r"[`*_>#]", "", paragraph)
    text = " ".join(text.split()).lower()
    return text.rstrip(".,;:!?")


def duplicate_paragraphs(files, repo_root, allowed=ALLOWED_DUPLICATES):
    """Return (normalised_text, words, [(rel_path, line), ...]) for paragraphs in two or more files."""
    allowed_texts = {text for text, _reason in allowed}
    seen = {}
    for path in files:
        name = rel(path, repo_root)
        for line, paragraph in paragraphs(path.read_text(encoding="utf-8")):
            text = normalise(paragraph)
            words = len(text.split())
            if words < MIN_DUPLICATE_WORDS or text in allowed_texts:
                continue
            seen.setdefault(text, {}).setdefault(name, line)
    groups = []
    for text, places in seen.items():
        if len(places) > 1:
            groups.append((text, len(text.split()), sorted(places.items())))
    return sorted(groups, key=lambda group: group[2])


def is_checked_path(token, repo_root):
    if "/" not in token or token.startswith(("/", "..")) or "://" in token:
        return False
    if PATTERN_CHARS & set(token):
        return False
    return (repo_root / token.split("/", 1)[0]).exists()


def dead_paths(files, repo_root):
    """Return (rel_path, line, token) for backticked repository paths that do not exist."""
    dead = []
    for path in files:
        name = rel(path, repo_root)
        for number, line in unfenced_lines(path.read_text(encoding="utf-8")):
            for token in SPAN.findall(line):
                if not is_checked_path(token, repo_root):
                    continue
                target = repo_root / token
                exists = target.is_dir() if token.endswith("/") else target.exists()
                if not exists:
                    dead.append((name, number, token))
    return dead


def em_dashes(files, repo_root):
    """Return (rel_path, count, [line, ...]) for each file that holds an em dash."""
    found = []
    for path in files:
        lines = [n for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
                 if EM_DASH in line]
        count = path.read_text(encoding="utf-8").count(EM_DASH)
        if lines:
            found.append((rel(path, repo_root), count, lines))
    return found


def report(repo_root, budgets=BUDGETS, allowed=ALLOWED_DUPLICATES):
    """Return the four sections as lists of lines, in heading order."""
    files = instruction_files(repo_root)
    over, missing = over_budget(repo_root, budgets)
    section1 = [f"  {n}: {w} words, budget {b}" for n, w, b in over]
    section1 += [f"  {n}: missing, budgeted but not found" for n in missing]
    section2 = []
    for text, words, places in duplicate_paragraphs(files, repo_root, allowed):
        section2.append(f"  {words} words: {text[:70]}...")
        section2 += [f"    {name}:{line}" for name, line in places]
    section3 = [f"  {n}:{line}: {token}" for n, line, token in dead_paths(files, repo_root)]
    section4 = [f"  {n}: {c} (lines {', '.join(map(str, ls))})"
                for n, c, ls in em_dashes(files, repo_root)]
    return [section1, section2, section3, section4]


def run(repo_root, strict=False, budgets=BUDGETS, out=sys.stdout, allowed=ALLOWED_DUPLICATES):
    sections = report(repo_root, budgets, allowed)
    for heading, lines in zip(HEADINGS, sections):
        print(heading, file=out)
        print("\n".join(lines) if lines else "  none", file=out)
        print(file=out)
    return 1 if strict and any(sections) else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit 1 when any section is non-empty")
    args = parser.parse_args(argv)
    return run(REPO_ROOT, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
