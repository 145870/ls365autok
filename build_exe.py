# -*- coding: utf-8 -*-
"""
打包脚本 - 将程序打包为 exe 可执行文件
使用 PyInstaller 进行打包
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在检查 PyInstaller...")
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller 安装完成")

def build_exe():
    """打包为 exe 文件"""
    print("\n开始打包程序...")
    
    # PyInstaller 打包命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 不显示控制台窗口
        "--name=湖南外国语自动学习助手",  # exe文件名
        "--icon=NONE",  # 如果有图标可以指定
        "--add-data=config.json;.",  # 包含配置文件
        "--hidden-import=selenium",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=openai",
        "--hidden-import=tkinter",
        "--hidden-import=json",
        "--clean",  # 清理临时文件
        "auto_study_gui_v2.py"  # 主程序文件
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*60)
        print("打包成功！")
        print("="*60)
        print("\n可执行文件位置:")
        print(f"  -> dist/湖南外国语自动学习助手.exe")
        print("\n注意事项:")
        print("  1. 首次运行需要在同目录下创建 config.json 配置文件")
        print("  2. 需要安装 Chrome 浏览器")
        print("  3. 程序会自动下载 ChromeDriver")
        print("  4. 建议将 config.json 和 exe 放在同一目录")
        print("\n" + "="*60)
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败: {e}")
        sys.exit(1)

def clean_build_files():
    """清理打包过程中的临时文件"""
    print("\n是否清理临时文件? (build/, __pycache__/ 等)")
    choice = input("输入 y 清理，其他键跳过: ").strip().lower()
    
    if choice == 'y':
        import shutil
        dirs_to_remove = ['build', '__pycache__']
        files_to_remove = ['湖南外国语自动学习助手.spec']
        
        for d in dirs_to_remove:
            if os.path.exists(d):
                shutil.rmtree(d)
                print(f"  已删除: {d}/")
        
        for f in files_to_remove:
            if os.path.exists(f):
                os.remove(f)
                print(f"  已删除: {f}")
        
        print("临时文件清理完成")

def main():
    print("="*60)
    print("湖南外国语自动学习助手 - EXE 打包工具")
    print("="*60)
    
    # 安装 PyInstaller
    install_pyinstaller()
    
    # 打包
    build_exe()
    
    # 清理临时文件
    clean_build_files()
    
    print("\n完成！")
    input("按回车键退出...")

if __name__ == "__main__":
    main()

