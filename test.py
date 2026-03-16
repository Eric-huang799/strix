"""
Strix v2.0 - Test Script
快速测试爬虫功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.crawler import StrixCrawler


def test_crawler():
    """测试爬虫核心功能"""
    print("测试 Strix v2.0 核心功能\n")
    
    # 创建爬虫实例
    crawler = StrixCrawler(output_dir="test_downloads")
    
    # 测试1: 提取媒体URL
    print("测试1: 提取图片和视频URL...")
    test_html = '''
    <html>
    <body>
        <img src="https://example.com/image1.jpg">
        <img data-src="https://example.com/image2.png">
        <video src="https://example.com/video.mp4">
        <a href="https://example.com/video2.m3u8">Stream</a>
    </body>
    </html>
    '''
    
    media = crawler.extract_media(test_html, "https://example.com")
    print(f"  [OK] 发现 {len(media['images'])} 张图片")
    print(f"  [OK] 发现 {len(media['videos'])} 个视频")
    
    # 测试2: 提取文本
    print("\n测试2: 提取文本内容...")
    test_html2 = '''
    <html>
    <head><title>测试页面</title></head>
    <body>
        <nav>导航</nav>
        <p>这是正文第一段，应该被提取。这是正文第一段，应该被提取。</p>
        <p>这是正文第二段，也应该被提取。这是正文第二段，也应该被提取。</p>
        <footer>页脚</footer>
    </body>
    </html>
    '''
    
    text = crawler.extract_text(test_html2)
    print(f"  [OK] 标题: {text['title']}")
    print(f"  [OK] 正文长度: {len(text['content'])} 字符")
    
    # 测试3: 插件管理器
    print("\n测试3: 插件系统...")
    from core.plugin_manager import PluginManager
    
    pm = PluginManager("plugins")
    pm.load_plugins()
    print(f"  [OK] 加载了 {len(pm.adapters)} 个插件")
    
    for adapter in pm.adapters:
        print(f"    - {adapter.name}")
    
    print("\n[PASS] 所有测试通过！")
    return True


if __name__ == "__main__":
    try:
        test_crawler()
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
