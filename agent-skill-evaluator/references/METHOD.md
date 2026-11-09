# Reference: Evaluation Methodology

Read this file when running an evaluation end-to-end. The workflow in SKILL.md summarizes; this file holds the schemas and procedures the steps rely on.

## Results Workspace

Put results in `<skill-name>-workspace/` as a sibling of the skill directory, organized per iteration:

```text
<skill-name>-workspace/
  iteration-1/
    eval-<descriptive-name>-with_skill/
      outputs/
      run.tsv
      grading.json
      feedback.md
    eval-<descriptive-name>-baseline/
      outputs/
      run.tsv
      grading.json
  iteration-2/
    ...
```

Name each eval directory after what it tests, not after its index, as `eval-<case>-<config>`: the aggregator's pairing verification parses that shape. Create directories as runs complete, not upfront. Keep prior iterations in place for cross-iteration comparison.

## run.tsv

Written by the grader after grading, one line of five tab-separated fields:

```text
config<TAB>passed<TAB>total<TAB>tokens<TAB>duration_ms
```

`config` is `with_skill` or `baseline` (or the snapshot's name for improvement runs). `tokens` and `duration_ms` come from the runtime's run notification where one exists; record them immediately, they are not persisted elsewhere. Where the runtime provides no notification, record 0 and note the absence in the report. The aggregator reads run.tsv as UTF-8, tolerating a leading byte-order mark and CRLF line endings.

## grading.json

One file per run directory, one entry per assertion:

```json
{
  "assertions": [
    {
      "id": "axis-labels-present",
      "description": "The chart output labels both axes",
      "check": "mechanical",
      "passed": true,
      "evidence": "outputs/chart.png opened; both axes carry labels",
      "discriminating": true
    }
  ]
}
```

## Assertion Design

Cover three classes: the user's primary goal per test case, required output formats, and the failure modes the skill exists to prevent. Write one assertion per check, with descriptive names that read clearly in a benchmark. Mark mechanically verifiable checks `mechanical` and prefer a one-off script over eyeballing. Subjective quality (style, taste) is never asserted; it goes to human comparison under the comparator rubric.

## Feedback Capture

After the human review, write `feedback.md` in each eval directory: one section per test case holding the user's comments; an empty section means acceptable. Before revising in the next iteration, read the previous iteration's `feedback.md` files and focus improvements where the feedback was specific.

## Description Optimization Loop

1. Build roughly 20 queries: half should-trigger (substantive, multi-step tasks in the skill's domain), half near-miss (adjacent tasks the skill must not claim; do not use trivially simple queries — they never trigger regardless of description quality).
2. Split the set 60/40 into train and held-out portions.
3. Run each query at least 3 times per candidate description; a query counts as a trigger only if the skill activates.
4. Revise the description from the train-set failures and re-evaluate each candidate on both portions; iterate up to 5 rounds.
5. Select the candidate by held-out trigger rate, apply it to the skill's frontmatter, and show the user before and after with the scores.

## Scale-Up and Traces

When the initial set passes with a delta that favors the skill, expand the test set with new cases and re-run; a skill perfect on known cases but weak on new ones is overfit. Before any re-run that follows a revision, re-apply the `agent-skill-architect` validation and content audit, per the re-check requirement in this skill's SKILL.md step 10. Read execution traces, not only outputs: wasted steps, redundant tool calls, and unproductive detours the skill's instructions caused are improvement targets even when the verdict passes.
