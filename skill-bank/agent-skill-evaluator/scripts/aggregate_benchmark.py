#!/usr/bin/env python3
"""Benchmark aggregator for skill evaluation results (Python 3, stdlib only).

Usage:
    python3 scripts/aggregate_benchmark.py /path/to/<iteration-directory>

It is a complete Python 3 script and runs
directly with python3. No extraction, renaming, or assembly step exists.

Input: every direct subdirectory of <iteration-directory> containing a run.tsv
with records of five tab-separated fields:
    config<TAB>passed<TAB>total<TAB>tokens<TAB>duration_ms
Each line is one run record; a blank line is a malformed record. run.tsv
files are read as UTF-8 with a tolerated byte-order mark (utf-8-sig), and
CRLF line endings are normalized on read; invalid UTF-8 fails closed. Directory names are not word-split;
test-case pairing verification parses eval-<case>-<config> directory names.

Output (stdout): per config — run count, pass rate, mean ± sample standard
deviation (n - 1) of tokens and duration_ms — plus the delta between the
with_skill and baseline configs (or the first two configs found, in
discovery order, when differently named).
Warnings are printed on stdout; errors are collected and printed on stderr.

Checks:
  1. The iteration directory exists (a missing directory is an input error).
  2. At least one run.tsv is found under its direct subdirectories.
  3. Every run.tsv record has exactly 5 tab-separated fields, fields 2-5 are
     non-negative integers, passed does not exceed total, and the assertion
     total is non-zero. The aggregator fails closed: any malformed record,
     unreadable file, or missing run.tsv fails the whole run; an empty
     result set is an error, not a pass.
  4. With two or more configs, test-case pairing is verified from directory
     names (eval-<case>-<config>): a test case without a counterpart in
     every configuration produces a warning listing every such case in
     discovery order, and naming that cannot be parsed produces a warning
     instead — the evaluation contract in SKILL.md step 2 requires a
     baseline counterpart for every test case. A single configuration draws
     a warning instead of a delta: every evaluation needs a baseline.

Analysis judgments — flakiness (variance relative to mean), cross-iteration
regression comparison, and assertion discrimination — are owned by
references/analyzer.md and are intentionally not mechanized; this script
reports the mean ± sample standard deviation that the rubric needs.

Exit codes: 0 = report produced (warnings possible), 1 = input errors found,
2 = usage error.

When the documented input format or the computed metrics change, update this
file in the same step as the methodology documentation in references/.
"""

import os
import re
import sys
from math import sqrt

FIELD_COUNT = 5
NONNEGATIVE = re.compile(r"^[0-9]+$")

ERRORS = []


def fail(message):
    ERRORS.append(message)


def report_errors():
    for message in ERRORS:
        sys.stderr.write("ERROR: %s\n" % message)


def warn(message):
    sys.stdout.write("WARNING: %s\n" % message)


def mean(values):
    return sum(values) / float(len(values))


def sample_stddev(values):
    """Sample standard deviation (n - 1); 0.0 for a single value."""
    count = len(values)
    if count < 2:
        return 0.0
    avg = mean(values)
    variance = sum((value - avg) ** 2 for value in values) / (count - 1)
    return sqrt(variance)


def read_records(path):
    """Split lines of one run.tsv; fail closed on an unreadable file."""
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            text = handle.read()
    except OSError as exc:
        fail("could not read %s: %s" % (path, exc))
        return []
    except UnicodeDecodeError as exc:
        fail("%s: not valid UTF-8 (%s)" % (path, exc))
        return []
    return text.splitlines()


def note_pairing(dir_name, config, parsed_configs, case_order,
                 case_configs):
    """Record eval-<case>-<config> pairing for one record's directory."""
    marker = "-" + config
    if len(dir_name) > len(marker) and dir_name.endswith(marker):
        key = dir_name[:len(dir_name) - len(marker)]
        if key.startswith("eval-"):
            key = key[5:]
        if not key:
            return  # "eval-<config>" has no case segment; unparseable
        parsed_configs.add(config)
        if key not in case_configs:
            case_configs[key] = set()
            case_order.append(key)
        case_configs[key].add(config)


