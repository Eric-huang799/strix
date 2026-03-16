"""
Strix v2.0 - Plugin Manager Dialog
插件管理对话框 - 支持添加和管理插件
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import shutil


class PluginManagerDialog:
    """插件管理对话框"""
    
    def __init__(self, parent, plugin_manager, style_config):
        self.parent = parent
        self.plugin_manager = plugin_manager
        self.style = style_config
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("插件管理 - Strix")
        self.dialog.geometry("900x600")
        self.dialog.minsize(700, 500)
        self.dialog.configure(bg=self.style['BG_PRIMARY'])
        
        # 模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        self._load_template()
        self._refresh_plugin_list()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = tk.Frame(self.dialog, bg=self.style['BG_PRIMARY'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title = tk.Label(main_frame,
                        text="插件管理",
                        font=(self.style['FONT_FAMILY'], 18, 'bold'),
                        bg=self.style['BG_PRIMARY'],
                        fg=self.style['ACCENT'])
        title.pack(anchor='w', pady=(0, 10))
        
        # 说明文字
        desc = tk.Label(main_frame,
                       text="左侧是插件模板，右侧可以添加新插件或管理已有插件",
                       font=(self.style['FONT_FAMILY'], 10),
                       bg=self.style['BG_PRIMARY'],
                       fg=self.style['TEXT_SECONDARY'])
        desc.pack(anchor='w', pady=(0, 15))
        
        # 左右分栏
        content_frame = tk.Frame(main_frame, bg=self.style['BG_PRIMARY'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # ===== 左侧：模板 =====
        left_frame = tk.Frame(content_frame, bg=self.style['BG_CARD'], padx=15, pady=15)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        left_title = tk.Label(left_frame,
                             text="插件模板",
                             font=(self.style['FONT_FAMILY'], 12, 'bold'),
                             bg=self.style['BG_CARD'],
                             fg=self.style['TEXT_PRIMARY'])
        left_title.pack(anchor='w', pady=(0, 10))
        
        # 模板文本框
        self.template_text = tk.Text(left_frame,
                                     font=('Consolas', 9),
                                     bg=self.style['BG_SECONDARY'],
                                     fg=self.style['TEXT_PRIMARY'],
                                     relief='flat',
                                     wrap=tk.NONE,
                                     padx=10,
                                     pady=10,
                                     height=20)
        self.template_text.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scroll_y = tk.Scrollbar(self.template_text, command=self.template_text.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.template_text.config(yscrollcommand=scroll_y.set)
        
        scroll_x = tk.Scrollbar(self.template_text, orient='horizontal', command=self.template_text.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.template_text.config(xscrollcommand=scroll_x.set)
        
        # 复制按钮
        copy_btn = tk.Button(left_frame,
                            text="复制模板到剪贴板",
                            font=(self.style['FONT_FAMILY'], 10),
                            bg=self.style['ACCENT'],
                            fg='white',
                            activebackground=self.style['ACCENT_HOVER'],
                            relief='flat',
                            padx=15,
                            pady=5,
                            cursor='hand2',
                            command=self._copy_template)
        copy_btn.pack(fill=tk.X, pady=(10, 0))
        
        # 创建新插件按钮
        new_btn = tk.Button(left_frame,
                           text="创建新插件文件",
                           font=(self.style['FONT_FAMILY'], 10),
                           bg=self.style['BG_SECONDARY'],
                           fg=self.style['TEXT_PRIMARY'],
                           activebackground=self.style['BG_CARD'],
                           relief='flat',
                           padx=15,
                           pady=5,
                           cursor='hand2',
                           command=self._create_new_plugin)
        new_btn.pack(fill=tk.X, pady=(5, 0))
        
        # ===== 右侧：添加插件 =====
        right_frame = tk.Frame(content_frame, bg=self.style['BG_CARD'], padx=15, pady=15)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        
        right_title = tk.Label(right_frame,
                              text="添加插件",
                              font=(self.style['FONT_FAMILY'], 12, 'bold'),
                              bg=self.style['BG_CARD'],
                              fg=self.style['TEXT_PRIMARY'])
        right_title.pack(anchor='w', pady=(0, 10))
        
        # 添加方式说明
        hint = tk.Label(right_frame,
                       text="步骤:\n1. 编写插件文件(.py)\n2. 点击按钮选择文件\n3. 插件自动安装并加载",
                       font=(self.style['FONT_FAMILY'], 10),
                       bg=self.style['BG_CARD'],
                       fg=self.style['TEXT_SECONDARY'],
                       justify='left')
        hint.pack(anchor='w', pady=(0, 15))
        
        # 选择文件按钮
        select_btn = tk.Button(right_frame,
                              text="选择插件文件",
                              font=(self.style['FONT_FAMILY'], 12, 'bold'),
                              bg=self.style['SUCCESS'],
                              fg='white',
                              activebackground='#8fb666',
                              relief='flat',
                              padx=20,
                              pady=12,
                              cursor='hand2',
                              command=self._select_file)
        select_btn.pack(fill=tk.X, pady=(0, 15))
        
        # 打开插件文件夹按钮
        open_btn = tk.Button(right_frame,
                            text="打开插件文件夹",
                            font=(self.style['FONT_FAMILY'], 10),
                            bg=self.style['BG_SECONDARY'],
                            fg=self.style['TEXT_PRIMARY'],
                            activebackground=self.style['BG_CARD'],
                            relief='flat',
                            padx=15,
                            pady=8,
                            cursor='hand2',
                            command=self._open_plugin_folder)
        open_btn.pack(fill=tk.X)
        
        # ===== 底部：已安装插件列表 =====
        bottom_frame = tk.Frame(main_frame, bg=self.style['BG_CARD'], padx=15, pady=15)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        bottom_title = tk.Label(bottom_frame,
                               text="已安装插件",
                               font=(self.style['FONT_FAMILY'], 12, 'bold'),
                               bg=self.style['BG_CARD'],
                               fg=self.style['TEXT_PRIMARY'])
        bottom_title.pack(anchor='w', pady=(0, 10))
        
        # 插件列表
        list_frame = tk.Frame(bottom_frame, bg=self.style['BG_CARD'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.plugin_tree = ttk.Treeview(list_frame,
                                       columns=('name', 'domains', 'status'),
                                       show='headings',
                                       height=6)
        self.plugin_tree.heading('name', text='插件名称')
        self.plugin_tree.heading('domains', text='支持域名')
        self.plugin_tree.heading('status', text='状态')
        self.plugin_tree.column('name', width=150)
        self.plugin_tree.column('domains', width=300)
        self.plugin_tree.column('status', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.plugin_tree.yview)
        self.plugin_tree.configure(yscrollcommand=scrollbar.set)
        
        self.plugin_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区
        btn_frame = tk.Frame(main_frame, bg=self.style['BG_PRIMARY'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        refresh_btn = tk.Button(btn_frame,
                               text="刷新列表",
                               font=(self.style['FONT_FAMILY'], 10),
                               bg=self.style['BG_SECONDARY'],
                               fg=self.style['TEXT_PRIMARY'],
                               activebackground=self.style['BG_CARD'],
                               relief='flat',
                               padx=20,
                               pady=8,
                               cursor='hand2',
                               command=self._refresh_plugin_list)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(btn_frame,
                             text="完成",
                             font=(self.style['FONT_FAMILY'], 11, 'bold'),
                             bg=self.style['ACCENT'],
                             fg='white',
                             activebackground=self.style['ACCENT_HOVER'],
                             relief='flat',
                             padx=30,
                             pady=8,
                             cursor='hand2',
                             command=self.dialog.destroy)
        close_btn.pack(side=tk.RIGHT)
    
    def _load_template(self):
        """加载模板代码"""
        template_path = Path(self.plugin_manager.plugin_dir) / "plugin_template.py"
        if template_path.exists():
            try:
                content = template_path.read_text(encoding='utf-8')
                self.template_text.insert('1.0', content)
                self.template_text.config(state='disabled')
            except Exception as e:
                self.template_text.insert('1.0', f"加载模板失败: {e}")
    
    def _copy_template(self):
        """复制模板到剪贴板"""
        self.template_text.config(state='normal')
        content = self.template_text.get('1.0', tk.END)
        self.template_text.config(state='disabled')
        
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(content)
        messagebox.showinfo("提示", "模板已复制到剪贴板！\n\n您可以粘贴到任意编辑器中修改。")
    
    def _create_new_plugin(self):
        """创建新插件文件"""
        # 获取插件文件夹路径
        plugin_dir = Path(self.plugin_manager.plugin_dir)
        
        # 弹出让用户输入文件名
        dialog = tk.Toplevel(self.dialog)
        dialog.title("创建新插件")
        dialog.geometry("400x150")
        dialog.configure(bg=self.style['BG_PRIMARY'])
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        frame = tk.Frame(dialog, bg=self.style['BG_PRIMARY'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(frame,
                        text="请输入插件文件名（不需要.py后缀）:",
                        font=(self.style['FONT_FAMILY'], 10),
                        bg=self.style['BG_PRIMARY'],
                        fg=self.style['TEXT_PRIMARY'])
        label.pack(anchor='w', pady=(0, 10))
        
        entry = tk.Entry(frame,
                        font=(self.style['FONT_FAMILY'], 11),
                        bg=self.style['BG_SECONDARY'],
                        fg=self.style['TEXT_PRIMARY'])
        entry.pack(fill=tk.X, pady=(0, 15))
        entry.insert(0, "plugin_mywebsite")
        
        def create():
            name = entry.get().strip()
            if not name:
                return
            if not name.startswith('plugin_'):
                name = 'plugin_' + name
            if not name.endswith('.py'):
                name += '.py'
            
            target = plugin_dir / name
            
            # 复制模板
            template = plugin_dir / "plugin_template.py"
            if template.exists():
                content = template.read_text(encoding='utf-8')
                # 修改类名
                content = content.replace('class MyPlugin:', f'class MyWebsitePlugin:')
                content = content.replace('"示例网站插件"', f'"我的网站插件"')
                target.write_text(content, encoding='utf-8')
                
                messagebox.showinfo("成功", f"插件文件已创建:\n{target}\n\n请用文本编辑器打开修改。")
                self._refresh_plugin_list()
            
            dialog.destroy()
        
        btn_frame = tk.Frame(frame, bg=self.style['BG_PRIMARY'])
        btn_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(btn_frame,
                              text="取消",
                              font=(self.style['FONT_FAMILY'], 10),
                              bg=self.style['BG_SECONDARY'],
                              fg=self.style['TEXT_PRIMARY'],
                              relief='flat',
                              padx=15,
                              pady=5,
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        create_btn = tk.Button(btn_frame,
                              text="创建",
                              font=(self.style['FONT_FAMILY'], 10, 'bold'),
                              bg=self.style['ACCENT'],
                              fg='white',
                              relief='flat',
                              padx=20,
                              pady=5,
                              command=create)
        create_btn.pack(side=tk.RIGHT)
    
    def _select_file(self):
        """选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择插件文件",
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if file_path:
            self._install_plugin(file_path)
    
    def _install_plugin(self, source_path):
        """安装插件"""
        try:
            source = Path(source_path)
            if not source.exists():
                messagebox.showerror("错误", "文件不存在！")
                return
            
            # 检查是否是Python文件
            if not source.name.endswith('.py'):
                messagebox.showwarning("提示", "请选择 .py 格式的Python文件")
                return
            
            # 目标路径
            target_dir = Path(self.plugin_manager.plugin_dir)
            target = target_dir / source.name
            
            # 如果已存在，询问是否覆盖
            if target.exists():
                if not messagebox.askyesno("确认", f"插件 {source.name} 已存在，是否覆盖？"):
                    return
            
            # 复制文件
            shutil.copy2(source, target)
            
            # 重新加载插件
            self.plugin_manager.reload()
            self._refresh_plugin_list()
            
            # 显示成功消息
            messagebox.showinfo("成功", f"插件 {source.name} 安装成功！\n\n已自动重新加载。")
            
        except Exception as e:
            messagebox.showerror("错误", f"安装失败: {str(e)}")
    
    def _open_plugin_folder(self):
        """打开插件文件夹"""
        import webbrowser
        plugin_dir = Path(self.plugin_manager.plugin_dir)
        plugin_dir.mkdir(exist_ok=True)
        webbrowser.open(str(plugin_dir))
    
    def _refresh_plugin_list(self):
        """刷新插件列表"""
        # 清空列表
        for item in self.plugin_tree.get_children():
            self.plugin_tree.delete(item)
        
        # 重新加载
        self.plugin_manager.reload()
        
        # 添加到列表
        errors = []
        for adapter in self.plugin_manager.adapters:
            try:
                domains = ', '.join(adapter.domains[:2])
                if len(adapter.domains) > 2:
                    domains += '...'
                
                self.plugin_tree.insert('', 'end', values=(
                    adapter.name,
                    domains,
                    "正常"
                ), tags=('success',))
            except Exception as e:
                errors.append(str(e))
        
        # 设置标签颜色
        self.plugin_tree.tag_configure('success', foreground=self.style['SUCCESS'])
        self.plugin_tree.tag_configure('error', foreground=self.style['ERROR'])
        
        # 显示加载报告中的错误
        for filename, message, level in self.plugin_manager.get_load_report():
            if level == 'error':
                # 显示错误项
                self.plugin_tree.insert('', 'end', values=(
                    filename,
                    "加载失败",
                    "错误"
                ), tags=('error',))
        
        # 如果有错误，显示汇总
        if errors:
            messagebox.showwarning("插件加载问题", 
                                  f"部分插件加载失败:\n" + "\n".join(errors[:3]))
