"""與模板模式相關的類及函數等"""

from enum import Enum
from copy import deepcopy

from . import util
from . import exceptions
from .time_util import Timerange
from .segment import BaseSegment
from .track import BaseTrack, TrackType
from .local_materials import VideoMaterial, AudioMaterial

from typing import List, Dict, Any

class ShrinkMode(Enum):
    """處理替換素材時素材變短情況的方法"""

    cut_head = "cut_head"
    """裁剪頭部, 即後移片段起始點"""
    cut_tail = "cut_tail"
    """裁剪尾部, 即前移片段終止點"""

    cut_tail_align = "cut_tail_align"
    """裁剪尾部並消除間隙, 即前移片段終止點, 後續片段也依次前移"""

    shrink = "shrink"
    """保持中間點不變, 兩端點向中間靠攏"""

class ExtendMode(Enum):
    """處理替換素材時素材變長情況的方法"""

    cut_material_tail = "cut_material_tail"
    """裁剪素材尾部(覆蓋`source_timerange`參數), 使得片段維持原長不變, 此方法總是成功"""

    extend_head = "extend_head"
    """延伸頭部, 即嘗試前移片段起始點, 與前續片段重合時失敗"""
    extend_tail = "extend_tail"
    """延伸尾部, 即嘗試後移片段終止點, 與後續片段重合時失敗"""

    push_tail = "push_tail"
    """延伸尾部, 若有必要則依次後移後續片段, 此方法總是成功"""

class ImportedSegment(BaseSegment):
    """導入的片段"""

    raw_data: Dict[str, Any]
    """原始json數據"""

    __DATA_ATTRS = ["material_id", "target_timerange"]
    def __init__(self, json_data: Dict[str, Any]):
        self.raw_data = deepcopy(json_data)

        util.assign_attr_with_json(self, self.__DATA_ATTRS, json_data)

    def export_json(self) -> Dict[str, Any]:
        json_data = deepcopy(self.raw_data)
        json_data.update(util.export_attr_to_json(self, self.__DATA_ATTRS))
        return json_data

class ImportedMediaSegment(ImportedSegment):
    """導入的視頻/音頻片段"""

    source_timerange: Timerange
    """片段取用的素材時間範圍"""

    __DATA_ATTRS = ["source_timerange"]
    def __init__(self, json_data: Dict[str, Any]):
        super().__init__(json_data)

        util.assign_attr_with_json(self, self.__DATA_ATTRS, json_data)

    def export_json(self) -> Dict[str, Any]:
        json_data = super().export_json()
        json_data.update(util.export_attr_to_json(self, self.__DATA_ATTRS))
        return json_data


class ImportedTrack(BaseTrack):
    """模板模式下導入的軌道"""

    raw_data: Dict[str, Any]
    """原始軌道數據"""

    def __init__(self, json_data: Dict[str, Any]):
        self.track_type = TrackType.from_name(json_data["type"])
        self.name = json_data["name"]
        self.track_id = json_data["id"]
        self.render_index = max([int(seg["render_index"]) for seg in json_data["segments"]], default=0)

        self.raw_data = deepcopy(json_data)

    def export_json(self) -> Dict[str, Any]:
        ret = deepcopy(self.raw_data)
        ret.update({
            "name": self.name,
            "id": self.track_id
        })
        return ret

class EditableTrack(ImportedTrack):
    """模板模式下導入且可修改的軌道(音視頻及文本軌道)"""

    segments: List[ImportedSegment]
    """該軌道包含的片段列表"""

    def __len__(self):
        return len(self.segments)

    @property
    def start_time(self) -> int:
        """軌道起始時間, 微秒"""
        if len(self.segments) == 0:
            return 0
        return self.segments[0].target_timerange.start

    @property
    def end_time(self) -> int:
        """軌道結束時間, 微秒"""
        if len(self.segments) == 0:
            return 0
        return self.segments[-1].target_timerange.end

    def export_json(self) -> Dict[str, Any]:
        ret = super().export_json()
        # 為每個片段寫入render_index
        segment_exports = [seg.export_json() for seg in self.segments]
        for seg in segment_exports:
            seg["render_index"] = self.render_index
        ret["segments"] = segment_exports
        return ret

