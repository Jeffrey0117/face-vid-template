from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import re


class UrlInput(BaseModel):
    urls: List[str]

    @field_validator('urls')
    @classmethod
    def validate_urls(cls, v):
        pattern = r'https?://(www\.)?instagram\.com/(reel|reels|p)/[\w-]+'
        validated = []
        for url in v:
            url = url.strip()
            if url and re.match(pattern, url):
                validated.append(url)
        if not validated:
            raise ValueError('No valid Instagram Reel URLs provided')
        return validated


class DownloadResponse(BaseModel):
    id: str
    url: str
    status: str
    filename: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    download_path: Optional[str] = None
    headless_mode: Optional[bool] = None
    auto_remove: Optional[bool] = None
    show_notification: Optional[bool] = None


class SettingsResponse(BaseModel):
    download_path: str
    headless_mode: bool
    auto_remove: bool
    show_notification: bool


class StatusUpdate(BaseModel):
    type: str = "status_update"
    id: str
    url: str
    status: str
    progress: Optional[str] = None
    filename: Optional[str] = None
    error_message: Optional[str] = None
