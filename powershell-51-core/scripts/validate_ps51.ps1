<#
.SYNOPSIS
Fail-closed static validation of PowerShell 5.1 script and module files.

.DESCRIPTION
Parses each input file under the Windows PowerShell 5.1 language grammar and,
when the PSScriptAnalyzer module is available, runs static analysis at Error
and Warning severity. PSScriptAnalyzer is not preinstalled with Windows; when
it is absent the parse check still runs and the result states that analysis
was skipped. Emits one JSON object and exits 0 only when every file passed;
any finding, missing file, or harness error exits 1. Static analysis does not
verify cmdlet availability (Join-String is invisible to it) - cmdlet
availability requires a dry-run under powershell.exe.

.NOTES
Part of the powershell-51-core skill (Cline deployment). Install this file as
validate_ps51.ps1 in the skill's scripts/ folder.

.PARAMETER Path
Literal paths of the .ps1 or .psm1 files to validate. Files are read from
disk; pasted script text is not accepted, so the validated state is always
the delivered artifact, never an in-session copy.

.EXAMPLE
powershell.exe -NoProfile -NonInteractive -File .\scripts\validate_ps51.ps1 -Path .\Admin.psm1, .\Services.psm1
#>
#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string[]]$Path
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$analyzerRan = $false
$results = @()

try {
    $analyzerModule = Get-Module -ListAvailable -Name PSScriptAnalyzer
    if ($null -ne $analyzerModule) {
        Import-Module -Name PSScriptAnalyzer
        $analyzerRan = $true
    }

    foreach ($file in $Path) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            $results += [PSCustomObject]@{
                File = $file
                Status = 'Failed'
                Findings = @(
                    [PSCustomObject]@{
                        Line = 0
                        Severity = 'Harness'
                        Message = 'File not found or is not a file.'
                    }
                )
            }
            continue
        }

        $fullPath = (Resolve-Path -LiteralPath $file).Path
        $tokens = $null
        $parseErrors = $null
        $null = [System.Management.Automation.Language.Parser]::ParseFile($fullPath, [ref]$tokens, [ref]$parseErrors)

        $findings = @()
        if (@($parseErrors).Count -gt 0) {
            $findings = @($parseErrors | ForEach-Object {
                [PSCustomObject]@{
                    Line = $_.Extent.StartLineNumber
                    Severity = 'ParseError'
                    Message = $_.Message
                }
            })
        }

        if ($analyzerRan) {
            $issues = Invoke-ScriptAnalyzer -Path $fullPath -Severity Error, Warning
            if (@($issues).Count -gt 0) {
                $findings = @($findings + @($issues | ForEach-Object {
                    [PSCustomObject]@{
                        Line = $_.Line
                        Severity = $_.Severity
                        Message = $_.Message
                    }
                }))
            }
        }

        $status = 'Passed'
        if (@($findings).Count -gt 0) {
            $status = 'Failed'
        }

        $results += [PSCustomObject]@{
            File = $file
            Status = $status
            Findings = $findings
        }
    }
}
catch {
    $errorMessage = $_.Exception.Message
    $results = @(
        [PSCustomObject]@{
            File = ''
            Status = 'Failed'
            Findings = @(
                [PSCustomObject]@{
                    Line = 0
                    Severity = 'Harness'
                    Message = $errorMessage
                }
            )
        }
    )
}

$failedCount = @($results | Where-Object { $_.Status -eq 'Failed' }).Count
$summary = [PSCustomObject]@{
    AnalyzerRan = $analyzerRan
    FailedCount = $failedCount
    Files = $results
}

Write-Output ($summary | ConvertTo-Json -Depth 5)

if ($failedCount -gt 0) {
    exit 1
}
exit 0