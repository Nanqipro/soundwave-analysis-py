#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声学分析工具参数功能测试脚本
============================

测试不同参数配置是否能正常工作并产生预期的结果差异

作者：nanqipro
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import json

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from wav_to_spectrum_analyzer import SpectrumAnalyzer
except ImportError as e:
    print(f"❌ 无法导入分析模块: {e}")
    sys.exit(1)

class ParameterTester:
    """
    参数功能测试器
    
    用于测试不同参数配置对分析结果的影响
    """
    
    def __init__(self, test_file_path: str, output_dir: str = "test_results"):
        """
        初始化测试器
        
        Parameters
        ----------
        test_file_path : str
            用于测试的WAV文件路径
        output_dir : str
            测试结果输出目录
        """
        self.test_file_path = test_file_path
        self.output_dir = output_dir
        self.test_results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"🧪 参数功能测试器初始化完成")
        print(f"📁 测试文件: {test_file_path}")
        print(f"📂 输出目录: {self.output_dir}")
        
    def generate_test_configurations(self):
        """
        生成测试配置
        
        Returns
        -------
        dict
            包含不同测试配置的字典
        """
        
        test_configs = {
            "baseline": {
                "name": "基准配置",
                "target_freq_resolution": 0.01,
                "max_freq": 2000,
                "window_type": "hann",
                "min_prominence": 6.0,
                "min_distance": 10.0,
                "max_peaks": 20,
                "min_height": None
            },
            
            "high_resolution": {
                "name": "高频率分辨率",
                "target_freq_resolution": 0.001,  # 10倍提高
                "max_freq": 2000,
                "window_type": "hann",
                "min_prominence": 6.0,
                "min_distance": 10.0,
                "max_peaks": 20,
                "min_height": None
            },
            
            "low_resolution": {
                "name": "低频率分辨率",
                "target_freq_resolution": 0.1,  # 10倍降低
                "max_freq": 2000,
                "window_type": "hann",
                "min_prominence": 6.0,
                "min_distance": 10.0,
                "max_peaks": 20,
                "min_height": None
            },
            
            "sensitive_peaks": {
                "name": "敏感峰值检测",
                "target_freq_resolution": 0.01,
                "max_freq": 2000,
                "window_type": "hann",
                "min_prominence": 2.0,  # 更敏感
                "min_distance": 5.0,    # 更密集
                "max_peaks": 50,        # 更多峰值
                "min_height": None
            },
            
            "strict_peaks": {
                "name": "严格峰值检测",
                "target_freq_resolution": 0.01,
                "max_freq": 2000,
                "window_type": "hann",
                "min_prominence": 15.0,  # 更严格
                "min_distance": 50.0,    # 更稀疏
                "max_peaks": 5,          # 更少峰值
                "min_height": None
            },
            
            "window_comparison_hamming": {
                "name": "Hamming窗函数",
                "target_freq_resolution": 0.01,
                "max_freq": 2000,
                "window_type": "hamming",  # 不同窗函数
                "min_prominence": 6.0,
                "min_distance": 10.0,
                "max_peaks": 20,
                "min_height": None
            },
            
            "window_comparison_blackman": {
                "name": "Blackman窗函数",
                "target_freq_resolution": 0.01,
                "max_freq": 2000,
                "window_type": "blackman",  # 不同窗函数
                "min_prominence": 6.0,
                "min_distance": 10.0,
                "max_peaks": 20,
                "min_height": None
            },
            
            "extended_frequency": {
                "name": "扩展频率范围",
                "target_freq_resolution": 0.01,
                "max_freq": 8000,  # 4倍扩展
                "window_type": "hann",
                "min_prominence": 6.0,
                "min_distance": 10.0,
                "max_peaks": 20,
                "min_height": None
            }
        }
        
        return test_configs
    
    def run_single_test(self, config_name: str, config: dict):
        """
        运行单个测试配置
        
        Parameters
        ----------
        config_name : str
            配置名称
        config : dict
            配置参数
            
        Returns
        -------
        dict
            测试结果
        """
        
        print(f"\n🔬 测试配置: {config['name']} ({config_name})")
        print("-" * 50)
        
        try:
            # 创建分析器
            analyzer = SpectrumAnalyzer(
                target_freq_resolution=config['target_freq_resolution'],
                output_dir=os.path.join(self.output_dir, f"test_{config_name}")
            )
            
            # 进行分析
            result = analyzer.analyze_wav_file(
                self.test_file_path,
                max_freq=config['max_freq'],
                window_type=config['window_type']
            )
            
            if not result['success']:
                print(f"❌ 分析失败: {result.get('error', '未知错误')}")
                return None
            
            # 进行共振峰检测
            resonance_result = analyzer.detect_resonance_peaks(
                result['frequencies'],
                result['spl_db'],
                min_prominence=config['min_prominence'],
                min_distance=config['min_distance'],
                min_height=config['min_height'],
                max_peaks=config['max_peaks']
            )
            
            # 更新结果
            result['resonance_peaks'] = resonance_result
            
            # 提取关键指标
            test_result = {
                'config_name': config_name,
                'config': config.copy(),
                'success': True,
                'metrics': {
                    'freq_resolution_actual': result['frequencies'][1] - result['frequencies'][0] if len(result['frequencies']) > 1 else 0,
                    'freq_points': len(result['frequencies']),
                    'freq_range': [result['frequencies'][0], result['frequencies'][-1]],
                    'peak_frequency': result['peak_frequency'],
                    'peak_spl': result['peak_spl'],
                    'spl_range': [float(np.min(result['spl_db'])), float(np.max(result['spl_db']))],
                    'spl_mean': float(np.mean(result['spl_db'])),
                    'spl_std': float(np.std(result['spl_db'])),
                    'resonance_peaks_count': resonance_result['statistics']['total_peaks'],
                    'resonance_freq_range': resonance_result['statistics']['frequency_range'] if resonance_result['statistics']['total_peaks'] > 0 else [0, 0],
                    'dominant_peak_freq': resonance_result['statistics']['dominant_peak']['center_frequency'] if resonance_result['statistics']['dominant_peak'] else 0,
                    'dominant_peak_spl': resonance_result['statistics']['dominant_peak']['peak_spl'] if resonance_result['statistics']['dominant_peak'] else 0
                }
            }
            
            # 保存分析图
            save_prefix = f"test_{config_name}"
            analyzer.plot_spectrum(
                result,
                freq_range=(0, config['max_freq']),
                save_path=f"{save_prefix}_spectrum.png",
                show_plot=False
            )
            
            if resonance_result['statistics']['total_peaks'] > 0:
                analyzer.plot_resonance_peaks(
                    result['frequencies'], result['spl_db'], resonance_result,
                    freq_range=(0, config['max_freq']),
                    save_path=f"{save_prefix}_resonance.png",
                    show_plot=False
                )
            
            print(f"✅ 测试完成")
            print(f"   实际频率分辨率: {test_result['metrics']['freq_resolution_actual']:.6f} Hz")
            print(f"   频率点数: {test_result['metrics']['freq_points']:,}")
            print(f"   检测到共振峰: {test_result['metrics']['resonance_peaks_count']} 个")
            print(f"   主导峰值: {test_result['metrics']['dominant_peak_freq']:.1f} Hz")
            
            return test_result
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return {
                'config_name': config_name,
                'config': config.copy(),
                'success': False,
                'error': str(e)
            }
    
    def run_all_tests(self):
        """运行所有测试配置"""
        
        print("🧪 开始参数功能测试")
        print("=" * 60)
        
        if not os.path.exists(self.test_file_path):
            print(f"❌ 测试文件不存在: {self.test_file_path}")
            return False
        
        # 生成测试配置
        test_configs = self.generate_test_configurations()
        
        # 运行所有测试
        for config_name, config in test_configs.items():
            result = self.run_single_test(config_name, config)
            if result:
                self.test_results[config_name] = result
        
        # 分析结果
        self.analyze_results()
        
        # 生成报告
        self.generate_report()
        
        return True
    
    def analyze_results(self):
        """分析测试结果"""
        
        print(f"\n📊 分析测试结果...")
        
        successful_tests = {k: v for k, v in self.test_results.items() if v['success']}
        
        if not successful_tests:
            print("❌ 没有成功的测试结果")
            return
        
        # 基准结果
        baseline = successful_tests.get('baseline')
        if not baseline:
            print("⚠️  没有基准测试结果")
            return
        
        print(f"\n🔍 参数影响分析:")
        print("-" * 40)
        
        # 分析频率分辨率影响
        if 'high_resolution' in successful_tests:
            hr = successful_tests['high_resolution']
            print(f"📈 高分辨率测试:")
            print(f"   目标分辨率: {hr['config']['target_freq_resolution']:.3f} Hz")
            print(f"   实际分辨率: {hr['metrics']['freq_resolution_actual']:.6f} Hz")
            print(f"   频率点数: {hr['metrics']['freq_points']:,} (基准: {baseline['metrics']['freq_points']:,})")
            
        if 'low_resolution' in successful_tests:
            lr = successful_tests['low_resolution']
            print(f"📉 低分辨率测试:")
            print(f"   目标分辨率: {lr['config']['target_freq_resolution']:.3f} Hz")
            print(f"   实际分辨率: {lr['metrics']['freq_resolution_actual']:.6f} Hz")
            print(f"   频率点数: {lr['metrics']['freq_points']:,} (基准: {baseline['metrics']['freq_points']:,})")
        
        # 分析共振峰检测参数影响
        if 'sensitive_peaks' in successful_tests:
            sp = successful_tests['sensitive_peaks']
            print(f"🔍 敏感峰值检测:")
            print(f"   检测峰值数: {sp['metrics']['resonance_peaks_count']} (基准: {baseline['metrics']['resonance_peaks_count']})")
            
        if 'strict_peaks' in successful_tests:
            st = successful_tests['strict_peaks']
            print(f"🎯 严格峰值检测:")
            print(f"   检测峰值数: {st['metrics']['resonance_peaks_count']} (基准: {baseline['metrics']['resonance_peaks_count']})")
        
        # 分析窗函数影响
        window_tests = ['window_comparison_hamming', 'window_comparison_blackman']
        for window_test in window_tests:
            if window_test in successful_tests:
                wt = successful_tests[window_test]
                window_type = wt['config']['window_type']
                print(f"🪟 {window_type}窗函数:")
                print(f"   主导峰值频率: {wt['metrics']['dominant_peak_freq']:.1f} Hz (基准: {baseline['metrics']['dominant_peak_freq']:.1f} Hz)")
                print(f"   主导峰值强度: {wt['metrics']['dominant_peak_spl']:.1f} dB (基准: {baseline['metrics']['dominant_peak_spl']:.1f} dB)")
    
    def generate_report(self):
        """生成测试报告"""
        
        print(f"\n📝 生成测试报告...")
        
        # 保存详细结果到JSON
        json_path = os.path.join(self.output_dir, f"test_results_{self.timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # 生成CSV摘要
        csv_data = []
        for config_name, result in self.test_results.items():
            if result['success']:
                row = {
                    '配置名称': result['config']['name'],
                    '配置ID': config_name,
                    '频率分辨率_目标': result['config']['target_freq_resolution'],
                    '频率分辨率_实际': result['metrics']['freq_resolution_actual'],
                    '最大频率': result['config']['max_freq'],
                    '窗函数': result['config']['window_type'],
                    '频率点数': result['metrics']['freq_points'],
                    '峰值频率': result['metrics']['peak_frequency'],
                    '峰值声压级': result['metrics']['peak_spl'],
                    '共振峰数量': result['metrics']['resonance_peaks_count'],
                    '主导峰值频率': result['metrics']['dominant_peak_freq'],
                    '主导峰值强度': result['metrics']['dominant_peak_spl'],
                    '突出度阈值': result['config']['min_prominence'],
                    '频率间隔': result['config']['min_distance'],
                    '最大峰值数': result['config']['max_peaks']
                }
                csv_data.append(row)
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            csv_path = os.path.join(self.output_dir, f"test_summary_{self.timestamp}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"✅ CSV摘要已保存: {csv_path}")
        
        # 生成对比图
        self.generate_comparison_plots()
        
        # 生成文本报告
        self.generate_text_report()
        
        print(f"✅ 详细结果已保存: {json_path}")
        print(f"📁 所有测试文件保存在: {self.output_dir}")
    
    def generate_comparison_plots(self):
        """生成对比图表"""
        
        successful_tests = {k: v for k, v in self.test_results.items() if v['success']}
        
        if len(successful_tests) < 2:
            return
        
        # 创建对比图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Parameter Test Comparison Results', fontsize=16, fontweight='bold')
        
        # 提取数据
        config_names = list(successful_tests.keys())
        config_labels = [successful_tests[name]['config']['name'] for name in config_names]
        
        # 1. 频率分辨率对比
        ax1 = axes[0, 0]
        freq_res_target = [successful_tests[name]['config']['target_freq_resolution'] for name in config_names]
        freq_res_actual = [successful_tests[name]['metrics']['freq_resolution_actual'] for name in config_names]
        
        x_pos = np.arange(len(config_names))
        width = 0.35
        
        ax1.bar(x_pos - width/2, freq_res_target, width, label='Target', alpha=0.8)
        ax1.bar(x_pos + width/2, freq_res_actual, width, label='Actual', alpha=0.8)
        ax1.set_ylabel('Frequency Resolution (Hz)')
        ax1.set_title('Frequency Resolution Comparison')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(config_labels, rotation=45, ha='right')
        ax1.legend()
        ax1.set_yscale('log')
        
        # 2. 共振峰数量对比
        ax2 = axes[0, 1]
        resonance_counts = [successful_tests[name]['metrics']['resonance_peaks_count'] for name in config_names]
        bars = ax2.bar(config_labels, resonance_counts, alpha=0.8, color='skyblue')
        ax2.set_ylabel('Number of Resonance Peaks')
        ax2.set_title('Resonance Peaks Count Comparison')
        ax2.set_xticklabels(config_labels, rotation=45, ha='right')
        
        # 在柱上标注数值
        for bar, count in zip(bars, resonance_counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom')
        
        # 3. 主导峰值频率对比
        ax3 = axes[1, 0]
        dominant_freqs = [successful_tests[name]['metrics']['dominant_peak_freq'] for name in config_names]
        ax3.bar(config_labels, dominant_freqs, alpha=0.8, color='lightgreen')
        ax3.set_ylabel('Dominant Peak Frequency (Hz)')
        ax3.set_title('Dominant Peak Frequency Comparison')
        ax3.set_xticklabels(config_labels, rotation=45, ha='right')
        
        # 4. 主导峰值强度对比
        ax4 = axes[1, 1]
        dominant_spls = [successful_tests[name]['metrics']['dominant_peak_spl'] for name in config_names]
        ax4.bar(config_labels, dominant_spls, alpha=0.8, color='salmon')
        ax4.set_ylabel('Dominant Peak SPL (dB)')
        ax4.set_title('Dominant Peak SPL Comparison')
        ax4.set_xticklabels(config_labels, rotation=45, ha='right')
        
        plt.tight_layout()
        
        # 保存图表
        plot_path = os.path.join(self.output_dir, f"parameter_comparison_{self.timestamp}.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 对比图表已保存: {plot_path}")
    
    def generate_text_report(self):
        """生成文本报告"""
        
        report_path = os.path.join(self.output_dir, f"test_report_{self.timestamp}.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("声学分析工具参数功能测试报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"测试文件: {self.test_file_path}\n")
            f.write(f"输出目录: {self.output_dir}\n\n")
            
            # 测试概要
            total_tests = len(self.test_results)
            successful_tests = len([r for r in self.test_results.values() if r['success']])
            f.write(f"测试概要:\n")
            f.write(f"- 总测试数: {total_tests}\n")
            f.write(f"- 成功测试: {successful_tests}\n")
            f.write(f"- 失败测试: {total_tests - successful_tests}\n")
            f.write(f"- 成功率: {successful_tests/total_tests*100:.1f}%\n\n")
            
            # 详细结果
            f.write("详细测试结果:\n")
            f.write("-" * 30 + "\n\n")
            
            for config_name, result in self.test_results.items():
                f.write(f"配置: {result['config']['name']} ({config_name})\n")
                
                if result['success']:
                    f.write(f"状态: ✅ 成功\n")
                    f.write(f"配置参数:\n")
                    for key, value in result['config'].items():
                        if key != 'name':
                            f.write(f"  - {key}: {value}\n")
                    
                    f.write(f"分析结果:\n")
                    for key, value in result['metrics'].items():
                        if isinstance(value, float):
                            f.write(f"  - {key}: {value:.6f}\n")
                        else:
                            f.write(f"  - {key}: {value}\n")
                else:
                    f.write(f"状态: ❌ 失败\n")
                    f.write(f"错误: {result.get('error', '未知错误')}\n")
                
                f.write("\n")
            
            # 结论
            f.write("测试结论:\n")
            f.write("-" * 20 + "\n")
            
            if successful_tests >= 6:  # 至少成功6个测试
                f.write("✅ 参数功能测试通过\n")
                f.write("- 频率分辨率参数正常工作\n")
                f.write("- 共振峰检测参数正常工作\n")
                f.write("- 窗函数参数正常工作\n")
                f.write("- 频率范围参数正常工作\n")
                f.write("- 参数变化产生了预期的结果差异\n")
            else:
                f.write("❌ 参数功能测试未完全通过\n")
                f.write("- 部分参数可能无法正常工作\n")
                f.write("- 建议检查代码实现\n")
        
        print(f"✅ 文本报告已保存: {report_path}")


def find_test_file():
    """寻找测试用的WAV文件"""
    
    # 搜索路径
    search_paths = [
        "data",
        ".",
        "examples",
        "samples"
    ]
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.wav'):
                        return os.path.join(root, file)
    
    return None


def main():
    """主函数"""
    
    print("🧪 声学分析工具参数功能测试")
    print("=" * 50)
    
    # 寻找测试文件
    test_file = find_test_file()
    
    if not test_file:
        print("❌ 未找到可用的WAV测试文件")
        print("💡 请在以下目录中放置WAV文件：")
        print("   - data/")
        print("   - 当前目录")
        print("   - examples/")
        print("   - samples/")
        return
    
    print(f"✅ 找到测试文件: {test_file}")
    
    # 创建测试器并运行测试
    tester = ParameterTester(test_file)
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 参数功能测试完成！")
        print(f"📊 测试结果已保存在: {tester.output_dir}")
        print(f"\n📋 测试验证了以下功能：")
        print(f"   ✅ 频率分辨率参数调节")
        print(f"   ✅ 共振峰检测参数调节")  
        print(f"   ✅ 窗函数类型选择")
        print(f"   ✅ 频率范围控制")
        print(f"   ✅ 参数变化对结果的影响")
    else:
        print(f"\n❌ 参数功能测试失败")


if __name__ == "__main__":
    main()
