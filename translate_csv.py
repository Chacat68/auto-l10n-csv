#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV自动翻译工具
支持翻译CSV文件中的TH（泰语）和VN（越南语）列
"""

import csv
import os
import time
import argparse
from typing import List, Dict
from googletrans import Translator


class CSVTranslator:
    """CSV翻译器类"""
    
    def __init__(self):
        self.translator = Translator()
        self.translation_cache = {}
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'zh-cn') -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言代码 (th=泰语, vi=越南语)
            source_lang: 源语言代码 (默认为简体中文)
        
        Returns:
            翻译后的文本
        """
        if not text or text.strip() == '':
            return ''
        
        # 使用缓存避免重复翻译
        cache_key = f"{text}_{source_lang}_{target_lang}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            # 处理包含HTML标签的文本
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            translated = result.text
            self.translation_cache[cache_key] = translated
            
            # 避免API速率限制
            time.sleep(0.1)
            
            return translated
        except Exception as e:
            print(f"翻译失败: {text[:50]}... -> {target_lang}, 错误: {str(e)}")
            return text  # 失败时返回原文
    
    def process_csv(self, input_file: str, output_file: str, 
                   source_col: str = 'ZH', 
                   target_cols: List[str] = None,
                   skip_existing: bool = True):
        """
        处理CSV文件，翻译指定列
        
        Args:
            input_file: 输入CSV文件路径
            output_file: 输出CSV文件路径
            source_col: 源语言列名（默认为'ZH'）
            target_cols: 需要翻译的目标列名列表（默认为['TH', 'VN']）
            skip_existing: 是否跳过已有翻译的单元格（默认True）
        """
        if target_cols is None:
            target_cols = ['TH', 'VN']
        
        # 语言代码映射
        lang_map = {
            'TH': 'th',
            'VN': 'vi'
        }
        
        print(f"开始处理文件: {input_file}")
        print(f"源语言列: {source_col}")
        print(f"目标列: {', '.join(target_cols)}")
        
        # 读取CSV文件
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        # 检查列名是否存在
        if source_col not in fieldnames:
            raise ValueError(f"源列 '{source_col}' 不存在于CSV文件中")
        
        for col in target_cols:
            if col not in fieldnames:
                raise ValueError(f"目标列 '{col}' 不存在于CSV文件中")
        
        total_rows = len(rows)
        print(f"共 {total_rows} 行数据")
        
        # 翻译每一行
        for idx, row in enumerate(rows, 1):
            source_text = row.get(source_col, '').strip()
            
            if not source_text:
                print(f"[{idx}/{total_rows}] 跳过空行")
                continue
            
            print(f"\n[{idx}/{total_rows}] 处理: {source_text[:50]}...")
            
            for target_col in target_cols:
                # 如果设置了跳过已有翻译，且该单元格已有内容，则跳过
                if skip_existing and row.get(target_col, '').strip():
                    print(f"  - {target_col}: 已有翻译，跳过")
                    continue
                
                target_lang = lang_map.get(target_col)
                if not target_lang:
                    print(f"  - {target_col}: 不支持的语言，跳过")
                    continue
                
                # 执行翻译
                translated = self.translate_text(source_text, target_lang)
                row[target_col] = translated
                print(f"  - {target_col}: {translated[:50]}...")
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"\n翻译完成！输出文件: {output_file}")
        print(f"共处理 {total_rows} 行数据")


def main():
    parser = argparse.ArgumentParser(description='CSV自动翻译工具')
    parser.add_argument('input', help='输入CSV文件路径')
    parser.add_argument('-o', '--output', help='输出CSV文件路径（默认为input_translated.csv）')
    parser.add_argument('-s', '--source', default='ZH', help='源语言列名（默认为ZH）')
    parser.add_argument('-t', '--targets', nargs='+', default=['TH', 'VN'], 
                       help='目标语言列名列表（默认为TH VN）')
    parser.add_argument('--overwrite', action='store_true', 
                       help='覆盖已有翻译（默认跳过已翻译的单元格）')
    
    args = parser.parse_args()
    
    # 生成输出文件名
    if not args.output:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_translated{ext}"
    
    # 执行翻译
    translator = CSVTranslator()
    translator.process_csv(
        input_file=args.input,
        output_file=args.output,
        source_col=args.source,
        target_cols=args.targets,
        skip_existing=not args.overwrite
    )


if __name__ == '__main__':
    main()
