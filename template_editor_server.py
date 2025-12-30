#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板文字編輯器 - 本地伺服器
提供 API 讓 Vue 前端可以讀寫模板文件
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# 設定工作目錄
os.chdir(Path(__file__).parent)

TEMPLATE_PATH = Path("面相專案/draft_content.json")
PORT = 8080


class EditorHandler(SimpleHTTPRequestHandler):
    """處理編輯器的 HTTP 請求"""

    def do_GET(self):
        """處理 GET 請求"""
        parsed = urlparse(self.path)

        if parsed.path == '/api/template':
            self.handle_get_template()
        else:
            # 預設檔案服務
            super().do_GET()

    def do_POST(self):
        """處理 POST 請求"""
        parsed = urlparse(self.path)

        if parsed.path == '/api/template':
            self.handle_save_template()
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

    def handle_get_template(self):
        """讀取模板"""
        try:
            if not TEMPLATE_PATH.exists():
                self.send_error(404, "Template not found")
                return

            with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, str(e))

    def handle_save_template(self):
        """儲存模板"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # 備份原檔案
            backup_path = TEMPLATE_PATH.with_suffix('.json.bak')
            if TEMPLATE_PATH.exists():
                import shutil
                shutil.copy(TEMPLATE_PATH, backup_path)

            # 寫入新內容
            with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.end_headers()
            response = {"success": True, "message": "模板已儲存"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        """自訂日誌格式"""
        print(f"[Server] {args[0]}")


def main():
    print("=" * 50)
    print("  模板文字編輯器伺服器")
    print("=" * 50)
    print()
    print(f"  模板路徑: {TEMPLATE_PATH.absolute()}")
    print(f"  伺服器網址: http://localhost:{PORT}")
    print(f"  編輯器網址: http://localhost:{PORT}/template_editor.html")
    print()
    print("  按 Ctrl+C 關閉伺服器")
    print("=" * 50)
    print()

    # 自動開啟瀏覽器
    webbrowser.open(f'http://localhost:{PORT}/template_editor.html')

    # 啟動伺服器
    server = HTTPServer(('localhost', PORT), EditorHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已關閉")
        server.shutdown()


if __name__ == "__main__":
    main()
