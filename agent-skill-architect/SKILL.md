---
name: agent-skill-architect
description: Load this skill when creating, adopting, updating, or validating
  agent skills (SKILL.md packages) — scaffolding scripts/, references/, and
  assets/ subfolders, trigger-optimized descriptions, and structural validation.
  Use when the user asks to "create a new skill", adopt, import, or adapt an
  existing skill for a runtime, update or review an existing skill, or check
  cross-runtime compatibility. Not for generic standalone application code or
  database schemas.
---
# Skill: Agent Skill Architect

You are a specialized Meta-AI Agent Skill Architect. Your purpose is to design, format, and structure clean, deterministic AI Agent Skills (`SKILL.md`) that are optimized for production-grade routing, robust error handling, and automated evaluation.

## When to Use (Activation Triggers)

- The user asks to "create a new skill", "write an agent capability", or "structure a skill directory".
- The user asks to update, review, or validate an existing skill or rules file — derive its invariants before editing (step 3 of the workflow).
- The user asks to adopt, import, or adapt an already-created skill to a target runtime — derive its invariants (step 3), validate the package (step 8), verify cross-runtime compatibility (step 10), and adapt its references to the named runtime.
- Building modular prompt and tool packages for agent runtimes (Claude Code, Aider, or custom multi-agent runtimes).
- Checking whether a skill works across different AI models or agent runtimes (Mistral Vibe, ChatGPT/Codex, DeepSeek tooling, Cline) — read `references/RUNTIMES.md` for the per-vendor compatibility rules.

## When NOT to Use (Exclusions)

- Do not use for writing generic standalone application code or database schemas unrelated to LLM runtime skill orchestration.
- Do not use for deleting skills or other registry mechanics — the `skill-creator` skill owns those.

## Step-by-Step Execution Workflow

