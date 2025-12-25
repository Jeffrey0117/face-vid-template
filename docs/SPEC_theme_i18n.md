# Theme & i18n MVP Specification

## Overview
為 AutoReels 添加淺色模式切換和中英文切換功能。

---

## 1. Theme System

### 1.1 CSS Variables Structure
```css
/* 在 :root 定義深色主題 (預設) */
:root {
  --bg-primary: #030303;
  --bg-card: #111111;
  --text-primary: #ffffff;
  /* ... existing dark theme */
}

/* 淺色主題 */
[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #fafafa;
  --bg-card: #f4f4f5;
  --bg-card-hover: #e4e4e7;
  --text-primary: #09090b;
  --text-secondary: #52525b;
  --text-muted: #a1a1aa;
  --border-default: #e4e4e7;
  --border-hover: #d4d4d8;
}
```

### 1.2 Theme Toggle
- 位置：Header 右側
- 圖標：太陽/月亮
- 儲存：localStorage `theme`
- 預設：跟隨系統 `prefers-color-scheme`

### 1.3 Implementation
```javascript
// 初始化主題
const initTheme = () => {
  const saved = localStorage.getItem('theme');
  const system = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  document.documentElement.dataset.theme = saved || system;
};

// 切換主題
const toggleTheme = () => {
  const current = document.documentElement.dataset.theme;
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('theme', next);
};
```

---

## 2. i18n System

### 2.1 Translation Structure
```javascript
const i18n = {
  zh: {
    nav: {
      home: '首頁',
      workflow: '工作流',
      igDownload: 'IG下載',
      ytDownload: 'YT下載',
      settings: '設定'
    },
    workflow: {
      faceProject: '面相專案',
      translateProject: '翻譯專案',
      startExecute: '開始執行',
      executing: '執行中...',
      videoFolder: '影片資料夾',
      draftPath: '剪映草稿路徑',
      select: '選擇',
      waiting: '等待執行...',
      totalVideos: '總影片',
      processed: '已處理',
      processing: '處理中',
      errors: '錯誤',
      executionLog: '執行日誌',
      clear: '清除'
    },
    download: {
      title: 'IG Reels 下載',
      subtitle: '批次下載 Instagram Reels 影片',
      inputUrl: '輸入網址',
      placeholder: '貼上 Instagram Reel 網址（每行一個）...',
      addToQueue: '加入佇列',
      startDownload: '開始下載',
      stop: '停止',
      queue: '佇列',
      history: '歷史',
      settings: '設定',
      delete: '刪除',
      retry: '重試',
      waiting: '等待中',
      downloading: '下載中',
      completed: '完成',
      failed: '失敗'
    },
    youtube: {
      title: 'YouTube 下載',
      subtitle: '使用 yt-dlp 下載 YouTube 影片',
      parse: '解析',
      parsing: '解析中...',
      quality: '畫質',
      bestQuality: '最高畫質',
      audioOnly: '僅下載音訊 (MP3)',
      startDownload: '開始下載',
      downloading: '下載中...',
      speed: '下載速度',
      eta: '預估剩餘時間',
      fileSize: '檔案大小',
      historyTab: '歷史紀錄',
      filesTab: '已下載檔案'
    },
    settings: {
      title: '設定',
      subtitle: '配置系統路徑和偏好設定',
      pathConfig: '路徑配置',
      projectRoot: '專案根目錄',
      theme: '主題',
      dark: '深色',
      light: '淺色',
      language: '語言',
      chinese: '繁體中文',
      english: 'English'
    },
    common: {
      loading: '載入中...',
      error: '錯誤',
      success: '成功',
      cancel: '取消',
      confirm: '確認',
      save: '儲存'
    }
  },
  en: {
    nav: {
      home: 'Home',
      workflow: 'Workflow',
      igDownload: 'IG Download',
      ytDownload: 'YT Download',
      settings: 'Settings'
    },
    workflow: {
      faceProject: 'Face Project',
      translateProject: 'Translate Project',
      startExecute: 'Start',
      executing: 'Running...',
      videoFolder: 'Video Folder',
      draftPath: 'Draft Path',
      select: 'Select',
      waiting: 'Waiting...',
      totalVideos: 'Total',
      processed: 'Done',
      processing: 'Processing',
      errors: 'Errors',
      executionLog: 'Execution Log',
      clear: 'Clear'
    },
    download: {
      title: 'IG Reels Download',
      subtitle: 'Batch download Instagram Reels',
      inputUrl: 'Input URL',
      placeholder: 'Paste Instagram Reel URLs (one per line)...',
      addToQueue: 'Add to Queue',
      startDownload: 'Start',
      stop: 'Stop',
      queue: 'Queue',
      history: 'History',
      settings: 'Settings',
      delete: 'Delete',
      retry: 'Retry',
      waiting: 'Waiting',
      downloading: 'Downloading',
      completed: 'Done',
      failed: 'Failed'
    },
    youtube: {
      title: 'YouTube Download',
      subtitle: 'Download YouTube videos with yt-dlp',
      parse: 'Parse',
      parsing: 'Parsing...',
      quality: 'Quality',
      bestQuality: 'Best',
      audioOnly: 'Audio only (MP3)',
      startDownload: 'Download',
      downloading: 'Downloading...',
      speed: 'Speed',
      eta: 'ETA',
      fileSize: 'Size',
      historyTab: 'History',
      filesTab: 'Files'
    },
    settings: {
      title: 'Settings',
      subtitle: 'Configure paths and preferences',
      pathConfig: 'Path Configuration',
      projectRoot: 'Project Root',
      theme: 'Theme',
      dark: 'Dark',
      light: 'Light',
      language: 'Language',
      chinese: '繁體中文',
      english: 'English'
    },
    common: {
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      cancel: 'Cancel',
      confirm: 'Confirm',
      save: 'Save'
    }
  }
};
```

