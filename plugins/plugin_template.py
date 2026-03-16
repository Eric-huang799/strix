"""
Strix 插件编写模板
复制此文件并重命名，然后修改对应的方法即可
"""
# 注意：SiteAdapter 基类会由主程序自动注入，不需要在这里定义


class MyPlugin:
    """
    示例插件 - 爬取特定网站
    类名可以自定义，建议用描述性的名称如: BilibiliPlugin, ZhihuPlugin
    """
    
    @property
    def name(self):
        """插件名称，会显示在界面上"""
        return "示例网站插件"
    
    @property
    def domains(self):
        """
        支持的域名列表
        当用户输入的URL包含这些域名时，会优先使用此插件
        """
        return ['example.com', 'www.example.com']
    
    def can_handle(self, url):
        """
        检查是否可以处理该URL
        返回 True 表示使用此插件，False 表示使用默认爬取
        """
        return any(domain in url for domain in self.domains)
    
    def extract(self, crawler, url, html):
        """
        执行自定义提取逻辑
        
        参数:
            crawler: 爬虫实例，可以使用:
                - crawler.session  # requests.Session 对象
                - crawler.log("消息")  # 输出日志
                - crawler.download_file(url, folder, filename)  # 下载文件
            
            url: 当前爬取的网址
            html: 页面HTML源码
        
        返回:
            dict: 必须包含以下键
                {
                    'images': ['图片URL1', '图片URL2', ...],  # 图片链接列表
                    'videos': ['视频URL1', '视频URL2', ...],  # 视频链接列表
                    'text': '提取的文本内容'  # 文本内容
                }
        """
        import re
        
        crawler.log(f"插件运行中: {self.name}")
        
        # 使用正则表达式提取内容
        images = []
        videos = []
        
        # 示例：提取所有图片
        img_pattern = r'<img[^\u003e]+src=["\']([^"\']+)["\']'
        for match in re.findall(img_pattern, html):
            if match.startswith('http'):
                images.append(match)
        
        # 示例：提取标题和正文
        title_match = re.search(r'<h1[^\u003e]*\u003e([^\u003c]+)\u003c/h1\u003e', html)
        title = title_match.group(1) if title_match else "无标题"
        
        content_match = re.search(r'<div class="content"\u003e(.*?)\u003c/div\u003e', html, re.DOTALL)
        content = content_match.group(1) if content_match else ""
        content = re.sub(r'<[^\u003e]+\u003e', '', content)  # 去除HTML标签
        
        return {
            'images': images,
            'videos': videos,
            'text': f"{title}\n\n{content}"
        }
