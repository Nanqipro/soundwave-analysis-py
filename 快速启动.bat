@echo off
chcp 65001 >nul
title 声学分析工具 - 快速启动
color 0B

echo.
echo 🎵 声学分析工具 v2.0 - 快速启动
echo ================================
echo.

:: 快速检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先运行"启动声学分析工具.bat"进行完整安装
    pause
    exit /b 1
)

:: 快速检查主文件
if not exist "streamlit_app.py" (
    echo ❌ 未找到主程序文件
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo 🚀 启动中...
echo.
echo 📱 浏览器将打开 http://localhost:8501
echo 🛑 按 Ctrl+C 停止服务
echo.

:: 直接启动，不检查依赖（假设已经安装过）
streamlit run streamlit_app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false

echo.
echo 👋 应用已停止
pause
