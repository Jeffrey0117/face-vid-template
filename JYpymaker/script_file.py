"""草稿文件核心類（精簡版 - 移除特效相關功能）"""

import os
import json
import math
from copy import deepcopy

from typing import Optional, Literal, Union, overload
from typing import Type, Dict, List, Any

from . import util
from . import assets
from . import exceptions
from .template_mode import ImportedTrack, EditableTrack, ImportedMediaTrack, ImportedTextTrack, ShrinkMode, ExtendMode, import_track
from .time_util import Timerange, tim, srt_tstamp
from .local_materials import VideoMaterial, AudioMaterial
from .segment import BaseSegment, Speed, ClipSettings, AudioFade
from .audio_segment import AudioSegment
from .video_segment import VideoSegment, StickerSegment, Transition, Filter, BackgroundFilling
from .effect_segment import EffectSegment, FilterSegment
from .text_segment import TextSegment, TextStyle, TextBubble
from .track import TrackType, BaseTrack, Track
from .animation import SegmentAnimations


class ScriptMaterial:
    """草稿文件中的素材信息部分"""

    audios: List[AudioMaterial]
    """音頻素材列表"""
    videos: List[VideoMaterial]
    """視頻素材列表"""
    stickers: List[Dict[str, Any]]
    """貼紙素材列表"""
    texts: List[Dict[str, Any]]
    """文本素材列表"""

    audio_fades: List[AudioFade]
    """音頻淡入淡出效果列表"""
    animations: List[SegmentAnimations]
    """動畫素材列表"""

    speeds: List[Speed]
    """變速列表"""
    masks: List[Dict[str, Any]]
    """蒙版列表"""
    transitions: List[Transition]
    """轉場效果列表"""
    filters: List[Union[Filter, TextBubble]]
    """濾鏡/文本花字/文本氣泡列表"""
    canvases: List[BackgroundFilling]
    """背景填充列表"""

    def __init__(self):
        self.audios = []
        self.videos = []
        self.stickers = []
        self.texts = []

        self.audio_fades = []
        self.animations = []

        self.speeds = []
        self.masks = []
        self.transitions = []
        self.filters = []
        self.canvases = []

    def __contains__(self, item) -> bool:
        if isinstance(item, VideoMaterial):
            return item.material_id in [video.material_id for video in self.videos]
        elif isinstance(item, AudioMaterial):
            return item.material_id in [audio.material_id for audio in self.audios]
        elif isinstance(item, AudioFade):
            return item.fade_id in [fade.fade_id for fade in self.audio_fades]
        elif isinstance(item, SegmentAnimations):
            return item.animation_id in [ani.animation_id for ani in self.animations]
        elif isinstance(item, Transition):
            return item.global_id in [transition.global_id for transition in self.transitions]
        elif isinstance(item, Filter):
            return item.global_id in [filter_.global_id for filter_ in self.filters]
        else:
            raise TypeError("Invalid argument type '%s'" % type(item))

    def export_json(self) -> Dict[str, List[Any]]:
        return {
            "ai_translates": [],
            "audio_balances": [],
            "audio_effects": [],
            "audio_fades": [fade.export_json() for fade in self.audio_fades],
            "audio_track_indexes": [],
            "audios": [audio.export_json() for audio in self.audios],
            "beats": [],
            "canvases": [canvas.export_json() for canvas in self.canvases],
            "chromas": [],
            "color_curves": [],
            "digital_humans": [],
            "drafts": [],
            "effects": [_filter.export_json() for _filter in self.filters],
            "flowers": [],
            "green_screens": [],
            "handwrites": [],
            "hsl": [],
            "images": [],
            "log_color_wheels": [],
            "loudnesses": [],
            "manual_deformations": [],
            "masks": self.masks,
            "material_animations": [ani.export_json() for ani in self.animations],
            "material_colors": [],
            "multi_language_refs": [],
            "placeholders": [],
            "plugin_effects": [],
            "primary_color_wheels": [],
            "realtime_denoises": [],
            "shapes": [],
            "smart_crops": [],
            "smart_relights": [],
            "sound_channel_mappings": [],
            "speeds": [spd.export_json() for spd in self.speeds],
            "stickers": self.stickers,
            "tail_leaders": [],
            "text_templates": [],
            "texts": self.texts,
            "time_marks": [],
            "transitions": [transition.export_json() for transition in self.transitions],
            "video_effects": [],
            "video_trackings": [],
            "videos": [video.export_json() for video in self.videos],
            "vocal_beautifys": [],
            "vocal_separations": []
        }

