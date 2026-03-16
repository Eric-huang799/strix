# 🦉 Strix v2.0 - 发布说明

## 📦 项目信息

- **名称**: Strix v2.0
- **版本**: 2.0.0
- **作者**: TARS (AI Assistant)
- **许可证**: MIT

## ✨ 核心特性

### 1. 现代化界面
- 深色主题设计
- 简洁直观的操作
- 实时日志显示

### 2. 强大的爬取能力
- 图片自动提取（支持 data-src、background-image 等）
- 视频下载（支持 m3u8 流自动合并）
- 智能文本提取（过滤广告和导航）

### 3. 反爬机制
- User-Agent 轮换
- 随机请求延迟
- 自动重试机制
- 完整请求头模拟

### 4. 插件系统 v2
- 热重载支持
- 模板化开发
- 自动域名匹配
- 详细的加载报告

## 📂 项目结构

```
Strix-v2/
├── strix.py                 # 主入口
├── start.bat               # Windows启动脚本
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── crawler.py         # 爬虫引擎
│   └── plugin_manager.py  # 插件管理
├── gui/                    # 界面模块
│   └── main_window.py     # 主界面
├── plugins/                # 插件目录
│   ├── plugin_template.py # 插件模板
│   ├── plugin_bilibili.py # B站插件示例
│   └── README.md          # 插件开发文档
├── downloads/              # 下载目录
│   ├── images/
│   ├── videos/
│   └── texts/
├── test.py                 # 测试脚本
├── README.md              # 项目说明
└── 使用说明.md            # 中文使用指南
```

## 🚀 快速开始

```bash
# 安装依赖
pip install requests beautifulsoup4 pillow

# 运行程序
python strix.py

# 或双击 start.bat
```

## 🔌 插件开发示例

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

## 📝 改进点（对比 v1）

| 功能 | v1 | v2 |
|------|-----|-----|
| 界面 | 复杂难用 | 简洁现代 |
| 插件系统 | 经常加载失败 | 热重载+详细报告 |
| 代码结构 | 单一文件 55KB | 模块化清晰 |
| 反爬能力 | 基础 | 完善 |
| 用户体验 | 一般 | 优秀 |

## 🎯 发布清单

- [x] 核心爬虫引擎
- [x] 现代化 GUI
- [x] 插件系统
- [x] 示例插件
- [x] 完整文档
- [x] 测试脚本
- [x] 使用说明

## 📜 许可证

MIT License

---

**准备好发布了！** 🎉

提交到 GitHub:
```bash
git init
git add .
git commit -m "Initial release: Strix v2.0"
git remote add origin https://github.com/yourusername/strix.git
git push -u origin main
```
