#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CSV to JSON converter.

Why this exists:
- Many CSV->JSON pipelines break when the CSV has an UTF-8 BOM.
  The BOM can become part of the first header key (e.g. "\ufeffTable"),
  causing "format issues" downstream.

This script:
- Reads CSV using utf-8-sig (auto strips BOM)
- Writes JSON using utf-8 (no BOM)
- Preserves all columns as strings

Usage:
  python csv_to_json.py input.csv -o output.json
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def read_csv_rows(path: Path, encoding: str = "utf-8-sig") -> List[Dict[str, str]]:
    with path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        return list(reader)


def write_json(path: Path, data: Any, encoding: str = "utf-8") -> None:
    with path.open("w", encoding=encoding, newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a CSV file to JSON (array of objects).")
    parser.add_argument("input", help="输入CSV文件路径")
    parser.add_argument("-o", "--output", help="输出JSON文件路径（默认: 与输入同名 .json）")
    parser.add_argument(
        "--input-encoding",
        default="utf-8-sig",
        help="输入CSV编码（默认: utf-8-sig，会自动去掉BOM）",
    )
    parser.add_argument(
        "--output-encoding",
        default="utf-8",
        help="输出JSON编码（默认: utf-8，不带BOM）",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"输入文件不存在: {input_path}")

    output_path = Path(args.output) if args.output else input_path.with_suffix(".json")

    rows = read_csv_rows(input_path, encoding=args.input_encoding)
    write_json(output_path, rows, encoding=args.output_encoding)

    print(f"OK: {input_path} -> {output_path} (rows={len(rows)})")


if __name__ == "__main__":
    main()
