"""
Strix v2.0 - 插件开发模板（简化版）
适合新手快速上手，只需填写4个地方
"""

# 1️⃣ 插件名称
NAME = "示例站点适配器"

# 2️⃣ 支持的域名列表
DOMAINS = ["example.com", "www.example.com"]

# 3️⃣ 判断是否能处理这个URL
def can_handle(url: str) -> bool:
    """
    检查URL是否属于这个站点
    返回 True 表示这个插件会处理这个URL
    """
    return any(domain in url for domain in DOMAINS)

# 4️⃣ 提取内容
def extract(crawler, url: str, html: str) -> dict:
    """
    从页面HTML中提取内容
    
    参数:
        crawler: 爬虫实例，可以使用:
            - crawler.session  (requests.Session)
            - crawler.log(msg) (记录日志)
        url: 当前页面URL
        html: 页面HTML源代码
    
    返回:
        {
            'images': ['图片URL1', '图片URL2', ...],  # 可选
            'videos': ['视频URL1', ...],               # 可选
            'text': '提取的文本内容'                    # 可选
        }
    """
    import re
    from urllib.parse import urljoin
    
    result = {'images': [], 'videos': [], 'text': ''}
    
    # ===== 在这里写你的提取逻辑 =====
    
    # 示例：提取所有图片
    for match in re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html):
        full_url = urljoin(url, match)
        result['images'].append(full_url)
    
    # 示例：提取标题
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html)
    if title_match:
        result['text'] = f"标题: {title_match.group(1).strip()}"
    
    # ================================
    
    crawler.log(f"{NAME}: 找到 {len(result['images'])} 张图片")
    return result


# ========== 高级用法（可选）==========

# 如果需要更复杂的逻辑，可以继承 SiteAdapter 类
# 参见 plugin_bilibili.py 获取完整示例
