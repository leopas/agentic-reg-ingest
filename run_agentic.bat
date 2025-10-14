@echo off
REM Agentic Search Runner - Windows Wrapper
REM Usage: run_agentic.bat "seu prompt aqui"

if "%~1"=="" (
    echo.
    echo ========================================
    echo   Agentic Search - Quick Runner
    echo ========================================
    echo.
    echo Usage:
    echo   run_agentic.bat "Buscar RNs da ANS sobre prazos de atendimento"
    echo.
    echo Options:
    echo   run_agentic.bat --example       Run with example plan (PDFs/ZIPs)
    echo   run_agentic.bat --html          Run with HTML-only plan
    echo   run_agentic.bat --view PLAN_ID  View iterations
    echo   run_agentic.bat --help          Show full help
    echo.
    exit /b 1
)

if "%~1"=="--example" (
    echo Running with example plan (PDFs/ZIPs)...
    .venv\Scripts\python.exe scripts\run_agentic.py --plan-file examples\agentic_plan_example.json --debug
    exit /b 0
)

if "%~1"=="--html" (
    echo Running with HTML-only plan...
    .venv\Scripts\python.exe scripts\run_agentic.py --plan-file examples\agentic_plan_html_only.json --debug
    exit /b 0
)

if "%~1"=="--view" (
    if "%~2"=="" (
        echo Error: PLAN_ID required
        echo Usage: run_agentic.bat --view PLAN_ID
        exit /b 1
    )
    .venv\Scripts\python.exe scripts\view_agentic_iters.py %2
    exit /b 0
)

if "%~1"=="--help" (
    .venv\Scripts\python.exe scripts\run_agentic.py --help
    exit /b 0
)

REM Run with prompt
echo.
echo ========================================
echo   Agentic Search Starting...
echo ========================================
echo.
.venv\Scripts\python.exe scripts\run_agentic.py --prompt "%~1" --debug

exit /b %ERRORLEVEL%

