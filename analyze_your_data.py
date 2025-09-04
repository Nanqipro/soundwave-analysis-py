#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析您实际数据的专用脚本
=======================

专门用于处理data目录中的WAV音频文件
包含完整的数据分析流程和结果可视化

数据结构：
- data/S1R1/, S1R2/, S1R3/ (第一声源位置)
- data/S2R4/, S2R5/, S2R6/ (第二声源位置)
- 每个目录包含：record1.wav, record2.wav, record3.wav, 混响时间.txt

功能：
- WAV文件自动识别和加载
- 批量信号分析
- 共振频率识别
- 结果对比和可视化
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from signal_analysis import SignalAnalyzer
from typing import Dict, List, Tuple
import pandas as pd


def load_reverberation_data(txt_file_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    加载混响时间数据
    
    Parameters
    ----------
    txt_file_path : str
        混响时间.txt文件路径
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        频率数组和混响时间数组
    """
    try:
        # 读取数据（跳过表头，使用制表符分隔）
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 解析频率行
        freq_line = lines[0].strip().split('\t')
        frequencies = []
        for freq_str in freq_line[1:]:  # 跳过"频率"标题
            if freq_str.endswith('Hz'):
                freq_val = float(freq_str.replace('Hz', ''))
                frequencies.append(freq_val)
        
        # 解析平均值行
        avg_line = lines[-1].strip().split('\t')  # 最后一行是平均值
        rt_values = []
        for val_str in avg_line[1:]:  # 跳过"平均"标题
            try:
                rt_val = float(val_str)
                rt_values.append(rt_val)
            except ValueError:
                break
                
        return np.array(frequencies), np.array(rt_values)
        
    except Exception as e:
        print(f"❌ 读取混响时间数据失败 {txt_file_path}: {e}")
        return np.array([]), np.array([])


def analyze_single_directory(data_dir: str) -> Dict:
    """
    分析单个数据目录
    
    Parameters
    ---------- 
    data_dir : str
        数据目录路径 (如 data/S1R1)
        
    Returns
    -------
    Dict
        分析结果字典
    """
    print(f"\n📁 分析目录: {os.path.basename(data_dir)}")
    print("-" * 40)
    
    results = {
        'directory': data_dir,
        'wav_files': [],
        'analyses': [],
        'reverberation_data': None
    }
    
    # 查找WAV文件
    wav_files = glob.glob(os.path.join(data_dir, "*.wav"))
    wav_files.sort()
    
    if not wav_files:
        print("❌ 未找到WAV文件")
        return results
        
    print(f"📄 发现 {len(wav_files)} 个WAV文件")
    
    # 分析每个WAV文件
    for i, wav_file in enumerate(wav_files):
        filename = os.path.basename(wav_file)
        print(f"\n🎵 分析 {filename}...")
        
        try:
            # 创建分析器
            analyzer = SignalAnalyzer()
            
            # 加载WAV数据
            analyzer.load_data_from_wav(wav_file, max_duration=2.0)  # 最多2秒
            
            # 执行分析（不显示图形）
            analyzer.analyze_all(show_plots=False)
            
            # 保存分析结果
            analysis_result = {
                'file': wav_file,
                'filename': filename,
                'analyzer': analyzer,
                'success': True
            }
            
            results['analyses'].append(analysis_result)
            print(f"✅ {filename} 分析完成")
            
        except Exception as e:
            print(f"❌ {filename} 分析失败: {e}")
            analysis_result = {
                'file': wav_file,
                'filename': filename,
                'analyzer': None,
                'success': False,
                'error': str(e)
            }
            results['analyses'].append(analysis_result)
    
    # 加载混响时间数据
    rt_file = os.path.join(data_dir, "混响时间.txt")
    if os.path.exists(rt_file):
        print(f"\n📊 加载混响时间数据...")
        frequencies, rt_values = load_reverberation_data(rt_file)
        if len(frequencies) > 0:
            results['reverberation_data'] = {
                'frequencies': frequencies,
                'rt_values': rt_values
            }
            print(f"✅ 混响时间数据加载完成 ({len(frequencies)} 个频率点)")
        else:
            print(f"❌ 混响时间数据加载失败")
    else:
        print(f"⚠️  未找到混响时间.txt文件")
    
    return results


def analyze_all_data() -> Dict[str, Dict]:
    """
    分析data目录中的所有数据
    
    Returns
    -------
    Dict[str, Dict]
        所有目录的分析结果
    """
    print("🎯 开始分析所有数据...")
    print("=" * 60)
    
    if not os.path.exists("data"):
        print("❌ data目录不存在")
        return {}
    
    all_results = {}
    
    # 获取所有子目录
    subdirs = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
    subdirs.sort()
    
    if not subdirs:
        print("❌ data目录中未找到子目录")
        return {}
        
    print(f"📊 发现 {len(subdirs)} 个数据目录: {', '.join(subdirs)}")
    
    # 分析每个目录
    for subdir in subdirs:
        subdir_path = os.path.join("data", subdir)
        results = analyze_single_directory(subdir_path)
        all_results[subdir] = results
    
    return all_results


def create_comparison_plots(all_results: Dict[str, Dict]) -> None:
    """
    创建对比分析图表
    
    Parameters
    ----------
    all_results : Dict[str, Dict]
        所有分析结果
    """
    print(f"\n📈 生成对比分析图表...")
    
    # 过滤出成功的分析结果
    successful_results = {}
    for dir_name, results in all_results.items():
        successful_analyses = [a for a in results['analyses'] if a['success']]
        if successful_analyses:
            successful_results[dir_name] = {
                'analyses': successful_analyses,
                'reverberation_data': results['reverberation_data']
            }
    
    if not successful_results:
        print("❌ 没有成功的分析结果用于绘图")
        return
        
    # 设置图形布局
    n_dirs = len(successful_results)
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 频域对比图
    plt.subplot(2, 2, 1)
    colors = plt.cm.tab10(np.linspace(0, 1, n_dirs))
    
    for i, (dir_name, results) in enumerate(successful_results.items()):
        # 使用第一个成功的分析结果
        first_analysis = results['analyses'][0]
        analyzer = first_analysis['analyzer']
        
        # 计算频域数据
        N = len(analyzer.signal_data) - 1
        Y = np.fft.fft(analyzer.signal_data, N)
        mag = 2 / N * np.abs(Y)
        fn = np.arange(0, N//2 + 1) * analyzer.sampling_freq / N
        
        plt.plot(fn[:len(fn)//10], mag[:len(mag)//10], 
                color=colors[i], label=f'{dir_name}', alpha=0.8)
    
    plt.xlim([0, 2000])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('Frequency Domain Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. 混响时间对比图
    plt.subplot(2, 2, 2)
    
    for i, (dir_name, results) in enumerate(successful_results.items()):
        rt_data = results['reverberation_data']
        if rt_data:
            plt.plot(rt_data['frequencies'], rt_data['rt_values'], 
                    'o-', color=colors[i], label=f'{dir_name}', alpha=0.8)
    
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Reverberation Time (s)')
    plt.title('Reverberation Time Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')  # 对数刻度更好地显示混响时间差异
    
    # 3. 时域信号对比
    plt.subplot(2, 2, 3)
    
    for i, (dir_name, results) in enumerate(successful_results.items()):
        first_analysis = results['analyses'][0]
        analyzer = first_analysis['analyzer']
        
        # 显示前1000个点
        time_subset = analyzer.time_data[:1000]
        signal_subset = analyzer.signal_data[:1000]
        
        plt.plot(time_subset, signal_subset, 
                color=colors[i], label=f'{dir_name}', alpha=0.8)
    
    plt.xlabel('Time (s)')
    plt.ylabel('Signal Amplitude')
    plt.title('Time Domain Comparison (First 1000 Points)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 4. 频谱统计对比
    plt.subplot(2, 2, 4)
    
    peak_freqs = []
    peak_mags = []
    dir_names = []
    
    for dir_name, results in successful_results.items():
        first_analysis = results['analyses'][0]
        analyzer = first_analysis['analyzer']
        
        # 寻找频谱峰值
        N = len(analyzer.signal_data) - 1
        Y = np.fft.fft(analyzer.signal_data, N)
        mag = 2 / N * np.abs(Y[:N//2 + 1])
        fn = np.arange(0, N//2 + 1) * analyzer.sampling_freq / N
        
        # 在0-2000Hz范围内寻找峰值
        freq_mask = fn < 2000
        mag_subset = mag[freq_mask]
        freq_subset = fn[freq_mask]
        
        # 找到最大峰值
        peak_idx = np.argmax(mag_subset)
        peak_freq = freq_subset[peak_idx]
        peak_mag = mag_subset[peak_idx]
        
        peak_freqs.append(peak_freq)
        peak_mags.append(peak_mag)
        dir_names.append(dir_name)
    
    x_pos = np.arange(len(dir_names))
    bars = plt.bar(x_pos, peak_mags, color=colors[:len(dir_names)], alpha=0.8)
    
    # 在柱状图上标注频率
    for i, (freq, mag) in enumerate(zip(peak_freqs, peak_mags)):
        plt.text(i, mag + mag*0.05, f'{freq:.1f}Hz', 
                ha='center', va='bottom', fontsize=9)
    
    plt.xlabel('Data Directory')
    plt.ylabel('Peak Magnitude')
    plt.title('Main Peak Frequency & Magnitude')
    plt.xticks(x_pos, dir_names, rotation=45)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data_analysis_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"✅ 对比图表已保存: data_analysis_comparison.png")


def generate_analysis_report(all_results: Dict[str, Dict]) -> None:
    """
    生成分析报告
    
    Parameters
    ----------
    all_results : Dict[str, Dict]
        所有分析结果
    """
    print(f"\n📋 生成分析报告...")
    
    report_lines = [
        "# 古戏台声学数据分析报告",
        "=" * 50,
        f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # 总体统计
    total_dirs = len(all_results)
    total_wav_files = sum(len(r['analyses']) for r in all_results.values())
    successful_analyses = sum(len([a for a in r['analyses'] if a['success']]) 
                             for r in all_results.values())
    
    report_lines.extend([
        "## 数据概览",
        f"- 数据目录数量: {total_dirs}",
        f"- WAV文件总数: {total_wav_files}",
        f"- 成功分析数: {successful_analyses}",
        f"- 成功率: {successful_analyses/total_wav_files*100:.1f}%",
        ""
    ])
    
    # 各目录详细信息
    for dir_name, results in all_results.items():
        report_lines.extend([
            f"## 目录: {dir_name}",
            ""
        ])
        
        # WAV文件分析结果
        for analysis in results['analyses']:
            status = "✅" if analysis['success'] else "❌"
            report_lines.append(f"- {status} {analysis['filename']}")
            
            if analysis['success']:
                analyzer = analysis['analyzer']
                duration = analyzer.time_data[-1] if analyzer.time_data is not None else 0
                sample_points = len(analyzer.signal_data) if analyzer.signal_data is not None else 0
                report_lines.extend([
                    f"  - 数据时长: {duration:.3f} 秒",
                    f"  - 采样点数: {sample_points:,}",
                    f"  - 等效采样率: {analyzer.sampling_freq:,.0f} Hz"
                ])
        
        # 混响时间数据
        rt_data = results['reverberation_data']
        if rt_data:
            report_lines.extend([
                "- 📊 混响时间数据:",
                f"  - 频率范围: {rt_data['frequencies'].min():.0f} - {rt_data['frequencies'].max():.0f} Hz",
                f"  - 测量点数: {len(rt_data['frequencies'])}",
                f"  - RT值范围: {rt_data['rt_values'].min():.2f} - {rt_data['rt_values'].max():.2f} 秒"
            ])
        else:
            report_lines.append("- ⚠️  未找到混响时间数据")
            
        report_lines.append("")
    
    # 写入报告文件
    report_content = "\n".join(report_lines)
    
    with open('analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 分析报告已保存: analysis_report.md")
    
    # 同时打印到控制台
    print("\n" + "="*60)
    print("📋 分析报告摘要:")
    print("="*60)
    for line in report_lines[:15]:  # 显示前15行
        print(line)
    print("...")
    print(f"📄 完整报告请查看: analysis_report.md")


def main():
    """
    主函数：执行完整的数据分析流程
    """
    print("🎵 古戏台声学数据专项分析")
    print("=" * 80)
    
    # 检查数据目录
    if not os.path.exists("data"):
        print("❌ 未找到data目录，请确保数据文件在正确位置")
        return
    
    # 分析所有数据
    all_results = analyze_all_data()
    
    if not all_results:
        print("❌ 没有找到可分析的数据")
        return
    
    # 生成对比图表
    create_comparison_plots(all_results)
    
    # 生成分析报告
    generate_analysis_report(all_results)
    
    print(f"\n🎉 数据分析完成！")
    print(f"📊 生成的文件:")
    print(f"   - data_analysis_comparison.png (对比图表)")
    print(f"   - analysis_report.md (分析报告)")
    
    # 给出使用建议
    print(f"\n💡 使用建议:")
    print(f"   1. 查看对比图表了解不同位置的声学特性差异")
    print(f"   2. 分析频域图寻找共振频率峰值")
    print(f"   3. 对比混响时间数据验证分析结果") 
    print(f"   4. 根据需要调整分析参数进行进一步研究")


if __name__ == "__main__":
    main()
