@echo off
chcp 65001 >nul
echo 🚀 面相專案影片替換工具 - 自動啟動腳本
echo =================================================

:: 設置當前目錄為腳本所在目錄
cd /d "%~dp0"

:: 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安裝或不在系統 PATH 中
    echo 💡 請先安裝 Python 3.7 或更高版本
    echo.
    pause
    exit /b 1
)

echo ✅ Python 環境檢查完成
echo.

:: 直接執行 run.py（統一入口，包含同步面相專案到剪映草稿夾）
python run.py

:: 檢查程序執行結果
if errorlevel 1 (
    echo.
    echo ❌ 程序執行過程中發生錯誤
) else (
    echo.
    echo ✅ 程序執行完成
)

echo.
pause
