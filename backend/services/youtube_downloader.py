# -*- coding: utf-8 -*-
"""
YouTube 下載服務 - 使用 yt-dlp
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp

from api.websocket import manager


class YouTubeDownloadService:
    """YouTube 下載服務"""

    def __init__(self):
        self.download_path = Path("./downloads/youtube")
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.is_running = False
        self.current_task: Optional[Dict[str, Any]] = None
        self.queue = []
        self.history = []

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "current_task": self.current_task,
            "queue_count": len(self.queue),
            "history_count": len(self.history),
        }

    def _progress_hook(self, d: Dict[str, Any]):
        """下載進度回調"""
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').strip()
            try:
                percent = float(percent_str.replace('%', ''))
            except:
                percent = 0

            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')

            self.current_task = {
                "status": "downloading",
                "progress": percent,
                "speed": speed,
                "eta": eta,
                "filename": d.get('filename', ''),
            }

            # 發送 WebSocket 更新
            asyncio.create_task(manager.broadcast({
                "type": "yt_progress",
                "data": self.current_task
            }))

        elif d['status'] == 'finished':
            self.current_task = {
                "status": "processing",
                "progress": 100,
                "message": "正在處理...",
                "filename": d.get('filename', ''),
            }
            asyncio.create_task(manager.broadcast({
                "type": "yt_progress",
                "data": self.current_task
            }))

    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """獲取影片資訊"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "id": info.get('id'),
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "thumbnail": info.get('thumbnail'),
                    "channel": info.get('channel') or info.get('uploader'),
                    "view_count": info.get('view_count'),
                    "formats": [
                        {
                            "format_id": f.get('format_id'),
                            "ext": f.get('ext'),
                            "resolution": f.get('resolution') or f"{f.get('width', '?')}x{f.get('height', '?')}",
                            "filesize": f.get('filesize') or f.get('filesize_approx'),
                            "vcodec": f.get('vcodec'),
                            "acodec": f.get('acodec'),
                        }
                        for f in info.get('formats', [])
                        if f.get('vcodec') != 'none' or f.get('acodec') != 'none'
                    ][-10:],  # 只返回最後 10 個格式
                }
        except Exception as e:
            return {"error": str(e)}

    async def download_video(
        self,
        url: str,
        format_option: str = "best",
        extract_audio: bool = False,
    ) -> Dict[str, Any]:
        """下載影片"""
        if self.is_running:
            return {"success": False, "message": "已有下載任務進行中"}

        self.is_running = True

        try:
            # 設定下載選項
            ydl_opts = {
                'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
            }

            if extract_audio:
                # 只下載音訊
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                # 下載影片
                if format_option == "best":
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif format_option == "1080p":
                    ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]'
                elif format_option == "720p":
                    ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]'
                elif format_option == "480p":
                    ydl_opts['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]'
                else:
                    ydl_opts['format'] = format_option

                # 合併為 mp4
                ydl_opts['merge_output_format'] = 'mp4'

            # 廣播開始下載
            await manager.broadcast({
                "type": "yt_started",
                "data": {"url": url}
            })

            # 執行下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # 記錄歷史
                self.history.insert(0, {
                    "id": info.get('id'),
                    "title": info.get('title'),
                    "filename": os.path.basename(filename),
                    "url": url,
                    "status": "completed",
                })

            # 廣播完成
            await manager.broadcast({
                "type": "yt_completed",
                "data": {
                    "title": info.get('title'),
                    "filename": os.path.basename(filename),
                }
            })

            return {
                "success": True,
                "title": info.get('title'),
                "filename": os.path.basename(filename),
            }

        except Exception as e:
            error_msg = str(e)

            # 記錄失敗
            self.history.insert(0, {
                "url": url,
                "status": "failed",
                "error": error_msg,
            })

            # 廣播錯誤
            await manager.broadcast({
                "type": "yt_error",
                "data": {"error": error_msg}
            })

            return {"success": False, "error": error_msg}

        finally:
            self.is_running = False
            self.current_task = None

    def get_history(self):
        return self.history[:50]

    def clear_history(self):
        self.history = []

    def list_downloads(self):
        """列出已下載的檔案"""
        if not self.download_path.exists():
            return []

        videos = []
        video_extensions = {'.mp4', '.webm', '.mkv', '.avi', '.mp3', '.m4a'}

        for file in self.download_path.iterdir():
            if file.is_file() and file.suffix.lower() in video_extensions:
                stat = file.stat()
                videos.append({
                    "filename": file.name,
                    "size": stat.st_size,
                    "created_at": stat.st_ctime,
                })

        videos.sort(key=lambda x: x["created_at"], reverse=True)
        return videos


# 單例
youtube_service = YouTubeDownloadService()
