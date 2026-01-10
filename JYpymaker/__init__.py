"""
JYpymaker - 精簡版剪映草稿生成庫

專為 translate_video.py 設計的輕量化版本，移除了大部分特效相關功能，
僅保留核心的素材管理、軌道操作、字幕導入等功能。
"""

import sys

from .local_materials import CropSettings, VideoMaterial, AudioMaterial
from .keyframe import KeyframeProperty

from .time_util import Timerange
from .audio_segment import AudioSegment
from .video_segment import VideoSegment, StickerSegment, ClipSettings
from .effect_segment import EffectSegment, FilterSegment
from .text_segment import TextSegment, TextStyle, TextBorder, TextBackground, TextShadow

from .track import TrackType
from .template_mode import ShrinkMode, ExtendMode
from .script_file import ScriptFile
from .draft_folder import DraftFolder

from .time_util import SEC, tim, trange

# 簡繁轉換（延遲導入，避免強制依賴 opencc）
from .converter import (
    convert_text, convert_srt_file, convert_draft, convert_draft_file,
    get_jianying_drafts_path, list_drafts, find_draft_by_name
)

__all__ = [
    # 素材類
    "CropSettings",
    "VideoMaterial",
    "AudioMaterial",

    # 關鍵幀
    "KeyframeProperty",

    # 時間工具
    "Timerange",
    "SEC",
    "tim",
    "trange",

    # 片段類
    "AudioSegment",
    "VideoSegment",
    "StickerSegment",
    "ClipSettings",
    "EffectSegment",
    "FilterSegment",
    "TextSegment",
    "TextStyle",
    "TextBorder",
    "TextBackground",
    "TextShadow",

    # 軌道和模式
    "TrackType",
    "ShrinkMode",
    "ExtendMode",

    # 核心類
    "ScriptFile",
    "DraftFolder",

    # 簡繁轉換
    "convert_text",
    "convert_srt_file",
    "convert_draft",
    "convert_draft_file",

    # 草稿管理
    "get_jianying_drafts_path",
    "list_drafts",
    "find_draft_by_name",
]

# 版本信息
__version__ = "0.1.0"
