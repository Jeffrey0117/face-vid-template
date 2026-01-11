"""
JYpymaker 語音辨識模組 - 直接輸出繁體字幕

支援引擎：
    - faster-whisper（預設，多語言）
    - sensevoice（中文優化，支援中英日韓粵）

使用方式：
    python -m JYpymaker.transcribe video.mp4 -o output.srt
    python -m JYpymaker.transcribe video.mp4 --traditional  # 輸出繁體（預設）
    python -m JYpymaker.transcribe video.mp4 --simplified   # 輸出簡體
    python -m JYpymaker.transcribe video.mp4 --engine sensevoice  # 使用 SenseVoice
"""

import sys
from pathlib import Path
from typing import Optional, List, Tuple


def _transcribe_with_sensevoice(media_path: str, device: str = "auto") -> List[dict]:
    """
    使用 sherpa-onnx SenseVoice 進行語音辨識（中文優化，支援中英日韓粵）

    Returns:
        List[dict]: [{"start": float, "end": float, "text": str}, ...]
    """
    try:
        import sherpa_onnx
    except ImportError:
        raise ImportError("請安裝 sherpa-onnx: pip install sherpa-onnx")

    import tempfile
    import subprocess
    import os

    media_file = Path(media_path)

    # 找模型路徑
    model_dir = Path(__file__).parent.parent / "models" / "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17"
    if not model_dir.exists():
        raise FileNotFoundError(
            f"找不到 SenseVoice 模型，請先下載：\n"
            f"cd models && curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2 && tar xvf sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2"
        )

    # 轉換為 16kHz wav
    print("[SenseVoice] 準備音訊...")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    cmd = [
        "ffmpeg", "-y", "-i", str(media_file),
        "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le",
        wav_path
    ]
    subprocess.run(cmd, capture_output=True)

    # 載入 VAD 模型（用於分段）
    vad_model_path = Path(__file__).parent.parent / "models" / "silero_vad.onnx"
    if not vad_model_path.exists():
        print("[SenseVoice] 下載 VAD 模型...")
        import urllib.request
        vad_model_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(
            "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx",
            str(vad_model_path)
        )

    print("[SenseVoice] 載入模型...")

    # 建立 SenseVoice 辨識器
    recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
        model=str(model_dir / "model.onnx"),
        tokens=str(model_dir / "tokens.txt"),
        use_itn=True,
        num_threads=4,
    )

    # 建立 VAD
    vad_config = sherpa_onnx.VadModelConfig()
    vad_config.silero_vad.model = str(vad_model_path)
    vad_config.sample_rate = 16000

    vad = sherpa_onnx.VoiceActivityDetector(vad_config, buffer_size_in_seconds=30)

    # 讀取音訊
    print(f"[SenseVoice] 辨識中: {media_file.name}")
    wave = sherpa_onnx.read_wave(wav_path)
    samples = wave.samples
    sample_rate = wave.sample_rate

    # 清理暫存檔
    os.unlink(wav_path)

    # VAD 分段辨識
    segments = []
    window_size = int(0.1 * sample_rate)  # 100ms 窗口

    for i in range(0, len(samples), window_size):
        chunk = samples[i:i+window_size]
        if len(chunk) < window_size:
            chunk = list(chunk) + [0.0] * (window_size - len(chunk))
        vad.accept_waveform(chunk)

    vad.flush()

    while not vad.empty():
        segment = vad.front()
        vad.pop()

        start_time = segment.start / sample_rate
        end_time = (segment.start + len(segment.samples)) / sample_rate

        # 辨識這個片段
        stream = recognizer.create_stream()
        stream.accept_waveform(sample_rate, segment.samples)
        recognizer.decode_stream(stream)

        text = stream.result.text.strip()
        if text:
            segments.append({
                "start": start_time,
                "end": end_time,
                "text": text
            })

    print(f"[SenseVoice] 辨識完成，共 {len(segments)} 個片段")
    return segments


