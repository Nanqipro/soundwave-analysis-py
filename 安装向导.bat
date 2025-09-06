@echo off
chcp 65001 >nul
title 声学分析工具安装向导
color 0E

:MENU
cls
echo.
echo ====================================================
echo           🎵 声学分析工具安装向导 v2.0
echo ====================================================
echo.
echo 请选择操作：
echo.
echo [1] 💻 检查系统环境
echo [2] 📦 安装Python和依赖
echo [3] 🚀 首次启动设置
echo [4] 🔗 创建桌面快捷方式
echo [5] 📁 创建示例数据文件夹
echo [6] ❌ 退出
echo.
set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" goto CHECK_ENV
if "%choice%"=="2" goto INSTALL_DEPS
if "%choice%"=="3" goto FIRST_RUN
if "%choice%"=="4" goto CREATE_SHORTCUT
if "%choice%"=="5" goto CREATE_FOLDERS
if "%choice%"=="6" goto EXIT
goto MENU

:CHECK_ENV
cls
echo.
echo 🔍 系统环境检查
echo ==================
echo.

:: 检查Windows版本
echo 📋 Windows版本信息：
ver
echo.

:: 检查Python
echo 🐍 检查Python环境：
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python未安装
    echo.
    echo 💡 请访问 https://www.python.org/downloads/ 下载安装Python
    echo    安装时请确保勾选 "Add Python to PATH"
) else (
    echo ✅ Python已安装
    python -c "import sys; print(f'   Python路径: {sys.executable}')"
)
echo.

:: 检查pip
echo 📦 检查pip包管理器：
pip --version 2>nul
if errorlevel 1 (
    echo ❌ pip不可用
) else (
    echo ✅ pip可用
)
echo.

:: 检查项目文件
echo 📁 检查项目文件：
if exist "streamlit_app.py" (
    echo ✅ streamlit_app.py 存在
) else (
    echo ❌ streamlit_app.py 不存在
)

if exist "wav_to_spectrum_analyzer.py" (
    echo ✅ wav_to_spectrum_analyzer.py 存在
) else (
    echo ❌ wav_to_spectrum_analyzer.py 不存在
)

if exist "requirements_web.txt" (
    echo ✅ requirements_web.txt 存在
) else (
    echo ❌ requirements_web.txt 不存在
)
echo.

pause
goto MENU

:INSTALL_DEPS
cls
echo.
echo 📦 安装Python依赖包
echo =====================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Python未安装
    echo 请先安装Python后再运行此选项
    pause
    goto MENU
)

echo ✅ Python环境正常
echo.
echo 📦 正在安装依赖包...
echo.

if exist "requirements_web.txt" (
    echo 📋 使用 requirements_web.txt 安装...
    pip install -r requirements_web.txt
) else (
    echo 📋 安装基础依赖包...
    pip install streamlit numpy matplotlib scipy pandas Pillow
)

echo.
if errorlevel 1 (
    echo ❌ 安装过程中出现错误
    echo 💡 请检查网络连接，然后重试
) else (
    echo ✅ 依赖包安装完成！
)
echo.

pause
goto MENU

:FIRST_RUN
cls
echo.
echo 🚀 首次启动设置
echo =================
echo.

:: 检查环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先选择选项2安装依赖
    pause
    goto MENU
)

if not exist "streamlit_app.py" (
    echo ❌ 主程序文件不存在
    pause
    goto MENU
)

echo ✅ 环境检查通过
echo.

:: 创建必要的目录
echo 📁 创建必要目录...
if not exist "data" mkdir data
if not exist "web_results" mkdir web_results
if not exist "ana_res" mkdir ana_res
echo ✅ 目录创建完成
echo.

:: 测试启动
echo 🧪 测试应用启动...
echo 📱 将打开浏览器窗口，测试成功后请关闭应用返回
echo.
timeout /t 3 >nul

streamlit run streamlit_app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false

echo.
echo 🎉 首次启动设置完成！
echo 💡 您现在可以使用"快速启动.bat"来启动应用
echo.

pause
goto MENU

:CREATE_SHORTCUT
cls
echo.
echo 🔗 创建桌面快捷方式
echo ====================
echo.

:: 创建VBS脚本来生成快捷方式
echo Set WshShell = WScript.CreateObject("WScript.Shell"^) > temp_shortcut.vbs
echo DesktopPath = WshShell.SpecialFolders("Desktop"^) >> temp_shortcut.vbs
echo Set oShellLink = WshShell.CreateShortcut(DesktopPath ^& "\声学分析工具 v2.0.lnk"^) >> temp_shortcut.vbs
echo oShellLink.TargetPath = "%~dp0启动声学分析工具.bat" >> temp_shortcut.vbs
echo oShellLink.WorkingDirectory = "%~dp0" >> temp_shortcut.vbs
echo oShellLink.Description = "声学分析工具 v2.0 Professional - 专业声学信号分析平台" >> temp_shortcut.vbs
echo oShellLink.Save >> temp_shortcut.vbs

