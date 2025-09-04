#!/usr/bin/env python3
"""
简单的数据结构演示
================

快速展示Te数据的基本结构和格式
"""

import numpy as np

def show_te_data_structure():
    """展示Te数据的基本结构"""
    
    print("🎯 Te数据结构演示")
    print("=" * 50)
    
    # 创建示例Te数据
    # 模拟1毫秒的测量数据，1000个采样点
    time_points = 1000
    time_duration = 0.001  # 1毫秒
    
    # 时间列：从0到0.001秒
    time_col = np.linspace(0, time_duration, time_points)
    
    # 信号列：一个简单的衰减正弦波
    frequency = 440  # 440Hz (音乐中的A4)
    signal_col = np.sin(2 * np.pi * frequency * time_col) * np.exp(-1000 * time_col)
    
    # 组合成Te格式：N×2矩阵
    te_data = np.column_stack((time_col, signal_col))
    
    print(f"📊 Te数据基本信息：")
    print(f"   数据类型: {type(te_data)}")
    print(f"   数据形状: {te_data.shape}")
    print(f"   数据类型: {te_data.dtype}")
    
    print(f"\n📋 矩阵结构：")
    print(f"   Te是一个 {te_data.shape[0]}×{te_data.shape[1]} 的矩阵")
    print(f"   第1列 Te[:, 0]: 时间数据 (秒)")
    print(f"   第2列 Te[:, 1]: 信号数据 (任意单位)")
    
    print(f"\n🔢 数据范围：")
    print(f"   时间范围: {te_data[:, 0].min():.6f} ~ {te_data[:, 0].max():.6f} 秒")
    print(f"   信号范围: {te_data[:, 1].min():.6f} ~ {te_data[:, 1].max():.6f}")
    
    print(f"\n📝 前10行数据：")
    print("   索引    时间(秒)        信号值")
    print("   " + "-" * 35)
    for i in range(10):
        print(f"   {i:3d}    {te_data[i, 0]:10.6f}    {te_data[i, 1]:10.6f}")
    
    print(f"\n📝 最后5行数据：")
    print("   索引    时间(秒)        信号值")
    print("   " + "-" * 35)
    for i in range(-5, 0):
        idx = te_data.shape[0] + i
        print(f"   {idx:3d}    {te_data[i, 0]:10.6f}    {te_data[i, 1]:10.6f}")
    
    return te_data

def show_matlab_usage():
    """展示在MATLAB中如何使用Te数据"""
    
    print(f"\n🔧 在MATLAB代码中的使用：")
    print("=" * 50)
    
    print("📄 shipin.m 第6行关键代码：")
    print("   y = interp1(Te(:,1), Te(:,2), tt, 'linear');")
    print()
    print("🔍 代码解析：")
    print("   Te(:,1)  ← 使用Te的第1列作为原始时间轴")
    print("   Te(:,2)  ← 使用Te的第2列作为原始信号值")
    print("   tt       ← 新的统一时间轴 (0:Ts:1)")
    print("   'linear' ← 线性插值方法")
    print("   y        ← 插值后的统一采样信号")

def show_python_equivalent():
    """展示Python中的等效操作"""
    
    print(f"\n🐍 Python中的等效操作：")
    print("=" * 50)
    
    te_data = show_te_data_structure()
    
    # 模拟MATLAB的插值操作
    sampling_step = 1e-6  # 1微秒
    tt = np.arange(0, 0.001 + sampling_step, sampling_step)  # 新时间轴
    
    # 线性插值
    y = np.interp(tt, te_data[:, 0], te_data[:, 1])
    
    # 去直流分量
    y = y - np.mean(y)
    
    print("📊 处理结果：")
    print(f"   原始数据点数: {te_data.shape[0]}")
    print(f"   插值后数据点数: {len(y)}")
    print(f"   原始采样间隔: {(te_data[1, 0] - te_data[0, 0]) * 1e6:.1f} 微秒")
    print(f"   插值后采样间隔: {sampling_step * 1e6:.1f} 微秒")
    print(f"   直流分量: {np.mean(te_data[:, 1]):.6f}")

def show_file_formats():
    """展示不同文件格式的Te数据"""
    
    print(f"\n📁 不同文件格式中的Te数据：")
    print("=" * 50)
    
    te_data = show_te_data_structure()
    
    print("🔸 1. MATLAB .mat文件格式：")
    print("   文件: data样例.mat")
    print("   变量: Te")
    print("   结构: N×2 double数组")
    print("   读取: mat_data = loadmat('data样例.mat')")
    print("        te_data = mat_data['Te']")
    
    print("\n🔸 2. CSV文件格式：")
    print("   Time_s,Signal")
    print("   0.000000,0.125000") 
    print("   0.000001,0.128000")
    print("   ...")
    
    print("\n🔸 3. 文本文件格式 (制表符分隔)：")
    print("   Time(s)\\tSignal")
    print("   0.000000\\t0.125000")
    print("   0.000001\\t0.128000") 
    print("   ...")
    
    print("\n🔸 4. NumPy数组格式：")
    print("   time_array = np.array([0.000000, 0.000001, ...])")
    print("   signal_array = np.array([0.125000, 0.128000, ...])")
    print("   te_data = np.column_stack((time_array, signal_array))")

def main():
    """主函数"""
    
    print("🎵 声学信号分析 - 输入数据结构说明")
    print("=" * 80)
    
    # 展示Te数据结构
    te_data = show_te_data_structure()
    
    # 展示MATLAB使用方法
    show_matlab_usage()
    
    # 展示Python等效操作
    show_python_equivalent()
    
    # 展示文件格式
    show_file_formats()
    
    print(f"\n✅ 总结：")
    print("   📋 Te数据是一个N×2的矩阵")
    print("   ⏰ 第1列是时间数据（秒）")
    print("   📊 第2列是信号数据（任意单位）")
    print("   🔧 通过插值转换为统一采样")
    print("   📈 然后进行时域、频域、相位、时频分析")

if __name__ == "__main__":
    main()
