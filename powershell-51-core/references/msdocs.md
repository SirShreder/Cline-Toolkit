# PowerShell 5.1 Core — Official Documentation

URLs for the about topics, cmdlets, and documented behaviors that `powershell-51-core`'s rules depend on. Load this file only when verification or details are needed, not for code generation.

## Portals

- Microsoft Learn — PowerShell documentation: https://learn.microsoft.com/en-us/powershell/

## Language & Syntax

- about_Command_Syntax: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_command_syntax?view=powershell-5.1
- about_Operators: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_operators?view=powershell-5.1
- about_Pipeline_Chain_Operators (documents the PS 7+ `&&` / `||` operators): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipeline_chain_operators

## Automatic & Preference Variables

- about_Automatic_Variables: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables?view=powershell-5.1
- about_Preference_Variables: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables?view=powershell-5.1
- about_PowerShell_exe (`powershell.exe` command-line syntax; `-Version` valid values are 2.0 and 3.0 only): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe?view=powershell-5.1

## Encoding, Documentation & Localization

- about_Character_Encoding (per-cmdlet defaults in PowerShell 5.1): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1
- about_Comment_Based_Help: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_comment_based_help?view=powershell-5.1
- Import-LocalizedData: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/import-localizeddata?view=powershell-5.1

## Cmdlets Cited by Rules

- Invoke-WebRequest (TLS 1.2 rule): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest?view=powershell-5.1
- Invoke-RestMethod (TLS 1.2 rule): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod?view=powershell-5.1
- Get-Content (encoding rule): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-content?view=powershell-5.1
- Set-Content (encoding rule): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-content?view=powershell-5.1
- Out-File (encoding rule): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/out-file?view=powershell-5.1
- Join-Path (path handling): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/join-path?view=powershell-5.1
- Test-Path (parenthesized command calls): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/test-path?view=powershell-5.1
- Export-Clixml (DPAPI credential export): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/export-clixml?view=powershell-5.1
- Import-Clixml (DPAPI credential import): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/import-clixml?view=powershell-5.1
- Set-AuthenticodeSignature (script signing): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-authenticodesignature?view=powershell-5.1
- Invoke-ScriptAnalyzer (PSScriptAnalyzer; CI gate): https://learn.microsoft.com/en-us/powershell/module/psscriptanalyzer/invoke-scriptanalyzer?view=powershell-5.1
- ConvertTo-Json (structured logs): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertto-json?view=powershell-5.1
- Export-Csv (structured logs): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/export-csv?view=powershell-5.1

## Documented Behavior References

- `New-Item -Path` globbing behavior when combined with `-Name` (PowerShell/PowerShell#17106): https://github.com/PowerShell/PowerShell/issues/17106
- Parser.ParseFile (System.Management.Automation.Language, PowerShell SDK): https://learn.microsoft.com/en-us/dotnet/api/system.management.automation.language.parser.parsefile?view=powershellsdk-7.6.0
