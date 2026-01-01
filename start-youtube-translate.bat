@echo off
chcp 65001 >nul
title YouTube Translation Pipeline v2.0
color 0B

cd /d "%~dp0"

echo.
echo  ============================================================
echo       YT TRANSLATE - YouTube Video Translation Pipeline
echo  ============================================================
echo       Faster-Whisper + DeepSeek API + JianYing Draft
echo  ============================================================
echo.

:: Timestamp
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set DATESTAMP=%%a/%%b/%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIMESTAMP=%%a:%%b
echo  [%DATESTAMP% %TIMESTAMP%] Initializing...
echo.

:: Check Python
echo  [CHECK] Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [FAIL] Python not found!
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo  [OK] Python %%i
echo  [OK] Faster-Whisper engine
echo  [OK] Auto GPU/CPU fallback
echo.

:: Check video folder
if not exist "backend\downloads\youtube" (
    mkdir "backend\downloads\youtube"
    echo  [INFO] Created: backend\downloads\youtube
)

:: Count videos
echo  [INFO] Scanning for videos...
set COUNT=0
for %%f in (backend\downloads\youtube\*.mp4) do set /a COUNT+=1
for %%f in (backend\downloads\youtube\*.mkv) do set /a COUNT+=1
for %%f in (backend\downloads\youtube\*.mov) do set /a COUNT+=1
for %%f in (backend\downloads\youtube\*.webm) do set /a COUNT+=1

if %COUNT%==0 (
    echo  [WARN] No videos found in backend\downloads\youtube
    echo.
    echo  Please add video files and run again.
    echo.
    pause
    exit /b 0
)

echo  [INFO] Found %COUNT% video(s)
echo.

:: Start
echo  ============================================================
echo  [%DATESTAMP% %TIMESTAMP%] Starting translation...
echo  [INFO] Model: medium / VAD: ON / Workers: 2
echo  ============================================================
echo.

python translate_video.py

echo.
echo  ============================================================
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set ENDTIME=%%a:%%b
echo  [%DATESTAMP% %ENDTIME%] Pipeline completed
echo  ============================================================
echo.
echo  Done! Open JianYing to view generated drafts.
echo.

pause
