"""
Strix v2.0 - Intelligent Web Crawler
智能爬虫工具
"""

__version__ = "2.0.0"
__author__ = "TARS"

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 确保目录存在
(Path(__file__).parent / "downloads" / "images").mkdir(parents=True, exist_ok=True)
(Path(__file__).parent / "downloads" / "videos").mkdir(parents=True, exist_ok=True)
(Path(__file__).parent / "downloads" / "texts").mkdir(parents=True, exist_ok=True)
(Path(__file__).parent / "plugins").mkdir(exist_ok=True)

from gui.main_window import main

if __name__ == "__main__":
    main()
