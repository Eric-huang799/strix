"""
Strix 打包脚本
使用 PyInstaller 生成带图标的独立可执行文件
"""

import subprocess
import sys
from pathlib import Path


def build():
    """打包 Strix 为可执行文件"""
    
    # 确保资源目录存在
    resources_dir = Path("resources")
    icon_file = resources_dir / "strix.ico"
    
    if not icon_file.exists():
        print("错误: 找不到图标文件 resources/strix.ico")
        print("请将图标文件放入 resources/ 目录后再打包")
        return False
    
    # PyInstaller 参数
    args = [
        "pyinstaller",
        "--name=Strix",                    # 程序名称
        "--windowed",                       # GUI 模式（无控制台）
        "--onefile",                        # 打包成单个文件
        f"--icon={icon_file}",             # 程序图标
        "--add-data=resources;resources",   # 包含资源文件
        "--add-data=plugins;plugins",       # 包含插件目录
        "--clean",                          # 清理临时文件
        "--noconfirm",                      # 不确认覆盖
        "strix.py",                         # 入口文件
    ]
    
    print("开始打包 Strix...")
    print(f"命令: {' '.join(args)}")
    print()
    
    try:
        result = subprocess.run(args, check=True)
        print()
        print("✅ 打包成功!")
        print("输出文件: dist/Strix.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 找不到 pyinstaller，请先安装:")
        print("   pip install pyinstaller")
        return False


def build_directory():
    """打包为文件夹模式（启动更快，文件更小）"""
    
    resources_dir = Path("resources")
    icon_file = resources_dir / "strix.ico"
    
    if not icon_file.exists():
        print("错误: 找不到图标文件 resources/strix.ico")
        return False
    
    args = [
        "pyinstaller",
        "--name=Strix",
        "--windowed",
        # 不使用 --onefile，生成文件夹
        f"--icon={icon_file}",
        "--add-data=resources;resources",
        "--add-data=plugins;plugins",
        "--clean",
        "--noconfirm",
        "strix.py",
    ]
    
    print("开始打包 Strix (文件夹模式)...")
    print(f"命令: {' '.join(args)}")
    print()
    
    try:
        subprocess.run(args, check=True)
        print()
        print("✅ 打包成功!")
        print("输出目录: dist/Strix/")
        print("运行方式: 双击 dist/Strix/Strix.exe")
        return True
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Strix 打包工具")
    parser.add_argument(
        "--dir", "-d",
        action="store_true",
        help="打包为文件夹模式（启动更快）"
    )
    
    args = parser.parse_args()
    
    if args.dir:
        build_directory()
    else:
        build()
