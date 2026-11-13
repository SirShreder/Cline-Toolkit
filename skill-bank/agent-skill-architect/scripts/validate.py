#!/usr/bin/env python3
"""Validate Cline customization artifacts: skills, rules, workflows, hooks.

Static checks by default.

Usage:
    python validate.py [root]

Exit code 1 if any FAIL was reported. WARN and SKIP do not fail the run.
"""
import argparse
import os
import re
import sys
from pathlib import Path

SKILL_ROOTS = (".cline/skills", ".clinerules/skills", ".claude/skills", ".agents/skills")
RULE_ROOTS = (".cline/rules", ".clinerules")
WORKFLOW_ROOTS = (".cline/workflows", ".clinerules/workflows")
HOOK_ROOTS = (".cline/hooks", ".clinerules/hooks")

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EVENTS = {
    "TaskStart", "TaskResume", "UserPromptSubmit", "PreToolUse", "PostToolUse",
    "TaskComplete", "TaskError", "TaskCancel", "SessionShutdown",
}
HOOK_OUTPUT_KEYS = {"cancel", "review", "context", "errorMessage", "overrideInput"}
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 500


class Report:
    def __init__(self, quiet=False):
        self.rows = []
        self.quiet = quiet

    def add(self, level, path, message):
        self.rows.append((level, str(path), message))

    def fail(self, path, message):
        self.add("FAIL", path, message)

    def warn(self, path, message):
        self.add("WARN", path, message)

    def ok(self, path, message=""):
        self.add("OK", path, message)

    def skip(self, path, message):
        self.add("SKIP", path, message)

    def emit(self):
        for level, path, message in self.rows:
            if self.quiet and level in {"OK", "SKIP"}:
                continue
            line = f"{level:<4} {path}"
            print(f"{line} — {message}" if message else line)
        failures = sum(1 for level, _, _ in self.rows if level == "FAIL")
        warnings = sum(1 for level, _, _ in self.rows if level == "WARN")
        skipped = sum(1 for level, _, _ in self.rows if level == "SKIP")
        oks = sum(1 for level, _, _ in self.rows if level == "OK")
        print()
        print(f"SUMMARY ok={oks} fail={failures} warn={warnings} skip={skipped}")
        return 1 if failures else 0


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def parse_frontmatter(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fields = {}
            for j in range(1, i):
                line = lines[j].strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, val = line.split(":", 1)
                    fields[key.strip()] = val.strip()
            body = "\n".join(lines[i + 1:])
            return fields, body
    return None, text

def check_skill(skill_dir, report, root):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        report.fail(skill_dir, "SKILL.md missing")
        return

    text = read_text(skill_md)
    if not text.strip():
        report.fail(skill_md, "SKILL.md is empty")
        return

    fields, body = parse_frontmatter(text)
    if fields is None:
        report.fail(skill_md, "YAML frontmatter missing (no opening '---')")
        return

    name = fields.get("name", "")
    description = fields.get("description", "")

    if not name:
        report.fail(skill_md, "frontmatter 'name' is empty")
    elif not KEBAB.match(name):
        report.fail(skill_md, f"name '{name}' is not kebab-case")
    elif name != skill_dir.name:
        report.fail(skill_md, f"name '{name}' does not match directory '{skill_dir.name}'")

    if not description:
        report.fail(skill_md, "frontmatter 'description' is empty")
    elif len(description) > MAX_DESCRIPTION:
        report.warn(skill_md, f"description is {len(description)} chars (>1024)")

    if len(text.split("\n")) > MAX_SKILL_LINES:
        report.warn(skill_md, f"SKILL.md exceeds {MAX_SKILL_LINES} lines")

    for md_file in skill_dir.rglob("*.md"):
        if md_file == skill_md:
            continue
        md_text = read_text(md_file)
        for match in re.finditer(r'\(((?:docs|templates|scripts|references|assets)/[^)\s]+)\)', md_text):
            ref = match.group(1)
            if ref.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (skill_dir / ref).resolve()
            if not resolved.exists():
                report.fail(md_file, f"referenced path does not exist: {ref}")
            else:
                report.ok(md_file, f"path resolves: {ref}")


def check_rule(rule_file, report):
    text = read_text(rule_file)
    if not text.strip():
        report.fail(rule_file, "rule file is empty")
        return

    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        fields, _ = parse_frontmatter(text)
        if fields is None:
            report.fail(rule_file, "YAML frontmatter opens but never closes")


def check_workflow(workflow_file, report):
    text = read_text(workflow_file)
    if not text.strip():
        report.fail(workflow_file, "workflow file is empty")
        return

    if not re.search(r"^\s*\d+\.\s+\S", text, re.MULTILINE):
        report.warn(workflow_file, "no numbered step found")


def check_hooks(hook_dir, report):
    if not hook_dir.is_dir():
        return
    for hook_file in hook_dir.iterdir():
        if not hook_file.is_file():
            continue
        name = hook_file.name
        event = name.rsplit(".", 1)[0] if "." in name else name
        if event not in EVENTS:
            report.fail(hook_file, f"unknown event '{event}'; expected one of {sorted(EVENTS)}")
        text = read_text(hook_file)
        if not text.strip():
            report.fail(hook_file, "hook file is empty")
            continue
        has_output_key = any(k in text for k in HOOK_OUTPUT_KEYS)
        if not has_output_key:
            report.warn(hook_file, "no hook output key found (cancel/review/context/errorMessage/overrideInput)")

def main():
    parser = argparse.ArgumentParser(
        description="Validate Cline skills, rules, workflows, and hooks."
    )
    parser.add_argument("root", nargs="?", default=".", help="project root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"FAIL {root} — not a directory")
        return 1

    report = Report()

    for relative in SKILL_ROOTS:
        base = root / relative
        if not base.is_dir():
            continue
        for skill in sorted(base.iterdir()):
            if skill.is_dir() and (skill / "SKILL.md").is_file():
                check_skill(skill, report, root)
            elif skill.is_dir():
                report.fail(skill, "directory has no SKILL.md")

    for relative in RULE_ROOTS:
        base = root / relative
        if not base.is_dir():
            continue
        for rule in sorted(base.glob("*.md")):
            check_rule(rule, report)

    for relative in WORKFLOW_ROOTS:
        base = root / relative
        if not base.is_dir():
            continue
        for workflow in sorted(base.glob("*.md")):
            check_workflow(workflow, report)

    for relative in HOOK_ROOTS:
        check_hooks(root / relative, report)

    if not report.rows:
        print(f"nothing to validate under {root} (no .cline/ or .clinerules/ artifacts found)")
        return 0
    return report.emit()


if __name__ == "__main__":
    sys.exit(main())