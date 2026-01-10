"""草稿文件夾管理"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from . import assets


class DraftFolder:
    """草稿文件夾管理類"""

    draft_path: Path
    """草稿文件夾路徑"""
    draft_content_path: Path
    """draft_content.json 文件路徑"""
    draft_meta_path: Path
    """draft_meta_info.json 文件路徑"""

    def __init__(self, draft_path: str):
        """初始化草稿文件夾

        Args:
            draft_path (`str`): 草稿文件夾路徑
        """
        self.draft_path = Path(draft_path)
        self.draft_content_path = self.draft_path / "draft_content.json"
        self.draft_meta_path = self.draft_path / "draft_meta_info.json"

    @classmethod
    def create(cls, draft_path: str, draft_name: Optional[str] = None) -> "DraftFolder":
        """創建一個新的草稿文件夾

        Args:
            draft_path (`str`): 草稿文件夾路徑
            draft_name (`str`, optional): 草稿名稱, 如果不指定, 默認使用文件夾名

        Returns:
            `DraftFolder`: 草稿文件夾實例
        """
        draft_folder = cls(draft_path)
        draft_folder.draft_path.mkdir(parents=True, exist_ok=True)

        # 複製模板文件
        template_content = assets.get_asset_path('DRAFT_CONTENT_TEMPLATE')
        template_meta = assets.get_asset_path('DRAFT_META_TEMPLATE')

        shutil.copy(template_content, draft_folder.draft_content_path)
        shutil.copy(template_meta, draft_folder.draft_meta_path)

        # 設置草稿名稱
        if draft_name is None:
            draft_name = draft_folder.draft_path.name

        with open(draft_folder.draft_meta_path, 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        meta_data['draft_name'] = draft_name
        with open(draft_folder.draft_meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)

        return draft_folder

    def load_content(self) -> Dict[str, Any]:
        """加載草稿內容

        Returns:
            `Dict[str, Any]`: 草稿內容
        """
        with open(self.draft_content_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_content(self, content: Dict[str, Any]) -> None:
        """保存草稿內容

        Args:
            content (`Dict[str, Any]`): 草稿內容
        """
        with open(self.draft_content_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False)

    def exists(self) -> bool:
        """檢查草稿文件夾是否存在"""
        return self.draft_path.exists() and self.draft_content_path.exists()
