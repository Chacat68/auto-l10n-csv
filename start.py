#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV自动翻译工具 - 统一启动器
"""

import sys
import os
import subprocess


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """打印横幅"""
    print("=" * 50)
    print("       CSV自动翻译工具")
    print("=" * 50)
    print()


def check_dependencies():
    """检查依赖"""
    try:
        import googletrans
        import tkinter
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e.name}")
        print()
        print("请先安装依赖:")
        print("  pip install -r requirements.txt")
        print()
        return False


def main():
    """主函数"""
    clear_screen()
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        input("按Enter键退出...")
        return
    
    print("请选择启动方式:")
    print()
    print("  [1] 图形界面 (GUI) - 推荐")
    print("  [2] 命令行 (CLI)")
    print("  [3] 查看帮助")
    print("  [0] 退出")
    print()
    
    choice = input("请输入选项 [1]: ").strip() or "1"
    
    if choice == "1":
        print("\n正在启动图形界面...")
        subprocess.run([sys.executable, "translate_csv_gui.py"])
    
    elif choice == "2":
        print("\n命令行模式:")
        print("用法: python translate_csv.py <输入文件> [选项]")
        print()
        print("示例:")
        print("  python translate_csv.py input.csv")
        print("  python translate_csv.py input.csv -o output.csv")
        print("  python translate_csv.py input.csv -t TH")
        print()
        
        csv_file = input("请输入CSV文件路径 (或按Enter返回): ").strip()
        if csv_file:
            if not os.path.exists(csv_file):
                print(f"\n❌ 文件不存在: {csv_file}")
            else:
                print(f"\n正在处理: {csv_file}")
                subprocess.run([sys.executable, "translate_csv.py", csv_file])
        else:
            main()
    
    elif choice == "3":
        print("\n" + "=" * 50)
        print("帮助信息")
        print("=" * 50)
        print()
        print("图形界面模式 (推荐):")
        print("  - 双击运行 '启动GUI.bat' (Windows)")
        print("  - 或执行: python translate_csv_gui.py")
        print()
        print("命令行模式:")
        print("  python translate_csv.py <输入文件> [选项]")
        print()
        print("可用选项:")
        print("  -o, --output    指定输出文件")
        print("  -s, --source    源语言列 (默认: ZH)")
        print("  -t, --targets   目标语言列 (默认: TH VN)")
        print("  --overwrite     覆盖已有翻译")
        print()
        print("详细文档请查看 README.md")
        print()
        input("按Enter键返回...")
        main()
    
    elif choice == "0":
        print("\n再见！")
    
    else:
        print("\n❌ 无效选项，请重试")
        input("按Enter键继续...")
        main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        input("按Enter键退出...")
