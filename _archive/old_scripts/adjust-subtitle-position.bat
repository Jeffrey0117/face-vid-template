@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 啟動字幕位置調整器...
python subtitle_position_server.py
pause
