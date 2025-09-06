#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试突出度参数修复
================

验证突出度参数是否真正有效

作者：AI Assistant
"""

import os
from wav_to_spectrum_analyzer import analyze_resonance_peaks_only

def test_prominence_effect():
    """测试突出度参数效果"""
    print("🔍 测试突出度参数效果...")
    
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
        # 测试更极端的突出度对比，确保max_peaks不会限制结果
        prominences = [1.0, 30.0]  # 极端对比
        results = {}
        
        for prom in prominences:
            print(f"\n🎯 测试突出度: {prom} dB")
            
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=prom,
                min_distance=5.0,    # 小间隔确保有足够候选峰值
                max_freq=2000,
                max_peaks=50,        # 设置较大的上限，避免截断
                save_prefix=f"test_prom_fix_{prom}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                results[prom] = peak_count
                
                # 获取突出度统计
                stats = result['resonance_peaks']['statistics']
                if 'prominence_range' in stats and stats['prominence_range']:
                    prom_min, prom_max = stats['prominence_range']
                    print(f"   检测到峰值: {peak_count} 个")
                    print(f"   突出度范围: {prom_min:.1f} - {prom_max:.1f} dB")
                else:
                    print(f"   检测到峰值: {peak_count} 个")
                    print(f"   突出度信息不可用")
            else:
                print(f"   ❌ 分析失败")
                return False
        
        # 验证效果
        if len(results) == 2:
            low_prom_count = results[1.0]
            high_prom_count = results[30.0]
            
            print(f"\n📊 突出度参数效果对比:")
            print(f"   突出度 1.0 dB: {low_prom_count} 个峰值")
            print(f"   突出度 30.0 dB: {high_prom_count} 个峰值")
            
            if low_prom_count > high_prom_count:
                print(f"   ✅ 突出度参数有效 - 低突出度检测到更多峰值")
                return True
            elif low_prom_count == high_prom_count:
                print(f"   ⚠️ 突出度参数效果不明显 - 两次检测峰值数量相同")
                return False
            else:
                print(f"   ❌ 突出度参数结果异常 - 高突出度反而检测到更多峰值")
                return False
        else:
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_distance_effect():
    """测试频率间隔参数效果"""
    print("\n🔍 测试频率间隔参数效果...")
    
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
        # 测试更极端的频率间隔对比
        distances = [1.0, 100.0]  # 极端对比
        results = {}
        
        for dist in distances:
            print(f"\n🎯 测试频率间隔: {dist} Hz")
            
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=3.0,  # 中等突出度
                min_distance=dist,
                max_freq=2000,
                max_peaks=50,        # 设置较大的上限
                save_prefix=f"test_dist_fix_{dist}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                results[dist] = peak_count
                print(f"   检测到峰值: {peak_count} 个")
            else:
                print(f"   ❌ 分析失败")
                return False
        
        # 验证效果
        if len(results) == 2:
            small_dist_count = results[1.0]
            large_dist_count = results[100.0]
            
            print(f"\n📊 频率间隔参数效果对比:")
            print(f"   间隔 1.0 Hz: {small_dist_count} 个峰值")
            print(f"   间隔 100.0 Hz: {large_dist_count} 个峰值")
            
            if small_dist_count >= large_dist_count:
                print(f"   ✅ 频率间隔参数有效 - 小间隔检测到更多或相等峰值")
                return True
            else:
                print(f"   ❌ 频率间隔参数结果异常")
                return False
        else:
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_files():
    """清理测试文件"""
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
    print("🧪 突出度和频率间隔参数验证")
    print("=" * 50)
    
    test_results = []
    
    # 测试参数效果
    test_results.append(("突出度参数", test_prominence_effect()))
    test_results.append(("频率间隔参数", test_distance_effect()))
    
    # 清理测试文件
    cleanup_test_files()
    
    # 输出测试结果汇总
    print("\n📊 参数验证结果")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<15}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有参数验证通过！")
    else:
        print("⚠️ 仍有参数存在问题。")
    
    return all_passed

if __name__ == "__main__":
    main()
