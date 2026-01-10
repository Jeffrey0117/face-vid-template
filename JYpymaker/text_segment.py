"""定義文本片段及其相關類（精簡版）"""

import json
import uuid
from copy import deepcopy

from typing import Dict, Tuple, Any
from typing import Union, Optional, Literal

from .time_util import Timerange, tim
from .segment import ClipSettings, VisualSegment
from .animation import SegmentAnimations

class TextStyle:
    """字體樣式類"""

    size: float
    """字體大小"""

    bold: bool
    """是否加粗"""
    italic: bool
    """是否斜體"""
    underline: bool
    """是否加下劃線"""

    color: Tuple[float, float, float]
    """字體顏色, RGB三元組, 取值範圍為[0, 1]"""
    alpha: float
    """字體不透明度"""

    align: Literal[0, 1, 2]
    """對齊方式"""
    vertical: bool
    """是否為豎排文本"""

    letter_spacing: int
    """字符間距"""
    line_spacing: int
    """行間距"""

    auto_wrapping: bool
    """是否自動換行"""
    max_line_width: float
    """最大行寬, 取值範圍為[0, 1]"""

    def __init__(self, *, size: float = 8.0, bold: bool = False, italic: bool = False, underline: bool = False,
                 color: Tuple[float, float, float] = (1.0, 1.0, 1.0), alpha: float = 1.0,
                 align: Literal[0, 1, 2] = 0, vertical: bool = False,
                 letter_spacing: int = 0, line_spacing: int = 0,
                 auto_wrapping: bool = False, max_line_width: float = 0.82):
        """
        Args:
            size (`float`, optional): 字體大小, 默認為8.0
            bold (`bool`, optional): 是否加粗, 默認為否
            italic (`bool`, optional): 是否斜體, 默認為否
            underline (`bool`, optional): 是否加下劃線, 默認為否
            color (`Tuple[float, float, float]`, optional): 字體顏色, RGB三元組, 取值範圍為[0, 1], 默認為白色
            alpha (`float`, optional): 字體不透明度, 取值範圍[0, 1], 默認不透明
            align (`int`, optional): 對齊方式, 0: 左對齊, 1: 居中, 2: 右對齊, 默認為左對齊
            vertical (`bool`, optional): 是否為豎排文本, 默認為否
            letter_spacing (`int`, optional): 字符間距, 定義與剪映中一致, 默認為0
            line_spacing (`int`, optional): 行間距, 定義與剪映中一致, 默認為0
            auto_wrapping (`bool`, optional): 是否自動換行, 默認關閉
            max_line_width (`float`, optional): 每行最大行寬占屏幕寬度比例, 取值範圍為[0, 1], 默認為0.82
        """
        self.size = size
        self.bold = bold
        self.italic = italic
        self.underline = underline

        self.color = color
        self.alpha = alpha

        self.align = align
        self.vertical = vertical

        self.letter_spacing = letter_spacing
        self.line_spacing = line_spacing

        self.auto_wrapping = auto_wrapping
        self.max_line_width = max_line_width

class TextBorder:
    """文本描邊的參數"""

    alpha: float
    """描邊不透明度"""
    color: Tuple[float, float, float]
    """描邊顏色, RGB三元組, 取值範圍為[0, 1]"""
    width: float
    """描邊寬度"""

    def __init__(self, *, alpha: float = 1.0, color: Tuple[float, float, float] = (0.0, 0.0, 0.0), width: float = 40.0):
        """
        Args:
            alpha (`float`, optional): 描邊不透明度, 取值範圍[0, 1], 默認為1.0
            color (`Tuple[float, float, float]`, optional): 描邊顏色, RGB三元組, 取值範圍為[0, 1], 默認為黑色
            width (`float`, optional): 描邊寬度, 取值範圍大約為[0, 50], 默認為40.0
        """
        self.alpha = alpha
        self.color = color
        self.width = width

class TextBackground:
    """文本背景框的參數"""

    alpha: float
    """背景不透明度"""
    color: Tuple[float, float, float]
    """背景顏色, RGB三元組, 取值範圍為[0, 1]"""
    round: float
    """背景框圓角程度"""

    def __init__(self, *, alpha: float = 1.0, color: Tuple[float, float, float] = (0.0, 0.0, 0.0), round: float = 0.0):
        """
        Args:
            alpha (`float`, optional): 背景不透明度, 取值範圍[0, 1], 默認為1.0
            color (`Tuple[float, float, float]`, optional): 背景顏色, RGB三元組, 取值範圍為[0, 1], 默認為黑色
            round (`float`, optional): 背景框圓角程度, 取值範圍大約為[0, 1], 默認為0.0
        """
        self.alpha = alpha
        self.color = color
        self.round = round

class TextShadow:
    """文本陰影的參數"""

    alpha: float
    """陰影不透明度"""
    color: Tuple[float, float, float]
    """陰影顏色, RGB三元組, 取值範圍為[0, 1]"""
    angle: float
    """陰影角度（度）"""
    distance: float
    """陰影距離"""
    blur: float
    """陰影模糊程度"""

    def __init__(self, *, alpha: float = 0.8, color: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 angle: float = -45.0, distance: float = 4.0, blur: float = 8.0):
        """
        Args:
            alpha (`float`, optional): 陰影不透明度, 取值範圍[0, 1], 默認為0.8
            color (`Tuple[float, float, float]`, optional): 陰影顏色, RGB三元組, 取值範圍為[0, 1], 默認為黑色
            angle (`float`, optional): 陰影角度（度）, 默認為-45.0
            distance (`float`, optional): 陰影距離, 默認為4.0
            blur (`float`, optional): 陰影模糊程度, 默認為8.0
        """
        self.alpha = alpha
        self.color = color
        self.angle = angle
        self.distance = distance
        self.blur = blur


