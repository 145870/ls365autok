@echo off
chcp 65001 >nul
echo ====================================
echo 湖南外国语自动学习助手 - 快速打包
echo ====================================
echo.

echo [1/3] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未安装 Python 或 Python 不在系统 PATH 中
    pause
    exit /b 1
)
echo.

echo [2/3] 开始打包...
python build_exe.py
if errorlevel 1 (
    echo 错误: 打包失败
    pause
    exit /b 1
)
echo.

echo [3/3] 打包完成！
echo.
echo 生成的文件位置:
echo   dist\湖南外国语自动学习助手.exe
echo.
echo 建议分发的文件:
echo   1. 湖南外国语自动学习助手.exe
echo   2. config.json (可选)
echo   3. 使用说明.txt
echo.
pause

