#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV翻译工具 - 将ZH列翻译成TH（泰语）和VN（越南语）

使用方法:
    python translate_csv.py input.csv -o output.csv
    python translate_csv.py input.csv --no-th  # 只翻译VN
    python translate_csv.py input.csv --force  # 强制重新翻译
"""

import csv
import os
import re
import time
import argparse
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("警告: 请安装 deep-translator: pip install deep-translator")


class CSVTranslator:
    """CSV翻译器类"""
    
    # 颜色标签正则表达式
    COLOR_TAG_PATTERN = re.compile(r'(<color[^>]*>|</color>)')
    
    def __init__(self, translator_type: str = "google", api_key: Optional[str] = None):
        """
        初始化翻译器
        
        Args:
            translator_type: 翻译器类型 ("google")
            api_key: API密钥（保留参数，暂未使用）
        """
        self.translator_type = translator_type
        
        if not TRANSLATOR_AVAILABLE:
            raise ImportError("请安装 deep-translator: pip install deep-translator")
        
        # 创建翻译器实例（每种语言需要单独创建）
        self.translators = {
            "th": GoogleTranslator(source='zh-CN', target='th'),
            "vi": GoogleTranslator(source='zh-CN', target='vi'),
        }
    
    def _extract_color_tags(self, text: str) -> tuple[str, list[tuple[int, str]]]:
        """
        提取文本中的颜色标签，返回纯文本和标签位置信息
        
        Args:
            text: 包含颜色标签的文本
            
        Returns:
            (纯文本, [(位置, 标签)...])
        """
        tags = []
        pure_text = ""
        last_end = 0
        
        for match in self.COLOR_TAG_PATTERN.finditer(text):
            # 添加标签前的文本
            pure_text += text[last_end:match.start()]
            # 记录标签在纯文本中的位置
            tags.append((len(pure_text), match.group()))
            last_end = match.end()
        
        # 添加最后一部分文本
        pure_text += text[last_end:]
        
        return pure_text, tags
    
    def _restore_color_tags(self, translated_text: str, original_tags: list[tuple[int, str]], 
                            original_pure_text: str) -> str:
        """
        将颜色标签还原到翻译后的文本中
        
        由于翻译后文本长度可能变化，我们按比例重新计算标签位置
        
        Args:
            translated_text: 翻译后的纯文本
            original_tags: 原始标签位置信息
            original_pure_text: 原始纯文本
            
        Returns:
            还原标签后的文本
        """
        if not original_tags:
            return translated_text
        
        if not original_pure_text:
            # 原文只有标签没有文字
            result = ""
            for _, tag in original_tags:
                result += tag
            return result + translated_text
        
        # 按比例计算新位置
        ratio = len(translated_text) / len(original_pure_text) if original_pure_text else 1
        
        # 调整标签位置
        adjusted_tags = []
        for pos, tag in original_tags:
            new_pos = int(pos * ratio)
            new_pos = min(new_pos, len(translated_text))
            adjusted_tags.append((new_pos, tag))
        
        # 按位置从后向前插入标签
        result = translated_text
        for pos, tag in reversed(adjusted_tags):
            result = result[:pos] + tag + result[pos:]
        
        return result
    
    def translate_text(self, text: str, target_lang: str) -> str:
        """
        翻译文本，保留颜色标签
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言代码 ("th" 或 "vi")
            
        Returns:
            翻译后的文本
        """
        if not text or text.strip() == "":
            return text
        
        # 提取颜色标签
        pure_text, tags = self._extract_color_tags(text)
        
        if not pure_text.strip():
            # 只有标签没有文字
            return text
        
        try:
            # 使用 deep-translator
            translator = self.translators.get(target_lang)
            if not translator:
                print(f"不支持的目标语言: {target_lang}")
                return text
            
            translated = translator.translate(pure_text)
            
            # 还原颜色标签
            return self._restore_color_tags(translated, tags, pure_text)
            
        except Exception as e:
            print(f"翻译失败: {e}, 原文: {text[:50]}...")
            return text
    
    def needs_translation(self, zh_text: str, target_text: str) -> bool:
        """
        判断是否需要翻译
        
        如果目标文本为空，或者目标文本与中文相同（说明还没翻译），则需要翻译
        
        Args:
            zh_text: 中文文本
            target_text: 目标语言文本
            
        Returns:
            是否需要翻译
        """
        if not target_text or target_text.strip() == "":
            return True
        
        # 如果目标文本和中文相同，说明还没翻译
        if target_text.strip() == zh_text.strip():
            return True
        
        return False
    
    def translate_csv(self, input_file: str, output_file: Optional[str] = None,
                      translate_th: bool = True, translate_vn: bool = True,
                      force: bool = False, batch_size: int = 10,
                      delay: float = 0.5) -> dict:
        """
        翻译CSV文件
        
        Args:
            input_file: 输入CSV文件路径
            output_file: 输出CSV文件路径（默认为输入文件名_translated.csv）
            translate_th: 是否翻译TH列
            translate_vn: 是否翻译VN列
            force: 是否强制翻译（即使已有翻译）
            batch_size: 批处理大小（每处理多少行保存一次）
            delay: 每次翻译后的延迟（秒），避免API限制
            
        Returns:
            翻译统计信息
        """
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.parent / f"{input_path.stem}_translated{input_path.suffix}")
        
        stats = {
            "total_rows": 0,
            "translated_th": 0,
            "translated_vn": 0,
            "skipped_th": 0,
            "skipped_vn": 0,
            "errors": 0
        }
        
        # 读取CSV
        print(f"正在读取文件: {input_file}")
        rows = []
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)
        
        stats["total_rows"] = len(rows)
        print(f"共读取 {len(rows)} 行数据")
        
        # 检查必要的列
        required_cols = ["ZH"]
        if translate_th:
            required_cols.append("TH")
        if translate_vn:
            required_cols.append("VN")
        
        for col in required_cols:
            if col not in fieldnames:
                raise ValueError(f"CSV文件缺少必要的列: {col}")
        
        # 翻译
        for i, row in enumerate(rows):
            zh_text = row.get("ZH", "")
            
            if translate_th:
                th_text = row.get("TH", "")
                if force or self.needs_translation(zh_text, th_text):
                    print(f"[{i+1}/{len(rows)}] 翻译TH: {zh_text[:30]}...")
                    try:
                        row["TH"] = self.translate_text(zh_text, "th")
                        stats["translated_th"] += 1
                        time.sleep(delay)
                    except Exception as e:
                        print(f"  错误: {e}")
                        stats["errors"] += 1
                else:
                    stats["skipped_th"] += 1
            
            if translate_vn:
                vn_text = row.get("VN", "")
                if force or self.needs_translation(zh_text, vn_text):
                    print(f"[{i+1}/{len(rows)}] 翻译VN: {zh_text[:30]}...")
                    try:
                        row["VN"] = self.translate_text(zh_text, "vi")
                        stats["translated_vn"] += 1
                        time.sleep(delay)
                    except Exception as e:
                        print(f"  错误: {e}")
                        stats["errors"] += 1
                else:
                    stats["skipped_vn"] += 1
            
            # 批量保存
            if (i + 1) % batch_size == 0:
                self._save_csv(output_file, fieldnames, rows)
                print(f"已保存进度: {i+1}/{len(rows)}")
        
        # 最终保存
        self._save_csv(output_file, fieldnames, rows)
        print(f"\n翻译完成! 输出文件: {output_file}")
        
        return stats
    
    def _save_csv(self, output_file: str, fieldnames: list, rows: list):
        """保存CSV文件"""
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="CSV翻译工具 - 将ZH列翻译成TH和VN")
    parser.add_argument("input", help="输入CSV文件路径")
    parser.add_argument("-o", "--output", help="输出CSV文件路径")
    parser.add_argument("--th", action="store_true", default=True, help="翻译TH列（默认开启）")
    parser.add_argument("--vn", action="store_true", default=True, help="翻译VN列（默认开启）")
    parser.add_argument("--no-th", action="store_true", help="不翻译TH列")
    parser.add_argument("--no-vn", action="store_true", help="不翻译VN列")
    parser.add_argument("-f", "--force", action="store_true", help="强制翻译（即使已有翻译）")
    parser.add_argument("--translator", choices=["google", "deepl"], default="google",
                        help="翻译器类型（默认: google）")
    parser.add_argument("--api-key", help="DeepL API密钥")
    parser.add_argument("--batch-size", type=int, default=10, help="批处理大小（默认: 10）")
    parser.add_argument("--delay", type=float, default=0.5, help="翻译延迟秒数（默认: 0.5）")
    
    args = parser.parse_args()
    
    # 处理翻译选项
    translate_th = not args.no_th
    translate_vn = not args.no_vn
    
    # 创建翻译器
    translator = CSVTranslator(
        translator_type=args.translator,
        api_key=args.api_key
    )
    
    # 执行翻译
    stats = translator.translate_csv(
        input_file=args.input,
        output_file=args.output,
        translate_th=translate_th,
        translate_vn=translate_vn,
        force=args.force,
        batch_size=args.batch_size,
        delay=args.delay
    )
    
    # 打印统计
    print("\n=== 翻译统计 ===")
    print(f"总行数: {stats['total_rows']}")
    print(f"翻译TH: {stats['translated_th']} (跳过: {stats['skipped_th']})")
    print(f"翻译VN: {stats['translated_vn']} (跳过: {stats['skipped_vn']})")
    print(f"错误数: {stats['errors']}")


if __name__ == "__main__":
    main()
