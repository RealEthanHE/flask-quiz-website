#!/usr/bin/env python3
"""
启动应用程序的简单脚本
"""
import subprocess
import sys
import time
import webbrowser
from threading import Timer

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')
    print("🌐 浏览器已打开: http://localhost:5000")

def start_app():
    """启动Flask应用"""
    print("🚀 启动Quiz应用...")
    print("📝 错题本功能已集成")
    print("🔗 访问地址: http://localhost:5000")
    print("📖 错题本地址: http://localhost:5000/wrong_answers")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 延迟打开浏览器
    Timer(2.0, open_browser).start()
    
    # 启动Flask应用
    try:
        subprocess.run([sys.executable, "main_new.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    start_app()
