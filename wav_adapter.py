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
import csv
import pandas as pd
from datetime import datetime
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass, asdict
from pathlib import Path

# 数据路径配置常量
DEFAULT_DATA_DIRS = [
    "data",  # 相对路径
    "./data",  # 显式相对路径
    # "/Users/nanpipro/Documents/gitlocal/soundwave-analysis-py/data",  # 项目绝对路径
    # os.path.expanduser("~/Documents/gitlocal/soundwave-analysis-py/data"),  # 用户目录
]

# 输出路径配置常量
DEFAULT_OUTPUT_DIR = "./data_res"  # 默认输出目录
OUTPUT_SUBDIRS = {
    "analysis": "analysis_results",      # 音频分析结果
    "conversion": "wav_to_te_data",      # WAV转Te格式数据
    "statistics": "summary_statistics",   # 统计汇总数据
    "individual": "individual_files",    # 单个文件分析结果
}

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


def setup_output_directories(output_base_dir: str = DEFAULT_OUTPUT_DIR) -> Dict[str, str]:
    """
    创建输出目录结构
    
    Parameters
    ----------
    output_base_dir : str, optional
        输出基础目录路径，默认为DEFAULT_OUTPUT_DIR
        
    Returns
    -------
    Dict[str, str]
        各类型输出目录的完整路径映射
    """
    # 创建基础输出目录
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 创建所有子目录并返回路径映射
    output_paths = {}
    for key, subdir in OUTPUT_SUBDIRS.items():
        full_path = os.path.join(output_base_dir, subdir)
        os.makedirs(full_path, exist_ok=True)
        output_paths[key] = full_path
        
    print(f"📁 输出目录结构创建完成:")
    print(f"   基础目录: {os.path.abspath(output_base_dir)}")
    for key, path in output_paths.items():
        print(f"   {key}: {os.path.abspath(path)}")
        
    return output_paths


def save_audio_analysis_to_csv(analysis_results: Dict[str, List[AudioInfo]], 
                              output_dir: str) -> str:
    """
    将音频分析结果保存为CSV文件
    
    Parameters
    ----------
    analysis_results : Dict[str, List[AudioInfo]]
        音频分析结果字典
    output_dir : str
        输出目录路径
        
    Returns
    -------
    str
        保存的CSV文件路径
    """
    # 准备CSV数据
    csv_data = []
    for subdir, audio_infos in analysis_results.items():
        for info in audio_infos:
            row = {
                'directory': subdir,
                'filename': os.path.basename(info.file_path),
                'file_path': info.file_path,
                'sample_rate': info.sample_rate,
                'duration_seconds': info.duration,
                'channels': info.channels,
                'bit_depth': info.bit_depth,
                'total_samples': info.samples,
                'file_size_bytes': info.file_size,
                'file_size_kb': info.file_size / 1024,
                'analysis_timestamp': datetime.now().isoformat()
            }
            csv_data.append(row)
    
    # 保存为CSV文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"audio_analysis_results_{timestamp}.csv"
    csv_filepath = os.path.join(output_dir, csv_filename)
    
    df = pd.DataFrame(csv_data)
    df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
    
    print(f"💾 音频分析结果已保存: {csv_filepath}")
    print(f"   总文件数: {len(csv_data)}")
    print(f"   CSV列数: {len(df.columns)}")
    
    return csv_filepath


def save_te_data_to_csv(te_data: np.ndarray, 
                       source_file: str, 
                       output_dir: str) -> str:
    """
    将Te格式数据保存为CSV文件
    
    Parameters
    ----------
    te_data : np.ndarray
        Te格式数据 (N×2矩阵)
    source_file : str
        源WAV文件路径
    output_dir : str
        输出目录路径
        
    Returns
    -------
    str
        保存的CSV文件路径
    """
    # 准备CSV数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_name = os.path.splitext(os.path.basename(source_file))[0]
    csv_filename = f"te_data_{source_name}_{timestamp}.csv"
    csv_filepath = os.path.join(output_dir, csv_filename)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'time_seconds': te_data[:, 0],
        'signal_amplitude': te_data[:, 1],
        'source_file': source_file,
        'conversion_timestamp': datetime.now().isoformat()
    })
    
    # 保存为CSV文件
    df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
    
    print(f"💾 Te格式数据已保存: {csv_filepath}")
    print(f"   数据点数: {len(te_data)}")
    print(f"   时间范围: {te_data[:, 0].min():.6f} ~ {te_data[:, 0].max():.6f} 秒")
    
    return csv_filepath


