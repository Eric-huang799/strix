"""
Strix v2.0 - Plugin System
强大的插件系统，支持热重载
"""

import importlib.util
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Any


class SiteAdapter(ABC):
    """
    网站适配器基类
    所有自定义插件必须继承此类
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def domains(self) -> List[str]:
        """
        支持的域名列表
        例如: ['bilibili.com', 'b23.tv']
        """
        pass
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """检查是否可以处理该URL"""
        pass
    
    @abstractmethod
    def extract(self, crawler, url: str, html: str) -> Dict[str, Any]:
        """
        执行自定义提取
        
        Args:
            crawler: 爬虫实例 (可使用 crawler.session, crawler.log 等)
            url: 目标URL
            html: 页面HTML
            
        Returns:
            dict: {'images': [], 'videos': [], 'text': ''}
        """
        pass


class PluginManager:
    """插件管理器 - 支持热重载"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(exist_ok=True)
        self.adapters: List[SiteAdapter] = []
        self.load_results: List[tuple] = []
        
    def load_plugins(self) -> None:
        """加载所有插件"""
        self.adapters = []
        self.load_results = []
        
        # 创建 __init__.py
        init_file = self.plugin_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Strix Plugins\n")
        
        # 只加载 .py 文件
        py_files = [f for f in self.plugin_dir.glob("*.py") 
                   if not f.name.startswith('_')]
        
        if not py_files:
            self.load_results.append(("扫描", "没有发现插件文件", "info"))
            return
        
        for file_path in py_files:
            try:
                adapter = self._load_plugin_file(file_path)
                if adapter:
                    self.adapters.append(adapter)
                    self.load_results.append((
                        file_path.name, 
                        f"✅ 成功加载: {adapter.name}", 
                        "success"
                    ))
                else:
                    self.load_results.append((
                        file_path.name, 
                        "❌ 失败: 未找到有效的 SiteAdapter 子类", 
                        "error"
                    ))
            except SyntaxError as e:
                self.load_results.append((
                    file_path.name, 
                    f"❌ 语法错误 (行{e.lineno}): {e.msg}", 
                    "error"
                ))
            except Exception as e:
                self.load_results.append((
                    file_path.name, 
                    f"❌ 错误: {str(e)}", 
                    "error"
                ))
    
    def _load_plugin_file(self, file_path: Path) -> Optional[SiteAdapter]:
        """加载单个插件文件"""
        import builtins
        
        # 将 SiteAdapter 注入到 builtins，确保插件可以继承
        builtins.SiteAdapter = SiteAdapter
        
        # 创建独立模块命名空间
        module_name = f"strix_plugin_{file_path.stem}_{id(file_path)}"
        
        spec = importlib.util.spec_from_file_location(
            module_name, 
            file_path,
            submodule_search_locations=None
        )
        module = importlib.util.module_from_spec(spec)
        
        # 同时注入到模块全局命名空间
        module.__dict__['SiteAdapter'] = SiteAdapter
        
        try:
            spec.loader.exec_module(module)
        finally:
            # 清理 builtins
            if hasattr(builtins, 'SiteAdapter'):
                delattr(builtins, 'SiteAdapter')
        
        # 查找适配器类 - 同时检查是否继承 SiteAdapter 或是有效的插件类
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type):
                # 检查是否继承 SiteAdapter
                if (issubclass(attr, SiteAdapter) and 
                    attr is not SiteAdapter and
                    not attr_name.startswith('_')):
                    return attr()
                # 或者检查是否是有效的插件类（有必需的方法）
                elif (hasattr(attr, 'name') and 
                      hasattr(attr, 'domains') and
                      hasattr(attr, 'can_handle') and
                      hasattr(attr, 'extract') and
                      not attr_name.startswith('_') and
                      attr_name != 'SiteAdapter'):
                    return attr()
        
        return None
    
    def get_adapter(self, url: str) -> Optional[SiteAdapter]:
        """获取可以处理该URL的适配器"""
        for adapter in self.adapters:
            try:
                if adapter.can_handle(url):
                    return adapter
            except Exception:
                continue
        return None
    
    def get_all_adapters_info(self) -> List[Dict]:
        """获取所有适配器信息"""
        return [
            {'name': a.name, 'domains': a.domains}
            for a in self.adapters
        ]
    
    def get_load_report(self) -> List[tuple]:
        """获取加载报告"""
        return self.load_results
    
    def reload(self) -> None:
        """热重载所有插件"""
        self.load_plugins()
