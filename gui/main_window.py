"""
Strix v2.0 - Modern GUI
简洁美观的可视化界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import webbrowser
from pathlib import Path
from datetime import datetime

# 导入核心模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.crawler import StrixCrawler
from core.plugin_manager import PluginManager, SiteAdapter


class ModernStyle:
    """现代化样式定义"""
    
    # 配色方案 - 深色主题
    BG_PRIMARY = "#1e1e2e"      # 主背景
    BG_SECONDARY = "#252537"    # 次背景
    BG_CARD = "#2d2d44"         # 卡片背景
    
    ACCENT = "#7aa2f7"          # 强调色（蓝）
    ACCENT_HOVER = "#5d87e6"    # 悬停色
    SUCCESS = "#9ece6a"         # 成功绿
    WARNING = "#e0af68"         # 警告黄
    ERROR = "#f7768e"           # 错误红
    INFO = "#7dcfff"            # 信息蓝
    
    TEXT_PRIMARY = "#c0caf5"    # 主文字
    TEXT_SECONDARY = "#a9b1d6"  # 次文字
    TEXT_MUTED = "#565f89"      # 弱化文字
    
    FONT_FAMILY = "Microsoft YaHei UI"
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_SMALL = 9


class StrixGUI:
    """Strix 主界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Strix v2.0 - 智能爬虫")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=ModernStyle.BG_PRIMARY)
        
        # 设置图标（如果有的话）
        # self.root.iconbitmap("strix.ico")
        
        # 初始化核心组件
        self.crawler = None
        self.plugin_manager = PluginManager("plugins")
        self.plugin_manager.load_plugins()
        
        # 状态
        self.is_crawling = False
        self.download_dir = Path("downloads").absolute()
        
        # 配置ttk样式
        self._setup_styles()
        
        # 创建界面
        self._create_widgets()
        
        # 加载插件信息
        self._refresh_plugin_info()
    
    def _setup_styles(self):
        """配置ttk样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置全局样式
        style.configure('.',
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.TEXT_PRIMARY)
        
        # Frame样式
        style.configure('Card.TFrame',
                       background=ModernStyle.BG_CARD,
                       relief='flat')
        
        # 按钮样式
        style.configure('Accent.TButton',
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, 'bold'),
                       background=ModernStyle.ACCENT,
                       foreground='white',
                       padding=(20, 10))
        
        style.map('Accent.TButton',
                  background=[('active', ModernStyle.ACCENT_HOVER), ('pressed', ModernStyle.ACCENT)],
                  foreground=[('active', 'white')])
        
        style.configure('Secondary.TButton',
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
                       background=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       padding=(15, 8))
        
        # 标签样式
        style.configure('Title.TLabel',
                       font=(ModernStyle.FONT_FAMILY, 18, 'bold'),
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.ACCENT)
        
        style.configure('Subtitle.TLabel',
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE),
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.TEXT_SECONDARY)
        
        style.configure('CardTitle.TLabel',
                       font=(ModernStyle.FONT_FAMILY, 11, 'bold'),
                       background=ModernStyle.BG_CARD,
                       foreground=ModernStyle.TEXT_PRIMARY)
        
        # Entry样式
        style.configure('Modern.TEntry',
                       fieldbackground=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       insertcolor=ModernStyle.TEXT_PRIMARY,
                       padding=10)
        
        # Checkbutton样式
        style.configure('Modern.TCheckbutton',
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.TEXT_PRIMARY,
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL))
        
        # 进度条样式
        style.configure('Modern.Horizontal.TProgressbar',
                       background=ModernStyle.ACCENT,
                       troughcolor=ModernStyle.BG_SECONDARY,
                       borderwidth=0,
                       thickness=6)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = tk.Frame(self.root, bg=ModernStyle.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ===== 标题区 =====
        header_frame = tk.Frame(main_container, bg=ModernStyle.BG_PRIMARY)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header_frame,
                        text="🦉 Strix",
                        font=(ModernStyle.FONT_FAMILY, 28, 'bold'),
                        bg=ModernStyle.BG_PRIMARY,
                        fg=ModernStyle.ACCENT)
        title.pack(side=tk.LEFT)
        
        subtitle = tk.Label(header_frame,
                           text="v2.0",
                           font=(ModernStyle.FONT_FAMILY, 12),
                           bg=ModernStyle.BG_PRIMARY,
                           fg=ModernStyle.TEXT_MUTED)
        subtitle.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))
        
        # 版本信息按钮
        about_btn = tk.Button(header_frame,
                             text="关于",
                             font=(ModernStyle.FONT_FAMILY, 9),
                             bg=ModernStyle.BG_SECONDARY,
                             fg=ModernStyle.TEXT_SECONDARY,
                             activebackground=ModernStyle.BG_CARD,
                             activeforeground=ModernStyle.TEXT_PRIMARY,
                             relief='flat',
                             padx=15,
                             pady=5,
                             cursor='hand2',
                             command=self._show_about)
        about_btn.pack(side=tk.RIGHT)
        
        # ===== 输入区（卡片） =====
        input_card = tk.Frame(main_container, bg=ModernStyle.BG_CARD, padx=20, pady=20)
        input_card.pack(fill=tk.X, pady=(0, 15))
        input_card.configure(highlightbackground=ModernStyle.BG_SECONDARY,
                            highlightthickness=1)
        
        input_label = tk.Label(input_card,
                              text="🔗 目标网址",
                              font=(ModernStyle.FONT_FAMILY, 11, 'bold'),
                              bg=ModernStyle.BG_CARD,
                              fg=ModernStyle.TEXT_PRIMARY)
        input_label.pack(anchor='w', pady=(0, 10))
        
        # URL输入框
        self.url_entry = tk.Entry(input_card,
                                  font=(ModernStyle.FONT_FAMILY, 11),
                                  bg=ModernStyle.BG_SECONDARY,
                                  fg=ModernStyle.TEXT_PRIMARY,
                                  insertbackground=ModernStyle.TEXT_PRIMARY,
                                  relief='flat',
                                  highlightthickness=1,
                                  highlightcolor=ModernStyle.ACCENT,
                                  highlightbackground=ModernStyle.BG_SECONDARY)
        self.url_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        self.url_entry.insert(0, "https://")
        
        # 选项区
        options_frame = tk.Frame(input_card, bg=ModernStyle.BG_CARD)
        options_frame.pack(fill=tk.X)
        
        # 复选框
        self.var_images = tk.BooleanVar(value=True)
        self.var_videos = tk.BooleanVar(value=True)
        self.var_text = tk.BooleanVar(value=True)
        
        chk_images = tk.Checkbutton(options_frame,
                                   text="📸 图片",
                                   variable=self.var_images,
                                   bg=ModernStyle.BG_CARD,
                                   fg=ModernStyle.TEXT_PRIMARY,
                                   selectcolor=ModernStyle.BG_SECONDARY,
                                   activebackground=ModernStyle.BG_CARD,
                                   activeforeground=ModernStyle.TEXT_PRIMARY,
                                   font=(ModernStyle.FONT_FAMILY, 10))
        chk_images.pack(side=tk.LEFT, padx=(0, 20))
        
        chk_videos = tk.Checkbutton(options_frame,
                                   text="🎬 视频",
                                   variable=self.var_videos,
                                   bg=ModernStyle.BG_CARD,
                                   fg=ModernStyle.TEXT_PRIMARY,
                                   selectcolor=ModernStyle.BG_SECONDARY,
                                   activebackground=ModernStyle.BG_CARD,
                                   activeforeground=ModernStyle.TEXT_PRIMARY,
                                   font=(ModernStyle.FONT_FAMILY, 10))
        chk_videos.pack(side=tk.LEFT, padx=(0, 20))
        
        chk_text = tk.Checkbutton(options_frame,
                                 text="📝 文本",
                                 variable=self.var_text,
                                 bg=ModernStyle.BG_CARD,
                                 fg=ModernStyle.TEXT_PRIMARY,
                                 selectcolor=ModernStyle.BG_SECONDARY,
                                 activebackground=ModernStyle.BG_CARD,
                                 activeforeground=ModernStyle.TEXT_PRIMARY,
                                 font=(ModernStyle.FONT_FAMILY, 10))
        chk_text.pack(side=tk.LEFT)
        
        # ===== 按钮区 =====
        button_frame = tk.Frame(main_container, bg=ModernStyle.BG_PRIMARY)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.start_btn = tk.Button(button_frame,
                                  text="▶ 开始爬取",
                                  font=(ModernStyle.FONT_FAMILY, 12, 'bold'),
                                  bg=ModernStyle.ACCENT,
                                  fg='white',
                                  activebackground=ModernStyle.ACCENT_HOVER,
                                  activeforeground='white',
                                  relief='flat',
                                  padx=30,
                                  pady=12,
                                  cursor='hand2',
                                  command=self._start_crawl)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(button_frame,
                                 text="⏹ 停止",
                                 font=(ModernStyle.FONT_FAMILY, 12),
                                 bg=ModernStyle.ERROR,
                                 fg='white',
                                 activebackground='#e06c75',
                                 activeforeground='white',
                                 relief='flat',
                                 padx=25,
                                 pady=12,
                                 cursor='hand2',
                                 state='disabled',
                                 command=self._stop_crawl)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 添加插件管理按钮
        plugin_btn = tk.Button(button_frame,
                              text="🔌 插件管理",
                              font=(ModernStyle.FONT_FAMILY, 11),
                              bg=ModernStyle.BG_SECONDARY,
                              fg=ModernStyle.TEXT_PRIMARY,
                              activebackground=ModernStyle.BG_CARD,
                              activeforeground=ModernStyle.TEXT_PRIMARY,
                              relief='flat',
                              padx=20,
                              pady=10,
                              cursor='hand2',
                              command=self._open_plugin_manager)
        plugin_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        open_folder_btn = tk.Button(button_frame,
                                   text="📂 打开下载目录",
                                   font=(ModernStyle.FONT_FAMILY, 11),
                                   bg=ModernStyle.BG_SECONDARY,
                                   fg=ModernStyle.TEXT_PRIMARY,
                                   activebackground=ModernStyle.BG_CARD,
                                   activeforeground=ModernStyle.TEXT_PRIMARY,
                                   relief='flat',
                                   padx=20,
                                   pady=10,
                                   cursor='hand2',
                                   command=self._open_downloads)
        open_folder_btn.pack(side=tk.RIGHT)
        
        # ===== 日志区（卡片） =====
        log_card = tk.Frame(main_container, bg=ModernStyle.BG_CARD)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        log_header = tk.Frame(log_card, bg=ModernStyle.BG_CARD)
        log_header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        log_label = tk.Label(log_header,
                            text="📋 运行日志",
                            font=(ModernStyle.FONT_FAMILY, 11, 'bold'),
                            bg=ModernStyle.BG_CARD,
                            fg=ModernStyle.TEXT_PRIMARY)
        log_label.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(log_header,
                             text="清空",
                             font=(ModernStyle.FONT_FAMILY, 9),
                             bg=ModernStyle.BG_SECONDARY,
                             fg=ModernStyle.TEXT_SECONDARY,
                             activebackground=ModernStyle.BG_CARD,
                             activeforeground=ModernStyle.TEXT_PRIMARY,
                             relief='flat',
                             padx=10,
                             pady=3,
                             cursor='hand2',
                             command=self._clear_log)
        clear_btn.pack(side=tk.RIGHT)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_card,
            font=('Consolas', 10),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief='flat',
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # 配置日志标签颜色
        self.log_text.tag_config('success', foreground=ModernStyle.SUCCESS)
        self.log_text.tag_config('error', foreground=ModernStyle.ERROR)
        self.log_text.tag_config('warning', foreground=ModernStyle.WARNING)
        self.log_text.tag_config('info', foreground=ModernStyle.INFO)
        
        # ===== 状态栏 =====
        status_frame = tk.Frame(main_container, bg=ModernStyle.BG_SECONDARY, padx=15, pady=8)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.status_label = tk.Label(status_frame,
                                    text="就绪",
                                    font=(ModernStyle.FONT_FAMILY, 9),
                                    bg=ModernStyle.BG_SECONDARY,
                                    fg=ModernStyle.TEXT_SECONDARY)
        self.status_label.pack(side=tk.LEFT)
        
        # 插件信息
        self.plugin_label = tk.Label(status_frame,
                                    text="插件: 0",
                                    font=(ModernStyle.FONT_FAMILY, 9),
                                    bg=ModernStyle.BG_SECONDARY,
                                    fg=ModernStyle.TEXT_MUTED)
        self.plugin_label.pack(side=tk.RIGHT)
    
    def _log(self, message, level='info'):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, full_message, level)
        self.log_text.see(tk.END)
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def _refresh_plugin_info(self):
        """刷新插件信息"""
        count = len(self.plugin_manager.adapters)
        self.plugin_label.config(text=f"已加载插件: {count}")
        
        if count > 0:
            names = [a.name for a in self.plugin_manager.adapters]
            self._log(f"已加载插件: {', '.join(names)}", 'success')
        
        # 显示加载报告
        for filename, message, level in self.plugin_manager.get_load_report():
            if level != 'info':
                self._log(f"[{filename}] {message}", level)
    
    def _start_crawl(self):
        """开始爬取"""
        url = self.url_entry.get().strip()
        
        if not url or url == "https://":
            messagebox.showwarning("提示", "请输入有效的网址")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        # 更新状态
        self.is_crawling = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="正在爬取...", fg=ModernStyle.ACCENT)
        
        # 清空日志
        self._clear_log()
        self._log(f"🦉 Strix v2.0 启动", 'info')
        self._log(f"目标: {url}")
        
        # 创建爬虫实例
        self.crawler = StrixCrawler(
            output_dir=str(self.download_dir),
            log_callback=lambda msg, lvl: self.root.after(0, lambda: self._log(msg, lvl))
        )
        
        # 配置选项
        options = {
            'images': self.var_images.get(),
            'videos': self.var_videos.get(),
            'text': self.var_text.get(),
            'threads': 4
        }
        
        # 在新线程中运行
        def crawl_thread():
            try:
                success = self.crawler.crawl(url, options)
                self.root.after(0, lambda: self._crawl_finished(success))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"❌ 错误: {str(e)}", 'error'))
                self.root.after(0, lambda: self._crawl_finished(False))
        
        threading.Thread(target=crawl_thread, daemon=True).start()
    
    def _stop_crawl(self):
        """停止爬取"""
        if self.crawler:
            self.crawler.stop()
        self.is_crawling = False
        self._log("🛑 用户取消操作", 'warning')
    
    def _crawl_finished(self, success):
        """爬取完成回调"""
        self.is_crawling = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        if success:
            self.status_label.config(text="完成", fg=ModernStyle.SUCCESS)
            self._log("✅ 任务完成！", 'success')
        else:
            self.status_label.config(text="失败", fg=ModernStyle.ERROR)
        
        # 显示结果
        if self.crawler:
            stats = self.crawler.stats
            msg = f"\n📊 统计:\n"
            msg += f"  图片: {stats['images']}\n"
            msg += f"  视频: {stats['videos']}\n"
            msg += f"  文本: {stats['texts']}\n"
            if stats['errors']:
                msg += f"  错误: {stats['errors']}\n"
            self._log(msg, 'info')
    
    def _open_downloads(self):
        """打开下载目录"""
        self.download_dir.mkdir(exist_ok=True)
        webbrowser.open(str(self.download_dir))
    
    def _open_plugin_manager(self):
        """打开插件管理器"""
        from gui.plugin_dialog import PluginManagerDialog
        
        style = {
            'BG_PRIMARY': ModernStyle.BG_PRIMARY,
            'BG_SECONDARY': ModernStyle.BG_SECONDARY,
            'BG_CARD': ModernStyle.BG_CARD,
            'ACCENT': ModernStyle.ACCENT,
            'ACCENT_HOVER': ModernStyle.ACCENT_HOVER,
            'SUCCESS': ModernStyle.SUCCESS,
            'WARNING': ModernStyle.WARNING,
            'ERROR': ModernStyle.ERROR,
            'INFO': ModernStyle.INFO,
            'TEXT_PRIMARY': ModernStyle.TEXT_PRIMARY,
            'TEXT_SECONDARY': ModernStyle.TEXT_SECONDARY,
            'TEXT_MUTED': ModernStyle.TEXT_MUTED,
            'FONT_FAMILY': ModernStyle.FONT_FAMILY
        }
        
        PluginManagerDialog(self.root, self.plugin_manager, style)
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = """🦉 Strix v2.0

智能爬虫工具

功能特点:
• 图片、视频、文本自动提取
• 强大的反爬机制
• 插件系统支持自定义
• 简洁美观的界面

快捷键:
Ctrl+C  复制
Ctrl+V  粘贴

提示:
• 插件放在 plugins 文件夹
• 下载内容保存在 downloads 文件夹

Made with ❤️ by TARS
"""
        messagebox.showinfo("关于 Strix", about_text)


def main():
    """主入口"""
    root = tk.Tk()
    
    # 设置DPI感知（Windows）
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = StrixGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
