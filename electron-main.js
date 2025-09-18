const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// 保持對窗口對象的全局引用，如果不這樣做，當 JavaScript 對象被垃圾回收時，窗口會被自動關閉。
let mainWindow;

function createWindow() {
  // 創建瀏覽器窗口
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: false,
      webSecurity: false
    },
    // icon: path.join(__dirname, 'assets/icon.ico'), // 可選的應用圖標
    title: '剪映助手 - 模板工作流',
    minWidth: 800,
    minHeight: 600,
    show: false // 先隱藏窗口，載入完成後再顯示
  });

  // 載入應用的 index.html
  mainWindow.loadFile('index.html');

  // 當頁面準備好時顯示窗口
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 開發環境下打開 DevTools
  if (process.env.NODE_ENV === 'development' || process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  // 當窗口被關閉時，清除對它的引用
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Electron 會在初始化後並準備創建瀏覽器窗口時，調用這個函數
app.whenReady().then(createWindow);

// 當全部窗口關閉時退出
app.on('window-all-closed', () => {
  // 在 macOS 上，除非用戶用 Cmd + Q 確定地退出，否則絕大部分應用會保持激活
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // 在 macOS 上，當點擊 dock 圖標並且該應用沒有打開的窗口時，重新創建一個窗口
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC 處理程序

// 處理一鍵執行
ipcMain.handle('execute-main-process', async () => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['run.py'], {
      cwd: __dirname,
      stdio: 'pipe',
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8'
      }
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      const chunk = data.toString();
      output += chunk;
      // 發送即時輸出到渲染進程
      mainWindow.webContents.send('process-output', chunk);
    });

    pythonProcess.stderr.on('data', (data) => {
      const chunk = data.toString();
      errorOutput += chunk;
      mainWindow.webContents.send('process-error', chunk);
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output });
      } else {
        reject({ success: false, error: errorOutput, code });
      }
    });

    pythonProcess.on('error', (error) => {
      reject({ success: false, error: error.message });
    });
  });
});

// 處理配置路徑設置
ipcMain.handle('setup-paths', async () => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['setup_paths.py'], {
      cwd: __dirname,
      stdio: 'pipe',
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8'
      }
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      const chunk = data.toString();
      output += chunk;
      mainWindow.webContents.send('setup-output', chunk);
    });

    pythonProcess.stderr.on('data', (data) => {
      const chunk = data.toString();
      errorOutput += chunk;
      mainWindow.webContents.send('setup-error', chunk);
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output });
      } else {
        reject({ success: false, error: errorOutput, code });
      }
    });
  });
});

// 處理批量導出面相
ipcMain.handle('export-faces', async () => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['batch_export_faces.py'], {
      cwd: __dirname,
      stdio: 'pipe',
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8'
      }
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      const chunk = data.toString();
      output += chunk;
      mainWindow.webContents.send('process-output', chunk);
    });

    pythonProcess.stderr.on('data', (data) => {
      const chunk = data.toString();
      errorOutput += chunk;
      mainWindow.webContents.send('process-error', chunk);
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output });
      } else {
        reject({ success: false, error: errorOutput, code });
      }
    });

    pythonProcess.on('error', (error) => {
      reject({ success: false, error: error.message });
    });
  });
});

// 處理文件夾選擇
ipcMain.handle('select-folder', async (event, title) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: title || '選擇資料夾',
    properties: ['openDirectory']
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// 讀取配置文件
ipcMain.handle('load-config', async () => {
  try {
    const configPath = path.join(__dirname, 'config.json');
    if (fs.existsSync(configPath)) {
      const configData = fs.readFileSync(configPath, 'utf8');
      return JSON.parse(configData);
    }
    return null;
  } catch (error) {
    throw new Error(`載入配置失敗: ${error.message}`);
  }
});

// 保存配置文件
ipcMain.handle('save-config', async (event, config) => {
  try {
    const configPath = path.join(__dirname, 'config.json');
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');
    return { success: true };
  } catch (error) {
    throw new Error(`保存配置失敗: ${error.message}`);
  }
});

// 檢查文件是否存在
ipcMain.handle('check-file-exists', async (event, filePath) => {
  return fs.existsSync(filePath);
});

// 獲取目錄中的影片文件
ipcMain.handle('get-video-files', async (event, dirPath) => {
  try {
    if (!fs.existsSync(dirPath)) {
      return [];
    }
    
    const files = fs.readdirSync(dirPath);
    const videoExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'];
    
    return files.filter(file => {
      const ext = path.extname(file).toLowerCase();
      return videoExtensions.includes(ext);
    }).map(file => ({
      name: file,
      path: path.join(dirPath, file),
      size: fs.statSync(path.join(dirPath, file)).size
    }));
  } catch (error) {
    throw new Error(`讀取影片文件失敗: ${error.message}`);
  }
});