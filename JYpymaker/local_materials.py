"""本地素材類"""

import os
import uuid
import pymediainfo

from typing import Optional, Literal
from typing import Dict, Any

class CropSettings:
    """素材的裁剪設置, 各屬性均在0-1之間, 注意素材的座標原點在左上角"""

    upper_left_x: float
    upper_left_y: float
    upper_right_x: float
    upper_right_y: float
    lower_left_x: float
    lower_left_y: float
    lower_right_x: float
    lower_right_y: float

    def __init__(self, *, upper_left_x: float = 0.0, upper_left_y: float = 0.0,
                 upper_right_x: float = 1.0, upper_right_y: float = 0.0,
                 lower_left_x: float = 0.0, lower_left_y: float = 1.0,
                 lower_right_x: float = 1.0, lower_right_y: float = 1.0):
        """初始化裁剪設置, 默認參數表示不裁剪"""
        self.upper_left_x = upper_left_x
        self.upper_left_y = upper_left_y
        self.upper_right_x = upper_right_x
        self.upper_right_y = upper_right_y
        self.lower_left_x = lower_left_x
        self.lower_left_y = lower_left_y
        self.lower_right_x = lower_right_x
        self.lower_right_y = lower_right_y

    def export_json(self) -> Dict[str, Any]:
        return {
            "upper_left_x": self.upper_left_x,
            "upper_left_y": self.upper_left_y,
            "upper_right_x": self.upper_right_x,
            "upper_right_y": self.upper_right_y,
            "lower_left_x": self.lower_left_x,
            "lower_left_y": self.lower_left_y,
            "lower_right_x": self.lower_right_x,
            "lower_right_y": self.lower_right_y
        }

class VideoMaterial:
    """本地視頻素材（視頻或圖片）, 一份素材可以在多個片段中使用"""

    material_id: str
    """素材全局id, 自動生成"""
    local_material_id: str
    """素材本地id, 意義暫不明確"""
    material_name: str
    """素材名稱"""
    path: str
    """素材文件路徑"""
    duration: int
    """素材時長, 單位為微秒"""
    height: int
    """素材高度"""
    width: int
    """素材寬度"""
    crop_settings: CropSettings
    """素材裁剪設置"""
    material_type: Literal["video", "photo"]
    """素材類型: 視頻或圖片"""

    def __init__(self, path: str, material_name: Optional[str] = None, crop_settings: CropSettings = CropSettings()):
        """從指定位置加載視頻（或圖片）素材

        Args:
            path (`str`): 素材文件路徑, 支持mp4, mov, avi等常見視頻文件及jpg, jpeg, png等圖片文件.
            material_name (`str`, optional): 素材名稱, 如果不指定, 默認使用文件名作為素材名稱.
            crop_settings (`CropSettings`, optional): 素材裁剪設置, 默認不裁剪.

        Raises:
            `FileNotFoundError`: 素材文件不存在.
            `ValueError`: 不支持的素材文件類型.
        """
        path = os.path.abspath(path)
        postfix = os.path.splitext(path)[1]
        if not os.path.exists(path):
            raise FileNotFoundError(f"找不到 {path}")

        self.material_name = material_name if material_name else os.path.basename(path)
        self.material_id = uuid.uuid4().hex
        self.path = path
        self.crop_settings = crop_settings
        self.local_material_id = ""

        if not pymediainfo.MediaInfo.can_parse():
            raise ValueError(f"不支持的視頻素材類型 '{postfix}'")

        info: pymediainfo.MediaInfo = \
            pymediainfo.MediaInfo.parse(path, mediainfo_options={"File_TestContinuousFileNames": "0"})  # type: ignore
        # 有視頻軌道的視為視頻素材
        if len(info.video_tracks):
            self.material_type = "video"
            self.duration = int(info.video_tracks[0].duration * 1e3)  # type: ignore
            self.width, self.height = info.video_tracks[0].width, info.video_tracks[0].height  # type: ignore
        # gif文件使用imageio庫獲取長度
        elif postfix.lower() == ".gif":
            import imageio
            gif = imageio.get_reader(path)

            self.material_type = "video"
            self.duration = int(round(gif.get_meta_data()['duration'] * gif.get_length() * 1e3))
            self.width, self.height = info.image_tracks[0].width, info.image_tracks[0].height  # type: ignore
            gif.close()
        elif len(info.image_tracks):
            self.material_type = "photo"
            self.duration = 10800000000  # 相當於3h
            self.width, self.height = info.image_tracks[0].width, info.image_tracks[0].height  # type: ignore
        else:
            raise ValueError(f"輸入的素材文件 {path} 沒有視頻軌道或圖片軌道")

    def export_json(self) -> Dict[str, Any]:
        video_material_json = {
            "audio_fade": None,
            "category_id": "",
            "category_name": "local",
            "check_flag": 63487,
            "crop": self.crop_settings.export_json(),
            "crop_ratio": "free",
            "crop_scale": 1.0,
            "duration": self.duration,
            "height": self.height,
            "id": self.material_id,
            "local_material_id": self.local_material_id,
            "material_id": self.material_id,
            "material_name": self.material_name,
            "media_path": "",
            "path": self.path,
            "type": self.material_type,
            "width": self.width
        }
        return video_material_json

class AudioMaterial:
    """本地音頻素材"""

    material_id: str
    """素材全局id, 自動生成"""
    material_name: str
    """素材名稱"""
    path: str
    """素材文件路徑"""

    duration: int
    """素材時長, 單位為微秒"""

    def __init__(self, path: str, material_name: Optional[str] = None):
        """從指定位置加載音頻素材, 注意視頻文件不應該作為音頻素材使用

        Args:
            path (`str`): 素材文件路徑, 支持mp3, wav等常見音頻文件.
            material_name (`str`, optional): 素材名稱, 如果不指定, 默認使用文件名作為素材名稱.

        Raises:
            `FileNotFoundError`: 素材文件不存在.
            `ValueError`: 不支持的素材文件類型.
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"找不到 {path}")

        self.material_name = material_name if material_name else os.path.basename(path)
        self.material_id = uuid.uuid4().hex
        self.path = path

        if not pymediainfo.MediaInfo.can_parse():
            raise ValueError("不支持的音頻素材類型 %s" % os.path.splitext(path)[1])
        info: pymediainfo.MediaInfo = pymediainfo.MediaInfo.parse(path)  # type: ignore
        if len(info.video_tracks):
            raise ValueError("音頻素材不應包含視頻軌道")
        if not len(info.audio_tracks):
            raise ValueError(f"給定的素材文件 {path} 沒有音頻軌道")
        self.duration = int(info.audio_tracks[0].duration * 1e3)  # type: ignore

    def export_json(self) -> Dict[str, Any]:
        return {
            "app_id": 0,
            "category_id": "",
            "category_name": "local",
            "check_flag": 3,
            "copyright_limit_type": "none",
            "duration": self.duration,
            "effect_id": "",
            "formula_id": "",
            "id": self.material_id,
            "local_material_id": self.material_id,
            "music_id": self.material_id,
            "name": self.material_name,
            "path": self.path,
            "source_platform": 0,
            "type": "extract_music",
            "wave_points": []
        }
