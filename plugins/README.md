# Strix 插件开发指南

## 快速开始（2分钟）

最简单的方式：复制 `plugins/plugin_simple_template.py`，改4个地方就行：

```python
NAME = "你的插件名称"                           # 1. 改名字
DOMAINS = ["site.com", "www.site.com"]         # 2. 改域名

def can_handle(url):                           # 3. 判断URL
    return "site.com" in url

def extract(crawler, url, html):               # 4. 写提取逻辑
    # 用正则或BeautifulSoup提取内容
    return {'images': [...], 'videos': [...], 'text': '...'}
```

保存为 `plugins/my_site.py`，重启 Strix 即可！

---

## 完整示例：B站适配器

参见 `plugin_bilibili.py`，展示了：
- 处理多种URL格式 (bilibili.com, b23.tv)
- 解析JSON数据
- 处理特殊请求头
- 调用API获取视频信息

---

## API 参考

### crawler 对象可用方法

```python
# 发送HTTP请求
response = crawler.session.get(url, headers=...)

# 记录日志（会显示在GUI中）
crawler.log("消息", level="info")   # level: info/warning/error

# 下载文件
crawler.download_file(url, folder="images", filename="xxx.jpg")

# 随机延迟（防封）
crawler._random_delay(0.5, 2.0)
```

### 返回值格式

```python
{
    'images': ['https://.../1.jpg', 'https://.../2.png'],  # 图片URL列表
    'videos': ['https://.../video.mp4'],                    # 视频URL列表  
    'text': '页面文本内容'                                   # 提取的文本
}
```

---

## 调试技巧

1. **打印调试**: 在 extract() 里用 `print()` 输出变量
2. **查看HTML**: 先 `print(html[:1000])` 看看页面结构
3. **浏览器F12**: 在浏览器开发者工具里找到元素的选择器

---

## 常见问题

**Q: 插件没加载？**  
A: 检查：1) 文件在 plugins/ 目录 2) 文件后缀是 .py 3) 语法没错误

**Q: 怎么提取特定class的元素？**  
A: 用 BeautifulSoup: `soup.find('div', class_='content')`

**Q: 需要登录/Cookie怎么办？**  
A: 可以在 extract() 里用 `crawler.session.headers.update({'Cookie': '...'})`