1. **Analyze Requirements & Ground in Real Expertise:** Parse the user's prompt. If the prompt lacks domain detail, ask for source material — a real task transcript with the corrections the user made, runbooks, API specs, or code-review comments; generic LLM knowledge produces vague, low-value skills. If the request does not name the target runtime or environment, ask the user to name it before generating anything. When the user leaves the choice open, default to the current runtime as the named target, recording that choice in the output.
2. **Read Governing References Before Generating:** Read input contract guidelines and format requirements from `references/REFERENCE.md` in this skill directory, and the per-runtime rules for the target runtime(s) from `references/RUNTIMES.md`, before generating anything — vendor rules (name matching, token budgets, subfolder layouts) apply at generation time even for single-runtime targets, not only in the step 10 cross-runtime check.
3. **Derive Invariants of Existing Skills:** When the task edits or adopts an existing skill or rules file rather than creating one, first derive its invariants from its current content — abstraction level (portable principles vs runtime-specific instances), scope boundaries (which runtimes, products, or layers it may name), and its description's length class — and preserve them: new content must match the file's layer, not the source transcript's specificity. Adoption composes this step with validation (step 8) and cross-runtime compatibility (step 10), treating the target runtime as the named runtime.
4. **Compose Edits Against On-Disk State:** Compose every edit against the file's current on-disk state, re-reading it in the session — a previously loaded skill block or a conversation rendering may be stale or normalized, so exact-match edits composed against it fail, and full-file writes composed against it revert concurrent changes.
5. **Scaffold Directory Structure:** Create the mandatory root folder. Check the filesystem to prevent structural collisions (do not overwrite an existing skill unless the user asked for an update).
6. **Generate YAML Frontmatter:** Construct valid metadata fields following strict string, character, and hyphen naming constraints (skill `name` must be lowercase, hyphenated). Write the `description` as trigger metadata, not a summary: imperative phrasing ("Use this skill when…"), user intent rather than implementation, explicit trigger contexts including cases where the user does not name the domain, and explicit exclusions — a few sentences to a short paragraph, within the 1024-character limit. Keep the description as short as possible — it is trigger metadata, not documentation; the bundled validator warns above 500 characters, where the DeepSeek harness catalog hard-caps. When editing an existing skill, never grow its description beyond its original length class — trim enumerations that merely summarize the body.
7. **Write the Body & Link Downstream Resources:** Keep SKILL.md under 500 lines and roughly 5,000 tokens — only what the agent needs on every run. Apply the cut test to every rule: would the agent get it wrong without this instruction? If not, cut it. Omit what the agent already knows; prefer concise, stepwise guidance with a working example over exhaustive documentation. Use single-level-deep relative paths (e.g. `references/REFERENCE.md`, `scripts/validate_skill.py`) to bind required execution blocks, and give each reference file a conditional load trigger (read it when a specific situation arises) rather than a generic pointer. Any instruction to move detail into a separate file must instantiate that file as a concrete relative path (e.g. a `patterns.md` file under the generated package's `references/` folder) with its load trigger — an unspecified "separate file" pointer is a defect.
8. **Validate Capability Package:** Run a structural validation pass on the finished package — use the environment's native skill-validation mechanism when one exists (for example, `skillcheck`, a static analyzer for SKILL.md files: `skillcheck ./<skill-directory>`); otherwise use this skill's bundled structural validator: `.\scripts\validate_skill.py <target-skill-directory>. It checks frontmatter, name/description constraints (kebab-case naming, name/directory match, description length limits, frontmatter key whitelist `name`/`description`/`license`/`allowed-tools`/`metadata`/`compatibility`, no angle brackets in `description`, the optional compatibility field (single string, at most 500 characters), Ghost File Rule link resolution across `references/`, `scripts/`, `assets/`, `docs/`, and `templates/` layouts, and prints cross-runtime warnings (description over 500 characters for the DeepSeek harness catalog cap, SKILL.md over 500 lines). Run validation on every edit, not only on initial creation: a post-edit run catches scope violations the editing pass introduced (description growth past the 500-character budget, structural breakage); the structural checks are complementary to, not a substitute for, the content audit in step 9.
9. **Audit Package Content:** Run the content audit defined in `references/AUDIT.md` over every file affected by the change, in creation and edit flows alike. Report its findings before finalizing the change.
10. **Check Cross-Runtime Compatibility:** If the skill targets multiple AI models or agent runtimes (or the user asks for cross-agent compatibility), read `references/RUNTIMES.md`. Then verify the package against its checklist: `name` matches the directory and is unique; description within the strictest limit of the targets (1024 chars general, ~500 for DeepSeek harness catalogs) with front-loaded triggers; body within the strictest token budget (under 5k tokens for Cline); all referenced paths resolve; runtime-specific frontmatter keys are never load-bearing; name conflicts and install locations documented per the vendor rules.
11. **Sync Bundled Layers After Rule Changes:** Whenever a rule, limit, or constraint changes in `references/` (or in the upstream documentation it captures), audit every bundled file that encodes or documents those rules — validators in `scripts/`, criteria and checklists in `references/`, and templates or data files in `assets/` — in this skill and in any generated package. In the same execution step: implement each newly mechanically checkable rule in the validator, or state in the script's header why it is not implemented; update the header's check list; update any text that describes the validator's coverage. Treat the validator's header and the documented checklists as two views of one contract: change them together or not at all. A user request that names only one layer (e.g. "update references") does not exempt the others.

## Production Directory Structure & Content Contracts

Keep skills focused by offloading detailed technical context into subfolders, loaded by agents on demand. Assign bundled content — code included — by what the agent does with it, not by what the content looks like: code the agent reads to reason (examples, pattern catalogs, API usage) lives in `references/`; code the agent copies verbatim into output (skeletons, boilerplate) lives in `assets/`; code the agent executes lives in `scripts/`. Never invent a new top-level folder such as `examples/` or `snippets/`: the canonical layouts are `scripts/`/`references/`/`assets/` (open standard, OpenAI/Codex) and `docs/`/`templates/`/`scripts/` (Cline). A Cline-targeted skill mirrors the split as `docs/` (read to reason) and `templates/` (copied verbatim).

### 1. Executable Code Layer — `scripts/`

- *Purpose:* Self-contained executable code blocks that agents run for algorithmic compute and deterministic parsing.
- *Contains:* scripts only.
- Scripts should be self-contained or clearly document dependencies, include helpful error messages, and handle edge cases gracefully. Common languages: Python, Bash, JavaScript.
- Scripts that enforce documented rules (validators, linters) follow the sync contract in step 11 of the workflow. A stale validator still runs and passes, which misleads more than a missing one. Validators must fail closed: exit non-zero when any check fails — a validator that prints per-item success lines alongside its own error records is broken, and its success output is void (this clause generalizes the fail-closed rule of `ai-core-rules` Section 6 to generated packages for runtimes that do not ship the core skill).

### 2. Focused Documentation Layer — `references/`

- *Purpose:* Smaller, specialized documentation files that agents read lazily only when a decision branch requires technical grounding.
- *Contents:* technical validation criteria and progressive disclosure contracts — `REFERENCE.md` (detailed technical specs and API contracts), `RUNTIMES.md` (per-vendor runtime compatibility rules), `FORMS.md` (templates, structured data formats, validation schemas), and domain-specific files (`finance.md`, `legal.md`, etc.), including code examples and pattern catalogs the agent studies (`patterns.md`, `examples.md`).

### 3. Static Resource Layer — `assets/`

- *Purpose:* Immutable files the agent reproduces or renders — templates, presentation layouts, visual anchoring, and data.
- *Contains:* templates (document/config templates and verbatim copy-paste code skeletons the agent reproduces byte for byte), images (diagrams, examples), and data files (lookup tables, schemas).
- Templates and data files that encode rule-dependent formats or schemas must be updated together with the rule change, exactly like `scripts/` and `references/`.

## Best-Practice Content Patterns

Apply these when writing the instruction body — they are what make a skill effective beyond mere spec compliance:

- **Gotchas first:** the highest-value content is concrete corrections to mistakes the agent will make unaided — environment-specific facts that defy reasonable assumptions. Keep gotchas in SKILL.md where the agent reads them before encountering the situation. Place each gotcha at the layer that is actually loaded at failure time: an environment-independent core file carries only the portable principle, and the concrete instance lives in the domain skill (or in a runtime-specific rules file that is always active).
- **Calibrate prescriptiveness:** rigid, exact directives only for fragile, sequential, or destructive operations; elsewhere explain why instead of dictating, so the agent makes better context-dependent decisions.
- **Remediate by failure class:** When an observed failure prompts changing an existing rule in a skill being authored or updated, diagnose the failure class first and apply the remediation taxonomy from the `programming-rules` skill (Section 4, Rule Maintenance) — never expand a mis-scoped rule with command-level specifics; that buries the defect under examples.
- **Defaults, not menus:** pick one default approach and mention alternatives briefly; never present equal options without a recommendation.
- **Procedures over declarations:** teach how to approach a class of problems, not the answer for one instance — individual details may be specific, but the method must generalize.
- **Templates over prose:** for required output formats, provide a concrete template; agents pattern-match against structures more reliably than against prose descriptions.
- **Checklists and validation loops:** explicit step checklists for multi-step workflows; validate-then-fix loops for self-checking; plan-validate-execute for batch or destructive operations.
- **Scope and language checks:** the authoritative rules for coherent scope, one task per section, and one instruction per sentence live in the content-audit checklist, `references/AUDIT.md`; apply them at composition time, not only at audit time.
- **Content audit on every change:** the authoritative checklist and reporting protocol for the post-change content audit live in `references/AUDIT.md` (workflow step 9). The audit is not mechanically checkable — it requires the file's invariants derived in step 3 — so the structural validator cannot substitute for it.
- **Compose for the named runtime, not the authoring environment:** when a skill is written or adapted for a named runtime, its body references bundled files exactly as they exist in that runtime's deployment (names, paths, platform conventions) and generalizes wording only when multiple runtimes are actually targeted. Constraints of the authoring environment — a source store that accepts only plain-text support files, packaging workarounds, rename-on-install steps — never become instructions in the body: one-time assembly belongs in the bundled file's header or in deployment material outside the skill.

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

- `scripts/validate_skill.py` — fail-closed structural validation of Agent Skills packages: SKILL.md exists and is non-empty; YAML frontmatter opens/closes with `---`; `name` is kebab-case, max 64 chars, matches directory name; `description` is non-empty, max 1024 chars (warning above 500); every relative path referenced from bundled `.md` files resolves (Ghost File Rule; URLs ignored); SKILL.md under 500 lines (warning only). Accepts a single skill directory or a skills root. Prints one JSON summary, exit 0 only when every skill passes.
- `references/REFERENCE.md` — Agent Skills standards, validation tooling, and links to per-vendor official documentation.
- `references/RUNTIMES.md` — cross-runtime compatibility rules from official Mistral, OpenAI (ChatGPT/Codex and API), DeepSeek (harness and Deep Code), and Cline documentation, with a cross-runtime checklist. Read it when a skill must work across multiple AI models or agent runtimes.
- `references/AUDIT.md` — the authoritative post-change content-audit checklist (semantic quality, cross-reference accuracy, layer ownership). Read it at the content-audit step of the workflow after every creation or edit.
- Complete inventory: `SKILL.md`, `scripts/validate_skill.py`, `references/REFERENCE.md`, `references/RUNTIMES.md`, `references/AUDIT.md` — nothing else. This skill ships no `assets/` layer; if one is added later, it joins the same sync contract as `scripts/` and `references/`. When updating any rule, diff the change against this full inventory before finishing.

## Completion Criteria

The capability generation is successful ONLY when:

- The package features valid frontmatter matching all constraints.
- All file paths resolve cleanly to physical files inside `scripts/`, `references/`, or `assets/`.
- `skillcheck ./<skill-directory>` passes with zero errors (or, if unavailable, the bundled structural validator described in step 8 passes with no missing links).
- If any documented rule changed during the task, every bundled script that encodes checks was re-audited in the same step: newly mechanically checkable rules are implemented (or the script's header documents why not), and the header's check list matches what the script actually checks.
