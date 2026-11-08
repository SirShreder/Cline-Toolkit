#!/usr/bin/env python3
"""
Bash benchmark aggregator - Python equivalent of aggregate_benchmark.txt.

Reads tab-separated run.tsv files from subdirectories of an iteration
directory and computes per-config pass rate, mean ± stddev of tokens and
duration_ms (sample stddev with n-1 denominator), plus min/max, plus delta
between configurations.

Input: every subdirectory of <iteration-directory> containing a run.tsv with
one line of five tab-separated fields:
    config<TAB>passed<TAB>total<TAB>tokens<TAB>duration_ms

Output (stdout): per config — run count, pass rate, min/max/mean ± stddev of
tokens and duration_ms — plus the delta between the with_skill and baseline
configs (or the first two configs found, in discovery order, when differently named).

Exit codes: 0 = report produced (warnings possible), 1 = input errors found,
2 = usage error. The aggregator fails closed: any malformed or missing run.tsv
fails the whole run.
"""

import json
import math
import os
import sys


def collect_run_files(iter_dir):
    """Find all run.tsv files under subdirectories of iter_dir."""
    runfiles = []
    if not os.path.isdir(iter_dir):
        return runfiles
    for root, dirs, files in os.walk(iter_dir):
        for fn in files:
            if fn == "run.tsv":
                rel = os.path.relpath(root, iter_dir)
                depth = rel.count(os.sep) + (1 if rel != "." else 0)
                if depth == 2:
                    runfiles.append(os.path.join(root, fn))
    runfiles.sort()
    return runfiles


def parse_run_file(path):
    """Parse a single run.tsv line into (config, passed, total, tokens, duration_ms)."""
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read().strip()
    except OSError as e:
        return None, None, f"cannot read {path}: {e}"

    if not content:
        return None, None, f"{path}: empty run.tsv"

    lines = content.splitlines()
    if len(lines) != 1:
        return None, None, f"{path}: expected exactly 1 line, found {len(lines)}"

    fields = lines[0].split("\t")
    if len(fields) != 5:
        return None, None, (
            f"{path}: expected 5 tab-separated fields, found {len(fields)}"
        )

    config = fields[0]
    try:
        passed = int(fields[1])
        total = int(fields[2])
        tokens = int(fields[3])
        duration_ms = int(fields[4])
    except ValueError:
        return None, None, f"{path}: fields 2-5 must be non-negative integers"

    if passed < 0 or total < 0 or tokens < 0 or duration_ms < 0:
        return None, None, f"{path}: fields 2-5 must be non-negative integers"

    if total == 0:
        return None, None, f"{path}: assertion total is zero"

    return config, {
        "passed": passed,
        "total": total,
        "tokens": tokens,
        "duration_ms": duration_ms,
    }, None


def mean(values):
    return sum(values) / len(values) if values else 0.0


def stddev(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    var = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(var) if var > 0 else 0.0


def aggregate(iter_dir):
    """Aggregate all run.tsv files under iter_dir and print a report.

    Returns (exit_code, report_string).
    """
    errors = []
    runfiles = collect_run_files(iter_dir)

    if not runfiles:
        return 1, f"ERROR: no run.tsv files found under: {iter_dir}"

    configs = {}
    order = []

    for rf in runfiles:
        config, fields, err = parse_run_file(rf)
        if err:
            errors.append(err)
            continue
        if config not in configs:
            configs[config] = {
                "passed": 0,
                "total": 0,
                "runs": 0,
                "tokens": [],
                "duration": [],
            }
            order.append(config)
        c = configs[config]
        c["passed"] += fields["passed"]
        c["total"] += fields["total"]
        c["runs"] += 1
        c["tokens"].append(fields["tokens"])
        c["duration"].append(fields["duration_ms"])

    if errors:
        return 1, "\n".join(errors)

    if not order:
        return 1, "ERROR: no valid runs"

    lines = []
    header = (
        "{:<16} {:>5}  {:>7}  {:<22}  {:<26}".format(
            "config", "runs", "pass%",
            "tokens (min/max/mean±sd)", "duration_ms (min/max/mean±sd)"
        )
    )
    lines.append(header)

    for config in order:
        c = configs[config]
        pr = 100.0 * c["passed"] / c["total"] if c["total"] else 0.0
        mt = mean(c["tokens"])
        st = stddev(c["tokens"])
        tmin = min(c["tokens"])
        tmax = max(c["tokens"])
        md = mean(c["duration"])
        sd = stddev(c["duration"])
        dmin = min(c["duration"])
        dmax = max(c["duration"])
        lines.append(
            "{:<16} {:>5}  {:>6.1f}%  {:>4}/{:<4}/{:>6.0f} ± {:<6.0f}  {:>5}/{:<5}/{:>7.0f} ± {:<7.0f}".format(
                config, c["runs"], pr, tmin, tmax, mt, st, dmin, dmax, md, sd
            )
        )

    if len(order) == 1:
        lines.append(
            "WARNING: single configuration found; no delta computed "
            "— every evaluation needs a baseline."
        )
        return 0, "\n".join(lines)

    if "with_skill" in configs and "baseline" in configs:
        a, b = "with_skill", "baseline"
    else:
        a, b = order[0], order[1]

    ca = configs[a]
    cb = configs[b]
    delta_pass = 100.0 * ca["passed"] / ca["total"] - 100.0 * cb["passed"] / cb["total"]
    delta_tokens = mean(ca["tokens"]) - mean(cb["tokens"])
    delta_duration = mean(ca["duration"]) - mean(cb["duration"])

    lines.append("")
    lines.append(f"Delta ({a} vs {b}):")
    lines.append(f"  pass rate:   {delta_pass:+.1f} percentage points")
    lines.append(f"  tokens:      {delta_tokens:+.0f} mean per run")
    lines.append(f"  duration:   {delta_duration:+.0f} ms mean per run")

    return 0, "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python aggregate_benchmark.py /path/to/<iteration-directory>",
            file=sys.stderr,
        )
        return 2

    iter_dir = sys.argv[1]
    exit_code, report = aggregate(iter_dir)
    print(report)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())