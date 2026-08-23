# Installed-build acceptance for Snapmaker Studio.
#
# Installs the built NSIS installer into an isolated directory, launches the
# installed application with its WebView2 opened for remote debugging, drives the
# real UI over CDP, then uninstalls and proves the machine is clean.
#
# Why this exists: every capability check before this ran against the dev server.
# That proves the feature works; it does not prove the installer ships it. This
# runs the shipped exe and the frozen sidecar.
#
# SAFETY, and these are not negotiable:
#  * Every process this script starts is tracked by PID and only those are ever
#    stopped. A Snapmaker Orca or other user process is never touched.
#  * The app runs with an isolated WebView2 profile and an isolated engine data
#    directory, so the maintainer's own library, recent files and settings are
#    neither read nor modified — which also keeps private model names out of the
#    screenshots this produces.
#  * If another Snapmaker Studio is already installed, its uninstall registry key
#    is exported first and restored afterwards.
#  * Nothing is installed to a shared location and nothing needs administrator.
#
# Usage:
#   pwsh -File tools/acceptance/run.ps1 [-Installer <path>] [-KeepInstall]

[CmdletBinding()]
param(
    [string]$Installer,
    [string]$WorkDir = (Join-Path $env:TEMP "snapstudio-acceptance"),
    [int]$DebugPort = 9333,
    [switch]$KeepInstall
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$started = @()          # every PID this script created
$checks = @()

function Add-Check($name, $ok, $detail = "") {
    $script:checks += [pscustomobject]@{ name = $name; ok = [bool]$ok; detail = $detail }
    $tag = if ($ok) { "PASS" } else { "FAIL" }
    Write-Host ("{0}  {1}{2}" -f $tag, $name, $(if ($detail) { "  — $detail" } else { "" }))
}

function Resolve-Installer {
    if ($Installer) { return (Resolve-Path $Installer).Path }
    $bundle = Join-Path $repo "desktop\src-tauri\target\release\bundle\nsis"
    $newest = Get-ChildItem $bundle -Filter "*_x64-setup.exe" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $newest) { throw "No installer found in $bundle — run `npm run release:windows` first." }
    return $newest.FullName
}

