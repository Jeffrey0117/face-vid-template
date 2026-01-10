"""自定義異常類"""

class TrackNotFound(NameError):
    """未找到滿足條件的軌道"""
class AmbiguousTrack(ValueError):
    """找到多個滿足條件的軌道"""
class SegmentOverlap(ValueError):
    """新片段與已有的軌道片段重疊"""

class MaterialNotFound(NameError):
    """未找到滿足條件的素材"""
class AmbiguousMaterial(ValueError):
    """找到多個滿足條件的素材"""

class ExtensionFailed(ValueError):
    """替換素材時延伸片段失敗"""

class DraftNotFound(NameError):
    """未找到草稿"""
class AutomationError(Exception):
    """自動化操作失敗"""
class ExportTimeout(Exception):
    """導出超時"""
