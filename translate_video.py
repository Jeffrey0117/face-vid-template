#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 影片翻譯工作流程
使用 Whisper 語音識別 + DeepSeek API 翻譯 + 剪映字幕生成
"""

import os
import re
import sys
import json
import shutil
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 設置路徑
sys.path.insert(0, str(Path(__file__).parent))

from faster_whisper import WhisperModel
from openai import OpenAI
from utils.color_utils import hex_to_rgb

# 載入設定
CONFIG_FILE = Path(__file__).parent / "translation_config.json"

def load_config():
    """載入翻譯設定"""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 預編譯正則表達式
TEXT_NUMBER_PATTERN = re.compile(r'^\d+\.\s*(.+)$')

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
        """初始化 Whisper 模型（自動降級：CUDA 失敗時使用 CPU）"""
        if self.whisper_model is None:
            model_name = self.config["whisper"]["model"]

            # 嘗試 GPU，失敗則降級到 CPU
            try:
                print(f"[Whisper] 載入模型: {model_name} (GPU)")
                self.whisper_model = WhisperModel(model_name, device="cuda", compute_type="float16")
                print("[Whisper] GPU 加速已啟用")
            except Exception as e:
                print(f"[Whisper] GPU 初始化失敗: {e}")
                print(f"[Whisper] 降級到 CPU 模式...")
                self.whisper_model = WhisperModel(model_name, device="cpu", compute_type="int8")
                print("[Whisper] CPU 模式已啟用（速度較慢）")

        return self.whisper_model

    def init_deepseek(self):
        """初始化 DeepSeek API 客戶端"""
        if self.deepseek_client is None:
            # 優先從 config 讀取，其次環境變數
            api_key = self.config["translation"].get("api_key") or os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("請在 translation_config.json 的 translation.api_key 填入 DeepSeek API Key")

            self.deepseek_client = OpenAI(
                api_key=api_key,
                base_url=self.config["translation"]["base_url"]
            )
        return self.deepseek_client

    def transcribe(self, video_path: Path) -> list:
        """使用 Whisper 轉錄影片"""
        print(f"[1/4] 語音識別: {video_path.name}")

        model = self.init_whisper()
        segments_generator, info = model.transcribe(
            str(video_path),
            language=self.config["whisper"]["language"],
            task=self.config["whisper"]["task"],
            temperature=self.config["whisper"]["temperature"],
            word_timestamps=self.config["whisper"]["word_timestamps"],
            vad_filter=True
        )

        segments = []
        for segment in segments_generator:
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })

        print(f"    識別完成: {len(segments)} 個片段")
        return segments

    def translate_batch(self, texts: list, max_retries: int = 3) -> list:
        """批次翻譯多句文字（含重試機制）"""
        client = self.init_deepseek()

        # 用編號格式組合多句
        numbered_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(texts)])

        prompt = f"""將以下英文字幕翻譯成繁體中文，保持編號格式，每行一句：

{numbered_text}

