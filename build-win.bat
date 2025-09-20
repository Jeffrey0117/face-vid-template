@echo off
chcp 65001>nul
echo ========================================
echo 剪映助手 Windows 打包工具
echo ========================================

REM 檢查依賴
echo.
echo [1/5] 檢查依賴...
call npm list electron-builder >nul 2>&1
if errorlevel 1 (
    echo 安裝 electron-builder...
    call npm install --save-dev electron-builder
)

REM 安裝 Python 依賴
echo.
echo [2/5] 安裝 Python 依賴...
pip install pyinstaller >nul 2>&1

REM 創建 Python 執行檔
echo.
echo [3/5] 打包 Python 腳本...
echo 創建 Python 打包規格檔案...

REM 創建 pyinstaller spec 檔案
echo # -*- mode: python ; coding: utf-8 -*- > jianying.spec
echo block_cipher = None >> jianying.spec
echo a = Analysis( >> jianying.spec
echo     ['run.py'], >> jianying.spec
echo     pathex=[], >> jianying.spec
echo     binaries=[], >> jianying.spec
echo     datas=[ >> jianying.spec
echo         ('pyJianYingDraft', 'pyJianYingDraft'), >> jianying.spec
echo         ('面相專案', '面相專案'), >> jianying.spec
echo         ('videos', 'videos'), >> jianying.spec
echo         ('config.json', '.'), >> jianying.spec
echo         ('setup_paths.py', '.'), >> jianying.spec
echo         ('template_video_replacer.py', '.'), >> jianying.spec
echo         ('batch_export_faces.py', '.') >> jianying.spec
echo     ], >> jianying.spec
echo     hiddenimports=['pyJianYingDraft'], >> jianying.spec
echo     hookspath=[], >> jianying.spec
echo     hooksconfig={}, >> jianying.spec
echo     runtime_hooks=[], >> jianying.spec
echo     excludes=[], >> jianying.spec
echo     win_no_prefer_redirects=False, >> jianying.spec
echo     win_private_assemblies=False, >> jianying.spec
echo     cipher=block_cipher, >> jianying.spec
echo     noarchive=False, >> jianying.spec
echo ) >> jianying.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) >> jianying.spec
echo exe = EXE( >> jianying.spec
echo     pyz, >> jianying.spec
echo     a.scripts, >> jianying.spec
echo     a.binaries, >> jianying.spec
echo     a.zipfiles, >> jianying.spec
echo     a.datas, >> jianying.spec
echo     [], >> jianying.spec
echo     name='jianying_helper', >> jianying.spec
echo     debug=False, >> jianying.spec
echo     bootloader_ignore_signals=False, >> jianying.spec
echo     strip=False, >> jianying.spec
echo     upx=True, >> jianying.spec
echo     upx_exclude=[], >> jianying.spec
echo     runtime_tmpdir=None, >> jianying.spec
echo     console=True, >> jianying.spec
echo     disable_windowed_traceback=False, >> jianying.spec
echo     argv_emulation=False, >> jianying.spec
echo     target_arch=None, >> jianying.spec
echo     codesign_identity=None, >> jianying.spec
echo     entitlements_file=None, >> jianying.spec
echo ) >> jianying.spec

echo 使用 PyInstaller 打包...
pyinstaller jianying.spec --clean --noconfirm

REM 複製 Python 執行檔到根目錄
echo.
echo [4/5] 準備打包資源...
if exist dist\jianying_helper.exe (
    copy dist\jianying_helper.exe . >nul
    echo Python 執行檔已準備完成
) else (
    echo 警告: Python 執行檔打包失敗，將使用原始 Python 腳本
)

REM 確保資源存在
if not exist assets\icon.ico (
    echo 創建預設圖標...
    python create_icon.py >nul 2>&1
)

REM 執行 Electron 打包
echo.
echo [5/5] 打包 Electron 應用程式...
set ELECTRON_BUILDER_DISABLE_CODE_SIGN=1
call npm run build-win

REM 清理臨時檔案
echo.
echo 清理臨時檔案...
if exist jianying.spec del jianying.spec
if exist build rd /s /q build
if exist jianying_helper.exe del jianying_helper.exe

echo.
echo ========================================
echo 打包完成！
echo 輸出位置: dist\
echo ========================================
echo.
echo 提示: 
echo 1. 安裝檔案位於 dist\ 資料夾
echo 2. 執行 .exe 檔案即可安裝應用程式
echo 3. 如遇問題，請查看 dist\ 資料夾中的日誌檔案
echo.
pause