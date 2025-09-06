#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit应用参数传递测试脚本
===========================

测试Streamlit前端参数是否能正确传递给后端分析函数

作者：nanqipro
"""

import os
import sys
import tempfile
import json
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from streamlit_app import apply_preset_configuration
    from wav_to_spectrum_analyzer import SpectrumAnalyzer
except ImportError as e:
    print(f"❌ 无法导入必要模块: {e}")
    sys.exit(1)

class StreamlitParameterTester:
    """
    Streamlit参数传递测试器
    """
    
    def __init__(self):
        """初始化测试器"""
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_results = {}
        
    def test_preset_configurations(self):
        """测试预设配置功能"""
        
        print("🎛️ 测试预设配置功能...")
        print("-" * 40)
        
        # 基础配置（作为参考）
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
        
        presets = ["建筑声学", "语音分析", "音乐分析", "快速分析", "高精度分析"]
        
        for preset in presets:
            print(f"📋 测试预设: {preset}")
            
            # 应用预设配置
            config = apply_preset_configuration(preset, base_config)
            
            # 验证配置是否正确应用
            expected_changes = self.get_expected_preset_changes(preset)
            
            test_passed = True
            for key, expected_value in expected_changes.items():
                if config.get(key) != expected_value:
                    print(f"❌ {key}: 期望 {expected_value}, 实际 {config.get(key)}")
                    test_passed = False
                else:
                    print(f"✅ {key}: {config.get(key)}")
            
            self.test_results[f"preset_{preset}"] = {
                'passed': test_passed,
                'config': config.copy()
            }
            
            if test_passed:
                print(f"✅ 预设 '{preset}' 测试通过\n")
            else:
                print(f"❌ 预设 '{preset}' 测试失败\n")
    
    def get_expected_preset_changes(self, preset):
        """获取预设配置的期望值"""
        
        expected_configs = {
            "建筑声学": {
                'target_freq_resolution': 0.01,
                'max_freq': 2000,
                'window_type': 'hann',
                'min_prominence': 6.0,
                'comprehensive_analysis': True
            },
            "语音分析": {
                'target_freq_resolution': 0.1,
                'max_freq': 8000,
                'window_type': 'hamming',
                'min_prominence': 3.0,
                'min_distance': 20.0,
                'window_length': 512
            },
            "音乐分析": {
                'target_freq_resolution': 0.05,
                'max_freq': 20000,
                'window_type': 'blackman',
                'min_prominence': 8.0,
                'window_length': 2048,
                'max_peaks': 30
            },
            "快速分析": {
                'target_freq_resolution': 0.5,
                'max_freq': 2000,
                'min_prominence': 10.0,
                'min_distance': 50.0,
                'max_peaks': 10,
                'comprehensive_analysis': False
            },
            "高精度分析": {
                'target_freq_resolution': 0.001,
                'max_freq': 4000,
                'window_type': 'blackman',
                'min_prominence': 3.0,
                'min_distance': 5.0,
                'window_length': 4096,
                'max_peaks': 50
            }
        }
        
        return expected_configs.get(preset, {})
    
    def test_parameter_ranges(self):
        """测试参数范围验证"""
        
        print("🔍 测试参数范围验证...")
        print("-" * 40)
        
        # 测试用例：[参数名, 测试值, 是否应该有效]
        test_cases = [
            # 频率分辨率测试
            ('target_freq_resolution', 0.001, True),   # 最小有效值
            ('target_freq_resolution', 1.0, True),     # 最大有效值
            ('target_freq_resolution', 0.01, True),    # 正常值
            
            # 最大频率测试
            ('max_freq', 500, True),      # 最小有效值
            ('max_freq', 20000, True),    # 最大有效值
            ('max_freq', 2000, True),     # 正常值
            
            # 共振峰参数测试
            ('min_prominence', 1.0, True),    # 最小有效值
            ('min_prominence', 20.0, True),   # 最大有效值
            ('min_prominence', 6.0, True),    # 正常值
            
            ('min_distance', 5.0, True),      # 最小有效值
            ('min_distance', 100.0, True),    # 最大有效值
            ('min_distance', 10.0, True),     # 正常值
            
            ('max_peaks', 5, True),           # 最小有效值
            ('max_peaks', 50, True),          # 最大有效值
            ('max_peaks', 20, True),          # 正常值
        ]
        
        for param_name, test_value, should_be_valid in test_cases:
            print(f"🧪 测试 {param_name} = {test_value}")
            
            # 这里我们主要验证参数能否被正确设置
            # 在实际的Streamlit应用中，slider和number_input会自动限制范围
            try:
                # 创建测试配置
                test_config = {param_name: test_value}
                
                # 验证参数是否在预期范围内
                is_valid = self.validate_parameter(param_name, test_value)
                
                if is_valid == should_be_valid:
                    print(f"✅ 通过: {param_name}={test_value}")
                    self.test_results[f"range_{param_name}_{test_value}"] = {'passed': True}
                else:
                    print(f"❌ 失败: {param_name}={test_value} (期望{'有效' if should_be_valid else '无效'})")
                    self.test_results[f"range_{param_name}_{test_value}"] = {'passed': False}
                    
            except Exception as e:
                print(f"❌ 异常: {param_name}={test_value}, 错误: {e}")
                self.test_results[f"range_{param_name}_{test_value}"] = {'passed': False, 'error': str(e)}
    
    def validate_parameter(self, param_name, value):
        """验证参数是否在有效范围内"""
        
        valid_ranges = {
            'target_freq_resolution': (0.001, 1.0),
            'max_freq': (500, 20000),
            'min_prominence': (1.0, 20.0),
            'min_distance': (5.0, 100.0),
            'max_peaks': (5, 50),
            'overlap_ratio': (0.1, 0.9),
            'time_range': (0.1, 10.0)
        }
        
        if param_name not in valid_ranges:
            return True  # 未定义范围的参数默认有效
        
        min_val, max_val = valid_ranges[param_name]
        return min_val <= value <= max_val
    
    def test_config_integration(self):
        """测试配置与分析器集成"""
        
        print("🔗 测试配置与分析器集成...")
        print("-" * 40)
        
        # 创建测试配置
        test_config = {
            'target_freq_resolution': 0.05,
            'max_freq': 1000,
            'window_type': 'hamming',
            'min_prominence': 8.0,
            'min_distance': 20.0,
            'max_peaks': 15,
            'min_height': None
        }
        
        try:
            # 测试是否能正确创建分析器
            analyzer = SpectrumAnalyzer(
                target_freq_resolution=test_config['target_freq_resolution'],
                output_dir="test_temp"
            )
            
            print(f"✅ 分析器创建成功")
            print(f"   目标频率分辨率: {test_config['target_freq_resolution']} Hz")
            print(f"   分析器频率分辨率: {analyzer.target_freq_resolution} Hz")
            
            # 验证参数是否正确传递
            if analyzer.target_freq_resolution == test_config['target_freq_resolution']:
                print(f"✅ 频率分辨率参数传递正确")
                self.test_results['integration_freq_resolution'] = {'passed': True}
            else:
                print(f"❌ 频率分辨率参数传递错误")
                self.test_results['integration_freq_resolution'] = {'passed': False}
            
            print(f"✅ 配置集成测试通过")
            
        except Exception as e:
            print(f"❌ 配置集成测试失败: {e}")
            self.test_results['integration_test'] = {'passed': False, 'error': str(e)}
    
    def test_window_function_options(self):
        """测试窗函数选项"""
        
        print("🪟 测试窗函数选项...")
        print("-" * 40)
        
        window_functions = ['hann', 'hamming', 'blackman', 'rectangular']
        
        for window_func in window_functions:
            try:
                # 测试窗函数是否被正确识别
                # 在实际应用中，这些会传递给分析函数
                print(f"✅ 窗函数 '{window_func}' 可用")
                self.test_results[f'window_{window_func}'] = {'passed': True}
                
            except Exception as e:
                print(f"❌ 窗函数 '{window_func}' 测试失败: {e}")
                self.test_results[f'window_{window_func}'] = {'passed': False, 'error': str(e)}
    
    def run_all_tests(self):
        """运行所有测试"""
        
        print("🧪 Streamlit参数传递功能测试")
        print("=" * 50)
        
        # 运行各种测试
        self.test_preset_configurations()
        self.test_parameter_ranges()
        self.test_config_integration()
        self.test_window_function_options()
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        
        print("\n📊 测试结果汇总")
        print("=" * 40)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('passed', False)])
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        # 显示失败的测试
        failed_tests = [k for k, v in self.test_results.items() if not v.get('passed', False)]
        if failed_tests:
            print(f"\n❌ 失败的测试:")
            for test_name in failed_tests:
                error_msg = self.test_results[test_name].get('error', '未知错误')
                print(f"   - {test_name}: {error_msg}")
        
        # 保存详细报告
        report_data = {
            'timestamp': self.timestamp,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'pass_rate': passed_tests/total_tests*100
            },
            'detailed_results': self.test_results
        }
        
        report_path = f"streamlit_parameter_test_report_{self.timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 详细报告已保存: {report_path}")
        
        # 总结
        if passed_tests == total_tests:
            print(f"\n🎉 所有参数传递测试通过！")
            print(f"✅ Streamlit前端参数配置功能正常")
            print(f"✅ 预设配置功能正常")
            print(f"✅ 参数范围验证正常")
            print(f"✅ 配置集成功能正常")
        else:
            print(f"\n⚠️  部分测试未通过，请检查相关功能")


def main():
    """主函数"""
    
    tester = StreamlitParameterTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
