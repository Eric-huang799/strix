"""
Strix Core Module
"""

from .crawler import StrixCrawler
from .plugin_manager import PluginManager, SiteAdapter

__all__ = ['StrixCrawler', 'PluginManager', 'SiteAdapter']
