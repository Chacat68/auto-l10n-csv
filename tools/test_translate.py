#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试翻译工具
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from translate_csv import CSVTranslator

def test_translation():
    """测试基本翻译功能"""
    print("=== 测试翻译工具 ===\n")
    
    translator = CSVTranslator(translator_type="google")
    
    # 测试文本列表
    test_texts = [
        "打狗棒",
        "圣火令",
        "屠龙刀",
        "低级残卷",
        "<color=#ffa500>史诗诡术：2.2%</color>",
        "对敌方随机敌人造成绝对伤害，并有概率对其施加流血",
    ]
    
    print("测试泰语翻译 (TH):")
    print("-" * 50)
    for text in test_texts[:3]:  # 只测试前3个，节省时间
        result = translator.translate_text(text, "th")
        print(f"原文: {text}")
        print(f"翻译: {result}")
        print()
    
    print("\n测试越南语翻译 (VN):")
    print("-" * 50)
    for text in test_texts[:3]:  # 只测试前3个，节省时间
        result = translator.translate_text(text, "vi")
        print(f"原文: {text}")
        print(f"翻译: {result}")
        print()
    
    print("\n测试带颜色标签的文本:")
    print("-" * 50)
    text = "<color=#ffa500>史诗诡术：2.2%</color>"
    result_th = translator.translate_text(text, "th")
    result_vi = translator.translate_text(text, "vi")
    print(f"原文: {text}")
    print(f"泰语: {result_th}")
    print(f"越南语: {result_vi}")

if __name__ == "__main__":
    test_translation()
