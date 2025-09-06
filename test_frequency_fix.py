#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试频率修复效果
==============

验证频率数组的负值问题是否已修复

作者：AI Assistant
"""

import os
from wav_to_spectrum_analyzer import SpectrumAnalyzer

def test_frequency_fix():
    """测试频率修复"""
    print("🔍 测试频率数组修复...")
    
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
        
        # 测试不同最大频率设置
        max_freqs = [1000, 2000, 3000]
        
        for max_freq in max_freqs:
            print(f"\n🎯 测试最大频率: {max_freq} Hz")
            result = analyzer.analyze_wav_file(test_file, max_freq=max_freq)
            
            if result['success']:
                frequencies = result['frequencies']
                print(f"   频率数组长度: {len(frequencies)}")
                print(f"   最小频率: {frequencies.min():.3f} Hz")
                print(f"   最大频率: {frequencies.max():.3f} Hz")
                print(f"   频率步长: {frequencies[1] - frequencies[0]:.6f} Hz")
                print(f"   是否包含负频率: {'是' if (frequencies < 0).any() else '否'}")
                
                # 检查频率范围是否合理
                if frequencies.min() >= 0 and frequencies.max() <= max_freq + 1:
                    print(f"   ✅ 频率范围正常")
                else:
                    print(f"   ❌ 频率范围异常")
                    return False
            else:
                print(f"   ❌ 分析失败")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 频率修复验证")
    print("=" * 50)
    
    success = test_frequency_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 频率数组修复成功！")
    else:
        print("❌ 频率数组仍有问题。")
    
    return success

if __name__ == "__main__":
    main()
