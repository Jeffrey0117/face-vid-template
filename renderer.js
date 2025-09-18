const { ipcRenderer } = require('electron');

// DOM 元素
const elements = {
    // 按鈕
    executeBtn: document.getElementById('executeBtn'),
    executeBtnText: document.getElementById('executeBtnText'),
    setupBtn: document.getElementById('setupBtn'),
    configBtn: document.getElementById('configBtn'),
    clearLogBtn: document.getElementById('clearLogBtn'),
    
    // 狀態指示器
    statusIndicator: document.getElementById('statusIndicator'),
    statusText: document.getElementById('statusText'),
    
    // 配置輸入
    videoFolder: document.getElementById('videoFolder'),
    draftFolder: document.getElementById('draftFolder'),
    selectVideoFolder: document.getElementById('selectVideoFolder'),
    selectDraftFolder: document.getElementById('selectDraftFolder'),
    
    // 進度相關
    progressBar: document.getElementById('progressBar'),
    progressText: document.getElementById('progressText'),
    progressPercent: document.getElementById('progressPercent'),
    
    // 統計數據
    videoCount: document.getElementById('videoCount'),
    processedCount: document.getElementById('processedCount'),
    successCount: document.getElementById('successCount'),
    errorCount: document.getElementById('errorCount'),
    
    // 日誌
    logOutput: document.getElementById('logOutput'),
    
    // 模態框
    configModal: document.getElementById('configModal'),
    closeConfigModal: document.getElementById('closeConfigModal'),
    configForm: document.getElementById('configForm'),
    cancelConfig: document.getElementById('cancelConfig'),
    
    // 配置表單
    configProjectRoot: document.getElementById('configProjectRoot'),
    configTemplateFolder: document.getElementById('configTemplateFolder'),
    configVideoFolder: document.getElementById('configVideoFolder'),
    configDraftFolder: document.getElementById('configDraftFolder')
};

// 應用狀態
let appState = {
    isExecuting: false,
    currentProgress: 0,
    config: null,
    stats: {
        videoCount: 0,
        processedCount: 0,
        successCount: 0,
        errorCount: 0
    }
};

// 初始化應用
async function initializeApp() {
    try {
        // 載入配置
        await loadConfiguration();
        
        // 綁定事件監聽器
        bindEventListeners();
        
        // 設置 IPC 監聽器
        setupIpcListeners();
        
        addLog('系統', '剪映助手初始化完成', 'info');
        updateStatus('idle', '就緒');
        
    } catch (error) {
        addLog('錯誤', `初始化失敗: ${error.message}`, 'error');
        updateStatus('error', '初始化失敗');
    }
}

// 載入配置
async function loadConfiguration() {
    try {
        const config = await ipcRenderer.invoke('load-config');
        if (config) {
            appState.config = config;
            updateConfigDisplay(config);
            addLog('系統', '配置文件載入成功', 'success');
        } else {
            addLog('警告', '未找到配置文件，請先進行路徑設置', 'warning');
        }
    } catch (error) {
        addLog('錯誤', `載入配置失敗: ${error.message}`, 'error');
    }
}

// 更新配置顯示
function updateConfigDisplay(config) {
    elements.videoFolder.value = config.videos_raw_folder || '';
    elements.draftFolder.value = config.jianying_draft_folder || '';
    
    // 更新配置表單
    elements.configProjectRoot.value = config.project_root || '';
    elements.configTemplateFolder.value = config.template_folder || '';
    elements.configVideoFolder.value = config.videos_raw_folder || '';
    elements.configDraftFolder.value = config.jianying_draft_folder || '';
}

// 綁定事件監聽器
function bindEventListeners() {
    // 主要操作按鈕
    elements.executeBtn.addEventListener('click', handleExecute);
    elements.setupBtn.addEventListener('click', handleSetupPaths);
    elements.configBtn.addEventListener('click', showConfigModal);
    
    // 其他功能按鈕
    const exportFacesBtn = document.querySelector('.btn-feature');
    if (exportFacesBtn) {
        exportFacesBtn.addEventListener('click', handleExportFaces);
    }
    
    // 資料夾選擇
    elements.selectVideoFolder.addEventListener('click', () => selectFolder('video'));
    elements.selectDraftFolder.addEventListener('click', () => selectFolder('draft'));
    
    // 日誌控制
    elements.clearLogBtn.addEventListener('click', clearLog);
    
    // 模態框控制
    elements.closeConfigModal.addEventListener('click', hideConfigModal);
    elements.cancelConfig.addEventListener('click', hideConfigModal);
    elements.configForm.addEventListener('submit', handleConfigSave);
    
    // 點擊模態框背景關閉
    elements.configModal.addEventListener('click', (e) => {
        if (e.target === elements.configModal) {
            hideConfigModal();
        }
    });
}

