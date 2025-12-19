const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let pythonProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    frame: true,
    backgroundColor: '#f5f5f5',
    show: false
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 开发模式下打开开发者工具
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
    // 关闭Python进程
    if (pythonProcess) {
      pythonProcess.kill();
    }
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 选择输入文件
ipcMain.handle('select-input-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// 选择输出文件
ipcMain.handle('select-output-file', async (event, defaultPath) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultPath,
    filters: [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  
  if (!result.canceled) {
    return result.filePath;
  }
  return null;
});

// 开始翻译
ipcMain.handle('start-translation', async (event, options) => {
  return new Promise((resolve, reject) => {
    const { inputFile, outputFile, sourceCol, targetCols, skipExisting } = options;
    
    // 构建Python命令
    const pythonScript = path.join(__dirname, '..', 'translate_csv.py');
    const args = [
      pythonScript,
      inputFile,
      '-o', outputFile,
      '-s', sourceCol,
      '-t', ...targetCols
    ];
    
    if (!skipExisting) {
      args.push('--overwrite');
    }
    
    // 启动Python进程
    pythonProcess = spawn('python', args);
    
    let outputData = '';
    let errorData = '';
    
    pythonProcess.stdout.on('data', (data) => {
      const text = data.toString();
      outputData += text;
      // 发送日志到渲染进程
      event.sender.send('translation-log', text);
    });
    
    pythonProcess.stderr.on('data', (data) => {
      const text = data.toString();
      errorData += text;
      event.sender.send('translation-log', `错误: ${text}`);
    });
    
    pythonProcess.on('close', (code) => {
      pythonProcess = null;
      if (code === 0) {
        resolve({ success: true, message: '翻译完成' });
      } else {
        reject({ success: false, message: `进程退出代码: ${code}`, error: errorData });
      }
    });
    
    pythonProcess.on('error', (err) => {
      pythonProcess = null;
      reject({ success: false, message: '启动Python进程失败', error: err.message });
    });
  });
});

// 停止翻译
ipcMain.handle('stop-translation', async () => {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
    return { success: true, message: '翻译已停止' };
  }
  return { success: false, message: '没有正在运行的翻译任务' };
});

// 检查文件是否存在
ipcMain.handle('check-file-exists', async (event, filePath) => {
  return fs.existsSync(filePath);
});