def _transcribe_with_whisper(
    media_path: str,
    model: str = "medium",
    language: str = "zh",
    device: str = "auto",
    initial_prompt: Optional[str] = None
) -> List[dict]:
    """
    使用 faster-whisper 進行語音辨識

    Returns:
        List[dict]: [{"start": float, "end": float, "text": str}, ...]
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError("請安裝 faster-whisper: pip install faster-whisper")

    media_file = Path(media_path)

    # 初始化模型
    print(f"[Whisper] 載入模型: {model}")

    if device == "auto":
        try:
            whisper_model = WhisperModel(model, device="cuda", compute_type="float16")
            print("[Whisper] 使用 GPU 加速")
        except Exception:
            print("[Whisper] GPU 不可用，使用 CPU")
            whisper_model = WhisperModel(model, device="cpu", compute_type="int8")
    elif device == "cuda":
        whisper_model = WhisperModel(model, device="cuda", compute_type="float16")
    else:
        whisper_model = WhisperModel(model, device="cpu", compute_type="int8")

    # 辨識（使用 VAD 過濾 + 更好的分句參數）
    print(f"[Whisper] 辨識中: {media_file.name}")
    segments, info = whisper_model.transcribe(
        str(media_file),
        language=language,
        initial_prompt=initial_prompt,
        word_timestamps=True,  # 開啟字級時間戳
        vad_filter=True,       # VAD 過濾靜音
        vad_parameters={
            "min_silence_duration_ms": 500,   # 靜音 0.5 秒就斷句
            "speech_pad_ms": 200,             # 語音前後 padding
        },
    )

    print(f"[Whisper] 偵測語言: {info.language}, 機率: {info.language_probability:.2%}")

    # 收集原始片段
    raw_segments = []
    for segment in segments:
        raw_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
            "words": segment.words if segment.words else []
        })

    # 智慧分句：根據標點和長度進一步切分
    srt_segments = _smart_split_segments(raw_segments)

    print(f"[Whisper] 辨識完成，共 {len(srt_segments)} 個片段")
    return srt_segments


def _smart_split_segments(segments: List[dict], max_chars: int = 25) -> List[dict]:
    """
    智慧分句：根據標點符號和長度切分過長的字幕

    Args:
        segments: 原始片段列表
        max_chars: 每段最大字數（預設 25 字，適合字幕閱讀）

    Returns:
        切分後的片段列表
    """
    import re

    result = []
    # 中文斷句標點
    split_pattern = re.compile(r'([。！？，、；：\.\!\?\,\;])')

    for seg in segments:
        text = seg["text"]
        start = seg["start"]
        end = seg["end"]
        words = seg.get("words", [])

        # 如果文字夠短，直接保留
        if len(text) <= max_chars:
            result.append({"start": start, "end": end, "text": text})
            continue

        # 有字級時間戳的話，用更精確的方式分句
        if words:
            current_text = ""
            current_start = None
            current_end = None

            for word in words:
                word_text = word.word if hasattr(word, 'word') else word.get('word', '')
                word_start = word.start if hasattr(word, 'start') else word.get('start', 0)
                word_end = word.end if hasattr(word, 'end') else word.get('end', 0)

                if current_start is None:
                    current_start = word_start

                current_text += word_text
                current_end = word_end

                # 遇到斷句標點或超過長度限制
                is_punctuation = bool(split_pattern.search(word_text))
                is_too_long = len(current_text) >= max_chars

                if is_punctuation or is_too_long:
                    if current_text.strip():
                        result.append({
                            "start": current_start,
                            "end": current_end,
                            "text": current_text.strip()
                        })
                    current_text = ""
                    current_start = None

            # 處理剩餘文字
            if current_text.strip():
                result.append({
                    "start": current_start or start,
                    "end": current_end or end,
                    "text": current_text.strip()
                })
        else:
            # 沒有字級時間戳，用標點切分並估算時間
            parts = split_pattern.split(text)
            # 合併標點到前一個片段
            merged = []
            for i, part in enumerate(parts):
                if split_pattern.match(part) and merged:
                    merged[-1] += part
                elif part.strip():
                    merged.append(part)

            if not merged:
                result.append({"start": start, "end": end, "text": text})
                continue

            # 按比例分配時間
            total_chars = sum(len(p) for p in merged)
            duration = end - start
            current_time = start

            for part in merged:
                part_duration = (len(part) / total_chars) * duration if total_chars > 0 else 0
                part_end = current_time + part_duration

                # 如果還是太長，再切分
                if len(part) > max_chars:
                    sub_parts = [part[i:i+max_chars] for i in range(0, len(part), max_chars)]
                    sub_duration = part_duration / len(sub_parts)
                    for sub in sub_parts:
                        result.append({
                            "start": current_time,
                            "end": current_time + sub_duration,
                            "text": sub.strip()
                        })
                        current_time += sub_duration
                else:
                    result.append({
                        "start": current_time,
                        "end": part_end,
                        "text": part.strip()
                    })
                    current_time = part_end

    return result


def transcribe_to_srt(
    media_path: str,
    output_path: Optional[str] = None,
    model: str = "medium",
    language: str = "zh",
    traditional: bool = True,
    device: str = "auto",
    initial_prompt: Optional[str] = None,
    engine: str = "whisper"
) -> str:
    """
    語音辨識並輸出 SRT 字幕檔

    Args:
        media_path: 影片或音訊檔案路徑
        output_path: 輸出 SRT 路徑（預設為原檔名.srt）
        model: Whisper 模型 (tiny, base, small, medium, large-v3)
        language: 語言代碼 (zh, en, ja, etc.)
        traditional: 是否轉換為繁體中文（預設 True）
        device: 裝置 (auto, cuda, cpu)
        initial_prompt: 提示詞，可引導輸出風格
        engine: 辨識引擎 (whisper, paddle)

    Returns:
        輸出的 SRT 檔案路徑
    """
    media_file = Path(media_path)
    if not media_file.exists():
        raise FileNotFoundError(f"找不到檔案: {media_path}")

    # 決定輸出路徑
    if output_path is None:
        suffix = "_zh-TW" if traditional else "_zh-CN"
        output_path = str(media_file.with_suffix("")) + suffix + ".srt"

    # 根據引擎選擇辨識方式
    if engine == "sensevoice":
        # SenseVoice 辨識（中文優化）
        srt_segments = _transcribe_with_sensevoice(media_path, device=device)
    else:
        # faster-whisper 辨識（預設）
        if initial_prompt is None and language == "zh" and traditional:
            initial_prompt = "以下是繁體中文的語音內容。"

        srt_segments = _transcribe_with_whisper(
            media_path,
            model=model,
            language=language,
            device=device,
            initial_prompt=initial_prompt
        )

    # 繁體轉換
    if traditional and language == "zh":
        print("[OpenCC] 轉換為繁體中文...")
        try:
            from .converter import convert_text
            for seg in srt_segments:
                seg["text"] = convert_text(seg["text"], mode="s2twp")
        except ImportError:
            print("[OpenCC] 警告：無法載入 OpenCC，跳過繁體轉換")

    # 寫入 SRT
    _write_srt(srt_segments, output_path)
    print(f"[SRT] 已儲存: {output_path}")

    return output_path


def _format_srt_time(seconds: float) -> str:
    """格式化 SRT 時間碼"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _write_srt(segments: List[dict], output_path: str):
    """寫入 SRT 檔案"""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            start_time = _format_srt_time(seg["start"])
            end_time = _format_srt_time(seg["end"])
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{seg['text']}\n\n")


