# 🎵 声学信号分析工具 v2.0 Professional

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**专业级声学信号分析平台 | 支持参数定制 | Web界面 | 批量处理**

[🚀 快速开始](#快速开始) •
[📖 使用指南](#使用指南) • 
[🔧 功能特性](#功能特性) •
[📊 应用场景](#应用场景) •
[💡 技术支持](#技术支持)

</div>

---

## 📋 项目概述

**声学信号分析工具 v2.0 Professional** 是一个功能强大的声学信号分析平台，专为声学研究、建筑声学、音频工程等专业领域设计。该工具基于现代信号处理技术，提供完整的时域、频域、相位域和时频域分析功能。

### 🎯 核心特性

- **🔧 参数定制化**：16个核心参数可实时调节
- **🎛️ 专业预设**：5种场景化配置（建筑声学、语音分析、音乐分析等）
- **📊 多维分析**：时域、频域、相位域、时频域全覆盖
- **🎯 共振峰检测**：智能识别并分析共振特性
- **🌐 Web界面**：现代化Streamlit界面，操作简单
- **⚡ 双击启动**：Windows用户无需命令行，双击即用
- **📈 专业图表**：高质量可视化输出，支持论文发表标准

## 🚀 快速开始

### Windows用户（推荐）

1. **下载项目**到Windows电脑
2. **双击 `安装向导.bat`** 进行一键安装配置
3. **双击桌面快捷方式**启动应用
4. **上传WAV文件**开始专业分析

### 命令行方式

```bash
# 克隆项目
git clone https://github.com/your-username/soundwave-analysis-py.git
cd soundwave-analysis-py

# 安装依赖
pip install -r requirements_web.txt

# 启动Web界面
python start_web.py
# 或
streamlit run streamlit_app.py
```

### 快速测试

```python
# 直接使用分析器
from wav_to_spectrum_analyzer import quick_analyze
result = quick_analyze("your_audio.wav")
```

## 🔧 功能特性

### 📊 多维度分析

| 分析维度 | 功能描述 | 应用场景 |
|---------|----------|----------|
| **时域分析** | 波形图、RMS、峰值统计 | 信号基础特征分析 |
| **频域分析** | 高精度FFT、声压级计算 | 频谱特性、共振检测 |
| **相位分析** | 频率-相位关系图 | 信号延迟、滤波效果 |
| **时频分析** | 短时傅里叶变换谱图 | 时变信号、瞬态分析 |

### 🎛️ 参数配置系统

#### 基础分析参数
- **频率分辨率**：0.001-1.0 Hz（精度控制）
- **最大分析频率**：500-20000 Hz（范围控制）
- **窗函数类型**：hann/hamming/blackman/rectangular

#### 共振峰检测参数
- **最小突出度**：1-20 dB（敏感度控制）
- **最小频率间隔**：5-100 Hz（密度控制）
- **最大峰值数**：5-50（数量限制）

#### 时频分析参数
- **STFT窗长度**：256-4096（时频分辨率平衡）
- **窗重叠比例**：0.1-0.9（平滑度控制）

### 🎯 五种专业预设

| 预设配置 | 目标应用 | 核心参数 |
|---------|----------|----------|
| **🏢 建筑声学** | 室内声学测量、建筑空间分析 | 0.01Hz分辨率、0-2000Hz、6dB阈值 |
| **🎤 语音分析** | 语音信号处理、通信系统 | 0.1Hz分辨率、0-8000Hz、hamming窗 |
| **🎵 音乐分析** | 音乐信号分析、音频工程 | 0.05Hz分辨率、0-20000Hz、blackman窗 |
| **⚡ 快速分析** | 快速预览、降低计算时间 | 0.5Hz分辨率、简化检测、关闭综合分析 |
| **🔬 高精度分析** | 研究级精度、论文发表 | 0.001Hz分辨率、50峰值、4096窗长 |

## 📊 应用场景

### 🏛️ 建筑声学研究
- **古建筑声学效应**：分析传统建筑的声学特性
- **室内声学设计**：优化音响效果和混响时间
- **声学材料测试**：评估吸声和隔声性能

### 🎭 文化遗产保护
- **古戏台声学**：研究传统戏台的扩声机制
- **音乐考古学**：分析古代音乐空间的声学智慧
- **非遗保护**：记录和分析传统音乐表演空间

### 🔊 音频工程
- **扬声器测试**：频响特性和失真分析
- **录音室设计**：声学环境优化
- **音响调试**：系统频响调整和均衡

### 🎵 音乐研究
- **乐器声学**：分析乐器的频谱特征
- **音乐律学**：研究音高与频率关系
- **演出空间**：评估音乐厅声学效果

## 🛠️ 技术架构

### 核心算法
- **FFT频谱分析**：高精度傅里叶变换，支持0.001Hz分辨率
- **智能峰值检测**：基于scipy.signal的专业共振峰识别
- **多窗函数支持**：hann、hamming、blackman、rectangular
- **自适应参数调整**：根据信号特性自动优化分析参数

### 技术栈
- **后端**：Python 3.8+、NumPy、SciPy、Matplotlib
- **前端**：Streamlit、现代化Web界面
- **音频处理**：LibROSA（可选）、SciPy.io.wavfile
- **数据分析**：Pandas、专业统计分析

### 性能特性
- **高精度分析**：频率分辨率可达0.001Hz
- **批量处理**：支持多文件自动化分析
- **内存优化**：大文件智能分块处理
- **多平台支持**：Windows、macOS、Linux全兼容

## 📁 项目结构

```
soundwave-analysis-py/
├── 📱 前端界面
│   ├── streamlit_app.py          # 主Web应用
│   ├── start_web.py              # 启动脚本
│   └── requirements_web.txt      # Web依赖
├── 🔧 分析引擎
│   ├── wav_to_spectrum_analyzer.py  # 核心分析器
│   └── shipin.py                    # MATLAB转换工具
├── 🖥️ Windows启动
│   ├── 安装向导.bat              # 一键安装配置
│   ├── 启动声学分析工具.bat      # 主启动文件
│   ├── 快速启动.bat              # 快速启动
│   └── Start-SoundAnalyzer.ps1   # PowerShell版本
├── 📊 数据目录
│   ├── data/                     # 音频文件存放
│   ├── ana_res/                  # 分析结果输出
│   └── web_results/              # Web界面结果
├── 📚 文档系统
│   ├── 参数配置指南.md           # 详细参数说明
│   ├── 新功能使用指南.md         # 功能使用指南
│   ├── Windows启动说明.md        # Windows用户指南
│   └── 项目升级总结.md           # 版本升级说明
└── 🧪 测试验证
    ├── test_*.py                 # 自动化测试脚本
    └── 测试说明.md               # 测试使用说明
```

## 📖 使用指南

### 🌐 Web界面使用

1. **启动应用**
   ```bash
   python start_web.py
   ```

2. **配置参数**
   - 打开浏览器访问 `http://localhost:8501`
   - 在左侧栏调节分析参数或选择预设配置
   - 查看实时配置预览

3. **分析音频**
   - 上传WAV音频文件（支持最大50MB）
   - 点击"🚀 开始分析"按钮
   - 查看多维度分析结果

4. **结果导出**
   - 下载完整分析报告（ZIP格式）
   - 包含所有图表和数据文件

### 💻 编程接口使用

#### 基础分析
```python
from wav_to_spectrum_analyzer import SpectrumAnalyzer

# 创建分析器
analyzer = SpectrumAnalyzer(target_freq_resolution=0.01)

# 分析WAV文件
result = analyzer.analyze_wav_file("audio.wav", max_freq=2000)

# 绘制频谱图
analyzer.plot_spectrum(result, save_path="spectrum.png")
```

#### 高级配置
```python
# 自定义参数配置
config = {
    'target_freq_resolution': 0.001,  # 高精度
    'min_prominence': 3.0,            # 敏感检测
    'window_type': 'blackman',        # 高质量窗函数
    'comprehensive_analysis': True     # 全面分析
}

# 使用配置进行分析
analyzer = SpectrumAnalyzer(**config)
result = analyzer.analyze_wav_file("audio.wav")

# 综合分析（四合一图表）
analyzer.comprehensive_analysis(result, save_prefix="detailed")
```

#### 批量处理
```python
# 批量分析目录中的所有WAV文件
results = analyzer.batch_analyze_directory(
    data_dir="data",
    max_freq=2000,
    comprehensive_analysis=True
)
```

### 🔬 研究应用示例

#### 建筑声学研究
```python
# 配置建筑声学参数
analyzer = SpectrumAnalyzer(
    target_freq_resolution=0.01,  # 适中精度
    output_dir="building_acoustics"
)

# 分析室内混响
result = analyzer.analyze_wav_file("room_response.wav", max_freq=2000)

# 检测共振频率
resonance = analyzer.detect_resonance_peaks(
    result['frequencies'], 
    result['spl_db'],
    min_prominence=6.0,    # 建筑声学标准阈值
    min_distance=10.0      # 避免谐波干扰
)

# 生成专业报告
analyzer.comprehensive_analysis(result, save_prefix="acoustic_analysis")
```

#### 音乐律学研究
```python
# 高精度音乐分析配置
analyzer = SpectrumAnalyzer(
    target_freq_resolution=0.001,  # 高精度检测音高
    output_dir="music_analysis"
)

# 分析乐器音色
result = analyzer.analyze_wav_file("instrument.wav", max_freq=4000)

# 精确识别基频和泛音
resonance = analyzer.detect_resonance_peaks(
    result['frequencies'], 
    result['spl_db'],
    min_prominence=3.0,    # 敏感检测所有泛音
    min_distance=5.0,      # 密集泛音检测
    max_peaks=50           # 检测更多泛音成分
)
```

## 🎓 学术应用

### 📄 论文发表支持
- **高质量图表**：300 DPI矢量图输出
- **专业术语**：符合国际声学标准
- **数据导出**：CSV格式便于后续分析
- **方法重现**：完整参数记录确保可重复性

### 🔬 研究案例
本工具已成功应用于多项学术研究：

- **古戏台声学效应研究**：平遥超山庙、真武庙古戏台声学分析
- **传统建筑声学智慧**：古代建筑空间的声学设计原理
- **音乐律学对比研究**：共振频率与十二平均律的定量分析
- **声学增益效果量化**：建筑结构对声音传播的影响评估

### 📊 数据处理流程
1. **原始数据采集**：专业设备录制WAV格式音频
2. **信号预处理**：去噪、归一化、窗函数处理
3. **频域变换**：高精度FFT分析，提取频谱特征
4. **特征识别**：智能共振峰检测和参数提取
5. **关联分析**：与音乐理论、建筑声学原理对比
6. **结果可视化**：生成专业级图表和分析报告

## 💡 技术支持

### 🐛 常见问题

<details>
<summary><strong>Q: Windows下双击启动失败？</strong></summary>

**A: 解决方案**
1. 确保已安装Python 3.8+并勾选"Add to PATH"
2. 运行`安装向导.bat`进行环境检查
3. 检查是否有防火墙阻止8501端口
4. 尝试使用`快速启动.bat`
</details>

<details>
<summary><strong>Q: 分析结果不准确？</strong></summary>

**A: 优化建议**
1. 检查音频文件质量（采样率≥44.1kHz）
2. 调整频率分辨率参数（更小值=更高精度）
3. 选择合适的窗函数（blackman用于高精度）
4. 调节共振峰检测阈值
</details>

<details>
<summary><strong>Q: 大文件处理缓慢？</strong></summary>

**A: 性能优化**
1. 使用"快速分析"预设配置
2. 适当降低频率分辨率
3. 关闭综合分析功能
4. 限制最大分析频率范围
</details>

### 📞 获取帮助

- **📚 查看文档**：`参数配置指南.md`、`新功能使用指南.md`
- **🧪 运行测试**：验证功能是否正常工作
- **💬 问题反馈**：提交Issue或联系开发团队
- **🔧 技术交流**：参与声学信号处理技术讨论

### 🚀 版本更新

**v2.0 Professional 主要更新**：
- ✅ 新增16个可调节参数
- ✅ 5种专业预设配置
- ✅ Windows双击启动支持
- ✅ 实时参数配置界面
- ✅ 完整测试验证体系
- ✅ 专业级文档系统

## 🤝 贡献指南

我们欢迎社区贡献！如果您想参与项目开发：

1. **Fork** 本项目
2. **创建** 功能分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **打开** Pull Request

### 🎯 贡献方向
- 🔧 新增分析算法
- 🎨 界面优化改进
- 📚 文档完善翻译
- 🧪 测试用例补充
- 🐛 Bug修复报告

## 📜 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目和研究工作的支持：
- **NumPy & SciPy**：科学计算基础
- **Matplotlib**：专业图表绘制
- **Streamlit**：现代Web界面框架
- **古戏台声学研究**：提供理论基础和验证案例

---

<div align="center">

**🎵 专业级声学分析，从这里开始！**

[⬆️ 回到顶部](#-声学信号分析工具-v20-professional)

</div>
