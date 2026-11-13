#!/usr/bin/env python3
"""Structural validator for AgentSkills.io skill packages (Python 3, stdlib only).

Usage:
    python3 scripts/validate_skill.py /path/to/<skill-directory>

It is a complete Python 3 script and runs
directly with python3. No extraction, renaming, or assembly step exists.

Checks:
  1. The skill directory and SKILL.md exist (SKILL.md non-empty).
  2. YAML frontmatter opens with a '---' line, is closed by a '---' line,
     and every non-empty line between the delimiters is frontmatter-shaped
     (a key line, an indented continuation, or a comment). Prose between
     the delimiters fails instead of being scraped as frontmatter.
  3. Frontmatter keys are restricted to name, description, license,
     allowed-tools, metadata, and compatibility; any other key fails
     (user-created registry skills must not add fields such as visibility
     or defaultEnabled).
  4. 'name' is non-empty, lowercase letters/digits/hyphens only, max 64
     characters, and matches the skill directory name (Cline requires an
     exact match).
  5. 'description' is non-empty, at most 1024 characters, and contains no
     angle brackets (< or >; some runtimes render the catalog as markup).
     Above 500 characters a warning is printed: the recommended cross-runtime
     budget is 500 characters, and the DeepSeek harness session catalog caps
     descriptions at 500 characters by default (catalogDescriptionMaxLength,
     configurable).
  6. The optional 'compatibility' field, when present, is a single string of
     at most 500 characters (lists and mappings fail — flow style '[...]',
     '{...}' and block style '- item' alike).
  7. Every relative path under references/, scripts/, assets/, docs/, or
     templates/ referenced in any of the skill's Markdown files resolves to
     an existing file or directory (Ghost File Rule). Paths in prose are
     package-root relative. URLs are ignored when matching. Only paths
     rooted at this package's layers are captured: a captured reference
     containing a parent-relative '..' segment draws a warning (it is
     outside the single-level-deep path contract) and is not
     existence-checked; cross-skill references such as
     ../other-skill/references/x.md are not captured at all. A captured
     reference nesting deeper than one folder level draws a warning
     (SKILL.md requires single-level-deep relative paths) and is still
     existence-checked.
  8. Warning when SKILL.md exceeds 500 lines (cross-runtime context budget
     guidance: under 5k tokens, roughly 500 lines).
  9. Warning when a Markdown line references another skill as '<name>'
     skill without conditional wording (installed, absent, unavailable,
     or 'if/when present') on the same line: a cross-skill reference
     must state when it applies. A reference to the package's own name
     is skipped.
  10. Warning when a package file (besides SKILL.md and hidden files) is
     referenced by no scanned Markdown file: inventory drift. A reference
     to a directory covers the files beneath it.

Frontmatter parsing: plain scalars and block scalars (|, >, |-, >-) are both
supported. Multi-line values — block scalars and indented plain-scalar
continuations — are joined with single spaces. An indented key-shaped line
('key: value') inside a plain multi-line value fails closed: plain scalars
cannot contain key lines (invalid YAML); block scalars (| or >) accept such
lines as content. Matching single or double
quotes are stripped, surrounding whitespace is trimmed, and ' #' trailing
comments are removed outside quotes. A quoted scalar never starts a block
scalar (the block check runs before quote stripping); a block-scalar
indentation indicator (e.g. '|2') is accepted with the indicator digits
ignored. CRLF line endings are normalized and a leading UTF-8 byte-order
mark is tolerated on read (utf-8-sig). Lengths are counted in Unicode
code points.

Self-test: scripts/selftest_skill.py pins every check and parser shape
documented in this header with positive and negative fixtures. Run it
whenever this file changes, and change the fixtures in the same step as
any check they pin.

Exit codes: 0 = valid (warnings possible), 1 = validation errors found,
2 = usage error (missing directory argument, or the directory does not exist).

Authoring-decision rules in SKILL.md (compose edits against on-disk state,
remediate by failure class, layer ownership of enforcement mechanisms,
three-way code placement — code read to reason in references/, verbatim copy
targets in assets/ or templates/, executable code in scripts/, always named
as concrete relative paths — fail-closed validators, circular reference
chains, priority-chain contradiction resolution, stale-content sweeps, one
task per section / one instruction per sentence) are procedural judgments
and are not structurally checkable; they are intentionally not implemented
in this script. Two further semantic rules are intentionally not
implemented, with reasons: the description-to-body fidelity check
(references/AUDIT.md, item 19 — the validator checks only the description's
schema, length, and bracket constraints) and the ban on enumerations in
frontmatter descriptions (references/AUDIT.md, Layer Ownership — trigger
phrases and summary enumerations cannot be distinguished by a regular
expression). The single-level-deep path rule is mechanized as a warning in
check 7.
"""

