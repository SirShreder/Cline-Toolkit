# Package Content Audit

Authoritative checklist for the post-change content audit (the content-audit step of the workflow in this skill's SKILL.md). Run it over every file affected by a change: the changed files plus their cross-reference targets. Run it after every creation, edit, or update of a skill or rules file. Do not wait for a user request to run it. Report each finding with a proposed resolution. Apply fixes only after user approval.

The audit is semantic, not mechanical. It requires the file's invariants derived in the workflow. The structural validator cannot substitute for it. The validator owns the mechanical checks: frontmatter schema, name and description constraints, link resolution. This checklist owns the checks below. Verify against the current on-disk state. Re-read the changed files before auditing. Never audit against cached or in-session content.

## Checklist

0. **Draft before edit:** Draft the full change before the first edit call; no partial or incremental edits without a complete draft.
1. **Incorrect or outdated data:** every factual claim, limit, and behavior statement matches its authoritative source; where a claim depends on changeable facts, verify it externally before accepting it.
2. **Circular references:** every reference chain terminates at one authoritative location; no loop between files.
3. **Duplicated content:** nothing restates a rule owned by another section of the package; other files may reference the owning location, never restate it.
4. **Conflicting rules:** no two rules inside the change set contradict each other.
5. **Missing required sections:** the file contains every section its contract requires.
6. **Ambiguous wording:** every rule has exactly one reading; no indefinite referents or undefined terms.
6a. **Define gating terms:** every gating term that triggers an obligation is defined inline or by one reference hop; an undefined gating term is the highest-severity defect class.
7. **Overlapping responsibilities:** the skill's scope and activation triggers do not overlap another skill's; duplicate task ownership is a finding.
8. **Priority and order conflicts:** rule priorities and workflow step ordering stay consistent; resolve any conflict by the priority chain — the more specific rule wins, and a still-ambiguous case goes to the user — never by restating the other rule.
9. **Unused or dead content:** no orphaned bullets, unused enumerations, or content that no instruction or step references.
10. **Formatting and schema errors:** markdown structure, YAML frontmatter, and directory layout follow their contracts.
11. **Contradictions with higher-priority rules:** nothing in the change contradicts a higher-priority rule or instruction.
12. **Outdated examples and instructions:** examples reflect current syntax and behavior; content the change obsoleted is updated or deleted, and references to deleted content are removed, not repaired.
13. **Scope:** scope the skill like a function — too narrow forces multiple skills to load for one task, too broad prevents precise activation; the unit of work is coherent.
14. **One task per section:** no section covers more than one type of task; split compound sections.
15. **One instruction per sentence:** every sentence issues exactly one directive — a sentence the agent could misread as two different actions is a defect. A labeled rule cluster that groups several one-directive sentences under one bold label is the expected pattern, not a defect.
15b. **Sentence length:** every sentence stays under about thirty words; sentences longer than thirty words are split into multiple directives.
16. **Cross-reference accuracy:** every cross-reference — file path, section number, step number — matches its current target; a reference left stale by renumbering or moving is a finding (the validator proves path existence; this check proves the target is the intended one).
17. **Unnecessary cross-references:** replace a cross-reference with short self-contained guidance where the target does not own the rule; reference only what another file owns.
18. **Version references:** files contain no specific product or model version numbers unless the user requested them directly; generalize to version-independent phrasing. Exception: version facts that document a runtime or tool the user explicitly targets are compatibility facts, not stale-prone claims — keep them where they carry load-bearing information.
19. **Description-to-body fidelity:** every trigger context in the frontmatter description corresponds to a capability the body actually performs, every major body capability is reachable from at least one description trigger, and the description's exclusions match the body's exclusions section.
20. **External references and dependencies:** every external link, tool, or skill the package names carries a stated purpose and traces to an official source or a dependency present in the environment. An external reference the change set cannot verify is a finding.

## Layer Ownership

- Runtime- or product-specific references stay out of environment-independent files.
- Bundled code lives in the layer matching the agent's use of it: code read to reason in `references/`, code copied verbatim into output in `assets/` (`templates/` in Cline layouts), executable code in `scripts/`; no package introduces a top-level folder outside the documented layouts.
- An instruction to place content in a separate file names that file as a concrete relative path with a load trigger; an unspecified "separate file" pointer is a finding.
- An enforcement mechanism (an analyzer, exit code, or harness) is named only in the layer that owns it; an environment-independent file states the principle, and the rule moves to the owning layer even when its principle reads as general.
- Frontmatter descriptions contain no summary enumerations; trigger phrasing is exempt — trigger phrasing names when to load (user intents, task shapes, gerunds of requests), while capability clauses (what the skill does — routes, holds, validates) are summary enumerations.

## Reporting

Classify each finding against defined severities:

- **High:** a rule is unenforceable or broken (an undefined gating term, a looping reference chain, an unreachable required element).
- **Medium:** a rule conflicts with another rule, has two live readings, or restates another owner's content.
- **Low:** a wording or terminology improvement that does not affect enforceability.
- **Do not inflate severity:** do not upgrade a finding's severity beyond its definition; a Low finding stays Low regardless of emotional emphasis.

Report every finding with its file, its location, a verbatim quote of the on-disk evidence, and a proposed resolution. A claim about content that does not exist on disk is a report defect.

An ambiguity finding states both readings and why an agent would plausibly take the unintended one. An unlikely parse is not a finding.

Return a rejected or settled finding only with new evidence. A re-carry without new evidence is itself a report defect.

An empty report means the audit passed.
