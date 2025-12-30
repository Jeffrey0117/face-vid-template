#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
長片草稿字幕樣式編輯器 - 本地伺服器
可以修改已存在剪映草稿中的字幕樣式
"""

import os
import sys
import json
import webbrowser
import getpass
import shutil
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime

# 設定工作目錄
os.chdir(Path(__file__).parent)

USERNAME = getpass.getuser()
DRAFT_FOLDER = Path(f"C:/Users/{USERNAME}/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft")
PORT = 8082


def hex_to_rgb(hex_color: str) -> list:
    """轉換 HEX 顏色為 RGB (0-1)"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return [r, g, b]


def rgb_to_hex(rgb: list) -> str:
    """轉換 RGB (0-1) 為 HEX 顏色"""
    if not rgb or len(rgb) < 3:
        return '#FFFFFF'
    r = int(rgb[0] * 255)
    g = int(rgb[1] * 255)
    b = int(rgb[2] * 255)
    return f"#{r:02X}{g:02X}{b:02X}"


def is_file_encrypted(file_path: Path) -> bool:
    """檢查檔案是否加密（非 JSON 格式）"""
    if not file_path.exists():
        return False
    try:
        with open(file_path, 'rb') as f:
            first_byte = f.read(1)
        return first_byte != b'{'
    except:
        return True


