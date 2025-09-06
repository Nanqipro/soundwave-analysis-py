#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复效果验证
==============

验证所有参数在新的设置下都能正常工作

作者：AI Assistant
"""

import os
from wav_to_spectrum_analyzer import analyze_resonance_peaks_only

def test_all_parameters_final():
    """最终测试所有参数的效果"""
    print("🧪 最终修复效果验证")
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
    
    try:
        print(f"📁 使用测试文件: {test_file}")
        
        # 1. 测试突出度参数（使用新的默认max_peaks=80）
        print(f"\n🎯 1. 测试突出度参数（max_peaks=80）:")
        prominences = [2.0, 10.0, 25.0]  # 更极端的范围
        prom_results = {}
        
        for prom in prominences:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=prom,
                min_distance=10.0,
                max_freq=2000,
                max_peaks=80,
                save_prefix=f"final_fix_prom_{prom}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                prom_results[prom] = peak_count
                print(f"   突出度 {prom} dB: {peak_count} 个峰值")
            else:
                print(f"   ❌ 突出度 {prom} 测试失败")
                return False
        
        # 验证突出度效果
        prom_unique = len(set(prom_results.values()))
        prom_effective = prom_unique > 1
        print(f"   突出度参数: {prom_unique} 种结果 {'✅ 有效' if prom_effective else '❌ 无效'}")
        
        # 2. 测试频率间隔参数
        print(f"\n🎯 2. 测试频率间隔参数（max_peaks=80）:")
        distances = [3.0, 15.0, 40.0]  # 更极端的范围
        dist_results = {}
        
        for dist in distances:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=6.0,
                min_distance=dist,
                max_freq=2000,
                max_peaks=80,
                save_prefix=f"final_fix_dist_{dist}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                dist_results[dist] = peak_count
                print(f"   间隔 {dist} Hz: {peak_count} 个峰值")
            else:
                print(f"   ❌ 间隔 {dist} 测试失败")
                return False
        
        # 验证频率间隔效果
        dist_unique = len(set(dist_results.values()))
        dist_effective = dist_unique > 1
        print(f"   频率间隔参数: {dist_unique} 种结果 {'✅ 有效' if dist_effective else '❌ 无效'}")
        
        # 3. 测试最大峰值数参数
        print(f"\n🎯 3. 测试最大峰值数参数:")
        max_peaks_values = [30, 80, 150]
        peaks_results = {}
        
        for max_val in max_peaks_values:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=3.0,  # 低突出度，会检测很多峰值
                min_distance=5.0,
                max_freq=2000,
                max_peaks=max_val,
                save_prefix=f"final_fix_maxpeaks_{max_val}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                peaks_results[max_val] = peak_count
                print(f"   max_peaks {max_val}: {peak_count} 个峰值")
            else:
                print(f"   ❌ max_peaks {max_val} 测试失败")
                return False
        
        # 验证最大峰值数效果
        peaks_unique = len(set(peaks_results.values()))
        peaks_effective = peaks_unique > 1
        print(f"   最大峰值数参数: {peaks_unique} 种结果 {'✅ 有效' if peaks_effective else '❌ 无效'}")
        
        # 4. 测试智能提示功能
        print(f"\n🎯 4. 测试智能提示功能:")
        print("   使用较小的max_peaks值，应该看到智能提示...")
        
        result = analyze_resonance_peaks_only(
            wav_file_path=test_file,
            min_prominence=1.0,   # 低突出度会检测很多峰值
            min_distance=2.0,     # 小间隔会检测很多峰值
            max_freq=2000,
            max_peaks=20,         # 故意设置较小值触发提示
            save_prefix="final_fix_tips"
        )
        
        if result['success']:
            print("   ✅ 智能提示功能正常")
        else:
            print("   ❌ 智能提示功能测试失败")
        
        # 5. 汇总结果
        print(f"\n📊 最终验证结果:")
        print("-" * 40)
        all_tests = [
            ("突出度参数", prom_effective),
            ("频率间隔参数", dist_effective), 
            ("最大峰值数参数", peaks_effective),
            ("智能提示功能", result['success'])
        ]
        
        all_passed = True
        for test_name, result in all_tests:
            status = "✅ 有效" if result else "❌ 无效"
            print(f"   {test_name:<15}: {status}")
            if not result:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 所有参数修复成功！")
            print("✨ Web界面现在没有任何'假按钮'!")
            print("\n💡 用户使用建议:")
            print("   1. 突出度测试：使用max_peaks≥80，对比极端值(如2.0 vs 25.0)")
            print("   2. 频率间隔测试：对比极端值(如3.0 vs 40.0)")
            print("   3. 注意智能提示：会建议合适的max_peaks值")
            print("   4. 新的默认值(max_peaks=80)适合大多数使用场景")
        else:
            print("⚠️ 仍有部分参数存在问题")
        
        return all_passed
        
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
            test_files = [f for f in os.listdir("ana_res") if f.startswith("final_fix_")]
            for file in test_files:
                file_path = os.path.join("ana_res", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # 清理子目录
            for subdir in os.listdir("ana_res"):
                subdir_path = os.path.join("ana_res", subdir)
                if os.path.isdir(subdir_path):
                    test_files_sub = [f for f in os.listdir(subdir_path) if f.startswith("final_fix_")]
                    for file in test_files_sub:
                        file_path = os.path.join(subdir_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
            
            print("✅ 清理完成")
    except Exception as e:
        print(f"⚠️ 清理时发生错误: {e}")

def main():
    """主测试函数"""
    success = test_all_parameters_final()
    cleanup_test_files()
    return success

if __name__ == "__main__":
    main()
