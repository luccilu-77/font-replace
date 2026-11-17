[CmdletBinding()]
param(
    [string]$PhotoshopPath,
    [switch]$AsJson
)

$ErrorActionPreference = "Stop"
$skillRoot = Split-Path -Parent $PSScriptRoot
$fontDir = Join-Path $skillRoot "assets\fonts"
$manifestPath = Join-Path $fontDir "font-manifest.json"

function Add-PhotoshopCandidate {
    param(
        [System.Collections.Generic.List[object]]$List,
        [string]$Path,
        [string]$Source,
        [int]$Priority
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return
    }

    $expanded = [Environment]::ExpandEnvironmentVariables($Path.Trim('"'))
    if (-not (Test-Path -LiteralPath $expanded -PathType Leaf)) {
        return
    }

    $resolved = (Resolve-Path -LiteralPath $expanded).Path
    if ($List | Where-Object { $_.path -eq $resolved }) {
        return
    }

    $info = (Get-Item -LiteralPath $resolved).VersionInfo
    $versionText = $info.ProductVersion
    if ([string]::IsNullOrWhiteSpace($versionText)) {
        $versionText = $info.FileVersion
    }

    $major = 0
    if ($versionText -match '^(\d+)') {
        $major = [int]$Matches[1]
    }

    $profile = "unknown-version-smoke-test-required"
    if ($major -ge 22) {
        $profile = "standard-jsx"
    } elseif ($major -gt 0) {
        $profile = "legacy-jsx-smoke-test-required"
    }

    $List.Add([pscustomobject]@{
        path = $resolved
        source = $Source
        priority = $Priority
        product_version = $versionText
        file_version = $info.FileVersion
        major_version = $major
        compatibility_profile = $profile
    })
}

$candidates = New-Object 'System.Collections.Generic.List[object]'

Add-PhotoshopCandidate -List $candidates -Path $PhotoshopPath -Source "parameter" -Priority 1000
Add-PhotoshopCandidate -List $candidates -Path $env:PHOTOSHOP_EXE -Source "PHOTOSHOP_EXE" -Priority 900

$appPathKeys = @(
    "Registry::HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\App Paths\Photoshop.exe",
    "Registry::HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\App Paths\Photoshop.exe",
    "Registry::HKEY_LOCAL_MACHINE\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\Photoshop.exe"
)

foreach ($key in $appPathKeys) {
    if (Test-Path -LiteralPath $key) {
        try {
            $value = (Get-Item -LiteralPath $key).GetValue("")
            Add-PhotoshopCandidate -List $candidates -Path $value -Source "registry" -Priority 800
        } catch {
            # Continue with other discovery methods.
        }
    }
}

$adobeRoots = @()
if ($env:ProgramFiles) {
    $adobeRoots += (Join-Path $env:ProgramFiles "Adobe")
}
if (${env:ProgramFiles(x86)}) {
    $adobeRoots += (Join-Path ${env:ProgramFiles(x86)} "Adobe")
}

foreach ($root in ($adobeRoots | Select-Object -Unique)) {
    if (-not (Test-Path -LiteralPath $root)) {
        continue
    }

    Get-ChildItem -LiteralPath $root -Filter "Photoshop.exe" -File -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object {
            Add-PhotoshopCandidate -List $candidates -Path $_.FullName -Source "adobe-directory" -Priority 500
        }
}

$selected = $null
if ($candidates.Count -gt 0) {
    $selected = $candidates |
        Sort-Object -Property @{Expression = "priority"; Descending = $true}, @{Expression = "major_version"; Descending = $true}, @{Expression = "product_version"; Descending = $true} |
        Select-Object -First 1
}

$fontCount = 0
$fontFilesPresent = 0
$missingFontFiles = @()
if (Test-Path -LiteralPath $manifestPath) {
    $manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $manifestPath | ConvertFrom-Json
    $fontCount = @($manifest.fonts).Count
    foreach ($font in $manifest.fonts) {
        $fontPath = Join-Path $fontDir $font.file
        if (Test-Path -LiteralPath $fontPath -PathType Leaf) {
            $fontFilesPresent++
        } else {
            $missingFontFiles += $font.file
        }
    }
}

$guidance = $null
if ($null -eq $selected) {
    $guidance = "Adobe Photoshop was not detected. Install Photoshop through Adobe Creative Cloud, launch it once, and rerun this check. For a custom install, pass -PhotoshopPath or set PHOTOSHOP_EXE. Native editable-text PSD delivery is blocked until Photoshop is available."
}

$result = [pscustomobject]@{
    schema_version = 1
    checked_at = (Get-Date).ToString("o")
    platform = [pscustomobject]@{
        os = [Environment]::OSVersion.VersionString
        is_windows = ($env:OS -eq "Windows_NT")
        powershell_version = $PSVersionTable.PSVersion.ToString()
    }
    photoshop = [pscustomobject]@{
        found = ($null -ne $selected)
        selected = $selected
        candidates = $candidates.ToArray()
        guidance = $guidance
    }
    bundled_fonts = [pscustomobject]@{
        manifest = $manifestPath
        expected = $fontCount
        present = $fontFilesPresent
        complete = ($fontCount -gt 0 -and $fontCount -eq $fontFilesPresent)
        missing = @($missingFontFiles)
    }
}

if ($AsJson) {
    $result | ConvertTo-Json -Depth 8
} else {
    $result
}

if ($null -eq $selected) {
    exit 2
}

if ($fontCount -eq 0 -or $fontFilesPresent -ne $fontCount) {
    exit 3
}

exit 0
