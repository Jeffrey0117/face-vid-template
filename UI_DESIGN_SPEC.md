# UI 設計規格書

## 基於 Radix UI 的統一設計系統

---

## 1. 設計風格概述

### 設計理念
- **風格**: 明亮、現代、簡潔 (參考 Fiverr 風格)
- **主題**: Light Mode 為主
- **特點**: 乾淨的白色背景、柔和陰影、圓角元素、清晰的視覺層次

### 設計原則
1. **簡潔性** - 減少視覺噪音，突出核心內容
2. **一致性** - 統一的間距、顏色、字體系統
3. **可訪問性** - 遵循 WCAG 2.1 AA 標準
4. **響應式** - 適配桌面和平板設備

---

## 2. 色彩系統

### 主色調 (Primary)
```css
--primary-50: #EEF2FF;
--primary-100: #E0E7FF;
--primary-200: #C7D2FE;
--primary-300: #A5B4FC;
--primary-400: #818CF8;
--primary-500: #6366F1;  /* 主色 */
--primary-600: #4F46E5;
--primary-700: #4338CA;
--primary-800: #3730A3;
--primary-900: #312E81;
```

### 中性色 (Neutral)
```css
--gray-50: #FAFAFA;     /* 頁面背景 */
--gray-100: #F5F5F5;    /* 卡片懸停背景 */
--gray-200: #E5E5E5;    /* 邊框色 */
--gray-300: #D4D4D4;    /* 禁用邊框 */
--gray-400: #A3A3A3;    /* 輔助文字 */
--gray-500: #737373;    /* 次要文字 */
--gray-600: #525252;    /* 正文文字 */
--gray-700: #404040;    /* 標題文字 */
--gray-800: #262626;    /* 強調標題 */
--gray-900: #171717;    /* 主標題 */
```

### 功能色
```css
--success-500: #22C55E;  /* 成功 */
--success-50: #F0FDF4;
--warning-500: #F59E0B;  /* 警告 */
--warning-50: #FFFBEB;
--error-500: #EF4444;    /* 錯誤 */
--error-50: #FEF2F2;
--info-500: #3B82F6;     /* 信息 */
--info-50: #EFF6FF;
```

### 表面色
```css
--surface-background: #FFFFFF;     /* 主要背景 */
--surface-elevated: #FFFFFF;       /* 卡片背景 */
--surface-overlay: rgba(0,0,0,0.5); /* 遮罩 */
```

---

## 3. 字體系統

### 字體族
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Noto Sans TC', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### 字體大小
```css
--text-xs: 0.75rem;    /* 12px - 標籤、徽章 */
--text-sm: 0.875rem;   /* 14px - 輔助文字 */
--text-base: 1rem;     /* 16px - 正文 */
--text-lg: 1.125rem;   /* 18px - 大正文 */
--text-xl: 1.25rem;    /* 20px - 小標題 */
--text-2xl: 1.5rem;    /* 24px - 標題 */
--text-3xl: 1.875rem;  /* 30px - 大標題 */
--text-4xl: 2.25rem;   /* 36px - 頁面標題 */
```

### 字重
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 行高
```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

---

## 4. 間距系統

### 基礎間距 (4px 基數)
```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

---

## 5. 圓角系統

```css
--radius-none: 0;
--radius-sm: 0.25rem;   /* 4px - 小元素 */
--radius-md: 0.5rem;    /* 8px - 按鈕、輸入框 */
--radius-lg: 0.75rem;   /* 12px - 卡片 */
--radius-xl: 1rem;      /* 16px - 大卡片 */
--radius-2xl: 1.5rem;   /* 24px - 特大卡片 */
--radius-full: 9999px;  /* 圓形 */
```

---

## 6. 陰影系統

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
```

---

## 7. Radix UI 組件規格

### 7.1 Button 按鈕

#### 變體
| 變體 | 背景色 | 文字色 | 邊框 | 用途 |
|------|--------|--------|------|------|
| Primary | `--primary-500` | `#FFFFFF` | 無 | 主要操作 |
| Secondary | `--gray-100` | `--gray-700` | 無 | 次要操作 |
| Outline | 透明 | `--gray-700` | `--gray-300` | 輔助操作 |
| Ghost | 透明 | `--gray-600` | 無 | 低優先級 |
| Destructive | `--error-500` | `#FFFFFF` | 無 | 危險操作 |

#### 尺寸
| 尺寸 | 高度 | 內邊距 | 字體大小 | 圖標大小 |
|------|------|--------|----------|----------|
| sm | 32px | 12px 16px | 14px | 16px |
| md | 40px | 16px 20px | 14px | 18px |
| lg | 48px | 20px 24px | 16px | 20px |

