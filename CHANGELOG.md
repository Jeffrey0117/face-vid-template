# 開發日誌 / Changelog

## [1.3.0] - 2024-12-26

### 新增功能 - 統一 Web App (SaaS 風格)

#### 核心功能
- **統一 Web 介面**：整合所有工具於單一 SaaS 風格 Web App
- **FastAPI 後端**：RESTful API + WebSocket 即時通訊
- **YouTube 下載**：使用 yt-dlp 支援多種格式下載
  - 支援格式：best / 1080p / 720p / 480p / 純音訊
  - 即時進度回報
  - 下載歷史記錄
- **Instagram 下載**：Selenium 自動化下載 Reels
  - 批量下載佇列
  - 自動重試機制

#### UI/UX 改進
- **移除側邊欄**：簡化版面配置
- **底部導航列**：App 風格的底部 Tab Bar
  - 首頁、工作流、IG下載、YT下載、設定
- **增強下載狀態管理**
  - 即時進度條與百分比顯示
  - 狀態圖示（解析中、下載中、處理中、完成、失敗）
  - CSS 動畫效果（脈衝、旋轉）
- **統一設計系統**：CSS custom properties

#### 技術架構
- **前端**：Vue 3 Composition API (CDN)
- **後端**：FastAPI + SQLite + SQLAlchemy
- **下載引擎**
  - yt-dlp (YouTube)
  - Selenium (Instagram)
- **即時通訊**：WebSocket

### 新增檔案
- `app.html` - 統一 Web App 主頁
- `backend/` - FastAPI 後端
  - `main.py` - 應用入口
  - `api/routes.py` - IG 下載 API
  - `api/youtube_routes.py` - YouTube 下載 API
  - `api/websocket.py` - WebSocket 管理
  - `services/youtube_downloader.py` - YouTube 下載服務
  - `services/downloader.py` - IG 下載服務
- `styles/design-system.css` - 統一設計系統
- `start-studio.bat` - Web App 啟動腳本
- `SPEC_unified_webapp.md` - 技術規格書

### 啟動方式
```bash
# 方式 1：使用啟動腳本
start-studio.bat

# 方式 2：手動啟動
cd backend
pip install -r requirements.txt
python main.py
# 然後在瀏覽器開啟 app.html
```

---

## [1.2.0] - 2024-12-18

### 新增功能 - 翻譯影片工作流程
- **Whisper 語音識別**：自動轉錄影片音軌為字幕
- **自動翻譯**：支援 OpenAI GPT 翻譯 (英文→繁體中文)
- **剪映字幕生成**：自動添加字幕軌道到剪映草稿
- **批量處理**：支援資料夾批量處理

### 新增檔案
- `translate_video.py` - 翻譯工作流程主程式
- `subtitle_generator.py` - Whisper + 翻譯模組
- `translation_config.json` - 翻譯設定檔
- `translate.bat` - 一鍵啟動腳本
- `requirements_translation.txt` - 依賴套件清單
- `docs/翻譯專案開發規格書.md` - 開發規格文件

---

## [1.1.0] - 2024-12-18

### 新增功能
- **模板同步機制**：每次執行自動將 `面相專案` 同步到剪映草稿夾（強制覆蓋）
- **Vue 模板文字編輯器**：雙向綁定編輯模板內的文字內容
  - `template-editor.html` - 前端編輯介面
  - `template_editor_server.py` - 後端 API
  - `start-editor.bat` - 一鍵啟動
- **批量導出失敗處理**
  - 自動跳過已導出成功的影片（比對輸出資料夾）
  - 顯示成功/失敗清單
  - 保存失敗清單到 `failed_exports.txt`
  - 支援重試失敗項目
- **新增啟動腳本**
  - `export-faces.bat` - 批量導出面相

### 改進
- `run.bat` 改為統一入口，確保所有啟動方式流程一致
- `.gitignore` 新增 `__pycache__/`、`config.json`、`*.spec`

---

## 待開發 / TODO

### 影片比例預檢機制
- [ ] 檢查影片長寬比是否符合模板（9:16 直式）
- [ ] 檢查影片解析度是否足夠
- [ ] 不符合的影片自動跳過或警告
- [ ] 考慮支援自動轉換/裁切不符合比例的影片

### 其他規劃
- [ ] 導出進度即時顯示
- [ ] 批量導出的並行處理優化
- [ ] 模板編輯器整合到 Electron GUI

---

## [1.0.0] - 初始版本

- 基於剪映模板批量替換影片
- 自動替換文字變數
- Electron 桌面應用介面
- 支援多種啟動方式（npm start / bat / python）
