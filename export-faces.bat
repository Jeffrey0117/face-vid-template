@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =====================================
echo   批量導出面相
echo =====================================
echo.

python batch_export_faces.py

echo.
pause
