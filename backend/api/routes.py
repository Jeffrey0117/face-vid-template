from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pathlib import Path
import os

from models import Download, Setting, get_db
from schemas import UrlInput, DownloadResponse, SettingUpdate, SettingsResponse
from services.scraper import scraper

router = APIRouter(prefix="/api", tags=["api"])


# ========== Queue Endpoints ==========

@router.post("/queue", response_model=List[DownloadResponse])
def add_to_queue(input: UrlInput, db: Session = Depends(get_db)):
    """新增網址到下載佇列"""
    added = []
    for url in input.urls:
        # 檢查是否已存在
        existing = db.query(Download).filter(
            Download.url == url,
            Download.status.in_(["pending", "processing"])
        ).first()
        if existing:
            continue

        download = Download(url=url, status="pending")
        db.add(download)
        db.commit()
        db.refresh(download)
        added.append(download)

    return added


@router.get("/queue", response_model=List[DownloadResponse])
def get_queue(db: Session = Depends(get_db)):
    """取得目前下載佇列"""
    return db.query(Download).filter(
        Download.status.in_(["pending", "processing"])
    ).order_by(Download.created_at.desc()).all()


@router.delete("/queue/{download_id}")
def remove_from_queue(download_id: str, db: Session = Depends(get_db)):
    """從佇列移除項目"""
    download = db.query(Download).filter(Download.id == download_id).first()
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")

    db.delete(download)
    db.commit()
    return {"message": "Removed successfully"}


@router.post("/queue/{download_id}/retry", response_model=DownloadResponse)
def retry_download(download_id: str, db: Session = Depends(get_db)):
    """重試失敗的下載"""
    download = db.query(Download).filter(Download.id == download_id).first()
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")

    download.status = "pending"
    download.error_message = None
    db.commit()
    db.refresh(download)
    return download


# ========== History Endpoints ==========

@router.get("/history", response_model=List[DownloadResponse])
def get_history(limit: int = 50, db: Session = Depends(get_db)):
    """取得下載歷史"""
    return db.query(Download).filter(
        Download.status.in_(["completed", "failed"])
    ).order_by(Download.completed_at.desc()).limit(limit).all()


@router.delete("/history")
def clear_history(db: Session = Depends(get_db)):
    """清除下載歷史"""
    db.query(Download).filter(
        Download.status.in_(["completed", "failed"])
    ).delete()
    db.commit()
    return {"message": "History cleared"}


# ========== Settings Endpoints ==========

@router.get("/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """取得設定"""
    settings = {s.key: s.value for s in db.query(Setting).all()}
    return SettingsResponse(
        download_path=settings.get("download_path", "./downloads"),
        headless_mode=settings.get("headless_mode", "false") == "true",
        auto_remove=settings.get("auto_remove", "true") == "true",
        show_notification=settings.get("show_notification", "true") == "true"
    )


@router.put("/settings", response_model=SettingsResponse)
def update_settings(update: SettingUpdate, db: Session = Depends(get_db)):
    """更新設定"""
    updates = update.model_dump(exclude_none=True)

    for key, value in updates.items():
        setting = db.query(Setting).filter(Setting.key == key).first()
        str_value = str(value).lower() if isinstance(value, bool) else value
        if setting:
            setting.value = str_value
        else:
            db.add(Setting(key=key, value=str_value))

    db.commit()
    return get_settings(db)


# ========== Videos Management Endpoints ==========

def get_download_path(db: Session) -> Path:
    """取得下載路徑"""
    setting = db.query(Setting).filter(Setting.key == "download_path").first()
    download_path = setting.value if setting else "../downloads"
    return Path(download_path)


@router.get("/videos")
def list_videos(db: Session = Depends(get_db)):
    """列出所有下載的影片"""
    download_path = get_download_path(db)

    if not download_path.exists():
        return []

    videos = []
    video_extensions = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}

    for file in download_path.iterdir():
        if file.is_file() and file.suffix.lower() in video_extensions:
            stat = file.stat()
            videos.append({
                "filename": file.name,
                "size": stat.st_size,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime
            })

    # 按修改時間排序，最新的在前
    videos.sort(key=lambda x: x["modified_at"], reverse=True)
    return videos


@router.get("/videos/{filename}")
def get_video(filename: str, db: Session = Depends(get_db)):
    """串流影片檔案"""
    download_path = get_download_path(db)
    file_path = download_path / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Video not found")

    # 安全檢查：確保檔案在下載目錄內
    try:
        file_path.resolve().relative_to(download_path.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename
    )


@router.put("/videos/{filename}/rename")
def rename_video(filename: str, new_name: str, db: Session = Depends(get_db)):
    """重命名影片檔案"""
    download_path = get_download_path(db)
    old_path = download_path / filename

    if not old_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    # 確保新名稱有副檔名
    new_name = new_name.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New name cannot be empty")

    # 保留原始副檔名
    old_ext = old_path.suffix
    if not new_name.lower().endswith(old_ext.lower()):
        new_name = new_name + old_ext

    new_path = download_path / new_name

    # 檢查新檔名是否已存在
    if new_path.exists() and new_path != old_path:
        raise HTTPException(status_code=400, detail="A file with this name already exists")

    # 安全檢查
    try:
        new_path.resolve().relative_to(download_path.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid filename")

    os.rename(old_path, new_path)

    return {"message": "Renamed successfully", "new_filename": new_name}


@router.delete("/videos/{filename}")
def delete_video(filename: str, db: Session = Depends(get_db)):
    """刪除影片檔案"""
    download_path = get_download_path(db)
    file_path = download_path / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    # 安全檢查
    try:
        file_path.resolve().relative_to(download_path.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    os.remove(file_path)
    return {"message": "Deleted successfully"}


# ========== Scraper Endpoints ==========

@router.get("/scrape/{username}")
def scrape_account(username: str, max_reels: int = 50):
    """爬取帳號的所有 Reels URL"""
    # 清理 username
    username = username.strip().lstrip("@")

    if not username:
        raise HTTPException(status_code=400, detail="請輸入帳號名稱")

    result = scraper.get_reels_urls(username, max_reels=max_reels)

    if "error" in result and result.get("urls", []) == []:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/scrape/{username}/download")
def scrape_and_queue(username: str, max_reels: int = 50, db: Session = Depends(get_db)):
    """爬取帳號的 Reels 並全部加入下載佇列"""
    username = username.strip().lstrip("@")

    if not username:
        raise HTTPException(status_code=400, detail="請輸入帳號名稱")

    # 爬取 URLs
    result = scraper.get_reels_urls(username, max_reels=max_reels)

    if "error" in result and not result.get("urls"):
        raise HTTPException(status_code=400, detail=result["error"])

    urls = result.get("urls", [])
    added = []

    for url in urls:
        # 檢查是否已存在
        existing = db.query(Download).filter(
            Download.url == url,
            Download.status.in_(["pending", "processing"])
        ).first()

        if existing:
            continue

        download = Download(url=url, status="pending")
        db.add(download)
        db.commit()
        db.refresh(download)
        added.append(download)

    return {
        "username": username,
        "found": len(urls),
        "added": len(added),
        "skipped": len(urls) - len(added),
        "downloads": [{"id": d.id, "url": d.url} for d in added[:10]]  # 只返回前 10 個
    }
