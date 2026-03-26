@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%open_stage0_rule_review_gui.ps1" %*
exit /b %ERRORLEVEL%
