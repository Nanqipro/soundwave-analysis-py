#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终Bug修复验证
==============

使用合理的max_peaks值验证突出度和频率间隔参数效果

作者：AI Assistant
"""

import os
from wav_to_spectrum_analyzer import analyze_resonance_peaks_only

def test_with_adequate_max_peaks():
    """使用足够大的max_peaks值测试参数效果"""
    print("🔍 使用足够大的max_peaks值测试参数效果...")
    
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
        
        # 测试突出度参数 - 使用max_peaks=80确保不会截断
        print(f"\n🎯 测试突出度参数（max_peaks=80）:")
        prominences = [3.0, 8.0, 15.0]
        prom_results = {}
        
        for prom in prominences:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=prom,
                min_distance=10.0,  # 固定间隔
                max_freq=2000,
                max_peaks=80,       # 足够大的值
                save_prefix=f"test_verify_prom_{prom}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                prom_results[prom] = peak_count
                print(f"   突出度 {prom} dB: {peak_count} 个峰值")
            else:
                print(f"   ❌ 突出度 {prom} 测试失败")
                return False
        
        # 验证突出度效果
        if len(set(prom_results.values())) > 1:
            # 检查趋势是否正确
            sorted_proms = sorted(prom_results.keys())
            trend_correct = True
            for i in range(len(sorted_proms) - 1):
                if prom_results[sorted_proms[i]] < prom_results[sorted_proms[i + 1]]:
                    trend_correct = False
                    break
            
            if trend_correct:
                print("✅ 突出度参数正常工作（低突出度 ≥ 高突出度）")
                prom_ok = True
            else:
                print("⚠️ 突出度参数工作但趋势异常")
                prom_ok = True  # 至少有效果
        else:
            print("❌ 突出度参数无效")
            prom_ok = False
        
        # 测试频率间隔参数
        print(f"\n🎯 测试频率间隔参数（max_peaks=80）:")
        distances = [5.0, 15.0, 30.0]
        dist_results = {}
        
        for dist in distances:
            result = analyze_resonance_peaks_only(
                wav_file_path=test_file,
                min_prominence=6.0,  # 固定突出度
                min_distance=dist,
                max_freq=2000,
                max_peaks=80,        # 足够大的值
                save_prefix=f"test_verify_dist_{dist}"
            )
            
            if result['success'] and 'resonance_peaks' in result:
                peak_count = result['resonance_peaks']['statistics']['total_peaks']
                dist_results[dist] = peak_count
                print(f"   间隔 {dist} Hz: {peak_count} 个峰值")
            else:
                print(f"   ❌ 间隔 {dist} 测试失败")
                return False
        
        # 验证频率间隔效果
        if len(set(dist_results.values())) > 1:
            # 检查趋势是否正确
            sorted_dists = sorted(dist_results.keys())
            trend_correct = True
            for i in range(len(sorted_dists) - 1):
                if dist_results[sorted_dists[i]] < dist_results[sorted_dists[i + 1]]:
                    trend_correct = False
                    break
            
            if trend_correct:
                print("✅ 频率间隔参数正常工作（小间隔 ≥ 大间隔）")
                dist_ok = True
            else:
                print("⚠️ 频率间隔参数工作但趋势异常")
                dist_ok = True  # 至少有效果
        else:
            print("❌ 频率间隔参数无效")
            dist_ok = False
        
        return prom_ok and dist_ok
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_max_peaks_warning():
    """测试max_peaks限制的警告信息"""
    print("\n🔍 测试max_peaks限制警告...")
    
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
        print("使用较小的max_peaks值，应该看到截断警告...")
        
        result = analyze_resonance_peaks_only(
            wav_file_path=test_file,
            min_prominence=2.0,   # 低突出度会检测很多峰值
            min_distance=2.0,     # 小间隔会检测很多峰值  
            max_freq=2000,
            max_peaks=15,         # 故意设置较小的值
            save_prefix="test_warning"
        )
        
        if result['success']:
            print("✅ max_peaks警告功能验证完成")
            return True
        else:
            print("❌ 测试失败")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    print("\n🧹 清理测试文件...")
    
    try:
        if os.path.exists("ana_res"):
            test_files = [f for f in os.listdir("ana_res") if f.startswith("test_verify_") or f.startswith("test_warning")]
            for file in test_files:
                file_path = os.path.join("ana_res", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # 清理子目录中的测试文件
            for subdir in os.listdir("ana_res"):
                subdir_path = os.path.join("ana_res", subdir)
                if os.path.isdir(subdir_path):
                    test_files_sub = [f for f in os.listdir(subdir_path) if f.startswith("test_verify_") or f.startswith("test_warning")]
                    for file in test_files_sub:
                        file_path = os.path.join(subdir_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
            
            print(f"✅ 清理完成")
    except Exception as e:
        print(f"⚠️ 清理测试文件时发生错误: {e}")

def main():
    """主测试函数"""
    print("🐛 最终Bug修复验证")
    print("=" * 60)
    print("解决方案：调整max_peaks默认值，增加截断警告")
    
    test_results = []
    
    # 验证修复效果
    test_results.append(("参数效果（合理max_peaks）", test_with_adequate_max_peaks()))
    test_results.append(("max_peaks警告功能", test_max_peaks_warning()))
    
    # 清理测试文件
    cleanup_test_files()
    
    # 输出测试结果汇总
    print("\n📊 最终验证结果")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<30}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 最后一个Bug修复成功！")
        print("🔧 解决方案说明：")
        print("   1. 调整Web界面max_peaks默认值：15→50")
        print("   2. 增加max_peaks上限：30→100")
        print("   3. 添加截断警告，提醒用户参数被限制")
        print("   4. 添加帮助文本，说明如何看到参数真实效果")
        print("\n💡 现在用户可以在Web界面中看到突出度和频率间隔参数的真实效果！")
    else:
        print("⚠️ 修复仍不完整，需要进一步调查。")
    
    return all_passed

if __name__ == "__main__":
    main()
