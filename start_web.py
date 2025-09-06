#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声学分析Web界面启动脚本
=====================

快速启动Streamlit Web界面的便捷脚本

作者：nanqipro
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = [
        'streamlit',
        'numpy', 
        'matplotlib',
        'scipy',
        'pandas',
        'Pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower())
        except ImportError:
            if package == 'Pillow':
                try:
                    __import__('PIL')
                except ImportError:
                    missing_packages.append(package)
            else:
                missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """安装缺失的依赖包"""
    print("🔧 正在安装缺失的依赖包...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"
        ])
        print("✅ 依赖包安装完成!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装依赖包失败: {e}")
        return False

def start_streamlit():
    """启动Streamlit应用"""
    print("🚀 正在启动声学分析Web界面...")
    print("📱 界面将在浏览器中自动打开")
    print("🛑 按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 启动Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎵 声学信号分析Web界面启动器")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = Path.cwd()
    streamlit_app = current_dir / "streamlit_app.py"
    wav_analyzer = current_dir / "wav_to_spectrum_analyzer.py"
    requirements_file = current_dir / "requirements_web.txt"
    
    if not streamlit_app.exists():
        print(f"❌ 未找到 streamlit_app.py 文件")
        print(f"   请确保在正确的目录中运行此脚本")
        return
    
    if not wav_analyzer.exists():
        print(f"❌ 未找到 wav_to_spectrum_analyzer.py 文件")
        print(f"   请确保分析模块文件存在")
        return
    
    print("✅ 核心文件检查完成")
    
    # 检查依赖
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"⚠️  检测到缺失的依赖包: {', '.join(missing_deps)}")
        
        if requirements_file.exists():
            response = input("是否自动安装依赖包? (y/n): ").lower().strip()
            if response in ['y', 'yes', '是']:
                if not install_dependencies():
                    print("❌ 依赖安装失败，请手动安装")
                    return
            else:
                print("💡 请手动安装依赖包:")
                print(f"   pip install -r requirements_web.txt")
                return
        else:
            print("💡 请手动安装依赖包:")
            for pkg in missing_deps:
                print(f"   pip install {pkg}")
            return
    else:
        print("✅ 依赖包检查完成")
    
    # 启动Web界面
    start_streamlit()

if __name__ == "__main__":
    main()
