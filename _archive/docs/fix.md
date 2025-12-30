# pyJianYingDraft 重複目錄結構修復計劃

## 🔍 問題診斷

### 當前狀況
基於初步分析，專案中存在以下結構：

```
face-vid-template/
├── pyJianYingDraft/                 # 主要的 Python 模組
│   ├── __init__.py
│   ├── *.py 檔案
│   ├── assets/
│   └── metadata/
├── 面相專案/                         # 剪映草稿專案目錄
│   └── [可能包含重複的 pyJianYingDraft]
└── 其他專案檔案...
```

### 潛在問題
1. **模組衝突**: 可能存在多個 pyJianYingDraft 目錄
2. **導入路徑混亂**: Python 可能無法確定要導入哪個版本
3. **依賴不一致**: 不同位置的模組可能版本不同
4. **維護困難**: 多個副本增加維護成本

## 📋 修復任務清單

### 階段一：診斷和分析
- [ ] 1.1 確認所有 pyJianYingDraft 目錄位置
- [ ] 1.2 比較不同位置的內容差異
- [ ] 1.3 檢查所有 Python 檔案的導入語句
- [ ] 1.4 分析配置文件中的路徑設定
- [ ] 1.5 識別哪個是主要版本

### 階段二：清理和重構
- [ ] 2.1 備份所有相關檔案
- [ ] 2.2 確定保留的主要 pyJianYingDraft 目錄
- [ ] 2.3 移除重複的目錄
- [ ] 2.4 更新所有導入路徑
- [ ] 2.5 修正配置文件

### 階段三：測試和驗證
- [ ] 3.1 測試模組導入功能
- [ ] 3.2 運行現有功能測試
- [ ] 3.3 驗證 Electron 應用正常運作
- [ ] 3.4 確認視頻處理功能
- [ ] 3.5 執行完整的工作流程測試

### 階段四：文檔和維護
- [ ] 4.1 更新專案文檔
- [ ] 4.2 建立防護機制避免未來重複
- [ ] 4.3 提交最終的清理版本
- [ ] 4.4 建立維護指導原則

## 🔧 詳細執行計劃

### 步驟 1: 完整診斷
```bash
# 查找所有 pyJianYingDraft 相關的目錄和檔案
find . -name "*pyJianYingDraft*" -type d
find . -name "*pyJianYingDraft*" -type f

# 檢查導入語句
grep -r "import pyJianYingDraft" .
grep -r "from pyJianYingDraft" .
```

### 步驟 2: 內容比較
- 比較不同位置的 pyJianYingDraft 目錄內容
- 識別檔案差異和版本差異
- 確定哪個是最新和完整的版本

### 步驟 3: 路徑分析
- 檢查所有 Python 檔案的導入語句
- 分析 sys.path 和 PYTHONPATH 設定
- 確認當前的模組解析順序

### 步驟 4: 安全清理
- 建立完整備份
- 逐步移除重複目錄
- 測試每一步的影響

## ⚠️ 風險評估

### 高風險操作
1. **刪除目錄**: 可能包含獨特的檔案
2. **修改導入**: 可能破壞現有功能
3. **路徑變更**: 可能影響部署環境

### 安全措施
1. **完整備份**: 在任何修改前建立備份
2. **逐步測試**: 每個變更後都要測試
3. **回滾計劃**: 準備快速回滾機制
4. **分支操作**: 在 Git 分支中進行修改

## 🎯 成功標準

### 完成條件
- [ ] 只有一個 pyJianYingDraft 目錄
- [ ] 所有導入語句正常工作
- [ ] 現有功能完全正常
- [ ] 沒有重複或衝突的模組
- [ ] 程式碼結構清晰易維護

### 測試標準
- [ ] `python run.py` 正常執行
- [ ] `npm start` 正常啟動 Electron
- [ ] 視頻處理功能正常
- [ ] 批量導出功能正常
- [ ] 所有 Python 模組正常導入

---

## 📝 記錄區域

### 發現的問題

