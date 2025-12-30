#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scan CSV cells for JSON-unsafe patterns.

Context
- Many CSV->JSON converters are *not* JSON serializers; they often build JSON
  by string concatenation without escaping values.
- In that case, certain characters inside CSV cells will break the generated JSON,
  causing errors like "Expected comma" / "Colon expected" in editors.

This script flags cells that contain characters which MUST be escaped in JSON
strings, or cells that Python's json module cannot serialize.

It does NOT modify the CSV by default; it produces a report to help you locate
problematic cells.

Usage:
  python check_csv_json_unsafe.py input.csv
  python check_csv_json_unsafe.py input.csv --columns ZH,VN,TH -o report.csv

Tips
- If you want a reliable CSV->JSON conversion, use tools/csv_to_json.py.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


RISK_CHARS = {
    '"': "double_quote",
    "\\": "backslash",
    "\n": "newline",
    "\r": "carriage_return",
    "\t": "tab",
    "\b": "backspace",
    "\f": "formfeed",
}


def find_control_chars(text: str) -> bool:
    # JSON strings cannot contain raw control chars U+0000..U+001F.
    # A correct serializer will escape them, but naive converters will break.
    return any(ord(ch) < 0x20 for ch in text)


def preview(text: str, limit: int = 120) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


@dataclass
class Finding:
    csv_line: int
    row_index: int
    column: str
    issues: str
    value_len: int
    value_preview: str
    table: str = ""
    sheet: str = ""
    field: str = ""
    position: str = ""


def iter_findings(
    rows: Sequence[Dict[str, str]],
    fieldnames: Sequence[str],
    columns: Optional[Sequence[str]] = None,
) -> Iterable[Finding]:
    cols = list(columns) if columns else list(fieldnames)

    # Common locator columns (optional)
    locator_keys = {
        "Table": "table",
        "Sheet": "sheet",
        "Field": "field",
        "Position": "position",
    }

    for i, row in enumerate(rows):
        csv_line = i + 2  # header is line 1
        row_index = i + 1

        locator_values = {attr: row.get(key, "") for key, attr in locator_keys.items()}

        for col in cols:
            value = row.get(col, "")
            if value is None:
                value = ""

            issues: List[str] = []
            for ch, label in RISK_CHARS.items():
                if ch in value:
                    issues.append(label)

            if find_control_chars(value):
                issues.append("control_char")

            # Also detect values that json can't serialize (rare, but catches invalid surrogates).
            try:
                json.dumps(value, ensure_ascii=False)
            except Exception as e:  # noqa: BLE001
                issues.append(f"json_dumps_error:{type(e).__name__}")

            if issues:
                yield Finding(
                    csv_line=csv_line,
                    row_index=row_index,
                    column=col,
                    issues="|".join(sorted(set(issues))),
                    value_len=len(value),
                    value_preview=preview(value),
                    **locator_values,
                )


def read_csv(path: Path, encoding: str) -> Tuple[List[Dict[str, str]], List[str]]:
    with path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return rows, list(fieldnames)


def write_report(path: Path, findings: Sequence[Finding]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "csv_line",
                "row_index",
                "Table",
                "Sheet",
                "Field",
                "Position",
                "column",
                "issues",
                "value_len",
                "value_preview",
            ],
        )
        writer.writeheader()
        for it in findings:
            writer.writerow(
                {
                    "csv_line": it.csv_line,
                    "row_index": it.row_index,
                    "Table": it.table,
                    "Sheet": it.sheet,
                    "Field": it.field,
                    "Position": it.position,
                    "column": it.column,
                    "issues": it.issues,
                    "value_len": it.value_len,
                    "value_preview": it.value_preview,
                }
            )


def parse_columns(arg: str) -> List[str]:
    cols = [c.strip() for c in arg.split(",") if c.strip()]
    if not cols:
        raise argparse.ArgumentTypeError("--columns 不能为空")
    return cols


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan CSV for JSON-unsafe cell content.")
    parser.add_argument("input", help="输入CSV文件路径")
    parser.add_argument(
        "-o",
        "--output",
        help="输出报告CSV路径（默认: {input}_json_unsafe_report.csv）",
    )
    parser.add_argument(
        "--columns",
        type=parse_columns,
        default=None,
        help="只检测指定列（逗号分隔），例如: ZH,VN,TH",
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
        f"{input_path.stem}_json_unsafe_report{input_path.suffix}"
    )

    rows, fieldnames = read_csv(input_path, encoding=args.encoding)
    if not fieldnames:
        raise SystemExit("CSV 没有表头（fieldnames 为空）")

    # Validate columns
    if args.columns:
        missing = [c for c in args.columns if c not in fieldnames]
        if missing:
            raise SystemExit(f"指定的列不存在: {missing}. 可用列: {fieldnames}")

    findings = list(iter_findings(rows, fieldnames, columns=args.columns))
    write_report(output_path, findings)

    print(f"Checked: {input_path}")
    print(f"Rows: {len(rows)}")
    print(f"Findings: {len(findings)}")
    print(f"Report: {output_path}")


if __name__ == "__main__":
    main()
