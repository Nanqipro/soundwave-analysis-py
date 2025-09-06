#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声学信号分析工具
================

专业版声学信号分析工具 - 支持参数定制的WAV音频文件分析

作者：nanqipro
"""

import streamlit as st
import os
import zipfile
from pathlib import Path
import pandas as pd
from PIL import Image
from datetime import datetime
import numpy as np

# 添加当前目录到Python路径
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from wav_to_spectrum_analyzer import (
        SpectrumAnalyzer, 
        analyze_single_wav_file
    )
except ImportError as e:
    st.error(f"无法导入分析模块: {e}")
    st.info("请确保wav_to_spectrum_analyzer.py文件在当前目录中")

# 页面配置
st.set_page_config(
    page_title="声学信号分析工具",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def configure_analysis_parameters():
    """
    配置分析参数界面
    
    Returns
    -------
    dict
        分析参数配置字典
    """
    
    st.sidebar.header("🔧 分析参数配置")
    
    # 参数配置标签页
    with st.sidebar.expander("📊 基础分析参数", expanded=True):
        # 频率分辨率
        target_freq_resolution = st.slider(
            "频率分辨率 (Hz)",
            min_value=0.001,
            max_value=1.0,
            value=0.01,
            step=0.001,
            format="%.3f",
            help="更小的值提供更高的频率精度，但计算时间更长"
        )
        
        # 最大分析频率
        max_freq = st.slider(
            "最大分析频率 (Hz)",
            min_value=500,
            max_value=20000,
            value=2000,
            step=100,
            help="限制分析的频率范围，建筑声学通常使用500-2000Hz"
        )
        
        # 窗函数类型
        window_type = st.selectbox(
            "窗函数类型",
            options=['hann', 'hamming', 'blackman', 'rectangular'],
            index=0,
            help="不同窗函数影响频谱分析的精度和旁瓣抑制"
        )
    
    with st.sidebar.expander("🎯 共振峰检测参数", expanded=True):
        # 最小突出度
        min_prominence = st.slider(
            "最小突出度 (dB)",
            min_value=1.0,
            max_value=20.0,
            value=6.0,
            step=0.5,
            help="峰值必须比周围至少突出的dB数"
        )
        
        # 最小频率间隔
        min_distance = st.slider(
            "最小频率间隔 (Hz)",
            min_value=5.0,
            max_value=100.0,
            value=10.0,
            step=1.0,
            help="相邻峰值之间的最小频率距离"
        )
        
        # 最大峰值数量
        max_peaks = st.slider(
            "最大检测峰值数",
            min_value=5,
            max_value=50,
            value=20,
            step=1,
            help="限制检测的峰值数量，避免过多噪声峰值"
        )
        
        # 是否设置最小高度阈值
        use_min_height = st.checkbox("设置最小高度阈值", value=False)
        min_height = None
        if use_min_height:
            min_height = st.slider(
                "最小高度 (dB SPL)",
                min_value=0.0,
                max_value=100.0,
                value=40.0,
                step=1.0,
                help="峰值的绝对最小高度阈值"
            )
    
    with st.sidebar.expander("📈 时频分析参数", expanded=False):
        # 时频分析窗长度
        use_custom_window = st.checkbox("自定义STFT窗长度", value=False)
        window_length = None
        if use_custom_window:
            window_length = st.slider(
                "STFT窗长度",
                min_value=256,
                max_value=4096,
                value=1024,
                step=256,
                help="更大的窗提供更好的频率分辨率，更小的窗提供更好的时间分辨率"
            )
        
        # 窗重叠比例
        overlap_ratio = st.slider(
            "窗重叠比例",
            min_value=0.1,
            max_value=0.9,
            value=0.75,
            step=0.05,
            format="%.2f",
            help="重叠比例越大，时频图越平滑"
        )
    
    with st.sidebar.expander("🖼️ 显示控制参数", expanded=False):
        # 时域显示时长
        time_range = st.slider(
            "时域显示时长 (秒)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="综合分析中时域图显示的最大时长"
        )
        
        # 是否进行综合分析
        comprehensive_analysis = st.checkbox(
            "启用综合分析",
            value=True,
            help="生成包含时域、频域、相位域和时频域的四合一分析图"
        )
        
        # 频率显示范围
        freq_range_mode = st.radio(
            "频率显示范围",
            options=["自动", "自定义"],
            index=0
        )
        
        freq_range = None
        if freq_range_mode == "自定义":
            col1, col2 = st.columns(2)
            with col1:
                freq_min = st.number_input("最小频率 (Hz)", min_value=0, value=0, step=10)
            with col2:
                freq_max = st.number_input("最大频率 (Hz)", min_value=100, value=max_freq, step=10)
            freq_range = (freq_min, freq_max)
    
    # 预设配置
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ 预设配置")
    
    preset = st.sidebar.selectbox(
        "选择预设配置",
        options=["自定义", "建筑声学", "语音分析", "音乐分析", "快速分析", "高精度分析"],
        index=0
    )
    
    # 应用预设配置
    config = apply_preset_configuration(preset, {
        'target_freq_resolution': target_freq_resolution,
        'max_freq': max_freq,
        'window_type': window_type,
        'min_prominence': min_prominence,
        'min_distance': min_distance,
        'max_peaks': max_peaks,
        'min_height': min_height,
        'window_length': window_length,
        'overlap_ratio': overlap_ratio,
        'time_range': time_range,
        'comprehensive_analysis': comprehensive_analysis,
        'freq_range': freq_range
    })
    
    # 显示当前配置摘要
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 当前配置")
    st.sidebar.write(f"频率分辨率: {config['target_freq_resolution']:.3f} Hz")
    st.sidebar.write(f"分析范围: 0-{config['max_freq']} Hz")
    st.sidebar.write(f"共振峰阈值: {config['min_prominence']} dB")
    st.sidebar.write(f"综合分析: {'开启' if config['comprehensive_analysis'] else '关闭'}")
    
    return config

def apply_preset_configuration(preset, current_config):
    """
    应用预设配置
    
    Parameters
    ----------
    preset : str
        预设配置名称
    current_config : dict
        当前配置
        
    Returns
    -------
    dict
        更新后的配置
    """
    
    if preset == "建筑声学":
        return {
            'target_freq_resolution': 0.01,
            'max_freq': 2000,
            'window_type': 'hann',
            'min_prominence': 6.0,
            'min_distance': 10.0,
            'max_peaks': 20,
            'min_height': None,
            'window_length': None,
            'overlap_ratio': 0.75,
            'time_range': 1.0,
            'comprehensive_analysis': True,
            'freq_range': None
        }
    elif preset == "语音分析":
        return {
            'target_freq_resolution': 0.1,
            'max_freq': 8000,
            'window_type': 'hamming',
            'min_prominence': 3.0,
            'min_distance': 20.0,
            'max_peaks': 15,
            'min_height': None,
            'window_length': 512,
            'overlap_ratio': 0.8,
            'time_range': 2.0,
            'comprehensive_analysis': True,
            'freq_range': None
        }
    elif preset == "音乐分析":
        return {
            'target_freq_resolution': 0.05,
            'max_freq': 20000,
            'window_type': 'blackman',
            'min_prominence': 8.0,
            'min_distance': 15.0,
            'max_peaks': 30,
            'min_height': None,
            'window_length': 2048,
            'overlap_ratio': 0.75,
            'time_range': 1.0,
            'comprehensive_analysis': True,
            'freq_range': None
        }
    elif preset == "快速分析":
        return {
            'target_freq_resolution': 0.5,
            'max_freq': 2000,
            'window_type': 'hann',
            'min_prominence': 10.0,
            'min_distance': 50.0,
            'max_peaks': 10,
            'min_height': None,
            'window_length': None,
            'overlap_ratio': 0.5,
            'time_range': 0.5,
            'comprehensive_analysis': False,
            'freq_range': None
        }
    elif preset == "高精度分析":
        return {
            'target_freq_resolution': 0.001,
            'max_freq': 4000,
            'window_type': 'blackman',
            'min_prominence': 3.0,
            'min_distance': 5.0,
            'max_peaks': 50,
            'min_height': None,
            'window_length': 4096,
            'overlap_ratio': 0.9,
            'time_range': 2.0,
            'comprehensive_analysis': True,
            'freq_range': None
        }
    else:
        return current_config

def main():
    """主界面"""
    
    # 参数配置
    config = configure_analysis_parameters()
    
    # 主要内容区域
    # 标题
    st.markdown('<h1 class="main-header">🎵 声学信号分析工具</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>🔧 专业版声学分析工具</strong><br>
    上传WAV音频文件，自定义分析参数，完成专业声学分析，自动生成频谱图和共振峰检测结果。
    支持参数调节、预设配置和综合分析。
    </div>
    """, unsafe_allow_html=True)
    
    # 显示当前配置信息
    st.info(f"""
    📋 **当前分析配置**: 
    频率分辨率: {config['target_freq_resolution']:.3f} Hz | 
    分析范围: 0-{config['max_freq']} Hz | 
    窗函数: {config['window_type']} | 
    共振峰阈值: {config['min_prominence']} dB |
    综合分析: {'开启' if config['comprehensive_analysis'] else '关闭'}
    """)
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "📂 选择WAV音频文件",
        type=['wav'],
        help="支持WAV格式音频文件，建议文件大小不超过50MB"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 文件名", uploaded_file.name)
        with col2:
            st.metric("📊 文件大小", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
        with col3:
            st.metric("🎵 文件类型", uploaded_file.type)
        
        # 分析按钮
        if st.button("🚀 开始分析", type="primary", use_container_width=True):
            with st.spinner("正在进行声学分析，请稍候..."):
                result = process_audio_file(uploaded_file, config)
                
                if result:
                    display_results(result)

def process_audio_file(uploaded_file, config):
    """
    处理音频文件分析
    
    Parameters
    ----------
    uploaded_file : UploadedFile
        上传的音频文件
    config : dict
        分析参数配置
        
    Returns
    -------
    str or None
        分析结果键值，成功时返回结果标识，失败时返回None
    """
    
    try:
        # 确保有输出目录
        if not os.path.exists("web_results"):
            os.makedirs("web_results")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = os.path.join("web_results", f"analysis_{timestamp}")
        os.makedirs(work_dir, exist_ok=True)
        
        # 保存上传的文件
        temp_file_path = os.path.join(work_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 创建输出目录
        output_dir = os.path.join(work_dir, "ana_res")
        
        # 创建分析器实例，使用用户配置的参数
        analyzer = SpectrumAnalyzer(
            target_freq_resolution=config['target_freq_resolution'],
            output_dir=output_dir
        )
        
        # 进行基础频谱分析，使用用户配置的参数
        result = analyzer.analyze_wav_file(
            temp_file_path, 
            max_freq=config['max_freq'],
            window_type=config['window_type']
        )
        
        if result['success']:
            # 使用用户配置重新进行共振峰检测
            resonance_result = analyzer.detect_resonance_peaks(
                result['frequencies'], 
                result['spl_db'],
                min_prominence=config['min_prominence'],
                min_distance=config['min_distance'],
                min_height=config['min_height'],
                max_peaks=config['max_peaks']
            )
            
            # 更新结果中的共振峰数据
            result['resonance_peaks'] = resonance_result
            
            # 绘制和保存分析图表
            save_prefix = "analysis"
            
            # 确定频率显示范围
            freq_range = config['freq_range'] if config['freq_range'] else (0, config['max_freq'])
            
            # 绘制频谱图
            analyzer.plot_spectrum(
                result, 
                freq_range=freq_range,
                save_path=f"{save_prefix}_frequency_spectrum.png",
                show_plot=False
            )
            
            # 绘制共振峰分析图和保存CSV数据
            if 'resonance_peaks' in result and result['resonance_peaks']:
                analyzer.plot_resonance_peaks(
                    result['frequencies'], result['spl_db'], result['resonance_peaks'],
                    freq_range=freq_range,
                    save_path=f"{save_prefix}_resonance_peaks.png",
                    show_plot=False
                )
                
                # 保存共振峰数据到CSV
                analyzer.save_resonance_peaks_csv(
                    result['resonance_peaks'],
                    result['filename'],
                    save_path=f"{save_prefix}_resonance_peaks.csv"
                )
            
            # 根据配置决定是否执行综合分析
            if config['comprehensive_analysis']:
                # 修改analyze_spectrogram方法调用以支持自定义参数
                if hasattr(analyzer, 'analyze_spectrogram') and config['window_length']:
                    # 如果用户设置了自定义窗长度，则使用自定义参数
                    frequencies_spec, times_spec, Sxx_spec = analyzer.analyze_spectrogram(
                        result['signal'],
                        result['sample_rate'],
                        window_length=config['window_length'],
                        overlap_ratio=config['overlap_ratio']
                    )
                
                analyzer.comprehensive_analysis(
                    result,
                    freq_range=freq_range,
                    time_range=config['time_range'],
                    save_prefix=save_prefix,
                    show_plot=False
                )
            
            # 保存结果到session state
            if 'analysis_results' not in st.session_state:
                st.session_state.analysis_results = {}
            
            result_key = f"analysis_{timestamp}"
            
            st.session_state.analysis_results[result_key] = {
                'result': result,
                'output_dir': output_dir,
                'work_dir': work_dir,
                'timestamp': timestamp,
                'filename': uploaded_file.name,
                'config': config  # 保存使用的配置
            }
            
            return result_key
        else:
            st.error(f"分析失败: {result.get('error', '未知错误')}")
            return None
            
    except Exception as e:
        st.error(f"处理文件时发生错误: {str(e)}")
        return None

def display_results(result_key):
    """
    显示分析结果
    
    Parameters
    ----------
    result_key : str
        分析结果的键值
    """
    
    if result_key not in st.session_state.analysis_results:
        st.error("分析结果不存在")
        return
    
    data = st.session_state.analysis_results[result_key]
    result = data['result']
    config = data.get('config', {})
    
    st.markdown('<div class="success-box">✅ 分析完成！</div>', unsafe_allow_html=True)
    
    # 显示分析配置信息
    with st.expander("📋 本次分析使用的配置参数", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**基础参数:**")
            st.write(f"• 频率分辨率: {config.get('target_freq_resolution', 'N/A')} Hz")
            st.write(f"• 最大分析频率: {config.get('max_freq', 'N/A')} Hz")
            st.write(f"• 窗函数类型: {config.get('window_type', 'N/A')}")
            st.write(f"• 综合分析: {'开启' if config.get('comprehensive_analysis', False) else '关闭'}")
            
        with col2:
            st.write("**共振峰检测参数:**")
            st.write(f"• 最小突出度: {config.get('min_prominence', 'N/A')} dB")
            st.write(f"• 最小频率间隔: {config.get('min_distance', 'N/A')} Hz")
            st.write(f"• 最大峰值数: {config.get('max_peaks', 'N/A')}")
            if config.get('min_height'):
                st.write(f"• 最小高度阈值: {config.get('min_height', 'N/A')} dB SPL")
    
    # 显示分析结果摘要
    st.markdown("### 📊 分析结果")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🕒 文件时长", f"{result['duration']:.2f} 秒")
    with col2:
        st.metric("📡 采样率", f"{result['sample_rate']:,} Hz")
    with col3:
        st.metric("🎯 峰值频率", f"{result['peak_frequency']:.1f} Hz")
    with col4:
        st.metric("📢 峰值声压级", f"{result['peak_spl']:.1f} dB")
    
    # 共振峰信息
    if 'resonance_peaks' in result and result['resonance_peaks']:
        resonance_stats = result['resonance_peaks']['statistics']
        resonance_peaks = result['resonance_peaks']['resonance_peaks']
        
        st.markdown("### 🎯 共振峰特征")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("检测到共振峰", f"{resonance_stats['total_peaks']} 个")
        with col2:
            st.metric("频率范围", f"{resonance_stats['frequency_range'][0]:.1f} - {resonance_stats['frequency_range'][1]:.1f} Hz")
        with col3:
            st.metric("主导峰值", f"{resonance_stats['dominant_peak']['center_frequency']:.1f} Hz")
        
        # 共振峰详细数据表（显示前5个）
        if resonance_peaks:
            st.markdown("#### 📋 主要共振峰")
            
            peak_data = []
            for peak in resonance_peaks[:5]:  # 只显示前5个
                peak_data.append({
                    "排名": peak['rank'],
                    "中心频率 (Hz)": f"{peak['center_frequency']:.2f}",
                    "声压级 (dB)": f"{peak['peak_spl']:.1f}",
                    "突出度 (dB)": f"{peak['prominence']:.1f}"
                })
            
            st.dataframe(pd.DataFrame(peak_data), width='stretch')
    
    # 图片展示
    display_result_images(data['output_dir'])
    
    # 下载功能
    st.markdown("### 📥 下载结果")
    create_download_package(result_key)








def display_result_images(output_dir):
    """显示结果图片"""
    
    if not os.path.exists(output_dir):
        return
    
    st.markdown("### 📈 分析图表")
    
    # 查找所有PNG图片
    image_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.png'):
                image_files.append(os.path.join(root, file))
    
    if image_files:
        # 按类型分组显示图片
        frequency_images = [f for f in image_files if 'frequency' in f]
        resonance_images = [f for f in image_files if 'resonance' in f]
        comprehensive_images = [f for f in image_files if 'comprehensive' in f]
        other_images = [f for f in image_files if f not in frequency_images + resonance_images + comprehensive_images]
        
        # 频谱图
        if frequency_images:
            st.markdown("#### 🎵 频谱分析图")
            for img_path in frequency_images:
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    st.image(image, caption=os.path.basename(img_path), width='stretch')
        
        # 共振峰图
        if resonance_images:
            st.markdown("#### 🎯 共振峰分析图")
            for img_path in resonance_images:
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    st.image(image, caption=os.path.basename(img_path), width='stretch')
        
        # 综合分析图
        if comprehensive_images:
            st.markdown("#### 📊 综合分析图")
            for img_path in comprehensive_images:
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    st.image(image, caption=os.path.basename(img_path), width='stretch')
        
        # 其他图
        if other_images:
            st.markdown("#### 📈 其他分析图")
            for img_path in other_images:
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    st.image(image, caption=os.path.basename(img_path), width='stretch')
    else:
        st.info("没有找到分析结果图片")

def create_download_package(result_key):
    """
    创建下载包
    
    Parameters
    ---------- 
    result_key : str
        分析结果的键值
    """
    
    if result_key not in st.session_state.analysis_results:
        st.error("分析结果不存在")
        return
    
    data = st.session_state.analysis_results[result_key]
    work_dir = data.get('work_dir')
    
    if not work_dir or not os.path.exists(work_dir):
        st.error("结果文件不存在")
        return
    
    # 创建ZIP文件
    zip_path = os.path.join(work_dir, f"analysis_results_{data['timestamp']}.zip")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(work_dir):
                for file in files:
                    if not file.endswith('.zip') and not file.endswith('.wav'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, work_dir)
                        zipf.write(file_path, arcname)
        
        if os.path.exists(zip_path):
            with open(zip_path, "rb") as f:
                zip_data = f.read()
            
            st.download_button(
                label="📦 下载分析结果",
                data=zip_data,
                file_name=f"analysis_results_{data['timestamp']}.zip",
                mime="application/zip",
                help="包含所有分析结果图片和数据文件",
                width='stretch'
            )
            
            st.success(f"✅ 下载包已准备完成，文件大小: {len(zip_data) / 1024 / 1024:.2f} MB")
        else:
            st.error("创建下载包失败")
            
    except Exception as e:
        st.error(f"创建下载包时发生错误: {e}")

# 页面底部信息
def show_footer():
    """显示页面底部信息"""
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🎵 声学信号分析工具 v2.0 Professional | 基于专业FFT频谱分析和共振峰检测技术</p>
        <p>支持参数定制、预设配置、实时调节 | 适用于建筑声学研究、音响工程、声学设计等专业领域</p>
        <p><small>新功能: 可调节频率分辨率、共振峰检测参数、时频分析参数、多种预设配置</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()
