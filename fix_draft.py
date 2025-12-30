#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修復剪映草稿 - 修正顏色格式問題"""

import json
import uuid
import re
from pathlib import Path

def fix_color_format(content_str):
    """修復顏色格式: ["#", "F", "F", ...] -> [1.0, 1.0, 1.0]"""
    # 找到錯誤的顏色格式
    pattern = r'"color":\s*\["#",\s*"([0-9A-Fa-f])",\s*"([0-9A-Fa-f])",\s*"([0-9A-Fa-f])",\s*"([0-9A-Fa-f])",\s*"([0-9A-Fa-f])",\s*"([0-9A-Fa-f])"\]'

    def replace_color(match):
        hex_str = ''.join(match.groups())
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return f'"color": [{r}, {g}, {b}]'

    return re.sub(pattern, replace_color, content_str)

def fix_draft():
    draft_folder = Path.home() / 'AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft/翻譯_I BLEW UP a YouTube Channel in 7 Days with AI'

    # 1. 修復 draft_content.json 中的顏色格式
    content_path = draft_folder / 'draft_content.json'
    print(f'讀取草稿內容...')

    with open(content_path, 'r', encoding='utf-8') as f:
        content_str = f.read()

    # 計算修復數量
    bad_colors = len(re.findall(r'"color":\s*\["#"', content_str))
    print(f'發現 {bad_colors} 個錯誤的顏色格式')

    if bad_colors > 0:
        fixed_content = fix_color_format(content_str)

        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f'顏色格式已修復')

    # 2. 修復 type: subtitle -> text
    with open(content_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fixed_types = 0
    for text in data.get('materials', {}).get('texts', []):
        if text.get('type') == 'subtitle':
            text['type'] = 'text'
            fixed_types += 1

    if fixed_types > 0:
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print(f'修復了 {fixed_types} 個 type 欄位 (subtitle -> text)')

    # 3. 修復 meta info
    meta_path = draft_folder / 'draft_meta_info.json'
    template_meta = Path('C:/face-vid-template/長片翻譯專案/draft_meta_info.json')

    with open(template_meta, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    meta['draft_name'] = '翻譯_I BLEW UP a YouTube Channel in 7 Days with AI'
    meta['draft_fold_path'] = str(draft_folder).replace(chr(92), '/')
    meta['draft_id'] = str(uuid.uuid4()).upper()
    meta['tm_duration'] = 1865734000
    meta['draft_new_version'] = '110.0.1'

    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)

    print(f'Meta info 已修復')
    print()
    print('=== 修復完成！請重新打開剪映 ===')

if __name__ == '__main__':
    fix_draft()
