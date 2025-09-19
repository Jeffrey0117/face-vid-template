# 面相影片模板專案 - 完整使用指南

![](https://storage.meteor.today/image/68cbbfe740d40989feca2551.png)

> **⚠️ 重要提醒：本專案必須搭配剪映 5.9 未加密版本使用！**
> 此專案提供自動化面相分析影片生成工具，可批量創建包含不同面相類型的影片專案。

## 🔄 使用流程與工作原理

### 快速使用流程

1. **複製模板**：這個會自動做 也不用做
2. **執行配置**：運行 [`run.py`](run.py) 腳本，自動配置草稿參數 自動將啟動模板 將 [`面相專案`](面相專案) 資料夾複製到剪映草稿區目錄
3. **重開剪映**：重新啟動剪映應用程式，即可在草稿列表中看到新的專案
4. **批量輸出**：執行 [`batch_export_faces.py`](batch_export_faces.py) 進行批量影片輸出

### 工作原理說明

本系統通過模擬剪映的草稿結構，實現面相影片的批量自動化生成：

- **模板管理**：[`面相專案`](面相專案) 資料夾包含完整的剪映草稿結構，包括影片軌道、音訊、特效等配置
- **自動配置**：[`run.py`](run.py) 會根據 [`config.json`](config.json) 設定，自動調整草稿中的影片路徑、時長等參數
- **批量處理**：系統可以讀取 [`videos/`](videos) 目錄中的多個影片檔案，逐一替換模板中的面相影片
- **無縫整合**：生成的草稿完全相容剪映格式，無需額外轉換即可直接使用

此流程避免了手動重複操作，大幅提升面相影片製作效率。

## 💻 Electron 桌面應用功能介紹

### 🎨 現代化用戶界面

本專案提供了完整的桌面應用解決方案，具備以下特色功能：

#### 主要功能區域

1. **🎯 一鍵執行區域**

   - 大型執行按鈕，一鍵啟動整個工作流程
   - 智能狀態顯示：準備就緒 / 執行中 / 完成 / 錯誤
   - 執行中可隨時取消操作

2. **📁 檔案管理區域**

   - 視覺化顯示當前配置的影片資料夾路徑
   - 拖拽或點擊選擇資料夾功能
   - 自動掃描並顯示找到的影片檔案數量
   - 支援影片預覽和基本資訊顯示

3. **⚙️ 配置管理區域**

   - 圖形化配置介面，無需手動編輯 JSON 檔案
   - 智能路徑偵測和驗證
   - 剪映安裝路徑自動搜尋
   - 配置匯入/匯出功能

4. **📊 進度監控區域**
   - 實時進度條顯示當前執行進度
   - 詳細的步驟說明和時間估算
   - 執行日誌即時輸出
   - 錯誤提示和解決建議

#### 使用流程

1. **啟動應用**：執行 `npm start` 開啟桌面應用
2. **配置檢查**：應用會自動檢查和驗證系統配置
3. **選擇影片**：透過介面選擇包含面相影片的資料夾
4. **一鍵執行**：點擊執行按鈕開始批量處理
5. **監控進度**：透過進度條和日誌監控執行狀態
6. **獲取結果**：處理完成後自動開啟結果資料夾

### 🔧 桌面應用安裝與設定

#### 首次安裝

```bash
# 1. 安裝 Node.js 依賴
npm install

# 2. 驗證安裝
npm start
```

#### 系統需求

- **Node.js**: 16.0+ (包含 npm)
- **Python**: 3.7+ (後端處理)
- **剪映**: 5.9 未加密版本
- **作業系統**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)

#### 開發模式

```bash
# 開啟開發模式（包含調試工具）
npm run dev
```

#### 打包為獨立應用

```bash
# 打包為 Windows 執行檔
npm run build-win

# 打包為 macOS 應用
npm run build-mac

# 打包為 Linux AppImage
npm run build-linux
```

## 📁 專案結構

