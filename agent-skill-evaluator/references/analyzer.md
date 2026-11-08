# Rubric: Benchmark Analysis

Read this file after `scripts/aggregate_benchmark.py` produces the benchmark.

- Non-discriminating assertions (passing in every configuration) are removed from the verdict and from the next iteration's assertion set.
- High variance — a standard deviation large relative to its mean — marks a flaky case: re-run it before trusting either configuration's verdict on it.
- Weigh pass-rate gain against cost: a skill that raises pass rate while inflating tokens or duration may be a net loss. Report the tradeoff and recommend keep, fix, or drop.
- Compare against the previous iteration when one exists: a regression fails the evaluation even if absolute scores remain high.
- Assertions that fail in exactly one configuration localize the skill's effect: name them in the report, because they tell the author what the skill changed.
