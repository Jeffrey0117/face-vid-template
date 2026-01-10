"""
簡繁轉換模組 - 轉換剪映草稿中的字幕文字

支援模式：
- s2t: 簡體 → 繁體
- s2tw: 簡體 → 台灣繁體（含詞彙轉換）
- s2hk: 簡體 → 香港繁體
- t2s: 繁體 → 簡體
"""

import os
import json
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any

try:
    import opencc
except ImportError:
    opencc = None

ConvertMode = Literal["s2t", "s2tw", "s2twp", "s2hk", "t2s", "tw2s", "hk2s"]


def _ensure_opencc():
    """確保 opencc 已安裝"""
    if opencc is None:
        raise ImportError(
            "需要安裝 opencc-python-reimplemented:\n"
            "  pip install opencc-python-reimplemented"
        )


def get_jianying_drafts_path() -> Path:
    """
    取得剪映草稿目錄路徑

    Returns:
        剪映草稿目錄的 Path 物件

    Raises:
        FileNotFoundError: 找不到剪映草稿目錄
    """
    # Windows 預設路徑
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', ''))
        candidates = [
            base / 'AppData' / 'Local' / 'JianyingPro' / 'User Data' / 'Projects' / 'com.lveditor.draft',
            base / 'AppData' / 'Local' / 'CapCut' / 'User Data' / 'Projects' / 'com.lveditor.draft',
        ]
    # macOS 預設路徑
    else:
        base = Path.home()
        candidates = [
            base / 'Movies' / 'JianyingPro' / 'User Data' / 'Projects' / 'com.lveditor.draft',
            base / 'Movies' / 'CapCut' / 'User Data' / 'Projects' / 'com.lveditor.draft',
        ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        f"找不到剪映草稿目錄，嘗試過以下路徑：\n" +
        "\n".join(f"  - {p}" for p in candidates)
    )


