#!/usr/bin/env python3
"""Fixture harness for the bundled structural validator (Python 3, stdlib only).

Usage:
    python3 scripts/selftest_skill.py

It is a complete Python 3 script and runs
directly with python3. No extraction, renaming, or assembly step exists.

For every check the validator's header lists, this harness ships at least
one positive fixture (must pass) and one negative fixture (must fail), and
one fixture for every parser shape the header documents. Fixtures are
generated in a temporary directory at run time and removed afterwards; the
harness never touches this skill package. When a check or parser shape
changes, change the fixtures that pin it in the same step (sync contract,
SKILL.md step 11).

Fixture map (fixture name -> pinned behavior):
    valid-minimal         checks 1, 3, 4, 5, 6 positive; no warnings
    missing-skill-md      check 1 negative: no SKILL.md
    empty-skill-md        check 1 negative: zero-byte SKILL.md
    unopened-frontmatter  check 2 negative: missing closing '---'
    prose-in-frontmatter  check 2 negative: prose between the delimiters
    extra-key             check 3 negative: non-whitelisted key
    uppercase-name        check 4 negative: non-kebab-case name
    name-dir-mismatch     check 4 negative: name differs from the directory
    long-description      check 5 negative: over 1024 characters
    bracket-description   check 5 negative: angle brackets
    wide-description      check 5 warning: 501-1024 characters
    block-scalar-name     parser: '|' block scalar folds
    block-scalar-strip    parser: '|-' block scalar folds
    folded-scalar        parser: '>' folded scalar folds
    folded-scalar-strip  parser: '>-' folded strip indicator folds
    indent-indicator      parser: '|2' accepted, indicator digits ignored
    quoted-description    parser: double-quoted scalar
    single-quoted         parser: single-quoted scalar
    quoted-pipe           parser: a quoted '|' scalar is not a block scalar;
                          its key-shaped continuation fails closed
    multiline-plain       parser: plain multi-line value folds
    trailing-comment      parser: ' #' trailing comment is stripped
    crlf-file             parser: CRLF line endings normalized
    bom-file              parser: leading byte-order mark tolerated
    keyline-continuation  parser: key-shaped line inside a plain multi-line
                          value fails closed
    compat-flow-list      check 6 negative: flow-style list
    compat-block-list     check 6 negative: block-style list
    compat-long           check 6 negative: over 500 characters
    missing-reference     check 7 negative: referenced path does not exist
    parent-relative       check 7 warning: '..' segment
    deep-nested           check 7 warning: deeper than one folder level
    line-budget           check 8 warning: over 500 lines
    cross-skill-ok        check 9 positive: conditional wording present
    cross-skill-warn      check 9 warning: conditional wording missing
    cross-skill-unavailable   check 9 positive: 'unavailable' and
                          'when present' conditionals accepted
    self-reference-ok     check 9: the package's own name is skipped
    unreferenced-file     check 10 warning: file referenced by no Markdown

Fail-closed: the harness exits 0 only when every fixture produces the
documented exit code and output; any mismatch exits 1. The validator
prints warnings on stderr, so warning fixtures assert on stderr.
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATOR = os.path.join(HERE, "validate_skill.py")

CASES = []


def write(path, content, encoding="utf-8"):
    with open(path, "w", encoding=encoding, newline="") as handle:
        handle.write(content)


def case(name, exit_code, build, err_has=(), err_lacks=(),
         out_has=(), out_lacks=()):
    CASES.append((name, exit_code, build, list(err_has), list(err_lacks),
                  list(out_has), list(out_lacks)))


def mkdirs(base, *parts):
    path = os.path.join(base, *parts)
    os.makedirs(path)
    return path


def build_valid(d):
    mkdirs(d, "references")
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: valid-minimal\n"
          "description: Trigger for the minimal valid package.\n"
          "compatibility: Any runtime that reads plain text.\n"
          "---\n\n"
          "# Valid Skill\n\n"
          "Read references/guide.md when details are needed.\n")
    write(os.path.join(d, "references", "guide.md"), "# Guide\n")


def build_missing(d):
    pass  # empty directory: no SKILL.md at all


def build_empty(d):
    write(os.path.join(d, "SKILL.md"), "")


def build_unopened(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: unopened-frontmatter\n"
          "description: Trigger.\n")


def build_prose(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: prose-in-frontmatter\n"
          "this line is prose\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n")


def build_extra_key(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: extra-key\n"
          "visibility: true\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n")


def build_uppercase(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: Uppercase-Skill\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n")


def build_mismatch(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: other-skill\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n")


def build_long_description(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: long-description\n"
          "description: %s\n"
          "---\n\n"
          "# Body\n" % ("word " * 210))


def build_bracket_description(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: bracket-description\n"
          "description: Uses <tags> in output.\n"
          "---\n\n"
          "# Body\n")


def build_wide_description(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: wide-description\n"
          "description: %s\n"
          "---\n\n"
          "# Body\n" % ("word " * 120))


def build_block_scalar_name(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: |\n"
          "  block-scalar-name\n"
          "description: Trigger for block scalars.\n"
          "---\n\n"
          "# Body\n")


def build_block_scalar_strip(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: |-\n"
          "  block-scalar-strip\n"
          "description: Trigger for strip indicators.\n"
          "---\n\n"
          "# Body\n")


def build_folded_scalar(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: folded-scalar\n"
          "description: >\n"
          "  Trigger for folded scalars.\n"
          "---\n\n"
          "# Body\n")


def build_folded_strip(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: folded-scalar-strip\n"
          "description: >-\n"
          "  Trigger for the folded strip indicator.\n"
          "---\n\n"
          "# Body\n")


def build_indent_indicator(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: |2\n"
          "  indent-indicator\n"
          "description: Trigger for indentation indicators.\n"
          "---\n\n"
          "# Body\n")


def build_quoted_description(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: quoted-description\n"
          'description: "Double quoted trigger with inner text."\n'
          "---\n\n"
          "# Body\n")


def build_single_quoted(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: single-quoted\n"
          "description: 'Single quoted trigger.'\n"
          "---\n\n"
          "# Body\n")


def build_quoted_pipe(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: quoted-pipe\n"
          'description: "| quoted pipe"\n'
          "  license: MIT\n"
          "---\n\n"
          "# Body\n")


def build_multiline_plain(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: multiline-plain\n"
          "description: Trigger that continues\n"
          "  on a folded second line\n"
          "---\n\n"
          "# Body\n")


def build_trailing_comment(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: trailing-comment\n"
          "description: Trigger comment case # spec reference\n"
          "---\n\n"
          "# Body\n")


def build_crlf(d):
    write(os.path.join(d, "SKILL.md"),
          "---\r\n"
          "name: crlf-file\r\n"
          "description: Trigger for CRLF.\r\n"
          "---\r\n\r\n"
          "# Body\r\n")


def build_bom(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: bom-file\n"
          "description: Trigger for a byte-order mark.\n"
          "---\n\n"
          "# Body\n",
          encoding="utf-8-sig")


def build_keyline(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: keyline-continuation\n"
          "description: Trigger that continues\n"
          "  license: MIT\n"
          "---\n\n"
          "# Body\n")


def build_compat_flow(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: compat-flow-list\n"
          "compatibility: [claude code, cline]\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n")


def build_compat_block(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: compat-block-list\n"
          "compatibility:\n"
          "  - claude code\n"
          "  - cline\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n")


def build_compat_long(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: compat-long\n"
          "compatibility: %s\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n" % ("x" * 501))


def build_missing_reference(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: missing-reference\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n\n"
          "Read references/missing.md first.\n")


def build_parent_relative(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: parent-relative\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n\n"
          "See ../references/outside.md for the shared rule.\n")


def build_deep_nested(d):
    mkdirs(d, "references", "deep")
    write(os.path.join(d, "references", "deep", "file.md"), "# Deep\n")
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: deep-nested\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n\n"
          "Read references/deep/file.md when needed.\n")


def build_line_budget(d):
    body = "\n".join("Filler line %d." % index for index in range(500))
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: line-budget\n"
          "description: Trigger.\n"
          "---\n\n"
          "%s\n" % body)


def build_cross_skill_ok(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: cross-skill-ok\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n\n"
          "Defer to the `agent-skill-evaluator` skill when it is installed "
          "in the runtime.\n")


def build_cross_skill_warn(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: cross-skill-warn\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n\n"
          "The `agent-skill-evaluator` skill benchmarks this package.\n")


def build_cross_skill_unavailable(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: cross-skill-unavailable\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n\n"
          "Defer to the `agent-skill-evaluator` skill when it is "
          "unavailable in the runtime. The `agent-skill-architect` "
          "skill, when present, adds checks.\n")


def build_self_reference(d):
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: self-reference-ok\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n\n"
          "The `self-reference-ok` skill is this package.\n")


def build_unreferenced(d):
    mkdirs(d, "scripts")
    write(os.path.join(d, "scripts", "orphan.py"), "# Orphan\n")
    write(os.path.join(d, "SKILL.md"),
          "---\n"
          "name: unreferenced-file\n"
          "description: Trigger.\n"
          "---\n\n"
          "# Body\n")


case("valid-minimal", 0, build_valid,
     out_has=("VALID: skill package passes", "compatibility is present"),
     err_lacks=("WARNING",))
case("missing-skill-md", 1, build_missing, err_has=("SKILL.md is missing",))
case("empty-skill-md", 1, build_empty, err_has=("SKILL.md is missing",))
case("unopened-frontmatter", 1, build_unopened, err_has=("never closed",))
case("prose-in-frontmatter", 1, build_prose,
     err_has=("non-frontmatter content",))
case("extra-key", 1, build_extra_key, err_has=("Unexpected frontmatter key",))
case("uppercase-name", 1, build_uppercase, err_has=("must be lowercase",))
case("name-dir-mismatch", 1, build_mismatch,
     err_has=("must match the skill directory",))
case("long-description", 1, build_long_description,
     err_has=("exceeds 1024",))
case("bracket-description", 1, build_bracket_description,
     err_has=("angle brackets",))
case("wide-description", 0, build_wide_description,
     err_has=("WARNING",), out_has=("VALID with",))
case("block-scalar-name", 0, build_block_scalar_name,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("block-scalar-strip", 0, build_block_scalar_strip,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("folded-scalar", 0, build_folded_scalar,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("folded-scalar-strip", 0, build_folded_strip,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("indent-indicator", 0, build_indent_indicator,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("quoted-description", 0, build_quoted_description,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("single-quoted", 0, build_single_quoted,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("quoted-pipe", 1, build_quoted_pipe, err_has=("key-shaped",))
case("multiline-plain", 0, build_multiline_plain,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("trailing-comment", 0, build_trailing_comment,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("crlf-file", 0, build_crlf,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("bom-file", 0, build_bom,
     out_has=("VALID: skill package passes",), err_lacks=("WARNING",))
case("keyline-continuation", 1, build_keyline, err_has=("key-shaped",))
case("compat-flow-list", 1, build_compat_flow,
     err_has=("not a list or mapping",))
case("compat-block-list", 1, build_compat_block,
     err_has=("not a list or mapping",))
case("compat-long", 1, build_compat_long, err_has=("exceeds 500",))
case("missing-reference", 1, build_missing_reference,
     err_has=("does not exist",))
case("parent-relative", 0, build_parent_relative,
     err_has=("parent-relative",))
case("deep-nested", 0, build_deep_nested, err_has=("deeper than one",))
case("line-budget", 0, build_line_budget, err_has=("500 lines",))
case("cross-skill-ok", 0, build_cross_skill_ok, err_lacks=("cross-skill",))
case("cross-skill-warn", 0, build_cross_skill_warn, err_has=("cross-skill",))
case("cross-skill-unavailable", 0, build_cross_skill_unavailable,
     err_lacks=("cross-skill",))
case("self-reference-ok", 0, build_self_reference,
     err_lacks=("cross-skill",))
case("unreferenced-file", 0, build_unreferenced,
     err_has=("referenced by no scanned Markdown file",))


def run_fixture(root, name, exit_code, build,
                err_has, err_lacks, out_has, out_lacks):
    fixture_dir = os.path.join(root, name)
    os.makedirs(fixture_dir)
    build(fixture_dir)
    try:
        proc = subprocess.run(
            [sys.executable, VALIDATOR, fixture_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as exc:
        return ["could not run the validator: %s" % exc]
    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")
    problems = []
    if proc.returncode != exit_code:
        problems.append("exit code %d (expected %d)"
                        % (proc.returncode, exit_code))
    for needle in err_has:
        if needle not in err:
            problems.append("stderr lacks %r" % needle)
    for needle in err_lacks:
        if needle in err:
            problems.append("stderr has %r" % needle)
    for needle in out_has:
        if needle not in out:
            problems.append("stdout lacks %r" % needle)
    for needle in out_lacks:
        if needle in out:
            problems.append("stdout has %r" % needle)
    return problems


def main():
    if not os.path.isfile(VALIDATOR):
        sys.stderr.write("Validator not found beside this harness: %s\n"
                         % VALIDATOR)
        return 1
    root = tempfile.mkdtemp(prefix="validator-selftest-")
    failed = 0
    try:
        for (name, exit_code, build,
             err_has, err_lacks, out_has, out_lacks) in CASES:
            problems = run_fixture(root, name, exit_code, build,
                                   err_has, err_lacks, out_has, out_lacks)
            if problems:
                failed += 1
                sys.stderr.write("FIXTURE FAILED: %s: %s\n"
                                 % (name, "; ".join(problems)))
            else:
                sys.stdout.write("FIXTURE OK: %s\n" % name)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    if failed:
        sys.stderr.write("SELFTEST FAILED: %d of %d fixtures misbehaved.\n"
                         % (failed, len(CASES)))
        return 1
    sys.stdout.write("SELFTEST PASSED: %d fixtures behave as documented.\n"
                     % len(CASES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
