# Silver Tier Digital FTE - Windows Task Scheduler Setup
#
# This PowerShell script sets up scheduled tasks for the Digital FTE system.
#
# Usage:
#   Run as Administrator:
#   powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1
#
# Author: Digital FTE System
# Date: 2026-02-13

# Require Administrator privileges
#Requires -RunAsAdministrator

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Silver Tier Digital FTE - Scheduler Setup (Windows)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$ProjectDir = Get-Location
Write-Host "Project Directory: $ProjectDir" -ForegroundColor Yellow
Write-Host ""

# Check if Python is installed
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor White
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.13+" -ForegroundColor Red
    exit 1
}

# Check if run_agent.py exists
Write-Host "[2/5] Checking run_agent.py..." -ForegroundColor Green
if (Test-Path "run_agent.py") {
    Write-Host "  Found: run_agent.py" -ForegroundColor White
} else {
    Write-Host "  ERROR: run_agent.py not found in current directory" -ForegroundColor Red
    exit 1
}

# Update XML files with current directory
Write-Host "[3/5] Updating task XML files with current directory..." -ForegroundColor Green

$xmlFiles = @(
    "scheduler\windows\run_watchers.xml",
    "scheduler\windows\ceo_report.xml"
)

foreach ($xmlFile in $xmlFiles) {
    if (Test-Path $xmlFile) {
        $content = Get-Content $xmlFile -Raw
        $content = $content -replace 'C:\\Users\\SEVEN86 COMPUTES\\hackthon-0\\silver-tier', $ProjectDir
        Set-Content $xmlFile -Value $content
        Write-Host "  Updated: $xmlFile" -ForegroundColor White
    } else {
        Write-Host "  WARNING: $xmlFile not found" -ForegroundColor Yellow
    }
}

# Import scheduled tasks
Write-Host "[4/5] Importing scheduled tasks..." -ForegroundColor Green

# Create DigitalFTE folder in Task Scheduler
$taskFolder = "\DigitalFTE"
try {
    $schedule = New-Object -ComObject Schedule.Service
    $schedule.Connect()
    $rootFolder = $schedule.GetFolder("\")

    try {
        $rootFolder.GetFolder($taskFolder)
        Write-Host "  Task folder already exists: $taskFolder" -ForegroundColor White
    } catch {
        $rootFolder.CreateFolder($taskFolder)
        Write-Host "  Created task folder: $taskFolder" -ForegroundColor White
    }
} catch {
    Write-Host "  WARNING: Could not create task folder" -ForegroundColor Yellow
}

# Import Run Watchers task
if (Test-Path "scheduler\windows\run_watchers.xml") {
    try {
        Register-ScheduledTask -Xml (Get-Content "scheduler\windows\run_watchers.xml" | Out-String) -TaskName "DigitalFTE\RunWatchers" -Force | Out-Null
        Write-Host "  Imported: RunWatchers (every 5 minutes)" -ForegroundColor White
    } catch {
        Write-Host "  ERROR: Failed to import RunWatchers task: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  ERROR: run_watchers.xml not found" -ForegroundColor Red
}

# Import CEO Report task
if (Test-Path "scheduler\windows\ceo_report.xml") {
    try {
        Register-ScheduledTask -Xml (Get-Content "scheduler\windows\ceo_report.xml" | Out-String) -TaskName "DigitalFTE\CEOReport" -Force | Out-Null
        Write-Host "  Imported: CEOReport (Monday 9:00 AM)" -ForegroundColor White
    } catch {
        Write-Host "  ERROR: Failed to import CEOReport task: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  ERROR: ceo_report.xml not found" -ForegroundColor Red
}

# Verify tasks
Write-Host "[5/5] Verifying scheduled tasks..." -ForegroundColor Green

$tasks = Get-ScheduledTask -TaskPath "\DigitalFTE\*" -ErrorAction SilentlyContinue

if ($tasks) {
    Write-Host "  Found $($tasks.Count) task(s):" -ForegroundColor White
    foreach ($task in $tasks) {
        $state = $task.State
        $stateColor = if ($state -eq "Ready") { "Green" } else { "Yellow" }
        Write-Host "    - $($task.TaskName): $state" -ForegroundColor $stateColor
    }
} else {
    Write-Host "  WARNING: No tasks found in \DigitalFTE\" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open Task Scheduler (taskschd.msc)" -ForegroundColor White
Write-Host "  2. Navigate to Task Scheduler Library > DigitalFTE" -ForegroundColor White
Write-Host "  3. Verify tasks are enabled and configured correctly" -ForegroundColor White
Write-Host "  4. Right-click a task and select 'Run' to test" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  Get-Content logs\run_agent_*.log -Tail 50" -ForegroundColor White
Write-Host ""
Write-Host "To uninstall:" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName 'DigitalFTE\RunWatchers' -Confirm:`$false" -ForegroundColor White
Write-Host "  Unregister-ScheduledTask -TaskName 'DigitalFTE\CEOReport' -Confirm:`$false" -ForegroundColor White
Write-Host ""