// 設置 IPC 監聽器
function setupIpcListeners() {
    // 處理進程輸出
    ipcRenderer.on('process-output', (event, data) => {
        addLog('執行', data.trim(), 'info');
        parseProgressFromOutput(data);
    });
    
    // 處理進程錯誤
    ipcRenderer.on('process-error', (event, data) => {
        addLog('錯誤', data.trim(), 'error');
        appState.stats.errorCount++;
        updateStats();
    });
    
    // 處理設置輸出
    ipcRenderer.on('setup-output', (event, data) => {
        addLog('設置', data.trim(), 'info');
    });
    
    // 處理設置錯誤
    ipcRenderer.on('setup-error', (event, data) => {
        addLog('設置錯誤', data.trim(), 'error');
    });
}

// 處理執行按鈕點擊
async function handleExecute() {
    if (appState.isExecuting) {
        // TODO: 實現取消功能
        return;
    }
    
    if (!appState.config) {
        addLog('錯誤', '請先進行配置設置', 'error');
        return;
    }
    
    try {
        setExecutionState(true);
        updateStatus('running', '正在執行...');
        resetStats();
        
        addLog('系統', '開始執行主要處理流程...', 'info');
        
        const result = await ipcRenderer.invoke('execute-main-process');
        
        if (result.success) {
            addLog('成功', '處理完成！', 'success');
            updateStatus('success', '執行完成');
            updateProgress(100, '處理完成');
        }
        
    } catch (error) {
        addLog('錯誤', `執行失敗: ${error.error || error.message}`, 'error');
        updateStatus('error', '執行失敗');
    } finally {
        setExecutionState(false);
    }
}

// 處理路徑設置
async function handleSetupPaths() {
    try {
        updateStatus('running', '正在設置路徑...');
        addLog('系統', '開始自動路徑設置...', 'info');
        
        const result = await ipcRenderer.invoke('setup-paths');
        
        if (result.success) {
            addLog('成功', '路徑設置完成', 'success');
            updateStatus('success', '設置完成');
            
            // 重新載入配置
            await loadConfiguration();
        }
        
    } catch (error) {
        addLog('錯誤', `路徑設置失敗: ${error.error || error.message}`, 'error');
        updateStatus('error', '設置失敗');
    }
}

// 資料夾選擇
async function selectFolder(type) {
    try {
        const title = type === 'video' ? '選擇影片資料夾' : '選擇剪映草稿資料夾';
        const folderPath = await ipcRenderer.invoke('select-folder', title);
        
        if (folderPath) {
            if (type === 'video') {
                elements.videoFolder.value = folderPath;
                // 更新影片數量統計
                updateVideoCount(folderPath);
            } else {
                elements.draftFolder.value = folderPath;
            }
            
            addLog('系統', `已選擇${title}: ${folderPath}`, 'info');
        }
        
    } catch (error) {
        addLog('錯誤', `選擇資料夾失敗: ${error.message}`, 'error');
    }
}

// 更新影片數量
async function updateVideoCount(folderPath) {
    try {
        const videoFiles = await ipcRenderer.invoke('get-video-files', folderPath);
        appState.stats.videoCount = videoFiles.length;
        updateStats();
        
        if (videoFiles.length > 0) {
            addLog('信息', `找到 ${videoFiles.length} 個影片檔案`, 'info');
        } else {
            addLog('警告', '該資料夾中沒有找到影片檔案', 'warning');
        }
        
    } catch (error) {
        addLog('錯誤', `讀取影片檔案失敗: ${error.message}`, 'error');
    }
}

// 顯示配置模態框
function showConfigModal() {
    elements.configModal.classList.remove('hidden');
    elements.configModal.classList.add('flex');
}

