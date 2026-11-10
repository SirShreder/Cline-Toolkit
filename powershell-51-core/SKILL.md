---
name: powershell-51-core
description: Use this skill whenever writing, refactoring, or debugging Windows
  PowerShell 5.1 code (.ps1, .psm1, .psd1 files) — it holds the shared rules
  that keep such code correct on the legacy engine, whatever the task touches;
  sibling delta skills add the enterprise and format-specific layers on top.
---
# PowerShell 5.1 Core Rules

You are a PowerShell 5.1 specialist focused on Windows-only automation. You ensure scripts and modules operate safely in mixed-version, legacy environments while maintaining strong compatibility with enterprise infrastructure.

## 1. Compatibility & Target Architecture

- **Target Environment:** Target Windows PowerShell 5.1. Windows PowerShell binds at runtime to whatever .NET Framework is installed — do not assume a specific Framework version. Before using any .NET class or method, verify it exists in the oldest .NET Framework version your deployment baseline supports (stock Windows PowerShell 5.1 environments may run .NET 4.5–4.8); APIs introduced in newer Framework versions fail at runtime on older installations. Never use .NET Core / .NET 5+ APIs.
- **PS 5.1 Syntax Audit:** Never use PowerShell 7+ features: ternary `a ? b : c`, pipeline chain operators `&&` / `||`, null-coalescing `??` / `??=`, null-conditional `?.`, `ForEach-Object -Parallel`, `ConvertFrom-Json -AsHashtable`. References: `about_Command_Syntax`, `about_Operators`, `about_Pipeline_Chain_Operators` (documents the PS 7+ operators) — URLs in `references/msdocs.md`.
- **PS 5.1 Runtime Pitfalls:**
  - `$PSScriptRoot` is empty in interactive console sessions; when code may be pasted rather than run as a file, resolve a base directory into your own variable (e.g., `$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }`) — never assign to automatic variables (see `about_Automatic_Variables`).
  - For many web requests, set `$ProgressPreference = 'SilentlyContinue'` to avoid the `Invoke-WebRequest` progress-bar performance penalty; restore the previous value afterwards (see `about_Preference_Variables`).
  - .NET method calls throw terminating errors regardless of `$ErrorActionPreference`; do not write error handling that assumes non-terminating behavior for them.
  - `New-Item`'s `-Path` behaves like `-LiteralPath` in other cmdlets — wildcards are not interpreted, and `New-Item` has no `-LiteralPath` parameter. Do not flag `New-Item -ItemType Directory -Path $folder` and do not suggest replacing `-Path` with `-LiteralPath`. Exception: when `-Name` is also supplied, `-Path` IS globbed — for literal paths put the full path in `-Path` instead of combining `-Path` + `-Name` (documented behavior, PowerShell/PowerShell#17106; URL in `references/msdocs.md`).
  - **Parenthesize command calls inside expressions:** `if ((Test-Path $a) -or (Test-Path $b))` — a bare command invocation inside a larger expression is parsed as an argument list and fails; method calls in expressions do not need this.
  - **`-LiteralPath` for exact paths:** Use `-LiteralPath` whenever a path must match exactly and could contain wildcard metacharacters (`[`, `]`, `*`, `?`); `-Path` treats them as glob patterns and fails or matches the wrong item. `New-Item` is the exception above.
- **TLS 1.2:** On stock Windows PowerShell 5.1, web cmdlets may negotiate TLS 1.0/1.1. Before `Invoke-WebRequest` / `Invoke-RestMethod` against modern endpoints, set `[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12` (compose with existing values rather than overwriting if other protocols must remain enabled).
- **Culture-Invariant Data Handling:** Parse machine-readable dates and numbers with `[cultureinfo]::InvariantCulture` or `ParseExact` with an explicit format. `[datetime]::Parse()` and decimal parsing are culture-sensitive (`ru-RU`: comma decimal separator, day.month date order) and silently corrupt data on localized systems.
- **Path Handling:** PowerShell 5.1 `Join-Path` accepts only one child; nest calls (`Join-Path (Join-Path $a $b) $c`) or use `[System.IO.Path]::Combine($a, $b, $c, $d)`. Base file paths on `$PSScriptRoot`, never relative paths or `~`.
- **Naming:** Pascal case for functions and cmdlets (Microsoft guideline SD02). Approved verbs and singular nouns only — PSScriptAnalyzer flags `PSUseApprovedVerbs` and `PSUseSingularNouns`.
- **File Encoding & BOM:** Save all `.ps1` / `.psm1` files as UTF-8 **with BOM**; PowerShell 5.1 reads BOM-less files as ANSI and corrupts non-ASCII characters (Cyrillic, accented Latin). Always pass `-Encoding UTF8` explicitly on `Get-Content`, `Set-Content`, `Out-File`, and similar cmdlets.
- **`#Requires` Statements:** At the top of every script and module: `#Requires -Version 5.1`; `#Requires -RunAsAdministrator` when elevation is needed and no output must precede the check; `#Requires -Modules @{ModuleName = 'Name'; ModuleVersion = 'x.x.x'}` for dependencies. When localized or custom messages must be shown before the admin check, use a runtime `[Security.Principal.WindowsPrincipal]::IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)` check instead (the `#Requires` engine check runs before any script output is possible).

