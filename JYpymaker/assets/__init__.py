"""
pyjymaker 的資源管理模組，提供集中管理資源文件的方式，避免硬編碼路徑
"""

from pathlib import Path

# 獲取當前模組所在目錄
ASSETS_DIR = Path(__file__).parent

# 資源文件映射表 - 集中管理所有asset文件名
ASSET_FILES = {
    # 模板文件
    'DRAFT_CONTENT_TEMPLATE': 'draft_content_template.json',
    'DRAFT_META_TEMPLATE': 'draft_meta_info.json',
}

def get_asset_path(asset_name: str) -> Path:
    """
    獲取指定資源文件的完整路徑

    Args:
        asset_name: 資源名稱（ASSET_FILES中的key）

    Returns:
        Path: 資源文件的完整路徑

    Raises:
        KeyError: 資源名稱不存在
        FileNotFoundError: 文件不存在
    """
    if asset_name not in ASSET_FILES:
        raise KeyError(f"Asset '{asset_name}' not found. Available assets: {list(ASSET_FILES.keys())}")

    file_path = ASSETS_DIR / ASSET_FILES[asset_name]

    if not file_path.exists():
        raise FileNotFoundError(f"Asset file '{file_path}' does not exist")

    return file_path

# 導出主要接口
__all__ = [
    'get_asset_path',
    'ASSET_FILES'
]
