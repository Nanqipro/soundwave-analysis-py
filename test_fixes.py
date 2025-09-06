#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复后的参数功能
==================

测试修复后的Web界面参数是否正常工作

作者：AI Assistant
"""

import os
from wav_to_spectrum_analyzer import analyze_resonance_peaks_only

def test_max_peaks_fix():
    """测试最大峰值数参数修复"""
    print("🔍 测试最大峰值数参数修复...")
    
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
        # 测试不同的max_peaks设置
        test_peaks = [5, 10, 15]
        results = {}
        
        for max_peaks in test_peaks:
            print(f"   测试最大峰值数: {max_peaks}")
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=2.0,  # 降低突出度以确保有足够的峰值
                min_distance=5.0,    # 降低间隔以确保有足够的峰值
                max_freq=2000,
                max_peaks=max_peaks,
                save_prefix=f"test_maxpeaks_{max_peaks}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                results[max_peaks] = peak_count
                print(f"   ✅ 最大峰值数 {max_peaks}: 实际检测到 {peak_count} 个峰值")
            else:
                print(f"   ❌ 分析失败")
                return False
        
        # 验证max_peaks参数的效果
        success = True
        for max_peaks, actual_count in results.items():
            if actual_count > max_peaks:
                print(f"   ❌ 错误：设置最大{max_peaks}个峰值，但检测到{actual_count}个")
                success = False
            else:
                print(f"   ✅ 正确：设置最大{max_peaks}个峰值，检测到{actual_count}个")
        
        # 检查不同设置是否产生不同结果
        peak_counts = list(results.values())
        if len(set(peak_counts)) > 1:
            print("✅ 最大峰值数参数修复成功 - 不同设置产生不同的峰值数量")
            return success
        else:
            print("⚠️ 最大峰值数参数可能仍有问题 - 所有设置产生相同的峰值数量")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_resonance_parameters_detailed():
    """详细测试共振峰检测参数"""
    print("\n🔍 详细测试共振峰检测参数...")
    
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
        # 测试突出度参数，使用更极端的值
        print("   测试突出度参数（使用极端值）...")
        prominences = [1.0, 15.0]  # 更极端的对比
        prominence_results = {}
        
        for prom in prominences:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=prom,
                min_distance=5.0,
                max_freq=2000,
                max_peaks=30,  # 增加上限确保不被限制
                save_prefix=f"test_prom_extreme_{prom}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                prominence_results[prom] = peak_count
                print(f"   突出度 {prom} dB: 检测到 {peak_count} 个峰值")
        
        # 验证突出度效果（低突出度应该产生更多峰值）
        if len(prominence_results) == 2:
            low_prom_count = prominence_results[1.0]
            high_prom_count = prominence_results[15.0]
            
            if low_prom_count > high_prom_count:
                print("✅ 突出度参数工作正常 - 低突出度检测到更多峰值")
                prominence_ok = True
            elif low_prom_count == high_prom_count:
                print("⚠️ 突出度参数可能无效 - 产生相同峰值数量")
                prominence_ok = False
            else:
                print("⚠️ 突出度参数结果异常 - 高突出度反而检测到更多峰值")
                prominence_ok = False
        else:
            prominence_ok = False
        
        # 测试频率间隔参数
        print("   测试频率间隔参数（使用极端值）...")
        distances = [1.0, 50.0]  # 更极端的对比
        distance_results = {}
        
        for dist in distances:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=3.0,  # 使用中等突出度
                min_distance=dist,
                max_freq=2000,
                max_peaks=30,
                save_prefix=f"test_dist_extreme_{dist}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                distance_results[dist] = peak_count
                print(f"   间隔 {dist} Hz: 检测到 {peak_count} 个峰值")
        
        # 验证频率间隔效果（小间隔应该产生更多峰值）
        if len(distance_results) == 2:
            small_dist_count = distance_results[1.0]
            large_dist_count = distance_results[50.0]
            
            if small_dist_count >= large_dist_count:
                print("✅ 频率间隔参数工作正常 - 小间隔检测到更多或相等峰值")
                distance_ok = True
            else:
                print("⚠️ 频率间隔参数结果异常 - 大间隔反而检测到更多峰值")
                distance_ok = False
        else:
            distance_ok = False
        
        return prominence_ok and distance_ok
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
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
            
            # 清理子目录中的测试文件
            for subdir in os.listdir("ana_res"):
                subdir_path = os.path.join("ana_res", subdir)
                if os.path.isdir(subdir_path):
                    test_files_sub = [f for f in os.listdir(subdir_path) if f.startswith("test_")]
                    for file in test_files_sub:
                        file_path = os.path.join(subdir_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
            
            print(f"✅ 清理完成")
    except Exception as e:
        print(f"⚠️ 清理测试文件时发生错误: {e}")

def main():
    """主测试函数"""
    print("🧪 验证参数修复效果")
    print("=" * 50)
    
    test_results = []
    
    # 测试修复效果
    test_results.append(("最大峰值数参数修复", test_max_peaks_fix()))
    test_results.append(("共振峰检测参数详细测试", test_resonance_parameters_detailed()))
    
    # 清理测试文件
    cleanup_test_files()
    
    # 输出测试结果汇总
    print("\n📊 修复验证结果")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<25}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有修复验证通过！参数功能已修复。")
    else:
        print("⚠️ 仍有问题需要进一步修复。")
    
    return all_passed

if __name__ == "__main__":
    main()
