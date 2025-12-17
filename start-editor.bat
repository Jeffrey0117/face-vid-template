@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =====================================
echo   模板文字編輯器
echo =====================================
echo.

python template_editor_server.py
pause
