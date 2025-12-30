#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蝦皮專案 - 批量處理影片
只更換影片和標題文字，@fu_island_ 固定不動
"""

import os
import json
import shutil
import copy
from pathlib import Path
from datetime import datetime

class ShopeeVideoProcessor:
    """蝦皮影片處理器"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.template_name = "蝦皮專案"
        self.output_prefix = "蝦皮專案_"
        self.video_folder = self.project_root / "videos" / "shopee_raw"

        # 剪映草稿路徑
        username = os.environ.get("USERNAME") or os.getlogin()
        self.jianying_draft_root = Path(rf"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft")

        # 確保資料夾存在
        self.video_folder.mkdir(parents=True, exist_ok=True)

    def process_video(self, video_path: str, force: bool = False):
        """處理單個影片"""
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"[Error] 找不到影片: {video_path}")
            return None

        video_name = video_path.stem
        output_name = f"{self.output_prefix}{video_name}"

        # 檢查是否已存在
        output_folder = self.jianying_draft_root / output_name
        if output_folder.exists() and not force:
            print(f"[Skip] 已存在: {output_name}")
            return output_name

        print(f"\n[Video] 處理: {video_name}")

        # 載入模板
        template_folder = self.jianying_draft_root / self.template_name
        template_file = template_folder / "draft_content.json"

        if not template_file.exists():
            print(f"[Error] 找不到模板: {template_folder}")
            return None

        with open(template_file, 'r', encoding='utf-8') as f:
            draft_data = json.load(f)

        # 替換影片
        draft_data = self._replace_video(draft_data, str(video_path))

        # 更新標題（第一個文字）
        draft_data = self._update_title(draft_data, video_name)

        # 儲存草稿
        if output_folder.exists():
            shutil.rmtree(output_folder, ignore_errors=True)
        output_folder.mkdir(parents=True, exist_ok=True)

        with open(output_folder / "draft_content.json", 'w', encoding='utf-8') as f:
            json.dump(draft_data, f, ensure_ascii=False)

        # 複製其他模板檔案
        for file in ["draft_meta_info.json", "draft_settings"]:
            src = template_folder / file
            if src.exists():
                shutil.copy(src, output_folder / file)

        print(f"[OK] 完成: {output_name}")
        return output_name

    def _replace_video(self, draft_data: dict, video_path: str) -> dict:
        """替換草稿中的影片"""
        import uuid

        video_path = Path(video_path)

        # 取得影片資訊
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(str(video_path))
            duration_us = int(clip.duration * 1_000_000)
            width, height = clip.size
            clip.close()
        except:
            # 預設值
            duration_us = 60_000_000
            width, height = 1080, 1920

        # 更新草稿時長
        draft_data["duration"] = duration_us

        # 更新影片素材
        for material in draft_data.get("materials", {}).get("videos", []):
            material["path"] = str(video_path)
            material["duration"] = duration_us
            material["width"] = width
            material["height"] = height

        # 更新影片軌道片段
        for track in draft_data.get("tracks", []):
            if track.get("type") == "video":
                for segment in track.get("segments", []):
                    segment["target_timerange"] = {
                        "duration": duration_us,
                        "start": 0
                    }
                    if "source_timerange" in segment:
                        segment["source_timerange"]["duration"] = duration_us

        # 更新文字軌道片段時長
        for track in draft_data.get("tracks", []):
            if track.get("type") == "text":
                for segment in track.get("segments", []):
                    segment["target_timerange"] = {
                        "duration": duration_us,
                        "start": 0
                    }

        return draft_data

    def _update_title(self, draft_data: dict, video_name: str) -> dict:
        """更新標題文字（第一個文字素材）"""
        texts = draft_data.get("materials", {}).get("texts", [])

        if len(texts) > 0:
            # 更新第一個文字（標題）
            title_text = texts[0]
            content_str = title_text.get("content", "{}")

            try:
                content = json.loads(content_str)
                content["text"] = video_name

                # 更新 styles 的 range
                if "styles" in content:
                    for style in content["styles"]:
                        style["range"] = [0, len(video_name)]

                title_text["content"] = json.dumps(content, ensure_ascii=False)
                print(f"   標題: {video_name}")
            except Exception as e:
                print(f"   [Warning] 更新標題失敗: {e}")

        return draft_data

    def batch_process(self, force: bool = False):
        """批量處理所有影片"""
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

        video_files = [
            f for f in self.video_folder.iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ]

        if not video_files:
            print(f"[Info] 沒有找到影片，請將影片放入: {self.video_folder}")
            return

        print(f"[Info] 找到 {len(video_files)} 個影片")
        print("=" * 50)

        success = 0
        for video_file in video_files:
            result = self.process_video(str(video_file), force)
            if result:
                success += 1

        print("\n" + "=" * 50)
        print(f"[Done] 完成 {success}/{len(video_files)} 個")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="蝦皮專案影片處理")
    parser.add_argument("--force", action="store_true", help="強制重新處理")
    parser.add_argument("video", nargs="?", help="單個影片路徑（可選）")

    args = parser.parse_args()

    processor = ShopeeVideoProcessor()

    if args.video:
        processor.process_video(args.video, args.force)
    else:
        processor.batch_process(args.force)


if __name__ == "__main__":
    main()
