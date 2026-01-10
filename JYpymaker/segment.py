"""定義片段基類及部分比較通用的屬性類"""

import uuid
from typing import Optional, Dict, List, Any, Union

from .animation import SegmentAnimations
from .time_util import Timerange, tim
from .keyframe import KeyframeList, KeyframeProperty

class BaseSegment:
    """片段基類"""

    segment_id: str
    """片段全局id, 由程序自動生成"""
    material_id: str
    """使用的素材id"""
    target_timerange: Timerange
    """片段在軌道上的時間範圍"""

    common_keyframes: List[KeyframeList]
    """各屬性的關鍵幀列表"""

    def __init__(self, material_id: str, target_timerange: Timerange):
        self.segment_id = uuid.uuid4().hex
        self.material_id = material_id
        self.target_timerange = target_timerange

        self.common_keyframes = []

    @property
    def start(self) -> int:
        """片段開始時間, 單位為微秒"""
        return self.target_timerange.start
    @start.setter
    def start(self, value: int):
        self.target_timerange.start = value

    @property
    def duration(self) -> int:
        """片段持續時間, 單位為微秒"""
        return self.target_timerange.duration
    @duration.setter
    def duration(self, value: int):
        self.target_timerange.duration = value

    @property
    def end(self) -> int:
        """片段結束時間, 單位為微秒"""
        return self.target_timerange.end

    def overlaps(self, other: "BaseSegment") -> bool:
        """判斷是否與另一個片段有重疊"""
        return self.target_timerange.overlaps(other.target_timerange)

    def export_json(self) -> Dict[str, Any]:
        """返回通用於各種片段的屬性"""
        return {
            "enable_adjust": True,
            "enable_color_correct_adjust": False,
            "enable_color_curves": True,
            "enable_color_match_adjust": False,
            "enable_color_wheels": True,
            "enable_lut": True,
            "enable_smart_color_adjust": False,
            "last_nonzero_volume": 1.0,
            "reverse": False,
            "track_attribute": 0,
            "track_render_index": 0,
            "visible": True,
            # 寫入自定義字段
            "id": self.segment_id,
            "material_id": self.material_id,
            "target_timerange": self.target_timerange.export_json(),

            "common_keyframes": [kf_list.export_json() for kf_list in self.common_keyframes],
            "keyframe_refs": [],  # 意義不明
        }

class Speed:
    """播放速度對象, 目前只支持固定速度"""

    global_id: str
    """全局id, 由程序自動生成"""
    speed: float
    """播放速度"""

    def __init__(self, speed: float):
        self.global_id = uuid.uuid4().hex
        self.speed = speed

    def export_json(self) -> Dict[str, Any]:
        return {
            "curve_speed": None,
            "id": self.global_id,
            "mode": 0,
            "speed": self.speed,
            "type": "speed"
        }

class AudioFade:
    """音頻淡入淡出效果"""

    fade_id: str
    """淡入淡出效果的全局id, 自動生成"""

    in_duration: int
    """淡入時長, 單位為微秒"""
    out_duration: int
    """淡出時長, 單位為微秒"""

    def __init__(self, in_duration: int, out_duration: int):
        """根據給定的淡入/淡出時長構造一個淡入淡出效果"""

        self.fade_id = uuid.uuid4().hex
        self.in_duration = in_duration
        self.out_duration = out_duration

    def export_json(self) -> Dict[str, Any]:
        return {
            "id": self.fade_id,
            "fade_in_duration": self.in_duration,
            "fade_out_duration": self.out_duration,
            "fade_type": 0,
            "type": "audio_fade"
        }

class ClipSettings:
    """素材片段的圖像調節設置"""

    alpha: float
    """圖像不透明度, 0-1"""
    flip_horizontal: bool
    """是否水平翻轉"""
    flip_vertical: bool
    """是否垂直翻轉"""
    rotation: float
    """順時針旋轉的**角度**, 可正可負"""
    scale_x: float
    """水平縮放比例"""
    scale_y: float
    """垂直縮放比例"""
    transform_x: float
    """水平位移, 單位為半個畫布寬"""
    transform_y: float
    """垂直位移, 單位為半個畫布高"""

    def __init__(self, *, alpha: float = 1.0,
                 flip_horizontal: bool = False, flip_vertical: bool = False,
                 rotation: float = 0.0,
                 scale_x: float = 1.0, scale_y: float = 1.0,
                 transform_x: float = 0.0, transform_y: float = 0.0):
        """初始化圖像調節設置, 默認不作任何圖像變換

        Args:
            alpha (float, optional): 圖像不透明度, 0-1. 默認為1.0.
            flip_horizontal (bool, optional): 是否水平翻轉. 默認為False.
            flip_vertical (bool, optional): 是否垂直翻轉. 默認為False.
            rotation (float, optional): 順時針旋轉的**角度**, 可正可負. 默認為0.0.
            scale_x (float, optional): 水平縮放比例. 默認為1.0.
            scale_y (float, optional): 垂直縮放比例. 默認為1.0.
            transform_x (float, optional): 水平位移, 單位為半個畫布寬. 默認為0.0.
            transform_y (float, optional): 垂直位移, 單位為半個畫布高. 默認為0.0.
                參考: 剪映導入的字幕似乎取此值為-0.8
        """
        self.alpha = alpha
        self.flip_horizontal, self.flip_vertical = flip_horizontal, flip_vertical
        self.rotation = rotation
        self.scale_x, self.scale_y = scale_x, scale_y
        self.transform_x, self.transform_y = transform_x, transform_y

    def export_json(self) -> Dict[str, Any]:
        clip_settings_json = {
            "alpha": self.alpha,
            "flip": {"horizontal": self.flip_horizontal, "vertical": self.flip_vertical},
            "rotation": self.rotation,
            "scale": {"x": self.scale_x, "y": self.scale_y},
            "transform": {"x": self.transform_x, "y": self.transform_y}
        }
        return clip_settings_json