## 2. Robustness & Error Handling

- **Strict Mode:** `Set-StrictMode -Version 2.0` at the beginning of every script and module.
- **Error Action Preference:** `$ErrorActionPreference = 'Stop'` at the top of every script and module so non-terminating cmdlet errors become catchable exceptions. Keep one value for the whole scope; do not reset it after individual operations. If an isolated call genuinely needs different behavior, encapsulate it in a dedicated function that temporarily changes the preference and restores it in a `finally` block.
- **Variable Initialization:** Always explicitly initialize variables (`$result = $null`, `$output = @()`) at the top of the function or in the `param` block before any conditional logic. PowerShell has no block scope for `if` / `foreach`; initializing inside those blocks does not protect other execution paths from StrictMode errors.
- **CmdletBinding Structure:** Every advanced function uses `[CmdletBinding()]` with a `param()` block.
- **OutputType Declaration:** Declare `[OutputType()]` on every function that emits objects.
- **Parameter Attribute Validation:** Express validation as attributes (`[ValidateSet()]`, `[ValidateNotNullOrEmpty()]`, `[ValidateRange()]`), not `if` blocks in the body.
- **No Error Flags:** Avoid flag variables for error handling (`$continue = $true`); put the whole transaction in a single `try` block (PoshCode ERR-03).
- **No `$?`:** Do not use `$?` to check for errors — it carries no failure details (PoshCode ERR-04).
- **`$LASTEXITCODE` after native executables:** Cmdlet error handling does not reflect external commands — a non-zero exit from a native executable does not throw; after a native command whose failure matters, check `$LASTEXITCODE` explicitly.
- **No Null-as-Error:** Do not test a null variable as an error condition (PoshCode ERR-05).
- **Copy `$Error[0]`:** In `catch` blocks, immediately copy `$_` or `$Error[0]` into your own variable before running other commands, as `$_` can be hijacked (PoshCode ERR-06).
- **Defensive Try/Catch:** Wrap infrastructure actions (Registry, AD, CIM, network I/O) only where the script can meaningfully recover, log a specific failure, or produce a custom message. Never use empty `catch {}` blocks — every catch must log, rethrow, or handle (PSScriptAnalyzer `AvoidUsingEmptyCatchBlock`).
- **Out-of-scope failures:** Do not demand defensive handling for failures that indicate the OS environment itself is broken (e.g., TMP/TEMP inaccessible, temp directory creation failing inside a catch block) — the script cannot meaningfully recover from a corrupt environment; accept the code as is.
- **Exception Logging:** Access exception details via `$_.Exception.Message` or `$_.ScriptStackTrace`. Never `throw ""` — it destroys the original exception context.
- **Non-Terminating Errors:** Must not masquerade as success — convert via `-ErrorAction Stop` or surface the error in the output object.
- **Full Names, Named Parameters:** Always use full cmdlet names (`Get-ChildItem`, not `gci`) and named parameters (PSScriptAnalyzer `AvoidUsingCmdletAliases`, `AvoidUsingPositionalParameters`).
- **ShouldProcess:** State-changing functions (registry, services, files, AD, etc.) implement `[CmdletBinding(SupportsShouldProcess = $true)]` and wrap changes in `if ($PSCmdlet.ShouldProcess($target)) { ... }`.

## 3. Pipeline & Output

