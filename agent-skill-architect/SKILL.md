---
name: agent-skill-architect
description: Use this skill whenever the user asks for work on an agent skill
  (SKILL.md package) or rules file itself — creating one, checking or changing
  an existing one, or fitting one to a target runtime so it works across AI
  models or agent runtimes. Not for generic standalone application code,
  database schemas, or registry mechanics such as deleting skills.
---
# Skill: Agent Skill Architect

You are a specialized Meta-AI Agent Skill Architect. Your purpose is to design, format, and structure clean, deterministic AI Agent Skills (`SKILL.md`) that are optimized for production-grade routing, robust error handling, and automated evaluation.

## When to Use (Activation Triggers)

- The user asks to "create a new skill", "write an agent capability", or "structure a skill directory".
- The user asks to update, review, or validate an existing skill or rules file — derive its invariants before editing (step 3 of the workflow).
- The user asks to adopt, import, or adapt an already-created skill to a target runtime — derive its invariants (step 3), validate the package (step 8), verify cross-runtime compatibility (step 10), and adapt its references to the named runtime.
- Building modular prompt and tool packages for skills-compatible agent runtimes.
- Checking whether a skill works across different AI models or agent runtimes (Claude Code, Mistral Vibe, ChatGPT/Codex, DeepSeek tooling, Cline) — read `references/RUNTIMES.md` for the per-vendor compatibility rules.

## When NOT to Use (Exclusions)

- Do not use for writing generic standalone application code or database schemas unrelated to LLM runtime skill orchestration.
- Do not use for deleting skills or other registry mechanics — those operations are outside this skill's scope.

## Step-by-Step Execution Workflow

