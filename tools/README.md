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

### CSV 转 JSON（解决BOM/表头乱码导致的格式问题）

有些外部“CSV→JSON”工具在遇到 UTF-8 BOM 时，会把 BOM 当成表头的一部分（例如第一列键变成 `\ufeffTable`），从而出现“转成JSON格式不对/字段名异常”。

本工具提供一个稳健的转换脚本（自动去 BOM）：

```bash
python csv_to_json.py ../CSV/活动翻译提取_20251219_170632.csv -o ../CSV/活动翻译提取_20251219_170632.json
```

### 检测 CSV 文本是否会“炸”JSON

如果你使用的“CSV→JSON”工具没有正确对字符串做 JSON 转义，CSV 单元格里出现这些字符就很容易导致 JSON 语法错误（例如 VS Code 报 `Expected comma` / `Colon expected`）：

- `"`（双引号）
- `\\`（反斜杠）
- 换行/回车/Tab 等控制字符

可以用下面脚本扫描并生成定位报告：

```bash
python check_csv_json_unsafe.py ../CSV/活动翻译提取_20251219_170632.csv --columns ZH,VN,TH
```

输出一个报告 CSV：`{input}_json_unsafe_report.csv`，包含行号、列名、问题类型和内容预览，方便你回到源表定位。

### 生成“JSON-safe”CSV（给不转义的CSV→JSON工具用）

如果你无法修改外部 CSV→JSON 工具，又必须用它（且它不做 JSON 转义），可以先生成一个“JSON-safe CSV”：

```bash
python sanitize_csv_for_json.py ../CSV/CN翻译提取_20251225_202755.csv
```

默认会对 `ZH,VN,TH` 三列做 JSON 级别的字符串转义，并输出：`*_jsonsafe.csv`。

Windows 一键：双击 [tools/生成JSON安全CSV.bat](tools/生成JSON安全CSV.bat)

可选参数：

```bash
# 指定输入/输出编码
python csv_to_json.py input.csv -o output.json --input-encoding utf-8-sig --output-encoding utf-8
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
