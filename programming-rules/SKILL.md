---
name: programming-rules
description: Load for any programming, code, or development task, in addition to
  ai-core-rules. The general programming core — it routes each task to the
  installed skill covering its stack or task type, and it holds the
  all-languages standards and quality gates that apply when no skill does,
  together with the upkeep of these rules.
---
# Programming Rules

Load for any programming, code, or development task, in addition to the `ai-core-rules` skill when it is installed.

## 1. Skill Routing
Two axes, checked independently:
- **Stack axis:** route to the installed skill whose description covers the target stack, language, framework, or toolchain, preferring the most specific.
- **Task axis:** review tasks → the `programming-code-review` skill when it is installed; it issues read-only, severity-ranked verdicts.
- **Task axis:** refactoring tasks → the `programming-code-refactorer` skill when it is installed; it applies incremental, test-verified changes.
- **Fallback:** no installed match on either axis → apply the standards in Section 2.

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
- **Comment language:** write comments in the language of the codebase's existing comments and documentation. When the codebase has none, use the language of the user's request. Documentation parity is owned by the Section 3 gate.

## 3. Quality Gates
- **Static analysis:** run the ecosystem's standard linter/analyzer before delivering code. Address all Warning and Error severity findings.
- **Testing:** state-changing code requires stated test expectations: minimum happy path plus failure path.
- **Documentation parity:** comments and help must match the code. Update them on every change. Outdated comments are worse than none.

## 4. Rule Maintenance
- **Diagnose the failure class before remediating:** A failure observed against a rule in this skill set triggers maintenance, not specificity by default.
  - Rule absent → add it at the correct layer (`ai-core-rules`, this skill, or a domain skill).
  - Rule present but wrong or mis-scoped → fix the explanation itself, without adding specific commands.
  - Rule present but too permissive → narrow it by the minimal specific instance.
  - Rule present and correct but ignored → make it mechanically checkable (analyzer, exit code, harness) instead of adding prose.
- Command-level specifics are the remedy only for the too-permissive class.