def print_report(runs, config_order):
    sys.stdout.write(
        "%-16s %5s  %7s  %s  %s\n"
        % ("config", "runs", "pass%", "tokens (mean±sd)",
           "duration_ms (mean±sd)"))
    for config in config_order:
        record = runs[config]
        count = len(record["tokens"])
        sys.stdout.write(
            "%-16s %5d  %6.1f%%  %7.0f ± %-7.0f  %7.0f ± %-7.0f\n"
            % (config, count, 100.0 * record["passed"] / record["total"],
               mean(record["tokens"]), sample_stddev(record["tokens"]),
               mean(record["durations"]),
               sample_stddev(record["durations"])))


def print_delta(runs, config_order):
    if "with_skill" in runs and "baseline" in runs:
        first, second = "with_skill", "baseline"
    else:
        first, second = config_order[0], config_order[1]
    sys.stdout.write("\nDelta (%s vs %s):\n" % (first, second))
    sys.stdout.write(
        "  pass rate:   %+.1f percentage points\n"
        % (100.0 * (runs[first]["passed"] / float(runs[first]["total"])
                    - runs[second]["passed"]
                    / float(runs[second]["total"]))))
    sys.stdout.write("  tokens:      %+.0f mean per run\n"
                     % (mean(runs[first]["tokens"])
                        - mean(runs[second]["tokens"])))
    sys.stdout.write("  duration:   %+.0f ms mean per run\n"
                     % (mean(runs[first]["durations"])
                        - mean(runs[second]["durations"])))


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(
            "Usage: python3 scripts/aggregate_benchmark.py "
            "/path/to/<iteration-directory>\n")
        return 2
    iter_dir = sys.argv[1]
    if not os.path.isdir(iter_dir):
        fail("iteration directory not found: %s" % iter_dir)
        report_errors()
        return 1
    try:
        entries = sorted(os.listdir(iter_dir))
    except OSError as exc:
        fail("could not list %s: %s" % (iter_dir, exc))
        report_errors()
        return 1
    run_files = []
    for entry in entries:
        subdir = os.path.join(iter_dir, entry)
        path = os.path.join(subdir, "run.tsv")
        if os.path.isdir(subdir) and os.path.isfile(path):
            run_files.append((path, entry))
    if not run_files:
        fail("no run.tsv files found under: %s" % iter_dir)
        report_errors()
        return 1

    runs = {}               # config -> {"passed", "total", "tokens",
                            #            "durations"}
    config_order = []       # configs in discovery order
    parsed_configs = set()  # configs with a parsed eval-dir name
    case_order = []         # unique test-case keys in discovery order
    case_configs = {}       # case key -> configs it appears in

    for path, dir_name in run_files:
        for line in read_records(path):
            fields = line.split("\t")
            if len(fields) != FIELD_COUNT:
                fail("%s: expected %d tab-separated fields, found %d"
                     % (path, FIELD_COUNT, len(fields)))
                continue
            config = fields[0]
            numbers = fields[1:]
            if not all(NONNEGATIVE.match(field) for field in numbers):
                fail("%s: fields 2-5 must be non-negative integers" % path)
                continue
            passed, total, tokens, duration = (int(field)
                                               for field in numbers)
            if passed > total:
                fail("%s: passed (%d) exceeds total (%d)"
                     % (path, passed, total))
                continue
            if total == 0:
                fail("%s: assertion total is zero" % path)
                continue
            record = runs.setdefault(config, {"passed": 0, "total": 0,
                                              "tokens": [],
                                              "durations": []})
            record["passed"] += passed
            record["total"] += total
            record["tokens"].append(tokens)
            record["durations"].append(duration)
            if config not in config_order:
                config_order.append(config)
            note_pairing(dir_name, config, parsed_configs, case_order,
                         case_configs)

    if ERRORS:
        report_errors()
        return 1
    if not config_order:
        fail("no valid runs")
        report_errors()
        return 1
    print_report(runs, config_order)
    if len(config_order) == 1:
        warn("single configuration found; no delta computed — every "
             "evaluation needs a baseline.")
        return 0
    if not case_order or len(parsed_configs) < len(config_order):
        warn("test-case pairing could not be verified from directory "
             "names (expected eval-<case>-<config>).")
    else:
        missing = [key for key in case_order
                   if len(case_configs[key]) < len(config_order)]
        if missing:
            warn("test cases without a counterpart in every "
                 "configuration: " + ", ".join(missing))
    print_delta(runs, config_order)
    return 0


if __name__ == "__main__":
    sys.exit(main())
