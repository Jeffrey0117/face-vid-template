# -*- coding: utf-8 -*-
"""
Instagram 下載服務 - 使用 yt-dlp 作為備案
當 saveclip.app 方式失敗時，使用此服務下載
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp

from api.websocket import manager


class InstagramYtdlpService:
    """使用 yt-dlp 下載 Instagram 內容（備案方案）"""

    def __init__(self):
        self.download_path = Path("./downloads/instagram")
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.is_running = False
        self.current_task: Optional[Dict[str, Any]] = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "current_task": self.current_task,
            "method": "yt-dlp"
        }

    def _progress_hook(self, d: Dict[str, Any]):
        """下載進度回調"""
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').strip()
            try:
                percent = float(percent_str.replace('%', ''))
            except:
                percent = 0

            self.current_task = {
                "status": "downloading",
                "progress": percent,
                "speed": d.get('_speed_str', 'N/A'),
                "filename": d.get('filename', ''),
            }

            asyncio.create_task(manager.broadcast({
                "type": "ig_ytdlp_progress",
                "data": self.current_task
            }))

        elif d['status'] == 'finished':
            self.current_task = {
                "status": "processing",
                "progress": 100,
                "message": "正在處理...",
            }

    async def download_reel(self, url: str) -> Dict[str, Any]:
        """
        使用 yt-dlp 下載 Instagram Reel

        Args:
            url: Instagram Reel 網址

        Returns:
            下載結果
        """
        if self.is_running:
            return {"success": False, "error": "已有下載任務進行中"}

        self.is_running = True

        try:
            ydl_opts = {
                'outtmpl': str(self.download_path / '%(id)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
                'format': 'best',
            }

            await manager.broadcast({
                "type": "ig_ytdlp_started",
                "data": {"url": url}
            })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            await manager.broadcast({
                "type": "ig_ytdlp_completed",
                "data": {
                    "url": url,
                    "filename": os.path.basename(filename),
                }
            })

            return {
                "success": True,
                "filename": os.path.basename(filename),
                "method": "yt-dlp"
            }

        except Exception as e:
            error_msg = str(e)

            await manager.broadcast({
                "type": "ig_ytdlp_error",
                "data": {"url": url, "error": error_msg}
            })

            return {
                "success": False,
                "error": error_msg,
                "method": "yt-dlp"
            }

        finally:
            self.is_running = False
            self.current_task = None

    async def get_info(self, url: str) -> Dict[str, Any]:
        """獲取 Instagram 內容資訊"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "id": info.get('id'),
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "thumbnail": info.get('thumbnail'),
                    "uploader": info.get('uploader'),
                }
        except Exception as e:
            return {"error": str(e)}


# 單例
ig_ytdlp_service = InstagramYtdlpService()
