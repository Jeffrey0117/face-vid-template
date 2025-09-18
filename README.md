# 面相影片模板專案

> **⚠️ 重要提醒：本專案必須搭配剪映 5.9 未加密版本使用！**

此專案提供自動化面相分析影片生成工具，可批量創建包含不同面相類型的影片專案。

## 🚀 快速開始

### ✨ 新的一鍵啟動方式

本專案現已支援自動路徑偵測系統，無需手動配置複雜路徑設定！

#### Windows 用戶（推薦）
```batch
# 雙擊運行或在命令列執行
run.bat
```

#### 跨平台用戶
```bash
# 適用於 Windows、macOS、Linux
python run.py
```

#### Linux/macOS 用戶
```bash
# 賦予執行權限並運行
chmod +x run.py
./run.py
```

### 🎯 自動化優勢

- **🔍 智能路徑偵測**：自動尋找項目根目錄和剪映安裝位置
- **📝 自動配置生成**：一鍵生成 config.json 配置文件
- **🛠️ 環境檢查**：自動檢查 Python 版本和必要模組
- **📁 目錄創建**：自動創建所需的文件夾結構
- **✅ 一鍵啟動**：無需記憶複雜的命令或路徑

## 📁 專案結構

```
face-vid-template/
├── README.md                    # 說明文檔（本文件）
├── run.bat                      # Windows 一鍵啟動腳本 ⭐ 新增
├── run.py                       # 跨平台啟動腳本 ⭐ 新增
├── setup_paths.py               # 自動路徑偵測系統 ⭐ 新增
├── config.json                  # 自動生成的配置文件 ⭐ 新增
├── template_video_replacer.py   # 核心影片替換腳本
├── batch_export_faces.py        # 批量導出影片腳本
├── pyJianYingDraft/            # 剪映草稿操作庫
│   ├── __init__.py             # 初始化文件
│   ├── *.py                    # 各種功能模組
│   ├── assets/                 # 草稿模板資源
│   └── metadata/               # 元數據定義
├── videos/                     # 面相影片素材庫
│   ├── raw/                    # 新影片素材放置資料夾
│   │   └── (待處理的新影片放這裡) # 新的待處理影片
│   ├── 婊子.mp4                 # 現有面相類型影片
│   ├── logo.jpg                # 素材圖片
│   └── video_for_template.mp4  # 模板影片
└── 面相專案/                   # 模板專案資料夾
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

## 🚀 使用說明

### ⭐ 新的簡化流程（推薦）

**只需兩步，輕鬆完成！**

#### 步驟 1：放置影片素材
將待處理的面相影片放入 `videos/raw/` 資料夾中：
- 檔案名稱建議使用面相類型命名（如：`典型妾相.mp4`、`頂級貴相.mp4` 等）
- 檔案名稱最多四個字，避免影片標題過長
- 支援 `.mp4` 格式影片

#### 步驟 2：一鍵啟動
```batch
# Windows 用戶（推薦）
run.bat

# 跨平台用戶
python run.py
```

**就這麼簡單！** 系統會自動：
- 🔍 偵測和配置所有必要路徑
- 📁 創建缺失的目錄結構
- 🎬 批量生成剪映專案
- ✅ 檢查環境和依賴

### 🔧 手動執行方式（進階用戶）

如果您偏好手動控制每個步驟：

#### 步驟 1：初始化配置（首次使用）
```bash
python setup_paths.py
```

#### 步驟 2：準備模板專案

系統會優先使用本地項目文件夾中的「**面相專案**」模板：

1. **主要模板來源**：本地項目文件夾 `face-vid-template/面相專案/`
2. **備用模板來源**：剪映草稿文件夾中的「面相專案」（如果本地不存在）

**模板查找邏輯**：
- ✅ 優先：從本地項目文件夾 `面相專案/` 讀取模板
- 🔄 備用：如果本地沒有，則從剪映用戶數據文件夾查找

這樣的設計讓您可以：
- 📦 將模板與項目一起管理和版本控制
- 🔧 輕鬆修改和自定義模板內容
- 🚀 無需依賴剪映軟體即可存取模板

#### 步驟 3：準備影片素材

確認 [`videos/raw`](videos/raw) 資料夾中包含面相類型影片：

- 將新的面相影片檔案放入 `videos/raw/` 資料夾
- 檔案名稱建議使用面相類型命名（如：`典型妾相.mp4`、`頂級貴相.mp4` 等）
- 系統會自動掃描此資料夾中的所有 `.mp4` 檔案

#### 步驟 4：執行批量生成

```bash
python template_video_replacer.py
```

#### 步驟 5：檢查生成結果

腳本會在剪映草稿資料夾中生成對應的專案：

- `面相專案_典型的妾相`
- `面相專案_婊子`
- `面相專案_頂級貴相`
- `面相專案_沉浸情色`

#### 步驟 6：批量導出影片

生成專案後，使用批量導出腳本將所有面相專案導出為影片：

```bash
# 使用默認設置（桌面輸出，1080P，30fps）
python batch_export_faces.py

# 指定輸出路徑
python batch_export_faces.py "C:\Users\YourName\Desktop\face_exports"

# 指定輸出路徑、解析度、幀率
python batch_export_faces.py "C:\Users\YourName\Desktop\face_exports" 1080P 24fps
```

**批量導出參數說明:**

- `output_path`: 可選，影片輸出資料夾路徑，默認為桌面
- `resolution`: 可選，導出分辨率 (480P, 720P, 1080P, 2K, 4K, 8K)，默認 1080P
- `framerate`: 可選，導出幀率 (24fps, 25fps, 30fps, 50fps, 60fps)，默認 30fps

#### 步驟 7：獲取最終影片

批量導出完成後，所有影片將保存在指定的輸出資料夾中。

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

## ⚠️ 重要注意事項

### 剪映版本要求

- **必須使用剪映 5.9 未加密版本**
- 較新版本可能會對草稿文件進行加密，導致無法正常讀取和修改
- 如果發現專案無法正常生成，請檢查剪映版本

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

---

**專案版本**：v2.0 ⭐ 全新自動化版本
**最後更新**：2025-09-18
**相容性**：剪映專業版 5.9（未加密版本）
**新功能**：自動路徑偵測、一鍵啟動、跨平台支援
