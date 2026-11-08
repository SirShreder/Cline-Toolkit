# PowerShell 5.1 Config & Data Stores — Official Documentation

URLs for the cmdlets, about topics, .NET APIs, and Win32 APIs cited by `powershell-51-config-data`. Load this file only when verification or details are needed, not for code generation.

## Encoding

- about_Character_Encoding (per-cmdlet defaults in PowerShell 5.1): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1

## Registry

- New-ItemProperty: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-itemproperty?view=powershell-5.1
- Set-ItemProperty: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-itemproperty?view=powershell-5.1
- Invoke-Command (remote registry edits): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/invoke-command?view=powershell-5.1

## CSV

- Import-Csv: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/import-csv?view=powershell-5.1
- Export-Csv: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/export-csv?view=powershell-5.1

## JSON

- ConvertFrom-Json: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertfrom-json?view=powershell-5.1
- ConvertTo-Json: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertto-json?view=powershell-5.1

## XML

- Select-Xml: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-xml?view=powershell-5.1
- Get-Content (XML loading): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-content?view=powershell-5.1
- System.IO.Path.Combine (.NET; schema path resolution): https://learn.microsoft.com/en-us/dotnet/api/system.io.path.combine
- XmlDocument.Save (.NET): https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmldocument.save

## PSD1 Data Files

- Import-PowerShellDataFile: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/import-powershelldatafile?view=powershell-5.1
- Import-LocalizedData (localized strings): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/import-localizeddata?view=powershell-5.1

## Clixml

- Export-Clixml: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/export-clixml?view=powershell-5.1
- Import-Clixml: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/import-clixml?view=powershell-5.1

## Environment Variables (.NET API)

- Environment.SetEnvironmentVariable: https://learn.microsoft.com/en-us/dotnet/api/system.environment.setenvironmentvariable

## INI (Win32 Profile API)

- GetPrivateProfileStringW: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getprivateprofilestringw
- WritePrivateProfileStringW: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-writeprivateprofilestringw
