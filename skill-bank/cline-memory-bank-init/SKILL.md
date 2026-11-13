---
name: cline-memory-bank-init
description: Use this skill to set up and initialize the Cline Memory Bank for a project — create the .clinerules/memory-bank.md rules file, populate memory-bank/ with the six core documentation files, add .gitignore exclusions, and record adoption decisions.
---

# Skill: Cline Memory Bank Initializer

## Purpose

You are a specialized Cline Memory Bank Initializer. Your purpose is to set up and initialize the Cline Memory Bank documentation system for a project so Cline can preserve context, architectural decisions, and active work across sessions. The Memory Bank transforms Cline from a stateless assistant into a persistent development partner through structured markdown files.

## When to Use (Activation Triggers)

- The user asks to "set up memory bank", "initialize memory bank", "create memory bank documentation", or "configure Cline memory bank for a project".
- The user asks to establish structured project context preservation across Cline sessions.
- The user needs a Memory Bank rule file plus core documentation files (project brief, product context, active context, system patterns, tech context, progress).
- A new project or repository needs Cline Memory Bank infrastructure from scratch.

## When NOT to Use (Exclusions)

- Do not use for generic application code, database schemas, or non-Cline agent runtimes.
- Do not use if the project already has a complete Memory Bank (check `memory-bank/` directory first).
- Do not use for skill deletion or registry mechanics — those are outside this skill's scope.
- Do not use for generic standalone application development unrelated to Cline context management.

## Step-by-Step Execution Workflow

1. **Analyze Repository:** Inspect workspace root, README, manifests (package.json, etc.), and git history. Identify existing skill packages, rule files, and project conventions. Note the current branch, commit count, and working tree state.

2. **Clarify with User (Mandatory):** Ask the user to confirm or provide details on project title, goals, target audience, architectural constraints, and priorities before generating files. Do not proceed without user confirmation.

3. **Create Rules File (`.clinerules/memory-bank.md`):** Add instructions including:
   - YAML frontmatter (`name`, `description`)
   - Purpose statement with the Cline session-reset directive ("I MUST read ALL memory bank files at the start of EVERY task — this is not optional.")
   - File hierarchy diagram (Mermaid)
   - Core memory-bank files table with purpose and update frequency
   - Workflow diagram (Mermaid stateDiagram)
   - Mandatory adoption rule (every skill must be adopted before use)
   - Fail-closed path validation rule (Ghost File Rule)
   - Key commands: `follow your custom instructions`, `initialize memory bank`, `update memory bank`
   - Integration note with existing skill packages

4. **Initialize `memory-bank/` Directory:** Create the six core documentation files:
   - `projectbrief.md` — foundation document with core requirements and goals
   - `productContext.md` — why the project exists, problems it solves, UX goals
   - `activeContext.md` — current focus, recent changes, next steps (updates most frequently)
   - `systemPatterns.md` — architecture, design patterns, component relationships
   - `techContext.md` — tech stack, setup, constraints, dependencies
   - `progress.md` — what works, what is left, known issues (updates every milestone)

   Each file must have YAML frontmatter (`name`, `description`) matching its purpose.

5. **Add `.gitignore` Exclusions:** Ensure `.clinerules/`, `.cline/`, and `memory-bank/` are excluded from version control (kept local). Add common IDE, OS, and language artifacts as needed.

6. **Verify & Recommend Storage:** Check file integrity by re-reading all created files from disk. Recommend Git tracking for committed project files while keeping Memory Bank directories local. Document any storage recommendation in `progress.md`.

7. **Record Adoption:** Record skill adoptions in `memory-bank/progress.md` (skill name, decision, date).

## Testing Guidance

- After initialization, run `follow your custom instructions` to confirm Cline reads the Memory Bank files.
- Verify all six core files exist and contain valid YAML frontmatter.
- Verify fail-closed path validation: every relative path referenced from a `.md` file resolves to a physical file.
- Confirm `.gitignore` excludes Memory Bank directories from version control.

## Bundled Files

- `SKILL.md` — this file, with purpose, triggers, exclusions, workflow, testing guidance, bundled files, completion criteria
- `references/` — optional reference contracts (none bundled initially; add as needed)
- `scripts/` — optional enforcement/validation scripts (none bundled initially; add as needed)
- Complete inventory: `SKILL.md`, `references/`, `scripts/` — nothing else

## Completion Criteria

The Memory Bank initialization is successful ONLY when:
- `.clinerules/memory-bank.md` exists with valid YAML frontmatter and all sections
- All six `memory-bank/` core files exist with valid YAML frontmatter
- `.gitignore` excludes `.clinerules/`, `.cline/`, and `memory-bank/`
- All relative paths referenced from bundled `.md` files resolve to physical files (Ghost File Rule)
- Skill adoptions are recorded in `memory-bank/progress.md`
- User has confirmed project details before file generation