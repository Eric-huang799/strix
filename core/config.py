"""
Strix v2.0 - 配置文件
支持自定义下载路径、代理、限速等
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class StrixConfig:
    """Strix 配置管理器"""
    
    DEFAULT_CONFIG = {
        # 下载设置
        "download": {
            "output_dir": "downloads",
            "image_folder": "images",
            "video_folder": "videos", 
            "text_folder": "texts",
            "max_filename_length": 200,
            "skip_existing": True,  # 跳过已存在的文件
        },
        
        # 网络设置
        "network": {
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 2,
            "concurrent_downloads": 5,
            "random_delay_min": 0.5,
            "random_delay_max": 2.0,
        },
        
        # 代理设置（特殊领域可能用到）
        "proxy": {
            "enabled": False,
            "http": "",
            "https": "",
            "rotation": False,  # 是否轮换代理
            "proxy_list": [],   # 代理列表，如 ["http://1.1.1.1:8080", ...]
        },
        
        # 请求头设置
        "headers": {
            "user_agent_rotation": True,
            "custom_headers": {},  # 自定义请求头
        },
        
        # 爬虫行为
        "crawler": {
            "follow_redirects": True,
            "verify_ssl": False,
            "respect_robots_txt": False,  # 是否遵守 robots.txt
            "max_depth": 3,  # 最大爬取深度（如果支持递归）
        },
        
        # 插件设置
        "plugins": {
            "auto_reload": True,  # 热重载
            "enabled": [],  # 启用的插件列表，空表示全部
        },
        
        # GUI设置
        "gui": {
            "theme": "system",  # system/dark/light
            "auto_scroll_log": True,
            "show_notifications": True,
        }
    }
    
    def __init__(self, config_path: str = "strix_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置，如果不存在则创建默认配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并用户配置和默认配置
                return self._merge_config(self.DEFAULT_CONFIG, user_config)
            except Exception as e:
                print(f"配置加载失败，使用默认配置: {e}")
        
        # 创建默认配置文件
        self.save_config(self.DEFAULT_CONFIG)
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """递归合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，支持点号路径如 'download.output_dir'"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save_config(self, config: Optional[Dict] = None):
        """保存配置到文件"""
        config = config or self.config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"配置保存失败: {e}")
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """获取代理字典（给requests用）"""
        if not self.get('proxy.enabled'):
            return None
        
        http_proxy = self.get('proxy.http')
        https_proxy = self.get('proxy.https')
        
        proxy_dict = {}
        if http_proxy:
            proxy_dict['http'] = http_proxy
        if https_proxy:
            proxy_dict['https'] = https_proxy
        
        return proxy_dict if proxy_dict else None
    
    def get_random_proxy(self) -> Optional[str]:
        """从代理列表随机获取一个代理"""
        import random
        proxy_list = self.get('proxy.proxy_list', [])
        if proxy_list and self.get('proxy.rotation'):
            return random.choice(proxy_list)
        return self.get('proxy.http') or self.get('proxy.https')


# 全局配置实例
_config_instance = None

def get_config(config_path: str = "strix_config.json") -> StrixConfig:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = StrixConfig(config_path)
    return _config_instance