```
face-vid-template/                           # 🏠 專案根目錄
│
├── 📋 核心啟動檔案
│   ├── README.md                            # 📖 專案說明文檔
│   ├── guide.md                             # 📋 詳細使用指南
│   ├── plan.md                              # 📋 專案開發計畫文檔
│   ├── start.bat                            # 🚀 Windows 一鍵啟動腳本
│   ├── run.bat                              # 🚀 Windows 啟動腳本（舊版）
│   ├── run.py                               # 🌐 跨平台啟動腳本
│   └── config.json                          # ⚙️ 自動生成配置檔案
│
├── 🖥️ Electron 桌面應用
│   ├── package.json                         # 📦 Node.js 專案配置與依賴
│   ├── package-lock.json                    # 🔒 依賴版本鎖定檔案
│   ├── electron-main.js                     # ⚡ Electron 主程序入口
│   ├── index.html                           # 🌐 桌面應用前端頁面
│   └── renderer.js                          # 🎨 前端互動邏輯腳本
│
├── 🛠️ 核心功能腳本
│   ├── setup_paths.py                       # 🔍 智能路徑偵測系統
│   ├── template_video_replacer.py           # 🎬 核心影片替換引擎
│   └── batch_export_faces.py                # 📤 批量導出影片工具
│
├── 📚 剪映草稿操作庫 (pyJianYingDraft/)
│   ├── __init__.py                          # 初始化模組
│   ├── draft_folder.py                      # 草稿資料夾管理
│   ├── script_file.py                       # 腳本檔案處理
│   ├── video_segment.py                     # 影片片段操作
│   ├── audio_segment.py                     # 音訊片段處理
│   ├── text_segment.py                      # 文字片段管理
│   ├── track.py                             # 軌道操作工具
│   ├── keyframe.py                          # 關鍵影格處理
│   ├── animation.py                         # 動畫效果管理
│   ├── effect_segment.py                    # 特效片段處理
│   ├── time_util.py                         # 時間工具函式
│   ├── util.py                              # 通用工具函式
│   ├── local_materials.py                   # 本地素材管理
│   ├── template_mode.py                     # 模板模式操作
│   ├── jianying_controller.py               # 剪映控制器
│   ├── segment.py                           # 基礎片段類別
│   ├── exceptions.py                        # 例外處理定義
│   ├── 📁 assets/                           # 草稿模板資源
│   │   ├── __init__.py
│   │   ├── draft_content_template.json      # 草稿內容模板
│   │   └── draft_meta_info.json             # 草稿元數據模板
│   └── 📁 metadata/                         # 元數據定義檔案
│       ├── __init__.py
│       ├── effect_meta.py                   # 特效元數據
│       ├── filter_meta.py                   # 濾鏡元數據
│       ├── font_meta.py                     # 字體元數據
│       ├── mask_meta.py                     # 遮罩元數據
│       ├── transition_meta.py               # 轉場元數據
│       └── [其他元數據檔案...]
│
├── 🎬 影片素材庫 (videos/)
│   ├── 📁 raw/                              # 🆕 新影片素材放置區
│   │   └── (請將待處理的面相影片放在此處)    # 💡 建議命名：面相類型.mp4
│   ├── logo.jpg                             # 專案 Logo 圖片
│   └── video_for_template.mp4               # 模板測試影片
│
└── 📂 剪映專案模板 (面相專案/)              # 🎭 完整剪映草稿模板
    ├── draft_content.json                   # 📝 主要專案配置檔案
    ├── draft_meta_info.json                 # 📊 專案元數據資訊
    ├── draft_settings                       # ⚙️ 草稿設定檔案
    ├── draft_cover.jpg                      # 🖼️ 專案封面圖片
    ├── template.tmp                         # 📋 模板檔案
    ├── template-2.tmp                       # 📋 備用模板檔案
    ├── draft.extra                          # 📎 額外設定檔案
    └── [其他資源目錄...]
```

## ⚙️ 環境需求

### 必要軟體

- **剪映專業版 5.9 未加密版本** ⚠️ 關鍵要求
- Python 3.7+
- Windows 作業系統（主要支援，macOS/Linux 部分功能可用）

### 依賴套件

所有依賴套件均為 Python 內建模組，無需額外安裝：

- `json` - JSON 數據處理
- `os`、`pathlib` - 作業系統接口和路徑操作
- `shutil` - 文件操作工具
- `glob` - 檔案模式匹配
- `getpass` - 用戶名獲取
- `uuid` - 唯一識別碼生成
- `pyJianYingDraft` - 剪映草稿操作庫（內建）

## 🔧 配置系統

### 自動配置生成

本專案採用智能路徑偵測系統，會自動：

1. **偵測項目根目錄**：尋找包含關鍵文件的目錄
2. **偵測剪映安裝位置**：搜尋常見的剪映安裝路徑
3. **生成配置文件**：自動創建 `config.json`
4. **創建必要目錄**：自動建立所需的文件夾結構

### config.json 配置文件

自動生成的配置文件包含：

```json
{
  "version": "1.0",
  "generated_at": "2025-09-18 10:08:55.924448",
  "project_root": "C:\\Users\\Jeffrey\\Desktop\\cut-project\\face-vid-template",
  "template_folder": "C:\\Users\\Jeffrey\\Desktop\\cut-project\\face-vid-template\\面相專案",
  "videos_folder": "C:\\Users\\Jeffrey\\Desktop\\cut-project\\face-vid-template\\videos",
  "videos_raw_folder": "C:\\Users\\Jeffrey\\Desktop\\cut-project\\face-vid-template\\videos\\raw",
  "jianying_draft_folder": "C:\\Users\\Jeffrey\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft",
  "username": "Jeffrey",
  "relative_paths": {
    "template_folder": "面相專案",
    "videos_folder": "videos",
    "videos_raw_folder": "videos\\raw"
  }
}
```

