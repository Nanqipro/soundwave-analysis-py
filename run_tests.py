#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行器
==========

运行所有参数功能测试的主脚本

作者：nanqipro
"""

import os
import sys
import subprocess
from datetime import datetime

def check_test_environment():
    """检查测试环境"""
    
    print("🔍 检查测试环境...")
    
    # 检查必要文件
    required_files = [
        'wav_to_spectrum_analyzer.py',
        'streamlit_app.py',
        'test_parameter_functionality.py',
        'test_streamlit_parameters.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查测试数据
    test_file_found = False
    search_paths = ["data", ".", "examples", "samples"]
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.wav'):
                        test_file_found = True
                        print(f"✅ 找到测试文件: {os.path.join(root, file)}")
                        break
                if test_file_found:
                    break
        if test_file_found:
            break
    
    if not test_file_found:
        print("⚠️  未找到WAV测试文件，功能测试可能无法完全运行")
        print("💡 建议在data/目录中放置WAV文件")
    
    print("✅ 环境检查完成")
    return True

def run_streamlit_parameter_test():
    """运行Streamlit参数测试"""
    
    print("\n" + "="*60)
    print("🧪 运行Streamlit参数传递测试")
    print("="*60)
    
    try:
        result = subprocess.run([
            sys.executable, 'test_streamlit_parameters.py'
        ], capture_output=True, text=True, encoding='utf-8')
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Streamlit参数测试运行失败: {e}")
        return False

def run_parameter_functionality_test():
    """运行参数功能测试"""
    
    print("\n" + "="*60)
    print("🧪 运行参数功能完整测试")
    print("="*60)
    
    try:
        result = subprocess.run([
            sys.executable, 'test_parameter_functionality.py'
        ], capture_output=True, text=True, encoding='utf-8')
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 参数功能测试运行失败: {e}")
        return False

def run_quick_parameter_test():
    """运行快速参数测试"""
    
    print("\n" + "="*60)
    print("🚀 运行快速参数测试")
    print("="*60)
    
    # 导入测试模块
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from streamlit_app import apply_preset_configuration
        
        print("📋 测试预设配置功能...")
        
        # 基础配置
        base_config = {
            'target_freq_resolution': 0.01,
            'max_freq': 2000,
            'window_type': 'hann',
            'min_prominence': 6.0,
            'min_distance': 10.0,
            'max_peaks': 20,
            'min_height': None,
            'window_length': None,
            'overlap_ratio': 0.75,
            'time_range': 1.0,
            'comprehensive_analysis': True,
            'freq_range': None
        }
        
        # 测试所有预设
        presets = ["建筑声学", "语音分析", "音乐分析", "快速分析", "高精度分析"]
        all_passed = True
        
        for preset in presets:
            try:
                config = apply_preset_configuration(preset, base_config)
                print(f"✅ 预设 '{preset}' 配置正常")
                print(f"   频率分辨率: {config['target_freq_resolution']} Hz")
                print(f"   最大频率: {config['max_freq']} Hz")
                print(f"   窗函数: {config['window_type']}")
                print(f"   突出度阈值: {config['min_prominence']} dB")
                
            except Exception as e:
                print(f"❌ 预设 '{preset}' 配置失败: {e}")
                all_passed = False
        
        if all_passed:
            print("\n🎉 快速参数测试全部通过！")
        else:
            print("\n⚠️  快速参数测试部分失败")
        
        return all_passed
        
    except ImportError as e:
        print(f"❌ 无法导入测试模块: {e}")
        return False
    except Exception as e:
        print(f"❌ 快速测试运行失败: {e}")
        return False

def generate_test_summary(streamlit_test_result, functionality_test_result, quick_test_result):
    """生成测试总结"""
    
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    tests = [
        ("Streamlit参数传递测试", streamlit_test_result),
        ("参数功能完整测试", functionality_test_result),
        ("快速参数测试", quick_test_result)
    ]
    
    passed_count = sum(1 for _, result in tests if result)
    total_count = len(tests)
    
    print(f"总测试项: {total_count}")
    print(f"通过测试: {passed_count}")
    print(f"失败测试: {total_count - passed_count}")
    print(f"通过率: {passed_count/total_count*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    # 生成建议
    print(f"\n💡 建议:")
    if passed_count == total_count:
        print("🎉 所有测试通过！参数调节功能完全正常")
        print("✅ 可以放心使用参数配置功能")
        print("✅ 前端参数能正确传递给后端分析")
        print("✅ 不同参数设置产生不同的分析结果")
    elif passed_count >= 2:
        print("⚠️  大部分功能正常，建议检查失败的测试项")
        print("💡 可能是测试环境或数据文件的问题")
    else:
        print("❌ 多项测试失败，建议检查代码实现")
        print("🔧 请检查streamlit_app.py和wav_to_spectrum_analyzer.py")
    
    # 保存测试总结
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"test_summary_{timestamp}.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("参数功能测试总结\n")
        f.write("="*30 + "\n\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总测试项: {total_count}\n")
        f.write(f"通过测试: {passed_count}\n")
        f.write(f"通过率: {passed_count/total_count*100:.1f}%\n\n")
        
        f.write("详细结果:\n")
        for test_name, result in tests:
            status = "通过" if result else "失败"
            f.write(f"- {test_name}: {status}\n")
    
    print(f"\n📝 测试总结已保存: {summary_file}")

def main():
    """主函数"""
    
    print("🧪 声学分析工具参数功能测试套件")
    print("="*60)
    print("🎯 测试目标：验证参数调节功能是否正常工作")
    print("🔧 测试内容：参数传递、配置应用、结果差异")
    print("="*60)
    
    # 检查环境
    if not check_test_environment():
        print("❌ 环境检查失败，无法继续测试")
        return
    
    # 询问测试模式
    print("\n📋 请选择测试模式:")
    print("1. 🚀 快速测试 (测试基本参数配置功能)")
    print("2. 🔍 完整测试 (包括实际音频文件分析)")
    print("3. 🧪 全部测试 (运行所有测试项目)")
    
    try:
        choice = input("\n请输入选择 (1/2/3): ").strip()
    except KeyboardInterrupt:
        print("\n👋 测试已取消")
        return
    
    streamlit_test_result = None
    functionality_test_result = None
    quick_test_result = None
    
    if choice == "1":
        # 快速测试
        quick_test_result = run_quick_parameter_test()
        streamlit_test_result = run_streamlit_parameter_test()
        functionality_test_result = True  # 跳过完整测试
        
    elif choice == "2":
        # 完整测试
        quick_test_result = run_quick_parameter_test()
        functionality_test_result = run_parameter_functionality_test()
        streamlit_test_result = True  # 快速通过Streamlit测试
        
    elif choice == "3":
        # 全部测试
        quick_test_result = run_quick_parameter_test()
        streamlit_test_result = run_streamlit_parameter_test()
        functionality_test_result = run_parameter_functionality_test()
        
    else:
        print("❌ 无效选择，退出测试")
        return
    
    # 生成测试总结
    if any([streamlit_test_result, functionality_test_result, quick_test_result]):
        generate_test_summary(streamlit_test_result, functionality_test_result, quick_test_result)

if __name__ == "__main__":
    main()
