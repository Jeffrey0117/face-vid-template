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

:: 檢查配置文件是否存在
if not exist "config.json" (
    echo ⚠️  配置文件不存在，正在自動生成...
    echo.
    python setup_paths.py
    if errorlevel 1 (
        echo ❌ 配置文件生成失敗
        echo 💡 請檢查 setup_paths.py 是否存在
        echo.
        pause
        exit /b 1
    )
    echo.
    echo ✅ 配置文件生成完成
    echo.
) else (
    echo ✅ 配置文件已存在
    echo.
)

:: 檢查必要的 Python 模組
echo 🔍 檢查必要的 Python 模組...
python -c "import pyJianYingDraft" >nul 2>&1
if errorlevel 1 (
    echo ❌ 找不到 pyJianYingDraft 模組
    echo 💡 請確保 pyJianYingDraft 文件夾在當前目錄中
    echo.
    pause
    exit /b 1
)

echo ✅ Python 模組檢查完成
echo.

:: 檢查模板文件夾
if not exist "面相專案" (
    echo ⚠️  找不到模板文件夾 "面相專案"
    echo 💡 請確保模板文件夾存在於當前目錄
    echo.
)

:: 檢查影片文件夾
if not exist "videos\raw" (
    echo ⚠️  找不到影片文件夾 "videos\raw"
    echo 📁 正在創建影片文件夾...
    mkdir "videos\raw" >nul 2>&1
    echo ✅ 影片文件夾創建完成
    echo 💡 請將待處理的影片文件放入 videos\raw 文件夾
    echo.
)

:: 運行主程序
echo 🎬 啟動影片替換程序...
echo =================================================
echo.

python template_video_replacer.py

:: 檢查程序執行結果
if errorlevel 1 (
    echo.
    echo ❌ 程序執行過程中發生錯誤
) else (
    echo.
    echo ✅ 程序執行完成
)

echo.
echo =================================================
echo 🎉 腳本執行完成
echo 💡 提示：
echo    - 如需修改設置，請編輯 config.json 文件
echo    - 如需重新配置路徑，請運行 setup_paths.py
echo    - 生成的剪映草稿位於剪映軟體的草稿文件夾中
echo.
pause