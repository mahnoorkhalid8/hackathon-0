@echo off
REM Instagram Workflow - Quick Start Script (Windows)
REM Run this to start the complete system

echo ==========================================
echo Instagram Workflow System - Starting
echo ==========================================
echo.

REM Check if folders exist
if not exist "workflow\Public" (
    echo Setting up folders...
    python ig_workflow_manager.py --setup
    echo.
)

REM Check credentials
findstr /C:"INSTAGRAM_BUSINESS_ID" ..\.env >nul 2>&1
if errorlevel 1 (
    echo ERROR: Instagram credentials not found in ..\.env
    echo Please configure your credentials first
    exit /b 1
)

echo [OK] Credentials found
echo [OK] Folders ready
echo.

REM Start public server in new window
echo Starting public image server...
start "Instagram Public Server" python public_server.py
echo [OK] Server started in new window
echo.

REM Wait for server to start
timeout /t 2 /nobreak >nul

REM Start workflow manager
echo Starting workflow manager...
echo ==========================================
echo.
python ig_workflow_manager.py
