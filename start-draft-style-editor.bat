@echo off
chcp 65001 >nul
echo ========================================
echo   Long Video Draft Subtitle Style Editor
echo ========================================
echo.
cd /d "%~dp0"
python draft_style_editor_server.py
pause
