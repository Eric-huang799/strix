# 🦉 Strix v2.0

> 简洁优雅的智能爬虫工具

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ 功能特点

- 🖼️ **多媒体爬取** - 自动提取图片、视频、文本
- 🛡️ **反爬机制** - User-Agent轮换、随机延迟、重试机制
- 🔌 **插件系统** - 支持自定义网站适配器，热重载
- 🎨 **简洁界面** - 现代化UI设计，上手即用
- 📹 **m3u8支持** - 自动下载并合并视频流
- 🧠 **智能提取** - 自动识别正文内容，过滤广告导航

## 🚀 快速开始

### 安装依赖

```bash
pip install requests beautifulsoup4 pillow
```

### 运行程序

```bash
python strix.py
```

### 基本使用

1. 输入目标网址
2. 选择要下载的内容类型（图片/视频/文本）
3. 点击"开始爬取"
4. 在下载目录查看结果

## 🔌 插件开发

Strix 支持通过插件扩展功能。在 `plugins` 目录创建 `.py` 文件：

```python
class MyPlugin:
    @property
    def name(self):
        return "我的插件"
    
    @property
    def domains(self):
        return ['example.com']
    
    def can_handle(self, url):
        return 'example.com' in url
    
    def extract(self, crawler, url, html):
        # 自定义提取逻辑
        return {
            'images': [],
            'videos': [],
            'text': '提取的内容'
        }
```

详见 [插件开发指南](plugins/README.md)

## 📁 项目结构

```
strix-v2/
├── strix.py              # 主入口
├── core/
│   ├── crawler.py        # 爬虫核心
│   └── plugin_manager.py # 插件管理
├── gui/
│   └── main_window.py    # 主界面
├── plugins/              # 插件目录
│   ├── plugin_template.py
│   ├── plugin_bilibili.py
│   └── README.md
└── downloads/            # 下载目录
    ├── images/
    ├── videos/
    └── texts/
```

## 🛡️ 反爬特性

- User-Agent 随机轮换
- 请求间隔随机延迟
- 自动重试机制（指数退避）
- Referer 伪造
- 请求头完整模拟

## ⚠️ 免责声明

本工具仅供学习研究使用。请遵守以下准则：

1. 遵守目标网站的 `robots.txt` 规则
2. 不要对网站造成过大负载（使用合理的线程数和延迟）
3. 仅爬取公开可访问的内容
4. 尊重版权，不要用于非法用途

使用本工具产生的任何法律责任由使用者自行承担。

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢所有贡献者和用户的支持！

---

Made with ❤️ by [TARS](https://github.com/yourusername)
