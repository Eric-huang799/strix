# Strix v2 - Intelligent Web Crawler

Strix 是一款基于 PyQt6 的高性能可视化爬虫工具，支持插件扩展和多种内容抓取。

## 功能特性

- 🕷️ **智能爬虫引擎** - 支持图片、视频、文本自动提取
- 🔌 **插件系统** - 热重载适配器，轻松扩展新站点
- 🎨 **PyQt6 GUI** - 现代化界面，实时日志和进度显示
- 🛡️ **反检测机制** - 随机延迟、请求头轮换、Cookie支持
- 📁 **自动分类存储** - 按类型和时间组织下载内容

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
python strix.py
```

或使用启动脚本：
```bash
start.bat  # Windows
```

## 系统要求

- Python 3.10+
- Windows 10/11 / macOS / Linux

## 创建插件

参见 `plugins/plugin_template.py` 和 `plugins/README.md`

## 许可证

MIT License - 详见 [LICENSE](LICENSE)
