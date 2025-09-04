#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信号分析工具使用示例
==================

展示如何使用SignalAnalyzer类进行信号分析
包含完整的使用流程和最佳实践

功能演示:
- 数据加载和预处理
- 时域信号分析
- 频域FFT分析
- 相位分析
- 时频谱图分析
"""

try:
    from signal_analysis import SignalAnalyzer, create_sample_data
    import numpy as np
    import matplotlib.pyplot as plt
    print("✓ 所有依赖库导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请先安装依赖包: pip install -r requirements.txt")
    exit(1)


def demonstrate_basic_usage() -> None:
    """
    演示基本使用方法
    
    创建示例数据并进行完整的信号分析
    """
    print("\n=== 基本使用演示 ===")
    
    # 创建信号分析器
    analyzer = SignalAnalyzer()
    print("✓ 创建信号分析器实例")
    
    # 生成示例数据：混合频率信号
    print("✓ 生成示例数据（混合频率信号）...")
    t_sample, signal_sample = create_sample_data()
    
    # 加载数据
    analyzer.load_data_from_arrays(t_sample, signal_sample)
    print("✓ 数据加载完成")
    
    # 执行完整分析
    print("✓ 开始信号分析...")
    analyzer.analyze_all(show_plots=False)  # 不自动显示图形
    
    print("✓ 信号分析完成！")


def demonstrate_individual_plots() -> None:
    """
    演示单独绘制各种图形
    
    展示如何分别调用不同的绘图函数
    """
    print("\n=== 单独绘图演示 ===")
    
    analyzer = SignalAnalyzer()
    
    # 创建更复杂的测试信号
    print("✓ 生成复杂测试信号...")
    t = np.linspace(0, 1, 10000)
    
    # 多频率分量 + 噪声
    signal_data = (
        1.0 * np.sin(2 * np.pi * 50 * t) +      # 50Hz基频
        0.8 * np.sin(2 * np.pi * 150 * t) +     # 150Hz谐波
        0.6 * np.sin(2 * np.pi * 300 * t) +     # 300Hz谐波
        0.4 * np.sin(2 * np.pi * 500 * t) +     # 500Hz谐波
        0.2 * np.random.randn(len(t))           # 噪声
    )
    
    analyzer.load_data_from_arrays(t, signal_data)
    
    # 分别绘制各种图形
    print("✓ 绘制时域图...")
    analyzer.plot_time_domain(figure_num=1)
    
    print("✓ 绘制频域图...")
    analyzer.plot_frequency_domain(figure_num=2, freq_limit=1000)
    
    print("✓ 绘制相位图...")
    analyzer.plot_phase_domain(figure_num=3, freq_limit=1000)
    
    print("✓ 绘制时频图...")
    analyzer.plot_spectrogram(figure_num=4, freq_limit=800, nfft=2048)
    
    print("✓ 所有图形绘制完成！")


def demonstrate_data_formats() -> None:
    """
    演示不同数据格式的处理
    
    展示如何处理不同来源和格式的数据
    """
    print("\n=== 数据格式演示 ===")
    
    analyzer = SignalAnalyzer()
    
    # 演示1: 从CSV数据加载（模拟）
    print("✓ 演示CSV格式数据处理...")
    time_csv = np.linspace(0, 2, 2000)
    signal_csv = np.sin(2 * np.pi * 60 * time_csv) * np.exp(-time_csv)  # 衰减正弦波
    
    analyzer.load_data_from_arrays(time_csv, signal_csv)
    analyzer.plot_time_domain(figure_num=5)
    
    # 演示2: 脉冲响应信号
    print("✓ 演示脉冲响应信号...")
    analyzer2 = SignalAnalyzer()
    
    t_pulse = np.linspace(0, 1, 5000)
    # 模拟脉冲响应：多个衰减振荡
    pulse_response = (
        np.exp(-10 * t_pulse) * np.sin(2 * np.pi * 100 * t_pulse) +
        0.5 * np.exp(-20 * t_pulse) * np.sin(2 * np.pi * 250 * t_pulse) +
        0.3 * np.exp(-30 * t_pulse) * np.sin(2 * np.pi * 400 * t_pulse)
    )
    
    analyzer2.load_data_from_arrays(t_pulse, pulse_response)
    analyzer2.plot_frequency_domain(figure_num=6, freq_limit=800)
    
    print("✓ 数据格式演示完成！")


def demonstrate_parameter_tuning() -> None:
    """
    演示参数调优
    
    展示如何调整分析参数以获得最佳结果
    """
    print("\n=== 参数调优演示 ===")
    
    # 创建高采样率分析器
    high_freq_analyzer = SignalAnalyzer(sampling_step=1e-7)  # 10MHz采样率
    print(f"✓ 创建高采样率分析器 (采样频率: {high_freq_analyzer.sampling_freq:.0e} Hz)")
    
    # 生成高频信号
    t_high = np.linspace(0, 0.001, 10000)  # 1ms时长
    signal_high = (
        np.sin(2 * np.pi * 1000 * t_high) +   # 1kHz
        0.5 * np.sin(2 * np.pi * 5000 * t_high) +  # 5kHz
        0.3 * np.sin(2 * np.pi * 10000 * t_high)   # 10kHz
    )
    
    high_freq_analyzer.load_data_from_arrays(t_high, signal_high)
    
    # 使用不同参数绘制时频图
    print("✓ 使用不同参数绘制时频图...")
    
    # 高分辨率参数
    high_freq_analyzer.plot_spectrogram(
        figure_num=7, 
        freq_limit=15000, 
        nfft=4096
    )
    
    print("✓ 参数调优演示完成！")


def main() -> None:
    """
    主函数：运行所有演示
    """
    print("🎵 信号分析工具演示程序")
    print("=" * 50)
    
    try:
        # 基本使用演示
        demonstrate_basic_usage()
        
        # 单独绘图演示
        demonstrate_individual_plots()
        
        # 数据格式演示
        demonstrate_data_formats()
        
        # 参数调优演示
        demonstrate_parameter_tuning()
        
        print(f"\n🎉 演示程序运行完成！")
        print(f"📊 总共生成了 {len(plt.get_fignums())} 个图形")
        print("📖 请查看各个图形窗口了解分析结果")
        
        # 显示所有图形
        if len(plt.get_fignums()) > 0:
            print("\n💡 提示：关闭图形窗口后程序将结束")
            plt.show()
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
