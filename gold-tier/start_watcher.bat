@echo off
REM Digital FTE Inbox Watcher - Windows Startup Script
REM Usage: start_watcher.bat

echo ==========================================
echo Digital FTE Inbox Watcher - Startup
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo X Python not found
    echo   Please install Python 3.13 or higher
    pause
    exit /b 1
)
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo Dependencies installed
echo.

REM Check Claude CLI
echo Checking Claude Code CLI...
claude --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Claude Code CLI not found
    echo   Please install Claude Code CLI first
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('claude --version 2^>^&1') do set claude_version=%%i
echo %claude_version%
echo.

REM Verify directory structure
echo Verifying directory structure...
if not exist "AI_Employee_Vault" (
    echo X Required directory not found: AI_Employee_Vault
    pause
    exit /b 1
)
if not exist "AI_Employee_Vault\Inbox" (
    echo X Required directory not found: AI_Employee_Vault\Inbox
    pause
    exit /b 1
)
if not exist "AI_Employee_Vault\Needs_Action" (
    echo X Required directory not found: AI_Employee_Vault\Needs_Action
    pause
    exit /b 1
)
if not exist "AI_Employee_Vault\Done" (
    echo X Required directory not found: AI_Employee_Vault\Done
    pause
    exit /b 1
)
echo All required directories exist
echo.

REM Check Dashboard
if not exist "AI_Employee_Vault\Dashboard.md" (
    echo X Dashboard.md not found
    pause
    exit /b 1
)
echo Dashboard.md found
echo.

REM Start the watcher
echo ==========================================
echo Starting Inbox Watcher...
echo ==========================================
echo.
echo Press Ctrl+C to stop
echo.

python inbox_watcher.py