注意：
- 保持原本的編號格式（1. 2. 3. ...）
- 翻譯要簡潔、口語化
- 每句獨立一行"""

        last_error = None
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.config["translation"]["model"],
                    messages=[
                        {"role": "system", "content": "你是專業的字幕翻譯員，翻譯要簡潔、口語化、符合繁體中文習慣。請保持編號格式輸出。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                result = response.choices[0].message.content.strip()
                break  # 成功則跳出重試迴圈
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指數退避: 1s, 2s, 4s
                    print(f"    API 錯誤，{wait_time} 秒後重試 ({attempt + 1}/{max_retries}): {e}")
                    time.sleep(wait_time)
                else:
                    raise last_error

        # 解析結果
        translations = []
        for line in result.split("\n"):
            line = line.strip()
            if not line:
                continue
            # 移除編號 "1. ", "2. " 等
            match = TEXT_NUMBER_PATTERN.match(line)
            if match:
                translations.append(match.group(1))
            elif line and not line[0].isdigit():
                translations.append(line)

        # 確保數量匹配
        while len(translations) < len(texts):
            translations.append(texts[len(translations)])  # 用原文填充

        return translations[:len(texts)]

    def translate_segments(self, segments: list) -> list:
        """批次翻譯所有片段"""
        print(f"[2/4] 翻譯字幕: {len(segments)} 個片段")

        batch_size = self.config.get("translation", {}).get("batch_size", 20)
        translated = []

        # 分批處理
        for batch_start in range(0, len(segments), batch_size):
            batch_end = min(batch_start + batch_size, len(segments))
            batch = segments[batch_start:batch_end]

            texts = [seg["text"] for seg in batch]

            try:
                translated_texts = self.translate_batch(texts)

                for i, seg in enumerate(batch):
                    translated.append({
                        "start": seg["start"],
                        "end": seg["end"],
                        "original": seg["text"],
                        "text": translated_texts[i] if i < len(translated_texts) else seg["text"]
                    })

                print(f"    進度: {batch_end}/{len(segments)}")

            except Exception as e:
                print(f"    批次翻譯錯誤: {e}")
                # 失敗時保留原文
                for seg in batch:
                    translated.append({
                        "start": seg["start"],
                        "end": seg["end"],
                        "original": seg["text"],
                        "text": seg["text"]
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

    def get_jianying_drafts_path(self) -> Path:
        """取得剪映草稿資料夾路徑"""
        return Path(self.config.get("jianying_draft_folder",
            Path.home() / "AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft"))

    def create_jianying_draft(self, video_path: Path, srt_path: Path) -> Path:
        """創建剪映草稿並添加字幕"""
        print(f"[4/4] 生成剪映草稿")

        from pyJianYingDraft import DraftFolder, ScriptFile, Intro_type
        from pyJianYingDraft import trange, tim
        from pyJianYingDraft import VideoMaterial, TrackType, ClipSettings, TextStyle
        from moviepy import VideoFileClip

        # 複製模板
        draft_name = f"翻譯_{video_path.stem}"
        jianying_drafts = self.get_jianying_drafts_path()

        output_draft = jianying_drafts / draft_name

        if output_draft.exists():
            shutil.rmtree(output_draft)
        shutil.copytree(self.template_folder, output_draft)

        # 取得影片實際時長
        try:
            clip = VideoFileClip(str(video_path))
            video_duration = clip.duration
            clip.close()
            print(f"    影片時長: {video_duration:.1f} 秒")
        except Exception as e:
            print(f"    無法取得影片時長: {e}")
            video_duration = None

        # 載入草稿
        draft_json = output_draft / "draft_content.json"
        script = ScriptFile.load_template(str(draft_json))

        # 替換影片素材 (必須用絕對路徑)
        video_material = VideoMaterial(str(video_path.resolve()))
        video_track = script.get_imported_track(TrackType.video, index=0)
        script.replace_material_by_seg(video_track, 0, video_material)

        # 更新草稿時長
        if video_duration:
            duration_us = int(video_duration * 1_000_000)  # 轉換為微秒
            script.duration = duration_us
            # 更新影片軌道的時長
            for track in script.imported_tracks:
                if track.track_type == TrackType.video:
                    for seg in track.raw_data.get("segments", []):
                        seg["source_timerange"] = {"start": 0, "duration": duration_us}
                        seg["target_timerange"] = {"start": 0, "duration": duration_us}

        # 導入 SRT 字幕
        style = self.config["subtitle_style"]

        text_style = TextStyle(
            size=style["font_size"],
            color=hex_to_rgb(style["text_color"]),
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

        # 檢查是否跳過已存在的草稿
        draft_name = f"翻譯_{video_path.stem}"
        output_draft = self.get_jianying_drafts_path() / draft_name

        skip_existing = self.config.get("workflow", {}).get("skip_existing", False)
        if skip_existing and output_draft.exists():
            print(f"[跳過] 草稿已存在: {draft_name}")
            return {
                "success": True,
                "video": video_path.name,
                "skipped": True,
                "draft": str(output_draft)
            }

        try:
            # 檢查是否已有 SRT 檔案（跳過語音識別和翻譯）
            srt_path = self.output_folder / f"{video_path.stem}.srt"

            if srt_path.exists():
                print(f"[快取] 發現已存在的 SRT: {srt_path.name}")
                print(f"[跳過] 語音識別和翻譯（使用快取）")
            else:
                # 1. 語音識別
                segments = self.transcribe(video_path)

                # 2. 翻譯
                translated = self.translate_segments(segments)

                # 3. 生成 SRT
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

    def batch_process(self, max_workers: int = 2):
        """批量處理所有影片（並行）"""
        video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
        videos = [
            f for f in self.source_folder.iterdir()
            if f.is_file() and f.suffix.lower() in video_exts
        ]

        if not videos:
            print(f"[警告] 沒有找到影片: {self.source_folder}")
            return []

        print(f"找到 {len(videos)} 個影片待處理（並行數: {max_workers}）")

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任務
            future_to_video = {
                executor.submit(self.process_video, video): video
                for video in videos
            }

            # 收集結果
            for future in as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"[錯誤] {video.name}: {e}")
                    results.append({
                        "success": False,
                        "video": video.name,
                        "error": str(e)
                    })

        # 統計結果
        success = sum(1 for r in results if r.get("success"))
        print(f"\n{'='*50}")
        print(f"處理完成: {success}/{len(results)} 成功")
        print(f"{'='*50}")

        return results


def main():
    """主程式入口"""
    print("YouTube 影片翻譯工作流程")
    print("=" * 50)

    # 檢查 API Key（從配置檔或環境變數）
    config = load_config()
    api_key = config.get("translation", {}).get("api_key") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("[錯誤] 請在 translation_config.json 設定 api_key")
        print("  或設定環境變數 DEEPSEEK_API_KEY")
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