def save_summary_statistics_to_csv(analysis_results: Dict[str, List[AudioInfo]], 
                                  output_dir: str) -> str:
    """
    保存汇总统计信息为CSV文件
    
    Parameters
    ---------- 
    analysis_results : Dict[str, List[AudioInfo]]
        音频分析结果字典
    output_dir : str
        输出目录路径
        
    Returns
    -------
    str
        保存的CSV文件路径
    """
    # 计算统计信息
    summary_data = []
    
    # 按目录统计
    for subdir, audio_infos in analysis_results.items():
        if not audio_infos:
            continue
            
        durations = [info.duration for info in audio_infos]
        sample_rates = [info.sample_rate for info in audio_infos]
        file_sizes = [info.file_size for info in audio_infos]
        
        row = {
            'directory': subdir,
            'file_count': len(audio_infos),
            'total_duration_seconds': sum(durations),
            'avg_duration_seconds': np.mean(durations),
            'min_duration_seconds': min(durations),
            'max_duration_seconds': max(durations),
            'unique_sample_rates': len(set(sample_rates)),
            'most_common_sample_rate': max(set(sample_rates), key=sample_rates.count),
            'total_file_size_mb': sum(file_sizes) / (1024 * 1024),
            'avg_file_size_kb': np.mean(file_sizes) / 1024,
            'analysis_timestamp': datetime.now().isoformat()
        }
        summary_data.append(row)
    
    # 整体统计
    all_infos = [info for infos in analysis_results.values() for info in infos]
    if all_infos:
        all_durations = [info.duration for info in all_infos]
        all_sample_rates = [info.sample_rate for info in all_infos]
        all_file_sizes = [info.file_size for info in all_infos]
        
        overall_row = {
            'directory': 'OVERALL_SUMMARY',
            'file_count': len(all_infos),
            'total_duration_seconds': sum(all_durations),
            'avg_duration_seconds': np.mean(all_durations),
            'min_duration_seconds': min(all_durations),
            'max_duration_seconds': max(all_durations),
            'unique_sample_rates': len(set(all_sample_rates)),
            'most_common_sample_rate': max(set(all_sample_rates), key=all_sample_rates.count),
            'total_file_size_mb': sum(all_file_sizes) / (1024 * 1024),
            'avg_file_size_kb': np.mean(all_file_sizes) / 1024,
            'analysis_timestamp': datetime.now().isoformat()
        }
        summary_data.append(overall_row)
    
    # 保存为CSV文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"summary_statistics_{timestamp}.csv"
    csv_filepath = os.path.join(output_dir, csv_filename)
    
    df = pd.DataFrame(summary_data)
    df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
    
    print(f"💾 汇总统计信息已保存: {csv_filepath}")
    print(f"   目录数: {len(analysis_results)}")
    print(f"   总文件数: {len(all_infos) if all_infos else 0}")
    
    return csv_filepath


def save_individual_audio_info_to_csv(audio_info: AudioInfo, output_dir: str) -> str:
    """
    将单个音频文件信息保存为CSV文件
    
    Parameters
    ----------
    audio_info : AudioInfo
        单个音频文件信息
    output_dir : str
        输出目录路径
        
    Returns
    -------
    str
        保存的CSV文件路径
    """
    # 准备CSV数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.splitext(os.path.basename(audio_info.file_path))[0]
    directory = os.path.basename(os.path.dirname(audio_info.file_path))
    csv_filename = f"audio_info_{directory}_{filename}_{timestamp}.csv"
    csv_filepath = os.path.join(output_dir, csv_filename)
    
    # 创建详细信息数据
    detailed_data = {
        'property': ['directory', 'filename', 'file_path', 'sample_rate', 'duration_seconds', 
                    'channels', 'bit_depth', 'total_samples', 'file_size_bytes', 'file_size_kb', 
                    'analysis_timestamp'],
        'value': [directory, os.path.basename(audio_info.file_path), audio_info.file_path,
                 audio_info.sample_rate, audio_info.duration, audio_info.channels,
                 audio_info.bit_depth, audio_info.samples, audio_info.file_size,
                 audio_info.file_size / 1024, datetime.now().isoformat()]
    }
    
    # 保存为CSV文件
    df = pd.DataFrame(detailed_data)
    df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
    
    print(f"💾 单个音频文件信息已保存: {csv_filename}")
    
    return csv_filepath


