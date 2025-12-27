# -*- coding: utf-8 -*-
"""
Instagram yt-dlp 備案下載 API 路由
當主要的 saveclip.app 方式失敗時使用
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

from services.ig_ytdlp_downloader import ig_ytdlp_service

router = APIRouter(prefix="/api/instagram/ytdlp", tags=["instagram-ytdlp"])


class DownloadRequest(BaseModel):
    url: str


@router.post("/info")
async def get_info(request: DownloadRequest):
    """獲取 Instagram 內容資訊（使用 yt-dlp）"""
    info = await ig_ytdlp_service.get_info(request.url)
    if "error" in info:
        raise HTTPException(status_code=400, detail=info["error"])
    return info


@router.post("/download")
async def download_reel(request: DownloadRequest):
    """
    使用 yt-dlp 下載 Instagram 內容（備案方案）

    這是主要下載方式（saveclip.app）的備案。
    當主要方式失敗時，可以嘗試使用此 API。
    """
    if ig_ytdlp_service.is_running:
        raise HTTPException(status_code=400, detail="已有下載任務進行中")

    # 在背景執行下載
    asyncio.create_task(ig_ytdlp_service.download_reel(request.url))

    return {"success": True, "message": "開始下載（使用 yt-dlp）", "method": "yt-dlp"}


@router.get("/status")
async def get_status():
    """獲取下載狀態"""
    return ig_ytdlp_service.get_status()
