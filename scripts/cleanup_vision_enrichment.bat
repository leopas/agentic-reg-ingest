@echo off
REM SPDX-License-Identifier: MIT
REM Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

REM Script wrapper para Windows

cd /d "%~dp0\.."

echo.
echo ========================================
echo   CLEANUP: Vision Enrichment
echo ========================================
echo.

python scripts/cleanup_vision_enrichment.py %*

