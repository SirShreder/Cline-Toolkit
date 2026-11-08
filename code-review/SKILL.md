---
name: code-review
description: Perform thorough code review — checks correctness, security, performance, readability, and test coverage. Gives actionable feedback ranked by severity. This skill is read-only: it never writes or modifies code. Use it when auditing pull requests, establishing review standards, or validating changes before or after refactoring.
---

# Code Review

This skill provides structured guidance for reviewing code thoroughly and objectively, covering correctness, security, performance, readability, and test coverage. It produces severity-ranked feedback and a verdict; it does not modify any files.

## When to Use This Skill

- Reviewing pull requests or code changes
- Establishing code review standards for a team
- Auditing code for correctness, security, or performance
- Validating changes before or after refactoring (pairs with `code-refactorer`)

## When NOT to Use This Skill

- There are no code changes to review
- The task is a design-only discussion without code
- You need to implement fixes instead of reviewing

## Read-Only Declaration

This skill is read-only. It reads code, produces findings, and issues a verdict. It never writes, modifies, or deletes any source file.

## Review Dimensions

Evaluate each changed file against these dimensions, mapped to the quality gates in `programming-rules` Section 3:

| Dimension | What to check | Source |
|-----------|--------------|--------|
| **Correctness** | Static analysis passes; no obvious bugs or logic errors | `programming-rules` §3 (static analysis) |
| **Security** | No hardcoded secrets; least privilege; safe input handling | `programming-rules` §2 (security by default) |
| **Performance** | No hot-path allocations; measure before optimizing; no N+1 or quadratic patterns | `programming-rules` §2 (boring and deterministic) |
| **Readability** | Clear names, structure self-documents, comments explain why not what | `programming-rules` §2 (comments) |
| **Test coverage** | State-changing code has happy path and failure path tests | `programming-rules` §3 (testing) |
| **Documentation parity** | Comments and help match the code; outdated comments updated | `programming-rules` §3 (documentation parity) |

## Severity Grading

| Severity | Meaning | Action required |
|----------|---------|-----------------|
| **Blocking** | Violates a hard gate; change must not merge until fixed | Must fix before approval |
| **Important** | Material risk or defect; strongly recommended to fix | Fix before approval or document exception |
| **Minor** | Polish or suggestion; does not block merge | Fix or defer at reviewer discretion |

## Output Format

```
## Code Review: <file or system>

### Summary
High-level summary of findings.

### Findings — Blocking
- [Finding] — <file>:<line> — <rationale>

### Findings — Important
- [Finding] — <file>:<line> — <rationale>

### Findings — Minor
- [Finding] — <file>:<line> — <rationale>

### Positive Observations
- What is done well — always include this section.

### Required Changes
- Must-fix items before approval. Blocking findings always appear here.

### Suggestions
- Nice-to-have improvements.

### Verdict: APPROVED / APPROVED WITH SUGGESTIONS / CHANGES REQUIRED
```

## Relationship to `code-refactorer`

- `code-review` decides **what** needs to change (verdict: CHANGES REQUIRED).
- `code-refactorer` applies **how** to change it safely — incremental, test-verified steps, each independently committable.
- After `code-refactorer` applies changes, re-run `code-review` to verify the verdict moves to APPROVED.

## Cline Workflow Notes

1. **Install location**: Copy this skill directory to `.cline/skills/code-review/` (project-level) or `~/.cline/skills/code-review/` (global)
2. **Activation**: Cline will suggest this skill when you request code review, PR auditing, or pre/post-refactoring validation
3. **Progressive loading**: Metadata is always in context; detailed review patterns load on demand via `use_skill`