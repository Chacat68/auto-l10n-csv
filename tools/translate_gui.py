#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV翻译工具 - 图形界面客户端
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import csv
import os
from pathlib import Path
from typing import Optional

from translate_csv import CSVTranslator


class TranslatorApp:
    """翻译工具GUI应用"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CSV翻译工具 - TH/VN")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 状态变量
        self.is_translating = False
        self.translator: Optional[CSVTranslator] = None
        self.log_queue = queue.Queue()
        
        # 创建UI
        self._create_widgets()
        
        # 启动日志更新
        self._update_log()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === 文件选择区域 ===
        file_frame = ttk.LabelFrame(main_frame, text="文件设置", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 输入文件
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(file_frame, textvariable=self.input_var, width=60)
        self.input_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Button(file_frame, text="浏览...", command=self._browse_input).grid(row=0, column=2, pady=2)
        
        # 输出文件
        ttk.Label(file_frame, text="输出文件:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(file_frame, textvariable=self.output_var, width=60)
        self.output_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Button(file_frame, text="浏览...", command=self._browse_output).grid(row=1, column=2, pady=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # === 翻译选项区域 ===
        options_frame = ttk.LabelFrame(main_frame, text="翻译选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 语言选择
        lang_frame = ttk.Frame(options_frame)
        lang_frame.pack(fill=tk.X)
        
        ttk.Label(lang_frame, text="目标语言:").pack(side=tk.LEFT)
        
        self.th_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(lang_frame, text="泰语 (TH)", variable=self.th_var).pack(side=tk.LEFT, padx=10)
        
        self.vn_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(lang_frame, text="越南语 (VN)", variable=self.vn_var).pack(side=tk.LEFT, padx=10)
        
        self.force_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(lang_frame, text="强制翻译 (覆盖已有翻译)", variable=self.force_var).pack(side=tk.LEFT, padx=20)
        
        # 高级选项
        adv_frame = ttk.Frame(options_frame)
        adv_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(adv_frame, text="批处理大小:").pack(side=tk.LEFT)
        self.batch_var = tk.StringVar(value="10")
        batch_spin = ttk.Spinbox(adv_frame, from_=1, to=100, width=6, textvariable=self.batch_var)
        batch_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(adv_frame, text="延迟(秒):").pack(side=tk.LEFT, padx=(20, 0))
        self.delay_var = tk.StringVar(value="0.5")
        delay_spin = ttk.Spinbox(adv_frame, from_=0.1, to=5.0, increment=0.1, width=6, textvariable=self.delay_var)
        delay_spin.pack(side=tk.LEFT, padx=5)
        
        # === 控制按钮区域 ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(btn_frame, text="开始翻译", command=self._start_translation, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self._stop_translation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="预览文件", command=self._preview_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="清空日志", command=self._clear_log).pack(side=tk.RIGHT, padx=5)
        
        # === 进度条 ===
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # 进度标签
        self.progress_label = ttk.Label(main_frame, text="就绪")
        self.progress_label.pack(anchor=tk.W)
        
        # === 日志区域 ===
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _browse_input(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialdir=os.path.join(os.path.dirname(__file__), "..", "CSV")
        )
        if filename:
            self.input_var.set(filename)
            # 自动设置输出文件名
            input_path = Path(filename)
            output_name = f"{input_path.stem}_translated{input_path.suffix}"
            self.output_var.set(str(input_path.parent / output_name))
    
    def _browse_output(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="保存翻译结果",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            defaultextension=".csv"
        )
        if filename:
            self.output_var.set(filename)
    
    def _log(self, message: str):
        """添加日志消息"""
        self.log_queue.put(message)
    
    def _update_log(self):
        """更新日志显示"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        
        self.root.after(100, self._update_log)
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _preview_file(self):
        """预览CSV文件"""
        input_file = self.input_var.get()
        if not input_file:
            messagebox.showwarning("警告", "请先选择输入文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", f"文件不存在: {input_file}")
            return
        
        # 创建预览窗口
        preview_win = tk.Toplevel(self.root)
        preview_win.title(f"预览 - {os.path.basename(input_file)}")
        preview_win.geometry("900x500")
        
        # 创建Treeview
        tree_frame = ttk.Frame(preview_win)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 读取CSV并显示
        try:
            with open(input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames
                
                # 创建Treeview
                tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
                
                # 设置列
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=100, minwidth=50)
                
                # 添加滚动条
                vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
                tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
                
                # 布局
                tree.grid(row=0, column=0, sticky="nsew")
                vsb.grid(row=0, column=1, sticky="ns")
                hsb.grid(row=1, column=0, sticky="ew")
                tree_frame.columnconfigure(0, weight=1)
                tree_frame.rowconfigure(0, weight=1)
                
                # 添加数据（只显示前100行）
                for i, row in enumerate(reader):
                    if i >= 100:
                        break
                    values = [row.get(col, '') for col in columns]
                    tree.insert('', tk.END, values=values)
                
                # 统计信息
                f.seek(0)
                total_rows = sum(1 for _ in f) - 1
                
            ttk.Label(preview_win, text=f"共 {total_rows} 行数据 (预览前100行)").pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {e}")
            preview_win.destroy()
    
    def _start_translation(self):
        """开始翻译"""
        # 验证输入
        input_file = self.input_var.get()
        output_file = self.output_var.get()
        
        if not input_file:
            messagebox.showwarning("警告", "请选择输入文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", f"输入文件不存在: {input_file}")
            return
        
        if not output_file:
            messagebox.showwarning("警告", "请指定输出文件")
            return
        
        if not self.th_var.get() and not self.vn_var.get():
            messagebox.showwarning("警告", "请至少选择一种目标语言")
            return
        
        # 开始翻译
        self.is_translating = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # 在后台线程执行翻译
        thread = threading.Thread(target=self._do_translation, daemon=True)
        thread.start()
    
    def _do_translation(self):
        """执行翻译（后台线程）"""
        input_file = self.input_var.get()
        output_file = self.output_var.get()
        
        try:
            self._log("=" * 50)
            self._log("开始翻译...")
            self._log(f"输入文件: {input_file}")
            self._log(f"输出文件: {output_file}")
            self._log(f"目标语言: {'TH ' if self.th_var.get() else ''}{'VN' if self.vn_var.get() else ''}")
            self._log("=" * 50)
            
            # 创建翻译器
            translator = CSVTranslator(translator_type="google")
            
            # 读取CSV
            rows = []
            with open(input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    rows.append(row)
            
            total_rows = len(rows)
            self._log(f"共读取 {total_rows} 行数据")
            
            translated_th = 0
            translated_vn = 0
            skipped = 0
            errors = 0
            
            batch_size = int(self.batch_var.get())
            delay = float(self.delay_var.get())
            force = self.force_var.get()
            translate_th = self.th_var.get()
            translate_vn = self.vn_var.get()
            
            for i, row in enumerate(rows):
                if not self.is_translating:
                    self._log("\n翻译已停止")
                    break
                
                zh_text = row.get("ZH", "")
                
                # 更新进度
                progress = (i + 1) / total_rows * 100
                self.progress_var.set(progress)
                self.root.after(0, lambda p=progress, c=i+1, t=total_rows: 
                    self.progress_label.config(text=f"进度: {c}/{t} ({p:.1f}%)"))
                
                # 翻译TH
                if translate_th:
                    th_text = row.get("TH", "")
                    if force or translator.needs_translation(zh_text, th_text):
                        try:
                            row["TH"] = translator.translate_text(zh_text, "th")
                            translated_th += 1
                            self._log(f"[{i+1}/{total_rows}] TH: {zh_text[:30]}... -> {row['TH'][:30]}...")
                            import time
                            time.sleep(delay)
                        except Exception as e:
                            self._log(f"[{i+1}/{total_rows}] TH翻译错误: {e}")
                            errors += 1
                    else:
                        skipped += 1
                
                # 翻译VN
                if translate_vn:
                    vn_text = row.get("VN", "")
                    if force or translator.needs_translation(zh_text, vn_text):
                        try:
                            row["VN"] = translator.translate_text(zh_text, "vi")
                            translated_vn += 1
                            self._log(f"[{i+1}/{total_rows}] VN: {zh_text[:30]}... -> {row['VN'][:30]}...")
                            import time
                            time.sleep(delay)
                        except Exception as e:
                            self._log(f"[{i+1}/{total_rows}] VN翻译错误: {e}")
                            errors += 1
                    else:
                        skipped += 1
                
                # 批量保存
                if (i + 1) % batch_size == 0:
                    self._save_csv(output_file, fieldnames, rows)
                    self._log(f"已保存进度: {i+1}/{total_rows}")
            
            # 最终保存
            self._save_csv(output_file, fieldnames, rows)
            
            self._log("")
            self._log("=" * 50)
            self._log("翻译完成!")
            self._log(f"翻译TH: {translated_th} 条")
            self._log(f"翻译VN: {translated_vn} 条")
            self._log(f"跳过: {skipped} 条")
            self._log(f"错误: {errors} 条")
            self._log(f"输出文件: {output_file}")
            self._log("=" * 50)
            
            self.progress_var.set(100)
            self.root.after(0, lambda: self.progress_label.config(text="完成!"))
            
            if self.is_translating:
                self.root.after(0, lambda: messagebox.showinfo("完成", 
                    f"翻译完成!\n\nTH: {translated_th} 条\nVN: {translated_vn} 条\n跳过: {skipped} 条\n错误: {errors} 条"))
            
        except Exception as e:
            self._log(f"\n错误: {e}")
            self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
        
        finally:
            self.is_translating = False
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
    
    def _save_csv(self, output_file: str, fieldnames: list, rows: list):
        """保存CSV文件"""
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    def _stop_translation(self):
        """停止翻译"""
        self.is_translating = False
        self._log("\n正在停止翻译...")


def main():
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    try:
        style.theme_use('vista')  # Windows
    except:
        try:
            style.theme_use('clam')  # Linux/Mac
        except:
            pass
    
    app = TranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
