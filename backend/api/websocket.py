from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json


class ConnectionManager:
    """WebSocket 連線管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """廣播訊息給所有連線"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # 清理斷開的連線
        for conn in disconnected:
            self.disconnect(conn)

    async def send_status_update(self, download_id: str, url: str, status: str,
                                  progress: str = None, progress_percent: int = None,
                                  filename: str = None, error_message: str = None):
        """發送狀態更新"""
        await self.broadcast({
            "type": "status_update",
            "data": {
                "id": download_id,
                "url": url,
                "status": status,
                "progress": progress,
                "progress_percent": progress_percent,
                "filename": filename,
                "error_message": error_message
            }
        })


# 全域連線管理器
manager = ConnectionManager()
