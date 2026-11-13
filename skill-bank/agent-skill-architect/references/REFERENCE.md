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
- [Claude Code — Extend agents with skills](https://code.claude.com/docs/en/agent-sdk/skills) — Anthropic's official Claude Code skills documentation: `SKILL.md` packaging, `.claude/skills/` discovery locations, and model-driven or slash-command invocation.
- [Agent Skills — Client showcase](https://agentskills.io/home) — The open standard's overview of skills-compatible clients.
- [Anthropic — Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — Skills as reusable filesystem-based resources across Claude Code, the Claude API, and claude.ai, loaded through metadata-first progressive disclosure.
- [Anthropic — Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Official authoring guidance: concise structure, appropriate degrees of freedom, progressive disclosure, and testing with the models you plan to use.
- [Anthropic — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — Design rationale and skill anatomy; recommends starting from evaluation — identify capability gaps on representative tasks before writing extensive documentation.
- [OpenAI — Agents guide](https://developers.openai.com/api/docs/guides/agents) — Choosing an agent runtime, adding tools and skills, function calling, MCP, prompt caching, and orchestration patterns.
- [DeepSeek — Tool Calls](https://api-docs.deepseek.com/guides/tool_calls) — Function calling at the API level for services without a skills feature: JSON Schema tool definitions (name, description, parameters, required fields) with application-side execution.
- [Mistral — Skills in Studio](https://docs.mistral.ai/studio/agents/learn/agent/skills) — Studio-side skill authoring: description-first triggers, one skill per job, bundled examples and templates, testing on realistic tasks.
- [Mistral — Agents Tools Overview](https://docs.mistral.ai/studio/agents/agent-tools) — Built-in tools, function calling, and MCP connectors for Studio agents.
- [Mistral — Function Calling](https://docs.mistral.ai/studio/agents/agent-tools/function-calling) — Defining functions with JSON Schemas and attaching them to Studio agents.
- [NVIDIA — Nemotron Speech Agent Skills](https://docs.nvidia.com/nim/speech/latest/resources/agent-skills.html) — Curated agentic skills for coding assistants working with Speech NIM microservices: routing rules, guardrails, reference files, a skill card, and evaluation tasks.
- [NVIDIA — NeMo Agent Toolkit — AI Coding Agent Skills](https://docs.nvidia.com/nemo/agent-toolkit/1.9/resources/contributing/agent-skills.html) — Reusable coding-agent skills under `skills/` following the SKILL.md directory pattern, installable into Claude Code or Codex skill directories.
- [NVIDIA — NeMo Gym — Agent Skills](https://docs.nvidia.com/nemo/gym/v0.7.0/agent-server/agent-skills) — Skills as reusable units of operational knowledge per the open Agent Skills standard, with `skills_ref` provenance in results.

## Skill sources — search before you synthesize

Before authoring a new skill from scratch, search these sources for an already-prepared candidate and adapt it instead of creating a new package. Verify each candidate's license, maintenance status, and runtime compatibility before adapting; community collections vary in curation quality.

Official repositories:

- [Anthropic skills repository](https://github.com/anthropics/skills) — Anthropic's public example Agent Skills.
- [Cline skills repository](https://github.com/cline/skills) — Skills used at Cline, in the `docs/`/`templates/`/`scripts/` layout.

Curated community lists:

- [awesome-cline-skills](https://github.com/TheArchitectit/awesome-cline-skills) — Curated, practical Cline skill examples.
- [awesome-ai-agent-skills (seb1n)](https://github.com/seb1n/awesome-ai-agent-skills) — Cross-platform list of ready-to-use Agent Skills.
- [awesome-agent-skills (VoltAgent)](https://github.com/VoltAgent/awesome-agent-skills) — Curated collection compatible with Claude Code, Codex, Gemini CLI, and Cursor.
- [awesome-agent-skills (Ditto190)](https://github.com/Ditto190/awesome-agent-skills) — Claude Code skills plus agent skills across testing, SwiftUI, and task decomposition.
- [awesome-agent-skills (philipbankier)](https://github.com/philipbankier/awesome-agent-skills) — Cross-ecosystem directory of skills, MCP servers, and editor rules.
- [awesome-agent-skills (YangsonHung)](https://github.com/YangsonHung/awesome-agent-skills) — Modular, bilingual Agent Skills collection.

## Tool, protocol, and manifest definitions

Where a vendor or standards body exposes no SKILL.md skill concept, skill creation means authoring well-specified tool, function, or manifest definitions. These are the protocol-level sources:

- [Model Context Protocol](https://modelcontextprotocol.io) — Open standard for connecting AI applications to external systems (tools, data sources, workflows).
- [A2A Protocol community](https://agent2agent.info) — Agent-to-agent interoperability with Agent Card implementation, validation, and signing guides, including an Agent Skills and Agent Card tutorial.
- [Microsoft Security Copilot — Agent manifest](https://learn.microsoft.com/en-us/copilot/security/developer/agent-manifest) — YAML manifest for building Security Copilot agents, with companion best-practices guidance.
- [Microsoft Copilot Studio — REST API tools](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api) — Extending Copilot Studio agents with REST API tools defined by an OpenAPI specification.
- [W3C AI Agent Memory Interoperability Community Group](https://www.w3.org/community/ai-agent-memory-interop/) — Open protocol-level specification for agent memory portable across vendors, models, frameworks, and tool ecosystems.

## Practical workflow

1. Before authoring a new skill, search the skill sources above for an already-prepared candidate; when one fits, adapt it after verifying its license, maintenance status, and runtime compatibility.
2. Follow the official format specification while authoring `SKILL.md`.
3. Link any bundled reference files from `SKILL.md` using paths that exist in the skill directory.
4. For the remaining workflow stages, follow the owning locations: validation — SKILL.md step 8; content audit — `references/AUDIT.md`; cross-runtime compatibility — SKILL.md step 10; rule sync — SKILL.md step 11; behavioral testing — SKILL.md Testing Guidance.
