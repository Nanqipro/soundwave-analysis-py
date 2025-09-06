#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数功能演示脚本
================

展示新增的参数调节功能如何使用

作者：nanqipro
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from wav_to_spectrum_analyzer import SpectrumAnalyzer
    from streamlit_app import apply_preset_configuration
except ImportError as e:
    print(f"❌ 无法导入分析模块: {e}")
    sys.exit(1)


def find_demo_file():
    """寻找演示用的WAV文件"""
    
    search_paths = ["data", ".", "examples", "samples"]
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.wav'):
                        return os.path.join(root, file)
    
    return None


def demo_frequency_resolution_impact():
    """演示频率分辨率参数的影响"""
    
    print("\n🎯 演示1：频率分辨率参数的影响")
    print("=" * 50)
    
    demo_file = find_demo_file()
    if not demo_file:
        print("❌ 未找到演示用WAV文件")
        return
    
    print(f"📁 使用文件: {os.path.basename(demo_file)}")
    
    # 测试不同的频率分辨率
    resolutions = [0.1, 0.01, 0.001]
    results = {}
    
    for resolution in resolutions:
        print(f"\n🔍 测试频率分辨率: {resolution} Hz")
        
        # 创建分析器
        analyzer = SpectrumAnalyzer(
            target_freq_resolution=resolution,
            output_dir=f"demo_resolution_{resolution}"
        )
        
        # 分析
        result = analyzer.analyze_wav_file(demo_file, max_freq=2000)
        
        if result['success']:
            actual_resolution = result['frequencies'][1] - result['frequencies'][0]
            freq_points = len(result['frequencies'])
            
            print(f"   实际分辨率: {actual_resolution:.6f} Hz")
            print(f"   频率点数: {freq_points:,}")
            
            results[resolution] = {
                'actual_resolution': actual_resolution,
                'freq_points': freq_points,
                'frequencies': result['frequencies'],
                'spl_db': result['spl_db']
            }
        else:
            print(f"   ❌ 分析失败: {result.get('error', '未知错误')}")
    
    # 生成对比图
    if len(results) >= 2:
        create_resolution_comparison_plot(results)
    
    return results


def demo_resonance_detection_parameters():
    """演示共振峰检测参数的影响"""
    
    print("\n🎯 演示2：共振峰检测参数的影响")
    print("=" * 50)
    
    demo_file = find_demo_file()
    if not demo_file:
        print("❌ 未找到演示用WAV文件")
        return
    
    # 创建基础分析器
    analyzer = SpectrumAnalyzer(target_freq_resolution=0.01, output_dir="demo_resonance")
    
    # 进行基础分析
    result = analyzer.analyze_wav_file(demo_file, max_freq=2000)
    
    if not result['success']:
        print(f"❌ 基础分析失败: {result.get('error', '未知错误')}")
        return
    
    # 测试不同的共振峰检测参数
    detection_configs = [
        {"name": "敏感检测", "min_prominence": 3.0, "min_distance": 5.0, "max_peaks": 50},
        {"name": "标准检测", "min_prominence": 6.0, "min_distance": 10.0, "max_peaks": 20},
        {"name": "严格检测", "min_prominence": 10.0, "min_distance": 20.0, "max_peaks": 10}
    ]
    
    resonance_results = {}
    
    for config in detection_configs:
        print(f"\n🔍 测试 {config['name']}:")
        print(f"   突出度阈值: {config['min_prominence']} dB")
        print(f"   频率间隔: {config['min_distance']} Hz")
        print(f"   最大峰值数: {config['max_peaks']}")
        
        # 检测共振峰
        resonance_result = analyzer.detect_resonance_peaks(
            result['frequencies'],
            result['spl_db'],
            min_prominence=config['min_prominence'],
            min_distance=config['min_distance'],
            max_peaks=config['max_peaks']
        )
        
        peak_count = resonance_result['statistics']['total_peaks']
        print(f"   检测到峰值: {peak_count} 个")
        
        if peak_count > 0:
            dominant_peak = resonance_result['statistics']['dominant_peak']
            print(f"   主导峰值: {dominant_peak['center_frequency']:.1f} Hz, {dominant_peak['peak_spl']:.1f} dB")
        
        resonance_results[config['name']] = resonance_result
    
    # 生成共振峰对比图
    create_resonance_comparison_plot(result['frequencies'], result['spl_db'], resonance_results)
    
    return resonance_results


