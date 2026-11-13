---
name: programming-rules
description: Load for any programming, code, or development task, in addition to
  the ai-core-rules skill when it is installed. The general programming core —
  the routing layer for installed stack and task skills, and the owner of the
  all-languages standards and quality gates for tasks no skill covers.
---
# Programming Rules

Load for any programming, code, or development task, in addition to the `ai-core-rules` skill when it is installed — the assistant-level behavioral core that governs how work is done and kept honest.

## When to Use This Skill

- Any task that writes, changes, reviews, or generates code, in any language or stack
- Choosing which installed skill should own a programming task (Section 1)
- Diagnosing a rule failure in this skill, `ai-core-rules`, or an installed domain skill before changing the rule (Section 4)

## When NOT to Use This Skill

- The task involves no programming, code, or development work

## 1. Skill Routing
Two axes, checked independently:
- **Stack axis:** route to the installed domain skill whose description covers the target stack, language, framework, or toolchain, preferring the most specific.
- **Task axis:** review tasks → the `programming-code-review` skill when it is installed; it issues read-only, severity-ranked verdicts.
- **Task axis:** refactoring tasks → the `programming-code-refactorer` skill when it is installed; it applies incremental, test-verified changes.
- **Both axes match:** load both skills — the task-axis skill owns the process and the stack-axis skill owns the platform rules.
- **Exactly one axis matches:** route to the matched skill and apply any Section 2 standard the loaded skill does not already own.
- **Fallback:** no installed match on either axis → no skill owns the task, so apply the standards in Section 2 as the governing standards.

## 2. Code Generation Standards (All Languages)
- **Non-trivial (working definition):** code that spans more than one function or file, or whose behavior a reader cannot verify at a glance.
- **Complete and runnable:** no placeholders, `TODO`s, pseudo-implementations, or gaps.
- **Environment assumptions:** non-trivial code answers state OS, language/runtime version, and required modules/dependencies.
- **Usage examples:** every non-trivial code answer includes at least one usage example with expected output.
- **Input validation:** validate untrusted input at the boundary. Fail fast with actionable error messages.
- **Boring and deterministic:** prefer straightforward, deterministic solutions.
- **Idempotent infrastructure:** infrastructure and configuration code must be idempotent and safe to re-run.
- **Security by default:** never hardcode secrets (passwords, keys, tokens). Use the platform's secure credential mechanism. Assume least privilege.
- **Ecosystem conventions:** follow the target language's community style guide and standard library before writing custom code.
- **Comments:** self-documenting names and structure come first. Comments explain why — reasoning, decisions, constraints, workarounds, non-obvious logic — and never restate what the code does.
- **Doc comments:** every new non-trivial function, class, or module carries a doc comment in the language's native format (docstring, doc comment, comment-based help). Trivial members need none.
- **Comment language:** write comments in the language of the codebase's existing comments and documentation. When the codebase has none, use the language of the user's request. This choice does not relax the documentation-parity gate in Section 3.

Example (Section 2 in miniature — complete, validated, documented):

```python
def median(values):
    """Return the median of a non-empty list of numbers."""
    if not values:
        raise ValueError("values must be non-empty")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2

# median([3, 1, 2]) -> 2; median([4, 1, 3, 2]) -> 2.5
```

## 3. Quality Gates
- **Static analysis:** run the ecosystem's standard linter/analyzer before delivering code. Address all Warning and Error severity findings.
- **Testing:** state-changing code (code that writes, mutates, or persists state — database writes, file writes, external service calls) requires stated test expectations: minimum happy path plus failure path.
- **Documentation parity:** comments and help must match the code. Update them on every change. Outdated comments are worse than none.

## 4. Rule Maintenance
- **Diagnose the failure class before remediating:** A failure observed against a rule in this skill, `ai-core-rules`, or an installed domain skill triggers maintenance, not by adding more specific rules by default.
  - Rule absent → add it at the correct layer (`ai-core-rules`, this skill, or a domain skill).
  - Rule present but wrong or mis-scoped → fix the explanation itself, without adding specific commands.
  - Rule present but too permissive → narrow it by the minimal specific instance.
  - Rule present and correct but ignored → make it mechanically checkable (analyzer, exit code, harness) instead of adding prose.
																		   
