#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從草稿複製字幕樣式到翻譯配置"""

import json
from pathlib import Path
import getpass

USERNAME = getpass.getuser()
DRAFTS_PATH = Path(f"C:/Users/{USERNAME}/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft")
CONFIG_PATH = Path("translation_config.json")

def rgb_to_hex(rgb):
    """RGB (0-1) 轉 HEX"""
    if not rgb or len(rgb) < 3:
        return "#FFFFFF"
    r = int(rgb[0] * 255)
    g = int(rgb[1] * 255)
    b = int(rgb[2] * 255)
    return f"#{r:02X}{g:02X}{b:02X}"

def find_draft(keyword):
    """搜尋包含關鍵字的草稿"""
    for d in DRAFTS_PATH.iterdir():
        if d.is_dir() and keyword.lower() in d.name.lower():
            return d
    return None

def read_draft(draft_path):
    """讀取草稿 JSON"""
    content = draft_path / "draft_content.json"
    bak = draft_path / "draft_content.json.bak"

    # 優先讀取未加密的檔案
    for src in [content, bak]:
        if src.exists():
            with open(src, 'rb') as f:
                if f.read(1) == b'{':
                    f.seek(0)
                    return json.load(f)
    return None

def extract_style(draft_data):
    """從草稿提取字幕樣式"""
    texts = draft_data.get('materials', {}).get('texts', [])
    if not texts:
        return None

    t = texts[0]

    text_color = t.get('text_color', [1, 1, 1])
    if isinstance(text_color, list):
        text_color = rgb_to_hex(text_color)

    bg_color = t.get('background_color', [0, 0, 0])
    if isinstance(bg_color, list):
        bg_color = rgb_to_hex(bg_color)

    return {
        "font_size": t.get('font_size', 7),
        "text_color": text_color,
        "background_color": bg_color,
        "background_alpha": t.get('background_alpha', 0),
        "bold": t.get('bold', False),
        "italic": t.get('italic', False),
        "position_y": -0.75,  # 預設值
        "stroke_width": 2,
        "stroke_color": "#000000",
        "shadow": True,
        "line_max_width": 0.85
    }

def main():
    keyword = "Impractical"
    print(f"搜尋草稿: {keyword}")

    draft = find_draft(keyword)
    if not draft:
        print("找不到草稿！")
        return

    print(f"找到: {draft.name}")

    data = read_draft(draft)
    if not data:
        print("無法讀取草稿（可能加密）")
        return

    texts = data.get('materials', {}).get('texts', [])
    print(f"字幕數: {len(texts)}")

    style = extract_style(data)
    if not style:
        print("草稿沒有字幕")
        return

    print(f"\n提取的樣式:")
    for k, v in style.items():
        print(f"  {k}: {v}")

    # 更新配置
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    config['subtitle_style'] = style

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n已更新 {CONFIG_PATH}")

if __name__ == "__main__":
    main()
