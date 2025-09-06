#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共振峰分析功能演示脚本
====================

演示如何使用wav_to_spectrum_analyzer.py中的共振峰检测和分析功能

🎯 演示功能：
- 共振峰自动检测
- 中心频率和峰值声压级提取  
- 共振峰可视化图表
- 统计分析结果

作者：AI Assistant
"""

import os
import sys
from wav_to_spectrum_analyzer import analyze_resonance_peaks_only, quick_analyze, SpectrumAnalyzer


def find_demo_wav_file():
    """
    寻找可用于演示的WAV文件
    
    Returns
    -------
    str or None
        找到的WAV文件路径，如果没找到返回None
    """
    search_paths = ["data", ".", "examples", "samples"]
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.wav'):
                        return os.path.join(root, file)
    return None


def demo_basic_resonance_analysis():
    """
    演示基础共振峰分析功能
    """
    print("🎯 演示1: 基础共振峰分析")
    print("=" * 60)
    
    # 寻找演示文件
    demo_file = find_demo_wav_file()
    if not demo_file:
        print("❌ 未找到可用于演示的WAV文件")
        print("💡 请在data目录中放置WAV文件进行演示")
        return False
    
    print(f"📁 使用演示文件: {demo_file}")
    
    # 进行共振峰分析
    result = analyze_resonance_peaks_only(
        wav_file_path=demo_file,
        min_prominence=6.0,    # 6dB突出度阈值
        min_distance=10.0,     # 10Hz最小间隔
        max_freq=2000         # 分析0-2000Hz
    )
    
    if result['success']:
        print("\n✅ 基础共振峰分析演示完成！")
        return True
    else:
        print(f"❌ 分析失败: {result.get('error', '未知错误')}")
        return False


def demo_advanced_resonance_analysis():
    """
    演示高级共振峰分析功能（自定义参数）
    """
    print("\n🎯 演示2: 高级共振峰分析（自定义参数）")
    print("=" * 60)
    
    demo_file = find_demo_wav_file()
    if not demo_file:
        return False
    
    print(f"📁 使用演示文件: {demo_file}")
    
    # 创建分析器
    analyzer = SpectrumAnalyzer(target_freq_resolution=0.01)
    
    # 先进行基础频谱分析
    result = analyzer.analyze_wav_file(demo_file, max_freq=2000)
    
    if not result['success']:
        print(f"❌ 频谱分析失败: {result.get('error', '未知错误')}")
        return False
    
    # 尝试不同的共振峰检测参数
    print("\n🔬 测试不同的共振峰检测参数:")
    
    test_configs = [
        {"name": "严格模式", "prominence": 8.0, "distance": 15.0},
        {"name": "标准模式", "prominence": 6.0, "distance": 10.0}, 
        {"name": "宽松模式", "prominence": 4.0, "distance": 5.0}
    ]
    
    for config in test_configs:
        print(f"\n--- {config['name']} ---")
        resonance_result = analyzer.detect_resonance_peaks(
            result['frequencies'], result['spl_db'],
            min_prominence=config['prominence'],
            min_distance=config['distance'],
            max_peaks=15
        )
        
        peaks = resonance_result['resonance_peaks']
        stats = resonance_result['statistics']
        
        print(f"检测到 {stats['total_peaks']} 个共振峰")
        if stats['total_peaks'] > 0:
            print(f"频率范围: {stats['frequency_range'][0]:.1f} - {stats['frequency_range'][1]:.1f} Hz")
            print(f"平均频率: {stats['mean_frequency']:.1f} Hz")
    
    print("\n✅ 高级共振峰分析演示完成！")
    return True


def demo_comprehensive_with_resonance():
    """
    演示综合分析中的共振峰功能
    """
    print("\n🎯 演示3: 综合分析中的共振峰功能")
    print("=" * 60)
    
    demo_file = find_demo_wav_file()
    if not demo_file:
        return False
    
    print(f"📁 使用演示文件: {demo_file}")
    
    # 进行完整的综合分析（包含共振峰）
    result = quick_analyze(
        wav_file_path=demo_file,
        comprehensive=True,     # 启用综合分析
        auto_subdir=True       # 自动创建子目录
    )
    
    if result['success']:
        print("\n📈 分析结果汇总:")
        print(f"   文件: {result['filename']}")
        print(f"   时长: {result['duration']:.2f} 秒")
        print(f"   采样率: {result['sample_rate']:,} Hz")
        
        # 显示共振峰信息
        if 'resonance_peaks' in result and result['resonance_peaks']:
            resonance_stats = result['resonance_peaks']['statistics']
            peaks = result['resonance_peaks']['resonance_peaks']
            
            print(f"\n🎯 共振峰特征:")
            print(f"   检测到: {resonance_stats['total_peaks']} 个共振峰")
            
            if resonance_stats['total_peaks'] > 0:
                print(f"   频率分布: {resonance_stats['frequency_range'][0]:.1f} - {resonance_stats['frequency_range'][1]:.1f} Hz")
                print(f"   声压级分布: {resonance_stats['spl_range'][0]:.1f} - {resonance_stats['spl_range'][1]:.1f} dB SPL")
                
                # 显示前5个最强的共振峰
                sorted_peaks = sorted(peaks, key=lambda x: x['peak_spl'], reverse=True)
                print(f"\n   🏆 前5个最强共振峰:")
                print(f"   {'排名':<4} {'频率(Hz)':<10} {'声压级(dB)':<12}")
                print("   " + "-" * 30)
                for i, peak in enumerate(sorted_peaks[:5]):
                    print(f"   {i+1:<4} {peak['center_frequency']:<10.1f} {peak['peak_spl']:<12.1f}")
        
        print("\n✅ 综合分析演示完成！")
        return True
    else:
        print(f"❌ 综合分析失败: {result.get('error', '未知错误')}")
        return False


def demo_resonance_visualization():
    """
    演示共振峰可视化功能说明
    """
    print("\n🎯 演示4: 共振峰可视化功能")
    print("=" * 60)
    
    print("📊 共振峰分析图表包含以下内容:")
    print()
    print("1️⃣ 主频谱图 (左上大图):")
    print("   - 蓝色曲线: 完整频谱")
    print("   - 红色圆点: 检测到的共振峰")
    print("   - 黄色标注: 前5个最强峰值的详细信息")
    print()
    print("2️⃣ 峰值分布直方图 (左下):")
    print("   - 显示共振峰在频率轴上的分布密度")
    print("   - 帮助识别频率集中区域")
    print()
    print("3️⃣ 峰值强度分析 (右下):")
    print("   - 气泡图：频率 vs 声压级") 
    print("   - 气泡大小表示峰值重要性")
    print("   - 颜色表示声压级强度")
    print()
    print("📁 生成的文件:")
    print("   - *_resonance_peaks.png - 专门的共振峰分析图")
    print("   - *_comprehensive_analysis.png - 四合一综合分析图")
    print("   - *_frequency_spectrum.png - 标准频谱图")


def main():
    """
    主演示函数
    """
    print("🎵 共振峰分析功能演示")
    print("=" * 80)
    print("本演示将展示声学信号共振峰检测和分析的完整功能")
    print()
    
    # 检查数据目录
    if not os.path.exists("data"):
        print("⚠️  注意: 未找到data目录")
        print("💡 建议: 在data目录中放置WAV文件以获得最佳演示效果")
        print()
    
    success_count = 0
    
    # 运行各个演示
    demos = [
        demo_basic_resonance_analysis,
        demo_advanced_resonance_analysis, 
        demo_comprehensive_with_resonance,
        demo_resonance_visualization
    ]
    
    for demo_func in demos:
        try:
            if demo_func():
                success_count += 1
        except Exception as e:
            print(f"❌ 演示过程中发生错误: {e}")
        finally:
            print()
    
    # 总结
    print("🎉 演示完成总结")
    print("=" * 80)
    print(f"✅ 成功完成演示: {success_count}/{len(demos)}")
    print()
    print("🔍 共振峰分析的核心价值:")
    print("   • 自动识别建筑结构的共振频率")
    print("   • 精确提取中心频率和峰值声压级")
    print("   • 量化分析声学放大效应")
    print("   • 为建筑声学设计提供科学依据")
    print()
    print("📊 输出数据的实际应用:")
    print("   • 中心频率(Hz): 建筑共振的特征频率")
    print("   • 峰值声压级(dB): 该频率上的声音放大强度")
    print("   • 突出度(dB): 峰值相对于周围频率的显著程度")
    print("   • 频率分布: 多个共振频率的分布特性")
    print()
    print("🎯 使用建议:")
    print("   • 对于古建筑: 使用较低的突出度阈值(4-6dB)")
    print("   • 对于现代建筑: 使用较高的突出度阈值(6-8dB)")
    print("   • 频率间隔: 根据建筑尺度调整(5-15Hz)")
    print()
    
    if success_count > 0:
        print("📁 查看生成的图表文件了解详细的可视化分析结果")
        print("🔬 可以通过调整检测参数来适应不同的分析需求")


if __name__ == "__main__":
    main()