def process_all_wav_files_to_csv(data_dir: str, output_paths: Dict[str, str]) -> Dict[str, int]:
    """
    批量处理所有WAV文件，为每个文件生成单独的CSV文件
    
    Parameters
    ----------
    data_dir : str
        数据目录路径
    output_paths : Dict[str, str]
        输出目录路径映射
        
    Returns
    -------
    Dict[str, int]
        处理结果统计
    """
    print("\n🔄 批量处理所有WAV文件...")
    print("=" * 60)
    
    converter = WAVToTeConverter()
    
    # 统计信息
    stats = {
        'total_files': 0,
        'success_files': 0,
        'failed_files': 0,
        'te_csv_files': 0,
        'info_csv_files': 0
    }
    
    # 遍历所有子目录
    for subdir in sorted(os.listdir(data_dir)):
        subdir_path = os.path.join(data_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue
            
        print(f"\n📁 处理目录: {subdir}")
        
        # 查找WAV文件
        wav_files = glob.glob(os.path.join(subdir_path, "*.wav"))
        if not wav_files:
            print(f"   ⚠️  未找到WAV文件")
            continue
            
        # 为每个子目录创建单独的输出目录
        subdir_output_te = os.path.join(output_paths['conversion'], subdir)
        subdir_output_info = os.path.join(output_paths['individual'], subdir)
        os.makedirs(subdir_output_te, exist_ok=True)
        os.makedirs(subdir_output_info, exist_ok=True)
        
        # 处理每个WAV文件
        for wav_file in sorted(wav_files):
            stats['total_files'] += 1
            filename = os.path.basename(wav_file)
            print(f"   📄 处理文件: {filename}")
            
            try:
                # 1. 获取音频信息并保存为CSV
                audio_info = converter.get_audio_info(wav_file)
                info_csv = save_individual_audio_info_to_csv(audio_info, subdir_output_info)
                stats['info_csv_files'] += 1
                
                # 2. 转换为Te格式并保存为CSV
                te_data = converter.wav_to_te_format(wav_file)
                
                # 自定义Te数据CSV文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = os.path.splitext(filename)[0]
                te_csv_filename = f"te_data_{subdir}_{base_filename}_{timestamp}.csv"
                te_csv_filepath = os.path.join(subdir_output_te, te_csv_filename)
                
                # 创建DataFrame并保存
                df = pd.DataFrame({
                    'time_seconds': te_data[:, 0],
                    'signal_amplitude': te_data[:, 1],
                    'source_file': wav_file,
                    'directory': subdir,
                    'filename': filename,
                    'conversion_timestamp': datetime.now().isoformat()
                })
                df.to_csv(te_csv_filepath, index=False, encoding='utf-8-sig')
                stats['te_csv_files'] += 1
                
                print(f"      ✅ 信息CSV: {os.path.basename(info_csv)}")
                print(f"      ✅ Te数据CSV: {te_csv_filename}")
                print(f"      📊 数据点数: {len(te_data):,}")
                print(f"      ⏱️  时长: {audio_info.duration:.3f}秒")
                
                stats['success_files'] += 1
                
            except Exception as e:
                print(f"      ❌ 处理失败: {e}")
                stats['failed_files'] += 1
    
    # 打印处理结果统计
    print(f"\n📈 批量处理完成统计:")
    print(f"   总文件数: {stats['total_files']}")
    print(f"   成功处理: {stats['success_files']}")
    print(f"   处理失败: {stats['failed_files']}")
    print(f"   生成Te数据CSV: {stats['te_csv_files']}")
    print(f"   生成信息CSV: {stats['info_csv_files']}")
    
    return stats


def configure_data_paths() -> str:
    """
    配置并验证数据输入路径
    
    Returns
    -------
    str
        验证通过的数据目录路径
        
    Raises
    ------
    FileNotFoundError
        当所有配置的数据路径都不存在时
    """
    # 使用全局配置的数据路径列表
    data_path_configs = DEFAULT_DATA_DIRS
    
    print("🔍 验证数据路径配置...")
    
    for i, path in enumerate(data_path_configs, 1):
        abs_path = os.path.abspath(path)
        print(f"   {i}. 检查路径: {path}")
        print(f"      绝对路径: {abs_path}")
        
        if os.path.exists(path) and os.path.isdir(path):
            # 检查是否包含WAV文件
            wav_count = 0
            for root, dirs, files in os.walk(path):
                wav_count += len([f for f in files if f.endswith('.wav')])
            
            if wav_count > 0:
                print(f"      ✅ 路径有效，发现 {wav_count} 个WAV文件")
                return path
            else:
                print(f"      ⚠️  路径存在但未发现WAV文件")
        else:
            print(f"      ❌ 路径不存在")
    
    # 如果所有路径都不可用，抛出异常
    raise FileNotFoundError(
        "未找到有效的数据目录。请确保以下路径之一存在并包含WAV文件：\n" +
        "\n".join(f"  - {path}" for path in data_path_configs)
    )


def analyze_project_data(data_dir: str, output_paths: Dict[str, str]):
    """
    分析项目data目录中的实际数据，并保存结果为CSV
    
    Parameters
    ----------
    data_dir : str
        数据目录路径
    output_paths : Dict[str, str]
        输出目录路径映射
        
    Returns
    -------
    Dict[str, List[AudioInfo]]
        音频分析结果字典
    """
    print("🔍 分析项目数据目录...")
    print("=" * 60)
    
    converter = WAVToTeConverter()
    
    try:
        # 分析所有音频文件
        results = converter.analyze_data_directory(data_dir)
        
        if not results:
            print("❌ 未找到WAV音频文件")
            return None
            
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
        
        # 保存分析结果为CSV文件
        print(f"\n💾 保存分析结果...")
        try:
            # 保存详细音频分析结果
            csv_file = save_audio_analysis_to_csv(results, output_paths['analysis'])
            
            # 保存汇总统计信息
            stats_file = save_summary_statistics_to_csv(results, output_paths['statistics'])
            
            print(f"✅ 所有分析结果已保存完成")
            
        except Exception as e:
            print(f"⚠️ 保存CSV文件时出错: {e}")
        
        return results
            
    except Exception as e:
        print(f"❌ 分析数据目录失败: {e}")
        return None


def demonstrate_wav_conversion(data_dir: str, output_paths: Dict[str, str]):
    """
    演示WAV文件转换为Te格式，并保存为CSV
    
    Parameters
    ----------
    data_dir : str
        数据目录路径
    output_paths : Dict[str, str]
        输出目录路径映射
        
    Returns
    -------
    np.ndarray or None
        Te格式数据数组，失败时返回None
    """
    print("\n🔄 WAV转Te格式演示...")
    print("=" * 60)
    
    converter = WAVToTeConverter()
    
    # 查找第一个可用的WAV文件
    test_wav = None
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.wav'):
                test_wav = os.path.join(root, file)
                break
        if test_wav:
            break
            
    if not test_wav:
        print("❌ 未找到WAV文件进行演示")
        return None
        
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
        
        # 保存Te数据为CSV文件
        print(f"\n💾 保存Te格式数据...")
        try:
            csv_file = save_te_data_to_csv(te_data, test_wav, output_paths['conversion'])
            print(f"✅ Te数据已保存为CSV")
        except Exception as e:
            print(f"⚠️ 保存Te数据CSV时出错: {e}")
            
        return te_data
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return None


def integration_example(data_dir: str, output_paths: Optional[Dict[str, str]] = None):
    """
    展示与现有信号分析工具的集成使用
    
    Parameters
    ----------
    data_dir : str
        数据目录路径
    output_paths : Optional[Dict[str, str]], optional
        输出目录路径映射，可选
    """
    print("\n🔧 与信号分析工具集成示例...")
    print("=" * 60)
    
    try:
        from signal_analysis import SignalAnalyzer
        
        converter = WAVToTeConverter()
        
        # 找到第一个WAV文件
        test_wav = None
        for root, dirs, files in os.walk(data_dir):
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
    
    统一配置数据输入路径并执行所有分析功能
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
        
    try:
        # 统一配置和验证数据输入路径
        data_directory = configure_data_paths()
        print(f"\n📁 确认使用数据目录: {os.path.abspath(data_directory)}")
        
        # 创建输出目录结构
        output_paths = setup_output_directories()
        
        # 分析项目数据并保存汇总CSV
        analysis_results = analyze_project_data(data_directory, output_paths)
        
        # 批量处理所有WAV文件，为每个文件生成单独的CSV
        individual_stats = process_all_wav_files_to_csv(data_directory, output_paths)
        
        # 演示转换功能（可选，用于测试）
        # te_data = demonstrate_wav_conversion(data_directory, output_paths)
        
        # 集成示例（如需要可以取消注释）
        # integration_example(data_directory, output_paths)
        
        print(f"\n✅ WAV数据适配完成！")
        print(f"📖 您的 {data_directory} 目录中的WAV文件可以通过转换使用现有的信号分析代码")
        print(f"📊 所有分析结果已保存到 {os.path.abspath(DEFAULT_OUTPUT_DIR)} 目录")
        
        if analysis_results:
            print(f"📈 汇总分析的音频文件总数: {sum(len(infos) for infos in analysis_results.values())}")
        if individual_stats:
            print(f"🔄 单独处理的音频文件总数: {individual_stats['success_files']}")
            print(f"📄 生成的Te数据CSV文件数: {individual_stats['te_csv_files']}")
            print(f"📄 生成的音频信息CSV文件数: {individual_stats['info_csv_files']}")
        
    except FileNotFoundError as e:
        print(f"\n❌ 数据路径配置错误:")
        print(str(e))
        print("\n💡 请检查项目结构并确保数据目录存在")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        print("请检查错误信息并重试")


def get_configured_data_path() -> str:
    """
    获取配置好的数据路径，供外部模块使用
    
    Returns
    -------
    str
        配置好的数据目录路径
        
    Examples
    --------
    >>> # 在其他模块中使用
    >>> from wav_adapter import get_configured_data_path
    >>> data_path = get_configured_data_path()
    >>> print(f"数据路径: {data_path}")
    """
    return configure_data_paths()


if __name__ == "__main__":
    main()
