# Reference: Evaluation Frameworks and Guides

The bundled rubrics and aggregator suffice for small-scale evaluation. Use these frameworks when you need repeatable automated evaluation, model comparisons, or CI integration, and the official guides for the authoring-side methodology.

## Official authoring guides

- [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) — Test cases with realistic prompts and expected outputs, with/without-skill baseline runs, assertions graded on concrete evidence, benchmark deltas (pass rate vs. token/time cost), and the iterate loop.
- [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) — Writing trigger-optimized descriptions (imperative phrasing, user intent, explicit contexts) and testing them with trigger eval queries, near-miss negatives, trigger-rate thresholds, and a train/validation split to avoid overfitting.

## Promptfoo

- [Promptfoo documentation](https://www.promptfoo.dev/docs/intro/) — CLI and library for evaluating prompts, models, and LLM applications, with CI/CD workflows.
- [Red-team testing guide](https://www.promptfoo.dev/docs/red-team/quickstart/) — Getting started with automated security testing for generative AI applications.

Use Promptfoo when you need repeatable prompt or application evaluations, model comparisons, or security-focused red-team tests.

## Ragas

- [Ragas documentation](https://docs.ragas.io/en/stable/) — Evaluation framework documentation.
- [Agent and tool-use metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/agents/) — Includes metrics such as Tool Call Accuracy and Agent Goal Accuracy.

Use Tool Call Accuracy to assess tool selection, call order, and arguments against expected calls. Use Agent Goal Accuracy to assess whether the agent achieved the user's goal.

## TruLens

- [TruLens](https://www.trulens.org/) — Instrumentation, tracing, and evaluation for LLM applications and agents.
- [RAG Triad guide](https://www.trulens.org/getting_started/core_concepts/rag_triad/) — Explains context relevance, groundedness, and answer relevance.

Use these three measures to inspect whether retrieved context fits the query, whether the response is supported by that context, and whether the response addresses the query. The RAG Triad evaluates RAG quality; do not confuse it with agent-specific measures such as tool selection or task completion.
