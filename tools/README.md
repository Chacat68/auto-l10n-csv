# CSV翻译工具

将CSV文件中的中文（ZH列）翻译成泰语（TH）和越南语（VN）。

## 功能特点

- ✅ 支持将中文翻译成泰语（TH）和越南语（VN）
- ✅ 自动保留颜色标签 `<color=#xxx>...</color>`
- ✅ 智能跳过已翻译的内容（如果目标列已有不同于中文的翻译）
- ✅ 批量保存，防止意外丢失进度
- ✅ 支持强制重新翻译模式

## 安装

```bash
cd tools
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 翻译CSV文件（自动生成 xxx_translated.csv）
python translate_csv.py ../CSV/系统翻译提取_20251219_165646.csv

# 指定输出文件
python translate_csv.py input.csv -o output.csv
```

### 选项

```bash
# 只翻译越南语（跳过泰语）
python translate_csv.py input.csv --no-th

# 只翻译泰语（跳过越南语）
python translate_csv.py input.csv --no-vn

# 强制翻译（即使目标列已有翻译）
python translate_csv.py input.csv --force

# 调整批处理大小和延迟
python translate_csv.py input.csv --batch-size 20 --delay 1.0
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入CSV文件路径 | 必填 |
| `-o, --output` | 输出CSV文件路径 | `{input}_translated.csv` |
| `--no-th` | 不翻译泰语列 | 否 |
| `--no-vn` | 不翻译越南语列 | 否 |
| `-f, --force` | 强制翻译（覆盖已有翻译） | 否 |
| `--batch-size` | 批处理大小（每N行保存一次） | 10 |
| `--delay` | 每次翻译后的延迟（秒） | 0.5 |

## CSV文件格式

输入CSV文件需要包含以下列：

| 列名 | 说明 |
|------|------|
| ZH | 中文原文（翻译源） |
| TH | 泰语翻译（翻译目标） |
| VN | 越南语翻译（翻译目标） |

其他列会被保留但不会被修改。

## 翻译逻辑

1. 如果目标列（TH/VN）为空，则进行翻译
2. 如果目标列内容与中文（ZH）相同，则进行翻译
3. 如果目标列已有不同于中文的内容，则跳过（除非使用 `--force`）

## 示例

```bash
# 翻译系统翻译文件
python translate_csv.py "../CSV/系统翻译提取_20251219_165646.csv"

# 翻译活动翻译文件，只翻译泰语
python translate_csv.py "../CSV/活动翻译提取_20251219_170632.csv" --no-vn

# 强制重新翻译所有内容
python translate_csv.py "../CSV/系统翻译提取_20251219_165646.csv" --force
```

## 注意事项

1. 使用Google翻译API，可能有速率限制
2. 建议设置适当的延迟（`--delay`）避免被限制
3. 大文件翻译可能需要较长时间，请耐心等待
4. 翻译过程中会定期保存进度，可以随时中断