#### 樣式
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  transition: all 150ms ease;
  cursor: pointer;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn:active {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### 7.2 Card 卡片

#### 標準卡片
```css
.card {
  background: var(--surface-elevated);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: all 200ms ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--gray-300);
}
```

#### 推薦卡片 (參考圖片)
```css
.card-recommended {
  background: var(--gray-50);
  border: none;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.card-recommended__label {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--gray-500);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: var(--space-3);
}
```

### 7.3 List Item 列表項目

#### 圖標列表項 (參考圖片)
```css
.list-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background 150ms ease;
}

.list-item:hover {
  background: var(--gray-100);
}

.list-item__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  color: var(--gray-700);
}

.list-item__content {
  flex: 1;
}

.list-item__title {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--gray-900);
}

.list-item__description {
  font-size: var(--text-sm);
  color: var(--gray-500);
}
```

#### 帶背景的動作項 (Keep exploring 樣式)
```css
.action-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  background: var(--gray-100);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: background 150ms ease;
}

.action-item:hover {
  background: var(--gray-200);
}

.action-item__icon {
  width: 20px;
  height: 20px;
  color: var(--gray-700);
}

.action-item__text {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--gray-900);
}
```

### 7.4 Input 輸入框

```css
.input {
  width: 100%;
  height: 40px;
  padding: 0 var(--space-4);
  background: var(--surface-background);
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  color: var(--gray-900);
  transition: all 150ms ease;
}

.input:hover {
  border-color: var(--gray-400);
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-100);
}

.input::placeholder {
  color: var(--gray-400);
}
```

### 7.5 Select 下拉選擇

使用 Radix Select 組件:
```css
.select-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  padding: 0 var(--space-4);
  background: var(--surface-background);
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  color: var(--gray-900);
  cursor: pointer;
}

.select-content {
  background: var(--surface-background);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: var(--space-1);
}

.select-item {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.select-item:hover,
.select-item[data-highlighted] {
  background: var(--gray-100);
}
```

### 7.6 Dialog 對話框

```css
.dialog-overlay {
  background: var(--surface-overlay);
  position: fixed;
  inset: 0;
}

.dialog-content {
  background: var(--surface-background);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--space-6);
  width: 90vw;
  max-width: 500px;
  max-height: 85vh;
}

.dialog-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--gray-900);
  margin-bottom: var(--space-4);
}

.dialog-description {
  font-size: var(--text-base);
  color: var(--gray-600);
  margin-bottom: var(--space-6);
}
```

### 7.7 Toast 通知

```css
.toast {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  background: var(--surface-background);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.toast--success {
  border-left: 4px solid var(--success-500);
}

.toast--error {
  border-left: 4px solid var(--error-500);
}

.toast--warning {
  border-left: 4px solid var(--warning-500);
}
```

### 7.8 Tabs 標籤頁

```css
.tabs-list {
  display: flex;
  border-bottom: 1px solid var(--gray-200);
  gap: var(--space-1);
}

.tabs-trigger {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--gray-500);
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 150ms ease;
}

.tabs-trigger:hover {
  color: var(--gray-700);
}

.tabs-trigger[data-state="active"] {
  color: var(--primary-600);
  border-bottom-color: var(--primary-600);
}

.tabs-content {
  padding: var(--space-6) 0;
}
```

### 7.9 Toggle / Switch

```css
.switch-root {
  width: 42px;
  height: 24px;
  background: var(--gray-300);
  border-radius: var(--radius-full);
  position: relative;
  cursor: pointer;
  transition: background 150ms ease;
}

.switch-root[data-state="checked"] {
  background: var(--primary-500);
}

.switch-thumb {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm);
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 150ms ease;
}

.switch-root[data-state="checked"] .switch-thumb {
  transform: translateX(18px);
}
```

### 7.10 Progress 進度條

```css
.progress-root {
  height: 8px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-indicator {
  height: 100%;
  background: var(--primary-500);
  border-radius: var(--radius-full);
  transition: width 300ms ease;
}
```

### 7.11 Badge 徽章

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  border-radius: var(--radius-sm);
}

.badge--default {
  background: var(--gray-100);
  color: var(--gray-700);
}

.badge--primary {
  background: var(--primary-100);
  color: var(--primary-700);
}

.badge--success {
  background: var(--success-50);
  color: var(--success-500);
}

.badge--warning {
  background: var(--warning-50);
  color: var(--warning-500);
}