import os
import re
import sys

WHITELISTED_KEYS = ("name", "description", "license", "allowed-tools",
                    "metadata", "compatibility")
KEY_LINE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:")
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
URL_PATTERN = re.compile(r"https?://\S+")
LAYER_PATH = re.compile(
    r"(?<![A-Za-z0-9._/-])(?:(?:\.\./)+)?"
    r"(?:references|scripts|assets|docs|templates)/[A-Za-z0-9._/-]+")
CROSS_SKILL = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*)` skill")

class FrontmatterError(ValueError):
    """Raised when a frontmatter value cannot be parsed unambiguously."""


ERRORS = 0
WARNINGS = 0


def fail(message):
    global ERRORS
    ERRORS += 1
    sys.stderr.write("ERROR: %s\n" % message)


def warn(message):
    global WARNINGS
    WARNINGS += 1
    sys.stderr.write("WARNING: %s\n" % message)


def ok(message):
    sys.stdout.write("OK: %s\n" % message)


def strip_scalar(raw):
    """Trim whitespace and trailing comments; strip matching quotes."""
    value = raw.strip()
    if not value:
        return ""
    if value[0] in ('"', "'"):
        if len(value) >= 2 and value[-1] == value[0]:
            return value[1:-1]
        return value
    cut = value.find(" #")
    if cut != -1:
        value = value[:cut].rstrip()
    return value


def parse_frontmatter(lines):
    """Return (frontmatter_lines, None) or (None, error_message)."""
    if not lines or lines[0].rstrip() != "---":
        first = lines[0].strip() if lines else "(empty file)"
        return None, ("SKILL.md must start with a '---' line "
                      "(found: '%s')" % first)
    close = -1
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            close = index
            break
    if close == -1:
        return None, "Frontmatter is never closed by a '---' line"
    body_lines = lines[1:close]
    for line in body_lines:
        if not line.strip():
            continue
        if line[0] in (" ", "\t"):
            continue
        if line.startswith("#"):
            continue
        if not KEY_LINE.match(line):
            return None, ("Frontmatter contains non-frontmatter content "
                          "before the closing '---' line (unclosed "
                          "frontmatter): '%s'" % line.strip())
    return body_lines, None


def get_field(fm_lines, field):
    """Folded scalar value of 'field:' or None when the field is absent."""
    for index, line in enumerate(fm_lines):
        if not KEY_LINE.match(line):
            continue
        key = line.split(":", 1)[0]
        if key != field:
            continue
        raw = line[len(key) + 1:]
        head = raw.strip()
        if head and head[0] in ("|", ">"):
            # Block scalar. The check runs on the raw text before quote
            # stripping, so a quoted scalar never starts a block scalar;
            # an explicit indentation indicator (e.g. '|2') is accepted
            # with the indicator digits ignored.
            folded = []
            for follow in fm_lines[index + 1:]:
                if not follow.strip():
                    continue
                if follow[0] not in (" ", "\t"):
                    break
                folded.append(follow.strip())
            return " ".join(folded)
        value = strip_scalar(raw)
        folded = [value]
        for follow in fm_lines[index + 1:]:
            if not follow.strip():
                break
            if follow[0] not in (" ", "\t"):
                break
            if KEY_LINE.match(follow.lstrip()):
                raise FrontmatterError(
                    "Frontmatter field '%s' has an indented key-shaped "
                    "line ('%s') inside a plain multi-line value: plain "
                    "scalars cannot contain key lines (invalid YAML); "
                    "use a block scalar ('|' or '>') for such content"
                    % (field, follow.strip()))
            folded.append(strip_scalar(follow.strip()))
        return " ".join(part for part in folded if part)
    return None


def frontmatter_bad_keys(fm_lines):
    """List of frontmatter keys outside the whitelist."""
    bad = []
    for line in fm_lines:
        if not line.strip() or line[0] in (" ", "\t"):
            continue
        if line.startswith("#"):
            continue
        key = line.split(":", 1)[0]
        if key not in WHITELISTED_KEYS and key not in bad:
            bad.append(key)
    return bad


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(
            "Usage: python3 scripts/validate_skill.py "
            "/path/to/<skill-directory>\n")
        return 2
    skill_dir = sys.argv[1]
    if not os.path.isdir(skill_dir):
        sys.stderr.write(
            "Usage: python3 scripts/validate_skill.py "
            "/path/to/<skill-directory>\n")
        fail("Skill directory not found: %s" % skill_dir)
        return 2
    skill_md = os.path.join(skill_dir, "SKILL.md")

    # --- Check 1: SKILL.md exists and is non-empty --------------------------
    if not os.path.isfile(skill_md) or os.path.getsize(skill_md) == 0:
        fail("SKILL.md is missing or empty at: %s" % skill_md)
        sys.stderr.write("FAILED: %d validation error(s).\n" % ERRORS)
        return 1
    ok("SKILL.md exists and is non-empty")

    with open(skill_md, "r", encoding="utf-8-sig", errors="replace") as handle:
        text = handle.read()
    lines = text.splitlines()

    # --- Check 2: frontmatter delimiters and shape --------------------------
    fm_lines, fm_error = parse_frontmatter(lines)
    if fm_error is not None:
        fail(fm_error)
        sys.stderr.write("FAILED: %d validation error(s).\n" % ERRORS)
        return 1
    ok("Frontmatter opens with '---' and is closed by a '---' line")

    # --- Check 3: whitelisted keys -------------------------------------------
    bad_keys = frontmatter_bad_keys(fm_lines)
    if bad_keys:
        fail("Unexpected frontmatter key(s): %s — allowed: %s"
             % (", ".join(bad_keys), ", ".join(WHITELISTED_KEYS)))
    else:
        ok("frontmatter keys are whitelisted")

    try:
        name = get_field(fm_lines, "name")
        desc = get_field(fm_lines, "description")
        compat = get_field(fm_lines, "compatibility")
    except FrontmatterError as exc:
        fail(str(exc))
        sys.stderr.write("FAILED: %d validation error(s).\n" % ERRORS)
        return 1

    # --- Check 4: name --------------------------------------------------------
    name_problems = []
    if not name:
        name_problems.append("Frontmatter field 'name' is missing or empty")
    else:
        if len(name) > 64:
            name_problems.append(
                "Frontmatter 'name' exceeds 64 characters: %s" % name)
        elif not NAME_PATTERN.match(name):
            name_problems.append(
                "Frontmatter 'name' must be lowercase letters, digits, and "
                "single hyphens: %s" % name)
        dir_name = os.path.basename(os.path.abspath(skill_dir))
        if name != dir_name:
            name_problems.append(
                "Frontmatter 'name' (%s) must match the skill directory "
                "name: %s" % (name, dir_name))
    if name_problems:
        for problem in name_problems:
            fail(problem)
    else:
        ok("name is valid and matches the directory name: %s" % name)

    # --- Check 5: description -------------------------------------------------
    desc_problems = []
    desc_warning = None
    if not desc:
        desc_problems.append(
            "Frontmatter field 'description' is missing or empty")
    else:
        if len(desc) > 1024:
            desc_problems.append(
                "Frontmatter 'description' exceeds 1024 characters (%d)"
                % len(desc))
        elif len(desc) > 500:
            desc_warning = (
                "description is %d characters; the recommended cross-runtime "
                "budget is 500 (the DeepSeek harness session catalog caps "
                "descriptions at 500 characters by default, "
                "catalogDescriptionMaxLength, configurable)" % len(desc))
        if "<" in desc or ">" in desc:
            desc_problems.append(
                "Frontmatter 'description' must not contain angle brackets "
                "(< or >): some runtimes render the catalog as markup")
    if desc_problems:
        for problem in desc_problems:
            fail(problem)
    elif desc_warning is not None:
        warn(desc_warning)
    else:
        ok("description is present (%d characters)" % len(desc))

    # --- Check 6: compatibility (optional) ------------------------------------
    if compat:
        if compat[0] in ("[", "{") or compat.startswith("- "):
            fail("Frontmatter 'compatibility' must be a single string, "
                 "not a list or mapping")
        elif len(compat) > 500:
            fail("Frontmatter 'compatibility' exceeds 500 characters (%d)"
                 % len(compat))
        else:
            ok("compatibility is present (%d characters)" % len(compat))

    # --- Check 7: referenced paths resolve (Ghost File Rule) -------------------
    referenced = set()
    cross_skill_refs = []
    md_files = []
    for root, dirs, files in os.walk(skill_dir):
        for file_name in sorted(files):
            if file_name.endswith(".md"):
                md_files.append(os.path.join(root, file_name))
    for md_file in sorted(md_files):
        try:
            with open(md_file, "r", encoding="utf-8-sig",
                      errors="replace") as handle:
                md_text = handle.read()
        except OSError as exc:
            fail("Could not read %s: %s" % (md_file, exc))
            continue
        for line in md_text.splitlines():
            for match in CROSS_SKILL.finditer(line):
                other = match.group(1)
                if other == name:
                    continue  # a reference to the package's own name
                if not re.search(r"installed|absent|unavailable|"
                                 r"(?:if|when) present", line):
                    cross_skill_refs.append(
                        (other, os.path.relpath(md_file, skill_dir)))
        stripped = URL_PATTERN.sub(" ", md_text)
        seen = []
        for match in LAYER_PATH.finditer(stripped):
            ref = match.group(0).rstrip(".,;:!?)]}\"'")
            if not ref or ref in seen:
                continue
            seen.append(ref)
            parts = [part for part in ref.split("/") if part]
            if ".." in parts:
                warn("%s uses a parent-relative '..' segment, which the "
                     "single-level-deep path contract forbids; it is not "
                     "existence-checked (in %s)" % (ref, md_file))
                continue
            resolved = os.path.normpath(os.path.join(skill_dir, ref))
            if len(parts) > 2:
                warn("%s nests deeper than one folder level; SKILL.md "
                     "requires single-level-deep relative paths (in %s)"
                     % (ref, md_file))
            if os.path.exists(resolved):
                referenced.add(os.path.abspath(resolved))
                if len(parts) <= 2:
                    ok("path resolves: %s (in %s)" % (ref, md_file))
            else:
                fail("Referenced path does not exist: %s (in %s)"
                     % (ref, md_file))

    # --- Check 8: SKILL.md context budget (warning only) -----------------------
    if len(lines) > 500:
        warn("SKILL.md is %d lines; keep it under 500 lines (~5k tokens) — "
             "move detail into reference files" % len(lines))

    # --- Check 9: cross-skill references carry conditional wording -------------
    if cross_skill_refs:
        for other, rel in cross_skill_refs:
            warn("cross-skill reference '%s skill' in %s carries no "
                 "conditional wording (installed, absent, unavailable, "
                 "or if/when present) on its line: state when it applies "
                 "or the fallback for its absence"
                 % (other, rel))
    else:
        ok("every cross-skill reference carries conditional wording")

    # --- Check 10: inventory drift — unreferenced files ------------------------
    unreferenced = []
    skill_md_abs = os.path.abspath(skill_md)
    for root, dirs, files in os.walk(skill_dir):
        dirs[:] = [d for d in sorted(dirs) if not d.startswith(".")]
        for file_name in sorted(files):
            if file_name.startswith("."):
                continue
            path = os.path.abspath(os.path.join(root, file_name))
            if path == skill_md_abs:
                continue
            if any(path == ref or path.startswith(ref + os.sep)
                   for ref in referenced):
                continue
            unreferenced.append(os.path.relpath(path, skill_dir))
    if unreferenced:
        for rel in unreferenced:
            warn("file referenced by no scanned Markdown file — inventory "
                 "drift: %s" % rel)
    else:
        ok("every packaged file besides SKILL.md is referenced")

    # --- Summary -----------------------------------------------------------------
    if ERRORS:
        sys.stderr.write("FAILED: %d validation error(s).\n" % ERRORS)
        return 1
    if WARNINGS:
        sys.stdout.write("VALID with %d warning(s): skill package passes "
                         "structural checks.\n" % WARNINGS)
    else:
        sys.stdout.write("VALID: skill package passes structural checks.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
