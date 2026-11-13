---
name: programming-code-refactorer
description: Use when existing code must be restructured without changing
  behavior — from SOLID and design-pattern application to dead-code removal and
  measured performance optimization. Applies the same verified, incremental
  workflow to every c
---
# Code Refactorer

This skill provides structured guidance for refactoring code safely and effectively, covering design patterns, SOLID principles, dead code elimination, and incremental transformation workflows.

## Prerequisites

- Existing codebase to refactor
- Test suite (essential for safe refactoring)
- Version control (git) for incremental changes

## When to Use This Skill

- Restructuring code without changing behavior
- Applying design patterns to improve architecture
- Reducing technical debt and code complexity
- Eliminating dead code and unused dependencies
- Improving performance through code optimization
- Making code more maintainable and readable

## When NOT to Use This Skill

- There is no existing code to restructure — write new code directly
- The task requires a behavior change — separate it from refactoring and never mix the two
- The test suite is red — fix the failing tests first, then refactor

## Refactoring Workflow

### The Golden Rule

**Refactor in small, verified steps.** Each step should:
1. Keep all tests passing
2. Change one thing at a time
3. Be independently committable
4. Be reversible if something goes wrong
5. Be complete and runnable — no placeholder bodies in the code you write during a refactor step (teaching examples in `references/examples.md` are illustrative)

### Step-by-Step Process

```
1. IDENTIFY  → What needs to change and why?
2. TEST      → Ensure existing tests cover the behavior
3. REFACTOR  → Make one small change
4. VERIFY    → Run tests, confirm behavior unchanged
5. COMMIT    → Save the increment
6. REPEAT    → Next small change
```

### Before Starting

- [ ] Green test suite — All tests passing before you touch anything
- [ ] Adequate coverage — Critical paths have tests
- [ ] Clean git state — No uncommitted changes
- [ ] Scoped goal — "Extract validation logic from controller" not "clean up the codebase"
- [ ] Time-boxed — Refactoring can expand infinitely; set a limit

### Safety Nets

| Net | Purpose | How |
|-----|---------|-----|
| **Tests** | Verify behavior preservation | Run full suite after each change |
| **Version control** | Revert if needed | Commit after each verified step |
| **Feature flags** | Incremental rollout | New code path behind a flag |
| **Pair programming** | Second pair of eyes | Especially for complex refactors |
| **Branching** | Isolate changes | Refactor on a branch, merge when done |

## SOLID Principles

### Single Responsibility Principle (SRP)

A module should have one reason to change.

### Open/Closed Principle (OCP)

Open for extension, closed for modification.

### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types.

### Interface Segregation Principle (ISP)

No code should be forced to depend on methods it doesn't use.

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions.

## Design Patterns

When applying a design pattern or working through a SOLID principle in a code change, read `references/examples.md` for the TypeScript-illustrated form before editing.

## Dead Code Elimination

### Finding Dead Code

Use static analysis tools, IDE "Find Usages", and dependency scanners appropriate to your language and build system. Look for unused exports, unused CSS rules, unused dependencies, large files that have not changed in a long time, and git history showing files untouched for months.

### Elimination Checklist

1. **Search for references** across the project before removing anything
2. **Check for dynamic access** patterns that may hide references
3. **Check external consumers** — public APIs may be used by other projects
4. **Mark deprecated first** — add deprecation notices and log warnings
5. **Remove after a grace period** — wait one release cycle, then delete
6. **Don't comment out code** — version control retains history; commented-out code is dead code that confuses

## Performance Optimization

### Measure First

Profile before optimizing using the profiling tools appropriate to your language and runtime. Measure baseline performance, identify hot spots, and only then apply optimizations.

### Common Optimization Patterns

| Pattern | When to Apply | Impact |
|---------|--------------|--------|
| **Memoization** | Pure functions called repeatedly | Cache results → O(1) repeat calls |
| **Lazy loading** | Expensive computations not always needed | Compute on first access |
| **Batching** | Multiple similar operations | Reduce N calls to 1 |
| **Debouncing** | Frequent events (resize, input) | Execute after pause |
| **Indexing** | Repeated searches in collections | O(n) → O(1) lookups |
| **Pagination** | Large data sets | Process/display subsets |

## Common Mistakes and Stopping Conditions

### Common Refactoring Mistakes

| Mistake | Why It's Dangerous | Prevention |
|---------|-------------------|------------|
| Big bang refactor | High risk, hard to revert | Small incremental steps |
| Refactor without tests | No safety net | Write characterization tests first |
| Changing behavior + structure | Bugs hide in mixed changes | One or the other, never both |
| Renaming without find-all | Broken references | IDE refactoring tools, not manual |
| Ignoring external consumers | Breaking public API | Check all callers before changing signatures |

### When to Stop Refactoring

- Tests start failing unexpectedly → Stop, revert, investigate
- The change is no longer small → Re-evaluate scope
- You're "polishing" without measurable benefit → Ship it
- New feature work is blocked too long → Refactor later

## Tips

- Refactor on a green test suite — if tests are red, fix bugs first
- Use your IDE's refactoring tools (rename, extract method, move) — they handle references you might miss
- Read Martin Fowler's "Refactoring" catalog for the full pattern library
- If you can't write a good commit message for a refactor step, the step is too broad
- Characterization tests (tests that document current behavior) are valid even if the current behavior is imperfect — lock it down before changing it
- Flag new technical debt: `// TODO(refactor): extract validation logic` — makes it findable later
- Refactoring is not a phase — it's a continuous activity woven into feature work
- After each verified step, run the static-analysis and testing gates owned by the `programming-rules` skill when it is installed

## Testing Patterns

When planning tests for a change that touches a SOLID boundary, read `references/testing.md` for the matching test-per-principle pattern.

## Relationship to `programming-code-review`

- The `programming-code-review` skill, when it is installed, decides **what** needs to change — it issues a severity-ranked verdict.
- This skill applies **how** to change it safely — incremental, test-verified steps, each independently committable.
- After this skill applies changes, re-run the `programming-code-review` skill when it is installed to verify the verdict moves to APPROVED.