def transcribe_to_draft(
    media_path: str,
    draft_name: Optional[str] = None,
    model: str = "medium",
    language: str = "zh",
    traditional: bool = True,
    device: str = "auto",
    engine: str = "whisper"
) -> str:
    """
    一條龍：影片 → 語音辨識 → 繁體字幕 → 剪映草稿

    Args:
        media_path: 影片檔案路徑
        draft_name: 草稿名稱（預設為影片檔名）
        model: Whisper 模型
        language: 語言代碼
        traditional: 是否轉換為繁體
        device: 運算裝置
        engine: 辨識引擎 (whisper, paddle)

    Returns:
        草稿資料夾路徑
    """
    import shutil
    import json
    from .converter import get_jianying_drafts_path
    from .script_file import ScriptFile
    from .local_materials import VideoMaterial
    from .text_segment import TextStyle
    from .segment import ClipSettings
    from .time_util import Timerange

    media_file = Path(media_path)
    if not media_file.exists():
        raise FileNotFoundError(f"找不到檔案: {media_path}")

    # 1. 語音辨識
    print("=" * 50)
    print("[Step 1/3] 語音辨識")
    print("=" * 50)

    srt_path = transcribe_to_srt(
        media_path,
        model=model,
        language=language,
        traditional=traditional,
        device=device,
        engine=engine
    )

    # 2. 建立草稿資料夾
    print()
    print("=" * 50)
    print("[Step 2/3] 建立剪映草稿")
    print("=" * 50)

    if draft_name is None:
        draft_name = media_file.stem

    drafts_path = get_jianying_drafts_path()
    draft_folder = drafts_path / draft_name

    # 如果已存在，加上數字
    counter = 1
    original_name = draft_name
    while draft_folder.exists():
        draft_name = f"{original_name}_{counter}"
        draft_folder = drafts_path / draft_name
        counter += 1

    draft_folder.mkdir(parents=True, exist_ok=True)
    print(f"[Draft] 建立資料夾: {draft_folder}")

    # 3. 建立草稿內容
    video_material = VideoMaterial(str(media_file))
    print(f"[Draft] 影片時長: {video_material.duration / 1_000_000:.1f} 秒")

    # 建立空白草稿
    script = ScriptFile(
        width=1920,
        height=1080,
        fps=30
    )

    # 加入影片軌道
    from .track import Track
    from .video_segment import VideoSegment

    video_track = Track(track_type="video", name="影片軌")
    video_seg = VideoSegment(
        material=video_material,
        target_timerange=Timerange(0, video_material.duration),
        source_timerange=Timerange(0, video_material.duration)
    )
    video_track.segments.append(video_seg)
    script.tracks.append(video_track)

    # 加入音訊軌道
    from .audio_segment import AudioSegment
    from .local_materials import AudioMaterial

    audio_track = Track(track_type="audio", name="音訊軌")
    # 從影片提取音訊素材
    audio_material = AudioMaterial(str(media_file))
    audio_seg = AudioSegment(
        material=audio_material,
        target_timerange=Timerange(0, video_material.duration),
        source_timerange=Timerange(0, video_material.duration)
    )
    audio_track.segments.append(audio_seg)
    script.tracks.append(audio_track)

    # 設定草稿時長
    script.duration = video_material.duration

    # 導入字幕
    print(f"[Draft] 導入字幕: {srt_path}")

    text_style = TextStyle(
        size=8.0,
        color=(1.0, 1.0, 1.0),
        bold=False
    )
    clip_settings = ClipSettings(
        transform_y=-0.75
    )

    script.import_srt(
        srt_path,
        track_name="字幕軌",
        text_style=text_style,
        clip_settings=clip_settings
    )

    # 儲存草稿
    draft_content_path = draft_folder / "draft_content.json"
    script.save_as(str(draft_content_path))
    print(f"[Draft] 已儲存: {draft_content_path}")

    # 建立 draft_meta_info.json
    meta_info = {
        "draft_fold_path": str(draft_folder),
        "draft_name": draft_name,
        "draft_timeline_materials_size_": 0,
        "tm_draft_create": int(Path(media_file).stat().st_mtime * 1000000),
        "tm_draft_modified": int(Path(media_file).stat().st_mtime * 1000000)
    }
    meta_path = draft_folder / "draft_meta_info.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 50)
    print("[完成]")
    print("=" * 50)
    print(f"草稿名稱: {draft_name}")
    print(f"草稿路徑: {draft_folder}")
    print(f"字幕檔案: {srt_path}")
    print()
    print("請重新開啟剪映即可看到此草稿！")

    return str(draft_folder)


