# 開發日誌 / Changelog

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
