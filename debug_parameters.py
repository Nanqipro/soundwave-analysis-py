#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试参数功能的专门脚本
===================

专门调试突出度参数和最大频率参数的问题

作者：AI Assistant
"""

import os
import numpy as np
from wav_to_spectrum_analyzer import SpectrumAnalyzer

def debug_prominence_parameter():
    """调试突出度参数问题"""
    print("🔍 调试突出度参数...")
    
    # 寻找测试文件
    test_file = None
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith('.wav'):
                test_file = os.path.join(root, file)
                break
        if test_file:
            break
    
    if not test_file:
        print("❌ 未找到测试WAV文件")
        return False
    
    try:
        analyzer = SpectrumAnalyzer()
        
        # 首先获取频谱数据
        result = analyzer.analyze_wav_file(test_file, max_freq=2000)
        
        if not result['success']:
            print("❌ 分析失败")
            return False
        
        frequencies = result['frequencies']
        spl_db = result['spl_db']
        
        print(f"📊 基础数据:")
        print(f"   频率范围: {frequencies[0]:.3f} - {frequencies[-1]:.1f} Hz")
        print(f"   声压级范围: {spl_db.min():.1f} - {spl_db.max():.1f} dB SPL")
        
        # 直接调用scipy.signal.find_peaks测试突出度
        from scipy.signal import find_peaks
        
        # 计算频率分辨率
        freq_resolution = frequencies[1] - frequencies[0]
        min_distance_idx = max(1, int(10.0 / freq_resolution))  # 10Hz间隔
        
        # 自动计算高度阈值
        min_height = np.median(spl_db) + 1.5 * np.std(spl_db)
        print(f"   自动计算的最小高度: {min_height:.1f} dB")
        
        # 测试不同突出度
        prominences_to_test = [1.0, 5.0, 10.0, 15.0]
        
        for prom in prominences_to_test:
            print(f"\n🎯 测试突出度: {prom} dB")
            
            # 直接调用find_peaks
            peak_indices, peak_properties = find_peaks(
                spl_db,
                height=min_height,
                prominence=prom,
                distance=min_distance_idx
            )
            
            print(f"   检测到峰值数: {len(peak_indices)}")
            
            if len(peak_indices) > 0:
                peak_freqs = frequencies[peak_indices]
                peak_spls = spl_db[peak_indices]
                peak_proms = peak_properties['prominences']
                
                print(f"   频率范围: {peak_freqs.min():.1f} - {peak_freqs.max():.1f} Hz")
                print(f"   突出度范围: {peak_proms.min():.1f} - {peak_proms.max():.1f} dB")
                
                # 显示前5个峰值的详细信息
                print(f"   前5个峰值:")
                for i in range(min(5, len(peak_indices))):
                    print(f"     {i+1}. {peak_freqs[i]:.1f} Hz, {peak_spls[i]:.1f} dB, 突出度: {peak_proms[i]:.1f} dB")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_max_freq_parameter():
    """调试最大频率参数问题"""
    print("\n🔍 调试最大频率参数...")
    
    # 寻找测试文件
    test_file = None
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith('.wav'):
                test_file = os.path.join(root, file)
                break
        if test_file:
            break
    
    if not test_file:
        print("❌ 未找到测试WAV文件")
        return False
    
    try:
        analyzer = SpectrumAnalyzer()
        
        # 测试不同的最大频率设置
        max_freqs = [1000, 2000, 3000, None]
        
        for max_freq in max_freqs:
            print(f"\n🎯 测试最大频率: {max_freq}")
            
            # 直接分析文件
            result = analyzer.analyze_wav_file(test_file, max_freq=max_freq)
            
            if result['success']:
                frequencies = result['frequencies']
                print(f"   频率数组长度: {len(frequencies)}")
                print(f"   频率数组前5个值: {frequencies[:5]}")
                print(f"   频率数组后5个值: {frequencies[-5:]}")
                print(f"   最小频率: {frequencies.min():.3f} Hz")
                print(f"   最大频率: {frequencies.max():.3f} Hz")
                print(f"   频率步长: {frequencies[1] - frequencies[0]:.6f} Hz")
            else:
                print(f"   ❌ 分析失败: {result.get('error', '未知错误')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_spectrum_generation():
    """调试频谱生成过程"""
    print("\n🔍 调试频谱生成过程...")
    
    # 寻找测试文件
    test_file = None
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith('.wav'):
                test_file = os.path.join(root, file)
                break
        if test_file:
            break
    
    if not test_file:
        print("❌ 未找到测试WAV文件")
        return False
    
    try:
        analyzer = SpectrumAnalyzer()
        
        # 加载音频文件
        import scipy.io.wavfile
        sr, signal = scipy.io.wavfile.read(test_file)
        
        print(f"📊 音频文件信息:")
        print(f"   采样率: {sr} Hz")
        print(f"   信号长度: {len(signal)} 点")
        print(f"   时长: {len(signal) / sr:.3f} 秒")
        
        # 直接调用频谱分析方法
        frequencies, spl_db, phase_deg = analyzer.signal_to_spectrum(signal, sr)
        
        print(f"\n📈 原始频谱信息:")
        print(f"   频率数组长度: {len(frequencies)}")
        print(f"   频率范围: {frequencies[0]:.3f} - {frequencies[-1]:.1f} Hz")
        print(f"   频率步长: {frequencies[1] - frequencies[0]:.6f} Hz")
        print(f"   声压级范围: {spl_db.min():.1f} - {spl_db.max():.1f} dB SPL")
        
        # 测试频率截取
        max_freq = 2000
        freq_mask = frequencies <= max_freq
        print(f"\n🔧 应用频率截取 (max_freq={max_freq}):")
        print(f"   掩码数量: {freq_mask.sum()} / {len(freq_mask)}")
        
        filtered_frequencies = frequencies[freq_mask]
        filtered_spl = spl_db[freq_mask]
        
        print(f"   截取后频率范围: {filtered_frequencies[0]:.3f} - {filtered_frequencies[-1]:.1f} Hz")
        print(f"   截取后数组长度: {len(filtered_frequencies)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主调试函数"""
    print("🐛 参数功能调试")
    print("=" * 50)
    
    # 调试各项功能
    debug_spectrum_generation()
    debug_max_freq_parameter()
    debug_prominence_parameter()
    
    print("\n" + "=" * 50)
    print("🔧 调试完成！")

if __name__ == "__main__":
    main()