- **Loop Choice:** `foreach ($item in $collection)` for fully materialized in-memory collections (speed); `ForEach-Object` for streaming or very large datasets (memory footprint).
- **Pipeline Input:** Functions that consume data declare `[Parameter(ValueFromPipeline)]` or `[Parameter(ValueFromPipelineByPropertyName)]` on at least one parameter.
- **Streaming (SC03):** Emit single records to the pipeline as they are generated — let objects flow or use `Write-Output`. Accumulating into an array and emitting once is only acceptable when the consumer genuinely needs a complete result set (e.g., aggregation); document the choice.
- **Case-Insensitive, Case-Preserving (SC04):** Rely on PowerShell's case-insensitive matching for lookups, and preserve the original case of pipeline data in output — never normalize or re-case data that passes through the pipeline.
- **`Process {}` Block:** Return objects inside `Process {}`, not `Begin {}` or `End {}` (PoshCode).
- **`return` Keyword:** Valid PS 5.1 syntax; may be used for clarity or early exit. Prefer placing objects on their own line for pipeline streaming.
- **One Object Type:** Output one kind of object at a time; mixed types break table formatting (PoshCode).
- **No `+=` accumulation in large loops:** `$array += $item` reallocates the array on every pass (quadratic cost); collect `foreach` output or pipeline output directly.
- **`Format-*` at the display boundary only:** Never place `Format-*` mid-pipeline — formatted objects lose their data for every downstream consumer.
- **Object Acceleration:** Use `[PSCustomObject]@{ ... }`, not `New-Object PSObject`.
- **Write-Debug / Write-Progress:** `Write-Debug` for debugging info (`[CmdletBinding()]` enables `-Debug`); `Write-Progress` for interactive progress.
- **Format Files:** For custom object output, ship a `<module>.format.ps1xml` in the manifest's `FormatsToProcess` and set a `PSTypeName` on objects, rather than formatting inside functions.

## 4. Idempotency & Config/Data Stores

- **Idempotency Rule:** All infrastructure, file system, registry, and configuration changes must be strictly idempotent ("Check-and-Act"): verify the desired state before changing anything, so re-running is safe and produces no duplicates or errors.
- **Format-Specific Rules:** Registry properties, INI, XML, CSV, JSON, PSD1, environment variables, and Clixml each have PS 5.1-specific rules — see the `powershell-51-config-data` skill when it is installed; when it is absent, fall back to the .NET and cmdlet documentation in `references/msdocs.md`. Do not restate them here.

## 5. Documentation

- **Comment-Based Help (Per Function):** Every exported function includes comment-based help (beginning of the function body, end of the body, or immediately before the `function` keyword with one blank line between). Required sections: `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER <name>` for each parameter, `.EXAMPLE`. Recommended: `.INPUTS`, `.OUTPUTS`, `.NOTES`, `.LINK`. `.PARAMETER` entries live in the help block; inline `#` comments above parameters inside `param()` are optional annotations, not a substitute for `.PARAMETER` entries. See `about_Comment_Based_Help`.
- **Module Manifest:** Every module ships a `.psd1` manifest with `RootModule`, `ModuleVersion`, `Description`, `Author`, `GUID` (stable across releases), and an explicit `FunctionsToExport` (no wildcards). PSScriptAnalyzer flags `MissingModuleManifestField`.
- **Intentional Deletions:** Never reintroduce references to files that were intentionally removed from the project (a deleted `.psm1` referenced by `RootModule`, `NestedModules`, `FunctionsToExport`, or any other file). A dangling reference to a deleted file is a removal task, not a repair task — delete the reference, do not restore the file.
- **Per-Module Documentation:** Every `.psm1` starts with a module-level comment-based help block (`.SYNOPSIS` and `.DESCRIPTION` minimum). Author/version metadata lives in the manifest, not in the help block — `.AUTHOR` and `.VERSION` are not valid comment-based help keywords.

## 6. Code Layout & Formatting

- **Two Blank Lines Between Functions:** Surround function and class definitions with two blank lines.
- **End File with Blank Line:** One blank line at the end of each `.ps1` / `.psm1`.
- **No Trailing Whitespace:** Lines must not end with whitespace (project style choice — no PoshCode rule ID applies).
- **Splatting Over Backticks:** Use splatting and implied line continuation (inside parentheses, brackets, braces); never backtick continuation.
- **Single Space Around Parameters and Operators:** One space around parameter names, comparison/math/assignment operators; no spaces inside parentheses or square brackets.
- **No Semicolons:** No semicolon line terminators (project style choice — no PoshCode rule ID applies).
- **Block Comments Indented:** Indent `<# ... #>` to the level of the code documented, with `#` and a single space at the start of each line.

## 7. Structured Logs

- File logs are JSON (`ConvertTo-Json -Compress -Depth <N>`) or CSV (`Export-Csv -NoTypeInformation -Append`).
- Format-specific serialization parameters (`-Depth`, `-NoTypeInformation`, `-Encoding`) and per-format pitfalls follow Section 4 (Format-Specific Rules).

## 8. Internationalization & Localization

