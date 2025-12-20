#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV翻译工具 - 将CSV中的ZH列翻译成TH（泰语）和VN（越南语）
"""

import csv
import re
import time
import os
from pathlib import Path
from typing import Optional
from googletrans import Translator

# 配置
INPUT_CSV = Path(__file__).parent.parent / "CSV" / "系统翻译提取_20251219_165646.csv"
OUTPUT_CSV = Path(__file__).parent.parent / "CSV" / "translated_output.csv"
BATCH_SIZE = 50  # 每批翻译的数量
DELAY_BETWEEN_BATCHES = 1  # 批次之间的延迟（秒）


def extract_text_parts(text: str) -> tuple[list[str], list[str]]:
    """
    提取文本中需要翻译的部分，保留颜色标签等格式
    返回: (需要翻译的文本列表, 格式标记列表)
    """
    # 匹配 <color=#xxx>内容</color> 格式
    color_pattern = r'(<color=[^>]+>)(.*?)(</color>)'
    
    parts = []
    formats = []
    last_end = 0
    
    for match in re.finditer(color_pattern, text):
        # 添加标签前的普通文本
        if match.start() > last_end:
            plain_text = text[last_end:match.start()]
            if plain_text.strip():
                parts.append(plain_text)
                formats.append(('plain', None, None))
        
        # 添加标签内的文本
        open_tag, content, close_tag = match.groups()
        parts.append(content)
        formats.append(('color', open_tag, close_tag))
        last_end = match.end()
    
    # 添加最后的普通文本
    if last_end < len(text):
        plain_text = text[last_end:]
        if plain_text.strip():
            parts.append(plain_text)
            formats.append(('plain', None, None))
    
    # 如果没有匹配到任何格式，整个文本作为普通文本
    if not parts:
        parts = [text]
        formats = [('plain', None, None)]
    
    return parts, formats


def reconstruct_text(translated_parts: list[str], formats: list[tuple]) -> str:
    """
    根据格式信息重建翻译后的文本
    """
    result = []
    for i, (fmt_type, open_tag, close_tag) in enumerate(formats):
        if i < len(translated_parts):
            if fmt_type == 'color':
                result.append(f"{open_tag}{translated_parts[i]}{close_tag}")
            else:
                result.append(translated_parts[i])
    return ''.join(result)


def should_translate(zh_text: str, target_text: str) -> bool:
    """
    判断是否需要翻译
    - 如果目标列为空，需要翻译
    - 如果目标列与中文列相同，需要翻译
    - 如果目标列已有不同内容，跳过
    """
    if not target_text or target_text.strip() == '':
        return True
    if target_text.strip() == zh_text.strip():
        return True
    return False


def translate_text(translator: Translator, text: str, dest_lang: str) -> str:
    """
    翻译单个文本，保留格式标签
    """
    if not text or text.strip() == '':
        return text
    
    # 检查是否包含颜色标签
    if '<color=' in text:
        parts, formats = extract_text_parts(text)
        translated_parts = []
        for part in parts:
            if part.strip():
                try:
                    result = translator.translate(part, src='zh-cn', dest=dest_lang)
                    translated_parts.append(result.text)
                except Exception as e:
                    print(f"翻译失败: {part[:30]}... 错误: {e}")
                    translated_parts.append(part)
            else:
                translated_parts.append(part)
        return reconstruct_text(translated_parts, formats)
    else:
        try:
            result = translator.translate(text, src='zh-cn', dest=dest_lang)
            return result.text
        except Exception as e:
            print(f"翻译失败: {text[:30]}... 错误: {e}")
            return text


def process_csv(input_path: Path, output_path: Path):
    """
    处理CSV文件，翻译TH和VN列
    """
    translator = Translator()
    
    print(f"读取CSV文件: {input_path}")
    
    # 读取CSV
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    print(f"共读取 {len(rows)} 行数据")
    
    # 统计需要翻译的行
    to_translate_th = 0
    to_translate_vn = 0
    
    for row in rows:
        zh_text = row.get('ZH', '')
        th_text = row.get('TH', '')
        vn_text = row.get('VN', '')
        
        if should_translate(zh_text, th_text):
            to_translate_th += 1
        if should_translate(zh_text, vn_text):
            to_translate_vn += 1
    
    print(f"需要翻译TH: {to_translate_th} 行")
    print(f"需要翻译VN: {to_translate_vn} 行")
    
    # 翻译
    translated_count = 0
    for i, row in enumerate(rows):
        zh_text = row.get('ZH', '')
        th_text = row.get('TH', '')
        vn_text = row.get('VN', '')
        
        if not zh_text:
            continue
        
        # 翻译TH（泰语）
        if should_translate(zh_text, th_text):
            row['TH'] = translate_text(translator, zh_text, 'th')
            translated_count += 1
        
        # 翻译VN（越南语）
        if should_translate(zh_text, vn_text):
            row['VN'] = translate_text(translator, zh_text, 'vi')
            translated_count += 1
        
        # 进度显示
        if (i + 1) % BATCH_SIZE == 0:
            print(f"进度: {i + 1}/{len(rows)} ({(i + 1) / len(rows) * 100:.1f}%)")
            time.sleep(DELAY_BETWEEN_BATCHES)
    
    print(f"翻译完成，共翻译 {translated_count} 个单元格")
    
    # 写入输出CSV
    print(f"写入输出文件: {output_path}")
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print("处理完成！")


def main():
    """主函数"""
    input_csv = INPUT_CSV
    output_csv = OUTPUT_CSV
    
    # 检查输入文件是否存在
    if not input_csv.exists():
        print(f"错误: 输入文件不存在 - {input_csv}")
        return
    
    # 确保输出目录存在
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    process_csv(input_csv, output_csv)


if __name__ == "__main__":
    main()
