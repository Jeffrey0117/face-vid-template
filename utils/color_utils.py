"""顏色格式轉換工具"""

from typing import Tuple, List


def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """
    轉換 HEX 顏色為 RGB (0.0-1.0)

    Args:
        hex_color: HEX 顏色字串，如 "#FFFFFF" 或 "FFFFFF"

    Returns:
        RGB 元組，值範圍 0.0-1.0
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)


def rgb_to_hex(rgb: List[float]) -> str:
    """
    轉換 RGB (0.0-1.0) 為 HEX 顏色

    Args:
        rgb: RGB 列表，值範圍 0.0-1.0

    Returns:
        HEX 顏色字串，如 "#FFFFFF"
    """
    r = int(rgb[0] * 255)
    g = int(rgb[1] * 255)
    b = int(rgb[2] * 255)
    return f"#{r:02X}{g:02X}{b:02X}"
