@echo off
chcp 65001 >nul
title YouTube 翻譯工作流程

echo ================================================
echo   YouTube 影片翻譯工作流程
echo   Whisper 語音識別 + DeepSeek 翻譯 + 剪映字幕
echo ================================================
echo.

cd /d "%~dp0"

:: 檢查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python
    pause
    exit /b 1
)

:: 檢查 DEEPSEEK_API_KEY
if "%DEEPSEEK_API_KEY%"=="" (
    echo [警告] 未設定 DEEPSEEK_API_KEY 環境變數
    echo.
    set /p DEEPSEEK_API_KEY="請輸入 DeepSeek API Key: "
)

:: 檢查影片資料夾
if not exist "backend\downloads\youtube" (
    mkdir "backend\downloads\youtube"
    echo [提示] 已建立影片資料夾: backend\downloads\youtube
)

:: 顯示待處理影片
echo.
echo [待處理影片]
dir /b "backend\downloads\youtube\*.mp4" 2>nul
dir /b "backend\downloads\youtube\*.mkv" 2>nul
dir /b "backend\downloads\youtube\*.mov" 2>nul
echo.

:: 選擇模式
echo 請選擇執行模式：
echo   1. 批量處理所有影片
echo   2. 開啟翻譯編輯器（GUI）
echo   3. 退出
echo.
set /p choice="請輸入選項 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo [開始批量翻譯]
    python translate_video.py
    echo.
    echo 處理完成！請開啟剪映查看草稿。
) else if "%choice%"=="2" (
    echo.
    echo [啟動翻譯編輯器]
    start "" http://localhost:8081/translate_editor.html
    python translate_editor_server.py
) else (
    echo 已退出
)

pause