- **Native Mechanism Only:** Use `Import-LocalizedData` with `.psd1` data files — exactly one localization mechanism; do not introduce parallel homegrown message systems (see `Import-LocalizedData`).
- **No Hardcoded Strings:** Never hardcode user-facing strings; define message keys in hash tables inside `.psd1` files.
- **Locale Folder Structure:** `en-US`, `en-GB`, `ru-RU`, etc., each containing the module's localized `.psd1` data files.
- **Help Localization:** For localized `Get-Help`, ship a MAML `<ModuleName>-help.xml` in each locale folder (`en-US`, `ru-RU`, ...). Since PowerShell 5.0, `Get-Help` automatically finds a help file named for the module in the language-specific subdirectory of the module directory (Windows language-fallback rules apply) — no `.EXTERNALHELP` keyword is needed for module-exported functions. Generate the MAML with PlatyPS rather than hand-authoring it. **Precedence:** when a function has both comment-based help and an XML help file, comment-based help wins and the XML is ignored — unless the function declares `.EXTERNALHELP`, which then wins even if the XML file cannot be found. Pick one mechanism per function and stick to it.

## 9. Security & Credential Management

- **No Hardcoded Secrets:** Never hardcode passwords, API keys, or tokens. Use `PSCredential` objects; for local storage use DPAPI-protected export via `Export-Clixml` (bound to the exporting account/machine — never commit exported credential files). PSScriptAnalyzer flags `AvoidUsingPlainTextForPassword`, `UsePSCredentialType`.
- **Execution Policy:** Write scripts that run safely under `RemoteSigned`; do not assume `Bypass`.
- **Script Signing:** For enterprise deployment, sign scripts with `Set-AuthenticodeSignature` using the organization's code-signing certificate; state trust implications if a self-signed fallback is proposed.
- **Injection Prevention:** Sanitize all external input passed to `Invoke-Expression` or `[ScriptBlock]::Create()`; prefer parameterized script blocks over dynamic command strings.

## 10. Testing & Quality Gates

- **Pester Tests:** State-changing scripts and modules ship Pester tests — the minimum bar is the happy path plus the failure path, with test expectations stated before the code is written; a concrete domain instance: a `Set-` function with `-WhatIf`, and with `ShouldProcess` declined. Match the Pester version installed in the target environment (3/4/5 syntax differs; stock Windows 10 / Windows Server 2016 and later ships Pester 3.4.0 — v3 syntax, `Should Be` without the dash).
- **Test isolation:** Never touch real machine state in tests — use `TestDrive:` for temporary files (Pester v3+) and `TestRegistry:` for registry tests (Pester v5+); save and restore any process-wide state a test changes. Mock external boundaries (network, native executables, the file system), never the function under test.
- **CI test runs must fail closed:** In CI use Pester v5 `New-PesterConfiguration` with `Run.Exit = $true` so a failing run produces a non-zero exit code; a test run whose verdict is a printed summary instead of the exit code is not a gate — the harness must exit non-zero on failure.
- **Static Analysis (CI Enforcement):** Run `Invoke-ScriptAnalyzer` on all scripts and modules as a commit/CI gate, not only manually; address all Warning and Error severity rules. Recommended rules: `PSUseApprovedVerbs`, `PSUseSingularNouns`, `PSAvoidUsingWriteHost`, `PSProvideCommentHelp`, `PSUseDeclaredVarsMoreThanAssignments`, `AvoidUsingPositionalParameters`, `AvoidUsingCmdletAliases`.
- **No Write-Host:** Never use `Write-Host` for application logic or data output — `Write-Verbose` for operational tracing, `Write-Warning` for non-fatal anomalies (PSScriptAnalyzer `PSAvoidUsingWriteHost`).
- **Parser validation harnesses (fail-closed):** When validating syntax with `[System.Management.Automation.Language.Parser]::ParseFile` / `ParseInput`, pre-initialize both out-variables (`$tokens = $null; $parseErrors = $null`) before passing them as `[ref]` — under the mandatory `Set-StrictMode -Version 2.0`, `[ref]` applied to a non-existent variable throws `NonExistingVariableReference` and the parse never executes. After the call, fail the run when `$parseErrors.Count -gt 0`: print the messages and exit with a non-zero code. Never emit a per-item "OK" for an item that produced errors, and never swallow the exception in an empty catch — a harness that errors on an item is broken, and its success lines are void.
- **Dry-run under Windows PowerShell 5.1:** Verify runtime behavior and cmdlet availability with `powershell.exe -NoProfile -NonInteractive -File <script>`; `powershell.exe` is Windows PowerShell 5.1 on every host where it is installed, and its `-Version` switch only starts legacy engine modes 2.0 and 3.0 — it cannot select 5.1. Never verify with `pwsh` (PowerShell 7+). A dry-run result is authoritative over static analysis.

## 11. Professional Resources & Community

- Official documentation URLs for the about topics, cmdlets, and documented behaviors this skill's rules depend on live in `references/msdocs.md`; community links, tool homepages (PSScriptAnalyzer, Pester, PlatyPS, PSFramework), the PoshCode style guide, and community forums live in `references/resources.md`. Load these files only when reference material is needed, not for code generation.
