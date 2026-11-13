---
name: powershell-ad-enterprise
description: Use this skill for enterprise Windows automation involving Active
  Directory queries, WinRM remoting with Invoke-Command, event-log auditing, or
  domain infrastructure management. It applies in addition to
  powershell-51-core, which holds all shared PowerShell 5.1 rules; this file
  contains only the enterprise and Active Directory delta.
disabled: true
---

# PowerShell Enterprise & Directory Services (Delta Rules)

> **Prerequisite:** The `powershell-51-core` skill applies in full. This file adds only enterprise-specific rules. Shared rules (error handling, formatting, comment-based help, localization, testing, PSScriptAnalyzer) are **not** repeated here — see the core skill.

## 1. Active Directory Queries
- **Server-Side Filtering:** Always use `-Filter` or `-LDAPFilter` directly inside AD cmdlets (e.g., `Get-ADUser`). Never pull all objects into memory to filter downstream with `Where-Object`.
- **Property Limitation:** Use `-Properties` with an exact list of required properties; never `*` — minimize network overhead on Domain Controllers.

## 2. Remoting (WinRM)
- **Invoke-Command Pattern:** Run remote code with `Invoke-Command -ScriptBlock { ... }` and pass local variables via `$using:` scope.
- **No Hardcoded Computer Names:** Avoid hardcoding `-ComputerName` arguments — information disclosure (PSScriptAnalyzer `AvoidUsingComputerNameHardcoded`); resolve targets from parameters, configuration, or discovery.

## 3. Event Logging & Auditing
- **Native Cmdlets:** Use `Write-EventLog` / `New-EventLog` when system auditing is required. Create and validate the event source during installation/setup, never in hot code paths.
- **Source Validation:** Check `[System.Diagnostics.EventLog]::SourceExists($source)` before writing; note that `SourceExists` can itself throw for restricted logs or under non-admin accounts — wrap the check in `try/catch` at install time.

## 4. Service Accounts
- Prefer group Managed Service Accounts (gMSA) where the domain supports them; never fall back to plaintext passwords in scheduled tasks or scripts. (Credential basics — PSCredential objects, DPAPI-protected `Export-Clixml`, never committing exported files — live in `powershell-51-core` Section 9 and are not repeated here.)

## 5. References
- Documentation URLs for every cmdlet and topic cited in this skill (Get-ADUser, Invoke-Command, about_Remoting, Write-EventLog, New-EventLog, gMSA overview) live in `references/msdocs.md` — load it only when reference material is needed, not for code generation.
