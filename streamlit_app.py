#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声学信号分析Web界面
==================

基于Streamlit的交互式声学信号分析工具
支持单个文件和批量文件分析

作者：AI Assistant
"""

import streamlit as st
import os
import tempfile
import zipfile
import shutil
from pathlib import Path
import pandas as pd
from PIL import Image
import time
from datetime import datetime
import base64

# 添加当前目录到Python路径
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from wav_to_spectrum_analyzer import (
        SpectrumAnalyzer, 
        analyze_single_wav_file, 
        analyze_resonance_peaks_only
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
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
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
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主界面"""
    
    # 标题
    st.markdown('<h1 class="main-header">🎵 声学信号分析工具</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>🎯 功能特点：</strong>
    <ul>
        <li>🎵 高精度频谱分析（0.01Hz分辨率）</li>
        <li>🎯 智能共振峰检测与特征提取</li>
        <li>📊 多维度声学分析（时域+频域+相位+时频）</li>
        <li>📈 专业可视化图表生成</li>
        <li>📋 详细数据CSV导出</li>
        <li>💼 支持单个文件和批量分析</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏 - 分析模式选择
    st.sidebar.title("📋 分析设置")
    
    analysis_mode = st.sidebar.selectbox(
        "🔍 选择分析模式",
        ["单个文件分析", "批量文件分析", "专门共振峰分析"]
    )
    
    # 分析参数设置
    st.sidebar.markdown("### ⚙️ 分析参数")
    
    max_freq = st.sidebar.slider(
        "最大分析频率 (Hz)",
        min_value=500,
        max_value=5000,
        value=2000,
        step=100
    )
    
    comprehensive = st.sidebar.checkbox(
        "启用综合分析",
        value=True,
        help="包含时域、频域、相位、时频四维分析"
    )
    
    # 共振峰检测参数
    with st.sidebar.expander("🎯 共振峰检测参数"):
        min_prominence = st.slider(
            "最小突出度 (dB)",
            min_value=2.0,
            max_value=15.0,
            value=6.0,
            step=0.5
        )
        
        min_distance = st.slider(
            "最小频率间隔 (Hz)",
            min_value=2.0,
            max_value=30.0,
            value=10.0,
            step=1.0
        )
        
        max_peaks = st.slider(
            "最大检测峰值数",
            min_value=5,
            max_value=30,
            value=15,
            step=1
        )
    
    # 根据分析模式显示不同界面
    if analysis_mode == "单个文件分析":
        single_file_interface(max_freq, comprehensive, min_prominence, min_distance, max_peaks)
    elif analysis_mode == "批量文件分析":
        batch_analysis_interface(max_freq, comprehensive, min_prominence, min_distance, max_peaks)
    else:
        resonance_only_interface(max_freq, min_prominence, min_distance, max_peaks)

def single_file_interface(max_freq, comprehensive, min_prominence, min_distance, max_peaks):
    """单个文件分析界面"""
    
    st.markdown('<h2 class="sub-header">📁 单个文件分析</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "选择WAV音频文件",
        type=['wav'],
        help="支持WAV格式音频文件"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        st.markdown("### 📋 文件信息")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("文件名", uploaded_file.name)
        with col2:
            st.metric("文件大小", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
        with col3:
            st.metric("文件类型", uploaded_file.type)
        
        # 分析按钮
        if st.button("🚀 开始分析", type="primary"):
            with st.spinner("正在分析中，请稍候..."):
                result = process_single_file(
                    uploaded_file, max_freq, comprehensive, 
                    min_prominence, min_distance, max_peaks
                )
                
                if result:
                    display_analysis_results(result)

def batch_analysis_interface(max_freq, comprehensive, min_prominence, min_distance, max_peaks):
    """批量文件分析界面"""
    
    st.markdown('<h2 class="sub-header">💼 批量文件分析</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
    <strong>📝 使用说明：</strong><br>
    1. 可以上传多个WAV文件进行批量分析<br>
    2. 建议单次上传文件数量不超过20个<br>
    3. 每个文件大小建议不超过50MB
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "选择多个WAV音频文件",
        type=['wav'],
        accept_multiple_files=True,
        help="可以选择多个WAV文件进行批量分析"
    )
    
    if uploaded_files:
        # 显示文件列表
        st.markdown("### 📋 待分析文件列表")
        
        file_data = []
        for file in uploaded_files:
            file_data.append({
                "文件名": file.name,
                "大小 (MB)": f"{file.size / 1024 / 1024:.2f}",
                "类型": file.type
            })
        
        st.dataframe(pd.DataFrame(file_data), use_container_width=True)
        
        total_size = sum(file.size for file in uploaded_files) / 1024 / 1024
        st.info(f"总计 {len(uploaded_files)} 个文件，总大小 {total_size:.2f} MB")
        
        # 批量分析按钮
        if st.button("🚀 开始批量分析", type="primary"):
            process_batch_files(
                uploaded_files, max_freq, comprehensive,
                min_prominence, min_distance, max_peaks
            )

def resonance_only_interface(max_freq, min_prominence, min_distance, max_peaks):
    """专门共振峰分析界面"""
    
    st.markdown('<h2 class="sub-header">🎯 专门共振峰分析</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>🔍 专门共振峰分析：</strong><br>
    专注于建筑声学共振频率的精确检测和分析，适用于古建筑声学研究、
    音厅设计等专业应用场景。
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "选择WAV音频文件",
        type=['wav'],
        key="resonance_file"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        st.markdown("### 📋 文件信息")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("文件名", uploaded_file.name)
        with col2:
            st.metric("文件大小", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
        
        # 共振峰分析按钮
        if st.button("🎯 开始共振峰分析", type="primary"):
            with st.spinner("正在进行共振峰分析..."):
                result = process_resonance_analysis(
                    uploaded_file, max_freq, 
                    min_prominence, min_distance, max_peaks
                )
                
                if result:
                    display_resonance_results(result)

def process_single_file(uploaded_file, max_freq, comprehensive, min_prominence, min_distance, max_peaks):
    """处理单个文件分析"""
    
    try:
        # 确保有输出目录
        if not os.path.exists("web_results"):
            os.makedirs("web_results")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = os.path.join("web_results", f"single_{timestamp}")
        os.makedirs(work_dir, exist_ok=True)
        
        # 保存上传的文件
        temp_file_path = os.path.join(work_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 创建输出目录
        output_dir = os.path.join(work_dir, "ana_res")
        
        # 创建分析器
        analyzer = SpectrumAnalyzer(output_dir=output_dir)
        
        # 执行分析
        result = analyze_single_wav_file(
            wav_file_path=temp_file_path,
            max_freq=max_freq,
            comprehensive=comprehensive,
            save_prefix="analysis",
            auto_subdir=False
        )
        
        if result['success']:
            # 保存结果到session state
            if 'analysis_results' not in st.session_state:
                st.session_state.analysis_results = {}
            
            result_key = f"single_{timestamp}"
            
            st.session_state.analysis_results[result_key] = {
                'type': 'single',
                'result': result,
                'output_dir': output_dir,
                'work_dir': work_dir,
                'timestamp': timestamp
            }
            
            return result_key
        else:
            st.error(f"分析失败: {result.get('error', '未知错误')}")
            return None
            
    except Exception as e:
        st.error(f"处理文件时发生错误: {str(e)}")
        return None

def process_batch_files(uploaded_files, max_freq, comprehensive, min_prominence, min_distance, max_peaks):
    """处理批量文件分析"""
    
    try:
        # 确保有输出目录
        if not os.path.exists("web_results"):
            os.makedirs("web_results")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = os.path.join("web_results", f"batch_{timestamp}")
        os.makedirs(work_dir, exist_ok=True)
        
        # 创建数据目录结构
        data_dir = os.path.join(work_dir, "data", "uploaded_files")
        os.makedirs(data_dir, exist_ok=True)
        
        # 保存所有上传的文件
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"正在保存文件: {uploaded_file.name}")
            
            file_path = os.path.join(data_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # 创建输出目录
        output_dir = os.path.join(work_dir, "ana_res")
        
        # 创建分析器
        analyzer = SpectrumAnalyzer(output_dir=output_dir)
        
        status_text.text("正在进行批量分析...")
        
        # 执行批量分析
        results = analyzer.batch_analyze_directory(
            data_dir=os.path.join(work_dir, "data"),
            max_freq=max_freq,
            plot_individual=True,
            plot_comparison=False,
            comprehensive_analysis=comprehensive
        )
        
        progress_bar.progress(1.0)
        status_text.text("分析完成!")
        
        # 保存结果到session state
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        
        result_key = f"batch_{timestamp}"
        
        st.session_state.analysis_results[result_key] = {
            'type': 'batch',
            'results': results,
            'output_dir': output_dir,
            'work_dir': work_dir,
            'timestamp': timestamp,
            'file_count': len(uploaded_files)
        }
        
        display_batch_results(result_key)
        
    except Exception as e:
        st.error(f"批量分析时发生错误: {str(e)}")

def process_resonance_analysis(uploaded_file, max_freq, min_prominence, min_distance, max_peaks):
    """处理共振峰分析"""
    
    try:
        # 确保有输出目录
        if not os.path.exists("web_results"):
            os.makedirs("web_results")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = os.path.join("web_results", f"resonance_{timestamp}")
        os.makedirs(work_dir, exist_ok=True)
        
        # 保存上传的文件
        temp_file_path = os.path.join(work_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 创建输出目录
        output_dir = os.path.join(work_dir, "ana_res")
        
        # 创建分析器
        analyzer = SpectrumAnalyzer(output_dir=output_dir)
        
        # 执行共振峰分析
        result = analyze_resonance_peaks_only(
            wav_file_path=temp_file_path,
            min_prominence=min_prominence,
            min_distance=min_distance,
            max_freq=max_freq,
            save_prefix="resonance"
        )
        
        if result['success']:
            # 保存结果到session state
            if 'analysis_results' not in st.session_state:
                st.session_state.analysis_results = {}
            
            result_key = f"resonance_{timestamp}"
            
            st.session_state.analysis_results[result_key] = {
                'type': 'resonance',
                'result': result,
                'output_dir': output_dir,
                'work_dir': work_dir,
                'timestamp': timestamp
            }
            
            return result_key
        else:
            st.error(f"共振峰分析失败: {result.get('error', '未知错误')}")
            return None
            
    except Exception as e:
        st.error(f"处理共振峰分析时发生错误: {str(e)}")
        return None

def display_analysis_results(result_key):
    """显示单个文件分析结果"""
    
    if result_key not in st.session_state.analysis_results:
        st.error("分析结果不存在")
        return
    
    data = st.session_state.analysis_results[result_key]
    result = data['result']
    
    st.markdown('<div class="success-box">✅ 分析完成！</div>', unsafe_allow_html=True)
    
    # 显示分析结果摘要
    st.markdown("### 📊 分析结果摘要")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("文件时长", f"{result['duration']:.2f} 秒")
    with col2:
        st.metric("采样率", f"{result['sample_rate']:,} Hz")
    with col3:
        st.metric("峰值频率", f"{result['peak_frequency']:.1f} Hz")
    with col4:
        st.metric("峰值声压级", f"{result['peak_spl']:.1f} dB")
    
    # 共振峰信息
    if 'resonance_peaks' in result and result['resonance_peaks']:
        st.markdown("### 🎯 共振峰特征")
        
        resonance_stats = result['resonance_peaks']['statistics']
        resonance_peaks = result['resonance_peaks']['resonance_peaks']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("检测到共振峰", f"{resonance_stats['total_peaks']} 个")
        with col2:
            st.metric("频率范围", f"{resonance_stats['frequency_range'][0]:.1f} - {resonance_stats['frequency_range'][1]:.1f} Hz")
        with col3:
            st.metric("主导峰值", f"{resonance_stats['dominant_peak']['center_frequency']:.1f} Hz")
        
        # 共振峰详细数据表
        if resonance_peaks:
            st.markdown("#### 📋 共振峰详细数据")
            
            peak_data = []
            for peak in resonance_peaks[:10]:  # 显示前10个
                peak_data.append({
                    "排名": peak['rank'],
                    "中心频率 (Hz)": f"{peak['center_frequency']:.2f}",
                    "声压级 (dB)": f"{peak['peak_spl']:.1f}",
                    "突出度 (dB)": f"{peak['prominence']:.1f}"
                })
            
            st.dataframe(pd.DataFrame(peak_data), use_container_width=True)
    
    # 图片展示
    display_result_images(data['output_dir'])
    
    # 下载功能
    st.markdown("### 📥 下载结果")
    create_download_section(result_key)

def display_batch_results(result_key):
    """显示批量分析结果"""
    
    if result_key not in st.session_state.analysis_results:
        st.error("分析结果不存在")
        return
    
    data = st.session_state.analysis_results[result_key]
    results = data['results']
    
    st.markdown('<div class="success-box">✅ 批量分析完成！</div>', unsafe_allow_html=True)
    
    # 统计信息
    total_files = sum(len(subdir_results) for subdir_results in results.values())
    successful_files = sum(len([r for r in subdir_results if r['success']]) 
                          for subdir_results in results.values())
    
    st.markdown("### 📊 批量分析统计")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("处理文件数", total_files)
    with col2:
        st.metric("成功分析", successful_files)
    with col3:
        st.metric("成功率", f"{successful_files/total_files*100:.1f}%")
    
    # 详细结果
    st.markdown("### 📋 详细分析结果")
    
    for subdir, subdir_results in results.items():
        with st.expander(f"📁 文件组: {subdir} ({len(subdir_results)} 个文件)"):
            result_data = []
            for result in subdir_results:
                if result['success']:
                    result_data.append({
                        "文件名": result['filename'],
                        "时长 (秒)": f"{result['duration']:.2f}",
                        "采样率 (Hz)": f"{result['sample_rate']:,}",
                        "峰值频率 (Hz)": f"{result['peak_frequency']:.1f}",
                        "峰值声压级 (dB)": f"{result['peak_spl']:.1f}",
                        "共振峰数量": result['resonance_peaks']['statistics']['total_peaks'] if 'resonance_peaks' in result else 0
                    })
                else:
                    result_data.append({
                        "文件名": result['filename'],
                        "状态": "分析失败",
                        "错误": result.get('error', '未知错误')
                    })
            
            if result_data:
                st.dataframe(pd.DataFrame(result_data), use_container_width=True)
    
    # 下载功能
    st.markdown("### 📥 下载结果")
    create_download_section(result_key)

def display_resonance_results(result_key):
    """显示共振峰分析结果"""
    
    if result_key not in st.session_state.analysis_results:
        st.error("分析结果不存在")
        return
    
    data = st.session_state.analysis_results[result_key]
    result = data['result']
    
    st.markdown('<div class="success-box">✅ 共振峰分析完成！</div>', unsafe_allow_html=True)
    
    # 共振峰详细信息
    if 'resonance_peaks' in result and result['resonance_peaks']:
        resonance_stats = result['resonance_peaks']['statistics']
        resonance_peaks = result['resonance_peaks']['resonance_peaks']
        
        st.markdown("### 🎯 共振峰分析结果")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("检测到共振峰", f"{resonance_stats['total_peaks']} 个")
        with col2:
            st.metric("频率范围", f"{resonance_stats['frequency_range'][0]:.1f} - {resonance_stats['frequency_range'][1]:.1f} Hz")
        with col3:
            st.metric("平均频率", f"{resonance_stats['mean_frequency']:.1f} Hz")
        with col4:
            st.metric("主导峰值", f"{resonance_stats['dominant_peak']['center_frequency']:.1f} Hz")
        
        # 详细共振峰数据
        st.markdown("### 📋 共振峰详细数据")
        
        peak_data = []
        for peak in resonance_peaks:
            peak_data.append({
                "排名": peak['rank'],
                "中心频率 (Hz)": f"{peak['center_frequency']:.3f}",
                "声压级 (dB SPL)": f"{peak['peak_spl']:.2f}",
                "突出度 (dB)": f"{peak['prominence']:.2f}"
            })
        
        st.dataframe(pd.DataFrame(peak_data), use_container_width=True)
    
    # 图片展示
    display_result_images(data['output_dir'])
    
    # 下载功能
    st.markdown("### 📥 下载结果")
    create_download_section(result_key)

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
                    st.image(image, caption=os.path.basename(img_path), use_column_width=True)
        
        # 共振峰图
        if resonance_images:
            st.markdown("#### 🎯 共振峰分析图")
            for img_path in resonance_images:
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    st.image(image, caption=os.path.basename(img_path), use_column_width=True)
        
        # 综合分析图
        if comprehensive_images:
            st.markdown("#### 📊 综合分析图")
            for img_path in comprehensive_images:
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    st.image(image, caption=os.path.basename(img_path), use_column_width=True)
        
        # 其他图
        if other_images:
            st.markdown("#### 📈 其他分析图")
            for img_path in other_images:
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    st.image(image, caption=os.path.basename(img_path), use_column_width=True)
    else:
        st.info("没有找到分析结果图片")

def create_download_section(result_key):
    """创建下载区域"""
    
    if result_key not in st.session_state.analysis_results:
        st.error("分析结果不存在")
        return
    
    data = st.session_state.analysis_results[result_key]
    work_dir = data.get('work_dir', data.get('output_dir'))
    
    if not work_dir or not os.path.exists(work_dir):
        st.error("结果文件不存在")
        return
    
    # 创建下载ZIP包
    zip_path = create_download_package(result_key)
    
    if zip_path and os.path.exists(zip_path):
        with open(zip_path, "rb") as f:
            zip_data = f.read()
        
        st.download_button(
            label="📦 下载全部结果文件",
            data=zip_data,
            file_name=f"analysis_results_{data['timestamp']}.zip",
            mime="application/zip",
            help="包含所有分析结果图片和数据文件"
        )
        
        st.success(f"✅ 结果文件已准备完成，文件大小: {len(zip_data) / 1024 / 1024:.2f} MB")
    else:
        st.error("创建下载包失败")

def create_download_package(result_key):
    """创建下载包"""
    
    if result_key not in st.session_state.analysis_results:
        return None
    
    data = st.session_state.analysis_results[result_key]
    work_dir = data.get('work_dir', data.get('output_dir'))
    
    if not work_dir or not os.path.exists(work_dir):
        return None
    
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
        
        return zip_path if os.path.exists(zip_path) else None
    except Exception as e:
        st.error(f"创建下载包时发生错误: {e}")
        return None

# 页面底部信息
def show_footer():
    """显示页面底部信息"""
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🎵 声学信号分析工具 v1.0 | 基于专业FFT频谱分析和共振峰检测技术</p>
        <p>适用于建筑声学研究、音响工程、声学设计等专业领域</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()
