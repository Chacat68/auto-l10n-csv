#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译接口测试脚本
"""

from googletrans import Translator
import requests
import time

def test_google_translate():
    """测试Google翻译"""
    print("=" * 50)
    print("测试 Google 翻译接口")
    print("=" * 50)
    
    test_texts = [
        "低级残卷",
        "中级残卷", 
        "高级残卷"
    ]
    
    # 测试多个服务地址
    service_urls = [
        ['translate.google.com'],
        ['translate.google.cn'],
        None  # 使用默认
    ]
    
    for idx, urls in enumerate(service_urls, 1):
        print(f"\n测试配置 {idx}: {urls or '默认'}")
        try:
            translator = Translator(service_urls=urls) if urls else Translator()
            
            for text in test_texts:
                try:
                    # 翻译成泰语
                    result_th = translator.translate(text, src='zh-cn', dest='th')
                    print(f"  ✅ {text} -> TH: {result_th.text}")
                    
                    # 翻译成越南语
                    result_vn = translator.translate(text, src='zh-cn', dest='vi')
                    print(f"  ✅ {text} -> VN: {result_vn.text}")
                    
                    time.sleep(0.2)  # 避免速率限制
                    
                except Exception as e:
                    print(f"  ❌ 翻译失败: {text} - {str(e)[:50]}")
                    
        except Exception as e:
            print(f"  ❌ 初始化失败: {str(e)[:50]}")


def test_mymemory_api():
    """测试MyMemory API"""
    print("\n" + "=" * 50)
    print("测试 MyMemory 翻译接口")
    print("=" * 50)
    
    test_texts = [
        "低级残卷",
        "中级残卷"
    ]
    
    for text in test_texts:
        try:
            # 翻译成泰语
            url = "https://api.mymemory.translated.net/get"
            params_th = {
                'q': text,
                'langpair': 'zh-CN|th-TH'
            }
            response_th = requests.get(url, params=params_th, timeout=10)
            if response_th.status_code == 200:
                data_th = response_th.json()
                if data_th.get('responseStatus') == 200:
                    print(f"  ✅ {text} -> TH: {data_th['responseData']['translatedText']}")
            
            # 翻译成越南语
            params_vn = {
                'q': text,
                'langpair': 'zh-CN|vi-VN'
            }
            response_vn = requests.get(url, params=params_vn, timeout=10)
            if response_vn.status_code == 200:
                data_vn = response_vn.json()
                if data_vn.get('responseStatus') == 200:
                    print(f"  ✅ {text} -> VN: {data_vn['responseData']['translatedText']}")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ 翻译失败: {text} - {str(e)}")


def main():
    print("\n🌍 开始测试翻译接口...\n")
    
    # 测试Google翻译
    test_google_translate()
    
    # 测试备用API
    test_mymemory_api()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == '__main__':
    main()
