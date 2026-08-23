# Record the 90-second demo from the running application.
#
# Nothing here is synthetic. The installed Snapmaker Studio is launched with the
# sample project, driven through the documented beats over the Chrome DevTools
# Protocol (the same mechanism the acceptance harness uses), and the real window
# is captured with FFmpeg's gdigrab. Every frame is the application.
#
# Requires: ffmpeg on PATH or passed with -FFmpeg, and the built NSIS installer.
# Uses the same isolation as tools/acceptance/run.ps1 — an isolated WebView2
# profile and engine data directory — so no personal library or recent-file names
# can appear in the recording.
#
# Usage:
#   pwsh -File tools/demo/record.ps1 [-FFmpeg <path>] [-Out <mp4>]

[CmdletBinding()]
param(
    [string]$Installer,
    [string]$FFmpeg = "ffmpeg",
    [string]$Out,
    [string]$WorkDir = (Join-Path $env:TEMP "snapstudio-demo"),
    [int]$DebugPort = 9355
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
if (-not $Out) { $Out = Join-Path $WorkDir "snapmaker-studio-demo.mp4" }
$started = @()

function Resolve-Installer {
    if ($Installer) { return (Resolve-Path $Installer).Path }
    $bundle = Join-Path $repo "desktop\src-tauri\target\release\bundle\nsis"
    $newest = Get-ChildItem $bundle -Filter "*_x64-setup.exe" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $newest) { throw "No installer found in $bundle" }
    return $newest.FullName
}

$installDir = Join-Path $WorkDir "app"
$sample     = Join-Path $repo "examples\demo_u1_showcase.3mf"
$sampleWork = Join-Path $WorkDir "demo_u1_showcase.3mf"
New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
Copy-Item $sample $sampleWork -Force
# Start from an empty engine data directory so the fix ledger in the recording
# shows this run's work rather than every previous take stacked on top of it.
Remove-Item (Join-Path $WorkDir "engine-data") -Recurse -Force -ErrorAction SilentlyContinue

if (-not (Test-Path (Join-Path $installDir "snapmaker-studio-desktop.exe"))) {
    $inst = Resolve-Installer
    Write-Host "Installing $inst"
    Start-Process -FilePath $inst -ArgumentList '/S', '/NCRC', "/D=$installDir" -Wait
}

$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = "--remote-debugging-port=$DebugPort --remote-allow-origins=*"
$env:WEBVIEW2_USER_DATA_FOLDER = Join-Path $WorkDir "webview-profile"
$env:SNAPSTUDIO_DATA_DIR = Join-Path $WorkDir "engine-data"

$recorder = $null
try {
    $app = Start-Process -FilePath (Join-Path $installDir "snapmaker-studio-desktop.exe") `
        -ArgumentList $sampleWork -PassThru
    $started += $app.Id
    Start-Sleep -Seconds 10

    # Put the window somewhere predictable so the capture is a consistent size.
    Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win {
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int t,bool r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h,IntPtr a,int x,int y,int w,int t,uint f);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
}
"@
    $handle = (Get-Process -Id $app.Id).MainWindowHandle
    [Win]::ShowWindow($handle, 9) | Out-Null      # restore, in case it opened maximised
    # Pin the window topmost at a known rectangle. gdigrab's window mode reads the
    # window DC, which for an occluded or background window can return a stale
    # frame — the first recording came out as 71 seconds of the dashboard that was
    # on screen when capture began. Capturing the screen region instead always
    # reflects what is actually displayed, and pinning the window guarantees the
    # region is the app.
    $x = 40; $y = 40; $w = 1600; $h = 1000
    [Win]::SetWindowPos($handle, [IntPtr](-1), $x, $y, $w, $h, 0x0040) | Out-Null   # HWND_TOPMOST
    [Win]::SetForegroundWindow($handle) | Out-Null
    Start-Sleep -Seconds 2

    # Capture the rectangle the window actually occupies. The requested size is in
    # logical units; on a scaled display the physical window is larger, and
    # capturing the requested size crops the right-hand side of the app.
    $rect = New-Object Win+RECT
    [Win]::GetWindowRect($handle, [ref]$rect) | Out-Null
    # GetWindowRect includes the drop shadow, which would film a strip of whatever
    # is behind the app. Inset by the shadow width and skip the title bar.
    $shadow = 8; $titleBar = 32
    $x = $rect.Left + $shadow; $y = $rect.Top + $titleBar
    $w = ($rect.Right - $rect.Left) - (2 * $shadow)
    $h = ($rect.Bottom - $rect.Top) - $titleBar - $shadow
    # x264 needs even dimensions.
    if ($w % 2) { $w-- }
    if ($h % 2) { $h-- }
    Write-Host "Capturing ${w}x${h} at ${x},${y}"

    # gdigrab captures the window itself, so nothing else on the desktop is filmed.
    # Recording lands in Matroska first: it tolerates an abruptly ended stream,
    # whereas an MP4 whose moov atom was never written is simply unplayable. The
    # file is remuxed to MP4 once the stream has been closed cleanly.
    $raw = [System.IO.Path]::ChangeExtension($Out, ".mkv")
    $log = Join-Path $WorkDir "ffmpeg.log"
    $recorder = Start-Process -FilePath $FFmpeg -PassThru -WindowStyle Hidden `
        -RedirectStandardError $log -ArgumentList @(
        "-y", "-f", "gdigrab", "-framerate", "30", "-draw_mouse", "1",
        "-offset_x", "$x", "-offset_y", "$y", "-video_size", "${w}x${h}",
        "-i", "desktop",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", $raw
    )
    $started += $recorder.Id
    Start-Sleep -Seconds 3

    Write-Host "Recording — driving the demo beats"
    & node (Join-Path $PSScriptRoot "beats.mjs") "http://127.0.0.1:$DebugPort"
    if ($LASTEXITCODE -ne 0) { throw "the demo beats failed" }

    Start-Sleep -Seconds 2
}
finally {
    # Let ffmpeg close the stream itself. A hard kill mid-write leaves a file
    # that will not play, which is indistinguishable from not recording at all.
    if ($recorder -and -not $recorder.HasExited) {
        try {
            & taskkill /PID $recorder.Id 2>&1 | Out-Null      # WM_CLOSE, not /F
        } catch { }
        $recorder.WaitForExit(15000) | Out-Null
        if (-not $recorder.HasExited) { Stop-Process -Id $recorder.Id -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2
    }
    foreach ($procId in $started) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
    Remove-Item Env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS -ErrorAction SilentlyContinue
    Remove-Item Env:WEBVIEW2_USER_DATA_FOLDER -ErrorAction SilentlyContinue
    Remove-Item Env:SNAPSTUDIO_DATA_DIR -ErrorAction SilentlyContinue
}

$raw = [System.IO.Path]::ChangeExtension($Out, ".mkv")
if (-not (Test-Path $raw)) {
    $log = Join-Path $WorkDir "ffmpeg.log"
    if (Test-Path $log) { Write-Host "--- ffmpeg log ---"; Get-Content $log -Tail 20 }
    throw "no recording was produced"
}

# Remux (no re-encode) into a normal MP4 with the index at the front.
& $FFmpeg -hide_banner -loglevel error -y -i $raw -c copy -movflags +faststart $Out
if (-not (Test-Path $Out)) { throw "the recording could not be remuxed to MP4" }

$mb = [math]::Round((Get-Item $Out).Length / 1MB, 2)
Write-Host "Recorded $Out ($mb MB)"
& $FFmpeg -hide_banner -i $Out 2>&1 | Select-String "Duration|Stream #0"
Remove-Item $raw -ErrorAction SilentlyContinue
