# auto-l10n-csv

🌍 自动翻译CSV文件中的多语言列（TH泰语、VN越南语）

## ✨ 功能特点

### 核心功能
- ✅ 自动翻译CSV文件中的指定列
- ✅ 支持从中文翻译到泰语(TH)和越南语(VN)
- ✅ 智能跳过已有翻译的单元格
- ✅ 多翻译引擎支持（Google + MyMemory备用）
- ✅ 支持HTML标签保留
- ✅ 翻译结果缓存，避免重复翻译
- ✅ 智能重试机制和错误恢复

### 界面选择
- 🖥️ **Electron桌面应用** (推荐) - 现代化跨平台桌面应用
- 🐍 **Python GUI** - 基于CustomTkinter的轻量级界面
- ⌨️ **命令行工具** - 适合批处理和自动化

## 🚀 快速开始

### 方式一：Electron 桌面应用（推荐）

现代化的跨平台桌面应用，无需Python环境！

```bash
# 1. 安装Node.js依赖
npm install

# 2. 启动应用
npm start
```

**打包为独立应用：**
```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

### 方式二：Python GUI

基于CustomTkinter的轻量级界面。

**Windows用户：**
1. 双击 `安装依赖.bat` - 自动安装依赖
2. 双击 `启动GUI.bat` - 启动界面

**所有平台：**
```bash
# 安装依赖
pip install -r requirements.txt

# 启动GUI
python translate_csv_gui.py
```

### 方式三：命令行

适合批处理和自动化脚本。

```bash
python translate_csv.py input.csv
```

## 使用方法

### 方式一：图形界面（推荐）

启动GUI：
```bash
python translate_csv_gui.py
# 或双击 启动GUI.bat (Windows)
```

启动后将看到现代化的图形界面：

#### GUI特性：
- 🎨 **现代化设计**: 基于CustomTkinter的美观界面
- 🌓 **主题切换**: 自动跟随系统深色/浅色模式
- 📊 **实时进度**: 进度条和百分比显示
- 📝 **详细日志**: 实时查看每条翻译记录
- 🎯 **简单易用**: 图形化文件选择，无需记忆命令

#### 使用步骤：
1. **选择输入文件**: 点击"📁 浏览"选择CSV文件
2. **选择输出文件**: 自动生成或手动指定
3. **配置源语言列**: 默认"ZH"（中文）
4. **选择目标语言**: 勾选 🇹🇭 TH (泰语) 和/或 🇻🇳 VN (越南语)
5. **点击"▶️ 开始翻译"**: 开始翻译过程
6. **查看进度**: 实时进度条和详细日志

### 方式二：命令行

#### 基本用法

```bash
python translate_csv.py input.csv
```

这将读取 `input.csv` 文件，翻译TH和VN两列，并输出到 `input_translated.csv`

#### 高级用法

```bash
# 指定输出文件
python translate_csv.py input.csv -o output.csv

# 指定源语言列和目标列
python translate_csv.py input.csv -s ZH -t TH VN

# 覆盖已有翻译（默认跳过已翻译的单元格）
python translate_csv.py input.csv --overwrite

# 只翻译TH列
python translate_csv.py input.csv -t TH
```

#### 参数说明

- `input`: 输入CSV文件路径（必需）
- `-o, --output`: 输出CSV文件路径（可选，默认为 `input_translated.csv`）
- `-s, --source`: 源语言列名（可选，默认为 `ZH`）
- `-t, --targets`: 目标语言列名列表（可选，默认为 `TH VN`）
- `--overwrite`: 覆盖已有翻译（可选，默认跳过已翻译的单元格）

## CSV文件格式要求

CSV文件应包含以下列：

| Table | Sheet | Field | Type | Position | ZH | VN | TH |
|-------|-------|-------|------|----------|----|----|-----|
| ... | ... | ... | ... | ... | 低级残卷 | (待翻译) | (待翻译) |
| ... | ... | ... | ... | ... | 中级残卷 | (待翻译) | (待翻译) |

- **ZH列**: 源语言（中文）
- **VN列**: 越南语翻译目标列
- **TH列**: 泰语翻译目标列

## 工作原理

1. 读取CSV文件，识别源语言列（默认ZH）和目标语言列（默认TH、VN）
2. 遍历每一行，从源语言列获取文本
3. 使用Google翻译API翻译到目标语言
4. 如果目标列已有内容且设置了 `skip_existing=True`，则跳过该单元格
5. 将翻译结果写入目标列
6. 保存到输出CSV文件

## 注意事项

- 使用免费的Google翻译API，可能有速率限制
- 程序已内置延迟（0.1秒/次）避免触发限制
- 建议分批次处理大量数据
- 翻译结果会自动缓存，避免重复翻译相同内容

## 示例

假设有文件 `game_items.csv`:

```csv
Table,Sheet,Field,Type,Position,ZH,VN,TH
item,quality,name,前端,B7,低级残卷,,
item,quality,name,前端,B24,中级残卷,,
item,quality,name,前端,B41,高级残卷,,
```

运行命令：

```bash
python translate_csv.py game_items.csv
```

输出文件 `game_items_translated.csv`:

```csv
Table,Sheet,Field,Type,Position,ZH,VN,TH
item,quality,name,前端,B7,低级残卷,Cuộn cấp thấp,ม้วนระดับต่ำ
item,quality,name,前端,B24,中级残卷,Cuộn cấp trung,ม้วนระดับกลาง
item,quality,name,前端,B41,高级残卷,Cuộn cấp cao,ม้วนระดับสูง
```

## 开发

### 项目结构

```
auto-l10n-csv/
├── electron/                    # Electron桌面应用
│   ├── main.js                 # 主进程
│   ├── preload.js              # 预加载脚本
│   └── renderer/               # 渲染进程
│       ├── index.html          # 主界面
│       ├── styles.css          # 样式表
│       └── app.js              # 前端逻辑
├── translate_csv.py            # Python翻译引擎（命令行）
├── translate_csv_gui.py        # Python GUI版本
├── start.py                    # Python统一启动器
├── test_translation.py         # 翻译接口测试
├── 启动GUI.bat                 # Windows快捷启动
├── 安装依赖.bat                # Windows依赖安装
├── package.json                # Node.js配置
├── requirements.txt            # Python依赖
└── README.md                   # 项目文档
```

## 📊 启动方式对比

| 方式 | 命令/操作 | 特点 | 适用场景 |
|------|----------|------|---------|
| **Electron应用** | `npm start` | 现代UI、跨平台、可打包 | 推荐所有用户 |
| **Python GUI** | `python translate_csv_gui.py` | 轻量级、简单 | Python环境用户 |
| **命令行** | `python translate_csv.py <文件>` | 高效、自动化 | 批处理脚本 |
| **统一启动器** | `python start.py` | 交互式菜单 | 选择困难症 😄 |

## 💻 界面展示

### Electron版本特性
- 🎨 **现代化设计**: 渐变标题栏、卡片布局、流畅动画
- 🌈 **精美UI**: Material Design风格、圆角卡片、悬浮效果
- 📊 **实时反馈**: 动态进度条、彩色日志、状态图标
- ⚡ **高性能**: 基于Chromium引擎，流畅运行
- 📦 **可打包**: 支持Windows/Mac/Linux独立安装包
- 🔒 **安全沙箱**: 进程隔离，安全可靠

### Python GUI特性
- 🎨 **CustomTkinter**: 现代化tkinter界面
- 🌓 **主题切换**: 跟随系统深浅色模式
- 📝 **详细日志**: 实时查看翻译过程
- 🎯 **简单易用**: 轻量级，启动快速

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！