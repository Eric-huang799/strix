"""
Strix v2.0 - Core Crawler Engine
高性能爬虫核心，带反检测机制
"""

import requests
import re
import json
import os
import time
import random
import hashlib
from urllib.parse import urljoin, urlparse, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Set, Optional, Callable
import logging

# 禁用SSL警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class StrixCrawler:
    """Strix 爬虫核心引擎"""
    
    def __init__(self, output_dir: str = "downloads", log_callback: Optional[Callable] = None):
        self.session = requests.Session()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.log_callback = log_callback
        
        # 下载统计
        self.stats = {'images': 0, 'videos': 0, 'texts': 0, 'errors': 0}
        self.downloaded = set()
        self.is_running = False
        
        # 反检测配置
        self._setup_headers()
        
    def _setup_headers(self):
        """配置反检测请求头"""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def log(self, message: str, level: str = 'info'):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message, level)
    
    def _get_headers(self, referer: Optional[str] = None) -> Dict:
        """动态生成请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Referer': referer or 'https://www.google.com/'
        }
    
    def _random_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        """随机延迟防检测"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        filename = unquote(filename)
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'_+', '_', filename).strip('_')
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:150] + ext
        return filename or 'unknown'
    
    def _get_ext(self, url: str, content_type: Optional[str] = None) -> str:
        """智能获取文件扩展名"""
        ext_map = {
            'image/jpeg': '.jpg', 'image/jpg': '.jpg', 'image/png': '.png',
            'image/gif': '.gif', 'image/webp': '.webp', 'image/svg+xml': '.svg',
            'video/mp4': '.mp4', 'video/webm': '.webm', 'video/x-matroska': '.mkv',
            'video/quicktime': '.mov', 'application/x-mpegURL': '.m3u8'
        }
        
        if content_type and content_type in ext_map:
            return ext_map[content_type]
        
        parsed = urlparse(url)
        path = unquote(parsed.path)
        if '.' in path:
            ext = os.path.splitext(path)[1].lower()
            valid_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', 
                         '.mp4', '.webm', '.mkv', '.mov', '.m3u8', '.ts']
            if ext in valid_exts:
                return ext if ext != '.jpeg' else '.jpg'
        
        return '.jpg'
    
    def fetch_page(self, url: str, retry: int = 3) -> Optional[requests.Response]:
        """获取页面内容，带重试机制"""
        for attempt in range(retry):
            try:
                headers = self._get_headers()
                response = self.session.get(
                    url, headers=headers, timeout=30,
                    verify=False, allow_redirects=True
                )
                response.raise_for_status()
                response.encoding = response.apparent_encoding or 'utf-8'
                return response
            except Exception as e:
                self.log(f"请求失败 (尝试 {attempt + 1}/{retry}): {str(e)[:50]}", 'warning')
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)
                else:
                    self.stats['errors'] += 1
        return None
    
    def extract_media(self, html: str, base_url: str) -> Dict[str, Set[str]]:
        """提取图片和视频URL"""
        results = {'images': set(), 'videos': set()}
        
        # 图片提取规则
        img_patterns = [
            r'<img[^>]+src=["\']([^"\']+)["\']',
            r'<img[^>]+data-src=["\']([^"\']+)["\']',
            r'<img[^>]+data-original=["\']([^"\']+)["\']',
            r'background-image:\s*url\(["\']?([^"\')]+)["\']?\)',
            r'["\']url["\']\s*:\s*["\'](https?://[^"\']+\.(?:jpg|jpeg|png|gif|webp))["\']'
        ]
        
        for pattern in img_patterns:
            for match in re.findall(pattern, html, re.IGNORECASE):
                full_url = urljoin(base_url, match)
                if full_url not in self.downloaded:
                    results['images'].add(full_url)
        
        # 视频提取规则
        video_patterns = [
            r'<video[^>]+src=["\']([^"\']+)["\']',
            r'<source[^>]+src=["\']([^"\']+)["\'][^>]*type=["\']video',
            r'["\']videoUrl["\']\s*:\s*["\']([^"\']+)["\']',
            r'["\']play_url["\']\s*:\s*["\']([^"\']+)["\']',
            r'(https?://[^"\']+\.(?:mp4|webm|mkv|mov))',
            r'(https?://[^"\']+\.m3u8[^"\']*)'
        ]
        
        for pattern in video_patterns:
            for match in re.findall(pattern, html, re.IGNORECASE):
                full_url = urljoin(base_url, match)
                if full_url not in self.downloaded:
                    results['videos'].add(full_url)
        
        # JSON中的URL
        for url in re.findall(r'https?://[^"\s<>]+?\.(?:jpg|jpeg|png|gif|webp|mp4|webm|m3u8)[^"\s<>]*', html):
            if '.m3u8' in url or any(v in url for v in ['.mp4', '.webm', '.mkv']):
                results['videos'].add(url)
            else:
                results['images'].add(url)
        
        return results
    
    def extract_text(self, html: str) -> Dict[str, str]:
        """智能提取正文文本"""
        # 清理
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<header[^>]*>.*?</header>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 提取标题
        title = ''
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        
        # 提取正文
        paragraphs = []
        patterns = [
            r'<p[^>]*>([^<]+)</p>',
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*class=["\'][^"\']*(?:content|article|post)[^"\']*["\'][^>]*>(.*?)</div>'
        ]
        
        for pattern in patterns:
            for match in re.findall(pattern, text, re.DOTALL | re.IGNORECASE):
                clean = re.sub(r'<[^>]+>', ' ', match)
                clean = re.sub(r'\s+', ' ', clean).strip()
                if len(clean) > 20:
                    paragraphs.append(clean)
        
        return {
            'title': title,
            'content': '\n\n'.join(paragraphs[:50])  # 限制段落数
        }
    
    def download_file(self, url: str, folder: str, filename: Optional[str] = None,
                     progress_callback: Optional[Callable] = None,
                     custom_referer: Optional[str] = None) -> bool:
        """下载单个文件"""
        try:
            if url in self.downloaded:
                return True
            
            if not self.is_running:
                return False
            
            headers = self._get_headers()
            
            # 如果提供了自定义referer，使用它
            if custom_referer:
                headers['Referer'] = custom_referer
            # 针对B站图片的特殊处理
            elif 'hdslb.com' in url or 'bilibili' in url:
                headers['Referer'] = 'https://www.bilibili.com/'
                headers['Origin'] = 'https://www.bilibili.com'
            
            response = self.session.get(url, headers=headers, stream=True, timeout=60, verify=False)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            if not filename:
                parsed = urlparse(url)
                original_name = os.path.basename(unquote(parsed.path)) or 'unknown'
                name, _ = os.path.splitext(original_name)
                ext = self._get_ext(url, content_type)
                filename = self._sanitize_filename(name) + ext
            
            filepath = self.output_dir / folder / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # 处理重名
            counter = 1
            original = filepath
            while filepath.exists():
                stem = original.stem
                suffix = original.suffix
                filepath = original.with_name(f"{stem}_{counter}{suffix}")
                counter += 1
            
            # 下载
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not self.is_running:
                        return False
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(url, downloaded, total_size)
            
            self.downloaded.add(url)
            
            if folder == 'images':
                self.stats['images'] += 1
            elif folder == 'videos':
                self.stats['videos'] += 1
            
            self._random_delay(0.3, 1.0)
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"下载失败: {str(e)[:50]}", 'error')
            return False
    
    def download_m3u8(self, url: str, folder: str = 'videos') -> bool:
        """下载m3u8视频流"""
        try:
            if url in self.downloaded:
                return True
            
            self.log(f"解析m3u8: {url[:60]}...", 'info')
            
            headers = self._get_headers()
            response = self.session.get(url, headers=headers, timeout=30, verify=False)
            content = response.text
            
            # 解析m3u8
            base_url = url.rsplit('/', 1)[0] + '/'
            ts_urls = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    ts_urls.append(urljoin(base_url, line) if not line.startswith('http') else line)
            
            if not ts_urls:
                self.log("未找到视频片段", 'warning')
                return False
            
            # 限制片段数
            ts_urls = ts_urls[:100]
            
            # 创建临时目录
            temp_dir = self.output_dir / folder / 'temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 下载ts片段
            self.log(f"下载 {len(ts_urls)} 个视频片段...", 'info')
            ts_files = []
            
            for i, ts_url in enumerate(ts_urls):
                if not self.is_running:
                    return False
                
                ts_filename = f"segment_{i:04d}.ts"
                ts_path = temp_dir / ts_filename
                
                try:
                    ts_response = self.session.get(ts_url, headers=headers, timeout=30, verify=False)
                    with open(ts_path, 'wb') as f:
                        f.write(ts_response.content)
                    ts_files.append(ts_path)
                except Exception as e:
                    self.log(f"片段下载失败: {str(e)[:30]}", 'warning')
                    continue
            
            if not ts_files:
                return False
            
            # 合并
            filename = self._sanitize_filename(url.split('/')[-1].split('.')[0]) + '.mp4'
            output_path = self.output_dir / folder / filename
            
            counter = 1
            original = output_path
            while output_path.exists():
                output_path = original.with_name(f"{original.stem}_{counter}{original.suffix}")
                counter += 1
            
            self.log("合并视频片段...", 'info')
            with open(output_path, 'wb') as outfile:
                for ts_file in ts_files:
                    with open(ts_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            # 清理
            for ts_file in ts_files:
                ts_file.unlink()
            temp_dir.rmdir()
            
            self.downloaded.add(url)
            self.stats['videos'] += 1
            
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            self.log(f"m3u8下载失败: {str(e)[:50]}", 'error')
            return False
    
    def crawl(self, url: str, options: Optional[Dict] = None) -> bool:
        """主爬取方法"""
        options = options or {}
        download_images = options.get('images', True)
        download_videos = options.get('videos', True)
        extract_text = options.get('text', True)
        max_workers = options.get('threads', 4)
        
        self.is_running = True
        self.stats = {'images': 0, 'videos': 0, 'texts': 0, 'errors': 0}
        
        self.log(f"🦉 Strix 开始分析: {url}", 'info')
        
        # 获取页面
        response = self.fetch_page(url)
        if not response:
            self.log("❌ 无法访问该网址", 'error')
            self.is_running = False
            return False
        
        html = response.text
        base_url = response.url
        
        # 提取媒体
        media = self.extract_media(html, base_url)
        self.log(f"📸 发现 {len(media['images'])} 个图片, {len(media['videos'])} 个视频", 'info')
        
        # 下载图片
        if download_images and media['images'] and self.is_running:
            self.log("⬇️ 开始下载图片...", 'info')
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.download_file, img_url, 'images') 
                          for img_url in media['images']]
                for future in as_completed(futures):
                    if not self.is_running:
                        break
        
        # 下载视频
        if download_videos and media['videos'] and self.is_running:
            self.log("⬇️ 开始下载视频...", 'info')
            for video_url in media['videos']:
                if not self.is_running:
                    break
                if '.m3u8' in video_url:
                    self.download_m3u8(video_url)
                else:
                    self.download_file(video_url, 'videos')
        
        # 提取文本
        if extract_text and self.is_running:
            self.log("📝 提取文本内容...", 'info')
            text_data = self.extract_text(html)
            text_data['url'] = url
            
            text_dir = self.output_dir / 'texts'
            text_dir.mkdir(exist_ok=True)
            
            domain = urlparse(url).netloc.replace('.', '_')
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            text_file = text_dir / f"{domain}_{timestamp}.txt"
            
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"标题: {text_data['title']}\n")
                f.write(f"来源: {text_data['url']}\n")
                f.write(f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(text_data['content'])
            
            self.stats['texts'] += 1
            self.log(f"💾 文本已保存: {text_file.name}", 'success')
        
        self.is_running = False
        
        # 输出统计
        self.log(f"\n✅ 抓取完成！", 'success')
        self.log(f"📊 图片: {self.stats['images']}, 视频: {self.stats['videos']}, 文本: {self.stats['texts']}", 'info')
        if self.stats['errors']:
            self.log(f"⚠️ 错误: {self.stats['errors']} 个", 'warning')
        
        return True
    
    def stop(self):
        """停止爬取"""
        self.is_running = False
        self.log("🛑 正在停止...", 'warning')
