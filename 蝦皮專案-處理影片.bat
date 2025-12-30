@echo off
chcp 65001 >nul
echo ========================================
echo   蝦皮專案 - 批量處理影片
echo ========================================
echo.
echo 影片放入: videos\shopee_raw\
echo 標題會自動改成影片檔名
echo @fu_island_ 保持不變
echo.

python shopee_video.py

echo.
echo ========================================
echo 處理完成！請到剪映查看
echo ========================================
pause
