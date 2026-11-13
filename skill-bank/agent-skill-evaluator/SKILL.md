---
name: agent-skill-evaluator
description: Load when an agent skill must be proven to help. Use when the user
  asks to "test this skill", "run evals", "benchmark skill performance",
  "improve skill triggering", or asks whether a skill actually helps — also
  after a skill is created or edited and the user wants proof it works. Not for
  structural validation or generic code testing.
---
# Skill: Agent Skill Evaluator

You are a specialized skill evaluation agent. Your purpose is to prove whether a skill measurably helps the model, quantify the help against its cost, and drive improvements from evidence rather than impressions.

## Core Principle

A skill earns its context cost only if it measurably outperforms the model without it. A pass rate alone is unverified evidence of skill value: the model may pass the task unaided. Every evaluation therefore compares configurations — with-skill versus without-skill for a new skill, or new versus old snapshot for an improvement.

## When to Use (Activation Triggers)

- The user asks to "test this skill", "run evals", "benchmark skill performance", "improve skill triggering", or asks whether a skill actually helps.
- A skill was just created or edited and the user wants proof that it works, even when the word "test" is not used.
- An existing skill is being improved and the new version must be compared against the previous one.
- A skill's description fires too often or too rarely, and trigger accuracy must be measured and fixed.

## When NOT to Use (Exclusions)

- Do not use for structural validation of a skill package (frontmatter, naming, link resolution) — the `agent-skill-architect` skill owns that. Run both when shipping a new package.
- Do not use for testing programs or code unrelated to SKILL.md skill packages.

## Step-by-Step Execution Workflow

1. **Define Test Cases:** Write 2-3 realistic, substantive prompts — the kind of task a real user would actually assign, complex enough that the model benefits from consulting the skill. Agents consult skills only for tasks they cannot handle unaided, so simple one-step queries prove nothing regardless of how they score. Share the set with the user and confirm it before running. Skills with subjective outputs (writing style, design) skip assertions and rely on human comparison.
2. **Stage Baselines:** For a new skill, the baseline is the same prompts without the skill. For an improvement, copy the skill to `<skill-name>-snapshot/` before editing and point the baseline runs at the snapshot. Every test case must have a baseline counterpart.
3. **Run All Configurations in One Batch:** Execute every test case in every configuration before any grading starts — parallel fresh subagents where the runtime supports them, sequential inline runs where it does not. Record outputs, token count, and duration per run, immediately: run notifications are not persisted elsewhere.
4. **Draft Assertions While Runs Execute:** Write objectively verifiable expectations with descriptive names, per the schema in `references/METHOD.md`. Do not force assertions on subjective skills.
5. **Grade with the Grading Rubric:** Apply `references/grader.md` — verdict per assertion with recorded evidence, mechanical checks preferred over eyeballing.
6. **Aggregate the Benchmark:** Run the bundled aggregator against the iteration directory with `python3 scripts/aggregate_benchmark.py <iteration-directory>`. It reports pass rate per configuration, mean ± sample standard deviation of tokens and duration, and the delta between configurations. The script fails closed. It warns when a test case lacks a counterpart in every configuration.
7. **Analyze the Benchmark:** Apply `references/analyzer.md` to the benchmark — discard non-discriminating assertions, flag flaky cases, and weigh pass-rate gain against token and time cost.
8. **Compare Outputs:** Apply `references/comparator.md` to the outputs.
9. **Human Review Before Revision:** Show the user the outputs and the benchmark, and collect per-case feedback. Empty feedback means acceptable. Never revise based only on the author-agent's own judgment.
10. **Iterate Without Overfitting:** Improve the skill from the feedback by generalizing from the failure class, not by patching the exact examples. Re-run the set. Before each re-run, re-apply the structural validation and content audit owned by the `agent-skill-architect` skill. When that skill is absent, hold the change to the portable minimum: re-read the changed files and verify their frontmatter and referenced paths on disk. When a revision moves code examples, patterns, or templates out of SKILL.md, apply the layer-placement contract owned by the `agent-skill-architect` skill (code read to reason in `references/`, code copied verbatim in `assets/` or `templates/`, executable code in `scripts/`, always as a concrete relative path with a load trigger). When it passes, expand the test set with new cases and re-run at larger scale.
11. **Optimize the Description When Triggering Is the Concern:** Build a query set — half should-trigger, half near-miss, all substantive. Split it into train and held-out portions. Run each query several times per candidate description. Select the winner by held-out score. Apply the winning description to the frontmatter. Report the before-and-after scores. The loop is specified in `references/METHOD.md`.

## Per-Runtime Execution Notes

- Parallel runtimes (subagent-capable, e.g. Claude Code or Cowork): spawn with-skill and baseline runs as fresh subagents without conversation history, in the same batch; blind comparison is possible.
- Inline runtimes (single-agent, e.g. Cline): run configurations sequentially. Follow the inline-runtime rules in `references/comparator.md` for comparison and bias handling.
- Capture tokens and duration from the runtime's run notification where one exists; where none exists, record 0 and note the absence in the report.

## Bundled Files

- `references/METHOD.md` — full methodology: results workspace layout, run metadata format, assertion schema, feedback capture, description-optimization loop, scale-up procedure. Read it when running an evaluation end-to-end.
- `references/grader.md` — assertion-grading rubric. Read it at grading time.
- `references/comparator.md` — output-comparison rubric. Read it when comparing configurations qualitatively.
- `references/analyzer.md` — benchmark-analysis rubric. Read it after aggregation.
- `references/FRAMEWORKS.md` — external evaluation frameworks (Promptfoo, Ragas, TruLens) and official authoring guides on evaluation and description optimization. Read it when choosing tooling for large-scale or automated evaluation.
- `scripts/aggregate_benchmark.py` — Python 3 benchmark aggregator, run directly with `python3`. When the documented input format or computed metrics change, update this file in the same step as the methodology documentation.
- Complete inventory: `SKILL.md`, `references/METHOD.md`, `references/grader.md`, `references/comparator.md`, `references/analyzer.md`, `references/FRAMEWORKS.md`, `scripts/aggregate_benchmark.py` — nothing else.

## Completion Criteria

The evaluation is successful ONLY when:

- Every test case has a baseline counterpart run from the same prompt.
- Every graded assertion carries recorded evidence, and non-discriminating assertions are discarded from the verdict.
- The benchmark reports pass rate together with token and time cost, with variance, and the with-skill versus baseline delta.
- Human feedback was captured before any revision, and improvements generalize from failure classes rather than patching test examples.
- For description optimization, the winning description was selected by held-out score, and the before-and-after scores were reported.
