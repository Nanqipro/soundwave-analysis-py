#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入数据结构示例和说明
===================

详细展示信号分析工具所需的输入数据格式和结构
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import savemat, loadmat
import pandas as pd


def create_sample_te_data() -> np.ndarray:
    """
    创建符合要求的Te数据示例
    
    Returns
    -------
    np.ndarray
        Te数据矩阵，形状为(N, 2)
        第一列：时间数据 (秒)
        第二列：信号数据 (电流/电压/声压等)
    """
    # 模拟声学测量数据
    # 时间范围：0-2秒，包含多个共振频率
    duration = 2.0  # 秒
    sample_rate = 44100  # Hz (音频采样率)
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 模拟古戏台的声学响应信号
    # 包含几个典型的共振频率成分
    signal = (
        # 基频及其谐波 (模拟戏曲基音)
        1.0 * np.sin(2 * np.pi * 220 * t) * np.exp(-0.5 * t) +  # A3 (220Hz)
        0.8 * np.sin(2 * np.pi * 330 * t) * np.exp(-0.8 * t) +  # E4 (330Hz)  
        0.6 * np.sin(2 * np.pi * 440 * t) * np.exp(-1.0 * t) +  # A4 (440Hz)
        0.4 * np.sin(2 * np.pi * 660 * t) * np.exp(-1.2 * t) +  # E5 (660Hz)
        
        # 低频共振 (模拟建筑结构共振)
        0.3 * np.sin(2 * np.pi * 98 * t) * np.exp(-0.3 * t) +   # G2 (98Hz)
        0.2 * np.sin(2 * np.pi * 147 * t) * np.exp(-0.4 * t) +  # D3 (147Hz)
        
        # 添加噪声模拟真实测量
        0.05 * np.random.randn(len(t))
    )
    
    # 组合成Te数据格式：N×2矩阵
    te_data = np.column_stack((t, signal))
    
    return te_data


def show_data_structure():
    """
    展示数据结构的详细信息
    """
    print("📊 输入数据结构详解")
    print("=" * 60)
    
    # 创建示例数据
    te_data = create_sample_te_data()
    
    print(f"🔍 Te数据基本信息：")
    print(f"   数据类型: {type(te_data)}")
    print(f"   数据维度: {te_data.shape}")
    print(f"   数据类型: {te_data.dtype}")
    print(f"   内存大小: {te_data.nbytes / 1024:.1f} KB")
    
    print(f"\n📋 数据结构说明：")
    print(f"   Te数据是一个 N×2 的二维数组")
    print(f"   第一列 Te[:, 0] : 时间数据 (单位: 秒)")
    print(f"   第二列 Te[:, 1] : 信号数据 (单位: 任意，如V、A、Pa等)")
    
    print(f"\n🔢 数据范围：")
    print(f"   时间范围: {te_data[:, 0].min():.6f} ~ {te_data[:, 0].max():.6f} 秒")
    print(f"   信号范围: {te_data[:, 1].min():.6f} ~ {te_data[:, 1].max():.6f}")
    
    print(f"\n📝 前10行数据示例：")
    print("   时间(秒)     信号值")
    print("   " + "-" * 25)
    for i in range(10):
        print(f"   {te_data[i, 0]:8.6f}   {te_data[i, 1]:8.6f}")
    
    return te_data


def demonstrate_data_formats():
    """
    演示不同的数据输入格式
    """
    print(f"\n📁 支持的数据格式：")
    print("=" * 60)
    
    te_data = create_sample_te_data()
    
    # 格式1：MATLAB .mat 文件
    print("🔸 格式1: MATLAB .mat文件")
    mat_file_path = "example_te_data.mat"
    savemat(mat_file_path, {'Te': te_data})
    print(f"   文件: {mat_file_path}")
    print(f"   变量名: Te")
    print(f"   使用方法: analyzer.load_data_from_mat('{mat_file_path}', 'Te')")
    
    # 验证读取
    loaded_data = loadmat(mat_file_path)
    print(f"   验证读取: Te形状 = {loaded_data['Te'].shape}")
    
    # 格式2：分离的时间和信号数组
    print(f"\n🔸 格式2: 分离的numpy数组")
    time_array = te_data[:, 0]
    signal_array = te_data[:, 1]
    print(f"   时间数组形状: {time_array.shape}")
    print(f"   信号数组形状: {signal_array.shape}")
    print(f"   使用方法: analyzer.load_data_from_arrays(time_array, signal_array)")
    
    # 格式3：CSV文件
    print(f"\n🔸 格式3: CSV文件 (需要额外处理)")
    csv_file_path = "example_te_data.csv"
    df = pd.DataFrame(te_data, columns=['Time_s', 'Signal'])
    df.to_csv(csv_file_path, index=False)
    print(f"   文件: {csv_file_path}")
    print(f"   列名: Time_s, Signal")
    print(f"   使用方法: df = pd.read_csv('{csv_file_path}')")
    print(f"            analyzer.load_data_from_arrays(df['Time_s'], df['Signal'])")
    
    # 格式4：文本文件
    print(f"\n🔸 格式4: 文本文件")
    txt_file_path = "example_te_data.txt"
    np.savetxt(txt_file_path, te_data, delimiter='\t', 
               header='Time(s)\tSignal', comments='')
    print(f"   文件: {txt_file_path}")
    print(f"   分隔符: Tab")
    print(f"   使用方法: data = np.loadtxt('{txt_file_path}', skiprows=1)")
    print(f"            analyzer.load_data_from_arrays(data[:, 0], data[:, 1])")


