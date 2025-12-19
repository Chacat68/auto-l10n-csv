const { contextBridge, ipcRenderer } = require('electron');

// 向渲染进程暴露安全的API
contextBridge.exposeInMainWorld('electronAPI', {
  // 文件选择
  selectInputFile: () => ipcRenderer.invoke('select-input-file'),
  selectOutputFile: (defaultPath) => ipcRenderer.invoke('select-output-file', defaultPath),
  
  // 翻译操作
  startTranslation: (options) => ipcRenderer.invoke('start-translation', options),
  stopTranslation: () => ipcRenderer.invoke('stop-translation'),
  
  // 文件检查
  checkFileExists: (filePath) => ipcRenderer.invoke('check-file-exists', filePath),
  
  // 日志监听
  onTranslationLog: (callback) => {
    ipcRenderer.on('translation-log', (event, message) => callback(message));
  },
  
  // 移除监听器
  removeTranslationLogListener: () => {
    ipcRenderer.removeAllListeners('translation-log');
  }
});
