@echo off
chcp 65001 >nul
title AutoReels Backend

echo.
echo ================================================
echo     AutoReels 後端服務啟動器
echo ================================================
echo.

cd /d "%~dp0"

:: 檢查 port 8000
netstat -ano 2>nul | findstr ":8000.*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo 後端已在運行中! Port 8000 已被佔用
    echo.
    pause
    exit /b 0
)

if not exist "backend" (
    echo 錯誤: 找不到 backend 目錄
    pause
    exit /b 1
)

cd backend

echo 檢查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 找不到 Python
    pause
    exit /b 1
)
echo Python OK

echo 檢查依賴...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 安裝依賴中...
    pip install -r requirements.txt -q
)
echo 依賴 OK

echo 更新 yt-dlp...
pip install -U yt-dlp -q 2>nul
echo yt-dlp OK

echo.
echo ================================================
echo 後端啟動於 http://localhost:8000
echo 按 Ctrl+C 停止
echo ================================================
echo.

python main.py

echo.
echo 後端已停止
pause
