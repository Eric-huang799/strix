"""
Bilibili 插件 - 爬取B站视频和图片
增强版 - 带反反爬处理
"""
# 注意：SiteAdapter 基类会由主程序自动注入


class BilibiliPlugin:
    """B站专用爬取插件 - 增强版"""
    
    @property
    def name(self):
        return "Bilibili解析器(增强版)"
    
    @property
    def domains(self):
        return ['bilibili.com', 'b23.tv', 'www.bilibili.com']
    
    def can_handle(self, url):
        return any(domain in url for domain in self.domains)
    
    def extract(self, crawler, url, html):
        import re
        import json
        import time
        
        crawler.log("正在解析B站页面...", 'info')
        
        # B站需要特殊请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0.36',
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com'
        }
        
        # 更新session的请求头
        crawler.session.headers.update(headers)
        
        # 如果是短链接，先获取真实URL
        if 'b23.tv' in url:
            try:
                resp = crawler.session.head(url, allow_redirects=True, timeout=10)
                url = resp.url
                crawler.log(f"短链接解析: {url}", 'info')
            except:
                pass
        
        images = []
        videos = []
        text_content = []
        
        # 1. 提取OpenGraph信息（最可靠）
        og_title = re.search(r'property="og:title" content="([^"]+)"', html)
        og_image = re.search(r'property="og:image" content="([^"]+)"', html)
        og_desc = re.search(r'property="og:description" content="([^"]+)"', html)
        
        title = og_title.group(1) if og_title else "B站视频"
        if og_image:
            images.append(og_image.group(1))
        desc = og_desc.group(1) if og_desc else ""
        
        text_content.append(f"标题: {title}")
        if desc:
            text_content.append(f"简介: {desc}")
        
        # 2. 提取UP主信息
        up_match = re.search(r'"up_name":"([^"]+)"', html)
        if up_match:
            up_name = up_match.group(1).encode('utf-8').decode('unicode_escape')
            text_content.append(f"UP主: {up_name}")
        
        # 3. 提取视频封面（多种方式）
        cover_patterns = [
            r'"pic":"([^"]+)"',
            r'"cover":"([^"]+)"',
            r'src="([^"]+@\d+\.\w+)"',
            r'data-src="([^"]+)"'
        ]
        
        for pattern in cover_patterns:
            for match in re.findall(pattern, html):
                img_url = match.replace('\\u002F', '/')
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                if img_url.startswith('http') and img_url not in images:
                    images.append(img_url)
        
        # 4. 尝试获取JSON数据
        try:
            # 查找 __INITIAL_STATE__
            initial_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});\s*</script>', html, re.DOTALL)
            if initial_match:
                data = json.loads(initial_match.group(1))
                
                # 提取视频信息
                if 'videoData' in data:
                    video_data = data['videoData']
                    if 'pic' in video_data and video_data['pic'] not in images:
                        images.append(video_data['pic'])
                    if 'title' in video_data:
                        title = video_data['title']
                    if 'desc' in video_data:
                        text_content.append(f"详细简介: {video_data['desc']}")
                
                # 提取UP主头像
                if 'upData' in data and 'face' in data['upData']:
                    face = data['upData']['face']
                    if face not in images:
                        images.append(face)
        except Exception as e:
            crawler.log(f"JSON解析失败: {str(e)[:50]}", 'warning')
        
        # 5. 尝试获取视频URL（需要额外请求）
        try:
            # 提取BV号
            bv_match = re.search(r'BV\w+', url)
            if bv_match:
                bvid = bv_match.group(0)
                crawler.log(f"检测到BV号: {bvid}", 'info')
                
                # 获取视频信息API（简化版，实际可能需要更多参数）
                api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
                time.sleep(0.5)  # 避免请求过快
                
                api_resp = crawler.session.get(api_url, timeout=10)
                if api_resp.status_code == 200:
                    api_data = api_resp.json()
                    if api_data.get('data'):
                        data = api_data['data']
                        # 提取封面
                        if 'pic' in data and data['pic'] not in images:
                            images.append(data['pic'])
                        # 提取UP主头像
                        if 'owner' in data and 'face' in data['owner']:
                            images.append(data['owner']['face'])
        except Exception as e:
            crawler.log(f"API请求失败: {str(e)[:50]}", 'warning')
        
        # 6. 提取所有B站图片链接
        for img_url in re.findall(r"https?://[^\s\"'<>]+\.hdslb\.com/[^\s\"'<>]+", html):
            clean_url = img_url.replace('\\u002F', '/').split('@')[0]
            if clean_url not in images:
                images.append(clean_url)
        
        # 去重并清理
        unique_images = []
        for img in images:
            if img and img not in unique_images and img.startswith('http'):
                unique_images.append(img)
        
        # 限制图片数量
        unique_images = unique_images[:20]
        
        crawler.log(f"发现 {len(unique_images)} 张图片", 'success')
        
        return {
            'images': unique_images,
            'videos': videos,  # B站视频需要特殊处理，这里只返回封面
            'text': '\n\n'.join(text_content)
        }
