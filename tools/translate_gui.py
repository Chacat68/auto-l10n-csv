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
import sys
import subprocess
from pathlib import Path
from typing import Optional


def check_dependencies():
    """检查并安装所需依赖"""
    missing_packages = []
    
    # 检查 deep-translator
    try:
        import deep_translator
    except ImportError:
        missing_packages.append("deep-translator")
    
    if missing_packages:
        # 创建简单的提示窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        msg = "检测到缺少以下依赖包:\n\n"
        msg += "\n".join(f"  • {pkg}" for pkg in missing_packages)
        msg += "\n\n是否自动安装？"
        
        result = messagebox.askyesno("依赖检查", msg, icon='warning')
        
        if result:
            # 自动安装
            root.destroy()
            
            print("正在安装依赖包...")
            for pkg in missing_packages:
                print(f"  安装 {pkg}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                    print(f"  ✓ {pkg} 安装成功")
                except subprocess.CalledProcessError as e:
                    print(f"  ✗ {pkg} 安装失败: {e}")
                    messagebox.showerror("安装失败", 
                        f"安装 {pkg} 失败!\n\n请手动运行:\npip install {pkg}")
                    sys.exit(1)
            
            print("\n所有依赖安装完成，正在启动程序...")
            # 重新导入模块
            import importlib
            importlib.invalidate_caches()
        else:
            # 用户取消，显示手动安装提示
            install_cmd = "pip install " + " ".join(missing_packages)
            messagebox.showinfo("安装提示", 
                f"请手动安装依赖:\n\n{install_cmd}\n\n或运行:\npip install -r requirements.txt")
            root.destroy()
            sys.exit(0)
    
    return True


# 启动时检查依赖
check_dependencies()

# 依赖检查通过后再导入
from translate_csv import CSVTranslator, load_api_config, save_api_config


class TranslatorApp:
    """翻译工具GUI应用"""
    
    # API类型选项
    API_TYPES = [
        ("google-free", "Google翻译(免费)"),
        ("google-cloud", "Google Cloud API"),
        ("openai", "OpenAI GPT"),
        ("deepseek", "DeepSeek(推荐)"),
        ("deepl", "DeepL API"),
    ]
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CSV翻译工具 - TH/VN")
        self.root.geometry("850x650")
        self.root.minsize(750, 550)
        
        # 状态变量
        self.is_translating = False
        self.translator: Optional[CSVTranslator] = None
        self.log_queue = queue.Queue()
        
        # 加载API配置
        self.api_config = load_api_config()
        
        # 创建UI
        self._create_widgets()
        
        # 加载保存的API设置
        self._load_api_settings()
        
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
        
        # === API设置区域 ===
        api_frame = ttk.LabelFrame(main_frame, text="API设置", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API类型选择
        api_type_frame = ttk.Frame(api_frame)
        api_type_frame.pack(fill=tk.X)
        
        ttk.Label(api_type_frame, text="翻译API:").pack(side=tk.LEFT)
        self.api_type_var = tk.StringVar(value="google-free")
        api_combo = ttk.Combobox(api_type_frame, textvariable=self.api_type_var, 
                                  values=[f"{t[0]} - {t[1]}" for t in self.API_TYPES],
                                  state="readonly", width=30)
        api_combo.pack(side=tk.LEFT, padx=10)
        api_combo.bind("<<ComboboxSelected>>", self._on_api_type_change)
        
        # API Key输入
        self.api_key_frame = ttk.Frame(api_frame)
        self.api_key_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(self.api_key_frame, text="API Key:").pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(self.api_key_frame, textvariable=self.api_key_var, width=50, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=10)
        
        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.api_key_frame, text="显示", variable=self.show_key_var, 
                        command=self._toggle_key_visibility).pack(side=tk.LEFT)
        
        ttk.Button(self.api_key_frame, text="保存设置", command=self._save_api_settings).pack(side=tk.LEFT, padx=10)
        
        # API端点（可选）
        self.api_endpoint_frame = ttk.Frame(api_frame)
        self.api_endpoint_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(self.api_endpoint_frame, text="API端点(可选):").pack(side=tk.LEFT)
        self.api_endpoint_var = tk.StringVar()
        ttk.Entry(self.api_endpoint_frame, textvariable=self.api_endpoint_var, width=50).pack(side=tk.LEFT, padx=10)
        ttk.Label(self.api_endpoint_frame, text="用于OpenAI兼容API", foreground="gray").pack(side=tk.LEFT)
        
        # 根据选择显示/隐藏API Key输入框
        self._on_api_type_change(None)
        
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
        self.delay_var = tk.StringVar(value="0.1")
        delay_spin = ttk.Spinbox(adv_frame, from_=0.0, to=5.0, increment=0.1, width=6, textvariable=self.delay_var)
        delay_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(adv_frame, text="并发线程:").pack(side=tk.LEFT, padx=(20, 0))
        self.workers_var = tk.StringVar(value="5")
        workers_spin = ttk.Spinbox(adv_frame, from_=1, to=20, width=6, textvariable=self.workers_var)
        workers_spin.pack(side=tk.LEFT, padx=5)
        
        # 提示标签
        tip_label = ttk.Label(options_frame, text="💡 提示: 增加并发线程数可加快翻译速度，但过高可能被API限制", 
                              foreground="gray")
        tip_label.pack(anchor=tk.W, pady=(10, 0))
        
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
    
    def _on_api_type_change(self, event):
        """API类型改变时的处理"""
        api_type = self.api_type_var.get().split(" - ")[0]
        
        # 显示/隐藏API Key输入框
        if api_type == "google-free":
            # 免费API不需要Key
            for widget in self.api_key_frame.winfo_children():
                widget.configure(state=tk.DISABLED)
            for widget in self.api_endpoint_frame.winfo_children():
                widget.configure(state=tk.DISABLED)
        else:
            for widget in self.api_key_frame.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Button, ttk.Checkbutton)):
                    widget.configure(state=tk.NORMAL)
            
            # OpenAI和DeepSeek支持自定义端点
            if api_type in ("openai", "deepseek"):
                for widget in self.api_endpoint_frame.winfo_children():
                    if isinstance(widget, ttk.Entry):
                        widget.configure(state=tk.NORMAL)
            else:
                for widget in self.api_endpoint_frame.winfo_children():
                    if isinstance(widget, ttk.Entry):
                        widget.configure(state=tk.DISABLED)
        
        # 加载对应的API Key
        if api_type in self.api_config:
            self.api_key_var.set(self.api_config[api_type].get("api_key", ""))
            self.api_endpoint_var.set(self.api_config[api_type].get("endpoint", ""))
    
    def _toggle_key_visibility(self):
        """切换API Key显示/隐藏"""
        if self.show_key_var.get():
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="*")
    
    def _save_api_settings(self):
        """保存API设置"""
        api_type = self.api_type_var.get().split(" - ")[0]
        
        if api_type not in self.api_config:
            self.api_config[api_type] = {}
        
        self.api_config[api_type]["api_key"] = self.api_key_var.get()
        self.api_config[api_type]["endpoint"] = self.api_endpoint_var.get()
        
        save_api_config(self.api_config)
        messagebox.showinfo("保存成功", f"{api_type} API设置已保存")
    
    def _load_api_settings(self):
        """加载保存的API设置"""
        # 设置默认API类型
        saved_type = self.api_config.get("default_type", "google-free")
        for i, (t, name) in enumerate(self.API_TYPES):
            if t == saved_type:
                self.api_type_var.set(f"{t} - {name}")
                break
        
        # 触发一次类型改变事件
        self._on_api_type_change(None)
    
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
            # 获取API设置
            api_type = self.api_type_var.get().split(" - ")[0]
            api_key = self.api_key_var.get() if api_type != "google-free" else None
            api_endpoint = self.api_endpoint_var.get() if api_type in ("openai", "deepseek") else None
            
            self._log("=" * 50)
            self._log("开始翻译...")
            self._log(f"翻译API: {api_type}")
            self._log(f"输入文件: {input_file}")
            self._log(f"输出文件: {output_file}")
            self._log(f"目标语言: {'TH ' if self.th_var.get() else ''}{'VN' if self.vn_var.get() else ''}")
            self._log("=" * 50)
            
            # 验证API Key
            if api_type != "google-free" and not api_key:
                self._log("错误: 请填写API Key")
                self.root.after(0, lambda: messagebox.showerror("错误", "请填写API Key"))
                return
            
            # 创建翻译器
            translator = CSVTranslator(api_type=api_type, api_key=api_key, api_endpoint=api_endpoint)
            
            # 保存当前使用的API类型
            self.api_config["default_type"] = api_type
            save_api_config(self.api_config)
            
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
            max_workers = int(self.workers_var.get())
            force = self.force_var.get()
            translate_th = self.th_var.get()
            translate_vn = self.vn_var.get()
            
            # 收集需要翻译的任务
            tasks = []
            for i, row in enumerate(rows):
                zh_text = row.get("ZH", "")
                
                if translate_th:
                    th_text = row.get("TH", "")
                    if force or translator.needs_translation(zh_text, th_text):
                        tasks.append((i, "TH", "th", zh_text))
                    else:
                        skipped += 1
                
                if translate_vn:
                    vn_text = row.get("VN", "")
                    if force or translator.needs_translation(zh_text, vn_text):
                        tasks.append((i, "VN", "vi", zh_text))
                    else:
                        skipped += 1
            
            self._log(f"需要翻译 {len(tasks)} 条内容，使用 {max_workers} 个并发线程")
            
            if not tasks:
                self._log("没有需要翻译的内容")
            else:
                # 并发翻译
                from concurrent.futures import ThreadPoolExecutor, as_completed
                import time as time_module
                
                completed_count = [0]
                lock = threading.Lock()
                
                def translate_task(task):
                    if not self.is_translating:
                        return None
                    idx, col, lang, text = task
                    try:
                        result = translator.translate_text(text, lang)
                        time_module.sleep(delay)
                        return (idx, col, lang, result, None)
                    except Exception as e:
                        return (idx, col, lang, text, str(e))
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(translate_task, task): task for task in tasks}
                    
                    for future in as_completed(futures):
                        if not self.is_translating:
                            executor.shutdown(wait=False, cancel_futures=True)
                            break
                        
                        result = future.result()
                        if result is None:
                            continue
                            
                        idx, col, lang, translated, error = result
                        
                        with lock:
                            rows[idx][col] = translated
                            completed_count[0] += 1
                            
                            # 更新进度
                            progress = completed_count[0] / len(tasks) * 100
                            self.progress_var.set(progress)
                            self.root.after(0, lambda p=progress, c=completed_count[0], t=len(tasks): 
                                self.progress_label.config(text=f"进度: {c}/{t} ({p:.1f}%)"))
                            
                            if error:
                                self._log(f"[{completed_count[0]}/{len(tasks)}] {col}翻译错误: {error}")
                                errors += 1
                            else:
                                if col == "TH":
                                    translated_th += 1
                                else:
                                    translated_vn += 1
                                zh_short = rows[idx].get('ZH', '')[:20]
                                tr_short = translated[:20] if translated else ''
                                self._log(f"[{completed_count[0]}/{len(tasks)}] {col}: {zh_short}... -> {tr_short}...")
                            
                            # 批量保存
                            if completed_count[0] % batch_size == 0:
                                self._save_csv(output_file, fieldnames, rows)
                                self._log(f"已保存进度: {completed_count[0]}/{len(tasks)}")
            
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
