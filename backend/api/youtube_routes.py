# -*- coding: utf-8 -*-
"""
YouTube 下載 API 路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio

from services.youtube_downloader import youtube_service

router = APIRouter(prefix="/api/youtube", tags=["youtube"])


class DownloadRequest(BaseModel):
    url: str
    format: str = "best"  # best, 1080p, 720p, 480p
    audio_only: bool = False


class InfoRequest(BaseModel):
    url: str


@router.post("/info")
async def get_video_info(request: InfoRequest):
    """獲取影片資訊"""
    info = await youtube_service.get_video_info(request.url)
    if "error" in info:
        raise HTTPException(status_code=400, detail=info["error"])
    return info


@router.post("/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    """開始下載影片"""
    if youtube_service.is_running:
        raise HTTPException(status_code=400, detail="已有下載任務進行中")

    # 在背景執行下載
    async def do_download():
        await youtube_service.download_video(
            url=request.url,
            format_option=request.format,
            extract_audio=request.audio_only,
        )

    asyncio.create_task(do_download())

    return {"success": True, "message": "開始下載"}


@router.get("/status")
async def get_status():
    """獲取下載狀態"""
    return youtube_service.get_status()


@router.get("/history")
async def get_history():
    """獲取下載歷史"""
    return youtube_service.get_history()


@router.delete("/history")
async def clear_history():
    """清除下載歷史"""
    youtube_service.clear_history()
    return {"message": "歷史已清除"}


@router.get("/files")
async def list_files():
    """列出已下載的檔案"""
    return youtube_service.list_downloads()