1. **Analyze Requirements & Ground in Real Expertise:** Parse the user's prompt. If the prompt lacks domain detail, ask for source material — a real task transcript with the corrections the user made, runbooks, API specs, or code-review comments; generic LLM knowledge produces vague, low-value skills. If the request does not name the target runtime or environment, ask the user to name it before generating anything. When the user leaves the choice open, default to the current runtime as the named target, stating that choice in the response; encode it in frontmatter only when the user asks. Before authoring a new skill from scratch, search the skill sources listed in `references/REFERENCE.md` for an already-prepared candidate; when one fits, adapt it (steps 3, 8, and 10) instead of creating a new package, after verifying its license and maintenance state.
2. **Read Governing References Before Generating:** Before generating anything, read the input contract guidelines and format requirements from `references/REFERENCE.md` in this skill directory. Read the per-runtime rules for the target runtime(s) from `references/RUNTIMES.md` in the same step — vendor rules (name matching, token budgets, subfolder layouts) apply at generation time even for single-runtime targets, not only in the step 10 cross-runtime check.
3. **Derive Invariants of Existing Skills:** When the task edits or adopts an existing skill or rules file rather than creating one, first derive its invariants from its current content — abstraction level (portable principles vs runtime-specific instances), scope boundaries (which runtimes, products, or layers it may name), and its description's length class (defined in the cross-runtime checklist in `references/RUNTIMES.md`) — and preserve them: new content must match the file's layer, not the source transcript's specificity. Adoption composes this step with validation (step 8) and cross-runtime compatibility (step 10). Treat the target runtime as the named runtime.
4. **Compose Edits Against On-Disk State:** Compose every edit against the file's current on-disk state, re-reading it in the session — a previously loaded skill block or a conversation rendering may be stale or normalized, so exact-match edits composed against it fail, and full-file writes composed against it revert concurrent changes. After applying each edit, verify the write landed byte-exact before moving on: confirm the new content is present, the old content is gone, and the line count or hash matches the expectation — a write can silently drop or normalize content, and an unverified write is an unapplied edit.
5. **Scaffold Directory Structure:** Create the mandatory root folder. Check the filesystem to prevent structural collisions (do not overwrite an existing skill unless the user asked for an update).
6. **Generate YAML Frontmatter:** Construct valid metadata fields following strict string, character, and hyphen naming constraints (skill `name` must be lowercase, hyphenated). Write the `description` as trigger metadata, not a summary: imperative phrasing ("Use this skill when…"), user intent rather than implementation, explicit trigger contexts including cases where the user does not name the domain, and explicit exclusions. Keep it to a few sentences up to a short paragraph, and as short as possible, within the cross-runtime description limits — the cross-runtime compatibility checklist in `references/RUNTIMES.md` owns them. When editing an existing skill, never grow its description beyond its original length class (defined in the cross-runtime checklist in `references/RUNTIMES.md`). Trim enumerations that merely summarize the body.
7. **Write the Body & Link Downstream Resources:** Keep SKILL.md under 500 lines and roughly 5,000 tokens — only what the agent needs on every run. Apply the cut test to every rule: would the agent get it wrong without this instruction? If not, cut it. Omit what the agent already knows. Prefer concise, stepwise guidance with a working example over exhaustive documentation. Use single-level-deep relative paths (e.g. `references/REFERENCE.md`, `scripts/validate_skill.py`) to bind required execution blocks. Give each reference file a conditional load trigger — read it when a specific situation arises — rather than a generic pointer. Any instruction to move detail into a separate file must instantiate that file as a concrete relative path (e.g. a `patterns.md` file under the generated package's `references/` folder) with its load trigger — an unspecified "separate file" pointer is a defect.
8. **Validate Capability Package:** Run a structural validation pass on the finished package — use the environment's native skill-validation mechanism when one exists (the cross-agent analyzer is described in `references/REFERENCE.md`); otherwise run this skill's bundled structural validator: `python3 scripts/validate_skill.py <skill-directory>`. A native mechanism substitutes for the bundled validator only when it covers every check the bundled validator performs. When it does not, run the bundled validator for the uncovered checks. The bundled validator checks whitelisted frontmatter keys (name, description, license, allowed-tools, metadata, compatibility — any other key fails), name and description constraints (kebab-case naming, name/directory match, description length limits, no angle brackets), the optional compatibility field (single string, at most 500 characters), Ghost File Rule link resolution across the `references/`, `scripts/`, `assets/`, `docs/`, and `templates/` layouts, and prints cross-runtime warnings (description over 500 characters for the DeepSeek harness catalog cap, SKILL.md over 500 lines, referenced paths that use parent-relative '..' segments, which skip existence checking, or nest deeper than one level) and consistency warnings (a cross-skill reference without conditional wording on its line, a package file referenced by no scanned Markdown file). For a rules file (a non-SKILL.md rule document that a runtime loads as standing rules), the bundled validator does not apply — its checks assume a SKILL.md package. Validate a rules file by inspection: apply the Ghost File Rule to its cited paths and check conditional wording on its tool mentions; the content audit in step 9 applies unchanged. Run validation on every edit, not only on initial creation: a post-edit run catches scope violations the editing pass introduced (description growth past the 500-character budget, structural breakage); the structural checks are complementary to, not a substitute for, the content audit in step 9. When the validator itself changes, run the bundled fixture harness (`python3 scripts/selftest_skill.py`) and the validator against this skill's own package in the same step. An error that persists after re-checking the package against the documented checks indicates a validator bug — fix the validator before trusting either.
9. **Audit Package Content:** Run the content audit defined in `references/AUDIT.md` over every file affected by the change, in creation and edit flows alike. Report its findings before finalizing the change.
10. **Check Cross-Runtime Compatibility:** If the skill targets multiple AI models or agent runtimes (or the user asks for cross-agent compatibility), read `references/RUNTIMES.md` and verify the package against its cross-runtime compatibility checklist.
11. **Sync Bundled Layers After Rule Changes:** Whenever a rule, limit, or constraint changes in `references/` (or in the upstream documentation it captures), audit every bundled file that encodes or documents those rules — validators in `scripts/`, criteria and checklists in `references/`, and templates or data files in `assets/` — in this skill and in any generated package. In the same execution step, implement each newly mechanically checkable rule in the validator, or state in the script's header why it is not implemented. Update the header's check list. Update the fixtures that pin the changed checks in `scripts/selftest_skill.py` in the same step. Update any text that describes the validator's coverage. Treat the validator's header and the documented checklists as two views of one contract: change them together or not at all. A user request that names only one layer (e.g. "update references") does not exempt the others.

## Production Directory Structure & Content Contracts

Keep skills focused by offloading detailed technical context into subfolders, loaded by agents on demand. Assign bundled content — code included — by what the agent does with it, not by what the content looks like: code the agent reads to reason (examples, pattern catalogs, API usage) lives in `references/`; code the agent copies verbatim into output (skeletons, boilerplate) lives in `assets/`; code the agent executes lives in `scripts/`. Never invent a new top-level folder such as `examples/` or `snippets/`: the canonical layouts are `scripts/`/`references/`/`assets/` (open standard, OpenAI/Codex) and `docs/`/`templates/`/`scripts/` (Cline). A Cline-targeted skill mirrors the split as `docs/` (read to reason) and `templates/` (copied verbatim).

### 1. Executable Code Layer — `scripts/`

- *Purpose:* Self-contained executable code blocks that agents run for algorithmic compute and deterministic parsing.
- *Contains:* scripts only.
- Scripts should be self-contained or clearly document dependencies, include helpful error messages, and handle edge cases gracefully. Common languages: Python, Bash, JavaScript.
- Scripts that enforce documented rules (validators, linters) follow the sync contract in step 11 of the workflow. A stale validator still runs and passes, which misleads more than a missing one. Validators must fail closed: exit non-zero when any check fails — a validator that prints per-item success lines alongside its own error records is broken, and its success output is void. Every check a bundled validator performs ships with a positive and a negative fixture in its self-test; change the pinned fixtures in the same step as the check.

### 2. Focused Documentation Layer — `references/`

- *Purpose:* Smaller, specialized documentation files that agents read lazily only when a decision branch requires technical grounding.
- *Contents:* technical validation criteria and progressive disclosure contracts — detailed technical specs and API contracts, per-vendor runtime compatibility rules, structured formats and validation schemas, and code examples and pattern catalogs the agent studies. File names in this contract are illustrative for generated packages (e.g. `REFERENCE.md`, `FORMS.md`, `finance.md`, `patterns.md`); the files this skill itself bundles are listed in its Bundled Files section.

### 3. Static Resource Layer — `assets/`

- *Purpose:* Immutable files the agent reproduces or renders — templates, presentation layouts, visual anchoring, and data.
- *Contains:* templates (document/config templates and verbatim copy-paste code skeletons the agent reproduces byte for byte), images (diagrams, examples), and data files (lookup tables, schemas).
- Templates and data files that encode rule-dependent formats or schemas must be updated together with the rule change, exactly like `scripts/` and `references/`.

## Best-Practice Content Patterns

Apply these when writing the instruction body — they are what make a skill effective beyond mere spec compliance:

- **Gotchas first:** the highest-value content is concrete corrections to mistakes the agent will make unaided — environment-specific facts that defy reasonable assumptions. Keep gotchas in SKILL.md where the agent reads them before encountering the situation. Place each gotcha at the layer that is actually loaded at failure time: an environment-independent core file carries only the portable principle, and the concrete instance lives in the domain skill (or in a runtime-specific rules file that is always active).
- **Calibrate prescriptiveness:** rigid, exact directives only for fragile, sequential, or destructive operations; elsewhere explain why instead of dictating, so the agent makes better context-dependent decisions.
- **Define gating terms:** every term a rule uses as the trigger of an obligation — a length class, a state change, an installed match, a severity class — is defined inline in parentheses or by reference to its owning location. An undefined gating term makes the rule unenforceable, the highest-severity defect class.
- **State compositions exhaustively:** when a rule set routes, layers, or falls back (routing axes, delta skills, fallback standards), state every combination explicitly — all match, some match, none match — and which rule set governs in each. An unstated combination forces the reader to guess.
- **Remediate by failure class:** When an observed failure prompts changing an existing rule in a skill being authored or updated, diagnose the failure class before changing the rule. Apply the matching remedy: add a missing rule at the correct layer; fix a wrong or mis-scoped rule in its own wording; narrow a too-permissive rule to its minimal specific instance; make a correct-but-ignored rule mechanically checkable rather than giving it more prose. Command-level specifics belong only to the too-permissive remedy — expanding a mis-scoped rule with examples buries the defect.
- **Defaults, not menus:** pick one default approach and mention alternatives briefly; never present equal options without a recommendation.
- **Procedures over declarations:** teach how to approach a class of problems, not the answer for one instance — individual details may be specific, but the method must generalize.
- **Templates over prose:** for required output formats, provide a concrete template; agents pattern-match against structures more reliably than against prose descriptions.
- **Checklists and validation loops:** explicit step checklists for multi-step workflows; validate-then-fix loops for self-checking; plan-validate-execute for batch or destructive operations.
- **Scope and language checks:** the authoritative rules for coherent scope, one task per section, and one instruction per sentence live in the content-audit checklist, `references/AUDIT.md`; apply them at composition time, not only at audit time.
- **Content audit on every change:** the authoritative checklist and reporting protocol for the post-change content audit live in `references/AUDIT.md` (workflow step 9). The audit is not mechanically checkable — it requires the file's invariants derived in step 3 — so the structural validator cannot substitute for it.
- **Compose for the named runtime, not the authoring environment:** when a skill is written or adapted for a named runtime, its body references bundled files exactly as they exist in that runtime's deployment (names, paths, platform conventions) and generalizes wording only when multiple runtimes are actually targeted. Constraints of the authoring environment — a source store that accepts only plain-text support files, packaging workarounds, rename-on-install steps — never become instructions in the body: one-time assembly belongs in the bundled file's header or in deployment material outside the skill.

## Common Authoring Failures

Failure modes repeatedly observed in shipped packages; check for each before delivering.

- A validator that fails on its own compliant package: run the bundled fixture harness and the validator against this skill's own package whenever the validator changes (step 8). The harness pins every documented parser shape with positive and negative fixtures.
- Filename drift — a file renamed in one location while another still references the old name: the structural validator fails closed on paths that no longer resolve, and content-audit item 16 in `references/AUDIT.md` catches a stale reference that still resolves to the wrong target.
- External references without conditional wording — the package names a skill or tool that the runtime may not have installed: the validator warns on cross-skill references lacking conditional wording. State the purpose and the fallback for its absence instead (content-audit item 20 in `references/AUDIT.md`).

## Strict Anti-Hallucination & Artifact Guardrails

- **The Ghost File Rule:** Never reference fictional or speculative files. Every script, template, or schema path written into the output must exist in the workspace or be explicitly generated as part of the current execution step.
- **Trace technical claims to source material:** In generated skills, never invent APIs, cmdlets, parameters, flags, error codes, or URLs — document only what the source material or verified official documentation confirms; copy identifiers and links verbatim from their source. If verification is impossible, state the uncertainty explicitly instead of presenting speculation as fact.
- **Falsifiable rules only:** Prefer rules backed by a documentation reference, an analyzer check, or an executable validation over prose opinion — an unverifiable rule teaches the agent to guess.
- **No Stale Enforcement Scripts:** A bundled script that encodes checks is trustworthy only while it matches the documented rules. Never let `references/`, `scripts/`, or `assets/` drift: adding or changing a rule without auditing the files that enforce or encode it produces a validator that silently contradicts its own documentation and passes output the rules would reject.
- **Tool-Driven Grounding:** If you need the parameters of an API or a script, do not guess — read the source file or the schema inside the skill's `references/` folder.
- **Zero Conversational Fluff:** In generated skill output, do not add introductory explanations, filler text, or structural summaries around code blocks. Output only clean, actionable markdown and source files.

## Testing Guidance

- Defer behavioral testing to the `agent-skill-evaluator` skill when it is installed in the runtime: it runs with-skill versus baseline comparisons, grades assertions with recorded evidence, benchmarks pass rate against token and time cost, and optimizes descriptions by trigger rate.
- If that skill is absent, hold every generated skill to this minimum bar before shipping: run at least one representative task with and without the skill, and confirm the delta favors the skill — a pass rate without a baseline may reflect the model's unaided ability rather than the skill's contribution. Structural validation (step 8) never substitutes for this.

## Bundled Files

- `scripts/validate_skill.py` — Python structural validator (whitelisted frontmatter keys, name/description constraints, optional compatibility validation, link resolution across all documented subfolder layouts, cross-runtime warnings, consistency warnings for cross-skill references lacking conditional wording and for files no scanned Markdown file references). It is a complete Python 3 script; run it directly with `python3 scripts/validate_skill.py <skill-directory>`. When rules change, follow the sync contract in step 11 of the workflow.
- `scripts/selftest_skill.py` — Python fixture harness for the structural validator: for every check the validator's header lists and every parser shape it documents, it generates a positive and a negative fixture package in a temporary directory and asserts the documented exit codes and output. It is a complete Python 3 script; run it directly with `python3 scripts/selftest_skill.py` whenever the validator changes.
- `references/REFERENCE.md` — Agent Skills standards, validation tooling, curated existing-skill sources to search before authoring, and links to per-vendor official documentation.
- `references/RUNTIMES.md` — cross-runtime compatibility rules from official Anthropic (Claude Code), Mistral, OpenAI (ChatGPT/Codex and API), DeepSeek (harness and Deep Code), and Cline documentation, with a cross-runtime checklist. Read it when a skill must work across multiple AI models or agent runtimes.
- `references/AUDIT.md` — the authoritative post-change content-audit checklist (semantic quality, cross-reference accuracy, layer ownership). Read it at the content-audit step of the workflow after every creation or edit.
- Complete inventory: `SKILL.md`, `scripts/validate_skill.py`, `scripts/selftest_skill.py`, `references/REFERENCE.md`, `references/RUNTIMES.md`, `references/AUDIT.md` — nothing else. This skill ships no `assets/` layer; if one is added later, it joins the same sync contract as `scripts/` and `references/`. When updating any rule, diff the change against this full inventory before finishing.

## Completion Criteria

The capability generation is successful ONLY when:

- The package features valid frontmatter matching all constraints.
- All file paths resolve cleanly to physical files inside the documented layer folders of the package's layout (`scripts/`, `references/`, `assets/`; or `docs/`, `templates/`, `scripts/` in Cline-targeted packages).
- Structural validation passes with no missing links: the environment's native skill-validation mechanism when one is available, and the bundled structural validator described in step 8 run for every check the native mechanism does not cover (or for all checks when none is available).
- If any documented rule changed during the task, every bundled script that encodes checks was re-audited in the same step: newly mechanically checkable rules are implemented (or the script's header documents why not), and the header's check list matches what the script actually checks.