### 2.2 i18n Implementation
```javascript
// 初始化語言
const initLocale = () => {
  const saved = localStorage.getItem('locale');
  return saved || 'zh';
};

// 取得翻譯
const t = (key) => {
  const keys = key.split('.');
  let result = i18n[currentLocale.value];
  for (const k of keys) {
    result = result?.[k];
  }
  return result || key;
};

// 切換語言
const setLocale = (locale) => {
  currentLocale.value = locale;
  localStorage.setItem('locale', locale);
};
```

### 2.3 Template Usage
```html
<!-- 使用 t() 函數 -->
<h1>{{ t('workflow.faceProject') }}</h1>
<button>{{ t('workflow.startExecute') }}</button>
```

---

## 3. UI Components

### 3.1 Theme Toggle Button (Header)
```html
<button class="theme-toggle" @click="toggleTheme">
  <i :data-lucide="theme === 'dark' ? 'sun' : 'moon'"></i>
</button>
```

### 3.2 Language Selector (Header)
```html
<button class="lang-toggle" @click="toggleLocale">
  {{ currentLocale === 'zh' ? 'EN' : '中' }}
</button>
```

### 3.3 Header Layout
```
[Logo: AutoReels] .............. [🌙/☀️] [EN/中]
```

---

## 4. File Changes

| File | Changes |
|------|---------|
| `styles/design-system.css` | 添加 `[data-theme="light"]` 變數 |
| `app.html` | 添加 i18n 對象、theme/locale 切換、更新所有文字為 `{{ t('key') }}` |
| `autoreels.html` | 添加 theme 支援、語言切換 |

---

## 5. localStorage Keys

| Key | Values | Default |
|-----|--------|---------|
| `theme` | `dark` / `light` | system preference |
| `locale` | `zh` / `en` | `zh` |

---

## 6. Agent Tasks

### Agent 1: Light Theme CSS
- 在 design-system.css 添加 `[data-theme="light"]` 區塊
- 定義所有淺色變數

### Agent 2: Theme Toggle
- app.html 添加 theme toggle 按鈕到 header
- 實現 initTheme、toggleTheme 函數
- 綁定 localStorage

### Agent 3: i18n System + Chinese
- app.html 添加 i18n 對象 (zh 部分)
- 實現 t() 函數、initLocale、setLocale
- 添加語言切換按鈕

### Agent 4: English Translations
- 補充 i18n.en 對象
- 更新所有 template 文字為 {{ t('key') }}

---

## 7. MVP Scope

### In Scope
- [x] 深色/淺色切換
- [x] 中/英文切換
- [x] localStorage 持久化
- [x] Header 切換按鈕

### Out of Scope
- [ ] 更多語言
- [ ] 自動偵測瀏覽器語言
- [ ] 動畫過渡效果
