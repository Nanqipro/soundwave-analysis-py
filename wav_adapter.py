#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAV音频数据适配器
===============

将WAV音频文件转换为信号分析工具所需的Te格式数据
支持批量处理和多种音频格式

主要功能：
- WAV文件读取和转换
- 音频格式信息分析
- Te格式数据生成
- 批量处理data目录中的音频文件
"""

import numpy as np
import os
import glob
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass

# 音频处理库导入（优先使用可用的库）
try:
    import librosa
    AUDIO_BACKEND = 'librosa'
    print("✓ 使用 librosa 作为音频处理后端")
except ImportError:
    try:
        import soundfile as sf
        AUDIO_BACKEND = 'soundfile'
        print("✓ 使用 soundfile 作为音频处理后端")
    except ImportError:
        try:
            from scipy.io import wavfile
            AUDIO_BACKEND = 'scipy'
            print("✓ 使用 scipy.io.wavfile 作为音频处理后端")
        except ImportError:
            AUDIO_BACKEND = None
            print("❌ 未找到音频处理库，请安装：pip install librosa 或 pip install soundfile")


@dataclass
class AudioInfo:
    """
    音频文件信息类
    
    Attributes
    ----------
    file_path : str
        音频文件路径
    sample_rate : int
        采样率 (Hz)
    duration : float
        时长 (秒)
    channels : int
        声道数
    bit_depth : int
        位深度
    samples : int
        总采样点数
    file_size : int
        文件大小 (字节)
    """
    file_path: str
    sample_rate: int
    duration: float
    channels: int
    bit_depth: int
    samples: int
    file_size: int


class WAVToTeConverter:
    """
    WAV音频文件到Te格式转换器
    
    将WAV音频文件转换为信号分析工具所需的Te格式数据
    """
    
    def __init__(self):
        """初始化转换器"""
        if AUDIO_BACKEND is None:
            raise ImportError(
                "未找到音频处理库，请安装其中之一：\n"
                "pip install librosa\n"
                "pip install soundfile\n"
                "pip install scipy"
            )
        self.backend = AUDIO_BACKEND
        
    def load_wav_file(self, wav_file_path: str, target_sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """
        加载WAV音频文件
        
        Parameters
        ----------
        wav_file_path : str
            WAV文件路径
        target_sr : int, optional
            目标采样率，None表示保持原采样率
            
        Returns
        -------
        Tuple[np.ndarray, int]
            音频信号数组和采样率
        """
        if not os.path.exists(wav_file_path):
            raise FileNotFoundError(f"音频文件不存在: {wav_file_path}")
            
        try:
            if self.backend == 'librosa':
                signal, sr = librosa.load(wav_file_path, sr=target_sr, mono=True)
            elif self.backend == 'soundfile':
                import soundfile as sf
                signal, sr = sf.read(wav_file_path)
                if len(signal.shape) > 1:  # 多声道转单声道
                    signal = np.mean(signal, axis=1)
                if target_sr and sr != target_sr:
                    signal = librosa.resample(signal, orig_sr=sr, target_sr=target_sr)
                    sr = target_sr
            elif self.backend == 'scipy':
                from scipy.io import wavfile
                sr, signal = wavfile.read(wav_file_path)
                # 归一化到[-1, 1]范围
                if signal.dtype == np.int16:
                    signal = signal.astype(np.float32) / 32768.0
                elif signal.dtype == np.int32:
                    signal = signal.astype(np.float32) / 2147483648.0
                # 多声道转单声道
                if len(signal.shape) > 1:
                    signal = np.mean(signal, axis=1)
                    
            return signal, sr
            
        except Exception as e:
            raise RuntimeError(f"加载WAV文件失败 {wav_file_path}: {e}")
            
    def get_audio_info(self, wav_file_path: str) -> AudioInfo:
        """
        获取音频文件详细信息
        
        Parameters
        ----------
        wav_file_path : str
            WAV文件路径
            
        Returns
        -------
        AudioInfo
            音频文件信息对象
        """
        if not os.path.exists(wav_file_path):
            raise FileNotFoundError(f"音频文件不存在: {wav_file_path}")
            
        # 获取文件大小
        file_size = os.path.getsize(wav_file_path)
        
        # 加载音频获取基本信息
        signal, sr = self.load_wav_file(wav_file_path)
        
        # 计算音频属性
        samples = len(signal)
        duration = samples / sr
        channels = 1  # 已转换为单声道
        
        # 估算位深度（从文件大小推算）
        expected_samples = file_size / 4  # 假设32位
        if abs(expected_samples - samples) < abs(file_size / 2 - samples):
            bit_depth = 32
        else:
            bit_depth = 16
            
        return AudioInfo(
            file_path=wav_file_path,
            sample_rate=sr,
            duration=duration,
            channels=channels,
            bit_depth=bit_depth,
            samples=samples,
            file_size=file_size
        )
        
    def wav_to_te_format(self, wav_file_path: str, target_sr: Optional[int] = None) -> np.ndarray:
        """
        将WAV文件转换为Te格式数据
        
        Parameters
        ----------
        wav_file_path : str
            WAV文件路径
        target_sr : int, optional
            目标采样率，None表示保持原采样率
            
        Returns
        -------
        np.ndarray
            Te格式数据 (N×2矩阵)，第1列为时间，第2列为信号
        """
        # 加载音频数据
        signal, sr = self.load_wav_file(wav_file_path, target_sr)
        
        # 生成时间轴
        samples = len(signal)
        duration = samples / sr
        time_array = np.linspace(0, duration, samples)
        
        # 组合成Te格式：N×2矩阵
        te_data = np.column_stack((time_array, signal))
        
        return te_data
        
    def analyze_data_directory(self, data_dir: str = "data") -> Dict[str, List[AudioInfo]]:
        """
        分析data目录中所有WAV文件
        
        Parameters
        ----------
        data_dir : str, optional
            数据目录路径，默认为"data"
            
        Returns
        -------
        Dict[str, List[AudioInfo]]
            每个子目录的音频文件信息列表
        """
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"数据目录不存在: {data_dir}")
            
        analysis_results = {}
        
        # 遍历所有子目录
        for subdir in sorted(os.listdir(data_dir)):
            subdir_path = os.path.join(data_dir, subdir)
            if not os.path.isdir(subdir_path):
                continue
                
            # 查找WAV文件
            wav_files = glob.glob(os.path.join(subdir_path, "*.wav"))
            if not wav_files:
                continue
                
            # 分析每个WAV文件
            audio_infos = []
            for wav_file in sorted(wav_files):
                try:
                    info = self.get_audio_info(wav_file)
                    audio_infos.append(info)
                except Exception as e:
                    print(f"❌ 分析文件失败 {wav_file}: {e}")
                    
            if audio_infos:
                analysis_results[subdir] = audio_infos
                
        return analysis_results


def analyze_project_data():
    """
    分析项目data目录中的实际数据
    """
    print("🔍 分析项目数据目录...")
    print("=" * 60)
    
    converter = WAVToTeConverter()
    
    try:
        # 分析所有音频文件
        results = converter.analyze_data_directory("data")
        
        if not results:
            print("❌ 未找到WAV音频文件")
            return
            
        print(f"📊 发现 {len(results)} 个数据子目录")
        
        total_files = 0
        for subdir, audio_infos in results.items():
            print(f"\n📁 目录: {subdir}")
            print(f"   WAV文件数量: {len(audio_infos)}")
            
            for i, info in enumerate(audio_infos):
                filename = os.path.basename(info.file_path)
                print(f"   📄 {filename}")
                print(f"      采样率: {info.sample_rate:,} Hz")
                print(f"      时长: {info.duration:.3f} 秒")
                print(f"      采样点数: {info.samples:,}")
                print(f"      位深度: {info.bit_depth} 位")
                print(f"      文件大小: {info.file_size / 1024:.1f} KB")
                
            total_files += len(audio_infos)
            
        print(f"\n📈 总计: {total_files} 个WAV文件")
        
        # 检查采样率一致性
        all_sample_rates = [info.sample_rate for infos in results.values() for info in infos]
        unique_rates = set(all_sample_rates)
        
        print(f"\n🎵 音频格式统计:")
        print(f"   采样率: {', '.join(map(str, unique_rates))} Hz")
        print(f"   是否统一: {'✓' if len(unique_rates) == 1 else '❌'}")
        
        if len(unique_rates) == 1:
            sr = list(unique_rates)[0]
            print(f"   ✓ 所有文件采样率统一为 {sr:,} Hz")
        else:
            print(f"   ❌ 采样率不统一，建议重采样到统一采样率")
            
    except Exception as e:
        print(f"❌ 分析数据目录失败: {e}")


def demonstrate_wav_conversion():
    """
    演示WAV文件转换为Te格式
    """
    print("\n🔄 WAV转Te格式演示...")
    print("=" * 60)
    
    converter = WAVToTeConverter()
    
    # 查找第一个可用的WAV文件
    test_wav = None
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith('.wav'):
                test_wav = os.path.join(root, file)
                break
        if test_wav:
            break
            
    if not test_wav:
        print("❌ 未找到WAV文件进行演示")
        return
        
    print(f"📄 使用文件: {test_wav}")
    
    try:
        # 获取音频信息
        info = converter.get_audio_info(test_wav)
        print(f"   原始采样率: {info.sample_rate:,} Hz")
        print(f"   原始时长: {info.duration:.3f} 秒")
        
        # 转换为Te格式
        te_data = converter.wav_to_te_format(test_wav)
        
        print(f"\n✅ 转换完成:")
        print(f"   Te数据形状: {te_data.shape}")
        print(f"   时间范围: {te_data[:, 0].min():.6f} ~ {te_data[:, 0].max():.6f} 秒")
        print(f"   信号范围: {te_data[:, 1].min():.6f} ~ {te_data[:, 1].max():.6f}")
        
        print(f"\n📝 前5行Te数据:")
        print("   时间(秒)        信号值")
        print("   " + "-" * 30)
        for i in range(5):
            print(f"   {te_data[i, 0]:10.6f}    {te_data[i, 1]:10.6f}")
            
        return te_data
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return None


def integration_example():
    """
    展示与现有信号分析工具的集成使用
    """
    print("\n🔧 与信号分析工具集成示例...")
    print("=" * 60)
    
    try:
        from signal_analysis import SignalAnalyzer
        
        converter = WAVToTeConverter()
        
        # 找到第一个WAV文件
        test_wav = None
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith('.wav'):
                    test_wav = os.path.join(root, file)
                    break
            if test_wav:
                break
                
        if not test_wav:
            print("❌ 未找到WAV文件")
            return
            
        print(f"📄 测试文件: {os.path.basename(test_wav)}")
        
        # 方法1：直接转换加载
        print("\n🔸 方法1: 直接转换加载")
        te_data = converter.wav_to_te_format(test_wav)
        
        analyzer = SignalAnalyzer()
        analyzer.load_data_from_arrays(te_data[:, 0], te_data[:, 1])
        
        print("   ✓ 数据加载成功")
        print(f"   数据点数: {len(analyzer.signal_data):,}")
        print(f"   采样频率: {analyzer.sampling_freq:,.0f} Hz")
        
        # 方法2：重采样到标准频率
        print("\n🔸 方法2: 重采样到1MHz (MATLAB兼容)")
        target_sr = 1000000  # 1MHz，与MATLAB代码一致
        
        # 注意：实际应用中可能需要根据信号特性调整采样率
        # 1MHz对于48kHz音频是过采样，但保持与原MATLAB代码一致
        
        analyzer_hf = SignalAnalyzer(sampling_step=1e-6)  # 1MHz
        signal, sr = converter.load_wav_file(test_wav)
        
        # 生成高频时间轴（截取到1秒）
        duration = min(1.0, len(signal) / sr)  # 最多1秒
        samples_needed = int(duration * analyzer_hf.sampling_freq)
        time_hf = np.linspace(0, duration, samples_needed)
        
        # 对原信号进行重采样
        time_orig = np.linspace(0, duration, int(duration * sr))
        signal_resampled = np.interp(time_hf, time_orig, signal[:len(time_orig)])
        
        analyzer_hf.load_data_from_arrays(time_hf, signal_resampled)
        
        print("   ✓ 高频重采样完成")
        print(f"   新数据点数: {len(analyzer_hf.signal_data):,}")
        print(f"   新采样频率: {analyzer_hf.sampling_freq:,.0f} Hz")
        
        print("\n🎯 可以进行的分析:")
        print("   • analyzer.plot_time_domain()     - 时域图")
        print("   • analyzer.plot_frequency_domain() - 频域图") 
        print("   • analyzer.plot_phase_domain()    - 相位图")
        print("   • analyzer.plot_spectrogram()     - 时频图")
        print("   • analyzer.analyze_all()          - 完整分析")
        
    except ImportError:
        print("❌ 未找到signal_analysis模块，请确保该文件在同一目录")
    except Exception as e:
        print(f"❌ 集成演示失败: {e}")


def main():
    """
    主函数：运行所有分析和演示
    """
    print("🎵 WAV音频数据适配器")
    print("=" * 80)
    
    # 检查音频处理库
    if AUDIO_BACKEND is None:
        print("❌ 请先安装音频处理库:")
        print("   pip install librosa  # 推荐")
        print("   # 或者")
        print("   pip install soundfile")
        return
        
    # 分析项目数据
    analyze_project_data()
    
    # 演示转换功能
    demonstrate_wav_conversion()
    
    # 集成示例
    integration_example()
    
    print(f"\n✅ WAV数据适配完成！")
    print(f"📖 您的data目录中的WAV文件可以通过转换使用现有的信号分析代码")


if __name__ == "__main__":
    main()