def analyze_existing_data_structure():
    """
    分析现有data目录中的数据结构
    """
    print(f"\n🗂️  现有数据目录分析：")
    print("=" * 60)
    
    print("📁 发现的数据类型：")
    print("   1. *.wav 文件 - 音频格式")
    print("      - 包含原始声音录音")
    print("      - 需要用音频库读取(如librosa, soundfile)")
    print("      - 采样率通常为44.1kHz或48kHz")
    
    print("   2. 混响时间.txt - 测量结果")
    print("      - 包含不同频率的混响时间数据")
    print("      - 格式：频率 vs 测量值")
    print("      - 用于验证分析结果")
    
    print("   3. data样例.mat - MATLAB数据文件")
    print("      - 包含Te变量(推测)")
    print("      - 可直接用于信号分析")


def create_data_conversion_example():
    """
    创建数据转换示例
    """
    print(f"\n🔄 数据转换示例：")
    print("=" * 60)
    
    # 示例：从WAV文件转换为Te格式
    print("📱 从WAV文件转换为Te格式：")
    print("""
# 需要安装: pip install librosa
import librosa
import numpy as np

def wav_to_te_format(wav_file_path):
    '''将WAV文件转换为Te格式'''
    # 读取音频文件
    signal, sample_rate = librosa.load(wav_file_path, sr=None)
    
    # 生成时间轴
    duration = len(signal) / sample_rate
    time_array = np.linspace(0, duration, len(signal))
    
    # 组合成Te格式
    te_data = np.column_stack((time_array, signal))
    
    return te_data, sample_rate

# 使用示例
te_data, sr = wav_to_te_format('data/S1R1/record1.wav')
analyzer.load_data_from_arrays(te_data[:, 0], te_data[:, 1])
""")
    
    # 示例：从混响时间数据生成分析
    print("\n📊 从混响时间数据进行分析：")
    print("""
import pandas as pd

def analyze_reverberation_data(txt_file_path):
    '''分析混响时间数据'''
    # 读取数据
    df = pd.read_csv(txt_file_path, sep='\\t', encoding='utf-8')
    frequencies = df.iloc[0, 1:].astype(str)  # 频率行
    rt_values = df.iloc[-1, 1:].astype(float)  # 平均值行
    
    # 提取频率数值
    freq_nums = []
    for freq_str in frequencies:
        freq_nums.append(float(freq_str.replace('Hz', '')))
    
    return np.array(freq_nums), rt_values

# 使用示例
freqs, rt_values = analyze_reverberation_data('data/S1R1/混响时间.txt')
plt.plot(freqs, rt_values)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Reverberation Time (s)')
""")


def main():
    """
    主函数：执行所有演示
    """
    print("🎯 声学信号分析 - 输入数据结构说明")
    print("=" * 80)
    
    # 基本数据结构
    te_data = show_data_structure()
    
    # 不同数据格式
    demonstrate_data_formats()
    
    # 现有数据分析
    analyze_existing_data_structure()
    
    # 数据转换示例
    create_data_conversion_example()
    
    print(f"\n✅ 数据结构说明完成！")
    print(f"📄 生成的示例文件：")
    print(f"   - example_te_data.mat")
    print(f"   - example_te_data.csv") 
    print(f"   - example_te_data.txt")
    
    # 可视化数据结构
    plt.figure(figsize=(12, 8))
    
    # 子图1：时间序列
    plt.subplot(2, 2, 1)
    plt.plot(te_data[:5000, 0], te_data[:5000, 1])
    plt.title('Time Domain Signal (First 5000 Points)')
    plt.xlabel('Time (s)')
    plt.ylabel('Signal Amplitude')
    plt.grid(True)
    
    # 子图2：数据结构示意
    plt.subplot(2, 2, 2)
    sample_indices = np.arange(10)
    plt.bar(sample_indices, te_data[:10, 0], alpha=0.7, label='Time Column')
    plt.bar(sample_indices + 0.4, te_data[:10, 1], alpha=0.7, label='Signal Column')
    plt.title('Te Data Structure (First 10 Rows)')
    plt.xlabel('Row Index')
    plt.ylabel('Value')
    plt.legend()
    
    # 子图3：信号全貌
    plt.subplot(2, 2, 3)
    plt.plot(te_data[:, 0], te_data[:, 1])
    plt.title('Complete Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Signal Amplitude')
    plt.grid(True)
    
    # 子图4：数据统计
    plt.subplot(2, 2, 4)
    plt.hist(te_data[:, 1], bins=50, alpha=0.7)
    plt.title('Signal Amplitude Distribution')
    plt.xlabel('Amplitude')
    plt.ylabel('Frequency')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('data_structure_visualization.png', dpi=300, bbox_inches='tight')
    print(f"   - data_structure_visualization.png")


if __name__ == "__main__":
    main()