### setup_paths.py 路徑偵測系統

智能路徑偵測功能：

- **🔍 項目根目錄偵測**：向上搜尋包含關鍵文件的目錄
- **📍 剪映路徑偵測**：自動搜尋常見的剪映安裝位置
- **🛠️ 自動修復**：創建缺失的目錄結構
- **✅ 路徑驗證**：檢查所有路徑的有效性

**偵測的關鍵文件**：

- `template_video_replacer.py`
- `pyJianYingDraft/`
- `面相專案/`
- `videos/`

**搜尋的剪映路徑**：

- `C:\Users\{用戶名}\AppData\Local\JianyingPro\...`
- `C:\Users\{用戶名}\AppData\Roaming\JianyingPro\...`
- `D:\JianyingPro\...`
- `C:\Program Files\JianyingPro\...`

## 🎬 完整工作流程

### 自動化面相影片生成流程

1. **準備階段**

   - 確保「面相專案」模板存在（系統會自動按優先順序查找）：
     - 優先：本地項目文件夾 `面相專案/`
     - 備用：剪映草稿文件夾中的「面相專案」
   - 在 `videos/raw/` 資料夾放置待處理的面相類型影片

2. **批量生成專案**

   - 執行 `template_video_replacer.py`
   - 系統自動為每個影片創建對應的剪映專案
   - 自動替換影片素材和相關文字

3. **批量導出影片**

   - 執行 `batch_export_faces.py`
   - 系統自動掃描所有面相專案草稿
   - 批量導出為 MP4 影片檔案

4. **結果獲取**
   - 所有影片保存在指定輸出資料夾
   - 每個影片對應一個面相類型

## 🔧 技術實現

### 模板讀取邏輯

系統使用雙層模板查找機制：

**1. 本地模板（優先）**

```
face-vid-template/面相專案/
├── draft_content.json     # 主要的專案配置文件
├── draft_meta_info.json   # 專案元數據
└── extra.json            # 附加設置信息（可選）
```

**2. 剪映草稿模板（備用）**

```
C:\Users\{用戶名}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\面相專案\
├── draft_content.json     # 主要的專案配置文件
├── draft_meta_info.json   # 專案元數據
└── extra.json            # 附加設置信息
```

### 輸出草稿文件結構

生成的新專案會保存到剪映草稿位置：

```
C:\Users\{用戶名}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\
├── 面相專案_典型妾相/
├── 面相專案_婊子/
└── 面相專案_頂級貴相/
```

每個生成的專案包含：

- `draft_content.json` - 主要的專案配置文件
- `draft_meta_info.json` - 專案元數據
- `extra.json` - 附加設置信息

## 🛠️ 故障排除

### 自動啟動問題

**Q：run.bat 或 run.py 無法執行？**
A：請檢查：

1. **Python 環境**：確保 Python 3.7+ 已安裝並在 PATH 中
2. **權限問題**：右鍵以管理員身份運行 run.bat
3. **文件完整性**：確保所有項目文件完整下載
4. **路徑問題**：確保在項目根目錄中執行腳本

**Q：配置文件生成失敗？**
A：可能原因：

1. **目錄權限**：檢查項目目錄的讀寫權限
2. **磁碟空間**：確保有足夠的磁碟空間
3. **防毒軟體**：檢查是否被防毒軟體阻止
4. **手動配置**：可嘗試手動運行 `python setup_paths.py`

### 路徑偵測問題

**Q：找不到剪映安裝目錄？**
A：解決方案：

1. **手動指定**：編輯 config.json 中的 `jianying_draft_folder` 路徑
2. **檢查安裝**：確認剪映是否正確安裝
3. **常見路徑**：檢查以下位置：
   - `C:\Users\{用戶名}\AppData\Local\JianyingPro\...`
   - `C:\Users\{用戶名}\AppData\Roaming\JianyingPro\...`

**Q：項目根目錄偵測錯誤？**
A：處理方法：

1. **手動調整**：直接編輯 config.json 文件
2. **重新生成**：刪除 config.json 後重新運行
3. **指定路徑**：確保在正確的項目目錄中運行腳本

### 專案生成問題

**Q：執行後沒有生成新專案？**
A：檢查：