// 隱藏配置模態框
function hideConfigModal() {
    elements.configModal.classList.add('hidden');
    elements.configModal.classList.remove('flex');
}

// 處理配置保存
async function handleConfigSave(e) {
    e.preventDefault();
    
    try {
        const config = {
            project_root: elements.configProjectRoot.value,
            template_folder: elements.configTemplateFolder.value,
            videos_raw_folder: elements.configVideoFolder.value,
            jianying_draft_folder: elements.configDraftFolder.value,
            username: appState.config?.username || 'User'
        };
        
        await ipcRenderer.invoke('save-config', config);
        
        appState.config = config;
        updateConfigDisplay(config);
        hideConfigModal();
        
        addLog('成功', '配置已保存', 'success');
        
    } catch (error) {
        addLog('錯誤', `保存配置失敗: ${error.message}`, 'error');
    }
}

// 設置執行狀態
function setExecutionState(isExecuting) {
    appState.isExecuting = isExecuting;
    
    elements.executeBtn.disabled = isExecuting;
    elements.setupBtn.disabled = isExecuting;
    
    if (isExecuting) {
        elements.executeBtnText.textContent = '執行中...';
        elements.executeBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        elements.executeBtnText.textContent = '開始執行';
        elements.executeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

// 更新狀態指示器
function updateStatus(status, text) {
    elements.statusIndicator.className = `status-indicator status-${status}`;
    elements.statusText.textContent = text;
}

// 更新進度條
function updateProgress(percent, text = '') {
    appState.currentProgress = percent;
    elements.progressBar.style.width = `${percent}%`;
    elements.progressPercent.textContent = `${Math.round(percent)}%`;
    
    if (text) {
        elements.progressText.textContent = text;
    }
}

// 從輸出解析進度
function parseProgressFromOutput(output) {
    // 嘗試解析進度信息
    const progressMatch = output.match(/(\d+)\/(\d+)/);
    if (progressMatch) {
        const current = parseInt(progressMatch[1]);
        const total = parseInt(progressMatch[2]);
        const percent = (current / total) * 100;
        
        updateProgress(percent, `處理 ${current}/${total} 個檔案`);
        appState.stats.processedCount = current;
        updateStats();
    }
    
    // 檢查成功完成的標記
    if (output.includes('✅') || output.includes('成功')) {
        appState.stats.successCount++;
        updateStats();
    }
}

// 更新統計數據
function updateStats() {
    elements.videoCount.textContent = appState.stats.videoCount;
    elements.processedCount.textContent = appState.stats.processedCount;
    elements.successCount.textContent = appState.stats.successCount;
    elements.errorCount.textContent = appState.stats.errorCount;
}

// 重置統計數據
function resetStats() {
    appState.stats.processedCount = 0;
    appState.stats.successCount = 0;
    appState.stats.errorCount = 0;
    updateStats();
    updateProgress(0, '準備開始...');
}

// 添加日誌
function addLog(type, message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString('zh-TW', { hour12: false });
    const logEntry = document.createElement('div');
    
    let colorClass;
    switch (level) {
        case 'error':
            colorClass = 'text-red-400';
            break;
        case 'warning':
            colorClass = 'text-yellow-400';
            break;
        case 'success':
            colorClass = 'text-green-400';
            break;
        default:
            colorClass = 'text-gray-300';
    }
    
    logEntry.className = `${colorClass} mb-1`;
    logEntry.innerHTML = `<span class="text-gray-500">[${timestamp}]</span> <span class="text-blue-300">[${type}]</span> ${message}`;
    
    elements.logOutput.appendChild(logEntry);
    elements.logOutput.scrollTop = elements.logOutput.scrollHeight;
    
    // 限制日誌條目數量（保持性能）
    if (elements.logOutput.children.length > 1000) {
        elements.logOutput.removeChild(elements.logOutput.firstChild);
    }
}

// 清除日誌
function clearLog() {
    elements.logOutput.innerHTML = '<div class="text-gray-400">[系統] 日誌已清除</div>';
}

// 初始化應用
document.addEventListener('DOMContentLoaded', initializeApp);

// 防止拖拽文件到應用程序
document.addEventListener('dragover', (e) => {
    e.preventDefault();
    return false;
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
    return false;
});