#!/usr/bin/env python3
"""
Fail-closed structural validation of Agent Skills packages.

Python equivalent of validate_skill.ps1 for cross-platform use.
Implements: SKILL.md exists and is non-empty; YAML frontmatter opens/closes
with '---'; frontmatter keys restricted to the allowed set
(name, description, license, allowed-tools, metadata, compatibility);
'name' is kebab-case, max 64 chars, matches directory name;
'description' is non-empty, max 1024 chars (warning above 500), no angle
brackets; optional 'compatibility' field, if present, is a string of at most
500 characters; every relative path referenced from bundled .md files under
references/, scripts/, assets/, docs/, or templates/ resolves (URLs ignored);
SKILL.md under 500 lines (warning only).

Usage:
    python validate_skill.py /path/to/<skill-or-skills-root>

Exit codes: 0 = all pass, 1 = any error, 2 = usage error.
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ALLOWED_PROPERTIES = {
    'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility',
}


def parse_frontmatter_value(frontmatter_lines, field_name):
    """Extract a top-level scalar or block-scalar value from frontmatter lines.

    Supports plain scalars (name: my-skill) and YAML block scalars (|, >,
    |-, >-); multi-line block values are joined with single spaces.
    Surrounding double quotes are stripped.
    """
    value = ""
    buffer = ""
    in_block = False

    for line in frontmatter_lines:
        if in_block:
            if line[:1].isspace():
                trimmed = line.strip()
                if buffer:
                    buffer = f"{buffer} {trimmed}"
                else:
                    buffer = trimmed
                continue
            value = buffer
            in_block = False
            break
        if line.startswith(f"{field_name}:"):
            scalar = line[len(field_name) + 1:].strip()
            if scalar in ("|", ">", "|-", ">-"):
                in_block = True
                continue
            value = scalar
            break

    if in_block and not value:
        value = buffer

    value = value.replace('^"', '', 1).replace('"$', '', 1)
    return value


def test_skill_package(skill_directory):
    """Run all structural checks against one skill directory."""
    errors = []
    warnings = []
    dir_name = os.path.basename(skill_directory.rstrip(os.sep))
    skill_md = os.path.join(skill_directory, "SKILL.md")
    skill_md_exists = os.path.isfile(skill_md) and os.path.getsize(skill_md) > 0
    if not skill_md_exists:
        errors.append(f"SKILL.md is missing or empty at: {skill_md}")
        return {"Skill": dir_name, "Path": skill_directory, "Status": "Failed",
                "Errors": errors, "Warnings": warnings}

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    if not lines or lines[0] != "---":
        first_line = lines[0] if lines else ""
        errors.append(
            f"SKILL.md must start with a '---' line (found: '{first_line}')"
        )

    close_index = -1
    for i in range(1, len(lines)):
        if re.match(r"^---\s*$", lines[i]):
            close_index = i
            break

    if close_index == -1:
        errors.append("Frontmatter is never closed by a '---' line")

    frontmatter_lines = []
    if close_index > 1:
        frontmatter_lines = lines[1:close_index]
    elif close_index == -1 and len(lines) > 1:
        frontmatter_lines = lines[1:]

    name = parse_frontmatter_value(frontmatter_lines, "name")
    if not name:
        errors.append("Frontmatter field 'name' is missing or empty")
    elif len(name) > 64:
        errors.append(f"Frontmatter 'name' exceeds 64 characters: {name}")
    elif not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        errors.append(
            f"Frontmatter 'name' must be lowercase letters, digits, and single hyphens: {name}"
        )

    if name and name != dir_name:
        errors.append(
            f"Frontmatter 'name' ({name}) must match the skill directory name: {dir_name}"
        )

    description = parse_frontmatter_value(frontmatter_lines, "description")
    if not description:
        errors.append("Frontmatter field 'description' is missing or empty")
    else:
        if '<' in description or '>' in description:
            errors.append("Frontmatter 'description' must not contain angle brackets (< or >)")
        if len(description) > 1024:
            errors.append(
                f"Frontmatter 'description' exceeds 1024 characters ({len(description)})"
            )
        elif len(description) > 500:
            warnings.append(
                "description is {} characters; recommended budget is 500 for all runtimes "
                "(the DeepSeek harness session catalog hard-caps at 500 by default)".format(
                    len(description)
                )
            )

    # C-1: frontmatter key whitelist (matches skill-creator quick_validate.py)
    fm_keys = set(frontmatter_lines)  # placeholder; actual keys parsed below
    # Re-parse frontmatter into a dict for key whitelist check
    fm_data = {}
    for line in frontmatter_lines:
        if ':' in line and not line.startswith(' ') and not line.startswith('-'):
            key, _, _ = line.partition(':')
            fm_data[key.strip()] = True
    unexpected_keys = set(fm_data.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        errors.append(
            "Unexpected frontmatter key(s): {}. Allowed: {}".format(
                ', '.join(sorted(unexpected_keys)),
                ', '.join(sorted(ALLOWED_PROPERTIES)),
            )
        )

    # C-3: optional compatibility field validation
    compatibility = parse_frontmatter_value(frontmatter_lines, "compatibility")
    if compatibility:
        if len(compatibility) > 500:
            errors.append(
                f"Frontmatter 'compatibility' exceeds 500 characters ({len(compatibility)})"
            )

    # Ghost File Rule: check cross-references in all .md files
    md_files = []
    for root, dirs, files in os.walk(skill_directory):
        for fn in files:
            if fn.endswith(".md"):
                md_files.append(os.path.join(root, fn))

    url_pattern = re.compile(r"https?://[^\)\s]+")
    ref_pattern = re.compile(
        r"(?:references|scripts|assets|docs|templates)/[A-Za-z0-9._/-]+"
    )

    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
        stripped = url_pattern.sub("", md_content)
        refs = sorted(set(ref_pattern.findall(stripped)))
        for ref in refs:
            ref_path = os.path.join(skill_directory, ref)
            if not os.path.exists(ref_path):
                errors.append(
                    f"Referenced path does not exist: {ref} (in {md_file})"
                )

    line_count = content.count("\n")
    if line_count > 500:
        warnings.append(
            f"SKILL.md is {line_count} lines; keep it under 500 lines (~5k tokens) - "
            "move detail into reference files"
        )

    status = "Passed" if not errors else "Failed"
    return {
        "Skill": dir_name,
        "Path": skill_directory,
        "Status": status,
        "Errors": errors,
        "Warnings": warnings,
    }


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python validate_skill.py /path/to/<skill-or-skills-root>",
            file=sys.stderr,
        )
        return 2

    path = sys.argv[1]
    results = []
    harness_errors = []

    if not os.path.isdir(path):
        harness_errors.append(f"Skill directory or skills root not found: {path}")
    else:
        root_skill_md = os.path.join(path, "SKILL.md")
        targets = []

        if os.path.isfile(root_skill_md):
            targets = [path]
        else:
            targets = sorted(
                os.path.join(path, d) for d in os.listdir(path)
                if os.path.isdir(os.path.join(path, d))
            )
            if not targets:
                harness_errors.append(f"No skill directories found under root: {path}")

        for target in targets:
            results.append(test_skill_package(target))

    failed_count = sum(1 for r in results if r["Status"] == "Failed")

    summary = {
        "Root": path,
        "TotalSkills": len(results),
        "FailedCount": failed_count,
        "HarnessErrors": harness_errors,
        "Skills": results,
    }

    print(json.dumps(summary, indent=2))

    if failed_count > 0 or harness_errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
