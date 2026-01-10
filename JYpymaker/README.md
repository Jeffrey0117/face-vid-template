# JYpymaker

精簡版剪映（CapCut）草稿生成庫，從 [pyJianYingDraft](https://github.com/GuoChen018/pyJianYingDraft) 精簡而來。

## 特色

- **輕量化**：從 ~19,773 行減少到 ~2,496 行（減少 87%）
- **專注核心功能**：僅保留素材管理、軌道操作、字幕導入等常用功能
- **簡繁轉換**：內建 OpenCC 支援，一鍵轉換字幕語言
- **草稿自動搜尋**：自動偵測剪映/CapCut 草稿目錄，支援名稱搜尋
- **移除依賴**：不需要龐大的特效/濾鏡元數據

## 安裝

```bash
# 複製到專案目錄
git clone https://github.com/Jeffrey0117/JYpymaker.git

# 安裝依賴
pip install pymediainfo

# 簡繁轉換功能（可選）
pip install opencc-python-reimplemented
```

> 注意：需要安裝 [MediaInfo](https://mediaarea.net/en/MediaInfo) 才能解析視頻資訊

## 快速開始

### 基本用法：從模板載入並替換素材

```python
from JYpymaker import ScriptFile, VideoMaterial, TrackType
from JYpymaker.template_mode import ExtendMode
from JYpymaker.time_util import Timerange

# 載入模板草稿
script = ScriptFile.load_template("path/to/draft_content.json")

# 取得視頻軌道
video_track = script.get_imported_track(TrackType.video, index=0)

# 建立新素材
new_video = VideoMaterial("path/to/video.mp4")

# 替換素材（使用完整時長）
source_timerange = Timerange(0, new_video.duration)
script.replace_material_by_seg(
    video_track, 0, new_video,
    source_timerange=source_timerange,
    handle_extend=ExtendMode.push_tail
)

# 更新草稿時長
script.duration = new_video.duration

# 儲存
script.save()
```

### 導入 SRT 字幕

```python
from JYpymaker import ScriptFile, TextStyle, ClipSettings

script = ScriptFile.load_template("path/to/draft_content.json")

# 設定字幕樣式
text_style = TextStyle(
    size=8.0,                    # 字體大小
    color=(1.0, 1.0, 1.0),       # 白色 (RGB 0-1)
    align=1,                     # 置中對齊
    auto_wrapping=True           # 自動換行
)

# 設定字幕位置
clip_settings = ClipSettings(
    transform_y=-0.8             # 畫面下方 (範圍 -1 到 1)
)

# 導入字幕
script.import_srt(
    "path/to/subtitle.srt",
    "字幕軌",                    # 軌道名稱
    text_style=text_style,
    clip_settings=clip_settings
)

script.save()
```

### 簡繁轉換

```python
from JYpymaker import convert_text, convert_srt_file, convert_draft_file

# 轉換單一文字
result = convert_text("视频翻译软件", mode="s2twp")
# -> "影片翻譯軟體"

# 轉換 SRT 檔案
convert_srt_file("subtitle.srt", mode="s2tw")

# 轉換剪映草稿中的所有字幕
convert_draft_file("draft_content.json", mode="s2tw", verbose=True)
```

**轉換模式：**

| 模式 | 說明 | 範例 |
|------|------|------|
| `s2t` | 簡體 → 繁體 | 视频 → 視頻 |
| `s2tw` | 簡體 → 台灣繁體 | 视频 → 視頻 |
| `s2twp` | 簡體 → 台灣繁體（含慣用詞） | 视频 → 影片、软件 → 軟體 |
| `s2hk` | 簡體 → 香港繁體 | 视频 → 視頻 |
| `t2s` | 繁體 → 簡體 | 視頻 → 视频 |

**命令列使用：**

```bash
# 轉換 SRT 檔案
python -m JYpymaker.converter subtitle.srt -m s2twp

# 轉換剪映草稿
python -m JYpymaker.converter draft_content.json -m s2tw -v
```

### 草稿自動搜尋

自動偵測並列出剪映/CapCut 草稿，無需手動尋找路徑：

```python
from JYpymaker import get_jianying_drafts_path, list_drafts, find_draft_by_name

# 取得剪映草稿目錄
drafts_path = get_jianying_drafts_path()
# Windows: C:\Users\xxx\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft
# macOS: ~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft

# 列出所有草稿（按修改時間排序）
drafts = list_drafts()
for d in drafts:
    print(f"{d['name']} - {d['path']}")

# 根據名稱搜尋草稿（支援部分匹配）
draft_path = find_draft_by_name("翻譯_video")
```

**命令列使用：**

```bash
# 列出所有草稿
python -m JYpymaker.converter --list

# 根據名稱搜尋並轉換草稿
python -m JYpymaker.converter --draft "翻譯_video" -m s2twp
```

## 核心概念

### 架構圖

```
ScriptFile (草稿文件)
├── materials (素材庫)
│   ├── videos: List[VideoMaterial]
│   ├── audios: List[AudioMaterial]
│   └── texts: List[Dict]
├── tracks (軌道)
│   ├── video tracks
│   ├── audio tracks
│   └── text tracks
└── imported_tracks (從模板導入的軌道)
```

### 時間單位

所有時間單位都是**微秒 (μs)**：
- 1 秒 = 1,000,000 微秒
- 使用 `tim()` 函數可以方便轉換：

```python
from JYpymaker import tim, trange, SEC

tim("1s")        # -> 1000000
tim("1.5s")      # -> 1500000
tim("1m30s")     # -> 90000000
tim(5 * SEC)     # -> 5000000

# 建立時間範圍
trange("0s", "5s")  # -> Timerange(start=0, duration=5000000)
```

### 座標系統

- `transform_x`: 水平位移，單位為半個畫布寬（-1 到 1）
- `transform_y`: 垂直位移，單位為半個畫布高（-1 到 1）
- 原點在畫面中心
- `transform_y=-0.8` 表示在畫面下方 80% 處

### 素材替換模式

當新素材比原素材長時，可選擇處理方式：

```python
from JYpymaker.template_mode import ExtendMode

ExtendMode.cut_material_tail  # 裁剪素材尾部，片段維持原長
ExtendMode.extend_tail        # 延伸片段尾部
ExtendMode.push_tail          # 延伸片段並推移後續片段
ExtendMode.extend_head        # 延伸片段頭部
```

當新素材比原素材短時：

```python
from JYpymaker.template_mode import ShrinkMode

ShrinkMode.cut_tail       # 裁剪片段尾部
ShrinkMode.cut_head       # 裁剪片段頭部
ShrinkMode.cut_tail_align # 裁剪尾部並對齊後續片段
ShrinkMode.shrink         # 兩端向中間收縮
```

## API 參考

### ScriptFile

| 方法 | 說明 |
|------|------|
| `load_template(path)` | 從 JSON 載入草稿模板 |
| `get_imported_track(type, name, index)` | 取得導入的軌道 |
| `replace_material_by_seg(track, index, material)` | 替換片段素材 |
| `import_srt(path, track_name, ...)` | 導入 SRT 字幕 |
| `add_track(type, name)` | 新增軌道 |
| `add_segment(segment, track_name)` | 新增片段 |
| `save()` | 儲存草稿 |
| `dumps()` | 匯出為 JSON 字串 |

### TextStyle

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `size` | float | 8.0 | 字體大小 |
| `color` | tuple | (1,1,1) | RGB 顏色 (0-1) |
| `alpha` | float | 1.0 | 不透明度 |
| `bold` | bool | False | 粗體 |
| `italic` | bool | False | 斜體 |
| `align` | int | 0 | 對齊 (0=左, 1=中, 2=右) |
| `auto_wrapping` | bool | False | 自動換行 |

### ClipSettings

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `transform_x` | float | 0.0 | 水平位移 |
| `transform_y` | float | 0.0 | 垂直位移 |
| `scale_x` | float | 1.0 | 水平縮放 |
| `scale_y` | float | 1.0 | 垂直縮放 |
| `rotation` | float | 0.0 | 旋轉角度 |
| `alpha` | float | 1.0 | 不透明度 |

## 與原版的差異

### 移除的功能

- ❌ 視頻特效 (VideoSceneEffectType, VideoCharacterEffectType)
- ❌ 音頻特效 (AudioSceneEffectType, ToneEffectType)
- ❌ 濾鏡 (FilterType)
- ❌ 轉場 (TransitionType)
- ❌ 蒙版 (MaskType)
- ❌ 動畫 (IntroType, OutroType, GroupAnimationType)
- ❌ 文字動畫 (TextIntro, TextOutro, TextLoopAnim)
- ❌ 字體類型 (FontType)
- ❌ 剪映自動化控制 (JianyingController)

### 保留的功能

- ✅ 模板載入與儲存
- ✅ 素材管理 (VideoMaterial, AudioMaterial)
- ✅ 軌道操作
- ✅ 素材替換
- ✅ SRT 字幕導入
- ✅ 文字樣式 (TextStyle, TextBorder, TextBackground, TextShadow)
- ✅ 圖像調節 (ClipSettings)
- ✅ 時間工具 (Timerange, tim, trange)
- ✅ 簡繁轉換 (convert_text, convert_srt_file, convert_draft)
- ✅ 草稿自動搜尋 (get_jianying_drafts_path, list_drafts, find_draft_by_name)

## 完整範例

請參考 [translate_video.py](../translate_video.py) 中的 `create_jianying_draft` 方法。

## 授權

MIT License

## 致謝

- 原始專案：[pyJianYingDraft](https://github.com/GuoChen018/pyJianYingDraft)
