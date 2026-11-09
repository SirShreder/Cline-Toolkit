# Reference: Runtime and Model Compatibility

Read this file when a generated or reviewed skill must work across different AI models and agent runtimes (Claude Code, Mistral Vibe, ChatGPT/Codex, DeepSeek tooling, Cline, or any skills-compatible client). All rules below are taken from the vendors' official documentation — verify against the linked sources before relying on details, since runtimes evolve.

## Universal baseline: the open Agent Skills standard

All five vendors below adopted the open [Agent Skills standard](https://agentskills.io/home) (originally developed by Anthropic). The portable core is: a folder with a `SKILL.md` file containing YAML frontmatter (`name`, `description`) plus instructions, loaded through progressive disclosure — discovery (name + description only), activation (full `SKILL.md`), execution (referenced files and scripts on demand). A skill that passes the standard's format rules works structurally on every runtime; runtime-specific behavior is where the checks below matter.

## Claude Code — Anthropic

Source: [Extend agents with skills — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/skills)

- Skills are packaged as `SKILL.md` files (instructions, description, and optional supporting resources), one directory per skill.
- Discovery locations: `~/.claude/skills/` (user) and `.claude/skills/` (project), including `.claude/skills/` in every parent directory up to the repository root.
- Invocation is model-driven — Claude invokes a skill when the request matches its description — or explicit via the `/<skill-name>` slash command.
- In Agent SDK sessions, the `skills` option scopes which discovered skills Claude may invoke; by default every discovered skill is enabled.
- Skills are filesystem artifacts: there is no programmatic registration API, so authoring means writing the files on disk.

## Mistral — Vibe Work

Source: [Reuse work with Skills](https://docs.mistral.ai/vibe/work/skills)

- Skills follow the open Agent Skills standard; each Skill is a folder with a `SKILL.md` plus optional files (references, templates, examples, data).
- Discovery loads only name and description (~100 tokens per skill); the description determines activation. Write descriptions as triggers: "Use when…" phrasing beats "This Skill helps with…".
- Supporting files load as needed when the Skill activates; they are subject to a file-count limit, so use progressive disclosure for larger methods.
- Best practices from Mistral: build Skills from real tasks; keep them focused (one Skill per job — split if it grows into unrelated procedures); avoid near-duplicate descriptions (overlapping descriptions confuse routing and inflate context); bundle supporting files next to `SKILL.md`; iterate on real tasks.
- Invocation: implicit on task match, explicit slash command `/{skill-name}`, or natural reference by name. Skills can be personal or workspace-scoped, and workspace admins can force-enable skills.

## OpenAI — ChatGPT, Codex, and the API

Sources: [Build skills](https://developers.openai.com/codex/skills), [Skills (API guide)](https://developers.openai.com/api/docs/guides/tools-skills)

- `SKILL.md` must include `name` and `description`. Optional subfolders: `scripts/`, `references/`, `assets/`, and `agents/openai.yaml` (appearance and dependencies).
- Progressive disclosure with a context budget: Codex's initial skill list uses at most 2% of the model's context window, or 8,000 characters when the window is unknown. With many skills installed, Codex shortens descriptions first and may omit skills with a warning. Therefore front-load the key use case and trigger words in the description so matching survives truncation.
- `skills.max_context_tokens` configures the initial-list budget, up to 10,000 tokens. The budget applies only to the initial list; a selected skill still loads its full `SKILL.md`.
- Local discovery locations: `.agents/skills` in the current directory and each directory up to the repository root, `$HOME/.agents/skills` (user), `/etc/codex/skills` (admin), and system-bundled skills. Symlinked skill folders are followed.
- If two skills share a `name`, Codex does not merge them — both can appear in skill selectors. Keep names unique.
- Invocation: explicit via `@` in ChatGPT, `$` or `/skills` in Codex CLI/IDE; implicit via description match.
- API form factor: skills are uploaded as versioned bundles (directory multipart or a `.zip` with a single top-level folder), then mounted through `tools[].environment.skills` with `skill_reference` entries (`skill_id`, optional `version`) on the Responses API shell tool; Agents API sessions discover skills from sandbox directories. A newly uploaded version can briefly return `404` — retrieve it with a short backoff before attaching.
- Skills are the authoring format; plugins distribute skills (and connectors) across ChatGPT and Codex products.

## DeepSeek — DeepSeek Harness and Deep Code

DeepSeek's API does not itself define a skills feature; official skill support lives in DeepSeek's agent tooling.

Sources: [deepseek-harness skills subsystem](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md), [skill package family](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/skill), [Deep Code integration guide](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/main/docs/deepcode.md)

- Skill names are kebab-case: `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- The local provider accepts directory bundles (`<name>/SKILL.md`) and flat files (`<name>.md`). Nested recursive `**/SKILL.md` discovery is **not** supported — do not nest skill folders inside skill folders.
- Local discovery priority (lower rank wins): `.dsh/skills` (100) → `.agents/skills` (200) → custom dirs (300) → user `.dsh` home skills (400) → user `.agents` home skills (500) → bundled (600). The project root is the nearest ancestor containing `.git`.
- Extra frontmatter keys understood by the harness: `disable-model-invocation` and `user-invocable` (both default `true`), and optional `whenToUse` routing guidance. Other runtimes ignore these extra keys.
- The model-facing session catalog exposes only each skill's `name` and normalized description — never the body or file paths. The catalog description is capped by `catalogDescriptionMaxLength` (default **500 characters**), so keep descriptions at or under ~500 characters to route reliably in DeepSeek harness sessions.
- A skill is loaded through the model-facing `skill({ name })` tool; `scripts/`, `references/`, and `assets/` resources are resolved from the skill's base directory only when explicitly referenced.
- Deep Code (DeepSeek's terminal assistant) discovers Agent Skills from `~/.agents/skills/<name>/SKILL.md` (user) and `./.deepcode/skills/<name>/SKILL.md` (project), invoked via the `/` skill picker or `/skill-name`.

## Cline

Source: [Skills — Cline docs](https://docs.cline.bot/customization/skills)

- Required frontmatter: `name` must **exactly match the directory name**, and `description` (max 1024 characters) states when the skill applies.
- Progressive loading costs: metadata ~100 tokens per skill always; instructions under 5k tokens when triggered; bundled resources as needed. Keep `SKILL.md` under 5k tokens — split detail into `docs/` files referenced from the main instructions.
- Subfolder conventions: Cline documents `docs/`, `templates/`, and `scripts/` (rather than `references/`/`assets/`). Referenced files load only when needed; only a script's output enters context.
- Locations: project skills in `.cline/skills/` (recommended), `.clinerules/skills/`, or `.claude/skills/`; global skills in `~/.cline/skills/`. Commit `.cline/skills/` to share skills with a team.
- Precedence: when a global and a project skill share a name, the **global skill wins** — the opposite of most runtimes. Keep names unique across scopes.
- Naming: kebab-case, descriptive (`aws-cdk-deploy`, not `aws`, `my_skill`, or `DeployToAWS`).
- Descriptions: start with action verbs, include trigger phrases and specific file types, tools, or domains; test with varied phrasings of real requests.
- Cline reads `SKILL.md` sequentially — front-load the common cases and use clear section headers so it can scan for relevant sections.
- Skills differ from rules (always active) by loading on demand; skills are enabled by default and can be toggled. Recent Cline releases added Agent Skills compatibility, so existing skills built for other clients work in Cline.

## Cross-runtime compatibility checklist

Apply this when one skill package targets multiple runtimes or models. The bundled structural validator (`scripts/validate_skill.py`) enforces the mechanical parts automatically — kebab-case naming, name/directory matching, the 1024-character description limit, Ghost File Rule resolution across the `references/`, `scripts/`, `assets/`, `docs/`, and `templates/` layouts, and warnings for the 500-character catalog cap, the 500-line body budget, and referenced paths that use parent-relative '..' segments, which skip existence checking, or nest deeper than one level (the single-level-deep path contract). The judgement calls (install locations, name-conflict behavior, load-bearing frontmatter) remain manual:

1. **name**: kebab-case, matches the directory name exactly, ≤ 64 characters, unique within and across installation scopes.
2. **description**: ≤ 1024 characters; front-load the key use case and trigger words; keep it as short as possible — the DeepSeek harness session catalog caps descriptions at 500 by default (catalogDescriptionMaxLength, configurable), and the bundled validator warns above 500. State when to use the skill, not what it is.
3. **SKILL.md body**: under 5k tokens (Cline's budget) and roughly 5,000 tokens as the general guidance; push detail into referenced files.
4. **File paths**: single-level-deep relative links that resolve inside the package; every referenced file exists (Ghost File Rule). Avoid instructing agents to use runtime-specific subfolder names in prose — reference actual files instead.
5. **Install locations**: document the right path per runtime (`~/.claude/skills/` for Claude Code, `.agents/skills` for Codex and DeepSeek tooling, `.cline/skills/` for Cline, Mistral's Skills editor for Vibe) without asserting them inside the skill body.
6. **Name conflicts**: Codex lists both duplicates, Cline lets the global skill win, DeepSeek harness lets the nearest layer win — never rely on shadowing; ship unique names.
7. **Scripts**: self-contained, non-interactive, with output-only context cost (works everywhere); pin one-off commands.
8. **Frontmatter**: only `name` and `description` are honored universally; runtime-specific extras (e.g. `disable-model-invocation`) are ignored elsewhere, so never put critical instructions into frontmatter keys. The specification's optional `compatibility` field is the one optional key the bundled validator shape-checks: a single string of at most 500 characters stating environment requirements (intended product, system packages, network access) — per the [format specification](https://agentskills.io/specification). The remaining optional keys (`license`, `allowed-tools`, `metadata`) are whitelisted but not shape-checked.