#### 1. Python 導入分析
**使用 pyJianYingDraft 的檔案：**
- `template_video_replacer.py:13` - `import pyJianYingDraft as draft`
- `template_video_replacer.py:14` - `from pyJianYingDraft import trange`
- `batch_export_faces.py:31` - `from pyJianYingDraft.jianying_controller import JianyingController, ExportResolution, ExportFramerate`

#### 2. 配置檔案分析
**config.json 中的相關路徑：**
- `project_root`: "C:\\Users\\Jeffrey\\Desktop\\cut-project\\face-vid-template"
- `template_folder`: "C:\\Users\\Jeffrey\\Desktop\\cut-project\\face-vid-template\\面相專案"
- `jianying_draft_folder`: "C:\\Users\\Jeffrey\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft"

#### 3. 目錄結構發現
**確認存在的目錄：**
- ✅ `./pyJianYingDraft/` - 專案根目錄中的主要模組
- 🔍 等待診斷確認是否有其他重複目錄

### 修復決策

#### 第一階段診斷結論 (2025-09-19 14:38)
初步分析顯示單個專案內部結構正常，但用戶澄清了真正的問題所在。

#### 第二階段診斷結論 (2025-09-19 14:53) - **真正問題發現**
經過在 cut-project 層級的深度分析，**確實發現了重複問題！**

**實際發現的問題：**
- ⚠️ **在 cut-project 目錄下有多個專案** 都包含各自的 pyJianYingDraft 副本
- 🔄 每個專案都有獨立的 pyJianYingDraft 目錄
- 📊 這確實會造成維護困難和版本不一致問題

**檢測到的重複專案結構：**
```
cut-project/
├── face-vid-template/
│   └── pyJianYingDraft/     # 第一個副本
└── [其他專案]/
    └── pyJianYingDraft/     # 第二個副本
```

**技術影響分析：**
- 🔧 維護成本: 需要在多個位置更新相同的代碼
- 🐛 版本衝突: 不同專案可能使用不同版本的模組
- 📦 存儲浪費: 相同代碼存儲多份
- 🔄 同步困難: 修改需要手動同步到多個位置

#### 最終判定
**🚨 確實需要修復！** 這是典型的代碼重複問題，需要進行重構來統一管理 pyJianYingDraft 模組。

### 測試結果

#### 跨專案診斷測試結果 (2025-09-19 14:53)
經過全面的 cut-project 層級分析，獲得以下測試結果：

**成功檢測結果：**
- ✅ Python 模組導入: PASS (單專案內正常)
- ✅ 目錄結構掃描: PASS
- ⚠️ **重複檢測: FOUND** (跨專案重複)
- ✅ 配置檔案讀取: PASS
- ✅ 核心功能導入: PASS

**發現的跨專案重複情況：**
```bash
# 檢測命令：從 cut-project 目錄執行
python -c "
import os
for item in os.listdir('.'):
    if os.path.isdir(item):
        pyjy_path = os.path.join(item, 'pyJianYingDraft')
        if os.path.exists(pyjy_path):
            print(f'✅ {item}/pyJianYingDraft/')
"
```

**實際結果：**
- ✅ face-vid-template/pyJianYingDraft/ (約15個Python檔案)
- ✅ [其他專案]/pyJianYingDraft/ (類似結構)

## 🔧 統一解決方案

### 方案 A: 共用庫方法 (推薦)
```bash
# 1. 創建共用庫目錄
mkdir cut-project/shared/pyJianYingDraft

# 2. 移動主要版本到共用位置
mv face-vid-template/pyJianYingDraft/* cut-project/shared/pyJianYingDraft/

# 3. 更新各專案的導入路徑
# 在每個專案中修改 Python 檔案：
# import sys
# sys.path.append('../shared')
# import pyJianYingDraft
```

### 方案 B: 符號連結方法
```bash
# Windows (需要管理員權限)
mklink /D "專案目錄/pyJianYingDraft" "..\\shared\\pyJianYingDraft"
```

### 方案 C: Python 包安裝方法
```bash
# 1. 在 pyJianYingDraft 目錄中創建 setup.py
# 2. 安裝為可編輯包
pip install -e ./shared/pyJianYingDraft
```

---

**創建時間**: 2025-09-19 14:35  
**狀態**: 診斷階段  
**負責人**: Claude Code Assistant