1. **剪映版本**：是否使用剪映 5.9 未加密版本
2. **模板存在**：「面相專案」模板是否存在（按優先順序檢查）：
   - ✅ 本地項目文件夾：`face-vid-template/面相專案/`
   - 🔄 剪映草稿文件夾：`C:\Users\{用戶名}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\面相專案\`
3. **影片素材**：videos/raw 資料夾中是否有對應的影片檔案
4. **模板完整性**：模板文件夾中是否包含必要的 `draft_content.json` 文件
5. **配置文件**：config.json 是否正確生成和配置

**Q：生成的專案無法在剪映中打開？**
A：可能是：

1. **版本不匹配**：剪映版本與專案格式不兼容
2. **文件損壞**：草稿文件格式有誤或損壞
3. **權限問題**：檔案權限設定不正確
4. **路徑問題**：剪映草稿路徑配置錯誤

**Q：文字沒有正確替換？**
A：確認：

1. **關鍵字存在**：模板中的文字是否包含「婊子無情」等關鍵字
2. **格式正確**：文字格式和編碼是否正確
3. **JSON 結構**：草稿文件的 JSON 結構是否完整
4. **模板更新**：模板是否為最新版本

### 批量導出問題

**Q：批量導出提示「未找到任何面相專案草稿」？**
A：請檢查：

1. **專案生成**：是否已先執行 `template_video_replacer.py` 生成專案
2. **路徑正確**：剪映草稿路徑是否在 config.json 中正確配置
3. **命名格式**：專案名稱格式是否正確（以「面相專案\_」開頭）
4. **權限問題**：是否有足夠權限存取剪映草稿目錄

**Q：導出過程中提示「未找到導出路徑框」？**
A：這表示：

1. **剪映狀態**：剪映軟體未處於主頁面
2. **版本兼容**：剪映版本與腳本不兼容
3. **介面變更**：剪映介面可能有更新

請確保剪映處於正確狀態後重試。

**Q：如何中途停止批量導出？**
A：使用 `Ctrl+C` 強制停止腳本。但請注意，正在導出的影片可能會被中斷。

### 環境問題

**Q：Python 模組缺失錯誤？**
A：解決方案：

1. **內建模組**：所有依賴都是 Python 內建模組，通常不需額外安裝
2. **Python 版本**：確保使用 Python 3.7 或更高版本
3. **pyJianYingDraft**：確保 pyJianYingDraft 文件夾在項目目錄中

**Q：Windows 上無法執行 .bat 文件？**
A：嘗試：

1. **管理員權限**：右鍵以管理員身份運行
2. **執行策略**：檢查 Windows 執行策略設定
3. **防毒軟體**：暫時停用防毒軟體的實時保護
4. **手動執行**：直接運行 `python run.py`

## 🎁 便利功能

### run.bat - Windows 一鍵啟動腳本

專為 Windows 用戶設計的便利腳本：

**功能特色：**

- 🔍 **環境檢查**：自動檢查 Python 版本和必要模組
- 📝 **配置管理**：自動生成或驗證 config.json 配置文件
- 📁 **目錄管理**：自動創建缺失的目錄結構
- 🎬 **一鍵執行**：自動運行主程序
- 💡 **友善提示**：提供清楚的執行狀態和錯誤提示

**使用方法：**

```batch
# 雙擊運行
run.bat

# 或在命令列執行
.\run.bat
```

### run.py - 跨平台啟動腳本

適用於所有作業系統的 Python 啟動腳本：

**功能特色：**

- 🌐 **跨平台支援**：Windows、macOS、Linux 通用
- 🔍 **智能檢查**：Python 版本、模組、項目結構檢查
- 📝 **自動配置**：智能生成和驗證配置文件
- 🛠️ **自動修復**：創建缺失的目錄和文件
- 📊 **詳細報告**：提供完整的執行過程和結果報告

**使用方法：**

```bash
# 直接執行
python run.py

# Linux/macOS 可賦予執行權限
chmod +x run.py
./run.py
```

### setup_paths.py - 路徑配置工具

獨立的路徑偵測和配置工具：

**功能特色：**

- 🔍 **智能偵測**：自動尋找項目根目錄和剪映安裝位置
- 📝 **配置生成**：生成完整的 config.json 配置文件
- 🛠️ **路徑修復**：創建缺失的目錄結構
- ✅ **路徑驗證**：檢查所有路徑的有效性
- 📊 **詳細報告**：提供路徑配置摘要

**使用方法：**

```bash
# 單獨運行配置工具
python setup_paths.py
```

**適用場景：**

- 首次使用專案時
- 移動專案到新位置後
- 配置文件損壞時
- 手動調整路徑設定時

---

**專案版本**：v2.0 ⭐ 全新自動化版本
**最後更新**：2025-09-20
**相容性**：剪映專業版 5.9（未加密版本）
**新功能**：自動路徑偵測、一鍵啟動、跨平台支援、Electron 桌面應用
