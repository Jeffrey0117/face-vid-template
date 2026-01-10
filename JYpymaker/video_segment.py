"""定義視頻片段及其相關類（精簡版 - 移除特效相關功能）"""

import uuid
from copy import deepcopy

from typing import Optional, Literal, Union
from typing import Dict, List, Tuple, Any

from .time_util import tim, Timerange
from .segment import VisualSegment, ClipSettings, AudioFade
from .local_materials import VideoMaterial
from .animation import SegmentAnimations


class VideoSegment(VisualSegment):
    """安放在軌道上的一個視頻片段（精簡版）"""

    material_instance: VideoMaterial
    """視頻素材實例"""

    fade: Optional[AudioFade]
    """音頻淡入淡出效果, 可能為空"""

    def __init__(self, material: Union[VideoMaterial, str], target_timerange: Timerange, *,
                 source_timerange: Optional[Timerange] = None, speed: Optional[float] = None,
                 volume: float = 1.0, change_pitch: bool = False,
                 clip_settings: Optional[ClipSettings] = None):
        """利用給定的視頻素材構建一個軌道片段, 並指定其時間信息及播放速度/音量

        Args:
            material (`VideoMaterial` or `str`): 素材實例或素材路徑, 若為路徑則自動構造素材實例
            target_timerange (`Timerange`): 片段在軌道上的目標時間範圍
            source_timerange (`Timerange`, optional): 截取的素材片段的時間範圍, 默認從開頭截取
            speed (`float`, optional): 播放速度, 默認為1.0
            volume (`float`, optional): 音量, 默認為1.0
            change_pitch (`bool`, optional): 是否跟隨變速改變音調, 默認為否
            clip_settings (`ClipSettings`, optional): 圖像調節設置, 默認不作任何變換
        """
        if isinstance(material, str):
            material = VideoMaterial(material)

        if source_timerange is not None and speed is not None:
            target_timerange = Timerange(target_timerange.start, round(source_timerange.duration / speed))
        elif source_timerange is not None and speed is None:
            speed = source_timerange.duration / target_timerange.duration
        else:  # source_timerange is None
            speed = speed if speed is not None else 1.0
            source_timerange = Timerange(0, round(target_timerange.duration * speed))

        if source_timerange.end > material.duration:
            raise ValueError(f"截取的素材時間範圍 {source_timerange} 超出了素材時長({material.duration})")

        super().__init__(material.material_id, source_timerange, target_timerange,
                         speed, volume, change_pitch, clip_settings=clip_settings)

        self.material_instance = deepcopy(material)
        self.fade = None

    def add_fade(self, in_duration: Union[str, int], out_duration: Union[str, int]) -> "VideoSegment":
        """為視頻片段添加音頻淡入淡出效果

        Args:
            in_duration (`int` or `str`): 音頻淡入時長, 單位為微秒
            out_duration (`int` or `str`): 音頻淡出時長, 單位為微秒
        """
        if self.fade is not None:
            raise ValueError("當前片段已存在淡入淡出效果")

        if isinstance(in_duration, str): in_duration = tim(in_duration)
        if isinstance(out_duration, str): out_duration = tim(out_duration)

        self.fade = AudioFade(in_duration, out_duration)
        self.extra_material_refs.append(self.fade.fade_id)

        return self

    def export_json(self) -> Dict[str, Any]:
        json_dict = super().export_json()
        json_dict.update({
            "hdr_settings": {"intensity": 1.0, "mode": 1, "nits": 1000}
        })
        return json_dict


class StickerSegment(VisualSegment):
    """貼紙片段（精簡版）"""

    sticker_data: Dict[str, Any]
    """貼紙數據"""

    def __init__(self, sticker_data: Dict[str, Any], target_timerange: Timerange, *,
                 clip_settings: Optional[ClipSettings] = None):
        """創建貼紙片段"""
        material_id = sticker_data.get("id", uuid.uuid4().hex)

        super().__init__(material_id, None, target_timerange,
                         1.0, 1.0, False, clip_settings=clip_settings)

        self.sticker_data = deepcopy(sticker_data)

    def export_json(self) -> Dict[str, Any]:
        json_dict = super().export_json()
        json_dict.update({
            "hdr_settings": None
        })
        return json_dict


# 為了兼容性保留的空類定義
class Transition:
    """轉場效果（精簡版不支持）"""
    global_id: str

    def __init__(self):
        self.global_id = uuid.uuid4().hex

    def export_json(self) -> Dict[str, Any]:
        return {}


class Filter:
    """濾鏡效果（精簡版不支持）"""
    global_id: str

    def __init__(self):
        self.global_id = uuid.uuid4().hex

    def export_json(self) -> Dict[str, Any]:
        return {}


class VideoEffect:
    """視頻特效（精簡版不支持）"""
    global_id: str

    def __init__(self):
        self.global_id = uuid.uuid4().hex

    def export_json(self) -> Dict[str, Any]:
        return {}


class BackgroundFilling:
    """背景填充（精簡版不支持）"""

    def __init__(self):
        pass

    def export_json(self) -> Dict[str, Any]:
        return {}
