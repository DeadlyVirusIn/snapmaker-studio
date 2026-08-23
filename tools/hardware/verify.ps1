# Verify the installed Snapmaker Studio against a real Snapmaker U1 — read-only.
#
# Installs the release installer into an isolated directory, launches it with an
# isolated WebView2 profile and engine data directory, asks the real printer a
# fixed set of read-only questions through the app's own engine, and uninstalls.
#
# SAFETY, and these are not negotiable:
#  * Read-only. No print is started, nothing is uploaded or queued, and no
#    temperature, motion, homing, pause, resume, cancel, emergency-stop or
#    configuration call is made. The route allow-list lives in checks.mjs and is
#    asserted there before the first request.
#  * Only processes this script starts are ever stopped, tracked by PID.
#  * An existing installation's uninstall registry entry is exported and restored.
#  * The printer's address is replaced with a placeholder before anything is
#    written to the evidence file.
#
# Usage:
#   pwsh -File tools/hardware/verify.ps1 -PrinterHost <ip-or-hostname> [-Installer <path>]

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PrinterHost,
    [string]$Installer,
    [string]$WorkDir = (Join-Path $env:TEMP "snapstudio-hardware"),
    [int]$DebugPort = 9377,
    [switch]$KeepInstall
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$started = @()

function Resolve-Installer {
    if ($Installer) { return (Resolve-Path $Installer).Path }
    $bundle = Join-Path $repo "desktop\src-tauri\target\release\bundle\nsis"
    $newest = Get-ChildItem $bundle -Filter "*_x64-setup.exe" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $newest) { throw "No installer found in $bundle" }
    return $newest.FullName
}

$installer  = Resolve-Installer
$installDir = Join-Path $WorkDir "app"
$profileDir = Join-Path $WorkDir "webview-profile"
$dataDir    = Join-Path $WorkDir "engine-data"
$outDir     = Join-Path $WorkDir "evidence"
$sample     = Join-Path $repo "examples\demo_u1_showcase.3mf"
$sampleWork = Join-Path $WorkDir "demo_u1_showcase.3mf"

foreach ($d in @($WorkDir, $outDir)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
if (Test-Path $installDir) { Remove-Item $installDir -Recurse -Force -ErrorAction SilentlyContinue }
Copy-Item $sample $sampleWork -Force

$existing = Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall' |
    Where-Object { (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DisplayName -like '*Snapmaker Studio*' }
$backupReg = Join-Path $WorkDir "backup-uninstall.reg"
if ($existing) { reg export $existing.Name $backupReg /y | Out-Null }

Write-Host "Installer: $installer"
Write-Host "Printer:   <redacted in evidence>"
$code = 1
try {
    $proc = Start-Process -FilePath $installer -ArgumentList '/S', '/NCRC', "/D=$installDir" -PassThru -Wait
    if ($proc.ExitCode -ne 0) { throw "install failed with exit code $($proc.ExitCode)" }

    $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = "--remote-debugging-port=$DebugPort --remote-allow-origins=*"
    $env:WEBVIEW2_USER_DATA_FOLDER = $profileDir
    $env:SNAPSTUDIO_DATA_DIR = $dataDir

    $app = Start-Process -FilePath (Join-Path $installDir "snapmaker-studio-desktop.exe") -PassThru
    $started += $app.Id
    Start-Sleep -Seconds 12

    if (-not (Test-Path (Join-Path $PSScriptRoot "node_modules"))) {
        throw "run 'npm install' in tools/hardware first"
    }

    & node (Join-Path $PSScriptRoot "checks.mjs") "http://127.0.0.1:$DebugPort" $outDir $PrinterHost $sampleWork
    $code = $LASTEXITCODE
}
finally {
    foreach ($procId in $started) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 3
    Remove-Item Env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS -ErrorAction SilentlyContinue
    Remove-Item Env:WEBVIEW2_USER_DATA_FOLDER -ErrorAction SilentlyContinue
    Remove-Item Env:SNAPSTUDIO_DATA_DIR -ErrorAction SilentlyContinue

    if (-not $KeepInstall) {
        $uninstaller = Join-Path $installDir "uninstall.exe"
        if (Test-Path $uninstaller) {
            Start-Process -FilePath $uninstaller -ArgumentList '/S' -Wait | Out-Null
            Start-Sleep -Seconds 3
        }
        if ($existing -and (Test-Path $backupReg)) { reg import $backupReg 2>&1 | Out-Null }
    }
}

Write-Host "Evidence: $outDir"
exit $code