class ImportedTextTrack(EditableTrack):
    """模板模式下導入的文本軌道"""

    def __init__(self, json_data: Dict[str, Any]):
        super().__init__(json_data)
        self.segments = [ImportedSegment(seg) for seg in json_data["segments"]]

class ImportedMediaTrack(EditableTrack):
    """模板模式下導入的音頻/視頻軌道"""

    segments: List[ImportedMediaSegment]
    """該軌道包含的片段列表"""

    def __init__(self, json_data: Dict[str, Any]):
        super().__init__(json_data)
        self.segments = [ImportedMediaSegment(seg) for seg in json_data["segments"]]

    def check_material_type(self, material: object) -> bool:
        """檢查素材類型是否與軌道類型匹配"""
        if self.track_type == TrackType.video and isinstance(material, VideoMaterial):
            return True
        if self.track_type == TrackType.audio and isinstance(material, AudioMaterial):
            return True
        return False

    def process_timerange(self, seg_index: int, src_timerange: Timerange,
                          shrink: ShrinkMode, extend: List[ExtendMode]) -> None:
        """處理素材替換的時間範圍變更"""
        seg = self.segments[seg_index]
        new_duration = src_timerange.duration

        # 時長變短
        delta_duration = abs(new_duration - seg.duration)
        if new_duration < seg.duration:
            if shrink == ShrinkMode.cut_head:
                seg.start += delta_duration
            elif shrink == ShrinkMode.cut_tail:
                seg.duration -= delta_duration
            elif shrink == ShrinkMode.cut_tail_align:
                seg.duration -= delta_duration
                for i in range(seg_index+1, len(self.segments)):  # 後續片段也依次前移相應值（保持間隙）
                    self.segments[i].start -= delta_duration
            elif shrink == ShrinkMode.shrink:
                seg.duration -= delta_duration
                seg.start += delta_duration // 2
            else:
                raise ValueError(f"Unsupported shrink mode: {shrink}")
        # 時長變長
        elif new_duration > seg.duration:
            success_flag = False
            prev_seg_end = int(0) if seg_index == 0 else self.segments[seg_index-1].target_timerange.end
            next_seg_start = int(1e15) if seg_index == len(self.segments)-1 else self.segments[seg_index+1].start
            for mode in extend:
                if mode == ExtendMode.extend_head:
                    if seg.start - delta_duration >= prev_seg_end:
                        seg.start -= delta_duration
                        success_flag = True
                elif mode == ExtendMode.extend_tail:
                    if seg.target_timerange.end + delta_duration <= next_seg_start:
                        seg.duration += delta_duration
                        success_flag = True
                elif mode == ExtendMode.push_tail:
                    shift_duration = max(0, seg.target_timerange.end + delta_duration - next_seg_start)
                    seg.duration += delta_duration
                    if shift_duration > 0:  # 有必要時後移後續片段
                        for i in range(seg_index+1, len(self.segments)):
                            self.segments[i].start += shift_duration
                    success_flag = True
                elif mode == ExtendMode.cut_material_tail:
                    src_timerange.duration = seg.duration
                    success_flag = True
                else:
                    raise ValueError(f"Unsupported extend mode: {mode}")

                if success_flag:
                    break
            if not success_flag:
                raise exceptions.ExtensionFailed(f"未能將片段延長至 {new_duration}μs, 嘗試過以下方法: {extend}")

        # 寫入素材時間範圍
        seg.source_timerange = src_timerange

def import_track(json_data: Dict[str, Any]) -> ImportedTrack:
    """導入軌道"""
    track_type = TrackType.from_name(json_data["type"])
    if not track_type.value.allow_modify:
        return ImportedTrack(json_data)
    if track_type == TrackType.text:
        return ImportedTextTrack(json_data)
    return ImportedMediaTrack(json_data)
