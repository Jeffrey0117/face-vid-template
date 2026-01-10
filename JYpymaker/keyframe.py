"""關鍵幀相關類"""

import uuid

from enum import Enum
from typing import Dict, List, Any

class Keyframe:
    """一個關鍵幀（關鍵點）, 目前只支持線性插值"""

    kf_id: str
    """關鍵幀全局id, 自動生成"""
    time_offset: int
    """相對於素材起始點的時間偏移量"""
    values: List[float]
    """關鍵幀的值, 似乎一般只有一個元素"""

    def __init__(self, time_offset: int, value: float):
        """給定時間偏移量及關鍵值, 初始化關鍵幀"""
        self.kf_id = uuid.uuid4().hex

        self.time_offset = time_offset
        self.values = [value]

    def export_json(self) -> Dict[str, Any]:
        return {
            # 默認值
            "curveType": "Line",
            "graphID": "",
            "left_control": {"x": 0.0, "y": 0.0},
            "right_control": {"x": 0.0, "y": 0.0},
            # 自定義屬性
            "id": self.kf_id,
            "time_offset": self.time_offset,
            "values": self.values
        }

class KeyframeProperty(Enum):
    """關鍵幀所控制的屬性類型"""

    position_x = "KFTypePositionX"
    """右移為正, 此處的數值應該為`剪映中顯示的值` / `草稿寬度`, 也即單位是半個畫布寬"""
    position_y = "KFTypePositionY"
    """上移為正, 此處的數值應該為`剪映中顯示的值` / `草稿高度`, 也即單位是半個畫布高"""
    rotation = "KFTypeRotation"
    """順時針旋轉的**角度**"""

    scale_x = "KFTypeScaleX"
    """單獨控制X軸縮放比例(1.0為不縮放), 與`uniform_scale`互斥"""
    scale_y = "KFTypeScaleY"
    """單獨控制Y軸縮放比例(1.0為不縮放), 與`uniform_scale`互斥"""
    uniform_scale = "UNIFORM_SCALE"
    """同時控制X軸及Y軸縮放比例(1.0為不縮放), 與`scale_x`和`scale_y`互斥"""

    alpha = "KFTypeAlpha"
    """不透明度, 1.0為完全不透明, 僅對`VideoSegment`有效"""
    saturation = "KFTypeSaturation"
    """飽和度, 0.0為原始飽和度, 範圍為-1.0到1.0, 僅對`VideoSegment`有效"""
    contrast = "KFTypeContrast"
    """對比度, 0.0為原始對比度, 範圍為-1.0到1.0, 僅對`VideoSegment`有效"""
    brightness = "KFTypeBrightness"
    """亮度, 0.0為原始亮度, 範圍為-1.0到1.0, 僅對`VideoSegment`有效"""

    volume = "KFTypeVolume"
    """音量, 1.0為原始音量, 僅對`AudioSegment`和`VideoSegment`有效"""

class KeyframeList:
    """關鍵幀列表, 記錄與某個特定屬性相關的一系列關鍵幀"""

    list_id: str
    """關鍵幀列表全局id, 自動生成"""
    keyframe_property: KeyframeProperty
    """關鍵幀對應的屬性"""
    keyframes: List[Keyframe]
    """關鍵幀列表"""

    def __init__(self, keyframe_property: KeyframeProperty):
        """為給定的關鍵幀屬性初始化關鍵幀列表"""
        self.list_id = uuid.uuid4().hex

        self.keyframe_property = keyframe_property
        self.keyframes = []

    def add_keyframe(self, time_offset: int, value: float):
        """給定時間偏移量及關鍵值, 向此關鍵幀列表中添加一個關鍵幀"""
        keyframe = Keyframe(time_offset, value)
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda x: x.time_offset)

    def export_json(self) -> Dict[str, Any]:
        return {
            "id": self.list_id,
            "keyframe_list": [kf.export_json() for kf in self.keyframes],
            "material_id": "",
            "property_type": self.keyframe_property.value
        }
