# 声学分析工具 v2.0 Professional PowerShell启动脚本
# =====================================================

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "声学分析工具 v2.0 Professional"

# 颜色定义
$SuccessColor = "Green"
$ErrorColor = "Red"
$WarningColor = "Yellow"
$InfoColor = "Cyan"
$TitleColor = "Magenta"

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [switch]$NoNewline
    )
    
    if ($NoNewline) {
        Write-Host $Message -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Show-Header {
    Clear-Host
    Write-ColoredOutput "====================================================" $TitleColor
    Write-ColoredOutput "          🎵 声学分析工具 v2.0 Professional" $TitleColor
    Write-ColoredOutput "====================================================" $TitleColor
    Write-ColoredOutput ""
    Write-ColoredOutput "🚀 正在启动专业版声学分析工具..." $InfoColor
    Write-ColoredOutput "💡 支持参数定制、预设配置、实时调节" $InfoColor
    Write-ColoredOutput ""
}

function Test-FileExists {
    param([string]$FilePath, [string]$Description)
    
    if (Test-Path $FilePath) {
        Write-ColoredOutput "✅ $Description 检查通过" $SuccessColor
        return $true
    } else {
        Write-ColoredOutput "❌ 错误：未找到 $FilePath" $ErrorColor
        return $false
    }
}

function Test-Command {
    param([string]$Command, [string]$Description)
    
    try {
        $null = Get-Command $Command -ErrorAction Stop
        Write-ColoredOutput "✅ $Description 检查通过" $SuccessColor
        return $true
    } catch {
        Write-ColoredOutput "❌ 错误：$Description 不可用" $ErrorColor
        return $false
    }
}

function Install-Dependencies {
    Write-ColoredOutput "📦 检查并安装依赖包..." $InfoColor
    
    if (Test-Path "requirements_web.txt") {
        try {
            $process = Start-Process -FilePath "pip" -ArgumentList "install", "-r", "requirements_web.txt" -Wait -PassThru -NoNewWindow
            if ($process.ExitCode -eq 0) {
                Write-ColoredOutput "✅ 依赖包安装完成" $SuccessColor
                return $true
            } else {
                throw "pip install 返回错误代码: $($process.ExitCode)"
            }
        } catch {
            Write-ColoredOutput "⚠️  requirements_web.txt 安装失败，尝试安装基础包..." $WarningColor
            return Install-BasicDependencies
        }
    } else {
        Write-ColoredOutput "⚠️  未找到 requirements_web.txt，安装基础依赖包..." $WarningColor
        return Install-BasicDependencies
    }
}

function Install-BasicDependencies {
    $packages = @("streamlit", "numpy", "matplotlib", "scipy", "pandas", "Pillow")
    
    foreach ($package in $packages) {
        try {
            Write-ColoredOutput "   安装 $package..." $InfoColor
            $process = Start-Process -FilePath "pip" -ArgumentList "install", $package -Wait -PassThru -NoNewWindow
            if ($process.ExitCode -ne 0) {
                throw "安装 $package 失败"
            }
        } catch {
            Write-ColoredOutput "❌ 安装 $package 失败: $_" $ErrorColor
            return $false
        }
    }
    
    Write-ColoredOutput "✅ 基础依赖包安装完成" $SuccessColor
    return $true
}

function Start-Application {
    Write-ColoredOutput ""
    Write-ColoredOutput "🚀 启动声学分析工具..." $InfoColor
    Write-ColoredOutput "📱 浏览器将自动打开 http://localhost:8501" $InfoColor
    Write-ColoredOutput "🎛️  请在左侧面板调节分析参数" $InfoColor
    Write-ColoredOutput "🛑 按 Ctrl+C 停止服务" $InfoColor
    Write-ColoredOutput ""
    Write-ColoredOutput "====================================================" $TitleColor
    Write-ColoredOutput "                  ✨ 新功能特性 ✨" $TitleColor
    Write-ColoredOutput "====================================================" $TitleColor
    Write-ColoredOutput "🔧 参数定制：16个核心参数可调节" $InfoColor
    Write-ColoredOutput "🎛️  预设配置：5种专业场景配置" $InfoColor
    Write-ColoredOutput "📊 实时调节：参数变化立即生效" $InfoColor
    Write-ColoredOutput "🏢 建筑声学：专门优化的分析配置" $InfoColor
    Write-ColoredOutput "🎤 语音分析：语音信号专用设置" $InfoColor
    Write-ColoredOutput "🎵 音乐分析：音频工程级别配置" $InfoColor
    Write-ColoredOutput "⚡ 快速分析：降低计算时间配置" $InfoColor
    Write-ColoredOutput "🔬 高精度：研究级精度分析配置" $InfoColor
    Write-ColoredOutput "====================================================" $TitleColor
    Write-ColoredOutput ""
    
    try {
        # 启动Streamlit应用
        & streamlit run streamlit_app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false
    } catch {
        Write-ColoredOutput ""
        Write-ColoredOutput "❌ 应用启动失败: $_" $ErrorColor
        Write-ColoredOutput "💡 可能的解决方案：" $WarningColor
        Write-ColoredOutput "   1. 检查是否有其他程序占用8501端口" $WarningColor
        Write-ColoredOutput "   2. 尝试重新安装streamlit：pip install --upgrade streamlit" $WarningColor
        Write-ColoredOutput "   3. 检查防火墙设置" $WarningColor
        Write-ColoredOutput ""
        Read-Host "按回车键退出"
        exit 1
    }
}

function Show-ErrorAndExit {
    param([string]$ErrorMessage)
    
    Write-ColoredOutput ""
    Write-ColoredOutput $ErrorMessage $ErrorColor
    Write-ColoredOutput ""
    Read-Host "按回车键退出"
    exit 1
}

# 主执行流程
try {
    # 显示标题
    Show-Header
    
    # 检查是否在正确的目录
    if (-not (Test-FileExists "streamlit_app.py" "主应用文件")) {
        Show-ErrorAndExit "💡 请确保将此脚本放在项目根目录中`n   项目根目录应包含以下文件：`n   - streamlit_app.py`n   - wav_to_spectrum_analyzer.py`n   - requirements_web.txt"
    }
    
    # 检查Python环境
    Write-ColoredOutput "🔍 检查Python环境..." $InfoColor
    if (-not (Test-Command "python" "Python")) {
        Show-ErrorAndExit "💡 请先安装Python 3.8或更高版本：`n   1. 访问 https://www.python.org/downloads/`n   2. 下载并安装最新版本的Python`n   3. 安装时确保勾选 'Add Python to PATH'"
    }
    
    # 检查pip
    Write-ColoredOutput "🔍 检查pip包管理器..." $InfoColor
    if (-not (Test-Command "pip" "pip包管理器")) {
        Show-ErrorAndExit "💡 请重新安装Python并确保包含pip"
    }
    
    # 检查核心文件
    Write-ColoredOutput "🔍 检查核心文件..." $InfoColor
    if (-not (Test-FileExists "wav_to_spectrum_analyzer.py" "分析器模块")) {
        Show-ErrorAndExit "请确保 wav_to_spectrum_analyzer.py 文件存在"
    }
    
    # 创建data目录
    if (-not (Test-Path "data")) {
        Write-ColoredOutput "📁 创建数据目录..." $InfoColor
        New-Item -ItemType Directory -Path "data" | Out-Null
        Write-ColoredOutput "✅ 数据目录已创建：data\" $SuccessColor
        Write-ColoredOutput "💡 您可以将WAV音频文件放入此目录进行分析" $InfoColor
    }
    
    # 安装依赖
    if (-not (Install-Dependencies)) {
        Show-ErrorAndExit "依赖包安装失败，请检查网络连接和Python环境"
    }
    
    # 启动应用
    Start-Application
    
    # 应用停止后的清理
    Write-ColoredOutput ""
    Write-ColoredOutput "👋 应用已停止运行" $InfoColor
    Read-Host "按回车键退出"
    
} catch {
    Write-ColoredOutput ""
    Write-ColoredOutput "❌ 发生未预期的错误: $_" $ErrorColor
    Write-ColoredOutput ""
    Read-Host "按回车键退出"
    exit 1
}