def demo_preset_configurations():
    """演示预设配置的效果"""
    
    print("\n🎯 演示3：预设配置的效果")
    print("=" * 50)
    
    # 基础配置
    base_config = {
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
    
    presets = ["建筑声学", "语音分析", "音乐分析"]
    
    print("📋 预设配置对比:")
    print("-" * 30)
    
    for preset in presets:
        config = apply_preset_configuration(preset, base_config)
        
        print(f"\n🎛️ {preset}配置:")
        print(f"   频率分辨率: {config['target_freq_resolution']} Hz")
        print(f"   最大频率: {config['max_freq']} Hz")
        print(f"   窗函数: {config['window_type']}")
        print(f"   突出度阈值: {config['min_prominence']} dB")
        print(f"   频率间隔: {config['min_distance']} Hz")
        
        if config.get('window_length'):
            print(f"   STFT窗长度: {config['window_length']}")
        
        # 显示应用场景
        scenarios = {
            "建筑声学": "适用于：室内声学测量、建筑空间分析、声学设计",
            "语音分析": "适用于：语音信号处理、通信系统、语音识别",
            "音乐分析": "适用于：音乐信号分析、音频工程、频谱研究"
        }
        print(f"   应用场景: {scenarios.get(preset, '')}")


def create_resolution_comparison_plot(results):
    """创建频率分辨率对比图"""
    
    print(f"\n📊 生成频率分辨率对比图...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 左图：频谱对比
    colors = ['blue', 'red', 'green']
    for i, (resolution, data) in enumerate(results.items()):
        freq = data['frequencies']
        spl = data['spl_db']
        
        # 限制显示范围以便对比
        mask = freq <= 1000  # 只显示0-1000Hz
        ax1.plot(freq[mask], spl[mask], 
                color=colors[i % len(colors)], 
                alpha=0.8, 
                linewidth=1.0,
                label=f'{resolution} Hz ({data["freq_points"]:,} points)')
    
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('SPL (dB)')
    ax1.set_title('Frequency Resolution Comparison (0-1000 Hz)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 右图：频率点数对比
    resolutions = list(results.keys())
    freq_points = [results[res]['freq_points'] for res in resolutions]
    
    bars = ax2.bar([str(res) for res in resolutions], freq_points, 
                   color=['lightblue', 'lightcoral', 'lightgreen'])
    ax2.set_xlabel('Target Frequency Resolution (Hz)')
    ax2.set_ylabel('Number of Frequency Points')
    ax2.set_title('Frequency Points vs Resolution')
    ax2.set_yscale('log')
    
    # 在柱上标注数值
    for bar, points in zip(bars, freq_points):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{points:,}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # 保存图片
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_path = f"demo_frequency_resolution_comparison_{timestamp}.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 对比图已保存: {plot_path}")


def create_resonance_comparison_plot(frequencies, spl_db, resonance_results):
    """创建共振峰检测对比图"""
    
    print(f"\n📊 生成共振峰检测对比图...")
    
    fig, axes = plt.subplots(len(resonance_results), 1, figsize=(12, 4*len(resonance_results)))
    
    if len(resonance_results) == 1:
        axes = [axes]
    
    colors = ['red', 'orange', 'purple']
    
    for i, (config_name, resonance_result) in enumerate(resonance_results.items()):
        ax = axes[i]
        
        # 绘制频谱
        ax.plot(frequencies, spl_db, 'b-', alpha=0.7, linewidth=1.0, label='Spectrum')
        
        # 标记共振峰
        resonance_peaks = resonance_result['resonance_peaks']
        if resonance_peaks:
            peak_freqs = [peak['center_frequency'] for peak in resonance_peaks]
            peak_spls = [peak['peak_spl'] for peak in resonance_peaks]
            
            ax.scatter(peak_freqs, peak_spls, 
                      color=colors[i % len(colors)], 
                      s=80, alpha=0.8, 
                      label=f'Peaks ({len(resonance_peaks)})', 
                      zorder=5)
        
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('SPL (dB)')
        ax.set_title(f'{config_name} - {len(resonance_peaks) if resonance_peaks else 0} Peaks Detected')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 1000])  # 限制显示范围
    
    plt.tight_layout()
    
    # 保存图片
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_path = f"demo_resonance_detection_comparison_{timestamp}.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 对比图已保存: {plot_path}")


def main():
    """主函数"""
    
    print("🎯 声学分析工具新功能演示")
    print("=" * 60)
    print("✨ 本演示将展示新增的参数调节功能")
    print("🔧 包括频率分辨率、共振峰检测、预设配置等")
    print("=" * 60)
    
    # 检查演示文件
    demo_file = find_demo_file()
    if not demo_file:
        print("❌ 未找到演示用WAV文件")
        print("💡 请在以下目录中放置WAV文件：")
        print("   - data/")
        print("   - 当前目录")
        print("   - examples/")
        return
    
    print(f"📁 将使用文件: {demo_file}")
    
    # 询问演示模式
    print("\n📋 请选择演示内容:")
    print("1. 🔍 频率分辨率参数影响")
    print("2. 🎯 共振峰检测参数影响")
    print("3. 🎛️ 预设配置展示")
    print("4. 🎪 完整演示（全部内容）")
    
    try:
        choice = input("\n请输入选择 (1/2/3/4): ").strip()
    except KeyboardInterrupt:
        print("\n👋 演示已取消")
        return
    
    if choice == "1":
        demo_frequency_resolution_impact()
    elif choice == "2":
        demo_resonance_detection_parameters()
    elif choice == "3":
        demo_preset_configurations()
    elif choice == "4":
        # 完整演示
        demo_preset_configurations()
        demo_frequency_resolution_impact()
        demo_resonance_detection_parameters()
    else:
        print("❌ 无效选择")
        return
    
    print(f"\n🎉 演示完成！")
    print(f"💡 您现在可以:")
    print(f"   1. 启动Web界面: python start_web.py")
    print(f"   2. 在侧边栏调节参数")
    print(f"   3. 观察不同参数对分析结果的影响")
    print(f"   4. 使用预设配置快速开始")


if __name__ == "__main__":
    main()