class MediaSegment(BaseSegment):
    """媒體片段基類"""

    source_timerange: Optional[Timerange]
    """截取的素材片段的時間範圍, 對貼紙而言不存在"""
    speed: Speed
    """播放速度設置"""
    volume: float
    """音量"""
    change_pitch: bool
    """是否跟隨變速改變音調"""

    extra_material_refs: List[str]
    """附加的素材id列表, 用於連結動畫/特效等"""

    def __init__(self, material_id: str, source_timerange: Optional[Timerange], target_timerange: Timerange, speed: float, volume: float, change_pitch: bool):
        super().__init__(material_id, target_timerange)

        self.source_timerange = source_timerange
        self.speed = Speed(speed)
        self.volume = volume
        self.change_pitch = change_pitch

        self.extra_material_refs = [self.speed.global_id]

    def export_json(self) -> Dict[str, Any]:
        """返回通用於音頻和視頻片段的默認屬性"""
        ret = super().export_json()
        ret.update({
            "source_timerange": self.source_timerange.export_json() if self.source_timerange else None,
            "speed": self.speed.speed,
            "volume": self.volume,
            "extra_material_refs": self.extra_material_refs,
            "is_tone_modify": self.change_pitch,
        })
        return ret

class VisualSegment(MediaSegment):
    """視覺片段基類，用於處理所有可見片段（視頻、貼紙、文本）的共同屬性和行為"""

    clip_settings: ClipSettings
    """圖像調節設置, 其效果可被關鍵幀覆蓋"""

    uniform_scale: bool
    """是否鎖定XY軸縮放比例"""

    animations_instance: Optional[SegmentAnimations]
    """動畫實例, 可能為空

    在放入軌道時自動添加到素材列表中
    """

    def __init__(self, material_id: str, source_timerange: Optional[Timerange], target_timerange: Timerange,
                 speed: float, volume: float, change_pitch: bool, *, clip_settings: Optional[ClipSettings]):
        """初始化視覺片段基類

        Args:
            material_id (`str`): 素材id
            source_timerange (`Timerange`, optional): 截取的素材片段的時間範圍
            target_timerange (`Timerange`): 片段在軌道上的目標時間範圍
            speed (`float`): 播放速度
            volume (`float`): 音量
            change_pitch (`bool`): 是否跟隨變速改變音調
            clip_settings (`ClipSettings`, optional): 圖像調節設置, 默認不作任何變換
        """
        super().__init__(material_id, source_timerange, target_timerange, speed, volume, change_pitch)

        self.clip_settings = clip_settings if clip_settings is not None else ClipSettings()
        self.uniform_scale = True
        self.animations_instance = None

    def add_keyframe(self, _property: KeyframeProperty, time_offset: Union[int, str], value: float) -> "VisualSegment":
        """為給定屬性創建一個關鍵幀, 並自動加入到關鍵幀列表中

        Args:
            _property (`KeyframeProperty`): 要控制的屬性
            time_offset (`int` or `str`): 關鍵幀的時間偏移量, 單位為微秒. 若傳入字串則會調用`tim()`函數進行解析.
            value (`float`): 屬性在`time_offset`處的值

        Raises:
            `ValueError`: 試圖同時設置`uniform_scale`以及`scale_x`或`scale_y`其中一者
        """
        if (_property == KeyframeProperty.scale_x or _property == KeyframeProperty.scale_y) and self.uniform_scale:
            self.uniform_scale = False
        elif _property == KeyframeProperty.uniform_scale:
            if not self.uniform_scale:
                raise ValueError("已設置 scale_x 或 scale_y 時, 不能再設置 uniform_scale")
            _property = KeyframeProperty.scale_x

        if isinstance(time_offset, str): time_offset = tim(time_offset)

        for kf_list in self.common_keyframes:
            if kf_list.keyframe_property == _property:
                kf_list.add_keyframe(time_offset, value)
                return self
        kf_list = KeyframeList(_property)
        kf_list.add_keyframe(time_offset, value)
        self.common_keyframes.append(kf_list)
        return self

    def export_json(self) -> Dict[str, Any]:
        """導出通用於所有視覺片段的JSON數據"""
        json_dict = super().export_json()
        json_dict.update({
            "clip": self.clip_settings.export_json(),
            "uniform_scale": {"on": self.uniform_scale, "value": 1.0},
        })
        return json_dict
