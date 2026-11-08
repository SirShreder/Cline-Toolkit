# Reference: Agent Skill Standards and Evaluation

Use these sources when creating or validating an agent skill. Check the official documentation for current requirements before relying on implementation details, since specifications and tool APIs can change.

## Agent Skills format

- [Agent Skills](https://agentskills.io/) — The initiative’s overview of the open skill format.
- [Format specification](https://agentskills.io/specification) — The canonical requirements for `SKILL.md`, YAML frontmatter, naming, and skill directories.
- [Official Agent Skills repository](https://github.com/agentskills/agentskills) — Specification source, related materials, and community discussions.
- [skillcheck](https://github.com/moonrunnerkc/skillcheck) — Cross-agent static analyzer for SKILL.md files: validates frontmatter, scores description discoverability, checks file references, enforces token budgets, and flags compatibility issues across Claude Code, VS Code/Copilot, Codex, and Cursor. Run `skillcheck ./<skill-directory>` to scan a directory.
- [Agent Skills Discord announcement](https://github.com/agentskills/agentskills/discussions/273) — Community announcement and discussion. Specification questions are directed to GitHub Discussions.

## Authoring guides

- [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices) — Grounding skills in real expertise, spending context wisely (the cut test, moderate detail, progressive disclosure), calibrating prescriptiveness to fragility, and content patterns (gotchas, templates, checklists, validation loops, plan-validate-execute).
- [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts) — Pinned one-off commands (uvx, npx, etc.), self-contained scripts with inline dependency declarations (PEP 723, Deno, Bun, Ruby), and designing script interfaces for agentic use: non-interactive, `--help` usage, helpful errors, structured data on stdout with diagnostics on stderr, meaningful exit codes, safe defaults.

## Runtime and vendor documentation (cross-model compatibility)

To check a skill against a specific AI model or agent runtime, read `references/RUNTIMES.md` in this skill directory first — it distills the official rules below into per-vendor constraints and a cross-runtime checklist.

- [Mistral Vibe Work — Reuse work with Skills](https://docs.mistral.ai/vibe/work/skills) — Official Mistral skill usage, discovery/activation/execution stages, and authoring best practices (descriptions as triggers, one skill per job, no near-duplicates, bundled files).
- [OpenAI — Build skills](https://developers.openai.com/codex/skills) — Skills in ChatGPT and Codex: required frontmatter, context budgets for the initial skill list, `.agents/skills` discovery locations, name-conflict behavior, and invocation modes.
- [OpenAI — Skills API guide](https://developers.openai.com/api/docs/guides/tools-skills) — Skills for Responses API shell tools and Agents API sandboxes: upload as versioned bundles, attach via `skill_reference`.
- [DeepSeek — deepseek-harness skills subsystem](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md) — DeepSeek's official agent harness: skill identity rules, discovery priority and roots, invocation-policy frontmatter, and the session catalog with its description cap.
- [DeepSeek — Deep Code integration](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/main/docs/deepcode.md) — DeepSeek's terminal assistant: Agent Skills locations (`~/.agents/skills`, `./.deepcode/skills`) and the `/` skill picker.
- [Cline — Skills](https://docs.cline.bot/customization/skills) — Official Cline skill format: name/directory matching, description limit, token budgets, `docs/`-`templates/`-`scripts/` layout, locations, and global-over-project precedence.
- [Agent Skills — Client showcase](https://agentskills.io/home) — The open standard's overview of skills-compatible clients.

## Practical workflow

1. Follow the official format specification while authoring `SKILL.md`.
2. Link any bundled reference files from `SKILL.md` using paths that exist in the skill directory.
3. Validate the skill package with `skillcheck` (or the environment's native skill-validation mechanism).
4. If the skill targets multiple AI models or agent runtimes, check it against the cross-runtime compatibility checklist in `references/RUNTIMES.md` (naming, description limits, token budgets, install locations, conflict behavior).
5. If any documented rule changed during the task, audit every bundled script that encodes checks (e.g. `scripts/validate_skill.py`) and update it in the same step — implement newly mechanically checkable rules, or document in the script's header why they are not implemented.
6. If behavioral testing is required and the `agent-skill-evaluator` skill is installed in the runtime, defer to it — baseline comparisons, evidence-graded assertions, benchmarking, and description trigger optimization are its scope.
