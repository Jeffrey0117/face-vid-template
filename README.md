# Face Video Template - 影片自動化處理工具

整合多種影片處理工作流程：長片翻譯、模板替換、字幕編輯。

---

## 快速啟動

| 功能 | 啟動方式 | 說明 |
|------|----------|------|
| **長片翻譯** | `start-youtube-translate.bat` | 英文影片 → 中文字幕草稿 |
| **草稿樣式編輯** | `start-draft-style-editor.bat` | 修改現有草稿字幕樣式 |
| **翻譯設定編輯** | `start-translate-editor.bat` | 修改翻譯參數/字幕預設樣式 |
| **面相專案** | `run.bat` | 模板批次替換影片 |
| **面相模板編輯** | `start-editor.bat` | 編輯面相模板文字 |
| **蝦皮專案** | `蝦皮專案-處理影片.bat` | 蝦皮商品影片處理 |

---

## 1. 長片翻譯

將英文影片自動轉錄、翻譯成繁體中文字幕。

### 使用流程

```
1. 放影片 → backend/downloads/youtube/
2. 執行   → start-youtube-translate.bat
3. 結果   → 剪映草稿 + videos/translated/*.srt
```

### 處理步驟

1. **Whisper** 語音識別 (英文)
2. **DeepSeek API** 批次翻譯 (50句/批)
3. 生成 **SRT** 字幕檔
4. 創建**剪映草稿** (含字幕)

### 配置 (`translation_config.json`)

```json
{
  "whisper": { "model": "medium" },
  "translation": {
    "api_key": "sk-xxx",
    "batch_size": 50
  },
  "subtitle_style": {
    "font_size": 7,
    "stroke_width": 2,
    "shadow": true
  },
  "workflow": { "skip_existing": true }
}
```

---

## 2. 草稿字幕樣式編輯器

修改已存在剪映草稿的字幕樣式。

```bash
start-draft-style-editor.bat
# 開啟 http://localhost:8082
```

功能：選擇草稿 → 調整樣式 → 套用
支援：字體大小、顏色、描邊、陰影、背景

---

## 3. 面相專案

使用預設模板批次生成影片。

```bash
# 1. 放影片
videos/raw/

# 2. 執行
run.bat
```

相關腳本：
- `start-editor.bat` - 編輯模板文字
- `export-faces.bat` - 批量導出

---

## 檔案結構

```
face-vid-template/
├── 核心腳本
│   ├── translate_video.py          # 長片翻譯
│   ├── template_video_replacer.py  # 面相模板替換
│   └── shopee_video.py             # 蝦皮處理
│
├── 編輯器
│   ├── draft_style_editor_server.py + .html   # 草稿樣式
│   ├── translate_editor_server.py + .html     # 翻譯設定
│   └── template_editor_server.py + .html      # 模板編輯
│
├── 配置
│   ├── config.json                 # 路徑設定
│   └── translation_config.json     # 翻譯參數
│
├── 模板 (剪映草稿模板)
│   ├── 長片翻譯專案/
│   └── 面相專案/
│
├── 影片
│   ├── backend/downloads/youtube/  # 待翻譯影片
│   ├── videos/raw/                 # 面相原始影片
│   └── videos/translated/          # SRT 輸出
│
└── pyJianYingDraft/                # 剪映 Python 庫
```

---

## 所有啟動腳本

| 腳本 | 用途 |
|------|------|
| `start-youtube-translate.bat` | 長片翻譯主程式 |
| `start-draft-style-editor.bat` | 草稿樣式編輯器 |
| `start-translate-editor.bat` | 翻譯設定編輯器 |
| `run.bat` | 面相專案執行 |
| `start-editor.bat` | 面相模板編輯器 |
| `export-faces.bat` | 面相批量導出 |
| `蝦皮專案-處理影片.bat` | 蝦皮影片處理 |
| `start-studio.bat` | 整合 Web App |
| `start-backend.bat` | 後端服務 |
| `build-win.bat` | Electron 打包 |

---

## 環境需求

- Python 3.10+
- Node.js 18+ (Electron)
- CUDA (可選，加速 Whisper)

```bash
pip install -r requirements_translation.txt
```

---

## 常見問題

| 問題 | 解決 |
|------|------|
| API Key 錯誤 | 檢查 `translation_config.json` 的 `api_key` |
| 影片時長不對 | 已修正，自動讀取實際時長 |
| 草稿加密無法編輯 | 編輯器會讀取 `.bak` 備份檔 |
| 想跳過已處理影片 | 設定 `skip_existing: true` |
| 翻譯太慢 | 使用批次翻譯 (`batch_size: 50`) |

---

*v3.1 | 2025-12-31*
