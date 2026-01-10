"""軌道類及其元數據"""

import uuid

from enum import Enum
from typing import TypeVar, Generic, Type
from typing import Dict, List, Any, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .exceptions import SegmentOverlap
from .segment import BaseSegment
from .video_segment import VideoSegment, StickerSegment
from .audio_segment import AudioSegment
from .text_segment import TextSegment
from .effect_segment import EffectSegment, FilterSegment

@dataclass
class Track_meta:
    """與軌道類型關聯的軌道元數據"""

    segment_type: Union[Type[VideoSegment], Type[AudioSegment],
                        Type[EffectSegment], Type[FilterSegment],
                        Type[TextSegment], Type[StickerSegment], None]
    """與軌道關聯的片段類型"""
    render_index: int
    """默認渲染順序, 值越大越接近前景"""
    allow_modify: bool
    """當被導入時, 是否允許修改"""

class TrackType(Enum):
    """軌道類型枚舉

    變量名對應type屬性, 值表示相應的軌道元數據
    """

    video = Track_meta(VideoSegment, 0, True)
    audio = Track_meta(AudioSegment, 0, True)
    effect = Track_meta(EffectSegment, 10000, False)
    filter = Track_meta(FilterSegment, 11000, False)
    sticker = Track_meta(StickerSegment, 14000, False)
    text = Track_meta(TextSegment, 15000, True)

    adjust = Track_meta(None, 0, False)
    """僅供導入時使用, 不要嘗試新建此類型的軌道"""

    @staticmethod
    def from_name(name: str) -> "TrackType":
        """根據名稱獲取軌道類型枚舉"""
        for t in TrackType:
            if t.name == name:
                return t
        raise ValueError("Invalid track type: %s" % name)


class BaseTrack(ABC):
    """軌道基類"""

    track_type: TrackType
    """軌道類型"""
    name: str
    """軌道名稱"""
    track_id: str
    """軌道全局ID"""
    render_index: int
    """渲染順序, 值越大越接近前景"""

    @abstractmethod
    def export_json(self) -> Dict[str, Any]: ...

Seg_type = TypeVar("Seg_type", bound=BaseSegment)
class Track(BaseTrack, Generic[Seg_type]):
    """非模板模式下的軌道"""

    mute: bool
    """是否靜音"""

    segments: List[Seg_type]
    """該軌道包含的片段列表"""

    def __init__(self, track_type: TrackType, name: str, render_index: int, mute: bool):
        self.track_type = track_type
        self.name = name
        self.track_id = uuid.uuid4().hex
        self.render_index = render_index

        self.mute = mute
        self.segments = []

    @property
    def end_time(self) -> int:
        """軌道結束時間, 微秒"""
        if len(self.segments) == 0:
            return 0
        return self.segments[-1].target_timerange.end

    @property
    def accept_segment_type(self) -> Type[Seg_type]:
        """返回該軌道允許的片段類型"""
        return self.track_type.value.segment_type  # type: ignore

    def add_segment(self, segment: Seg_type) -> "Track[Seg_type]":
        """向軌道中添加一個片段, 添加的片段必須匹配軌道類型且不與現有片段重疊

        Args:
            segment (Seg_type): 要添加的片段

        Raises:
            `TypeError`: 新片段類型與軌道類型不匹配
            `SegmentOverlap`: 新片段與現有片段重疊
        """
        if not isinstance(segment, self.accept_segment_type):
            raise TypeError("New segment (%s) is not of the same type as the track (%s)" % (type(segment), self.accept_segment_type))

        # 檢查片段是否重疊
        for seg in self.segments:
            if seg.overlaps(segment):
                raise SegmentOverlap("New segment overlaps with existing segment [start: {}, end: {}]"
                                     .format(segment.target_timerange.start, segment.target_timerange.end))

        self.segments.append(segment)
        return self

    def export_json(self) -> Dict[str, Any]:
        # 為每個片段寫入render_index
        segment_exports = [seg.export_json() for seg in self.segments]
        for seg in segment_exports:
            seg["render_index"] = self.render_index

        return {
            "attribute": int(self.mute),
            "flag": 0,
            "id": self.track_id,
            "is_default_name": len(self.name) == 0,
            "name": self.name,
            "segments": segment_exports,
            "type": self.track_type.name
        }
