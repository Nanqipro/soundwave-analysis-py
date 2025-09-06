#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度突出度参数分析
================

彻底分析突出度参数无效的根本原因

作者：AI Assistant
"""

import os
import numpy as np
from scipy.signal import find_peaks
from wav_to_spectrum_analyzer import SpectrumAnalyzer, analyze_resonance_peaks_only

def deep_prominence_analysis():
    """深度分析突出度参数的问题"""
    print("🔍 深度分析突出度参数问题...")
    
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
        # 获取原始频谱数据
        analyzer = SpectrumAnalyzer()
        result = analyzer.analyze_wav_file(test_file, max_freq=2000)
        
        if not result['success']:
            print("❌ 分析失败")
            return False
        
        frequencies = result['frequencies']
        spl_db = result['spl_db']
        freq_resolution = frequencies[1] - frequencies[0]
        
        print(f"📊 基础数据:")
        print(f"   频率范围: {frequencies[0]:.3f} - {frequencies[-1]:.1f} Hz")
        print(f"   声压级范围: {spl_db.min():.1f} - {spl_db.max():.1f} dB SPL")
        print(f"   声压级统计: 中位数={np.median(spl_db):.1f}, 标准差={np.std(spl_db):.1f}")
        
        # 当前的高度阈值
        min_height = np.median(spl_db) + 0.5 * np.std(spl_db)
        print(f"   当前高度阈值: {min_height:.1f} dB")
        
        # 1. 分析不同突出度的真实效果（不用高度阈值）
        print(f"\n🎯 分析突出度参数真实效果（无高度限制）:")
        prominences = [1.0, 5.0, 10.0, 20.0, 30.0]
        no_height_results = {}
        
        for prom in prominences:
            peak_indices, peak_properties = find_peaks(
                spl_db,
                prominence=prom,  # 只用突出度，不用高度
                distance=max(1, int(10.0 / freq_resolution))
            )
            
            no_height_results[prom] = len(peak_indices)
            if len(peak_indices) > 0:
                actual_prominences = peak_properties['prominences']
                print(f"   突出度≥{prom}dB: {len(peak_indices)}个峰值, "
                      f"实际突出度范围: {actual_prominences.min():.1f}-{actual_prominences.max():.1f}dB")
            else:
                print(f"   突出度≥{prom}dB: 0个峰值")
        
        # 2. 分析当前方法的效果（带高度阈值）
        print(f"\n🎯 分析当前方法效果（带高度阈值）:")
        current_results = {}
        
        for prom in prominences:
            peak_indices, peak_properties = find_peaks(
                spl_db,
                height=min_height,   # 使用当前的高度阈值
                prominence=prom,
                distance=max(1, int(10.0 / freq_resolution))
            )
            
            current_results[prom] = len(peak_indices)
            if len(peak_indices) > 0:
                actual_prominences = peak_properties['prominences']
                print(f"   突出度≥{prom}dB(带高度): {len(peak_indices)}个峰值, "
                      f"实际突出度范围: {actual_prominences.min():.1f}-{actual_prominences.max():.1f}dB")
            else:
                print(f"   突出度≥{prom}dB(带高度): 0个峰值")
        
        # 3. 尝试更宽松的高度阈值
        print(f"\n🎯 尝试更宽松的高度阈值:")
        loose_height = np.median(spl_db) - 0.5 * np.std(spl_db)  # 更宽松
        print(f"   更宽松的高度阈值: {loose_height:.1f} dB")
        
        loose_results = {}
        for prom in prominences:
            peak_indices, peak_properties = find_peaks(
                spl_db,
                height=loose_height,   # 更宽松的高度阈值
                prominence=prom,
                distance=max(1, int(10.0 / freq_resolution))
            )
            
            loose_results[prom] = len(peak_indices)
            if len(peak_indices) > 0:
                actual_prominences = peak_properties['prominences']
                print(f"   突出度≥{prom}dB(宽松): {len(peak_indices)}个峰值, "
                      f"实际突出度范围: {actual_prominences.min():.1f}-{actual_prominences.max():.1f}dB")
            else:
                print(f"   突出度≥{prom}dB(宽松): 0个峰值")
        
        # 4. 分析结果差异
        print(f"\n📊 结果对比分析:")
        print(f"{'突出度':<8} {'无高度':<8} {'当前方法':<10} {'宽松高度':<10}")
        print("-" * 40)
        
        for prom in prominences:
            print(f"{prom:<8.1f} {no_height_results[prom]:<8} {current_results[prom]:<10} {loose_results[prom]:<10}")
        
        # 判断哪种方法有效
        no_height_unique = len(set(no_height_results.values()))
        current_unique = len(set(current_results.values()))
        loose_unique = len(set(loose_results.values()))
        
        print(f"\n🔍 效果分析:")
        print(f"   无高度阈值: {no_height_unique} 种不同结果 {'✅ 有效' if no_height_unique > 1 else '❌ 无效'}")
        print(f"   当前方法: {current_unique} 种不同结果 {'✅ 有效' if current_unique > 1 else '❌ 无效'}")
        print(f"   宽松高度: {loose_unique} 种不同结果 {'✅ 有效' if loose_unique > 1 else '❌ 无效'}")
        
        return {
            'no_height_effective': no_height_unique > 1,
            'current_effective': current_unique > 1,
            'loose_effective': loose_unique > 1,
            'no_height_results': no_height_results,
            'current_results': current_results,
            'loose_results': loose_results
        }
        
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_optimized_method():
    """测试优化后的方法"""
    print("\n🚀 测试优化方法...")
    
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
        # 使用极端的突出度值进行测试
        prominences = [1.0, 30.0]  # 极端对比
        results = {}
        
        for prom in prominences:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=prom,
                min_distance=10.0,
                max_freq=2000,
                max_peaks=100,  # 足够大的值
                save_prefix=f"optimized_test_prom_{prom}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                results[prom] = peak_count
                print(f"   突出度 {prom} dB: {peak_count} 个峰值")
            else:
                print(f"   ❌ 突出度 {prom} 测试失败")
                return False
        
        # 验证效果
        if len(set(results.values())) > 1:
            print("✅ 极端值测试：突出度参数有效")
            return True
        else:
            print("❌ 极端值测试：突出度参数仍然无效")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def main():
    """主分析函数"""
    print("🐛 突出度参数深度分析")
    print("=" * 60)
    
    # 深度分析
    analysis_result = deep_prominence_analysis()
    
    if analysis_result:
        # 测试优化方法
        optimized_result = test_optimized_method()
        
        # 清理测试文件
        print("\n🧹 清理测试文件...")
        try:
            if os.path.exists("ana_res"):
                test_files = [f for f in os.listdir("ana_res") if f.startswith("optimized_test_")]
                for file in test_files:
                    file_path = os.path.join("ana_res", file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                
                # 清理子目录
                for subdir in os.listdir("ana_res"):
                    subdir_path = os.path.join("ana_res", subdir)
                    if os.path.isdir(subdir_path):
                        test_files_sub = [f for f in os.listdir(subdir_path) if f.startswith("optimized_test_")]
                        for file in test_files_sub:
                            file_path = os.path.join(subdir_path, file)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                
                print("✅ 清理完成")
        except Exception as e:
            print(f"⚠️ 清理时发生错误: {e}")
        
        # 提供修复建议
        print("\n🔧 修复建议:")
        if analysis_result['no_height_effective']:
            print("✅ 突出度参数本身有效，问题在于高度阈值")
            if not analysis_result['current_effective']:
                print("💡 建议：移除或大幅放宽高度阈值限制")
            if analysis_result['loose_effective']:
                print("💡 建议：采用更宽松的高度阈值计算方法")
        else:
            print("❌ 突出度参数本身可能有问题，需要更深入调查")
    
    return analysis_result

if __name__ == "__main__":
    main()
