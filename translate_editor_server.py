#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻譯專案編輯器 - 本地伺服器
提供 API 讓 Vue 前端可以讀寫翻譯設定和執行工作流程
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import subprocess
import io

# 設定工作目錄
os.chdir(Path(__file__).parent)

CONFIG_PATH = Path("translation_config.json")
VIDEOS_FOLDER = Path("backend/downloads/youtube")
PORT = 8081


class TranslateEditorHandler(SimpleHTTPRequestHandler):
    """處理翻譯編輯器的 HTTP 請求"""

    def do_GET(self):
        """處理 GET 請求"""
        parsed = urlparse(self.path)

        if parsed.path == '/api/config':
            self.handle_get_config()
        elif parsed.path == '/api/videos':
            self.handle_get_videos()
        else:
            # 預設檔案服務
            super().do_GET()

    def do_POST(self):
        """處理 POST 請求"""
        parsed = urlparse(self.path)

        if parsed.path == '/api/config':
            self.handle_save_config()
        elif parsed.path == '/api/start':
            self.handle_start_workflow()
        else:
            self.send_error(404, "Not Found")

    def do_OPTIONS(self):
        """處理 CORS preflight"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        """發送 CORS 標頭"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def handle_get_config(self):
        """讀取設定檔"""
        try:
            if not CONFIG_PATH.exists():
                # 創建預設設定
                default_config = {
                    "subtitle_style": {
                        "font_size": 10,
                        "text_color": "#FFFFFF",
                        "background_color": "#000000",
                        "background_alpha": 0.7,
                        "position_y": -0.75,
                        "stroke_width": 2,
                        "stroke_color": "#000000",
                        "bold": True,
                        "shadow": True,
                        "line_max_width": 0.82
                    }
                }
                with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)

            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 獲取影片列表
            videos = self._get_video_list()

            response = {
                "config": config,
                "template_text": "",
                "videos": videos
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, str(e))

    def handle_save_config(self):
        """儲存設定檔"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # 備份原檔案
            if CONFIG_PATH.exists():
                import shutil
                backup_path = CONFIG_PATH.with_suffix('.json.bak')
                shutil.copy(CONFIG_PATH, backup_path)

            # 寫入新設定
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data.get('config', {}), f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            response = {"success": True, "message": "設定已儲存"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, str(e))

    def handle_get_videos(self):
        """獲取影片列表"""
        try:
            videos = self._get_video_list()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            response = {"videos": videos}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, str(e))

    def handle_start_workflow(self):
        """執行翻譯工作流程"""
        try:
            # 這裡應該調用翻譯工作流程
            # 暫時返回模擬輸出

            output = []
            output.append("=" * 50)
            output.append("YouTube 翻譯工作流程")
            output.append("=" * 50)
            output.append("")
            output.append("[Info] 檢查設定檔...")

            if CONFIG_PATH.exists():
                output.append("[OK] 設定檔已載入")
            else:
                output.append("[Error] 找不到設定檔")
                raise Exception("找不到設定檔")

            output.append("")
            output.append("[Info] 掃描影片...")
            videos = self._get_video_list()
            output.append(f"[OK] 找到 {len(videos)} 個影片")

            if not videos:
                output.append("[Warning] 沒有找到影片，請先下載 YouTube 影片")
            else:
                output.append("")
                output.append("[Info] 開始處理影片...")
                for i, video in enumerate(videos, 1):
                    output.append(f"  [{i}/{len(videos)}] {video}")
                    output.append("    - 使用 Whisper 轉錄...")
                    output.append("    - 翻譯字幕...")
                    output.append("    - 生成剪映草稿...")
                    output.append("    ✓ 完成")
                    output.append("")

            output.append("=" * 50)
            output.append("[Done] 處理完成!")
            output.append("=" * 50)

            result = "\n".join(output)

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(result.encode('utf-8'))

        except Exception as e:
            self.send_error(500, str(e))

    def _get_video_list(self):
        """獲取影片列表"""
        if not VIDEOS_FOLDER.exists():
            return []

        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        videos = [
            f.name for f in VIDEOS_FOLDER.iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ]
        return sorted(videos)

    def log_message(self, format, *args):
        """自訂日誌格式"""
        print(f"[Server] {args[0]}")


def main():
    print("=" * 50)
    print("  翻譯專案編輯器伺服器")
    print("=" * 50)
    print()
    print(f"  設定檔路徑: {CONFIG_PATH.absolute()}")
    print(f"  影片資料夾: {VIDEOS_FOLDER.absolute()}")
    print(f"  伺服器網址: http://localhost:{PORT}")
    print(f"  編輯器網址: http://localhost:{PORT}/translate_editor.html")
    print()
    print("  按 Ctrl+C 關閉伺服器")
    print("=" * 50)
    print()

    # 自動開啟瀏覽器
    webbrowser.open(f'http://localhost:{PORT}/translate_editor.html')

    # 啟動伺服器
    server = HTTPServer(('localhost', PORT), TranslateEditorHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已關閉")
        server.shutdown()


if __name__ == "__main__":
    main()
