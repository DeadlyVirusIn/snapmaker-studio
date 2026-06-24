# Privacy-safe capture of the embedded Model Browser inside Studio.
# Drives the app via UI Automation (accessibility), then PrintWindow with
# PW_RENDERFULLCONTENT captures ONLY the Studio window's own content (no screen scrape).
$ErrorActionPreference = "Continue"
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes,System.Drawing
Add-Type @"
using System;using System.Runtime.InteropServices;
public class W{
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
 [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out R r);
 public struct R{public int L,T,Rt,B;}
}
"@
$exe = "D:\STL Files\snapmaker-studio\desktop\src-tauri\target\release\snapmaker-studio-desktop.exe"
Get-Process snapmaker-studio-desktop,snapstudio-api -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
$p = Start-Process $exe -PassThru
Start-Sleep 9
$root = [System.Windows.Automation.AutomationElement]::RootElement
function Find($name,$base){ $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name); return $base.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $c) }
$win = $null
for($i=0;$i -lt 10 -and -not $win;$i++){ $win = Find "Snapmaker Studio" $root; if(-not $win){ Start-Sleep 1 } }
if(-not $win){ Write-Host "NO STUDIO WINDOW (UIA)" }
else {
  $hwnd = [IntPtr]$win.Current.NativeWindowHandle
  Write-Host "studio hwnd=$hwnd"
  function Click($n){ $e = Find $n $win; if($e){ try{ $ip=$e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern); $ip.Invoke(); Write-Host "clicked $n"; return $true }catch{ Write-Host "no-invoke $n" } } else { Write-Host "notfound $n" }; return $false }
  Click "Find Models" | Out-Null
  Start-Sleep 2
  Click "Printables" | Out-Null
  Start-Sleep 8
  $r = New-Object W+R; [W]::GetClientRect($hwnd,[ref]$r) | Out-Null
  $w = $r.Rt - $r.L; $h = $r.B - $r.T; Write-Host "client ${w}x${h}"
  if($w -gt 0 -and $h -gt 0){
    $bmp = New-Object System.Drawing.Bitmap $w,$h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc()
    $ok = [W]::PrintWindow($hwnd,$hdc,2)
    $g.ReleaseHdc($hdc); $g.Dispose()
    New-Item -ItemType Directory -Force "D:\STL Files\snapmaker-studio\docs\screenshots\beta13" | Out-Null
    $bmp.Save("D:\STL Files\snapmaker-studio\docs\screenshots\beta13\embedded-browser-beta13.png")
    $bmp.Dispose()
    Write-Host "PrintWindow ok=$ok saved"
  }
}
Get-Process snapmaker-studio-desktop,snapstudio-api -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "done"
