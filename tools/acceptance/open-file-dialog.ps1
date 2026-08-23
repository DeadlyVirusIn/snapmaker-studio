# Drive the Windows file-open dialog through UI Automation.
#
# CDP reaches the WebView2 document and stops there: the picker Tauri opens is a
# Win32 common dialog with no DOM. Blind SendKeys is unreliable — focus can be
# stolen and there is no way to confirm the text landed. UI Automation exposes the
# dialog's actual control tree, so the filename edit can be located by role,
# written through the ValuePattern, and the Open button invoked by its pattern.
# That is verifiable at each step rather than hopeful.
#
# Usage: pwsh -File open-file-dialog.ps1 -OwnerPid <pid> -Path <file> [-TimeoutSec 20]

[CmdletBinding()]
param(
    [Parameter(Mandatory)][int]$OwnerPid,
    [Parameter(Mandatory)][string]$Path,
    [int]$TimeoutSec = 20
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement

function Find-Dialog {
    $cond = New-Object System.Windows.Automation.AndCondition(
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $OwnerPid)),
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::Window))
    )
    $windows = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
    foreach ($w in $windows) {
        # The picker is a modal window whose class is the Win32 common-dialog class.
        if ($w.Current.ClassName -eq "#32770") { return $w }
    }
    return $null
}

$deadline = (Get-Date).AddSeconds($TimeoutSec)
$dialog = $null
while ((Get-Date) -lt $deadline -and -not $dialog) {
    $dialog = Find-Dialog
    if (-not $dialog) { Start-Sleep -Milliseconds 300 }
}
if (-not $dialog) { throw "no file dialog appeared for pid $OwnerPid within ${TimeoutSec}s" }
Write-Host "dialog: '$($dialog.Current.Name)' class=$($dialog.Current.ClassName)"

# The filename box is the only edit control that supports ValuePattern.
$editCond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Edit)
$edits = $dialog.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCond)

$target = $null
foreach ($e in $edits) {
    $pattern = $null
    if ($e.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$pattern)) {
        if (-not $pattern.Current.IsReadOnly) { $target = $pattern; break }
    }
}
if (-not $target) { throw "the dialog exposes no writable filename field" }

$target.SetValue($Path)
Write-Host "filename set via ValuePattern"

# Invoke the Open button by pattern rather than pressing Enter, so the action is
# confirmed rather than assumed.
$btnCond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Button)
$buttons = $dialog.FindAll([System.Windows.Automation.TreeScope]::Descendants, $btnCond)
$invoked = $false
foreach ($b in $buttons) {
    $name = ($b.Current.Name -replace '&', '')
    if ($name -match '^(Open|Select|OK)$') {
        $ip = $null
        if ($b.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$ip)) {
            $ip.Invoke()
            Write-Host "invoked button '$name'"
            $invoked = $true
            break
        }
    }
}
if (-not $invoked) { throw "the dialog exposes no invokable Open button" }

# Confirm the dialog actually closed, rather than trusting the invoke.
$closed = $false
$deadline = (Get-Date).AddSeconds(10)
while ((Get-Date) -lt $deadline) {
    if (-not (Find-Dialog)) { $closed = $true; break }
    Start-Sleep -Milliseconds 250
}
if (-not $closed) { throw "the dialog is still open after invoking Open" }
Write-Host "dialog closed"