.badge--error {
  background: var(--error-50);
  color: var(--error-500);
}
```

---

## 8. 佈局規格

### 8.1 頁面結構
```
┌─────────────────────────────────────────────┐
│  Header (64px)                              │
├─────────┬───────────────────────────────────┤
│         │                                   │
│ Sidebar │    Main Content                   │
│ (240px) │    (padding: 24px-32px)           │
│         │                                   │
│         │                                   │
├─────────┴───────────────────────────────────┤
│  Footer (可選, 48px)                        │
└─────────────────────────────────────────────┘
```

### 8.2 Header
```css
.header {
  height: 64px;
  background: var(--surface-background);
  border-bottom: 1px solid var(--gray-200);
  padding: 0 var(--space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}
```

### 8.3 Sidebar
```css
.sidebar {
  width: 240px;
  background: var(--surface-background);
  border-right: 1px solid var(--gray-200);
  padding: var(--space-4);
  height: calc(100vh - 64px);
  position: sticky;
  top: 64px;
}

.sidebar--collapsed {
  width: 64px;
}
```

### 8.4 Main Content
```css
.main-content {
  flex: 1;
  padding: var(--space-8);
  background: var(--gray-50);
  min-height: calc(100vh - 64px);
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
}
```

---

## 9. 響應式斷點

```css
/* Mobile First */
--breakpoint-sm: 640px;   /* 小型平板 */
--breakpoint-md: 768px;   /* 平板 */
--breakpoint-lg: 1024px;  /* 小型桌面 */
--breakpoint-xl: 1280px;  /* 大型桌面 */
--breakpoint-2xl: 1536px; /* 超大螢幕 */
```

---

## 10. 動畫與過渡

### 過渡時間
```css
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
```

### 緩動函數
```css
--ease-default: cubic-bezier(0.4, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 標準動畫
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

---

## 11. 圖標規格

### 推薦圖標庫
- **Lucide Icons** (推薦) - 輕量、一致
- **Radix Icons** - 與 Radix UI 原生搭配

### 圖標尺寸
| 名稱 | 尺寸 | 用途 |
|------|------|------|
| xs | 12px | 徽章內圖標 |
| sm | 16px | 按鈕、列表內圖標 |
| md | 20px | 標準圖標 |
| lg | 24px | 標題圖標 |
| xl | 32px | 功能圖標 |

### 圖標顏色
- 默認: `var(--gray-600)`
- 懸停: `var(--gray-900)`
- 主要: `var(--primary-500)`
- 禁用: `var(--gray-400)`

---

## 12. 實施檢查清單

### Phase 1: 基礎設置
- [ ] 安裝 Radix UI 核心組件
- [ ] 創建 CSS 變數文件
- [ ] 設置字體引入
- [ ] 配置 Tailwind (如使用)

### Phase 2: 基礎組件
- [ ] Button 組件
- [ ] Input 組件
- [ ] Card 組件
- [ ] Badge 組件

### Phase 3: 複合組件
- [ ] Dialog 組件
- [ ] Select 組件
- [ ] Tabs 組件
- [ ] Toast 組件

### Phase 4: 佈局組件
- [ ] Header 組件
- [ ] Sidebar 組件
- [ ] PageContainer 組件

### Phase 5: 頁面改造
- [ ] app.html 改造
- [ ] translate_editor.html 改造
- [ ] template-editor.html 改造
- [ ] index.html 改造

---

## 13. Radix UI 依賴清單

```bash
# 核心
npm install @radix-ui/react-slot

# 組件
npm install @radix-ui/react-dialog
npm install @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select
npm install @radix-ui/react-tabs
npm install @radix-ui/react-toast
npm install @radix-ui/react-switch
npm install @radix-ui/react-progress
npm install @radix-ui/react-tooltip
npm install @radix-ui/react-popover
npm install @radix-ui/react-checkbox
npm install @radix-ui/react-label

# 圖標 (可選)
npm install @radix-ui/react-icons
# 或
npm install lucide-react
```

---

## 14. 文件結構建議

```
src/
├── styles/
│   ├── variables.css      # CSS 變數
│   ├── base.css          # 基礎樣式
│   ├── components.css    # 組件樣式
│   └── utilities.css     # 工具類
├── components/
│   ├── ui/
│   │   ├── Button.vue
│   │   ├── Card.vue
│   │   ├── Input.vue
│   │   ├── Select.vue
│   │   ├── Dialog.vue
│   │   ├── Tabs.vue
│   │   ├── Toast.vue
│   │   ├── Badge.vue
│   │   └── Progress.vue
│   └── layout/
│       ├── Header.vue
│       ├── Sidebar.vue
│       └── PageContainer.vue
└── pages/
    ├── App.vue
    ├── TranslateEditor.vue
    └── TemplateEditor.vue
```

---

## 附錄 A: 設計對比 (Before vs After)

### 現有設計問題
1. 暗色主題不適合所有用途
2. 樣式分散在各 HTML 文件中
3. 缺乏統一的設計語言
4. 組件樣式不一致

### 新設計優勢
1. 明亮、專業的視覺風格
2. 集中的設計系統
3. Radix UI 提供的可訪問性
4. 一致的組件庫

---

## 附錄 B: 參考資源

- [Radix UI 官方文檔](https://www.radix-ui.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide Icons](https://lucide.dev/)
- [Inter Font](https://rsms.me/inter/)
