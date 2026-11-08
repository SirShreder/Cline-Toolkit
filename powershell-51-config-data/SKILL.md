---
name: powershell-51-config-data
description: Use this skill when Windows PowerShell 5.1 code reads or writes
  structured configuration and data stores — the Windows Registry, INI, XML,
  CSV, JSON, PSD1 data files, environment variables, or Clixml round-trips. It
  applies in addition to powershell-51-core, which holds all shared rules; this
  file contains only the format-specific delta.
disabled: true
---
# PowerShell 5.1 Config & Data Stores (Delta Rules)

> **Prerequisite:** The `powershell-51-core` skill applies in full (encoding/BOM, idempotency, error handling, culture-invariant parsing, structured logs). This file adds only format-specific rules.

## 1. Registry
- **Provider drives:** Use the registry provider drives (`HKLM:`, `HKCU:`) with standard cmdlets; for remote edits, run these same cmdlets via `Invoke-Command` rather than .NET remote-registry APIs.
- **Idempotency:** Read the key and value before writing — a repeated run must produce no error and no duplicates (registry instance of the Check-and-Act rule in `powershell-51-core` Section 4).
- **Property Creation:** Always specify `-PropertyType` on `New-ItemProperty`.
- **Property Modification:** Cast values explicitly on `Set-ItemProperty` (e.g., `[int]$newValue` for DWORD). `Set-ItemProperty` cannot change an existing property's type — remove and recreate with `New-ItemProperty -PropertyType` when the type must change.
- **Type is creation-only state:** The registry value type applies at creation only: pass `-PropertyType` when creating (`New-ItemProperty`); an existing value's stored type is authoritative — modify via `Set-ItemProperty` with an explicit cast, and never report a missing type parameter on modification.
- **Wrappers follow the same creation-only rule:** For any write API, cmdlet or custom wrapper alike, a type parameter on a wrapper function is optional — it applies only when the value is absent (creation), never on modification, and is never enforced through `[ValidateSet()]` on every invocation; when the value exists, the stored type is authoritative (previous bullet).
- **Error handling:** Registry access is infrastructure I/O — wrap in `try/catch` with specific handling (access denied, key not found) per core rules.

## 2. INI
- **No native cmdlets in PS 5.1.** Use the Win32 profile API via P/Invoke (`GetPrivateProfileString` / `WritePrivateProfileString`, Unicode variants) or a small, tested parser/serializer function — never ad-hoc regex/`-replace` edits of INI text.
- **Win32 API encoding caveat:** the profile API reads ANSI or UTF-16 files; it does not handle UTF-8 with BOM. Match the file's existing encoding or normalize deliberately, and document which.
- **Round-trip fidelity:** many INI writers drop comments and reformat whitespace — if comments must survive, use a comment-preserving parser and state that requirement.
- **Idempotency:** check section/key existence before writing.

## 3. XML
- **Loading:** `[xml]$doc = Get-Content -LiteralPath $path -Raw -Encoding UTF8` — never rely on `Get-Content`'s default (ANSI for BOM-less files in 5.1).
- **Querying:** `Select-Xml -XPath` with `-Namespace` for namespaced documents. PowerShell's XML adapter gives case-insensitive property access, and repeated sibling nodes become arrays — wrap node access in `@(...)` when cardinality matters.
- **Saving:** `$doc.Save($path)` honors the XML declaration's encoding (UTF-8 when no declaration exists). Do not write XML via `Out-File` / `Set-Content` — their 5.1 defaults (UTF-16LE / ANSI) corrupt the declaration and BOM.
- **Editing idempotently:** check node existence before creating; modify via DOM methods (`CreateElement`, `AppendChild`, `RemoveChild`); save once at the end.
- **Schema location paths (never relative):** Never rely on a relative schema path. An `xsi:schemaLocation` hint or a relative path passed to a validation API resolves against the document's base URI only when the reader has one; without it, resolution falls back to the process working directory or fails outright — validation then depends on where the script is launched from, which is a defect. Resolve the schema path explicitly against `$PSScriptRoot` or the XML file's directory (`[System.IO.Path]::Combine`) and pass an absolute path.

## 4. CSV
- **Export:** `Export-Csv` always with `-NoTypeInformation` (the 5.1 default writes a `#TYPE` header) and explicit `-Encoding` (the 5.1 default is ASCII — non-ASCII data becomes `?`).
- **Import:** `Import-Csv` supports `-Encoding` (available since PS 3.0) — specify it explicitly; do not rely on defaults for non-ASCII data.
- **All imported values are strings:** convert dates and numbers with invariant-culture parsing per core rules; never rely on implicit parsing.
- **Large files:** stream `Import-Csv ... | ForEach-Object ...` rather than collecting whole files into memory.
- **Append:** `-Append` does not validate header consistency — verify column layout before appending.

## 5. JSON
- **Serialize:** `ConvertTo-Json` always with explicit `-Depth` (the default of 2 silently truncates nested objects).
- **Deserialize:** `ConvertFrom-Json` in 5.1 returns `[PSCustomObject]` (no `-AsHashtable`) and collapses single-element arrays to a scalar — wrap in `@(...)` when array semantics matter.
- **Dates:** `ConvertTo-Json` emits .NET-style date strings in 5.1 — convert dates explicitly (`ToString('yyyy-MM-ddTHH:mm:ss')`, UTC normalization, or Unix epoch) for interoperability.

## 6. PSD1 Data Files
- **Loading:** Read trusted data files with `Import-PowerShellDataFile` (available in 5.1); use `Import-LocalizedData` for localized strings (per core i18n rules).
- **Statement restrictions:** `.psd1` data files may contain only allowed statement types — never place executable logic in them.

## 7. Environment Variables
- **Persistent variables:** `[Environment]::GetEnvironmentVariable($name, 'Machine'|'User')` / `[Environment]::SetEnvironmentVariable($name, $value, 'Machine'|'User')`; `$env:` only affects the current process.
- **Deletion:** Passing `$null` or an empty string to `SetEnvironmentVariable` deletes the variable.
- **Scope visibility:** Machine/User-scope changes are not visible to already-running processes via `$env:` — re-read explicitly with `[Environment]::GetEnvironmentVariable($name, $scope)`.
- **Idempotency:** read and compare the current value before writing.

## 8. Clixml (Round-Trip Serialization)
- **Type-preserving serialization:** Use `Export-Clixml` / `Import-Clixml` when object types must survive a round trip (CSV and JSON do not preserve types); this is also the mechanism for DPAPI-protected credential files per core security rules.

## 9. References
- Documentation URLs for every cmdlet, about topic, .NET API, and Win32 API cited in this skill (character encoding, CSV, JSON, XML, PSD1, Clixml, environment variables, INI profile APIs) live in `references/msdocs.md` — load it only when reference material is needed, not for code generation.