def read_draft_json(file_path: Path) -> dict:
    """讀取草稿 JSON 檔案"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_readable_source(draft_path: Path) -> tuple:
    """
    獲取可讀取的草稿來源
    返回: (source_path, is_main_encrypted)
    """
    content_path = draft_path / "draft_content.json"
    bak_path = draft_path / "draft_content.json.bak"

    main_encrypted = is_file_encrypted(content_path)

    # 優先順序：
    # 1. 如果 draft_content.json 未加密，直接用它
    # 2. 如果加密，嘗試用 .bak
    # 3. 都不行就返回 None

    if content_path.exists() and not main_encrypted:
        return content_path, False
    elif bak_path.exists() and not is_file_encrypted(bak_path):
        return bak_path, main_encrypted
    elif content_path.exists():
        return None, True  # 加密且無備份
    else:
        return None, False  # 檔案不存在


class DraftStyleEditorHandler(SimpleHTTPRequestHandler):
    """處理草稿編輯器的 HTTP 請求"""

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/drafts':
            self.handle_get_drafts()
        elif parsed.path == '/api/draft':
            query = parse_qs(parsed.query)
            draft_name = query.get('name', [''])[0]
            self.handle_get_draft(draft_name)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/draft/style':
            self.handle_update_style()
        else:
            self.send_error(404, "Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def send_json(self, data: dict, status: int = 200):
        """發送 JSON 回應"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def handle_get_drafts(self):
        """獲取所有草稿列表"""
        try:
            drafts = []
            if DRAFT_FOLDER.exists():
                for item in sorted(DRAFT_FOLDER.iterdir()):
                    if not item.is_dir():
                        continue

                    content_path = item / "draft_content.json"
                    bak_path = item / "draft_content.json.bak"

                    if not content_path.exists() and not bak_path.exists():
                        continue

                    subtitle_count = 0
                    source_path, main_encrypted = get_readable_source(item)

                    if source_path:
                        try:
                            data = read_draft_json(source_path)
                            subtitle_count = len(data.get('materials', {}).get('texts', []))
                        except Exception as e:
                            print(f"[Error] 讀取 {item.name} 失敗: {e}")

                    drafts.append({
                        "name": item.name,
                        "subtitle_count": subtitle_count,
                        "is_encrypted": main_encrypted and source_path is None,
                        "has_backup": bak_path.exists(),
                        "source": source_path.name if source_path else None
                    })

            self.send_json({"drafts": drafts})

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))

    def handle_get_draft(self, draft_name: str):
        """獲取草稿詳細資訊"""
        try:
            draft_path = DRAFT_FOLDER / draft_name
            source_path, main_encrypted = get_readable_source(draft_path)

            if not source_path:
                self.send_json({"error": "草稿加密且無可用備份"}, 400)
                return

            print(f"[Read] 讀取 {draft_name} from {source_path.name}")
            data = read_draft_json(source_path)
            texts = data.get('materials', {}).get('texts', [])

            # 分析字幕
            subtitles = []
            style_sample = None

            for i, text in enumerate(texts):
                content_str = text.get('content', '')
                try:
                    content_data = json.loads(content_str) if content_str else {}
                    text_content = content_data.get('text', '')
                except:
                    text_content = ''

                font_size = text.get('font_size', 7.0)
                text_color = text.get('text_color', '#FFFFFF')
                if isinstance(text_color, list):
                    text_color = rgb_to_hex(text_color)

                subtitles.append({
                    "index": i,
                    "text": text_content[:50] + ('...' if len(text_content) > 50 else ''),
                    "font_size": font_size,
                    "text_color": text_color
                })

                if style_sample is None and text_content:
                    bg_color = text.get('background_color', '')
                    if isinstance(bg_color, list):
                        bg_color = rgb_to_hex(bg_color)

                    style_sample = {
                        "font_size": font_size,
                        "text_color": text_color,
                        "background_color": bg_color or '#000000',
                        "background_alpha": text.get('background_alpha', 0),
                        "bold": text.get('bold', False),
                        "italic": text.get('italic', False)
                    }

            self.send_json({
                "name": draft_name,
                "subtitle_count": len(texts),
                "subtitles": subtitles[:20],
                "style": style_sample or {
                    "font_size": 7.0,
                    "text_color": "#FFFFFF",
                    "background_color": "#000000",
                    "background_alpha": 0,
                    "bold": False,
                    "italic": False
                },
                "source": source_path.name,
                "main_encrypted": main_encrypted
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))

    def handle_update_style(self):
        """更新草稿字幕樣式"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            draft_name = data.get('draft_name')
            new_style = data.get('style', {})

            if not draft_name:
                self.send_json({"error": "缺少 draft_name"}, 400)
                return

            draft_path = DRAFT_FOLDER / draft_name
            content_path = draft_path / "draft_content.json"
            bak_path = draft_path / "draft_content.json.bak"

            # 找到可讀取的來源
            source_path, _ = get_readable_source(draft_path)
            if not source_path:
                self.send_json({"error": "無法讀取草稿"}, 400)
                return

            print(f"[Read] 從 {source_path.name} 讀取")
            draft_data = read_draft_json(source_path)

            # 備份到 .backup 資料夾
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = draft_path / ".backup"
            backup_folder.mkdir(exist_ok=True)
            backup_file = backup_folder / f"draft_content_{timestamp}.json"
            shutil.copy(source_path, backup_file)
            print(f"[Backup] {backup_file}")

            # 更新所有字幕樣式
            texts = draft_data.get('materials', {}).get('texts', [])
            updated_count = 0

            for text in texts:
                if 'font_size' in new_style:
                    text['font_size'] = new_style['font_size']

                if 'text_color' in new_style:
                    color = new_style['text_color']
                    text['text_color'] = hex_to_rgb(color) if color.startswith('#') else color

                if 'background_color' in new_style:
                    color = new_style['background_color']
                    text['background_color'] = hex_to_rgb(color) if color.startswith('#') else color

                if 'background_alpha' in new_style:
                    text['background_alpha'] = new_style['background_alpha']

                if 'bold' in new_style:
                    text['bold'] = new_style['bold']
                if 'italic' in new_style:
                    text['italic'] = new_style['italic']

                updated_count += 1

            # 寫入 draft_content.json（剪映讀取的主檔案）
            with open(content_path, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, ensure_ascii=False)
            print(f"[Save] {content_path.name}")

            # 同時更新 .bak
            with open(bak_path, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, ensure_ascii=False)
            print(f"[Save] {bak_path.name}")

            print(f"[Done] 更新了 {updated_count} 個字幕")

            self.send_json({
                "success": True,
                "message": f"已更新 {updated_count} 個字幕樣式",
                "backup": str(backup_file)
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]}")


def main():
    print("=" * 50)
    print("  長片草稿字幕樣式編輯器")
    print("=" * 50)
    print()
    print(f"  剪映草稿路徑: {DRAFT_FOLDER}")
    print(f"  伺服器網址: http://localhost:{PORT}")
    print()
    print("  按 Ctrl+C 關閉伺服器")
    print("=" * 50)
    print()

    webbrowser.open(f'http://localhost:{PORT}/draft_style_editor.html')

    server = HTTPServer(('localhost', PORT), DraftStyleEditorHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已關閉")
        server.shutdown()


if __name__ == "__main__":
    main()
