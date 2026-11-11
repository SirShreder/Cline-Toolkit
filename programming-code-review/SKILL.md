---
name: programming-code-review
description: Perform thorough, read-only code review of code changes. Use when
  code changes must be reviewed or audited before merging, or when review
  standards are established.
---
# Code Review

This skill provides structured guidance for reviewing code thoroughly and objectively, covering correctness, security, performance, readability, test coverage, and documentation parity. It produces severity-ranked feedback and a verdict.

## When to Use This Skill

- Reviewing pull requests or code changes
- Establishing code review standards for a team
- Auditing code for correctness, security, or performance
- Validating changes before or after refactoring (pairs with `programming-code-refactorer` when it is installed)

## When NOT to Use This Skill

- There are no code changes to review
- The task is a design-only discussion without code
- You need to implement fixes instead of reviewing

## Read-Only Declaration

This skill is read-only. It reads code, produces findings, and issues a verdict. It never writes, modifies, or deletes any source file.

## Review Dimensions

Evaluate each changed file against these dimensions, mapped to the standards (§2) and quality gates (§3) in `programming-rules`:

| Dimension | What to check | Source |
|-----------|--------------|--------|
| **Correctness** | Static analysis passes; no obvious bugs or logic errors | `programming-rules` §3 (static analysis) |
| **Security** | No hardcoded secrets; least privilege; safe input handling | `programming-rules` §2 (security by default) |
| **Performance** | No hot-path allocations; measure before optimizing; no N+1 or quadratic patterns | Review-local — no upstream rule |
| **Readability** | Clear names, structure self-documents, comments explain why not what | `programming-rules` §2 (comments) |
| **Test coverage** | State-changing code has happy path and failure path tests | `programming-rules` §3 (testing) |
| **Documentation parity** | Comments and help match the code; outdated comments updated | `programming-rules` §3 (documentation parity) |

## Severity Grading

| Severity | Meaning | Action required |
|----------|---------|-----------------|
| **Blocking** | Violates a hard gate — a security defect, or a `programming-rules` §3 gate (static analysis, testing, documentation parity); the change must not merge until fixed | Must fix before approval |
| **Important** | Material risk or defect; strongly recommended to fix | Fix before approval or document exception |
| **Minor** | Polish or suggestion; does not block merge | Fix or defer at reviewer discretion |

## Output Format

Copy and fill `assets/verdict-template.md` for each review. Section order: Summary; Findings — Blocking, Important, Minor (one per line with file:line and rationale); Positive Observations (always include this section); Required Changes (blocking findings always appear here); Suggestions; Verdict: APPROVED / APPROVED WITH SUGGESTIONS / CHANGES REQUIRED.

## Relationship to `programming-code-refactorer`

- This skill decides **what** needs to change (verdict: CHANGES REQUIRED).
- The `programming-code-refactorer` skill, when it is installed, applies **how** to change it safely — incremental, test-verified steps, each independently committable.
- After refactoring completes, re-run this skill to verify the verdict moves to APPROVED.
