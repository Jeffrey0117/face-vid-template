"""定義視頻/文本動畫相關類（精簡版 - 僅保留基本結構）"""

import uuid

from typing import Union, Optional
from typing import Literal, Dict, List, Any

from .time_util import Timerange


class SegmentAnimations:
    """附加於某素材上的一系列動畫

    對視頻片段：入場、出場或組合動畫；對文本片段：入場、出場或循環動畫

    精簡版：不支持添加新動畫，僅用於模板模式
    """

    animation_id: str
    """系列動畫的全局id, 自動生成"""

    animations: List[Dict[str, Any]]
    """動畫列表（原始數據）"""

    def __init__(self):
        self.animation_id = uuid.uuid4().hex
        self.animations = []

    def get_animation_trange(self, animation_type: Literal["in", "out", "group", "loop"]) -> Optional[Timerange]:
        """獲取指定類型的動畫的時間範圍"""
        for animation in self.animations:
            if animation.get("type") == animation_type:
                return Timerange(animation.get("start", 0), animation.get("duration", 0))
        return None

    def export_json(self) -> Dict[str, Any]:
        return {
            "id": self.animation_id,
            "type": "sticker_animation",
            "multi_language_current": "none",
            "animations": self.animations
        }
