# YouTube 翻譯工作流程使用指南

> 版本：1.0
> 日期：2025-12-26
> 專案：face-vid-template

---

## 目錄

1. [功能概述](#功能概述)
2. [前置準備](#前置準備)
3. [工作流程](#工作流程)
4. [設定說明](#設定說明)
5. [常見問題](#常見問題)

---

## 功能概述

### 核心功能

本工作流程整合以下功能，實現 YouTube 影片自動翻譯並生成剪映草稿：

1. **YouTube 影片下載** - 使用 yt-dlp 下載高畫質影片
2. **語音識別** - Whisper AI 自動轉錄英文字幕
3. **AI 翻譯** - OpenAI GPT 翻譯為繁體中文
4. **字幕樣式** - 可自訂字型、顏色、位置等
5. **剪映草稿生成** - 自動添加字幕軌道到長片專案

### 適用場景

- YouTube 教學影片本地化
- 國外技術影片翻譯
- Podcast 節目字幕製作
- 長影片批量處理

---

## 前置準備

### 1. 軟體需求

| 軟體 | 版本 | 用途 |
|-----|------|------|
| Python | 3.8+ | 執行環境 |
| 剪映專業版 | 5.9.0 | 草稿導入 |
| 瀏覽器 | Chrome/Edge | Web 編輯器 |

### 2. 安裝依賴套件

```bash
# 基礎套件（已安裝）
pip install -r backend/requirements.txt

# 翻譯專用套件
pip install -r requirements_translation.txt
```

### 3. 設定 OpenAI API Key

創建 `.env` 檔案（專案根目錄）：

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

### 4. 確認剪映草稿範本

確保以下範本存在於剪映草稿資料夾：

- **長片專案** - 橫式影片範本（1920x1080）
- **翻譯專案** - 直式影片範本（1080x1920，含字幕樣式）

路徑：`C:\Users\{你的使用者名稱}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft`

---

## 工作流程

### 步驟 1：下載 YouTube 影片

使用統一 Web App 下載影片：

```bash
# 啟動 Web App
start-studio.bat
```

1. 開啟瀏覽器訪問 `http://localhost:8000`
2. 切換到「YT下載」頁面
3. 輸入 YouTube 網址
4. 選擇畫質（建議：1080p）
5. 點擊「下載」

下載完成後，影片將儲存在：
`C:\face-vid-template\backend\downloads\youtube\`

### 步驟 2：啟動翻譯編輯器

執行啟動腳本：

```bash
start-youtube-translate.bat
```

瀏覽器將自動開啟編輯器：
`http://localhost:8081/translate_editor.html`

### 步驟 3：配置字幕樣式

在編輯器左側設定面板調整：

#### 基礎樣式
- **字體大小**：建議 8-12（依影片解析度調整）
- **文字顏色**：預設白色 `#FFFFFF`
- **背景顏色**：預設黑色 `#000000`
- **背景透明度**：0.7（70% 不透明）

#### 進階樣式
- **垂直位置**：-0.75（負值 = 畫面下方）
- **描邊粗細**：2（增強可讀性）
- **描邊顏色**：黑色 `#000000`
- **粗體**：建議開啟
- **陰影**：建議開啟
- **最大行寬**：0.82（82% 畫面寬度）

#### 即時預覽

右側預覽區會即時顯示字幕效果，調整至滿意後點擊「儲存設定」。

### 步驟 4：執行翻譯工作流程

1. 確認「待處理影片」列表顯示已下載的影片
2. 點擊「開始執行」按鈕
3. 等待處理完成（每個影片約需 3-10 分鐘，依長度而定）

#### 處理流程

```
[1/N] 影片檔名.mp4
  - 使用 Whisper 轉錄... ✓
  - 翻譯字幕... ✓
  - 生成剪映草稿... ✓
  完成
```

### 步驟 5：開啟剪映編輯

處理完成後：

1. 開啟剪映專業版
2. 在草稿列表中找到「翻譯專案_{影片名稱}」
3. 雙擊開啟草稿
4. 檢查字幕效果
5. 進行細部調整（如需要）
6. 導出影片

---

## 設定說明

### translation_config.json

完整設定檔結構：

```json
{
  "version": "1.0",
  "project_name": "YouTube翻譯專案",
  "project_type": "youtube_translate",

  "paths": {
    "source_video_folder": "backend/downloads/youtube",
    "output_folder": "videos/translated",
    "draft_template": "翻譯專案",
    "long_video_template": "長片專案"
  },

  "whisper": {
    "model": "base",
    "language": "en",
    "task": "transcribe",
    "temperature": 0,
    "word_timestamps": true
  },

  "translation": {
    "service": "openai",
    "source_language": "en",
    "target_language": "zh-TW",
    "model": "gpt-3.5-turbo",
    "prompt_template": "將以下英文字幕翻譯成繁體中文..."
  },

  "subtitle_style": {
    "font_size": 10,
    "text_color": "#FFFFFF",
    "background_color": "#000000",
    "background_alpha": 0.7,
    "position_y": -0.75,
    "stroke_width": 2,
    "stroke_color": "#000000",
    "bold": true,
    "shadow": true,
    "line_max_width": 0.82
  },

  "jianying": {
    "canvas_width": 1080,
    "canvas_height": 1920,
    "canvas_ratio": "original",
    "fps": 30
  },

  "workflow": {
    "auto_download_youtube": true,
    "auto_transcribe": true,
    "auto_translate": true,
    "auto_generate_draft": true,
    "skip_existing": true
  }
}
```

### 關鍵參數說明

#### Whisper 模型選擇

| 模型 | 準確度 | 速度 | 記憶體 | 建議場景 |
|-----|--------|------|--------|---------|
| tiny | 低 | 極快 | 1GB | 快速測試 |
| base | 中 | 快 | 1GB | 一般影片 |
| small | 中高 | 中 | 2GB | 教學影片 |
| medium | 高 | 慢 | 5GB | 專業影片 |
| large | 極高 | 極慢 | 10GB | 高品質需求 |

#### 翻譯服務選擇

- **OpenAI GPT-3.5-turbo** - 平衡品質與成本（推薦）
- **OpenAI GPT-4** - 最高品質但成本較高
- **Google Translate** - 免費但品質較差（需額外安裝）
- **DeepL** - 高品質但需付費 API

---

## 常見問題

### Q1：Whisper 轉錄失敗？

**原因**：可能是影片沒有語音或語言設定錯誤

**解決**：
1. 確認影片有清晰語音
2. 檢查 `whisper.language` 是否設為 `"en"`
3. 嘗試更換模型（如 `small` 或 `medium`）

### Q2：翻譯失敗或品質差？

**原因**：OpenAI API Key 無效或配額不足

**解決**：
1. 確認 `.env` 檔案中的 API Key 正確
2. 檢查 OpenAI 帳戶餘額
3. 調整 `prompt_template` 提示詞

### Q3：剪映草稿打不開？

**原因**：草稿範本不存在或已損壞

**解決**：
1. 確認「長片專案」和「翻譯專案」範本存在
2. 手動在剪映中創建範本專案
3. 檢查草稿路徑是否正確

### Q4：字幕位置或樣式不對？

**原因**：設定未生效或範本衝突

**解決**：
1. 重新調整 `subtitle_style` 參數
2. 點擊「儲存設定」並重新執行
3. 在剪映中手動微調

### Q5：處理速度很慢？

**原因**：Whisper 模型過大或影片過長

**解決**：
1. 使用較小的 Whisper 模型（如 `base` 或 `small`）
2. 確保有足夠的 GPU 記憶體（建議 CUDA）
3. 分段處理長影片

---

## 技術支援

### 檔案結構

```
face-vid-template/
├── backend/
│   └── downloads/
│       └── youtube/          # YouTube 下載影片存放處
├── videos/
│   └── translated/           # 翻譯後影片輸出（未來）
├── docs/
│   └── YouTube翻譯工作流程使用指南.md
├── translation_config.json   # 翻譯設定檔
├── translate_editor.html     # Web 編輯器前端
├── translate_editor_server.py # Web 編輯器後端
└── start-youtube-translate.bat # 啟動腳本
```

### 日誌位置

- **Web 編輯器日誌**：瀏覽器 Console (F12)
- **伺服器日誌**：終端機輸出
- **剪映草稿**：`%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft`

### 聯絡資訊

如有問題，請查閱：
- **專案文檔**：`docs/` 資料夾
- **CHANGELOG**：`CHANGELOG.md`
- **GitHub Issues**：（如有開源）

---

## 附錄：快速參考

### 一鍵執行流程

```bash
# 1. 下載影片
start-studio.bat
# 瀏覽器開啟後，在 YT 下載頁面輸入網址並下載

# 2. 翻譯影片
start-youtube-translate.bat
# 瀏覽器開啟後，調整設定並點擊「開始執行」

# 3. 開啟剪映編輯
# 手動開啟剪映專業版，找到對應草稿
```

### 推薦設定（中文字幕）

```json
{
  "subtitle_style": {
    "font_size": 10,
    "text_color": "#FFFF00",
    "background_color": "#000000",
    "background_alpha": 0.8,
    "position_y": -0.75,
    "stroke_width": 2.5,
    "stroke_color": "#000000",
    "bold": true,
    "shadow": true,
    "line_max_width": 0.85
  }
}
```

---

*本文檔由專案監督 Agent 生成*
*最後更新：2025-12-26*
