from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import asyncio
import os
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import threading

from models import Download, Setting, SessionLocal
from api.websocket import manager


class ServiceStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class DownloadService:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.status: ServiceStatus = ServiceStatus.IDLE
        self._stop_requested = False
        self._lock = threading.Lock()
        self.current_task: Optional[Dict[str, Any]] = None
        self.stats = {
            "completed_count": 0,
            "failed_count": 0,
            "queue_count": 0
        }

    def _get_settings(self) -> Dict[str, Any]:
        """取得設定"""
        db = SessionLocal()
        try:
            settings = {s.key: s.value for s in db.query(Setting).all()}
            return {
                "download_path": settings.get("download_path", "./downloads"),
                "headless_mode": settings.get("headless_mode", "false") == "true"
            }
        finally:
            db.close()

    def _init_driver(self, headless: bool = False):
        """初始化 WebDriver"""
        # 先確保舊的 driver 已關閉
        self._cleanup_driver()

        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # 設定下載路徑
        settings = self._get_settings()
        download_path = os.path.abspath(settings["download_path"])
        os.makedirs(download_path, exist_ok=True)

        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        }
        options.add_experimental_option("prefs", prefs)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def _cleanup_driver(self):
        """清理 WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            finally:
                self.driver = None

    async def _update_status(self, download: Download, status: str,
                             progress: str = None, progress_percent: int = None,
                             filename: str = None, error_message: str = None):
        """更新下載狀態並推播"""
        db = SessionLocal()
        try:
            db_download = db.query(Download).filter(Download.id == download.id).first()
            if db_download:
                db_download.status = status
                if filename:
                    db_download.filename = filename
                if error_message:
                    db_download.error_message = error_message
                if status in ["completed", "failed"]:
                    db_download.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

        # 更新當前任務資訊
        if status == "processing":
            self.current_task = {
                "id": download.id,
                "url": download.url,
                "progress": progress_percent or 0,
                "step": progress
            }
        elif status in ["completed", "failed"]:
            self.current_task = None

        # WebSocket 推播
        await manager.send_status_update(
            download_id=download.id,
            url=download.url,
            status=status,
            progress=progress,
            progress_percent=progress_percent,
            filename=filename,
            error_message=error_message
        )

    async def _process_download(self, download: Download) -> bool:
        """處理單一下載，返回是否成功"""
        try:
            # 20% - 開啟頁面
            await self._update_status(download, "processing", "正在開啟下載頁面...", 20)
            self.driver.get("https://saveclip.app/tw")

            # 40% - 輸入網址
            await self._update_status(download, "processing", "正在輸入網址...", 40)
            await asyncio.sleep(0.5)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#s_input"))
            )

            input_box = self.driver.find_element(By.CSS_SELECTOR, "#s_input")
            input_box.click()
            input_box.clear()
            input_box.send_keys(download.url)

            # 60% - 解析影片
            await self._update_status(download, "processing", "正在解析影片...", 60)
            search_button = self.driver.find_element(
                By.CSS_SELECTOR, "#search-form > div > div > button"
            )
            search_button.click()

            # 等待結果
            target_link = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#search-result > ul > li > div > div:nth-child(3) > a")
                )
            )

            # 80% - 下載中
            await self._update_status(download, "processing", "正在下載影片...", 80)
            target_url = target_link.get_attribute("href")
            self.driver.get(target_url)

            await asyncio.sleep(2)  # 等待下載開始

            # 100% - 完成
            filename = f"reel_{download.id[:8]}.mp4"
            await self._update_status(
                download, "completed",
                progress="下載完成", progress_percent=100,
                filename=filename
            )
            self.stats["completed_count"] += 1
            return True

        except TimeoutException:
            await self._update_status(
                download, "failed",
                error_message="解析逾時，找不到下載連結"
            )
            self.stats["failed_count"] += 1
            return False

        except WebDriverException as e:
            await self._update_status(
                download, "failed",
                error_message=f"瀏覽器異常：{str(e)[:50]}"
            )
            self.stats["failed_count"] += 1
            # 瀏覽器異常需要重啟
            self._cleanup_driver()
            return False

        except Exception as e:
            await self._update_status(
                download, "failed",
                error_message=str(e)[:100]
            )
            self.stats["failed_count"] += 1
            return False

    def _get_queue_count(self) -> int:
        """取得佇列數量"""
        db = SessionLocal()
        try:
            return db.query(Download).filter(Download.status == "pending").count()
        finally:
            db.close()

    async def start_downloads(self) -> Dict[str, Any]:
        """開始處理佇列"""
        # 使用鎖防止重複啟動
        with self._lock:
            if self.status == ServiceStatus.RUNNING:
                return {"success": False, "message": "Already running"}

            self.status = ServiceStatus.RUNNING
            self._stop_requested = False
            self.stats = {"completed_count": 0, "failed_count": 0, "queue_count": 0}

        settings = self._get_settings()

        try:
            # 初始化瀏覽器
            self._init_driver(headless=settings["headless_mode"])

            # 廣播開始下載
            await manager.broadcast({
                "type": "download_started",
                "data": {"status": "running"}
            })

            while not self._stop_requested:
                # 檢查瀏覽器是否還活著
                if not self.driver:
                    try:
                        self._init_driver(headless=settings["headless_mode"])
                    except Exception as e:
                        self.status = ServiceStatus.ERROR
                        await manager.broadcast({
                            "type": "error",
                            "data": {"message": f"無法啟動瀏覽器：{str(e)[:50]}"}
                        })
                        break

                # 取得下一個待處理項目
                db = SessionLocal()
                try:
                    download = db.query(Download).filter(
                        Download.status == "pending"
                    ).order_by(Download.created_at.asc()).first()

                    self.stats["queue_count"] = db.query(Download).filter(
                        Download.status == "pending"
                    ).count()

                    if not download:
                        break

                    # 複製資料避免 session 問題
                    download_copy = Download(
                        id=download.id,
                        url=download.url,
                        status=download.status
                    )
                finally:
                    db.close()

                await self._process_download(download_copy)
                await asyncio.sleep(1)

        except Exception as e:
            self.status = ServiceStatus.ERROR
            await manager.broadcast({
                "type": "error",
                "data": {"message": f"下載服務異常：{str(e)[:50]}"}
            })

        finally:
            self._cleanup_driver()
            self.current_task = None

            # 廣播完成
            final_status = "completed" if not self._stop_requested else "stopped"
            await manager.broadcast({
                "type": "download_finished",
                "data": {
                    "status": final_status,
                    "completed": self.stats["completed_count"],
                    "failed": self.stats["failed_count"]
                }
            })

            self.status = ServiceStatus.IDLE

        return {
            "success": True,
            "message": "Downloads completed",
            "stats": self.stats
        }

    async def stop_downloads(self) -> Dict[str, Any]:
        """停止下載"""
        if self.status != ServiceStatus.RUNNING:
            return {"success": False, "message": "Not running"}

        self.status = ServiceStatus.STOPPING
        self._stop_requested = True

        await manager.broadcast({
            "type": "download_stopping",
            "data": {"status": "stopping"}
        })

        return {"success": True, "message": "Stop requested"}

    def get_status(self) -> Dict[str, Any]:
        """取得詳細狀態"""
        return {
            "status": self.status.value,
            "is_running": self.status == ServiceStatus.RUNNING,
            "current_task": self.current_task,
            "stats": self.stats,
            "queue_count": self._get_queue_count()
        }


# 全域下載服務實例
download_service = DownloadService()