class ScriptFile:
    """剪映草稿文件（精簡版）"""

    save_path: Optional[str]
    """草稿文件保存路徑, 僅在模板模式下有效"""
    content: Dict[str, Any]
    """草稿文件內容"""

    width: int
    """視頻的寬度, 單位為像素"""
    height: int
    """視頻的高度, 單位為像素"""
    fps: int
    """視頻的幀率"""
    duration: int
    """視頻的總時長, 單位為微秒"""

    materials: ScriptMaterial
    """草稿文件中的素材信息部分"""
    tracks: Dict[str, Track]
    """軌道信息"""

    imported_materials: Dict[str, List[Dict[str, Any]]]
    """導入的素材信息"""
    imported_tracks: List[ImportedTrack]
    """導入的軌道信息"""

    def __init__(self, width: int, height: int, fps: int = 30):
        """創建剪映草稿

        Args:
            width (int): 視頻寬度, 單位為像素
            height (int): 視頻高度, 單位為像素
            fps (int, optional): 視頻幀率. 默認為30.
        """
        self.save_path = None

        self.width = width
        self.height = height
        self.fps = fps
        self.duration = 0

        self.materials = ScriptMaterial()
        self.tracks = {}

        self.imported_materials = {}
        self.imported_tracks = []

        with open(assets.get_asset_path('DRAFT_CONTENT_TEMPLATE'), "r", encoding="utf-8") as f:
            self.content = json.load(f)

    @staticmethod
    def load_template(json_path: str) -> "ScriptFile":
        """從JSON文件加載草稿模板

        Args:
            json_path (str): JSON文件路徑

        Raises:
            `FileNotFoundError`: JSON文件不存在
        """
        obj = ScriptFile(**util.provide_ctor_defaults(ScriptFile))
        obj.save_path = json_path
        if not os.path.exists(json_path):
            raise FileNotFoundError("JSON文件 '%s' 不存在" % json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            obj.content = json.load(f)

        util.assign_attr_with_json(obj, ["fps", "duration"], obj.content)
        util.assign_attr_with_json(obj, ["width", "height"], obj.content["canvas_config"])

        obj.imported_materials = deepcopy(obj.content["materials"])
        obj.imported_tracks = [import_track(track_data) for track_data in obj.content["tracks"]]

        return obj

    def add_material(self, material: Union[VideoMaterial, AudioMaterial]) -> "ScriptFile":
        """向草稿文件中添加一個素材"""
        if material in self.materials:  # 素材已存在
            return self
        if isinstance(material, VideoMaterial):
            self.materials.videos.append(material)
        elif isinstance(material, AudioMaterial):
            self.materials.audios.append(material)
        else:
            raise TypeError("錯誤的素材類型: '%s'" % type(material))
        return self

    def add_track(self, track_type: TrackType, track_name: Optional[str] = None, *,
                  mute: bool = False,
                  relative_index: int = 0, absolute_index: Optional[int] = None) -> "ScriptFile":
        """向草稿文件中添加一個指定類型、指定名稱的軌道

        Args:
            track_type (TrackType): 軌道類型
            track_name (str, optional): 軌道名稱.
            mute (bool, optional): 軌道是否靜音. 默認不靜音.
            relative_index (int, optional): 相對(同類型軌道的)圖層位置. 默認為0.
            absolute_index (int, optional): 絕對圖層位置.
        """

        if track_name is None:
            if track_type in [track.track_type for track in self.tracks.values()]:
                raise NameError("'%s' 類型的軌道已存在, 請為新軌道指定名稱以避免混淆" % track_type)
            track_name = track_type.name
        if track_name in [track.name for track in self.tracks.values()]:
            raise NameError("名為 '%s' 的軌道已存在" % track_name)

        render_index = track_type.value.render_index + relative_index
        if absolute_index is not None:
            render_index = absolute_index

        self.tracks[track_name] = Track(track_type, track_name, render_index, mute)
        return self

    def _get_track(self, segment_type: Type[BaseSegment], track_name: Optional[str]) -> Track:
        # 指定軌道名稱
        if track_name is not None:
            if track_name not in self.tracks:
                raise NameError("不存在名為 '%s' 的軌道" % track_name)
            return self.tracks[track_name]
        # 尋找唯一的同類型的軌道
        count = sum([1 for track in self.tracks.values() if track.accept_segment_type == segment_type])
        if count == 0: raise NameError("不存在接受 '%s' 的軌道" % segment_type)
        if count > 1: raise NameError("存在多個接受 '%s' 的軌道, 請指定軌道名稱" % segment_type)

        return next(track for track in self.tracks.values() if track.accept_segment_type == segment_type)

    def add_segment(self, segment: Union[VideoSegment, StickerSegment, AudioSegment, TextSegment],
                    track_name: Optional[str] = None) -> "ScriptFile":
        """向指定軌道中添加一個片段

        Args:
            segment: 要添加的片段
            track_name (`str`, optional): 添加到的軌道名稱.
        """
        target = self._get_track(type(segment), track_name)

        # 加入軌道並更新時長
        target.add_segment(segment)
        self.duration = max(self.duration, segment.end)

        # 自動添加相關素材
        if isinstance(segment, VideoSegment):
            # 淡入淡出
            if (segment.fade is not None) and (segment.fade not in self.materials):
                self.materials.audio_fades.append(segment.fade)
            self.materials.speeds.append(segment.speed)
        elif isinstance(segment, AudioSegment):
            # 淡入淡出
            if (segment.fade is not None) and (segment.fade not in self.materials):
                self.materials.audio_fades.append(segment.fade)
            self.materials.speeds.append(segment.speed)
        elif isinstance(segment, TextSegment):
            # 字體樣式
            self.materials.texts.append(segment._generate_text_material())

        # 添加片段素材
        if isinstance(segment, (VideoSegment, AudioSegment)):
            self.add_material(segment.material_instance)

        return self

    def import_srt(self, srt_path: str, track_name: str, *,
                   time_offset: Union[str, float] = 0.0,
                   text_style: TextStyle = TextStyle(size=5, align=1, auto_wrapping=True),
                   clip_settings: Optional[ClipSettings] = ClipSettings(transform_y=-0.8)) -> "ScriptFile":
        """從SRT文件中導入字幕

        Args:
            srt_path (`str`): SRT文件路徑
            track_name (`str`): 導入到的文本軌道名稱, 若不存在則自動創建
            time_offset: 字幕整體時間偏移, 單位為微秒, 默認為0.
            text_style (`TextStyle`, optional): 字幕樣式.
            clip_settings (`ClipSettings`, optional): 圖像調節設置.
        """
        time_offset = tim(time_offset)
        if track_name not in self.tracks:
            self.add_track(TrackType.text, track_name, relative_index=999)  # 在所有文本軌道的最上層

        with open(srt_path, "r", encoding="utf-8-sig") as srt_file:
            lines = srt_file.readlines()

        def __add_text_segment(text: str, t_range: Timerange) -> None:
            seg = TextSegment(text, t_range, text_style=text_style, clip_settings=clip_settings)
            self.add_segment(seg, track_name)

        index = 0
        text: str = ""
        text_trange: Timerange
        read_state: Literal["index", "timestamp", "content"] = "index"
        while index < len(lines):
            line = lines[index].strip()
            if read_state == "index":
                if len(line) == 0:
                    index += 1
                    continue
                if not line.isdigit():
                    raise ValueError("Expected a number at line %d, got '%s'" % (index+1, line))
                index += 1
                read_state = "timestamp"
            elif read_state == "timestamp":
                # 讀取時間戳
                start_str, end_str = line.split(" --> ")
                start, end = srt_tstamp(start_str), srt_tstamp(end_str)
                text_trange = Timerange(start + time_offset, end - start)

                index += 1
                read_state = "content"
            elif read_state == "content":
                # 內容結束, 生成片段
                if len(line) == 0:
                    __add_text_segment(text.strip(), text_trange)

                    text = ""
                    read_state = "index"
                else:
                    text += line + "\n"
                index += 1

        # 添加最後一個片段
        if len(text) > 0:
            __add_text_segment(text.strip(), text_trange)

        return self

    def get_imported_track(self, track_type: Literal[TrackType.video, TrackType.audio, TrackType.text],
                           name: Optional[str] = None, index: Optional[int] = None) -> EditableTrack:
        """獲取指定類型的導入軌道

        Args:
            track_type: 軌道類型, 目前只支持音視頻和文本軌道
            name (`str`, optional): 軌道名稱.
            index (`int`, optional): 軌道在同類型的導入軌道中的下標.
        """
        tracks_of_same_type: List[EditableTrack] = []
        for track in self.imported_tracks:
            if track.track_type == track_type:
                assert isinstance(track, EditableTrack)
                tracks_of_same_type.append(track)

        ret: List[EditableTrack] = []
        for ind, track in enumerate(tracks_of_same_type):
            if (name is not None) and (track.name != name): continue
            if (index is not None) and (ind != index): continue
            ret.append(track)

        if len(ret) == 0:
            raise exceptions.TrackNotFound(
                "沒有找到滿足條件的軌道: track_type=%s, name=%s, index=%s" % (track_type, name, index))
        if len(ret) > 1:
            raise exceptions.AmbiguousTrack(
                "找到多個滿足條件的軌道: track_type=%s, name=%s, index=%s" % (track_type, name, index))

        return ret[0]

    def replace_material_by_seg(self, track: EditableTrack, segment_index: int, material: Union[VideoMaterial, AudioMaterial],
                                source_timerange: Optional[Timerange] = None, *,
                                handle_shrink: ShrinkMode = ShrinkMode.cut_tail,
                                handle_extend: Union[ExtendMode, List[ExtendMode]] = ExtendMode.cut_material_tail) -> "ScriptFile":
        """替換指定音視頻軌道上指定片段的素材

        Args:
            track (`EditableTrack`): 要替換素材的軌道
            segment_index (`int`): 要替換素材的片段下標
            material: 新素材
            source_timerange (`Timerange`, optional): 從原素材中截取的時間範圍
            handle_shrink (`ShrinkMode`, optional): 新素材比原素材短時的處理方式
            handle_extend: 新素材比原素材長時的處理方式
        """
        if not isinstance(track, ImportedMediaTrack):
            raise TypeError("指定的軌道(類型為 %s)不支持素材替換" % track.track_type)
        if not 0 <= segment_index < len(track):
            raise IndexError("片段下標 %d 超出 [0, %d) 的範圍" % (segment_index, len(track)))
        if not track.check_material_type(material):
            raise TypeError("指定的素材類型 %s 不匹配軌道類型 %s", (type(material), track.track_type))
        seg = track.segments[segment_index]

        if isinstance(handle_extend, ExtendMode):
            handle_extend = [handle_extend]
        if source_timerange is None:
            if isinstance(material, VideoMaterial) and (material.material_type == "photo"):
                source_timerange = Timerange(0, seg.duration)
            else:
                source_timerange = Timerange(0, material.duration)

        # 處理時間變化
        track.process_timerange(segment_index, source_timerange, handle_shrink, handle_extend)

        # 最後替換素材連結
        track.segments[segment_index].material_id = material.material_id
        self.add_material(material)

        return self

    def replace_text(self, track: EditableTrack, segment_index: int, text: Union[str, List[str]],
                     recalc_style: bool = True) -> "ScriptFile":
        """替換指定文本軌道上指定片段的文字內容

        Args:
            track (`EditableTrack`): 要替換文字的文本軌道
            segment_index (`int`): 要替換文字的片段下標
            text: 新的文字內容
            recalc_style (`bool`): 是否重新計算字體樣式分佈
        """
        if not isinstance(track, ImportedTextTrack):
            raise TypeError("指定的軌道(類型為 %s)不支持文本內容替換" % track.track_type)
        if not 0 <= segment_index < len(track):
            raise IndexError("片段下標 %d 超出 [0, %d) 的範圍" % (segment_index, len(track)))

        def __recalc_style_range(old_len: int, new_len: int, styles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """調整字體樣式分佈"""
            new_styles: List[Dict[str, Any]] = []
            for style in styles:
                start = math.ceil(style["range"][0] / old_len * new_len)
                end = math.ceil(style["range"][1] / old_len * new_len)
                style["range"] = [start, end]
                if start != end:
                    new_styles.append(style)
            return new_styles

        replaced: bool = False
        material_id: str = track.segments[segment_index].material_id
        # 嘗試在文本素材中替換
        for mat in self.imported_materials["texts"]:
            if mat["id"] != material_id:
                continue

            if isinstance(text, list):
                if len(text) != 1:
                    raise ValueError(f"正常文本片段只能有一個文字內容, 但替換內容是 {text}")
                text = text[0]

            content = json.loads(mat["content"])
            if recalc_style:
                content["styles"] = __recalc_style_range(len(content["text"]), len(text), content["styles"])
            content["text"] = text
            mat["content"] = json.dumps(content, ensure_ascii=False)
            replaced = True
            break
        if replaced:
            return self

        # 嘗試在文本模板中替換
        for template in self.imported_materials.get("text_templates", []):
            if template["id"] != material_id:
                continue

            resources = template["text_info_resources"]
            if isinstance(text, str):
                text = [text]
            if len(text) > len(resources):
                raise ValueError(f"文字模板'{template['name']}'只有{len(resources)}段文本, 但提供了{len(text)}段替換內容")

            for sub_material_id, new_text in zip(map(lambda x: x["text_material_id"], resources), text):
                for mat in self.imported_materials["texts"]:
                    if mat["id"] != sub_material_id:
                        continue

                    try:
                        content = json.loads(mat["content"])
                        if recalc_style:
                            content["styles"] = __recalc_style_range(len(content["text"]), len(new_text), content["styles"])
                        content["text"] = new_text
                        mat["content"] = json.dumps(content, ensure_ascii=False)
                    except json.JSONDecodeError:
                        mat["content"] = new_text
                    except TypeError:
                        mat["content"] = new_text

                    break
            replaced = True
            break

        assert replaced, f"未找到指定片段的素材 {material_id}"

        return self

    def dumps(self) -> str:
        """將草稿文件內容導出為JSON字串"""
        self.content["fps"] = self.fps
        self.content["duration"] = self.duration
        self.content["canvas_config"] = {"width": self.width, "height": self.height, "ratio": "original"}
        self.content["materials"] = self.materials.export_json()

        # 合併導入的素材
        for material_type, material_list in self.imported_materials.items():
            if material_type not in self.content["materials"]:
                self.content["materials"][material_type] = material_list
            else:
                self.content["materials"][material_type].extend(material_list)

        # 對軌道排序並導出
        track_list: List[BaseTrack] = list(self.imported_tracks + list(self.tracks.values()))
        track_list.sort(key=lambda track: track.render_index)
        self.content["tracks"] = [track.export_json() for track in track_list]

        return json.dumps(self.content, ensure_ascii=False, indent=4)

    def dump(self, file_path: str) -> None:
        """將草稿文件內容寫入文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.dumps())

    def save(self) -> None:
        """保存草稿文件至打開時的路徑"""
        if self.save_path is None:
            raise ValueError("沒有設置保存路徑, 可能不在模板模式下")
        self.dump(self.save_path)
