@echo off
chcp 65001 >nul
title 影片工作室 - Video Studio

echo ========================================
echo    影片工作室 - Video Studio
echo ========================================
echo.

:: 檢查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python
    pause
    exit /b 1
)

:: 安裝依賴（如果需要）
echo [1/3] 檢查依賴...
cd /d "%~dp0backend"
if not exist "__pycache__" (
    echo 正在安裝依賴...
    pip install -r requirements.txt -q
)

:: 啟動後端
echo [2/3] 啟動後端服務...
start /min cmd /c "cd /d %~dp0backend && python main.py"
timeout /t 2 /nobreak >nul

:: 啟動前端
echo [3/3] 開啟應用程式...
start "" "%~dp0app.html"

echo.
echo ========================================
echo    啟動完成！
echo    後端: http://localhost:8000
echo    前端: 已在瀏覽器開啟
echo ========================================
echo.
echo 按任意鍵關閉此視窗（後端會繼續運行）
pause >nul
