# Rubric: Grading Assertions

Read this file at grading time. Grade each assertion into the run's grading.json as follows.

- Verdict requires evidence: a verbatim quote from the output, or a file path with the location that proves it. A verdict without evidence is unresolved, and unresolved counts as failed.
- Prefer mechanical checks: if an assertion can be verified by a script, write and run the one-off script. Scripts are faster than eyeballing, reusable across iterations, and immune to motivated reasoning.
- Mark discrimination: an assertion that passes in both the with-skill and baseline configurations measures the model, not the skill. Set `discriminating` to false for it; the analyzer discards it from the verdict.
- A missing or unreadable output fails the run, not the skill: record the run as failed with the reason, fix the harness, and re-run. Distinguish skill failures from harness failures explicitly in the report.
- After grading each run directory, write its run.tsv per the schema in `references/METHOD.md` — the aggregator consumes it.
