@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo =====================================
echo   YouTube 翻譯工作流程啟動器
echo =====================================
echo.
echo   此工具將協助您：
echo   1. 配置字幕樣式
echo   2. 選擇要處理的影片
echo   3. 執行 Whisper 語音識別
echo   4. 翻譯字幕為繁體中文
echo   5. 生成剪映草稿
echo.
echo =====================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.8+
    pause
    exit /b 1
)

REM 檢查設定檔
if not exist "translation_config.json" (
    echo [Info] 首次執行，將創建預設設定檔...
)

REM 檢查影片資料夾
if not exist "backend\downloads\youtube" (
    echo [Warning] 找不到 YouTube 下載資料夾
    echo [Info] 請先使用 start-studio.bat 下載 YouTube 影片
    echo.
    pause
)

echo [Info] 啟動翻譯編輯器伺服器...
echo [Info] 伺服器將在 http://localhost:8081 運行
echo [Info] 編輯器將自動開啟瀏覽器
echo.
echo 按 Ctrl+C 關閉伺服器
echo =====================================
echo.

python translate_editor_server.py

pause
