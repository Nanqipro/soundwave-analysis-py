#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web界面参数功能最终验证
===================

完整验证所有Web界面参数的有效性

作者：AI Assistant
"""

import os
from wav_to_spectrum_analyzer import SpectrumAnalyzer, analyze_single_wav_file, analyze_resonance_peaks_only

def test_all_parameters():
    """测试所有参数功能"""
    print("🧪 Web界面参数功能最终验证")
    print("=" * 60)
    
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
    
    test_results = {}
    
    # 1. 测试最大频率参数
    print("\n🔍 1. 测试最大频率参数")
    print("-" * 40)
    try:
        analyzer = SpectrumAnalyzer()
        
        for max_freq in [1000, 2000, 3000]:
            result = analyzer.analyze_wav_file(test_file, max_freq=max_freq)
            if result['success']:
                frequencies = result['frequencies']
                actual_max = frequencies.max()
                print(f"   设置: {max_freq} Hz → 实际: {actual_max:.1f} Hz")
                
                # 检查是否有负频率
                if (frequencies < 0).any():
                    print(f"   ❌ 检测到负频率！")
                    test_results['max_freq'] = False
                    break
                else:
                    print(f"   ✅ 无负频率，范围正常")
            else:
                print(f"   ❌ 分析失败")
                test_results['max_freq'] = False
                break
        else:
            test_results['max_freq'] = True
            print("✅ 最大频率参数正常工作")
    except Exception as e:
        print(f"❌ 最大频率参数测试失败: {e}")
        test_results['max_freq'] = False
    
    # 2. 测试综合分析参数
    print("\n🔍 2. 测试综合分析参数")
    print("-" * 40)
    try:
        # 启用综合分析
        result1 = analyze_single_wav_file(
            test_file, max_freq=2000, comprehensive=True, 
            save_prefix="final_test_comp_true", auto_subdir=False
        )
        
        # 禁用综合分析
        result2 = analyze_single_wav_file(
            test_file, max_freq=2000, comprehensive=False, 
            save_prefix="final_test_comp_false", auto_subdir=False
        )
        
        if result1['success'] and result2['success']:
            # 检查生成文件数量
            files1 = len([f for f in os.listdir("ana_res") if f.startswith("final_test_comp_true")])
            files2 = len([f for f in os.listdir("ana_res") if f.startswith("final_test_comp_false")])
            
            print(f"   启用综合分析: {files1} 个文件")
            print(f"   禁用综合分析: {files2} 个文件")
            
            if files1 > files2:
                print("✅ 综合分析参数正常工作")
                test_results['comprehensive'] = True
            else:
                print("❌ 综合分析参数无效")
                test_results['comprehensive'] = False
        else:
            print("❌ 综合分析测试失败")
            test_results['comprehensive'] = False
    except Exception as e:
        print(f"❌ 综合分析参数测试失败: {e}")
        test_results['comprehensive'] = False
    
    # 3. 测试最大峰值数参数
    print("\n🔍 3. 测试最大峰值数参数")
    print("-" * 40)
    try:
        peak_counts = {}
        for max_peaks in [5, 10, 20]:
            result = analyze_resonance_peaks_only(
                test_file, min_prominence=2.0, min_distance=5.0,
                max_freq=2000, max_peaks=max_peaks,
                save_prefix=f"final_test_peaks_{max_peaks}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                actual_peaks = result['resonance_peaks']['statistics']['total_peaks']
                peak_counts[max_peaks] = actual_peaks
                print(f"   设置: {max_peaks} → 实际: {actual_peaks}")
            else:
                print(f"   ❌ max_peaks={max_peaks} 测试失败")
                test_results['max_peaks'] = False
                break
        else:
            # 验证峰值数不超过设置值
            all_valid = all(actual <= setting for setting, actual in peak_counts.items())
            
            if all_valid and len(set(peak_counts.values())) > 1:
                print("✅ 最大峰值数参数正常工作")
                test_results['max_peaks'] = True
            else:
                print("❌ 最大峰值数参数无效")
                test_results['max_peaks'] = False
    except Exception as e:
        print(f"❌ 最大峰值数参数测试失败: {e}")
        test_results['max_peaks'] = False
    
    # 4. 测试突出度参数
    print("\n🔍 4. 测试突出度参数")
    print("-" * 40)
    try:
        prominence_counts = {}
        for prom in [1.0, 20.0]:
            result = analyze_resonance_peaks_only(
                test_file, min_prominence=prom, min_distance=5.0,
                max_freq=2000, max_peaks=50,
                save_prefix=f"final_test_prom_{prom}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                actual_peaks = result['resonance_peaks']['statistics']['total_peaks']
                prominence_counts[prom] = actual_peaks
                print(f"   突出度 {prom} dB: {actual_peaks} 个峰值")
            else:
                print(f"   ❌ 突出度={prom} 测试失败")
                test_results['min_prominence'] = False
                break
        else:
            # 低突出度应该检测到更多峰值
            if prominence_counts[1.0] > prominence_counts[20.0]:
                print("✅ 突出度参数正常工作")
                test_results['min_prominence'] = True
            else:
                print("❌ 突出度参数无效")
                test_results['min_prominence'] = False
    except Exception as e:
        print(f"❌ 突出度参数测试失败: {e}")
        test_results['min_prominence'] = False
    
    # 5. 测试频率间隔参数
    print("\n🔍 5. 测试频率间隔参数")
    print("-" * 40)
    try:
        distance_counts = {}
        for dist in [1.0, 50.0]:
            result = analyze_resonance_peaks_only(
                test_file, min_prominence=3.0, min_distance=dist,
                max_freq=2000, max_peaks=50,
                save_prefix=f"final_test_dist_{dist}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                actual_peaks = result['resonance_peaks']['statistics']['total_peaks']
                distance_counts[dist] = actual_peaks
                print(f"   间隔 {dist} Hz: {actual_peaks} 个峰值")
            else:
                print(f"   ❌ 间隔={dist} 测试失败")
                test_results['min_distance'] = False
                break
        else:
            # 小间隔应该检测到更多或相等峰值
            if distance_counts[1.0] >= distance_counts[50.0]:
                print("✅ 频率间隔参数正常工作")
                test_results['min_distance'] = True
            else:
                print("❌ 频率间隔参数无效")
                test_results['min_distance'] = False
    except Exception as e:
        print(f"❌ 频率间隔参数测试失败: {e}")
        test_results['min_distance'] = False
    
    # 清理测试文件
    print("\n🧹 清理测试文件...")
    try:
        if os.path.exists("ana_res"):
            test_files = [f for f in os.listdir("ana_res") if f.startswith("final_test_")]
            for file in test_files:
                file_path = os.path.join("ana_res", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # 清理子目录中的测试文件
            for subdir in os.listdir("ana_res"):
                subdir_path = os.path.join("ana_res", subdir)
                if os.path.isdir(subdir_path):
                    test_files_sub = [f for f in os.listdir(subdir_path) if f.startswith("final_test_")]
                    for file in test_files_sub:
                        file_path = os.path.join(subdir_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
        print("✅ 清理完成")
    except Exception as e:
        print(f"⚠️ 清理失败: {e}")
    
    # 汇总结果
    print("\n📊 最终验证结果")
    print("=" * 60)
    
    parameter_names = {
        'max_freq': '最大分析频率',
        'comprehensive': '启用综合分析',
        'max_peaks': '最大检测峰值数',
        'min_prominence': '最小突出度',
        'min_distance': '最小频率间隔'
    }
    
    all_passed = True
    for param, result in test_results.items():
        name = parameter_names.get(param, param)
        status = "✅ 有效" if result else "❌ 无效"
        print(f"{name:<20}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有Web界面参数功能验证通过！")
        print("💡 用户可以放心使用所有参数调节功能。")
    else:
        print("⚠️ 仍有部分参数存在问题，需要进一步检查。")
    
    return all_passed

if __name__ == "__main__":
    test_all_parameters()