:: 执行VBS脚本
cscript //nologo temp_shortcut.vbs

:: 删除临时文件
del temp_shortcut.vbs

echo ✅ 桌面快捷方式已创建
echo 💡 您现在可以双击桌面的"声学分析工具 v2.0"图标启动应用
echo.

:: 创建快速启动的快捷方式
echo Set WshShell = WScript.CreateObject("WScript.Shell"^) > temp_shortcut2.vbs
echo DesktopPath = WshShell.SpecialFolders("Desktop"^) >> temp_shortcut2.vbs
echo Set oShellLink = WshShell.CreateShortcut(DesktopPath ^& "\声学分析工具-快速启动.lnk"^) >> temp_shortcut2.vbs
echo oShellLink.TargetPath = "%~dp0快速启动.bat" >> temp_shortcut2.vbs
echo oShellLink.WorkingDirectory = "%~dp0" >> temp_shortcut2.vbs
echo oShellLink.Description = "声学分析工具快速启动（跳过环境检查）" >> temp_shortcut2.vbs
echo oShellLink.Save >> temp_shortcut2.vbs

cscript //nologo temp_shortcut2.vbs
del temp_shortcut2.vbs

echo ✅ 快速启动快捷方式也已创建
echo.

pause
goto MENU

:CREATE_FOLDERS
cls
echo.
echo 📁 创建示例数据文件夹
echo ======================
echo.

:: 创建完整的目录结构
echo 📁 创建目录结构...

if not exist "data" mkdir data
if not exist "data\examples" mkdir data\examples
if not exist "data\building_acoustics" mkdir data\building_acoustics
if not exist "data\speech_analysis" mkdir data\speech_analysis
if not exist "data\music_analysis" mkdir data\music_analysis
if not exist "web_results" mkdir web_results
if not exist "ana_res" mkdir ana_res

echo ✅ 目录创建完成
echo.

:: 创建说明文件
echo 📝 创建说明文件...

echo 声学分析工具数据目录说明 > data\README.txt
echo ========================== >> data\README.txt
echo. >> data\README.txt
echo 此目录用于存放WAV音频文件进行分析 >> data\README.txt
echo. >> data\README.txt
echo 目录结构： >> data\README.txt
echo - examples\        : 示例音频文件 >> data\README.txt
echo - building_acoustics\ : 建筑声学相关音频 >> data\README.txt
echo - speech_analysis\    : 语音分析相关音频 >> data\README.txt
echo - music_analysis\     : 音乐分析相关音频 >> data\README.txt
echo. >> data\README.txt
echo 支持的文件格式：WAV >> data\README.txt
echo 建议文件大小：小于50MB >> data\README.txt
echo. >> data\README.txt
echo 使用方法： >> data\README.txt
echo 1. 将WAV文件放入相应目录 >> data\README.txt
echo 2. 启动声学分析工具 >> data\README.txt
echo 3. 在界面中上传文件进行分析 >> data\README.txt

echo 建筑声学音频文件存放目录 > data\building_acoustics\README.txt
echo. >> data\building_acoustics\README.txt
echo 适用于：室内声学测量、建筑空间分析 >> data\building_acoustics\README.txt
echo 推荐设置：使用"建筑声学"预设配置 >> data\building_acoustics\README.txt

echo 语音分析音频文件存放目录 > data\speech_analysis\README.txt
echo. >> data\speech_analysis\README.txt
echo 适用于：语音信号处理、通信系统 >> data\speech_analysis\README.txt
echo 推荐设置：使用"语音分析"预设配置 >> data\speech_analysis\README.txt

echo 音乐分析音频文件存放目录 > data\music_analysis\README.txt
echo. >> data\music_analysis\README.txt
echo 适用于：音乐信号分析、音频工程 >> data\music_analysis\README.txt
echo 推荐设置：使用"音乐分析"预设配置 >> data\music_analysis\README.txt

echo ✅ 说明文件创建完成
echo.
echo 📁 已创建以下目录结构：
echo    data\
echo    ├── examples\
echo    ├── building_acoustics\
echo    ├── speech_analysis\
echo    └── music_analysis\
echo.
echo 💡 您可以将相应类型的WAV文件放入对应目录中
echo.

pause
goto MENU

:EXIT
cls
echo.
echo 👋 感谢使用声学分析工具安装向导
echo.
echo 🎉 安装向导已完成，您现在可以：
echo.
echo 1. 📱 双击"启动声学分析工具.bat"完整启动
echo 2. ⚡ 双击"快速启动.bat"快速启动
echo 3. 🔗 使用桌面快捷方式启动
echo 4. 📁 将WAV文件放入data目录进行分析
echo.
echo 💡 如需帮助，请查看项目中的说明文档
echo.
pause
exit
