#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声学信号分析工具
================

简约版声学信号分析工具 - 快速分析WAV音频文件

作者：nanqipro
"""

import streamlit as st
import os
import zipfile
from pathlib import Path
import pandas as pd
from PIL import Image
from datetime import datetime

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
    initial_sidebar_state="collapsed"
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

def main():
    """主界面"""
    
    # 标题
    st.markdown('<h1 class="main-header">🎵 声学信号分析工具</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>🔧 简约版声学分析工具</strong><br>
    上传WAV音频文件，一键完成专业声学分析，自动生成频谱图和共振峰检测结果。
    </div>
    """, unsafe_allow_html=True)
    
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
        if st.button("🚀 开始分析", type="primary", width='stretch'):
            with st.spinner("正在进行声学分析，请稍候..."):
                result = process_audio_file(uploaded_file)
                
                if result:
                    display_results(result)

def process_audio_file(uploaded_file):
    """
    处理音频文件分析
    
    Parameters
    ----------
    uploaded_file : UploadedFile
        上传的音频文件
        
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
        
        # 创建分析器实例并指定正确的输出目录
        analyzer = SpectrumAnalyzer(output_dir=output_dir)
        
        # 手动进行分析（因为analyze_single_wav_file不支持自定义output_dir）
        result = analyzer.analyze_wav_file(temp_file_path, max_freq=2000)
        
        if result['success']:
            # 绘制和保存分析图表
            save_prefix = "analysis"
            
            # 绘制频谱图
            analyzer.plot_spectrum(
                result, 
                freq_range=(0, 2000),
                save_path=f"{save_prefix}_frequency_spectrum.png",
                show_plot=False
            )
            
            # 绘制共振峰分析图和保存CSV数据
            if 'resonance_peaks' in result and result['resonance_peaks']:
                analyzer.plot_resonance_peaks(
                    result['frequencies'], result['spl_db'], result['resonance_peaks'],
                    freq_range=(0, 2000),
                    save_path=f"{save_prefix}_resonance_peaks.png",
                    show_plot=False
                )
                
                # 保存共振峰数据到CSV
                analyzer.save_resonance_peaks_csv(
                    result['resonance_peaks'],
                    result['filename'],
                    save_path=f"{save_prefix}_resonance_peaks.csv"
                )
            
            # 执行综合分析
            analyzer.comprehensive_analysis(
                result,
                freq_range=(0, 2000),
                time_range=1.0,  # 时域显示前1秒
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
                'filename': uploaded_file.name
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
    
    st.markdown('<div class="success-box">✅ 分析完成！</div>', unsafe_allow_html=True)
    
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
        <p>🎵 声学信号分析工具 v1.0 | 基于专业FFT频谱分析和共振峰检测技术</p>
        <p>适用于建筑声学研究、音响工程、声学设计等专业领域</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()