function Stop-Tracked {
    foreach ($procId in $script:started) {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 3
}

# --- prepare -----------------------------------------------------------------

$installer = Resolve-Installer
Write-Host "Installer: $installer"

$installDir = Join-Path $WorkDir "app"
$profileDir = Join-Path $WorkDir "webview-profile"
$dataDir    = Join-Path $WorkDir "engine-data"
$outDir     = Join-Path $WorkDir "evidence"
$sample     = Join-Path $repo "examples\demo_u1_showcase.3mf"
$sampleWork = Join-Path $WorkDir "demo_u1_showcase.3mf"

foreach ($d in @($WorkDir, $outDir)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
if (Test-Path $installDir) { Remove-Item $installDir -Recurse -Force -ErrorAction SilentlyContinue }

# Work on a copy so the repository fixture is provably never written to.
Copy-Item $sample $sampleWork -Force
$sampleHashBefore = (Get-FileHash $sampleWork -Algorithm SHA256).Hash

# An existing install of the same app shares the uninstall registry key. Save it.
$existing = Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall' |
    Where-Object { (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DisplayName -like '*Snapmaker Studio*' }
$backupReg = Join-Path $WorkDir "backup-uninstall.reg"
if ($existing) {
    reg export $existing.Name $backupReg /y | Out-Null
    Write-Host "Existing install detected; its registry entry was exported to $backupReg"
}

try {
    # --- install -------------------------------------------------------------
    $proc = Start-Process -FilePath $installer -ArgumentList '/S', '/NCRC', "/D=$installDir" -PassThru -Wait
    Add-Check "Scripted install completes" ($proc.ExitCode -eq 0) "exit code $($proc.ExitCode)"

    $appExe = Join-Path $installDir "snapmaker-studio-desktop.exe"
    $sidecarExe = Join-Path $installDir "snapstudio-api.exe"
    Add-Check "Application installed" (Test-Path $appExe)
    Add-Check "Frozen engine sidecar installed" (Test-Path $sidecarExe) `
        ("{0:N1} MB" -f ((Get-Item $sidecarExe -ErrorAction SilentlyContinue).Length / 1MB))
    Add-Check "Uninstaller installed" (Test-Path (Join-Path $installDir "uninstall.exe"))

    # --- launch --------------------------------------------------------------
    $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = "--remote-debugging-port=$DebugPort --remote-allow-origins=*"
    $env:WEBVIEW2_USER_DATA_FOLDER = $profileDir
    $env:SNAPSTUDIO_DATA_DIR = $dataDir

    # Hand the project to the app the same way a file association would.
    $app = Start-Process -FilePath $appExe -ArgumentList $sampleWork -PassThru
    $script:started += $app.Id
    Start-Sleep -Seconds 10

    $alive = $null -ne (Get-Process -Id $app.Id -ErrorAction SilentlyContinue)
    Add-Check "Application launches" $alive "pid $($app.Id)"
    Add-Check "Window title" (( Get-Process -Id $app.Id).MainWindowTitle -eq "Snapmaker Studio")

    $sidecars = @(Get-CimInstance Win32_Process -Filter "Name='snapstudio-api.exe'" |
        Where-Object { $_.ExecutablePath -like "$installDir*" })
    Add-Check "Sidecar boots from the install directory" ($sidecars.Count -ge 1) `
        "$($sidecars.Count) process(es)"

    $cdp = "http://127.0.0.1:$DebugPort"
    $node = Join-Path $PSScriptRoot "checks.mjs"

    function Invoke-Phase($phase, $arg = "") {
        $out = & node $node $phase $cdp $outDir $arg 2>&1
        $out | ForEach-Object { Write-Host "    $_" }
        return $LASTEXITCODE
    }

    Add-Check "CDP reachable on the installed webview" `
        ((Invoke-WebRequest "$cdp/json/version" -UseBasicParsing -TimeoutSec 10).StatusCode -eq 200)

    $code = Invoke-Phase "startup"
    Add-Check "Startup checks" ($code -eq 0)

    $code = Invoke-Phase "routes" $sampleWork
    Add-Check "Engine routes answer from the installed sidecar" ($code -eq 0)

    # --- the project the app was launched with --------------------------------
    #
    # The native picker is deliberately not used here. It is a Win32 common
    # dialog with no DOM, and on this stack invoking it without real user input
    # blocks without ever creating a window — verified by enumerating every
    # top-level window while the call was pending. No UI-automation client can
    # reach a window that does not exist, so the app instead accepts a model on
    # its command line, which a file association needs anyway.
    $code = Invoke-Phase "launch-file"
    Add-Check "Model passed on the command line is open" ($code -eq 0)

    Invoke-Phase "goto-compatibility" | Out-Null
    Start-Sleep -Seconds 4

    $code = Invoke-Phase "ui"
    Add-Check "Project opens and its findings render" ($code -eq 0)

    # --- prepare a copy -------------------------------------------------------
    Invoke-Phase "prepare" | Out-Null
    Start-Sleep -Seconds 3
    $code = Invoke-Phase "prepared"
    Add-Check "Prepare, fidelity, ledger and best-tool render" ($code -eq 0)

    $code = Invoke-Phase "colours"
    Add-Check "Colour plan renders on its own page" ($code -eq 0)

    $sampleHashAfter = (Get-FileHash $sampleWork -Algorithm SHA256).Hash
    Add-Check "Original file is byte-identical afterwards" `
        ($sampleHashBefore -eq $sampleHashAfter)

    # --- close and prove no orphan -------------------------------------------
    Stop-Tracked
    $script:started = @()
    $orphans = @(Get-CimInstance Win32_Process -Filter "Name='snapstudio-api.exe'" |
        Where-Object { $_.ExecutablePath -like "$installDir*" })
    Add-Check "No orphan sidecar after close" ($orphans.Count -eq 0) `
        "$($orphans.Count) left running"

    # --- reopen ---------------------------------------------------------------
    $again = Start-Process -FilePath $appExe -PassThru
    $script:started += $again.Id
    Start-Sleep -Seconds 8
    Add-Check "Reopens cleanly" ($null -ne (Get-Process -Id $again.Id -ErrorAction SilentlyContinue))
    Stop-Tracked
    $script:started = @()
}
finally {
    Stop-Tracked
    Remove-Item Env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS -ErrorAction SilentlyContinue
    Remove-Item Env:WEBVIEW2_USER_DATA_FOLDER -ErrorAction SilentlyContinue
    Remove-Item Env:SNAPSTUDIO_DATA_DIR -ErrorAction SilentlyContinue
}

# --- uninstall ---------------------------------------------------------------
if (-not $KeepInstall) {
    $uninstaller = Join-Path $installDir "uninstall.exe"
    if (Test-Path $uninstaller) {
        $u = Start-Process -FilePath $uninstaller -ArgumentList '/S' -PassThru -Wait
        Start-Sleep -Seconds 3
        Add-Check "Uninstall completes" ($u.ExitCode -eq 0) "exit code $($u.ExitCode)"
        $leftovers = @(Get-ChildItem $installDir -Recurse -File -ErrorAction SilentlyContinue)
        Add-Check "Install directory removed" ($leftovers.Count -eq 0) "$($leftovers.Count) file(s) left"
        $stillRunning = @(Get-CimInstance Win32_Process -Filter "Name='snapstudio-api.exe'" |
            Where-Object { $_.ExecutablePath -like "$installDir*" })
        Add-Check "No sidecar survives uninstall" ($stillRunning.Count -eq 0)
    }
    # Put the maintainer's own uninstall entry back exactly as it was.
    if ($existing -and (Test-Path $backupReg)) {
        reg import $backupReg 2>&1 | Out-Null
        $restored = Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall' |
            Where-Object { (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DisplayName -like '*Snapmaker Studio*' }
        Add-Check "Pre-existing install registration restored" ($null -ne $restored)
    }
}

# --- report -------------------------------------------------------------------
$passed = @($checks | Where-Object ok).Count
$total = $checks.Count
$report = [pscustomobject]@{
    schema_version = "acceptance/1"
    installer      = $installer
    checks         = $checks
    passed         = $passed
    total          = $total
    evidence       = $outDir
}
$reportPath = Join-Path $outDir "acceptance.json"

# The repository's own rules forbid local paths and usernames in tracked files,
# and this report is meant to be committed as release evidence. Replace them
# here rather than remembering to do it by hand later.
$json = $report | ConvertTo-Json -Depth 5
foreach ($pair in @(
    @{ from = $repo;      to = "<repo>" },
    @{ from = $WorkDir;   to = "<workdir>" },
    @{ from = $env:TEMP;  to = "<temp>" },
    @{ from = $env:USERNAME; to = "<user>" })) {
    if ($pair.from) {
        $json = $json.Replace($pair.from.Replace('\', '\\'), $pair.to)
        $json = $json.Replace($pair.from, $pair.to)
    }
}
$json | Set-Content $reportPath -Encoding utf8

Write-Host ""
Write-Host "$passed/$total checks passed"
Write-Host "Evidence and screenshots: $outDir"
if ($passed -ne $total) { exit 1 }