def list_drafts(drafts_path: Optional[Path] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    列出所有草稿

    Args:
        drafts_path: 草稿目錄路徑（預設自動偵測）
        limit: 最多顯示幾個草稿

    Returns:
        草稿列表，每個草稿包含 name, path, mtime
    """
    if drafts_path is None:
        drafts_path = get_jianying_drafts_path()

    drafts = []
    for folder in drafts_path.iterdir():
        if not folder.is_dir():
            continue

        draft_content = folder / 'draft_content.json'
        draft_meta = folder / 'draft_meta_info.json'

        if not draft_content.exists():
            continue

        # 讀取草稿名稱
        name = folder.name
        if draft_meta.exists():
            try:
                with open(draft_meta, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    name = meta.get('draft_name', folder.name)
            except:
                pass

        drafts.append({
            'name': name,
            'folder': folder.name,
            'path': draft_content,
            'mtime': draft_content.stat().st_mtime
        })

    # 按修改時間排序（最新的在前）
    drafts.sort(key=lambda x: x['mtime'], reverse=True)
    return drafts[:limit]


def find_draft_by_name(name: str, drafts_path: Optional[Path] = None) -> Path:
    """
    根據名稱搜尋草稿

    Args:
        name: 草稿名稱（部分匹配）
        drafts_path: 草稿目錄路徑

    Returns:
        draft_content.json 的路徑

    Raises:
        FileNotFoundError: 找不到匹配的草稿
    """
    drafts = list_drafts(drafts_path, limit=100)

    # 精確匹配
    for draft in drafts:
        if draft['name'] == name or draft['folder'] == name:
            return draft['path']

    # 部分匹配
    matches = [d for d in drafts if name.lower() in d['name'].lower()]
    if len(matches) == 1:
        return matches[0]['path']
    elif len(matches) > 1:
        raise ValueError(
            f"找到多個匹配的草稿：\n" +
            "\n".join(f"  - {d['name']}" for d in matches[:5])
        )

    raise FileNotFoundError(f"找不到名為 '{name}' 的草稿")


def convert_text(text: str, mode: ConvertMode = "s2tw") -> str:
    """
    轉換單一文字字串

    Args:
        text: 要轉換的文字
        mode: 轉換模式
            - s2t: 簡體 → 繁體
            - s2tw: 簡體 → 台灣繁體
            - s2twp: 簡體 → 台灣繁體（含慣用詞）
            - s2hk: 簡體 → 香港繁體
            - t2s: 繁體 → 簡體
            - tw2s: 台灣繁體 → 簡體
            - hk2s: 香港繁體 → 簡體

    Returns:
        轉換後的文字
    """
    _ensure_opencc()
    converter = opencc.OpenCC(mode)
    return converter.convert(text)


def convert_srt_file(
    input_path: str,
    output_path: Optional[str] = None,
    mode: ConvertMode = "s2tw"
) -> str:
    """
    轉換 SRT 字幕檔案

    Args:
        input_path: 輸入 SRT 檔案路徑
        output_path: 輸出檔案路徑（預設覆蓋原檔）
        mode: 轉換模式

    Returns:
        輸出檔案路徑
    """
    _ensure_opencc()
    converter = opencc.OpenCC(mode)

    if output_path is None:
        output_path = input_path

    with open(input_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    converted = converter.convert(content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(converted)

    return output_path


def convert_draft(
    script: "ScriptFile",
    mode: ConvertMode = "s2tw",
    verbose: bool = False
) -> int:
    """
    轉換剪映草稿中的所有文字

    Args:
        script: ScriptFile 實例（需已載入模板）
        mode: 轉換模式
        verbose: 是否顯示轉換詳情

    Returns:
        轉換的文字數量
    """
    _ensure_opencc()
    converter = opencc.OpenCC(mode)
    count = 0

    # 轉換 texts 素材
    texts = script.imported_materials.get("texts", [])
    for text_mat in texts:
        content_str = text_mat.get("content", "")
        if not content_str:
            continue

        try:
            # JSON 格式的 content
            content = json.loads(content_str)
            original = content.get("text", "")
            if original:
                converted = converter.convert(original)
                if converted != original:
                    content["text"] = converted
                    text_mat["content"] = json.dumps(content, ensure_ascii=False)
                    count += 1
                    if verbose:
                        print(f"  [{count}] {original[:30]}... → {converted[:30]}...")
        except (json.JSONDecodeError, TypeError):
            # 純文字格式
            original = content_str
            converted = converter.convert(original)
            if converted != original:
                text_mat["content"] = converted
                count += 1
                if verbose:
                    print(f"  [{count}] {original[:30]}... → {converted[:30]}...")

    # 轉換 text_templates 中的文字
    templates = script.imported_materials.get("text_templates", [])
    for template in templates:
        resources = template.get("text_info_resources", [])
        for resource in resources:
            text_material_id = resource.get("text_material_id")
            if not text_material_id:
                continue

            # 找到對應的 text 素材並轉換
            for text_mat in texts:
                if text_mat.get("id") != text_material_id:
                    continue

                content_str = text_mat.get("content", "")
                try:
                    content = json.loads(content_str)
                    original = content.get("text", "")
                    if original:
                        converted = converter.convert(original)
                        if converted != original:
                            content["text"] = converted
                            text_mat["content"] = json.dumps(content, ensure_ascii=False)
                            # 不重複計數，因為上面已經處理過
                except (json.JSONDecodeError, TypeError):
                    pass

    return count


def convert_draft_file(
    draft_path: str,
    mode: ConvertMode = "s2tw",
    verbose: bool = False
) -> int:
    """
    直接轉換草稿檔案（便捷函數）

    Args:
        draft_path: draft_content.json 的路徑
        mode: 轉換模式
        verbose: 是否顯示轉換詳情

    Returns:
        轉換的文字數量

    Raises:
        ValueError: 草稿檔案已加密（新版剪映格式）
    """
    from .script_file import ScriptFile
    from pathlib import Path

    # 先檢查是否為加密格式
    draft_file = Path(draft_path)
    if draft_file.exists():
        with open(draft_file, 'r', encoding='utf-8') as f:
            first_char = f.read(1)
            if first_char != '{':
                raise ValueError(
                    "此草稿已加密（新版剪映格式），無法直接轉換。\n"
                    "請選擇較舊的草稿，或在剪映中重新導出為未加密格式。"
                )

    script = ScriptFile.load_template(draft_path)
    count = convert_draft(script, mode, verbose)
    script.save()

    return count


# CLI 支援
def main():
    """命令列介面"""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description="簡繁轉換工具 - 轉換 SRT 字幕或剪映草稿",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 列出所有草稿
  python -m JYpymaker.converter --list

  # 轉換指定草稿（用名稱搜尋）
  python -m JYpymaker.converter --draft "翻譯_video" -m s2twp

  # 轉換 SRT 檔案
  python -m JYpymaker.converter subtitle.srt -m s2twp

  # 轉換草稿 JSON 檔案
  python -m JYpymaker.converter draft_content.json -m s2tw -v
"""
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="輸入檔案路徑（.srt 或 draft_content.json）"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="列出所有剪映草稿"
    )
    parser.add_argument(
        "-d", "--draft",
        help="根據名稱搜尋並轉換草稿"
    )
    parser.add_argument(
        "-o", "--output",
        help="輸出檔案路徑（預設覆蓋原檔）"
    )
    parser.add_argument(
        "-m", "--mode",
        default="s2tw",
        choices=["s2t", "s2tw", "s2twp", "s2hk", "t2s", "tw2s", "hk2s"],
        help="轉換模式（預設：s2tw）"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="顯示轉換詳情"
    )

    args = parser.parse_args()

    # 列出草稿
    if args.list:
        try:
            drafts = list_drafts()
            print(f"找到 {len(drafts)} 個草稿：\n")
            for i, d in enumerate(drafts, 1):
                mtime = datetime.fromtimestamp(d['mtime']).strftime('%Y-%m-%d %H:%M')
                print(f"  {i:2}. [{mtime}] {d['name']}")
            return 0
        except FileNotFoundError as e:
            print(f"錯誤：{e}")
            return 1

    # 根據名稱搜尋草稿
    if args.draft:
        try:
            draft_path = find_draft_by_name(args.draft)
            print(f"找到草稿：{draft_path.parent.name}")
            count = convert_draft_file(str(draft_path), args.mode, args.verbose)
            print(f"已轉換 {count} 個文字片段")
            return 0
        except (FileNotFoundError, ValueError) as e:
            print(f"錯誤：{e}")
            return 1

    # 處理輸入檔案
    if not args.input:
        parser.print_help()
        return 1

    if args.input.endswith(".srt"):
        output = convert_srt_file(args.input, args.output, args.mode)
        print(f"已轉換: {output}")
    elif args.input.endswith(".json"):
        count = convert_draft_file(args.input, args.mode, args.verbose)
        print(f"已轉換 {count} 個文字片段")
    else:
        print("不支援的檔案格式，請使用 .srt 或 .json")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
