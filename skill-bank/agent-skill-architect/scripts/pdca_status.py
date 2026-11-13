#!/usr/bin/env python3
"""Report the state of the current PDCA cycle in a memory bank.

Reads memory-bank/plan.md (cycle id, acceptance checkboxes) and
memory-bank/progress.md (verdict, closed flag), and prints a summary.

Usage:
    python pdca_status.py [project-root]

Exit code 0 always — this is a report, not a gate.
"""
import re
import sys
from pathlib import Path

CHECKBOX = re.compile(r"^\s*-\s*\[([ xX])\]\s+")
CYCLE = re.compile(r"Cycle:\s*(C\d+)\s*$", re.IGNORECASE)
VERDICT = re.compile(r"`(PASS|FAIL|PARTIAL)`")
CLOSED = re.compile(r"cycle closed:\s*(yes|no)", re.IGNORECASE)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def verdict_of(text: str) -> str:
    """Read the verdict from the most recent verdict marker."""
    matches = VERDICT.findall(text)
    return matches[-1] if matches else "—"


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    bank = root / "memory-bank"
    if not bank.is_dir():
        print(f"no memory-bank under {root}")
        return 0

    # Read progress.md for cycle state
    progress = read(bank / "progress.md")

    cycle = "—"
    for line in progress.splitlines():
        match = CYCLE.match(line.strip())
        if match:
            cycle = match.group(1)
            break

    boxes = [match.group(1) for line in progress.splitlines() if (match := CHECKBOX.match(line))]
    done = sum(1 for mark in boxes if mark in "xX")

    verdict = verdict_of(progress)
    closed_match = CLOSED.search(progress)
    closed = closed_match.group(1) if closed_match else "—"

    # Count archived cycles from progress.md headers
    cycles = sum(1 for line in progress.splitlines() if re.match(r"^##\s*C\d+", line))

    print(f"cycle:          {cycle}")
    print(f"criteria:       {done}/{len(boxes)} done" if boxes else "criteria:       none found")
    print(f"verdict:        {verdict}")
    print(f"cycle closed:   {closed}")
    print(f"archived:       {cycles} cycle(s)")

    gaps: list[str] = []
    if cycle == "—":
        gaps.append("no open cycle: progress.md has no 'Cycle: Cn' line")
    if boxes and verdict == "—":
        gaps.append("no PASS/FAIL/PARTIAL verdict yet")
    if verdict in {"FAIL", "PARTIAL"}:
        gaps.append(f"current cycle is {verdict}; start the next task from that gap")
    if closed.lower() == "yes" and cycle != "—":
        gaps.append("check.md says the cycle is closed; archive it and rewrite progress.md")
    if not boxes:
        gaps.append("no acceptance criteria found in progress.md")

    print()
    if gaps:
        print("attention:")
        for gap in gaps:
            print(f"  - {gap}")
    else:
        print("state looks consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())