class TextSegment(VisualSegment):
    """安放在軌道上的一個文本片段"""

    text_id: str
    """文本素材id, 由程序自動生成"""
    content: str
    """文本內容"""
    text_style: TextStyle
    """文本樣式"""

    border: Optional[TextBorder]
    """文本描邊"""
    background: Optional[TextBackground]
    """文本背景框"""
    shadow: Optional[TextShadow]
    """文本陰影"""

    def __init__(self, content: str, target_timerange: Timerange, *,
                 text_style: Optional[TextStyle] = None, clip_settings: Optional[ClipSettings] = None,
                 border: Optional[TextBorder] = None, background: Optional[TextBackground] = None,
                 shadow: Optional[TextShadow] = None):
        """創建一個文本片段

        Args:
            content (`str`): 文本內容
            target_timerange (`Timerange`): 片段在軌道上的目標時間範圍
            text_style (`TextStyle`, optional): 文本樣式, 默認使用TextStyle()的默認值
            clip_settings (`ClipSettings`, optional): 圖像調節設置, 默認不作任何變換
            border (`TextBorder`, optional): 文本描邊, 默認無描邊
            background (`TextBackground`, optional): 文本背景框, 默認無背景
            shadow (`TextShadow`, optional): 文本陰影, 默認無陰影
        """
        self.text_id = uuid.uuid4().hex

        super().__init__(self.text_id, None, target_timerange,
                         1.0, 1.0, False, clip_settings=clip_settings)

        self.content = content
        self.text_style = text_style if text_style is not None else TextStyle()
        self.border = border
        self.background = background
        self.shadow = shadow

    def _generate_text_material(self) -> Dict[str, Any]:
        """生成文本素材的JSON數據"""
        style = self.text_style

        # 基本樣式內容
        styles_content = {
            "background_alpha": self.background.alpha if self.background else 0.0,
            "background_color": list(self.background.color) if self.background else [0.0, 0.0, 0.0],
            "background_height": 0.14,
            "background_horizontal_offset": 0.0,
            "background_round": self.background.round if self.background else 0.0,
            "background_style": 1 if self.background else 0,
            "background_vertical_offset": 0.0,
            "background_width": 0.14,
            "bold_width": 1.0 if style.bold else 0.0,
            "border_alpha": self.border.alpha if self.border else 0.0,
            "border_color": list(self.border.color) if self.border else [0.0, 0.0, 0.0],
            "border_width": self.border.width if self.border else 0.0,
            "font_category_id": "",
            "font_category_name": "",
            "font_id": "",
            "font_name": "",
            "font_path": "",
            "font_resource_id": "",
            "font_source_platform": 0,
            "font_team_id": "",
            "font_title": "",
            "font_url": "",
            "fonts": [],
            "has_shadow": self.shadow is not None,
            "inner_padding": -1,
            "is_rich_text": False,
            "italic_degree": 12 if style.italic else 0,
            "ktv_color": "",
            "letter_spacing": style.letter_spacing / 100.0,
            "line_spacing": style.line_spacing / 100.0,
            "shadow_alpha": self.shadow.alpha if self.shadow else 0.0,
            "shadow_angle": self.shadow.angle if self.shadow else 0.0,
            "shadow_color": list(self.shadow.color) if self.shadow else [0.0, 0.0, 0.0],
            "shadow_distance": self.shadow.distance if self.shadow else 0.0,
            "shadow_point": {"x": 1.0, "y": -1.0},
            "shadow_smoothing": self.shadow.blur if self.shadow else 0.0,
            "underline": style.underline,
            "underline_offset": 0.22,
            "underline_width": 0.05,
            "use_effect_default_color": True,
            "v_alignment": 1 if style.vertical else 0,
        }

        return {
            "id": self.text_id,
            "type": "text",
            "add_type": 0,
            "alignment": style.align,
            "category_id": "",
            "category_name": "",
            "check_flag": 7,
            "content": self.content,
            "font_size": style.size,
            "fonts": [],
            "global_alpha": style.alpha,
            "has_ori_shadow_effect": False,
            "is_auto_wrapping": style.auto_wrapping,
            "is_preset_material": False,
            "is_rich_text": False,
            "layer_weight": 1,
            "max_line_width": style.max_line_width,
            "preset_category": "",
            "preset_category_id": "",
            "preset_has_set_alignment": False,
            "preset_id": "",
            "preset_index": 0,
            "preset_name": "",
            "recognize_task_id": "",
            "recognize_type": 0,
            "style_name": "",
            "styles": [{"fill": {"alpha": style.alpha, "content": {"render_type": "solid", "solid": {"color": list(style.color)}}},"font": {"id": "", "path": ""},"range": [0, len(self.content)],"size": style.size,**styles_content}],
            "subtitle_keywords": None,
            "text_alpha": style.alpha,
            "text_color": f"#{int(style.color[0]*255):02x}{int(style.color[1]*255):02x}{int(style.color[2]*255):02x}",
            "text_curve": None,
            "text_preset_resource_id": "",
            "text_size": style.size,
            "text_to_audio_ids": [],
            "tts_auto_update": False,
            "typesetting": 1 if style.vertical else 0,
        }

    def export_json(self) -> Dict[str, Any]:
        json_dict = super().export_json()
        json_dict.update({
            "hdr_settings": None
        })
        return json_dict


# 為了兼容性保留的空類
class TextBubble:
    """文本氣泡（精簡版不支持）"""
    global_id: str

    def __init__(self):
        self.global_id = uuid.uuid4().hex

    def export_json(self) -> Dict[str, Any]:
        return {}
