---
name: programming-rules
description: Load for any programming, code, or development task, in addition to
  ai-core-rules. The general programming core — routing to installed domain
																		  
  skills, all-languages code generation standards, quality gates (static
  analysis, testing, documentation parity), and rule maintenance.
---
# Programming Rules

Load for any programming, code, or development task, in addition to the `ai-core-rules` skill.

## 1. Skill Routing
- Route the task to an installed domain skill when one covers its stack; current mappings: Windows PowerShell 5.1 → `powershell-51-core`, plus `powershell-51-config-data` for registry, INI, XML, CSV, JSON, PSD1, environment variables, or Clixml.
																						
																													  
- No installed domain skill covers the stack (PowerShell 7+ or any other language) → the standards below..
																																																																																														  

## 2. Code Generation Standards (All Languages)
- **Complete and runnable:** no placeholders, `TODO`s, pseudo-implementations, or gaps.
- **Environment assumptions:** non-trivial code answers state OS, language/runtime version, and required modules/dependencies, and include at least one usage example with expected output.
- **Input validation:** validate untrusted input at the boundary; fail fast with actionable error messages.
- **Boring and deterministic:** prefer straightforward, deterministic solutions; infrastructure and configuration code must be idempotent and safe to re-run.
- **Security by default:** never hardcode secrets (passwords, keys, tokens); use the platform's secure credential mechanism; assume least privilege.
- **Ecosystem conventions:** follow the target language's community style guide and standard library before writing custom code.
- **Comments:** self-documenting names and structure come first; comments explain why — reasoning, decisions, constraints, workarounds, non-obvious logic — and never restate what the code does. Every new non-trivial function, class, or module carries a doc comment in the language's native format (docstring, doc comment, comment-based help); trivial members need none, and line comments are reserved for non-obvious logic. Write comments in the team's language; keep them in sync on every change (Quality Gates, Documentation parity).

## 3. Quality Gates
- **Static analysis:** run the ecosystem's standard linter/analyzer (e.g., PSScriptAnalyzer) before delivering code; address all Warning and Error severity findings.
- **Testing:** state-changing code requires stated test expectations (e.g., Pester): minimum happy path plus failure path.
- **Documentation parity:** comments and help must match the code; update them on every change. Outdated comments are worse than none.

## 4. Rule Maintenance
- **Diagnose the failure class before remediating:** A failure observed against a rule in this skill set triggers maintenance, not specificity by default. Rule absent → add it at the correct layer (`ai-core-rules`, this skill, or a domain skill); rule present but wrong or mis-scoped → fix the explanation itself, without adding specific commands; rule present but too permissive → narrow it by the minimal specific instance; rule present and correct but ignored → make it mechanically checkable (analyzer, exit code, harness) instead of adding prose. Command-level specifics are the remedy only for the third class.
