# auto-l10n-csv

🌍 自动翻译CSV文件中的多语言列（TH泰语、VN越南语）

## 功能特点

- ✅ 自动翻译CSV文件中的指定列
- ✅ 支持从中文翻译到泰语(TH)和越南语(VN)
- ✅ 智能跳过已有翻译的单元格
- ✅ 使用Google翻译API（免费）
- ✅ 支持HTML标签保留
- ✅ 翻译结果缓存，避免重复翻译
- ✅ 现代化GUI界面 (基于CustomTkinter)
- ✅ 支持深色/浅色主题自动切换
- ✅ 实时进度显示和日志输出

## 快速开始

### Windows用户（最简单）

1. **双击运行 `安装依赖.bat`** - 自动安装所需依赖
2. **双击运行 `启动GUI.bat`** - 启动图形界面

### 所有平台

1. **克隆或下载项目**
```bash
git clone <repository-url>
cd auto-l10n-csv
```

2. **安装Python依赖**
```bash
pip install -r requirements.txt
```

3. **选择启动方式**

**方式A：统一启动器（推荐）**
```bash
python start.py
```
交互式菜单，选择GUI或命令行模式

**方式B：直接启动GUI**
```bash
python translate_csv_gui.py
# 或 Windows双击: 启动GUI.bat
```

**方式C：命令行模式**
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
├── translate_csv.py         # 命令行版本主程序
├── translate_csv_gui.py     # GUI版本主程序（推荐）
├── start.py                 # 统一启动器
├── 启动GUI.bat              # Windows一键启动GUI
├── 安装依赖.bat             # Windows一键安装依赖
├── requirements.txt         # Python依赖
├── config.example.py        # 配置示例
├── .gitignore              # Git忽略文件
└── README.md               # 项目文档
```

## 启动方式总览

| 方式 | 命令/操作 | 适用场景 |
|------|----------|---------|
| **统一启动器** | `python start.py` | 交互式选择GUI或CLI |
| **GUI (推荐)** | `python translate_csv_gui.py` 或双击 `启动GUI.bat` | 可视化操作，适合所有用户 |
| **命令行** | `python translate_csv.py <文件>` | 批处理、自动化脚本 |
| **安装依赖** | 双击 `安装依赖.bat` (Windows) | 首次使用前安装 |

## GUI界面展示

### 主要特性
- 🎨 **现代化UI**: 基于CustomTkinter的专业界面设计
- 🌓 **智能主题**: 自动适配系统深色/浅色模式
- 📁 **便捷操作**: 图形化文件选择，操作直观
- 🗂️ **配置灵活**: 可视化配置源语言和目标语言
- 📊 **进度可视**: 实时进度条和百分比显示
- 📝 **日志详细**: 滚动日志窗口，记录每步操作
- ⏯️ **流程控制**: 支持开始、停止、清空日志等操作
- 🎭 **图标美化**: 使用Emoji增强视觉效果

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！