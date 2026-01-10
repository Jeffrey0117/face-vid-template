"""定義音頻片段及其相關類（精簡版）"""

import uuid
from copy import deepcopy

from typing import Optional, Union
from typing import Dict, List, Any

from .time_util import tim, Timerange
from .segment import MediaSegment, AudioFade
from .local_materials import AudioMaterial
from .keyframe import KeyframeProperty, KeyframeList


class AudioSegment(MediaSegment):
    """安放在軌道上的一個音頻片段"""

    material_instance: AudioMaterial
    """音頻素材實例"""

    fade: Optional[AudioFade]
    """音頻淡入淡出效果, 可能為空

    在放入軌道時自動添加到素材列表中
    """

    effects: List[Any]
    """音頻特效列表（精簡版不支持）"""

    def __init__(self, material: Union[AudioMaterial, str], target_timerange: Timerange, *,
                 source_timerange: Optional[Timerange] = None, speed: Optional[float] = None, volume: float = 1.0,
                 change_pitch: bool = False):
        """利用給定的音頻素材構建一個軌道片段, 並指定其時間信息及播放速度/音量

        Args:
            material (`AudioMaterial` or `str`): 素材實例或素材路徑, 若為路徑則自動構造素材實例
            target_timerange (`Timerange`): 片段在軌道上的目標時間範圍
            source_timerange (`Timerange`, optional): 截取的素材片段的時間範圍, 默認從開頭根據`speed`截取與`target_timerange`等長的一部分
            speed (`float`, optional): 播放速度, 默認為1.0. 此項與`source_timerange`同時指定時, 將覆蓋`target_timerange`中的時長
            volume (`float`, optional): 音量, 默認為1.0
            change_pitch (`bool`, optional): 是否跟隨變速改變音調, 默認為否

        Raises:
            `ValueError`: 指定的或計算出的`source_timerange`超出了素材的時長範圍
        """
        if isinstance(material, str):
            material = AudioMaterial(material)

        if source_timerange is not None and speed is not None:
            target_timerange = Timerange(target_timerange.start, round(source_timerange.duration / speed))
        elif source_timerange is not None and speed is None:
            speed = source_timerange.duration / target_timerange.duration
        else:  # source_timerange is None
            speed = speed if speed is not None else 1.0
            source_timerange = Timerange(0, round(target_timerange.duration * speed))

        if source_timerange.end > material.duration:
            raise ValueError(f"截取的素材時間範圍 {source_timerange} 超出了素材時長({material.duration})")

        super().__init__(material.material_id, source_timerange, target_timerange, speed, volume, change_pitch)

        self.material_instance = deepcopy(material)
        self.fade = None
        self.effects = []

    def add_fade(self, in_duration: Union[str, int], out_duration: Union[str, int]) -> "AudioSegment":
        """為音頻片段添加淡入淡出效果

        Args:
            in_duration (`int` or `str`): 音頻淡入時長, 單位為微秒, 若為字串則會調用`tim()`函數進行解析
            out_duration (`int` or `str`): 音頻淡出時長, 單位為微秒, 若為字串則會調用`tim()`函數進行解析

        Raises:
            `ValueError`: 當前片段已存在淡入淡出效果
        """
        if self.fade is not None:
            raise ValueError("當前片段已存在淡入淡出效果")

        if isinstance(in_duration, str): in_duration = tim(in_duration)
        if isinstance(out_duration, str): out_duration = tim(out_duration)

        self.fade = AudioFade(in_duration, out_duration)
        self.extra_material_refs.append(self.fade.fade_id)

        return self

    def add_keyframe(self, time_offset: int, volume: float) -> "AudioSegment":
        """為音頻片段創建一個*控制音量*的關鍵幀, 並自動加入到關鍵幀列表中

        Args:
            time_offset (`int`): 關鍵幀的時間偏移量, 單位為微秒
            volume (`float`): 音量在`time_offset`處的值
        """
        _property = KeyframeProperty.volume
        for kf_list in self.common_keyframes:
            if kf_list.keyframe_property == _property:
                kf_list.add_keyframe(time_offset, volume)
                return self
        kf_list = KeyframeList(_property)
        kf_list.add_keyframe(time_offset, volume)
        self.common_keyframes.append(kf_list)
        return self

    def export_json(self) -> Dict[str, Any]:
        json_dict = super().export_json()
        json_dict.update({
            "clip": None,
            "hdr_settings": None
        })
        return json_dict
