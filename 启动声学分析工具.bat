@echo off
chcp 65001 >nul
title 声学分析工具 v2.0 Professional
color 0A

echo.
echo ====================================================
echo           🎵 声学分析工具 v2.0 Professional
echo ====================================================
echo.
echo 🚀 正在启动专业版声学分析工具...
echo 💡 支持参数定制、预设配置、实时调节
echo.

:: 检查是否在正确的目录
if not exist "streamlit_app.py" (
    echo ❌ 错误：未找到 streamlit_app.py 文件
    echo 💡 请确保将此批处理文件放在项目根目录中
    echo    项目根目录应包含以下文件：
    echo    - streamlit_app.py
    echo    - wav_to_spectrum_analyzer.py
    echo    - requirements_web.txt
    pause
    exit /b 1
)

:: 检查Python是否安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到Python
    echo.
    echo 💡 请先安装Python 3.8或更高版本：
    echo    1. 访问 https://www.python.org/downloads/
    echo    2. 下载并安装最新版本的Python
    echo    3. 安装时确保勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python环境检查通过
)

:: 检查pip是否可用
echo 🔍 检查pip包管理器...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：pip不可用
    echo 💡 请重新安装Python并确保包含pip
    pause
    exit /b 1
) else (
    echo ✅ pip检查通过
)

:: 检查依赖文件是否存在
if not exist "requirements_web.txt" (
    echo ⚠️  警告：未找到 requirements_web.txt 文件
    echo 💡 将尝试安装基础依赖包...
    
    echo 📦 安装基础依赖包...
    pip install streamlit numpy matplotlib scipy pandas Pillow
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo 📦 检查并安装依赖包...
    pip install -r requirements_web.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败，尝试单独安装关键包...
        pip install streamlit numpy matplotlib scipy pandas Pillow
        if errorlevel 1 (
            echo ❌ 依赖安装失败
            pause
            exit /b 1
        )
    )
)

echo ✅ 依赖包安装完成

:: 检查核心文件
echo 🔍 检查核心文件...
if not exist "wav_to_spectrum_analyzer.py" (
    echo ❌ 错误：未找到 wav_to_spectrum_analyzer.py 文件
    pause
    exit /b 1
)
echo ✅ 核心文件检查通过

:: 创建data目录（如果不存在）
if not exist "data" (
    echo 📁 创建数据目录...
    mkdir data
    echo ✅ 数据目录已创建：data\
    echo 💡 您可以将WAV音频文件放入此目录进行分析
)

:: 启动应用
echo.
echo 🚀 启动声学分析工具...
echo 📱 浏览器将自动打开 http://localhost:8501
echo 🎛️  请在左侧面板调节分析参数
echo 🛑 按 Ctrl+C 停止服务
echo.
echo ====================================================
echo           ✨ 新功能特性 ✨
echo ====================================================
echo 🔧 参数定制：16个核心参数可调节
echo 🎛️  预设配置：5种专业场景配置
echo 📊 实时调节：参数变化立即生效
echo 🏢 建筑声学：专门优化的分析配置
echo 🎤 语音分析：语音信号专用设置
echo 🎵 音乐分析：音频工程级别配置
echo ⚡ 快速分析：降低计算时间配置
echo 🔬 高精度：研究级精度分析配置
echo ====================================================
echo.

:: 启动Streamlit应用
streamlit run streamlit_app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false
if errorlevel 1 (
    echo.
    echo ❌ 应用启动失败
    echo 💡 可能的解决方案：
    echo    1. 检查是否有其他程序占用8501端口
    echo    2. 尝试重新安装streamlit：pip install --upgrade streamlit
    echo    3. 检查防火墙设置
    echo.
    pause
    exit /b 1
)

echo.
echo 👋 应用已停止运行
pause
