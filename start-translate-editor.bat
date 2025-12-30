@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =====================================
echo   翻譯專案編輯器
echo =====================================
echo.

python translate_editor_server.py

pause
