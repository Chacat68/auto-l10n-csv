#!/usr/bin/env python#!/usr/bin/env python













#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 CSV 单元格内容转成 JSON-safe（给“字符串拼 JSON”的转换器用）。

背景
- 许多 CSV→JSON 工具不是 JSON 序列化器，而是用字符串拼接生成 JSON。
- 一旦单元格里含有 `"`、`\\`、控制字符/换行，拼出来的 JSON 很容易非法，
  VS Code 常见报错：`Expected comma` / `Colon expected`。

做法
- 对指定列（默认 ZH/VN/TH）做 JSON 字符串转义，但不额外加外层引号。
  具体实现：`json.dumps(value, ensure_ascii=False)[1:-1]`

用法
  python sanitize_csv_for_json.py input.csv
  python sanitize_csv_for_json.py input.csv --columns ZH,VN,TH
  python sanitize_csv_for_json.py input.csv --report input_json_unsafe_report.csv

输出
- 默认输出：`{input}_jsonsafe.csv`（不修改原文件）
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple


def parse_columns(arg: str) -> List[str]:
    cols = [c.strip() for c in arg.split(",") if c.strip()]
    if not cols:
        raise argparse.ArgumentTypeError("--columns 不能为空")
    return cols


def read_csv_rows(path: Path, encoding: str) -> Tuple[List[Dict[str, str]], List[str]]:
    with path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return rows, list(fieldnames)


def write_csv_rows(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_json_escaped_content(value: str) -> str:
    dumped = json.dumps(value or "", ensure_ascii=False)
    if len(dumped) >= 2 and dumped[0] == '"' and dumped[-1] == '"':
        return dumped[1:-1]
    return dumped


def load_report_pairs(report_path: Path) -> Set[Tuple[int, str]]:
    pairs: Set[Tuple[int, str]] = set()
    with report_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row_index = int((row.get("row_index") or "").strip())
            except ValueError:
                continue
            col = (row.get("column") or "").strip()
            if row_index > 0 and col:
                pairs.add((row_index, col))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Sanitize CSV cells for naive CSV→JSON converters.")
    parser.add_argument("input", help="输入CSV文件路径")
    parser.add_argument("-o", "--output", help="输出CSV文件路径（默认: {input}_jsonsafe.csv）")
    parser.add_argument(
        "--columns",
        type=parse_columns,
        default=None,
        help="要处理的列（逗号分隔，默认: ZH,VN,TH 若存在；否则处理全部列）",
    )
    parser.add_argument(
        "--report",
        help="报告CSV路径（*_json_unsafe_report.csv）。提供后仅修复报告里标记的单元格",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="输入CSV编码（默认: utf-8-sig，会自动去掉BOM）",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"输入文件不存在: {input_path}")

    output_path = Path(args.output) if args.output else input_path.with_name(
        f"{input_path.stem}_jsonsafe{input_path.suffix}"
    )

    report_pairs: Optional[Set[Tuple[int, str]]] = None
    if args.report:
        report_path = Path(args.report)
        if not report_path.exists():
            raise SystemExit(f"报告文件不存在: {report_path}")
        report_pairs = load_report_pairs(report_path)
        if not report_pairs:
            raise SystemExit("报告里没有可用的 row_index/column 记录")

    rows, fieldnames = read_csv_rows(input_path, encoding=args.encoding)
    if not fieldnames:
        raise SystemExit("CSV 没有表头（fieldnames 为空）")

    if args.columns:
        target_columns = args.columns
    else:
        preferred = [c for c in ("ZH", "VN", "TH") if c in fieldnames]
        target_columns = preferred if preferred else list(fieldnames)

    missing = [c for c in target_columns if c not in fieldnames]
    if missing:
        raise SystemExit(f"指定的列不存在: {missing}. 可用列: {fieldnames}")

    changed_cells = 0
    for i, row in enumerate(rows):
        row_index = i + 1
        for col in target_columns:
            if report_pairs is not None and (row_index, col) not in report_pairs:
                continue
            original = row.get(col, "")
            escaped = to_json_escaped_content(original)
            if escaped != original:
                row[col] = escaped
                changed_cells += 1

    write_csv_rows(output_path, fieldnames, rows)

    print(f"OK: {input_path} -> {output_path}")
    print(f"Rows: {len(rows)}")
    print(f"Changed cells: {changed_cells}")
    if report_pairs is not None:
        print(f"Report-driven targets: {len(report_pairs)}")


if __name__ == "__main__":
    main()
