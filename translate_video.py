#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 影片翻譯工作流程
使用 Whisper 語音識別 + DeepSeek API 翻譯 + 剪映字幕生成
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# 設置路徑
sys.path.insert(0, str(Path(__file__).parent))

import whisper
from openai import OpenAI

# 載入設定
CONFIG_FILE = Path(__file__).parent / "translation_config.json"

def load_config():
    """載入翻譯設定"""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

class TranslationWorkflow:
    def __init__(self):
        self.config = load_config()
        self.whisper_model = None
        self.deepseek_client = None

        # 路徑設定
        self.project_root = Path(__file__).parent
        self.source_folder = self.project_root / self.config["paths"]["source_video_folder"]
        self.output_folder = self.project_root / self.config["paths"]["output_folder"]
        self.template_folder = self.project_root / self.config["paths"]["draft_template"]

        # 確保輸出資料夾存在
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def init_whisper(self):
        """初始化 Whisper 模型"""
        if self.whisper_model is None:
            model_name = self.config["whisper"]["model"]
            print(f"[Whisper] 載入模型: {model_name}")
            self.whisper_model = whisper.load_model(model_name)
        return self.whisper_model

    def init_deepseek(self):
        """初始化 DeepSeek API 客戶端"""
        if self.deepseek_client is None:
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("請設定環境變數 DEEPSEEK_API_KEY")

            self.deepseek_client = OpenAI(
                api_key=api_key,
                base_url=self.config["translation"]["base_url"]
            )
        return self.deepseek_client

    def transcribe(self, video_path: Path) -> list:
        """使用 Whisper 轉錄影片"""
        print(f"[1/4] 語音識別: {video_path.name}")

        model = self.init_whisper()
        result = model.transcribe(
            str(video_path),
            language=self.config["whisper"]["language"],
            task=self.config["whisper"]["task"],
            temperature=self.config["whisper"]["temperature"],
            word_timestamps=self.config["whisper"]["word_timestamps"]
        )

        segments = []
        for seg in result["segments"]:
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })

        print(f"    識別完成: {len(segments)} 個片段")
        return segments

    def translate_text(self, text: str) -> str:
        """使用 DeepSeek 翻譯文字"""
        client = self.init_deepseek()

        prompt = self.config["translation"]["prompt_template"].format(text=text)

        response = client.chat.completions.create(
            model=self.config["translation"]["model"],
            messages=[
                {"role": "system", "content": "你是專業的字幕翻譯員，翻譯要簡潔、口語化、符合繁體中文習慣。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    def translate_segments(self, segments: list) -> list:
        """翻譯所有片段"""
        print(f"[2/4] 翻譯字幕: {len(segments)} 個片段")

        translated = []
        for i, seg in enumerate(segments):
            try:
                translated_text = self.translate_text(seg["text"])
                translated.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "original": seg["text"],
                    "text": translated_text
                })

                if (i + 1) % 10 == 0:
                    print(f"    進度: {i + 1}/{len(segments)}")

            except Exception as e:
                print(f"    翻譯錯誤 [{i}]: {e}")
                translated.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "original": seg["text"],
                    "text": seg["text"]  # 失敗時保留原文
                })

        print(f"    翻譯完成")
        return translated

    def generate_srt(self, segments: list, output_path: Path) -> Path:
        """生成 SRT 字幕檔"""
        print(f"[3/4] 生成 SRT: {output_path.name}")

        def format_timestamp(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments, 1):
                start_ts = format_timestamp(seg["start"])
                end_ts = format_timestamp(seg["end"])
                f.write(f"{i}\n")
                f.write(f"{start_ts} --> {end_ts}\n")
                f.write(f"{seg['text']}\n\n")

        print(f"    SRT 已儲存")
        return output_path

    def create_jianying_draft(self, video_path: Path, srt_path: Path) -> Path:
        """創建剪映草稿並添加字幕"""
        print(f"[4/4] 生成剪映草稿")

        from pyJianYingDraft import DraftFolder, ScriptFile, Intro_type
        from pyJianYingDraft import trange, tim
        from pyJianYingDraft import VideoMaterial, TrackType, ClipSettings, TextStyle

        # 複製模板
        draft_name = f"翻譯_{video_path.stem}"
        jianying_drafts = Path(self.config.get("jianying_draft_folder",
            Path.home() / "AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft"))

        output_draft = jianying_drafts / draft_name

        if output_draft.exists():
            shutil.rmtree(output_draft)
        shutil.copytree(self.template_folder, output_draft)

        # 載入草稿
        draft_json = output_draft / "draft_content.json"
        script = ScriptFile.load_template(str(draft_json))

        # 替換影片素材
        video_material = VideoMaterial(str(video_path))
        video_track = script.get_imported_track(TrackType.video, index=0)
        script.replace_material_by_seg(video_track, 0, video_material)

        # 導入 SRT 字幕
        style = self.config["subtitle_style"]
        text_style = TextStyle(
            size=style["font_size"],
            color=style["text_color"],
            align=1,
            auto_wrapping=True
        )
        clip_settings = ClipSettings(transform_y=style["position_y"])

        script.import_srt(
            str(srt_path),
            "字幕軌",
            text_style=text_style,
            clip_settings=clip_settings
        )

        # 儲存草稿
        script.save()

        print(f"    草稿已儲存: {draft_name}")
        return output_draft

    def process_video(self, video_path: Path) -> dict:
        """處理單個影片"""
        print(f"\n{'='*50}")
        print(f"處理影片: {video_path.name}")
        print(f"{'='*50}")

        try:
            # 1. 語音識別
            segments = self.transcribe(video_path)

            # 2. 翻譯
            translated = self.translate_segments(segments)

            # 3. 生成 SRT
            srt_path = self.output_folder / f"{video_path.stem}.srt"
            self.generate_srt(translated, srt_path)

            # 4. 生成剪映草稿
            draft_path = self.create_jianying_draft(video_path, srt_path)

            return {
                "success": True,
                "video": video_path.name,
                "srt": str(srt_path),
                "draft": str(draft_path)
            }

        except Exception as e:
            print(f"[錯誤] {e}")
            return {
                "success": False,
                "video": video_path.name,
                "error": str(e)
            }

    def batch_process(self):
        """批量處理所有影片"""
        video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
        videos = [
            f for f in self.source_folder.iterdir()
            if f.is_file() and f.suffix.lower() in video_exts
        ]

        if not videos:
            print(f"[警告] 沒有找到影片: {self.source_folder}")
            return []

        print(f"找到 {len(videos)} 個影片待處理")

        results = []
        for video in videos:
            result = self.process_video(video)
            results.append(result)

        # 統計結果
        success = sum(1 for r in results if r["success"])
        print(f"\n{'='*50}")
        print(f"處理完成: {success}/{len(results)} 成功")
        print(f"{'='*50}")

        return results


def main():
    """主程式入口"""
    print("YouTube 影片翻譯工作流程")
    print("=" * 50)

    # 檢查 API Key
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("[錯誤] 請設定環境變數 DEEPSEEK_API_KEY")
        print("  Windows: set DEEPSEEK_API_KEY=sk-...")
        print("  或在 .env 檔案中設定")
        sys.exit(1)

    workflow = TranslationWorkflow()

    # 如果有命令列參數，處理單個檔案
    if len(sys.argv) > 1:
        video_path = Path(sys.argv[1])
        if video_path.exists():
            workflow.process_video(video_path)
        else:
            print(f"[錯誤] 檔案不存在: {video_path}")
    else:
        # 批量處理
        workflow.batch_process()


if __name__ == "__main__":
    main()
