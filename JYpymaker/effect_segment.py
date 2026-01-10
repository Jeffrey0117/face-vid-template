"""定義特效/濾鏡片段（精簡版 - 僅保留基本結構）"""

import uuid
from typing import Optional, Dict, Any

from .time_util import Timerange
from .segment import BaseSegment


class EffectSegment(BaseSegment):
    """特效片段（精簡版 - 僅用於模板模式的導入）"""

    def __init__(self, material_id: str, target_timerange: Timerange):
        super().__init__(material_id, target_timerange)

    def export_json(self) -> Dict[str, Any]:
        json_dict = super().export_json()
        return json_dict


class FilterSegment(BaseSegment):
    """濾鏡片段（精簡版 - 僅用於模板模式的導入）"""

    def __init__(self, material_id: str, target_timerange: Timerange):
        super().__init__(material_id, target_timerange)

    def export_json(self) -> Dict[str, Any]:
        json_dict = super().export_json()
        return json_dict
