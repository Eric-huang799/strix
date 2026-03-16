# Strix v2.0 插件编写指南

## 📚 简介

Strix 支持通过插件扩展功能，可以为特定网站编写自定义爬取逻辑。

## 🚀 快速开始

### 1. 创建插件文件

在 `plugins` 文件夹中创建新的 `.py` 文件，例如 `plugin_mywebsite.py`。

### 2. 编写插件代码

```python
"""
我的网站插件
"""


class MyWebsitePlugin:
    """自定义网站爬取插件"""
    
    @property
    def name(self):
        """插件名称（显示用）"""
        return "我的网站解析器"
    
    @property
    def domains(self):
        """
        支持的域名列表
        当URL包含这些域名时，会优先使用此插件
        """
        return ['mywebsite.com', 'www.mywebsite.com']
    
    def can_handle(self, url):
        """检查是否可以处理该URL"""
        return any(domain in url for domain in self.domains)
    
    def extract(self, crawler, url, html):
        """
        执行自定义提取
        
        参数:
            crawler: 爬虫实例，可用方法：
                - crawler.session      # requests.Session
                - crawler.log("消息")   # 输出日志
            
            url: 当前网址
            html: 页面HTML源码
        
        返回:
            {
                'images': ['图片URL1', '图片URL2', ...],
                'videos': ['视频URL1', ...],
                'text': '提取的文本内容'
            }
        """
        import re
        
        # 输出日志
        crawler.log(f"正在解析: {url}")
        
        images = []
        videos = []
        
        # 使用正则提取图片
        for img_url in re.findall(r'src="(https?://[^"]+\.(?:jpg|png|gif))"', html):
            images.append(img_url)
        
        # 提取标题
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        title = title_match.group(1) if title_match else "无标题"
        
        # 提取正文
        content_match = re.search(r'<div class="content">(.*?)</div>', html, re.DOTALL)
        content = content_match.group(1) if content_match else ""
        content = re.sub(r'<[^>]+>', '', content)  # 去除HTML标签
        
        return {
            'images': images,
            'videos': videos,
            'text': f"{title}\n\n{content}"
        }
```

### 3. 重启 Strix

插件会自动加载，无需额外配置。

## 📖 API 参考

### crawler 对象

| 属性/方法 | 说明 | 示例 |
|-----------|------|------|
| `crawler.session` | requests.Session 对象 | `resp = crawler.session.get(url)` |
| `crawler.log(msg, level)` | 输出日志 | `crawler.log("成功", "success")` |
| `crawler.download_file(url, folder, filename)` | 下载文件 | `crawler.download_file(img_url, "images")` |

### 日志级别

- `'info'` - 普通信息（蓝色）
- `'success'` - 成功（绿色）
- `'warning'` - 警告（黄色）
- `'error'` - 错误（红色）

## 💡 示例插件

### 图片站插件

```python
class ImageSitePlugin:
    @property
    def name(self):
        return "图片站解析器"
    
    @property
    def domains(self):
        return ['picsite.com']
    
    def can_handle(self, url):
        return 'picsite.com' in url
    
    def extract(self, crawler, url, html):
        import re
        from urllib.parse import urljoin
        
        images = []
        
        # 提取所有高清图片
        for img_path in re.findall(r'data-original="([^"]+)"', html):
            full_url = urljoin(url, img_path)
            images.append(full_url)
        
        crawler.log(f"发现 {len(images)} 张图片", "success")
        
        return {
            'images': images,
            'videos': [],
            'text': ''
        }
```

### 视频站插件（带m3u8支持）

```python
class VideoSitePlugin:
    @property
    def name(self):
        return "视频站解析器"
    
    @property
    def domains(self):
        return ['videosite.com']
    
    def can_handle(self, url):
        return 'videosite.com' in url
    
    def extract(self, crawler, url, html):
        import re
        
        videos = []
        
        # 查找m3u8链接
        m3u8_match = re.search(r'"url":"([^"]+\.m3u8)"', html)
        if m3u8_match:
            m3u8_url = m3u8_match.group(1).replace('\\/', '/')
            videos.append(m3u8_url)
            crawler.log(f"找到m3u8: {m3u8_url}", "success")
        
        return {
            'images': [],
            'videos': videos,
            'text': ''
        }
```

## 🔧 调试技巧

1. **查看日志**: 插件中的 `crawler.log()` 会显示在主界面
2. **打印变量**: 使用 `crawler.log(f"变量值: {variable}")`
3. **检查HTML**: 可以先保存HTML到文件查看结构

## ⚠️ 常见问题

### 插件未加载
- 检查文件名是否以 `plugin_` 开头
- 检查类是否继承了正确的基类
- 查看日志中的加载错误信息

### 提取失败
- 使用 `crawler.log()` 输出调试信息
- 检查正则表达式是否正确
- 确认HTML结构是否与预期一致

## 📞 帮助

如有问题，请检查：
1. `plugins/plugin_template.py` - 官方模板
2. `plugins/plugin_bilibili.py` - B站示例
3. 日志窗口的加载报告
