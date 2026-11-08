# Package Content Audit

Authoritative checklist for the post-change content audit (the content-audit step of the workflow in this skill's SKILL.md). Run it over every file affected by a change — the changed files plus their cross-reference targets — after every creation, edit, or update of a skill or rules file. Do not wait for a user request to run it. Report the findings with a proposed resolution per finding, and apply fixes only after user approval.

The audit is semantic, not mechanical: it requires the file's invariants derived in the workflow, and the structural validator cannot substitute for it. The structural validator owns the mechanical checks (frontmatter schema, name and description constraints, link resolution); this checklist owns the checks below. Verify against the current on-disk state, re-reading the changed files before auditing, never against cached or in-session content.

## Checklist

1. **Incorrect or outdated data:** every factual claim, limit, and behavior statement matches its authoritative source; where a claim depends on changeable facts, verify it externally before accepting it (per the anti-hallucination rules in `ai-core-rules` Section 3).
2. **Circular references:** every reference chain terminates at one authoritative location; no loop between files (per `ai-core-rules` Section 1).
3. **Duplicated content:** nothing restates a rule owned by another section or skill; other files may reference the owning location, never restate it.
4. **Conflicting rules:** no two rules inside the change set contradict each other.
5. **Missing required sections:** the file contains every section its contract requires.
6. **Ambiguous wording:** every rule has exactly one reading; no indefinite referents or undefined terms.
7. **Overlapping responsibilities:** the skill's scope and activation triggers do not overlap another skill's; duplicate task ownership is a finding.
8. **Priority and order conflicts:** rule priorities and workflow step ordering stay consistent; resolve any conflict per the priority chain in `ai-core-rules` Section 7, never by restating the other rule.
9. **Unused or dead content:** no orphaned bullets, unused enumerations, or content that no instruction or step references.
10. **Formatting and schema errors:** markdown structure, YAML frontmatter, and directory layout follow their contracts.
11. **Contradictions with higher-priority rules:** nothing in the change contradicts a higher-priority rule or instruction.
12. **Outdated examples and instructions:** examples reflect current syntax and behavior; content the change obsoleted is updated or deleted, and references to deleted content are removed, not repaired.
13. **Scope:** scope the skill like a function — too narrow forces multiple skills to load for one task, too broad prevents precise activation; the unit of work is coherent.
14. **One task per section:** no section covers more than one type of task; split compound sections.
15. **One instruction per sentence:** no sentence or bullet combines multiple tasks or instructions; split compound directives — a sentence the agent could misread as two different actions is a defect.
16. **Cross-reference accuracy:** every cross-reference — file path, section number, step number — matches its current target; a reference left stale by renumbering or moving is a finding (the validator proves path existence; this check proves the target is the intended one).
17. **Unnecessary cross-references:** replace a cross-reference with short self-contained guidance where the target does not own the rule; reference only what another file owns.
18. **Version references:** files contain no specific product or model version numbers unless the user requested them directly; generalize to version-independent phrasing. Exception: version facts that document a runtime or tool the user explicitly targets are compatibility facts, not stale-prone claims — keep them where they carry load-bearing information.
19. **Description-to-body fidelity:** every trigger context in the frontmatter description corresponds to a capability the body actually performs, every major body capability is reachable from at least one description trigger, and the description's exclusions match the body's exclusions section.

## Layer Ownership

- Runtime- or product-specific references stay out of environment-independent files.
- Bundled code lives in the layer matching the agent's use of it: code read to reason in `references/`, code copied verbatim into output in `assets/` (`templates/` in Cline layouts), executable code in `scripts/`; no package introduces a top-level folder outside the documented layouts.
- An instruction to place content in a separate file names that file as a concrete relative path with a load trigger; an unspecified "separate file" pointer is a finding.
- An enforcement mechanism (an analyzer, exit code, or harness) is named only in the layer that owns it; an environment-independent file states the principle, and the rule moves to the owning layer even when its principle reads as general.
- Frontmatter descriptions contain no enumerations.

## Reporting

Classify each finding high, medium, or low. Report every finding with its file, its location, and a proposed resolution. An empty report means the audit passed.
