#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试DeepSeek翻译API
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 检查API Key
API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

if not API_KEY:
    print("=" * 50)
    print("请设置 DEEPSEEK_API_KEY 环境变量")
    print("或者直接在下面输入你的API Key:")
    print("=" * 50)
    API_KEY = input("DeepSeek API Key: ").strip()
    
    if not API_KEY:
        print("未提供API Key，退出测试")
        sys.exit(1)

print("\n正在测试DeepSeek翻译API...\n")

try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.deepseek.com"
    )
    
    # 测试文本
    test_texts = [
        "打狗棒",
        "屠龙刀",
        "对敌方随机敌人造成绝对伤害",
        "<color=#ffa500>史诗诡术：2.2%</color>",
    ]
    
    print("=" * 60)
    print("测试泰语翻译 (TH)")
    print("=" * 60)
    
    for text in test_texts:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的游戏本地化翻译助手。请将用户提供的中文文本翻译成泰语。只返回翻译结果，不要解释。保留所有HTML标签和特殊格式如<color=#xxx>。"},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            stream=False
        )
        result = response.choices[0].message.content.strip()
        print(f"原文: {text}")
        print(f"泰语: {result}")
        print()
    
    print("=" * 60)
    print("测试越南语翻译 (VN)")
    print("=" * 60)
    
    for text in test_texts:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的游戏本地化翻译助手。请将用户提供的中文文本翻译成越南语。只返回翻译结果，不要解释。保留所有HTML标签和特殊格式如<color=#xxx>。"},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            stream=False
        )
        result = response.choices[0].message.content.strip()
        print(f"原文: {text}")
        print(f"越南语: {result}")
        print()
    
    print("=" * 60)
    print("✅ DeepSeek API 测试成功!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
