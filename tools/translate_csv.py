#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV翻译工具 - 将ZH列翻译成TH（泰语）和VN（越南语）

使用方法:
    python translate_csv.py input.csv -o output.csv
    python translate_csv.py input.csv --no-th  # 只翻译VN
    python translate_csv.py input.csv --force  # 强制重新翻译
    python translate_csv.py input.csv --api-type google-cloud --api-key YOUR_KEY
"""

import csv
import os
import re
import time
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# 翻译库导入
DEEP_TRANSLATOR_AVAILABLE = False
GOOGLE_CLOUD_AVAILABLE = False
OPENAI_AVAILABLE = False

try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    pass

try:
    from google.cloud import translate_v2 as google_translate
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    pass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    pass


# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "api_config.json"


def load_api_config() -> Dict[str, Any]:
    """加载API配置"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_api_config(config: Dict[str, Any]):
    """保存API配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


class CSVTranslator:
    """CSV翻译器类"""
    
    # 颜色标签正则表达式
    COLOR_TAG_PATTERN = re.compile(r'(<color[^>]*>|</color>)')
    
    # 支持的API类型
    API_TYPES = {
        "google-free": "Google翻译(免费，有限制)",
        "google-cloud": "Google Cloud Translation API(需API Key)",
        "openai": "OpenAI GPT翻译(需API Key)",
        "deepseek": "DeepSeek翻译(需API Key，推荐)",
        "deepl": "DeepL翻译(需API Key)",
    }
    
    def __init__(self, api_type: str = "google-free", api_key: Optional[str] = None, 
                 api_endpoint: Optional[str] = None):
        """
        初始化翻译器
        
        Args:
            api_type: API类型 ("google-free", "google-cloud", "openai", "deepl")
            api_key: API密钥
            api_endpoint: 自定义API端点（用于OpenAI兼容的API）
        """
        self.api_type = api_type
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        
        # 验证依赖
        if api_type == "google-free" and not DEEP_TRANSLATOR_AVAILABLE:
            raise ImportError("请安装 deep-translator: pip install deep-translator")
        elif api_type == "google-cloud" and not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError("请安装 google-cloud-translate: pip install google-cloud-translate")
        elif api_type == "openai" and not OPENAI_AVAILABLE:
            raise ImportError("请安装 openai: pip install openai")
        
        # 并发设置
        self.max_workers = 5
        
        # 初始化API客户端
        self._init_client()
    
    def _init_client(self):
        """初始化API客户端"""
        if self.api_type == "google-cloud" and self.api_key:
            # 设置Google Cloud认证
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.api_key
        elif self.api_type == "openai" and self.api_key:
            # 配置OpenAI
            openai.api_key = self.api_key
            if self.api_endpoint:
                openai.api_base = self.api_endpoint
    
    def _create_translator(self, target_lang: str):
        """为指定语言创建翻译器实例（线程安全）"""
        if self.api_type == "google-free":
            return GoogleTranslator(source='zh-CN', target=target_lang)
        return None
    
    def _translate_with_google_cloud(self, text: str, target_lang: str) -> str:
        """使用Google Cloud Translation API翻译"""
        client = google_translate.Client()
        # 语言代码映射
        lang_map = {"th": "th", "vi": "vi"}
        result = client.translate(text, target_language=lang_map.get(target_lang, target_lang), source_language='zh-CN')
        return result['translatedText']
    
    def _translate_with_openai(self, text: str, target_lang: str) -> str:
        """使用OpenAI API翻译"""
        lang_names = {"th": "泰语", "vi": "越南语"}
        target_name = lang_names.get(target_lang, target_lang)
        
        # 使用新版OpenAI API
        client = openai.OpenAI(api_key=self.api_key, base_url=self.api_endpoint) if self.api_endpoint else openai.OpenAI(api_key=self.api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"你是一个专业的翻译助手。请将用户提供的中文文本翻译成{target_name}。只返回翻译结果，不要解释。保留所有HTML标签和特殊格式。"},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    
    def _translate_with_deepseek(self, text: str, target_lang: str) -> str:
        """使用DeepSeek API翻译"""
        lang_names = {"th": "泰语", "vi": "越南语"}
        target_name = lang_names.get(target_lang, target_lang)
        
        # DeepSeek API与OpenAI兼容
        base_url = self.api_endpoint or "https://api.deepseek.com"
        client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"你是一个专业的游戏本地化翻译助手。请将用户提供的中文文本翻译成{target_name}。只返回翻译结果，不要解释。保留所有HTML标签和特殊格式如<color=#xxx>。"},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            stream=False
        )
        return response.choices[0].message.content.strip()
    
    def _translate_with_deepl(self, text: str, target_lang: str) -> str:
        """使用DeepL API翻译"""
        import requests
        
        lang_map = {"th": "TH", "vi": "VI"}  # 注意：DeepL可能不支持这些语言
        
        url = "https://api-free.deepl.com/v2/translate"
        if self.api_endpoint:
            url = self.api_endpoint
        
        response = requests.post(url, data={
            "auth_key": self.api_key,
            "text": text,
            "source_lang": "ZH",
            "target_lang": lang_map.get(target_lang, target_lang.upper())
        })
        result = response.json()
        return result['translations'][0]['text']
    
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
            # 根据API类型选择翻译方法
            if self.api_type == "google-free":
                translator = self._create_translator(target_lang)
                translated = translator.translate(pure_text)
            elif self.api_type == "google-cloud":
                translated = self._translate_with_google_cloud(pure_text, target_lang)
            elif self.api_type == "openai":
                translated = self._translate_with_openai(pure_text, target_lang)
            elif self.api_type == "deepseek":
                translated = self._translate_with_deepseek(pure_text, target_lang)
            elif self.api_type == "deepl":
                translated = self._translate_with_deepl(pure_text, target_lang)
            else:
                print(f"不支持的API类型: {self.api_type}")
                return text
            
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
                      delay: float = 0.5, max_workers: int = 5) -> dict:
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
            max_workers: 最大并发线程数（默认5，设为1禁用并发）
            
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
        
        # 收集需要翻译的任务
        tasks = []
        for i, row in enumerate(rows):
            zh_text = row.get("ZH", "")
            
            if translate_th:
                th_text = row.get("TH", "")
                if force or self.needs_translation(zh_text, th_text):
                    tasks.append((i, "TH", "th", zh_text))
                else:
                    stats["skipped_th"] += 1
            
            if translate_vn:
                vn_text = row.get("VN", "")
                if force or self.needs_translation(zh_text, vn_text):
                    tasks.append((i, "VN", "vi", zh_text))
                else:
                    stats["skipped_vn"] += 1
        
        print(f"需要翻译 {len(tasks)} 条内容，使用 {max_workers} 个并发线程")
        
        # 并发翻译
        import threading
        lock = threading.Lock()
        completed = [0]
        
        def translate_task(task):
            idx, col, lang, text = task
            try:
                result = self.translate_text(text, lang)
                time.sleep(delay)
                return (idx, col, lang, result, None)
            except Exception as e:
                return (idx, col, lang, text, str(e))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(translate_task, task): task for task in tasks}
            
            for future in as_completed(futures):
                idx, col, lang, result, error = future.result()
                
                with lock:
                    rows[idx][col] = result
                    completed[0] += 1
                    
                    if error:
                        print(f"[{completed[0]}/{len(tasks)}] {col}翻译错误: {error}")
                        stats["errors"] += 1
                    else:
                        if col == "TH":
                            stats["translated_th"] += 1
                        else:
                            stats["translated_vn"] += 1
                        print(f"[{completed[0]}/{len(tasks)}] {col}: {rows[idx].get('ZH', '')[:20]}... -> {result[:20]}...")
                    
                    # 批量保存
                    if completed[0] % batch_size == 0:
                        self._save_csv(output_file, fieldnames, rows)
                        print(f"已保存进度: {completed[0]}/{len(tasks)}")
        
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
    parser.add_argument("--delay", type=float, default=0.1, help="翻译延迟秒数（默认: 0.1）")
    parser.add_argument("--workers", type=int, default=5, help="并发线程数（默认: 5，设为1禁用并发）")
    
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
        delay=args.delay,
        max_workers=args.workers
    )
    
    # 打印统计
    print("\n=== 翻译统计 ===")
    print(f"总行数: {stats['total_rows']}")
    print(f"翻译TH: {stats['translated_th']} (跳过: {stats['skipped_th']})")
    print(f"翻译VN: {stats['translated_vn']} (跳过: {stats['skipped_vn']})")
    print(f"错误数: {stats['errors']}")


if __name__ == "__main__":
    main()
