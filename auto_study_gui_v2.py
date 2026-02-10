# -*- coding: utf-8 -*-
"""
湖南外国语职业学院自动化学习脚本 - GUI版本 (美化版)
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import sys
import threading
import subprocess

# 尝试导入 ttkbootstrap 美化库
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    USE_BOOTSTRAP = True
    THEME = 'cosmo'  # 可选主题: cosmo, flatly, litera, minty, lumen, sandstone, yeti, pulse, united, morph, journal, darkly, superhero, solar, cyborg, vapor, simplex, cerculean
except ImportError:
    print("正在安装 ttkbootstrap 美化库...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ttkbootstrap", "--quiet"])
        import ttkbootstrap as ttk
        from ttkbootstrap.constants import *
        USE_BOOTSTRAP = True
        THEME = 'cosmo'
    except:
        print("无法安装 ttkbootstrap，使用默认主题")
        from tkinter import ttk
        USE_BOOTSTRAP = False
        THEME = None

from auto_study import AutoStudyBot

class AutoStudyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("湖南外国语自动学习助手")
        
        # 获取屏幕尺寸
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # 设置窗口尺寸
        window_width = 900
        window_height = 750
        
        # 计算居中位置
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        # 设置窗口位置和大小
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(False, False)  # 禁止调整窗口大小
        
        # 加载配置
        self.config = self.load_config()
        
        # 为每个任务维护独立的bot和运行状态
        self.video_bot = None
        self.homework_bot = None
        self.exam_bot = None
        self.video_running = False
        self.homework_running = False
        self.exam_running = False
        
        # 创建Notebook（选项卡）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建主页面框架
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text='  主程序  ')
        
        # 创建配置页面框架
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text='  配置  ')
        
        # 初始化页面
        self.init_main_page()
        self.init_config_page()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "website": {"url": "", "username": "", "password": ""},
            "browser": {"window_width": 1920, "window_height": 1080, "headless": False},
            "automation": {"element_timeout": 10, "page_load_timeout": 30, 
                          "enable_delays": False, "video_speed": "2X", "concurrent_videos": 3},
            "homework": {"use_ai": True, "auto_submit": True, 
                        "min_passing_score": 60, "retry_if_failed": True},
            "ai": {"provider": "openai", "openai_api_key": "", 
                  "openai_base_url": "https://api.openai.com/v1", 
                  "openai_model": "gpt-3.5-turbo",
                  "zhipu_api_key": "", "zhipu_model": "glm-4-flash"},
            "debug": {"highlight_elements": True}
        }
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def init_main_page(self):
        """初始化主程序页面（带滚动和居中）"""
        # 创建滚动容器
        canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 居中显示内容
        canvas_window = canvas.create_window((450, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 保存canvas引用
        self.main_canvas = canvas
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        self.main_frame.bind("<Enter>", _bind_mousewheel)
        self.main_frame.bind("<Leave>", _unbind_mousewheel)
        
        # 标题区域
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(pady=20)
        
        title_label = ttk.Label(title_frame, text="湖南外国语自动学习助手",
                                font=('Microsoft YaHei UI', 18, 'bold'))
        title_label.pack()
        
        # 开源标识
        if USE_BOOTSTRAP:
            opensource_label = ttk.Label(title_frame,
                                         text="开源免费 | 仅供学习交流使用 | 禁止商业用途",
                                         font=('Microsoft YaHei UI', 9),
                                         bootstyle="success")
        else:
            opensource_label = ttk.Label(title_frame,
                                         text="开源免费 | 仅供学习交流使用 | 禁止商业用途",
                                         font=('Microsoft YaHei UI', 9),
                                         foreground='green')
        opensource_label.pack(pady=5)
        
        # 设置统一宽度（固定不可变）
        FRAME_WIDTH = 750
        
        # 快捷设置区域
        quick_frame = ttk.LabelFrame(scrollable_frame, text="  快捷设置  ", padding=15)
        quick_frame.pack(pady=10, fill='x')
        quick_frame.configure(width=FRAME_WIDTH)
        
        # 强制显示浏览器窗口，不使用无头模式
        self.show_browser_var = tk.BooleanVar(value=True)
        # 确保配置中也是显示模式
        self.config['browser']['headless'] = False
        
        if USE_BOOTSTRAP:
            show_browser_cb = ttk.Checkbutton(quick_frame,
                                             text="显示浏览器窗口（始终显示，方便查看运行进度）",
                                             variable=self.show_browser_var,
                                             command=self.toggle_browser_display,
                                             bootstyle="success-round-toggle")
        else:
            show_browser_cb = ttk.Checkbutton(quick_frame,
                                             text="显示浏览器窗口（始终显示，方便查看运行进度）",
                                             variable=self.show_browser_var,
                                             command=self.toggle_browser_display)
        show_browser_cb.pack(anchor='w')
        
        # 刷视频区域
        video_frame = ttk.LabelFrame(scrollable_frame, text="  刷视频  ", padding=20)
        video_frame.pack(pady=10, fill='x')
        video_frame.configure(width=FRAME_WIDTH)
        
        video_settings = ttk.Frame(video_frame)
        video_settings.pack(anchor='w', pady=5)
        
        ttk.Label(video_settings, text="连续窗口数:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=0, padx=5, sticky='w')
        self.video_count_var = tk.IntVar(value=self.config['automation'].get('concurrent_videos', 3))
        ttk.Spinbox(video_settings, from_=1, to=10, textvariable=self.video_count_var,
                   width=15, font=('Microsoft YaHei UI', 10)).grid(row=0, column=1, padx=5)
        
        ttk.Label(video_settings, text="播放倍速:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=2, padx=10)
        self.video_speed_var = tk.StringVar(value=self.config['automation'].get('video_speed', '2X'))
        speed_combo = ttk.Combobox(video_settings, textvariable=self.video_speed_var,
                                   values=['0.5X', '1X', '1.25X', '1.5X', '2X'],
                                   width=12, state='readonly', font=('Microsoft YaHei UI', 10))
        speed_combo.grid(row=0, column=3, padx=5)
        
        if USE_BOOTSTRAP:
            ttk.Button(video_settings, text="开始刷视频", command=self.start_watch_video,
                      bootstyle="success", width=20).grid(row=0, column=4, padx=20)
        else:
            ttk.Button(video_settings, text="开始刷视频", command=self.start_watch_video,
                      width=20).grid(row=0, column=4, padx=20)
        
        # 答题区域
        homework_frame = ttk.LabelFrame(scrollable_frame, text="  答题  ", padding=20)
        homework_frame.pack(pady=10, fill='x')
        homework_frame.configure(width=FRAME_WIDTH)
        
        homework_settings = ttk.Frame(homework_frame)
        homework_settings.pack(anchor='w', pady=5)
        
        ttk.Label(homework_settings, text="答题模式:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=0, padx=5, sticky='w')
        
        self.homework_mode_var = tk.StringVar(value="ai" if self.config['homework']['use_ai'] else "random")
        ttk.Radiobutton(homework_settings, text="AI答题", variable=self.homework_mode_var,
                       value="ai").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(homework_settings, text="随机答题", variable=self.homework_mode_var,
                       value="random").grid(row=0, column=2, padx=5)
        
        ttk.Label(homework_settings, text="AI选择:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=3, padx=10)
        self.ai_provider_var = tk.StringVar(value=self.config['ai'].get('provider', 'openai'))
        ai_combo = ttk.Combobox(homework_settings, textvariable=self.ai_provider_var,
                               values=['openai', 'zhipu'], width=12, state='readonly',
                               font=('Microsoft YaHei UI', 10))
        ai_combo.grid(row=0, column=4, padx=5)
        
        if USE_BOOTSTRAP:
            ttk.Button(homework_settings, text="开始答题", command=self.start_homework,
                      bootstyle="info", width=20).grid(row=0, column=5, padx=20)
        else:
            ttk.Button(homework_settings, text="开始答题", command=self.start_homework,
                      width=20).grid(row=0, column=5, padx=20)
        
        # 考试区域
        exam_frame = ttk.LabelFrame(scrollable_frame, text="  考试  ", padding=20)
        exam_frame.pack(pady=10, fill='x')
        exam_frame.configure(width=FRAME_WIDTH)
        
        exam_settings = ttk.Frame(exam_frame)
        exam_settings.pack(anchor='w', pady=5)
        
        ttk.Label(exam_settings, text="考试模式:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=0, padx=5, sticky='w')
        
        self.exam_mode_var = tk.StringVar(value="ai" if self.config['homework']['use_ai'] else "random")
        ttk.Radiobutton(exam_settings, text="AI答题", variable=self.exam_mode_var,
                       value="ai").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(exam_settings, text="随机答题", variable=self.exam_mode_var,
                       value="random").grid(row=0, column=2, padx=5)
        
        ttk.Label(exam_settings, text="AI选择:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=3, padx=10)
        self.exam_ai_provider_var = tk.StringVar(value=self.config['ai'].get('provider', 'openai'))
        exam_ai_combo = ttk.Combobox(exam_settings, textvariable=self.exam_ai_provider_var,
                               values=['openai', 'zhipu'], width=12, state='readonly',
                               font=('Microsoft YaHei UI', 10))
        exam_ai_combo.grid(row=0, column=4, padx=5)
        
        if USE_BOOTSTRAP:
            ttk.Button(exam_settings, text="开始考试", command=self.start_exam,
                      bootstyle="warning", width=20).grid(row=0, column=5, padx=20)
        else:
            ttk.Button(exam_settings, text="开始考试", command=self.start_exam,
                      width=20).grid(row=0, column=5, padx=20)
        
        # 控制按钮区域
        control_frame = ttk.Frame(scrollable_frame)
        control_frame.pack(pady=20)
        
        if USE_BOOTSTRAP:
            ttk.Button(control_frame, text="停止任务", command=self.stop_task,
                      bootstyle="danger", width=20).pack(side='left', padx=10)
            ttk.Button(control_frame, text="清空日志", command=self.clear_log,
                      bootstyle="warning", width=20).pack(side='left', padx=10)
        else:
            ttk.Button(control_frame, text="停止任务", command=self.stop_task,
                      width=20).pack(side='left', padx=10)
            ttk.Button(control_frame, text="清空日志", command=self.clear_log,
                      width=20).pack(side='left', padx=10)
        
        # 日志区域
        log_frame = ttk.LabelFrame(scrollable_frame, text="  运行日志  ", padding=10)
        log_frame.pack(pady=10, fill='x')
        log_frame.configure(width=FRAME_WIDTH)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=88,
                                                  font=('Consolas', 9))
        self.log_text.pack()
        
        # 底部版权信息
        footer_frame = ttk.Frame(scrollable_frame)
        footer_frame.pack(pady=10)
        
        if USE_BOOTSTRAP:
            footer_label = ttk.Label(footer_frame,
                                    text="© 2025 开源项目 | 完全免费 | GitHub: 湖南外国语自动学习脚本",
                                    font=('Microsoft YaHei UI', 8),
                                    bootstyle="secondary")
        else:
            footer_label = ttk.Label(footer_frame,
                                    text="© 2025 开源项目 | 完全免费 | GitHub: 湖南外国语自动学习脚本",
                                    font=('Microsoft YaHei UI', 8),
                                    foreground='gray')
        footer_label.pack()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def init_config_page(self):
        """初始化配置页面（带滚动和居中）"""
        # 创建滚动容器
        canvas = tk.Canvas(self.config_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 居中显示内容
        canvas.create_window((450, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 保存canvas引用
        self.config_canvas = canvas
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        self.config_frame.bind("<Enter>", _bind_mousewheel)
        self.config_frame.bind("<Leave>", _unbind_mousewheel)
        
        # 设置统一宽度
        FRAME_WIDTH = 750
        
        # 登录配置
        login_frame = ttk.LabelFrame(scrollable_frame, text="  登录配置  ", padding=15)
        login_frame.pack(pady=10, fill='x')
        login_frame.configure(width=FRAME_WIDTH)
        
        ttk.Label(login_frame, text="学号:").grid(row=0, column=0, sticky='w', pady=5)
        self.username_var = tk.StringVar(value=self.config['website'].get('username', ''))
        ttk.Entry(login_frame, textvariable=self.username_var, width=60).grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(login_frame, text="密码:").grid(row=1, column=0, sticky='w', pady=5)
        self.password_var = tk.StringVar(value=self.config['website'].get('password', ''))
        ttk.Entry(login_frame, textvariable=self.password_var, width=60).grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(login_frame, text="网站地址:").grid(row=2, column=0, sticky='w', pady=5)
        self.url_var = tk.StringVar(value=self.config['website'].get('url', ''))
        ttk.Entry(login_frame, textvariable=self.url_var, width=60).grid(row=2, column=1, pady=5, padx=10)
        
        # OpenAI 兼容格式配置
        openai_frame = ttk.LabelFrame(scrollable_frame, text="  OpenAI 兼容格式配置  ", padding=15)
        openai_frame.pack(pady=10, fill='x')
        openai_frame.configure(width=FRAME_WIDTH)
        
        if USE_BOOTSTRAP:
            tip_label = ttk.Label(openai_frame,
                                 text="提示: 支持所有 OpenAI 兼容格式的 API (ChatGPT, Kimi, DeepSeek, 通义千问等)",
                                 font=('Microsoft YaHei UI', 9),
                                 bootstyle="info")
        else:
            tip_label = ttk.Label(openai_frame,
                                 text="提示: 支持所有 OpenAI 兼容格式的 API (ChatGPT, Kimi, DeepSeek, 通义千问等)",
                                 font=('Microsoft YaHei UI', 9),
                                 foreground='blue')
        tip_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
        
        ttk.Label(openai_frame, text="API Key:").grid(row=1, column=0, sticky='w', pady=5)
        self.openai_key_var = tk.StringVar(value=self.config['ai'].get('openai_api_key', ''))
        ttk.Entry(openai_frame, textvariable=self.openai_key_var, width=60).grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(openai_frame, text="Base URL:").grid(row=2, column=0, sticky='w', pady=5)
        self.openai_url_var = tk.StringVar(value=self.config['ai'].get('openai_base_url', 'https://api.openai.com/v1'))
        ttk.Entry(openai_frame, textvariable=self.openai_url_var, width=60).grid(row=2, column=1, pady=5, padx=10)
        
        url_examples = ttk.Label(openai_frame,
                                text="示例: ChatGPT: https://api.openai.com/v1 | Kimi: https://api.moonshot.cn/v1",
                                font=('Microsoft YaHei UI', 8),
                                foreground='gray')
        url_examples.grid(row=3, column=1, sticky='w', padx=10)
        
        ttk.Label(openai_frame, text="模型:").grid(row=4, column=0, sticky='w', pady=5)
        self.openai_model_var = tk.StringVar(value=self.config['ai'].get('openai_model', 'gpt-3.5-turbo'))
        ttk.Entry(openai_frame, textvariable=self.openai_model_var, width=60).grid(row=4, column=1, pady=5, padx=10)
        
        model_examples = ttk.Label(openai_frame,
                                   text="示例: gpt-3.5-turbo, moonshot-v1-8k, deepseek-chat",
                                   font=('Microsoft YaHei UI', 8),
                                   foreground='gray')
        model_examples.grid(row=5, column=1, sticky='w', padx=10)
        
        # 智谱AI配置
        zhipu_frame = ttk.LabelFrame(scrollable_frame, text="  智谱AI 配置  ", padding=15)
        zhipu_frame.pack(pady=10, fill='x')
        zhipu_frame.configure(width=FRAME_WIDTH)
        
        ttk.Label(zhipu_frame, text="API Key:").grid(row=0, column=0, sticky='w', pady=5)
        self.zhipu_key_var = tk.StringVar(value=self.config['ai'].get('zhipu_api_key', ''))
        ttk.Entry(zhipu_frame, textvariable=self.zhipu_key_var, width=60).grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(zhipu_frame, text="模型:").grid(row=1, column=0, sticky='w', pady=5)
        self.zhipu_model_var = tk.StringVar(value=self.config['ai'].get('zhipu_model', 'glm-4-flash'))
        ttk.Entry(zhipu_frame, textvariable=self.zhipu_model_var, width=60).grid(row=1, column=1, pady=5, padx=10)
        
        # 浏览器配置
        browser_frame = ttk.LabelFrame(scrollable_frame, text="  浏览器配置  ", padding=15)
        browser_frame.pack(pady=10, fill='x')
        browser_frame.configure(width=FRAME_WIDTH)
        
        ttk.Label(browser_frame, text="窗口宽度:").grid(row=0, column=0, sticky='w', pady=5)
        self.window_width_var = tk.IntVar(value=self.config['browser'].get('window_width', 1920))
        ttk.Spinbox(browser_frame, from_=800, to=3840, textvariable=self.window_width_var, width=58).grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(browser_frame, text="窗口高度:").grid(row=1, column=0, sticky='w', pady=5)
        self.window_height_var = tk.IntVar(value=self.config['browser'].get('window_height', 1080))
        ttk.Spinbox(browser_frame, from_=600, to=2160, textvariable=self.window_height_var, width=58).grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(browser_frame, text="无头模式:").grid(row=2, column=0, sticky='w', pady=5)
        self.headless_var = tk.BooleanVar(value=self.config['browser'].get('headless', False))
        ttk.Checkbutton(browser_frame, text="启用无头模式（后台运行，不显示浏览器窗口）",
                       variable=self.headless_var).grid(row=2, column=1, sticky='w', pady=5, padx=10)
        
        if USE_BOOTSTRAP:
            headless_tip = ttk.Label(browser_frame,
                                    text="提示: 取消勾选可以看到浏览器窗口和执行进度，方便调试",
                                    font=('Microsoft YaHei UI', 8),
                                    bootstyle="info")
        else:
            headless_tip = ttk.Label(browser_frame,
                                    text="提示: 取消勾选可以看到浏览器窗口和执行进度，方便调试",
                                    font=('Microsoft YaHei UI', 8),
                                    foreground='blue')
        headless_tip.grid(row=3, column=1, sticky='w', pady=2, padx=10)
        
        # 自动化配置
        auto_frame = ttk.LabelFrame(scrollable_frame, text="  自动化配置  ", padding=15)
        auto_frame.pack(pady=10, fill='x')
        auto_frame.configure(width=FRAME_WIDTH)
        
        ttk.Label(auto_frame, text="元素超时时间(秒):").grid(row=0, column=0, sticky='w', pady=5)
        self.element_timeout_var = tk.IntVar(value=self.config['automation'].get('element_timeout', 10))
        ttk.Spinbox(auto_frame, from_=5, to=60, textvariable=self.element_timeout_var, width=58).grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(auto_frame, text="页面加载超时(秒):").grid(row=1, column=0, sticky='w', pady=5)
        self.page_timeout_var = tk.IntVar(value=self.config['automation'].get('page_load_timeout', 30))
        ttk.Spinbox(auto_frame, from_=10, to=120, textvariable=self.page_timeout_var, width=58).grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(auto_frame, text="启用延迟:").grid(row=2, column=0, sticky='w', pady=5)
        self.enable_delays_var = tk.BooleanVar(value=self.config['automation'].get('enable_delays', False))
        ttk.Checkbutton(auto_frame, text="启用随机延迟（模拟人类操作）",
                       variable=self.enable_delays_var).grid(row=2, column=1, sticky='w', pady=5, padx=10)
        
        # 作业配置
        homework_config_frame = ttk.LabelFrame(scrollable_frame, text="  作业配置  ", padding=15)
        homework_config_frame.pack(pady=10, fill='x')
        homework_config_frame.configure(width=FRAME_WIDTH)
        
        ttk.Label(homework_config_frame, text="自动提交:").grid(row=0, column=0, sticky='w', pady=5)
        self.auto_submit_var = tk.BooleanVar(value=self.config['homework'].get('auto_submit', True))
        ttk.Checkbutton(homework_config_frame, text="完成后自动提交作业",
                       variable=self.auto_submit_var).grid(row=0, column=1, sticky='w', pady=5, padx=10)
        
        ttk.Label(homework_config_frame, text="及格分数:").grid(row=1, column=0, sticky='w', pady=5)
        self.min_score_var = tk.IntVar(value=self.config['homework'].get('min_passing_score', 60))
        ttk.Spinbox(homework_config_frame, from_=0, to=100, textvariable=self.min_score_var, width=58).grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(homework_config_frame, text="不及格重做:").grid(row=2, column=0, sticky='w', pady=5)
        self.retry_failed_var = tk.BooleanVar(value=self.config['homework'].get('retry_if_failed', True))
        ttk.Checkbutton(homework_config_frame, text="自动重做低于及格分数的作业",
                       variable=self.retry_failed_var).grid(row=2, column=1, sticky='w', pady=5, padx=10)
        
        # 调试配置
        debug_frame = ttk.LabelFrame(scrollable_frame, text="  调试配置  ", padding=15)
        debug_frame.pack(pady=10, fill='x')
        debug_frame.configure(width=FRAME_WIDTH)
        
        ttk.Label(debug_frame, text="高亮元素:").grid(row=0, column=0, sticky='w', pady=5)
        self.highlight_var = tk.BooleanVar(value=self.config['debug'].get('highlight_elements', True))
        ttk.Checkbutton(debug_frame, text="高亮显示操作的元素（调试用）",
                       variable=self.highlight_var).grid(row=0, column=1, sticky='w', pady=5, padx=10)
        
        # 保存按钮
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=20)
        
        if USE_BOOTSTRAP:
            ttk.Button(button_frame, text="保存配置", command=self.save_config_from_gui,
                      bootstyle="success", width=20).pack()
        else:
            ttk.Button(button_frame, text="保存配置", command=self.save_config_from_gui,
                      width=20).pack()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def toggle_browser_display(self):
        """切换浏览器显示模式"""
        self.config['browser']['headless'] = not self.show_browser_var.get()
        # 静默保存，不显示提示
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except:
            pass
        
        if hasattr(self, 'headless_var'):
            self.headless_var.set(not self.show_browser_var.get())
        
        status = "显示" if self.show_browser_var.get() else "隐藏"
        self.log(f"浏览器显示模式已切换为: {status}")
    
    def save_config_from_gui(self):
        """从GUI保存配置"""
        # 更新登录配置
        self.config['website']['username'] = self.username_var.get()
        self.config['website']['password'] = self.password_var.get()
        self.config['website']['url'] = self.url_var.get()
        
        # 更新AI配置
        self.config['ai']['openai_api_key'] = self.openai_key_var.get()
        self.config['ai']['openai_base_url'] = self.openai_url_var.get()
        self.config['ai']['openai_model'] = self.openai_model_var.get()
        self.config['ai']['zhipu_api_key'] = self.zhipu_key_var.get()
        self.config['ai']['zhipu_model'] = self.zhipu_model_var.get()
        
        # 更新浏览器配置
        self.config['browser']['window_width'] = self.window_width_var.get()
        self.config['browser']['window_height'] = self.window_height_var.get()
        self.config['browser']['headless'] = self.headless_var.get()
        
        # 同步更新主页面的显示浏览器开关
        if hasattr(self, 'show_browser_var'):
            self.show_browser_var.set(not self.headless_var.get())
        
        # 更新自动化配置
        self.config['automation']['element_timeout'] = self.element_timeout_var.get()
        self.config['automation']['page_load_timeout'] = self.page_timeout_var.get()
        self.config['automation']['enable_delays'] = self.enable_delays_var.get()
        
        # 更新作业配置
        self.config['homework']['auto_submit'] = self.auto_submit_var.get()
        self.config['homework']['min_passing_score'] = self.min_score_var.get()
        self.config['homework']['retry_if_failed'] = self.retry_failed_var.get()
        
        # 更新调试配置
        self.config['debug']['highlight_elements'] = self.highlight_var.get()
        
        self.save_config()
        messagebox.showinfo("成功", "配置已保存！")
    
    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def start_watch_video(self):
        """开始刷视频"""
        if self.video_running:
            messagebox.showwarning("警告", "刷视频任务正在运行中")
            return
        
        self.config['automation']['concurrent_videos'] = self.video_count_var.get()
        self.config['automation']['video_speed'] = self.video_speed_var.get()
        # 静默保存
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except:
            pass
        
        self.log("=" * 50)
        self.log("[刷视频] 开始任务...")
        self.log(f"[刷视频] 配置: {self.video_count_var.get()}个窗口, {self.video_speed_var.get()}倍速")
        self.log("=" * 50)
        
        thread = threading.Thread(target=self._run_watch_video)
        thread.daemon = True
        thread.start()
    
    def _run_watch_video(self):
        """运行刷视频任务"""
        try:
            self.video_running = True
            
            # 先重定向输出，确保所有信息都能显示
            sys.stdout = LogRedirector(self.log)
            
            # 创建bot实例
            self.log("[刷视频] 正在初始化...")
            self.video_bot = AutoStudyBot()
            
            if not self.video_running:
                return
            
            self.log("[刷视频] 正在启动浏览器...")
            if not self.video_bot.setup_browser():
                self.log("[刷视频] ✗ 浏览器启动失败")
                return
            
            if not self.video_running:
                return
            
            self.log("[刷视频] 正在登录...")
            if not self.video_bot.auto_login():
                self.log("[刷视频] ✗ 登录失败")
                return
            
            if not self.video_running:
                return
            
            self.log("[刷视频] 正在导航到课程页面...")
            self.video_bot.navigate_to_courses()
            
            if not self.video_running:
                return
            
            self.log("[刷视频] 开始播放视频...")
            self.video_bot.play_first_video()
            
        except Exception as e:
            self.log(f"[刷视频] ✗ 错误: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.video_running = False
            sys.stdout = sys.__stdout__
            if self.video_bot and self.video_bot.driver:
                try:
                    self.video_bot.driver.quit()
                    self.log("[刷视频] 浏览器已关闭")
                except:
                    pass
            self.log("=" * 50)
            self.log("[刷视频] 任务结束")
            self.log("=" * 50)
    
    def start_homework(self):
        """开始答题"""
        if self.homework_running:
            messagebox.showwarning("警告", "答题任务正在运行中")
            return
        
        self.config['homework']['use_ai'] = (self.homework_mode_var.get() == "ai")
        self.config['ai']['provider'] = self.ai_provider_var.get()
        # 静默保存
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except:
            pass
        
        mode = "AI答题" if self.homework_mode_var.get() == "ai" else "随机答题"
        self.log("=" * 50)
        self.log(f"[答题] 开始任务... (模式: {mode})")
        
        if self.homework_mode_var.get() == "ai":
            self.log(f"[答题] 使用AI: {self.ai_provider_var.get()}")
        self.log("=" * 50)
        
        thread = threading.Thread(target=self._run_homework)
        thread.daemon = True
        thread.start()
    
    def _run_homework(self):
        """运行答题任务"""
        try:
            self.homework_running = True
            
            # 先重定向输出
            sys.stdout = LogRedirector(self.log)
            
            # 创建bot实例
            self.log("[答题] 正在初始化...")
            self.homework_bot = AutoStudyBot()
            
            if not self.homework_running:
                return
            
            self.log("[答题] 正在启动浏览器...")
            if not self.homework_bot.setup_browser():
                self.log("[答题] ✗ 浏览器启动失败")
                return
            
            if not self.homework_running:
                return
            
            if not self.homework_bot.auto_login():
                self.log("[答题] 登录失败")
                return
            
            if not self.homework_running:
                return
            
            self.homework_bot.navigate_to_homework()
            
            if not self.homework_running:
                return
            
            self.homework_bot.do_all_homework()
            
        except Exception as e:
            self.log(f"[答题] 错误: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.homework_running = False
            sys.stdout = sys.__stdout__
            if self.homework_bot and self.homework_bot.driver:
                try:
                    self.homework_bot.driver.quit()
                    self.log("[答题] 浏览器已关闭")
                except:
                    pass
            self.log("=" * 50)
            self.log("[答题] 任务结束")
            self.log("=" * 50)
    
    def start_exam(self):
        """开始考试"""
        if self.exam_running:
            messagebox.showwarning("警告", "考试任务正在运行中")
            return
        
        self.config['homework']['use_ai'] = (self.exam_mode_var.get() == "ai")
        self.config['ai']['provider'] = self.exam_ai_provider_var.get()
        # 静默保存
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except:
            pass
        
        mode = "AI答题" if self.exam_mode_var.get() == "ai" else "随机答题"
        self.log("=" * 50)
        self.log(f"[考试] 开始任务... (模式: {mode})")
        
        if self.exam_mode_var.get() == "ai":
            self.log(f"[考试] 使用AI: {self.exam_ai_provider_var.get()}")
        self.log("=" * 50)
        
        thread = threading.Thread(target=self._run_exam)
        thread.daemon = True
        thread.start()
    
    def _run_exam(self):
        """运行考试任务"""
        try:
            self.exam_running = True
            
            # 先重定向输出
            sys.stdout = LogRedirector(self.log)
            
            # 创建bot实例
            self.log("[考试] 正在初始化...")
            self.exam_bot = AutoStudyBot()
            
            if not self.exam_running:
                return
            
            self.log("[考试] 正在启动浏览器...")
            if not self.exam_bot.setup_browser():
                self.log("[考试] ✗ 浏览器启动失败")
                return
            
            if not self.exam_running:
                return
            
            self.log("[考试] 正在登录...")
            if not self.exam_bot.auto_login():
                self.log("[考试] ✗ 登录失败")
                return
            
            if not self.exam_running:
                return
            
            self.exam_bot.do_all_exams()
            
        except Exception as e:
            self.log(f"[考试] 错误: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.exam_running = False
            sys.stdout = sys.__stdout__
            if self.exam_bot and self.exam_bot.driver:
                try:
                    self.exam_bot.driver.quit()
                    self.log("[考试] 浏览器已关闭")
                except:
                    pass
            self.log("=" * 50)
            self.log("[考试] 任务结束")
            self.log("=" * 50)
    
    def stop_task(self):
        """停止所有任务"""
        running_tasks = []
        if self.video_running:
            running_tasks.append("刷视频")
        if self.homework_running:
            running_tasks.append("答题")
        if self.exam_running:
            running_tasks.append("考试")
        
        if not running_tasks:
            messagebox.showinfo("提示", "当前没有正在运行的任务")
            return
        
        tasks_text = "、".join(running_tasks)
        if messagebox.askyesno("确认", f"确定要停止以下任务吗？\n\n{tasks_text}"):
            self.log("=" * 50)
            self.log("正在停止任务...")
            
            # 停止刷视频任务
            if self.video_running:
                self.video_running = False
                if self.video_bot and self.video_bot.driver:
                    try:
                        self.video_bot.driver.quit()
                        self.log("[刷视频] 浏览器已关闭")
                    except Exception as e:
                        self.log(f"[刷视频] 关闭浏览器时出错: {e}")
                self.video_bot = None
                self.log("[刷视频] 任务已停止")
            
            # 停止答题任务
            if self.homework_running:
                self.homework_running = False
                if self.homework_bot and self.homework_bot.driver:
                    try:
                        self.homework_bot.driver.quit()
                        self.log("[答题] 浏览器已关闭")
                    except Exception as e:
                        self.log(f"[答题] 关闭浏览器时出错: {e}")
                self.homework_bot = None
                self.log("[答题] 任务已停止")
            
            # 停止考试任务
            if self.exam_running:
                self.exam_running = False
                if self.exam_bot and self.exam_bot.driver:
                    try:
                        self.exam_bot.driver.quit()
                        self.log("[考试] 浏览器已关闭")
                    except Exception as e:
                        self.log(f"[考试] 关闭浏览器时出错: {e}")
                self.exam_bot = None
                self.log("[考试] 任务已停止")
            
            self.log("=" * 50)

class LogRedirector:
    """重定向标准输出到GUI"""
    def __init__(self, log_func):
        self.log_func = log_func
    
    def write(self, message):
        if message.strip():
            self.log_func(message.strip())
    
    def flush(self):
        pass

def main():
    if USE_BOOTSTRAP:
        root = ttk.Window(themename=THEME)
    else:
        root = tk.Tk()
    
    app = AutoStudyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

