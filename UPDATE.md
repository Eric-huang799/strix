# 🦉 Strix v2.1 - 更新日志

## 📅 2024-03-16 更新

### ✅ 修复的问题

#### 1. 插件加载失败 ✅
**问题**: 启动时显示 "❌ 失败: 未找到有效的 SiteAdapter 子类"
**原因**: 插件模板中的占位定义覆盖了注入的基类
**解决**: 移除插件文件中的 `class SiteAdapter: pass`，改为注释说明

#### 2. 新增"插件管理"功能 ✅
**功能**:
- 🔌 点击主界面"插件管理"按钮打开
- 📝 左侧显示插件模板代码
- 📋 一键复制模板到剪贴板
- 🆕 一键创建新插件文件
- 📂 选择插件文件安装
- 📂 打开插件文件夹（方便手动管理）
- 📋 显示已安装插件列表

#### 3. B站插件增强 ✅
**改进**:
- 添加B站专用请求头（避免403）
- 支持短链接(b23.tv)解析
- 多种方式提取封面图
- 提取UP主信息和头像
- 尝试调用B站API获取高清封面

---

## 📖 快速开始

### 启动程序
双击 `start.bat` 或运行 `python strix.py`

### 添加插件
1. 点击主界面 **"🔌 插件管理"** 按钮
2. 在左侧查看模板，或点击 **"复制模板到剪贴板"**
3. 用记事本/VSCODE粘贴模板并修改
4. 保存为 `.py` 文件
5. 点击 **"选择插件文件"** 安装
6. 安装成功后会自动重新加载

### 编写插件示例
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
        import re
        images = []
        for img in re.findall(r'src="(https?://[^"]+\.jpg)"', html):
            images.append(img)
        return {
            'images': images,
            'videos': [],
            'text': '提取成功'
        }
```

---

## 🔧 常见问题

### Q: 插件安装后没有生效？
A: 点击"刷新列表"按钮重新加载，或重启程序。

### Q: B站爬取失败？
A: B站有反爬机制，建议：
1. 确保使用B站插件（会自动添加请求头）
2. 不要爬取太快（程序已内置随机延迟）
3. 部分视频需要登录才能看，插件只能获取公开内容

### Q: 如何手动添加插件？
A: 直接把 `.py` 文件放到 `plugins` 文件夹，然后重启程序。

---

## 📝 文件结构

```
Strix-v2/
├── strix.py              # 主入口
├── start.bat             # 启动脚本
├── gui/
│   ├── main_window.py    # 主界面
│   └── plugin_dialog.py  # 插件管理对话框 ⭐新增
├── core/
│   ├── crawler.py        # 爬虫核心
│   └── plugin_manager.py # 插件管理（修复注入问题）⭐修复
├── plugins/              # 插件目录
│   ├── plugin_template.py # 模板（修复）⭐修复
│   ├── plugin_bilibili.py # B站插件（增强版）⭐改进
│   └── README.md         # 插件开发文档
└── downloads/            # 下载目录
```

---

Made by TARS 🤖
