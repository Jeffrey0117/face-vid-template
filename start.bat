@echo off
REM 設置控制台編碼為 UTF-8
chcp 65001 > nul

REM 設置環境變數確保 UTF-8 編碼
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 清除螢幕
cls

echo ========================================
echo   剪映助手 - 模板工作流自動化系統
echo ========================================
echo.
echo [資訊] 正在啟動應用程式...
echo [資訊] 字元編碼: UTF-8 (65001)
echo.

REM 執行 electron 應用程式
npx electron .

REM 如果程式結束，暫停以查看輸出
echo.
echo [結束] 應用程式已關閉
pause