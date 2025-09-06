#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web界面参数功能测试脚本
=====================

测试所有Web界面中的参数调节功能是否真正有效

作者：AI Assistant
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# 导入分析模块
try:
    from wav_to_spectrum_analyzer import (
        SpectrumAnalyzer, 
        analyze_single_wav_file, 
        analyze_resonance_peaks_only
    )
except ImportError as e:
    print(f"❌ 无法导入分析模块: {e}")
    sys.exit(1)

def test_max_freq_parameter():
    """测试最大频率参数是否有效"""
    print("🔍 测试最大频率参数...")
    
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
    
    print(f"📁 使用测试文件: {test_file}")
    
    try:
        # 创建分析器
        analyzer = SpectrumAnalyzer()
        
        # 测试不同的最大频率设置
        test_freqs = [1000, 2000, 3000]
        results = {}
        
        for max_freq in test_freqs:
            print(f"   测试最大频率: {max_freq} Hz")
            result = analyzer.analyze_wav_file(test_file, max_freq=max_freq)
            
            if result['success']:
                max_analyzed_freq = result['frequencies'][-1]
                results[max_freq] = max_analyzed_freq
                print(f"   ✅ 实际最大分析频率: {max_analyzed_freq:.1f} Hz")
            else:
                print(f"   ❌ 分析失败")
                return False
        
        # 验证频率参数确实影响了分析范围
        freq_values = list(results.values())
        if len(set(freq_values)) > 1:
            print("✅ 最大频率参数正常工作 - 不同设置产生不同的分析范围")
            return True
        else:
            print("❌ 最大频率参数无效 - 所有设置产生相同的分析范围")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_comprehensive_parameter():
    """测试综合分析参数是否有效"""
    print("\n🔍 测试综合分析参数...")
    
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
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 测试启用综合分析
            print("   测试综合分析: 启用")
            result1 = analyze_single_wav_file(
                wav_file_path=test_file,
                max_freq=2000,
                comprehensive=True,
                save_prefix="test_comp_true",
                auto_subdir=False
            )
            
            # 测试禁用综合分析
            print("   测试综合分析: 禁用")
            result2 = analyze_single_wav_file(
                wav_file_path=test_file,
                max_freq=2000,
                comprehensive=False,
                save_prefix="test_comp_false",
                auto_subdir=False
            )
            
            if result1['success'] and result2['success']:
                # 检查生成的文件数量差异
                dir1_files = len([f for f in os.listdir("ana_res") if f.startswith("test_comp_true")])
                dir2_files = len([f for f in os.listdir("ana_res") if f.startswith("test_comp_false")])
                
                print(f"   启用综合分析生成文件数: {dir1_files}")
                print(f"   禁用综合分析生成文件数: {dir2_files}")
                
                if dir1_files > dir2_files:
                    print("✅ 综合分析参数正常工作 - 启用时生成更多分析文件")
                    return True
                else:
                    print("❌ 综合分析参数可能无效 - 文件数量无差异")
                    return False
            else:
                print("❌ 分析失败")
                return False
                
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_resonance_parameters():
    """测试共振峰检测参数是否有效"""
    print("\n🔍 测试共振峰检测参数...")
    
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
        # 测试不同的突出度设置
        print("   测试突出度参数...")
        prominences = [2.0, 6.0, 10.0]
        prominence_results = {}
        
        for prom in prominences:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=prom,
                min_distance=10.0,
                max_freq=2000,
                save_prefix=f"test_prom_{prom}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                prominence_results[prom] = peak_count
                print(f"   突出度 {prom} dB: 检测到 {peak_count} 个峰值")
        
        # 验证突出度参数的效果（一般来说，突出度越高，检测到的峰值越少）
        peak_counts = list(prominence_results.values())
        if len(set(peak_counts)) > 1:
            print("✅ 突出度参数正常工作 - 不同设置产生不同的峰值数量")
            prominence_ok = True
        else:
            print("❌ 突出度参数可能无效 - 所有设置产生相同的峰值数量")
            prominence_ok = False
        
        # 测试不同的频率间隔设置
        print("   测试频率间隔参数...")
        distances = [5.0, 10.0, 20.0]
        distance_results = {}
        
        for dist in distances:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=6.0,
                min_distance=dist,
                max_freq=2000,
                save_prefix=f"test_dist_{dist}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                distance_results[dist] = peak_count
                print(f"   间隔 {dist} Hz: 检测到 {peak_count} 个峰值")
        
        # 验证频率间隔参数的效果
        peak_counts = list(distance_results.values())
        if len(set(peak_counts)) > 1:
            print("✅ 频率间隔参数正常工作 - 不同设置产生不同的峰值数量")
            distance_ok = True
        else:
            print("❌ 频率间隔参数可能无效 - 所有设置产生相同的峰值数量")
            distance_ok = False
        
        return prominence_ok and distance_ok
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_max_peaks_parameter():
    """测试最大峰值数参数是否有效"""
    print("\n🔍 测试最大峰值数参数...")
    
    # 检查analyze_resonance_peaks_only函数是否支持max_peaks参数
    import inspect
    signature = inspect.signature(analyze_resonance_peaks_only)
    
    if 'max_peaks' in signature.parameters:
        print("✅ analyze_resonance_peaks_only函数支持max_peaks参数")
        return True
    else:
        print("❌ analyze_resonance_peaks_only函数不支持max_peaks参数")
        print("   这意味着Web界面中的'最大检测峰值数'滑块是无效的")
        return False

def cleanup_test_files():
    """清理测试生成的文件"""
    print("\n🧹 清理测试文件...")
    
    try:
        if os.path.exists("ana_res"):
            test_files = [f for f in os.listdir("ana_res") if f.startswith("test_")]
            for file in test_files:
                file_path = os.path.join("ana_res", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"✅ 清理了 {len(test_files)} 个测试文件")
    except Exception as e:
        print(f"⚠️ 清理测试文件时发生错误: {e}")

def main():
    """主测试函数"""
    print("🧪 Web界面参数功能测试")
    print("=" * 50)
    
    test_results = []
    
    # 测试各项参数
    test_results.append(("最大频率参数", test_max_freq_parameter()))
    test_results.append(("综合分析参数", test_comprehensive_parameter()))
    test_results.append(("共振峰检测参数", test_resonance_parameters()))
    test_results.append(("最大峰值数参数", test_max_peaks_parameter()))
    
    # 清理测试文件
    cleanup_test_files()
    
    # 输出测试结果汇总
    print("\n📊 测试结果汇总")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有参数测试通过！Web界面的所有调节功能都正常工作。")
    else:
        print("⚠️ 发现问题！某些参数调节功能可能无效，需要修复。")
    
    return all_passed

if __name__ == "__main__":
    main()