def main():
    """命令列介面"""
    import argparse

    parser = argparse.ArgumentParser(
        description="語音辨識 → 繁體 SRT 字幕",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 辨識中文影片，輸出繁體 SRT
  python -m JYpymaker.transcribe video.mp4

  # 辨識英文影片
  python -m JYpymaker.transcribe video.mp4 -l en

  # 使用較大模型提高準確度
  python -m JYpymaker.transcribe video.mp4 -m large-v3

  # 輸出簡體
  python -m JYpymaker.transcribe video.mp4 --simplified
"""
    )

    parser.add_argument("input", help="影片或音訊檔案")
    parser.add_argument("-o", "--output", help="輸出 SRT 檔案路徑")
    parser.add_argument("-m", "--model", default="medium",
                        help="Whisper 模型 (tiny/base/small/medium/large-v3)")
    parser.add_argument("-l", "--language", default="zh",
                        help="語言代碼 (zh/en/ja/...)")
    parser.add_argument("--traditional", action="store_true", default=True,
                        help="輸出繁體中文（預設）")
    parser.add_argument("--simplified", action="store_true",
                        help="輸出簡體中文")
    parser.add_argument("--device", default="auto",
                        choices=["auto", "cuda", "cpu"],
                        help="運算裝置")
    parser.add_argument("-p", "--prompt", help="提示詞")

    args = parser.parse_args()

    # simplified 覆蓋 traditional
    traditional = not args.simplified

    try:
        output = transcribe_to_srt(
            args.input,
            output_path=args.output,
            model=args.model,
            language=args.language,
            traditional=traditional,
            device=args.device,
            initial_prompt=args.prompt
        )
        print(f"\n完成！字幕檔案: {output}")
    except Exception as e:
        print(f"\n錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
