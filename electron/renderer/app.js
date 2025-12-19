// 应用状态
const state = {
  isTranslating: false,
  inputFile: '',
  outputFile: ''
};

// DOM元素
const elements = {
  inputFile: document.getElementById('inputFile'),
  outputFile: document.getElementById('outputFile'),
  btnSelectInput: document.getElementById('btnSelectInput'),
  btnSelectOutput: document.getElementById('btnSelectOutput'),
  sourceCol: document.getElementById('sourceCol'),
  targetTH: document.getElementById('targetTH'),
  targetVN: document.getElementById('targetVN'),
  skipExisting: document.getElementById('skipExisting'),
  progressText: document.getElementById('progressText'),
  progressBar: document.getElementById('progressBar'),
  logContainer: document.getElementById('logContainer'),
  btnStart: document.getElementById('btnStart'),
  btnStop: document.getElementById('btnStop'),
  btnClearLog: document.getElementById('btnClearLog')
};

// 初始化
function init() {
  // 绑定事件
  elements.btnSelectInput.addEventListener('click', selectInputFile);
  elements.btnSelectOutput.addEventListener('click', selectOutputFile);
  elements.btnStart.addEventListener('click', startTranslation);
  elements.btnStop.addEventListener('click', stopTranslation);
  elements.btnClearLog.addEventListener('click', clearLog);
  
  // 监听翻译日志
  window.electronAPI.onTranslationLog((message) => {
    addLog(message);
    updateProgressFromLog(message);
  });
  
  addLog('✨ 应用已启动，准备就绪');
}

// 选择输入文件
async function selectInputFile() {
  try {
    const filePath = await window.electronAPI.selectInputFile();
    if (filePath) {
      state.inputFile = filePath;
      elements.inputFile.value = filePath;
      
      // 自动生成输出文件名
      if (!state.outputFile) {
        const outputPath = filePath.replace(/\.csv$/i, '_translated.csv');
        state.outputFile = outputPath;
        elements.outputFile.value = outputPath;
      }
      
      addLog(`📁 已选择输入文件: ${filePath}`);
    }
  } catch (error) {
    showError('选择文件失败', error);
  }
}

// 选择输出文件
async function selectOutputFile() {
  try {
    const defaultPath = state.outputFile || state.inputFile.replace(/\.csv$/i, '_translated.csv');
    const filePath = await window.electronAPI.selectOutputFile(defaultPath);
    if (filePath) {
      state.outputFile = filePath;
      elements.outputFile.value = filePath;
      addLog(`💾 已选择输出文件: ${filePath}`);
    }
  } catch (error) {
    showError('选择输出文件失败', error);
  }
}

// 开始翻译
async function startTranslation() {
  try {
    // 验证输入
    if (!state.inputFile) {
      showError('错误', '请先选择输入文件');
      return;
    }
    
    if (!state.outputFile) {
      showError('错误', '请先选择输出文件');
      return;
    }
    
    // 检查目标语言
    const targetCols = [];
    if (elements.targetTH.checked) targetCols.push('TH');
    if (elements.targetVN.checked) targetCols.push('VN');
    
    if (targetCols.length === 0) {
      showError('错误', '请至少选择一个目标语言');
      return;
    }
    
    // 更新UI状态
    state.isTranslating = true;
    elements.btnStart.disabled = true;
    elements.btnStop.disabled = false;
    elements.progressText.textContent = '⏳ 准备翻译...';
    setProgress(0);
    
    addLog('\n' + '='.repeat(50));
    addLog('▶️ 开始翻译任务');
    addLog('='.repeat(50));
    addLog(`📂 输入: ${state.inputFile}`);
    addLog(`💾 输出: ${state.outputFile}`);
    addLog(`🌐 源语言列: ${elements.sourceCol.value}`);
    addLog(`🎯 目标语言: ${targetCols.join(', ')}`);
    addLog(`⏭️ 跳过已有翻译: ${elements.skipExisting.checked ? '是' : '否'}`);
    addLog('');
    
    // 调用主进程开始翻译
    const options = {
      inputFile: state.inputFile,
      outputFile: state.outputFile,
      sourceCol: elements.sourceCol.value,
      targetCols: targetCols,
      skipExisting: elements.skipExisting.checked
    };
    
    const result = await window.electronAPI.startTranslation(options);
    
    if (result.success) {
      elements.progressText.textContent = '✅ 翻译完成!';
      setProgress(100);
      addLog('\n✅ 翻译任务成功完成!');
      showSuccess('翻译完成', `输出文件:\n${state.outputFile}`);
    }
    
  } catch (error) {
    elements.progressText.textContent = '❌ 翻译失败';
    addLog('\n❌ 翻译任务失败');
    addLog(`错误信息: ${error.message || error}`);
    showError('翻译失败', error.message || error);
  } finally {
    // 恢复UI状态
    state.isTranslating = false;
    elements.btnStart.disabled = false;
    elements.btnStop.disabled = true;
  }
}

// 停止翻译
async function stopTranslation() {
  try {
    addLog('\n⏹️ 正在停止翻译...');
    const result = await window.electronAPI.stopTranslation();
    
    if (result.success) {
      addLog('✅ 翻译已停止');
      elements.progressText.textContent = '⚠️ 已停止';
    }
    
    // 恢复UI状态
    state.isTranslating = false;
    elements.btnStart.disabled = false;
    elements.btnStop.disabled = true;
    
  } catch (error) {
    showError('停止失败', error);
  }
}

// 清空日志
function clearLog() {
  elements.logContainer.innerHTML = '';
  addLog('🗑️ 日志已清空');
}

// 添加日志
function addLog(message, type = 'normal') {
  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  entry.textContent = message;
  elements.logContainer.appendChild(entry);
  
  // 自动滚动到底部
  elements.logContainer.scrollTop = elements.logContainer.scrollHeight;
}

// 从日志更新进度
function updateProgressFromLog(message) {
  // 解析进度信息
  const progressMatch = message.match(/\[(\d+)\/(\d+)\]/);
  if (progressMatch) {
    const current = parseInt(progressMatch[1]);
    const total = parseInt(progressMatch[2]);
    const percent = Math.round((current / total) * 100);
    setProgress(percent);
    elements.progressText.textContent = `⏳ 翻译中: ${current}/${total} (${percent}%)`;
  }
  
  // 检查完成状态
  if (message.includes('翻译完成') || message.includes('translation complete')) {
    setProgress(100);
    elements.progressText.textContent = '✅ 翻译完成!';
  }
}

// 设置进度条
function setProgress(percent) {
  elements.progressBar.style.width = `${percent}%`;
}

// 显示错误
function showError(title, message) {
  addLog(`❌ ${title}: ${message}`, 'error');
  alert(`❌ ${title}\n\n${message}`);
}

// 显示成功
function showSuccess(title, message) {
  addLog(`✅ ${title}: ${message}`, 'success');
  alert(`✅ ${title}\n\n${message}`);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
