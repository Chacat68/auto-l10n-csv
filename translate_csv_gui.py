#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV自动翻译工具 - GUI版本 (CustomTkinter)
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv
import os
import threading
import time
from typing import List
from googletrans import Translator

# 设置外观模式和默认颜色主题
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# 自定义配色方案
COLOR_SCHEME = {
    "primary": "#2196F3",      # 主色调 - 蓝色
    "primary_dark": "#1976D2", # 深蓝色
    "success": "#4CAF50",      # 成功 - 绿色
    "success_dark": "#388E3C", # 深绿色
    "danger": "#F44336",       # 危险 - 红色
    "danger_dark": "#D32F2F",  # 深红色
    "warning": "#FF9800",      # 警告 - 橙色
    "info": "#00BCD4",         # 信息 - 青色
    "title_bg": ("#E3F2FD", "#1E3A5F"),  # 标题栏背景
    "card_bg": ("#FFFFFF", "#2B2B2B"),   # 卡片背景
}


class TranslatorGUI:
    """CSV翻译器GUI - 现代化界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CSV自动翻译工具")
        self.root.geometry("1000x750")
        
        # 设置窗口图标（如果有的话）
        # self.root.iconbitmap("icon.ico")
        
        self.translator = Translator()
        self.translation_cache = {}
        self.is_translating = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        # 配置网格布局
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # 主容器
        main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # 标题栏 - 渐变效果
        title_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SCHEME["title_bg"], corner_radius=0)
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        title_label = ctk.CTkLabel(title_frame, text="🌍 CSV自动翻译工具", 
                                   font=ctk.CTkFont(size=26, weight="bold"),
                                   text_color=("#1976D2", "#64B5F6"))
        title_label.pack(pady=20)
        
        # 文件选择区域
        file_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SCHEME["card_bg"], corner_radius=10)
        file_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 15))
        file_frame.grid_columnconfigure(1, weight=1)
        
        # 输入文件
        ctk.CTkLabel(file_frame, text="输入文件:", 
                    font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.input_file_var = ctk.StringVar()
        self.input_entry = ctk.CTkEntry(file_frame, textvariable=self.input_file_var, 
                                       height=35, font=ctk.CTkFont(size=12))
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=(15, 5))
        
        browse_input_btn = ctk.CTkButton(file_frame, text="📁 浏览", 
                                        command=self.browse_input_file, width=100, height=35,
                                        fg_color=COLOR_SCHEME["primary"],
                                        hover_color=COLOR_SCHEME["primary_dark"])
        browse_input_btn.grid(row=0, column=2, padx=(0, 15), pady=(15, 5))
        
        # 输出文件
        ctk.CTkLabel(file_frame, text="输出文件:", 
                    font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=15, pady=(5, 15))
        
        self.output_file_var = ctk.StringVar()
        self.output_entry = ctk.CTkEntry(file_frame, textvariable=self.output_file_var,
                                        height=35, font=ctk.CTkFont(size=12))
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=(5, 15))
        
        browse_output_btn = ctk.CTkButton(file_frame, text="📁 浏览", 
                                         command=self.browse_output_file, width=100, height=35,
                                         fg_color=COLOR_SCHEME["primary"],
                                         hover_color=COLOR_SCHEME["primary_dark"])
        browse_output_btn.grid(row=1, column=2, padx=(0, 15), pady=(5, 15))
        
        # 配置区域
        config_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SCHEME["card_bg"], corner_radius=10)
        config_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 15))
        config_frame.grid_columnconfigure(1, weight=1)
        
        # 源语言列
        ctk.CTkLabel(config_frame, text="源语言列:", 
                    font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.source_col_var = ctk.StringVar(value="ZH")
        source_entry = ctk.CTkEntry(config_frame, textvariable=self.source_col_var,
                                    width=150, height=35, font=ctk.CTkFont(size=12))
        source_entry.grid(row=0, column=1, sticky="w", padx=10, pady=(15, 5))
        
        # 目标语言列
        ctk.CTkLabel(config_frame, text="目标语言:", 
                    font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=15, pady=5)
        
        target_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        target_frame.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        self.translate_th_var = ctk.BooleanVar(value=True)
        self.translate_vn_var = ctk.BooleanVar(value=True)
        
        th_checkbox = ctk.CTkCheckBox(target_frame, text="🇹🇭 TH (泰语)", 
                                     variable=self.translate_th_var,
                                     font=ctk.CTkFont(size=13))
        th_checkbox.pack(side="left", padx=(0, 20))
        
        vn_checkbox = ctk.CTkCheckBox(target_frame, text="🇻🇳 VN (越南语)", 
                                     variable=self.translate_vn_var,
                                     font=ctk.CTkFont(size=13))
        vn_checkbox.pack(side="left")
        
        # 选项
        ctk.CTkLabel(config_frame, text="选项:", 
                    font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=2, column=0, sticky="w", padx=15, pady=(5, 15))
        
        self.skip_existing_var = ctk.BooleanVar(value=True)
        skip_checkbox = ctk.CTkCheckBox(config_frame, text="⏭️ 跳过已有翻译", 
                                       variable=self.skip_existing_var,
                                       font=ctk.CTkFont(size=13))
        skip_checkbox.grid(row=2, column=1, sticky="w", padx=10, pady=(5, 15))
        
        # 进度区域
        progress_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SCHEME["card_bg"], corner_radius=10)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 15))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_var = ctk.StringVar(value="就绪 ✨")
        progress_label = ctk.CTkLabel(progress_frame, textvariable=self.progress_var,
                                     font=ctk.CTkFont(size=13))
        progress_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=20,
                                               progress_color=COLOR_SCHEME["success"])
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 15))
        self.progress_bar.set(0)
        
        # 日志区域
        log_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SCHEME["card_bg"], corner_radius=10)
        log_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 15))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        
        ctk.CTkLabel(log_frame, text="📋 翻译日志:", 
                    font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.log_text = ctk.CTkTextbox(log_frame, height=250, font=ctk.CTkFont(size=11),
                                       wrap="word")
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 15))
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 20))
        
        self.start_button = ctk.CTkButton(button_frame, text="▶️ 开始翻译", 
                                         command=self.start_translation,
                                         width=150, height=40,
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         fg_color=COLOR_SCHEME["success"],
                                         hover_color=COLOR_SCHEME["success_dark"],
                                         corner_radius=8)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(button_frame, text="⏹️ 停止", 
                                        command=self.stop_translation,
                                        width=150, height=40,
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color=COLOR_SCHEME["danger"],
                                        hover_color=COLOR_SCHEME["danger_dark"],
                                        corner_radius=8,
                                        state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        clear_button = ctk.CTkButton(button_frame, text="🗑️ 清空日志", 
                                    command=self.clear_log,
                                    width=150, height=40,
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    fg_color=COLOR_SCHEME["warning"],
                                    hover_color=("#F57C00", "#E65100"),
                                    corner_radius=8)
        clear_button.pack(side="left", padx=5)
    
    def browse_input_file(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="选择输入CSV文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
            # 自动设置输出文件名
            if not self.output_file_var.get():
                base, ext = os.path.splitext(filename)
                self.output_file_var.set(f"{base}_translated{ext}")
    
    def browse_output_file(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="选择输出CSV文件",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
    
    def log(self, message):
        """添加日志"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", "end")
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'zh-cn') -> str:
        """翻译文本"""
        if not text or text.strip() == '':
            return ''
        
        cache_key = f"{text}_{source_lang}_{target_lang}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            result = self.translator.translate(text, src=source_lang, dest=target_lang)
            translated = result.text
            self.translation_cache[cache_key] = translated
            time.sleep(0.1)  # 避免API速率限制
            return translated
        except Exception as e:
            self.log(f"翻译失败: {text[:30]}... -> {target_lang}, 错误: {str(e)}")
            return text
    
    def start_translation(self):
        """开始翻译"""
        # 验证输入
        input_file = self.input_file_var.get()
        output_file = self.output_file_var.get()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请指定输出文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", f"输入文件不存在: {input_file}")
            return
        
        # 获取目标列
        target_cols = []
        if self.translate_th_var.get():
            target_cols.append('TH')
        if self.translate_vn_var.get():
            target_cols.append('VN')
        
        if not target_cols:
            messagebox.showerror("错误", "请至少选择一个目标语言")
            return
        
        # 禁用开始按钮，启用停止按钮
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        # 在新线程中执行翻译
        thread = threading.Thread(target=self.do_translation, 
                                 args=(input_file, output_file, target_cols))
        thread.daemon = True
        thread.start()
    
    def stop_translation(self):
        """停止翻译"""
        self.is_translating = False
        self.log("正在停止翻译...")
    
    def do_translation(self, input_file: str, output_file: str, target_cols: List[str]):
        """执行翻译任务"""
        try:
            source_col = self.source_col_var.get()
            skip_existing = self.skip_existing_var.get()
            
            lang_map = {'TH': 'th', 'VN': 'vi'}
            
            self.log(f"开始处理文件: {input_file}")
            self.log(f"源语言列: {source_col}")
            self.log(f"目标列: {', '.join(target_cols)}")
            self.log("")
            
            # 读取CSV文件
            with open(input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                rows = list(reader)
            
            # 检查列名
            if source_col not in fieldnames:
                raise ValueError(f"源列 '{source_col}' 不存在于CSV文件中")
            
            for col in target_cols:
                if col not in fieldnames:
                    raise ValueError(f"目标列 '{col}' 不存在于CSV文件中")
            
            total_rows = len(rows)
            self.log(f"共 {total_rows} 行数据\n")
            
            self.progress_bar.set(0)
            
            # 翻译每一行
            for idx, row in enumerate(rows, 1):
                if not self.is_translating:
                    self.log("\n翻译已停止")
                    break
                
                source_text = row.get(source_col, '').strip()
                
                if not source_text:
                    progress_percent = idx / total_rows
                    self.progress_var.set(f"⏳ 进度: {idx}/{total_rows} (跳过空行)")
                    self.progress_bar.set(progress_percent)
                    continue
                
                progress_percent = idx / total_rows
                self.progress_var.set(f"⏳ 翻译中: {idx}/{total_rows} ({int(progress_percent*100)}%)")
                self.log(f"[{idx}/{total_rows}] 处理: {source_text[:40]}...")
                
                for target_col in target_cols:
                    if not self.is_translating:
                        break
                    
                    if skip_existing and row.get(target_col, '').strip():
                        self.log(f"  - {target_col}: 已有翻译，跳过")
                        continue
                    
                    target_lang = lang_map.get(target_col)
                    if not target_lang:
                        continue
                    
                    translated = self.translate_text(source_text, target_lang)
                    row[target_col] = translated
                    self.log(f"  - {target_col}: {translated[:40]}...")
                
                self.progress_bar.set(progress_percent)
                self.log("")
            
            if self.is_translating:
                # 写入输出文件
                with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                
                self.log(f"✅ 翻译完成！输出文件: {output_file}")
                self.log(f"📊 共处理 {total_rows} 行数据")
                self.progress_var.set("✅ 完成!")
                self.progress_bar.set(1.0)
                messagebox.showinfo("完成", f"✅ 翻译完成！\n\n输出文件:\n{output_file}")
            
        except Exception as e:
            self.log(f"\n❌ 错误: {str(e)}")
            messagebox.showerror("错误", f"❌ 翻译过程中出现错误:\n\n{str(e)}")
            self.progress_var.set("❌ 错误")
        
        finally:
            # 恢复按钮状态
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.is_translating = False


def main():
    """主函数"""
    root = ctk.CTk()
    app = TranslatorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
