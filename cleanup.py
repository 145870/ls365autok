# -*- coding: utf-8 -*-
import shutil
import os
import subprocess
import sys

if __name__ == '__main__':
    try:
        os.chdir(r'C:\Users\ys\Desktop\湖南外国语自动课程脚本')
        
        print("Deleting directories...")
        for d in ['湖南外国语自动刷课', 'dist', 'build']:
            if os.path.exists(d):
                shutil.rmtree(d)
                print(f"  Deleted: {d}")
        
        print("\nDeleting spec file...")
        if os.path.exists('湖南外国语自动学习助手.spec'):
            os.remove('湖南外国语自动学习助手.spec')
            print("  Deleted: spec file")
        
        print("\nCreating new Git history without large files...")
        
        # 备份当前分支
        print("  Backing up current branch...")
        subprocess.run(['git', 'branch', 'backup-old'], check=False, shell=False)
        
        # 创建新的孤立分支
        print("  Creating orphan branch...")
        subprocess.run(['git', 'checkout', '--orphan', 'new-main'], check=True, shell=False)
        
        # 添加所有文件（.gitignore会排除exe）
        print("  Adding all files...")
        subprocess.run(['git', 'add', '-A'], check=True, shell=False)
        
        # 创建第一个提交
        print("  Creating initial commit...")
        subprocess.run(['git', 'commit', '-m', 'Initial commit: 湖南外国语自动学习助手 v2.0'], check=True, shell=False)
        
        # 删除旧的main分支
        print("  Deleting old main branch...")
        subprocess.run(['git', 'branch', '-D', 'main'], check=True, shell=False)
        
        # 重命名新分支为main
        print("  Renaming branch to main...")
        subprocess.run(['git', 'branch', '-m', 'main'], check=True, shell=False)
        
        # 强制推送
        print("\nPushing to GitHub...")
        result = subprocess.run(['git', 'push', '-f', 'origin', 'main'], 
                              capture_output=True, 
                              text=True, 
                              shell=False,
                              encoding='utf-8',
                              errors='ignore')
        print(result.stdout)
        if result.returncode != 0:
            print("Error:", result.stderr)
            sys.exit(1)
        
        print("\nDone! Git history has been completely rewritten.")
        print("Old history is backed up in 'backup-old' branch.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

