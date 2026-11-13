# Rubric: Comparing Configurations

Read this file when comparing with-skill and baseline outputs qualitatively, after assertion grading.

- In subagent-capable runtimes, compare blind: pass the two outputs to a fresh subagent with their labels shuffled, record which it prefers, then reveal the labels. Blind comparison cancels authorship bias.
- In inline runtimes, the same agent graded its own skill: state this bias in the report and lean on objective assertions wherever they exist.
- Compare each test case on explicit dimensions: correctness against the task goal, completeness, format and template compliance, wasted effort visible in the trace (redundant calls, detours, rework), and how much of the skill's guidance the run actually followed.
- Record a verdict per test case — with_skill better, baseline better, or tie — with the deciding dimension named.
- Unexpected differences the user did not anticipate are the highest-value findings: report them prominently, because they feed the improvement step.
