[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [switch]$ConfirmAuthorizedUse,
    [switch]$SystemWide,
    [switch]$CurrentUser,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if ($env:OS -ne "Windows_NT") {
    throw "This installer currently supports Windows only."
}

if ($SystemWide -and $CurrentUser) {
    throw "Use either -SystemWide or -CurrentUser, not both."
}

if (-not $WhatIfPreference -and -not $ConfirmAuthorizedUse) {
    throw "Installation requires explicit authorization. Confirm licensed use and rerun with -ConfirmAuthorizedUse."
}

$isAdmin = $false
try {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
} catch {
    $isAdmin = $false
}

if ($SystemWide -and -not $isAdmin) {
    throw "-SystemWide requires administrator privileges."
}

# Default to current-user scope. System-wide installation must be explicit.
$useSystemScope = [bool]$SystemWide

$skillRoot = Split-Path -Parent $PSScriptRoot
$fontDir = Join-Path $skillRoot "assets\fonts"
$manifestPath = Join-Path $fontDir "font-manifest.json"

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Font manifest not found: $manifestPath"
}

if ($useSystemScope) {
    $destination = Join-Path $env:WINDIR "Fonts"
    $registryPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
    $scope = "system"
} else {
    if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        throw "LOCALAPPDATA is unavailable; the current-user font directory cannot be resolved."
    }
    $destination = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
    $registryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    $scope = "current-user"
}

$manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $manifestPath | ConvertFrom-Json

$installed = @()
$alreadyInstalled = @()
$failed = @()

foreach ($font in $manifest.fonts) {
    $source = Join-Path $fontDir $font.file
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        $failed += [pscustomobject]@{
            font = $font.display_name
            error = "Bundled font file is missing: $source"
        }
        continue
    }

    $target = Join-Path $destination $font.file
    $registryName = "$($font.display_name) (TrueType)"
    $registered = $false

    if (Test-Path -LiteralPath $registryPath) {
        $registryValues = Get-ItemProperty -Path $registryPath -ErrorAction SilentlyContinue
        if ($null -ne $registryValues -and $registryValues.PSObject.Properties.Name -contains $registryName) {
            $registered = $true
        }
    }

    $filePresent = Test-Path -LiteralPath $target -PathType Leaf

    # A copied file alone does not mean the font is installed. Only skip when
    # BOTH the file and the registry entry are present.
    if ($filePresent -and $registered -and -not $Force) {
        $alreadyInstalled += $font.display_name
        continue
    }

    try {
        if ($PSCmdlet.ShouldProcess($target, "Install font $($font.display_name)")) {
            New-Item -ItemType Directory -Force -Path $destination | Out-Null
            New-Item -Path $registryPath -Force | Out-Null
            Copy-Item -LiteralPath $source -Destination $target -Force
            New-ItemProperty -Path $registryPath -Name $registryName -Value $font.file -PropertyType String -Force | Out-Null
            $installed += $font.display_name
        }
    } catch {
        $failed += [pscustomobject]@{
            font = $font.display_name
            error = $_.Exception.Message
        }
    }
}

$fontChangeBroadcast = $false
if ($installed.Count -gt 0) {
    if (-not ("FontChangeNotifier" -as [type])) {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class FontChangeNotifier
{
    [DllImport("user32.dll", SetLastError = true)]
    private static extern IntPtr SendMessageTimeout(
        IntPtr hWnd,
        uint msg,
        UIntPtr wParam,
        IntPtr lParam,
        uint flags,
        uint timeout,
        out UIntPtr result);

    public static bool Broadcast()
    {
        UIntPtr result;
        IntPtr response = SendMessageTimeout(
            new IntPtr(0xffff),
            0x001D,
            UIntPtr.Zero,
            IntPtr.Zero,
            0x0002,
            3000,
            out result);
        return response != IntPtr.Zero;
    }
}
"@
    }

    try {
        $fontChangeBroadcast = [FontChangeNotifier]::Broadcast()
    } catch {
        # Add-Type / Win32 calls can be blocked in restricted sandboxes.
        # See references/photoshop-automation-troubleshooting.md for the
        # Python ctypes fallback used to broadcast WM_FONTCHANGE.
        $fontChangeBroadcast = $false
    }
}

$result = [pscustomobject]@{
    schema_version = 1
    license_and_installation_confirmed = [bool]$ConfirmAuthorizedUse
    scope = $scope
    expected = @($manifest.fonts).Count
    installed = @($installed)
    already_installed = @($alreadyInstalled)
    failed = @($failed)
    destination = $destination
    registry_path = $registryPath
    font_change_broadcast = $fontChangeBroadcast
    restart_photoshop_required = ($installed.Count -gt 0)
    next_step = "Restart Photoshop, create a test text layer, and verify actualFont against font-manifest.json."
}

$result | ConvertTo-Json -Depth 6

if ($failed.Count -gt 0) {
    exit 1
}

exit 0
