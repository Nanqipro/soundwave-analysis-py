#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAV文件声学信号综合分析工具
========================

专业的声学信号多维度分析套件
支持时域、频域、相位域和时频域的全面分析

🎯 核心功能：
- 🎵 高精度频谱分析（精确到0.01Hz）
- 📊 声压级计算（dB SPL标准）
- 🕐 时域波形分析
- 📐 相位谱分析  
- 🎶 时频谱图分析
- 📈 四合一综合分析显示
- 🔄 批量处理WAV文件
- 📁 专业图表输出

🔍 分析维度：
- 时域分析：波形、RMS、峰值统计
- 频域分析：高精度FFT、声压级转换
- 相位分析：频率-相位关系
- 时频分析：短时傅里叶变换谱图
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from typing import Tuple, List, Dict, Optional
from scipy.io import wavfile
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

# 尝试导入librosa，如果失败则使用scipy
try:
    import librosa
    AUDIO_BACKEND = 'librosa'
except ImportError:
    AUDIO_BACKEND = 'scipy'
    print("⚠️  未安装librosa，使用scipy.io.wavfile (功能受限)")


class SpectrumAnalyzer:
    """
    声学信号综合分析器类
    
    专业的声学信号多维度分析工具，支持：
    - 时域分析：波形图、RMS、峰值统计
    - 频域分析：高精度FFT、声压级计算（dB SPL）
    - 相位分析：频率-相位关系图
    - 时频分析：谱图（短时傅里叶变换）
    - 综合分析：四合一显示所有分析结果
    
    特性：
    - 频率分辨率可达0.01Hz
    - 符合声学标准的dB SPL计算
    - 批量处理能力
    - 专业图表输出
    """
    
    def __init__(self, target_freq_resolution: float = 0.01, output_dir: str = "ana_res"):
        """
        初始化频谱分析器
        
        Parameters
        ----------
        target_freq_resolution : float, optional
            目标频率分辨率 (Hz)，默认0.01Hz
        output_dir : str, optional
            输出目录路径，默认"ana_res"
        """
        self.target_freq_resolution = target_freq_resolution
        self.reference_pressure = 20e-6  # 参考声压 20μPa (空气中的标准)
        self.output_dir = output_dir
        
        # 创建输出目录
        self._ensure_output_dir()
        
    def load_wav_file(self, wav_file_path: str) -> Tuple[np.ndarray, int]:
        """
        加载WAV音频文件
        
        Parameters
        ----------
        wav_file_path : str
            WAV文件路径
            
        Returns
        -------
        Tuple[np.ndarray, int]
            音频信号数组和采样率
        """
        if not os.path.exists(wav_file_path):
            raise FileNotFoundError(f"音频文件不存在: {wav_file_path}")
            
        try:
            if AUDIO_BACKEND == 'librosa':
                # 使用librosa加载，保持原始采样率
                signal, sr = librosa.load(wav_file_path, sr=None, mono=True)
            else:
                # 使用scipy加载
                sr, signal = wavfile.read(wav_file_path)
                
                # 数据类型转换和归一化
                if signal.dtype == np.int16:
                    signal = signal.astype(np.float64) / 32768.0
                elif signal.dtype == np.int32:
                    signal = signal.astype(np.float64) / 2147483648.0
                elif signal.dtype == np.uint8:
                    signal = (signal.astype(np.float64) - 128) / 128.0
                else:
                    signal = signal.astype(np.float64)
                
                # 转单声道
                if len(signal.shape) > 1:
                    signal = np.mean(signal, axis=1)
                    
            return signal, sr
            
        except Exception as e:
            raise RuntimeError(f"加载WAV文件失败 {wav_file_path}: {e}")
    
    def calculate_optimal_fft_length(self, signal_length: int, sample_rate: int) -> Tuple[int, float]:
        """
        计算最优FFT长度以达到目标频率分辨率
        
        Parameters
        ----------
        signal_length : int
            信号长度（采样点数）
        sample_rate : int
            采样率 (Hz)
            
        Returns
        -------
        Tuple[int, float]
            FFT长度和实际频率分辨率
        """
        # 理想FFT长度（达到目标分辨率）
        ideal_fft_length = int(sample_rate / self.target_freq_resolution)
        
        # 实际可用的最大FFT长度（受信号长度限制）
        max_available_length = signal_length
        
        # 选择实际FFT长度
        actual_fft_length = min(ideal_fft_length, max_available_length)
        
        # 调整到最近的2的幂次（提高FFT效率）
        # actual_fft_length = 2 ** int(np.log2(actual_fft_length))
        
        # 计算实际频率分辨率
        actual_freq_resolution = sample_rate / actual_fft_length
        
        return actual_fft_length, actual_freq_resolution
    
    def _ensure_output_dir(self) -> None:
        """
        确保输出目录存在
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✅ 创建输出目录: {self.output_dir}")
    
    def _get_output_path(self, filename: str, subdir: str = None) -> str:
        """
        获取完整的输出文件路径
        
        Parameters
        ----------
        filename : str
            文件名
        subdir : str, optional
            子目录名，用于按数据文件夹区分
            
        Returns
        -------
        str
            完整的输出路径
        """
        if subdir:
            # 创建子目录路径
            subdir_path = os.path.join(self.output_dir, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
                print(f"✅ 创建子目录: {subdir_path}")
            return os.path.join(subdir_path, filename)
        else:
            return os.path.join(self.output_dir, filename)
    
    def _extract_data_folder_name(self, wav_file_path: str) -> str:
        """
        从WAV文件路径中提取数据文件夹名称
        
        Parameters
        ----------
        wav_file_path : str
            WAV文件路径
            
        Returns
        -------
        str
            数据文件夹名称，如果无法提取则返回"single_files"
        """
        # 标准化路径
        normalized_path = os.path.normpath(wav_file_path)
        path_parts = normalized_path.split(os.sep)
        
        # 查找data目录的位置
        data_index = -1
        for i, part in enumerate(path_parts):
            if part == "data":
                data_index = i
                break
        
        # 如果找到data目录，返回其下一级目录名
        if data_index >= 0 and data_index + 1 < len(path_parts):
            return path_parts[data_index + 1]
        
        # 如果没找到data目录，尝试从文件名中提取
        filename = os.path.basename(wav_file_path)
        # 如果文件名包含类似S1R1的格式，提取出来
        import re
        match = re.match(r'([A-Z]\d+[A-Z]\d+)', filename)
        if match:
            return match.group(1)
        
        # 默认返回single_files
        return "single_files"
    
    def signal_to_spectrum(self, signal: np.ndarray, sample_rate: int, 
                          window_type: str = 'hann') -> Tuple[np.ndarray, np.ndarray]:
        """
        将时域信号转换为频谱
        
        Parameters
        ----------
        signal : np.ndarray
            时域信号
        sample_rate : int
            采样率 (Hz)
        window_type : str, optional
            窗函数类型，默认'hann'
            
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            频率数组(Hz)和声压级数组(dB)
        """
        # 去除直流分量
        signal = signal - np.mean(signal)
        
        # 计算最优FFT长度
        fft_length, actual_freq_res = self.calculate_optimal_fft_length(
            len(signal), sample_rate
        )
        
        print(f"📊 FFT参数:")
        print(f"   信号长度: {len(signal):,} 点")
        print(f"   信号时长: {len(signal)/sample_rate:.3f} 秒")
        print(f"   FFT长度: {fft_length:,} 点")
        print(f"   目标频率分辨率: {self.target_freq_resolution:.3f} Hz")
        print(f"   实际频率分辨率: {actual_freq_res:.4f} Hz")
        
        # 如果信号长度不足，进行零填充
        if len(signal) < fft_length:
            print(f"⚠️  信号长度不足，进行零填充: {len(signal)} → {fft_length}")
            signal_padded = np.zeros(fft_length)
            signal_padded[:len(signal)] = signal
            signal = signal_padded
        else:
            # 截取所需长度
            signal = signal[:fft_length]
        
        # 应用窗函数
        if window_type == 'hann':
            window = np.hanning(len(signal))
        elif window_type == 'hamming':
            window = np.hamming(len(signal))
        elif window_type == 'blackman':
            window = np.blackman(len(signal))
        else:
            window = np.ones(len(signal))  # 矩形窗
        
        signal_windowed = signal * window
        
        # 窗函数功率修正因子
        window_power_correction = np.sqrt(np.mean(window**2))
        
        # 计算FFT
        fft_result = np.fft.fft(signal_windowed)
        
        # 只取正频率部分
        n_positive_freqs = len(fft_result) // 2 + 1
        fft_positive = fft_result[:n_positive_freqs]
        
        # 生成频率轴
        frequencies = np.fft.fftfreq(len(fft_result), 1/sample_rate)[:n_positive_freqs]
        
        # 计算功率谱密度 (PSD)
        psd = np.abs(fft_positive)**2
        
        # 除DC外的频率成分要乘以2（因为只保留了正频率）
        psd[1:] *= 2
        
        # 归一化：除以FFT长度的平方和窗函数修正
        psd = psd / (len(signal)**2 * window_power_correction**2)
        
        # 转换为声压级 (dB SPL)
        # 假设信号已经是声压值（Pa），参考值为20μPa
        
        # 避免对零值取对数
        psd_safe = np.maximum(psd, 1e-20)
        
        # 计算声压级 (dB SPL)
        # SPL = 20 * log10(P_rms / P_ref)
        # 其中 P_rms = sqrt(PSD * df)，df = 频率分辨率
        
        df = frequencies[1] - frequencies[0]  # 频率分辨率
        p_rms = np.sqrt(psd_safe * df)
        spl_db = 20 * np.log10(p_rms / self.reference_pressure)
        
        return frequencies, spl_db
    
    def plot_time_domain(self, signal: np.ndarray, sample_rate: int, 
                        max_duration: Optional[float] = None,
                        save_path: Optional[str] = None,
                        show_plot: bool = False,
                        subdir: str = None) -> None:
        """
        绘制时域波形图
        
        Parameters
        ----------
        signal : np.ndarray
            时域信号数组
        sample_rate : int
            采样率 (Hz)
        max_duration : float, optional
            最大显示时长（秒），None表示显示全部
        save_path : str, optional
            保存路径，None表示不保存
        show_plot : bool, optional
            是否显示图片，默认False
        """
        # 生成时间轴
        time_axis = np.arange(len(signal)) / sample_rate
        
        # 限制显示时长
        if max_duration is not None:
            max_samples = int(max_duration * sample_rate)
            if len(signal) > max_samples:
                signal = signal[:max_samples]
                time_axis = time_axis[:max_samples]
        
        plt.figure(figsize=(12, 6))
        plt.plot(time_axis, signal, 'b-', linewidth=0.8, alpha=0.8)
        
        plt.xlabel('Time (s)', fontsize=12, fontfamily='Times New Roman')
        plt.ylabel('Amplitude', fontsize=12, fontfamily='Times New Roman')
        plt.title('Time Domain Analysis', fontsize=14, fontfamily='Times New Roman')
        
        plt.grid(True, alpha=0.3)
        plt.xlim([0, time_axis[-1]])
        
        # 添加统计信息
        rms_value = np.sqrt(np.mean(signal**2))
        peak_value = np.max(np.abs(signal))
        plt.text(0.02, 0.98, f'RMS: {rms_value:.4f}\nPeak: {peak_value:.4f}', 
                transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            full_save_path = self._get_output_path(save_path, subdir) if not os.path.dirname(save_path) else save_path
            plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 时域图已保存: {full_save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def analyze_phase_spectrum(self, signal: np.ndarray, sample_rate: int,
                              window_type: str = 'hann') -> Tuple[np.ndarray, np.ndarray]:
        """
        分析信号的相位谱
        
        Parameters
        ----------
        signal : np.ndarray
            时域信号
        sample_rate : int
            采样率 (Hz)
        window_type : str, optional
            窗函数类型，默认'hann'
            
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            频率数组(Hz)和相位数组(度)
        """
        # 去除直流分量
        signal = signal - np.mean(signal)
        
        # 计算最优FFT长度
        fft_length, _ = self.calculate_optimal_fft_length(len(signal), sample_rate)
        
        # 如果信号长度不足，进行零填充
        if len(signal) < fft_length:
            signal_padded = np.zeros(fft_length)
            signal_padded[:len(signal)] = signal
            signal = signal_padded
        else:
            signal = signal[:fft_length]
        
        # 应用窗函数
        if window_type == 'hann':
            window = np.hanning(len(signal))
        elif window_type == 'hamming':
            window = np.hamming(len(signal))
        elif window_type == 'blackman':
            window = np.blackman(len(signal))
        else:
            window = np.ones(len(signal))
        
        signal_windowed = signal * window
        
        # 计算FFT
        fft_result = np.fft.fft(signal_windowed)
        
        # 只取正频率部分
        n_positive_freqs = len(fft_result) // 2 + 1
        fft_positive = fft_result[:n_positive_freqs]
        
        # 生成频率轴
        frequencies = np.fft.fftfreq(len(fft_result), 1/sample_rate)[:n_positive_freqs]
        
        # 计算相位（转换为度）
        phase_rad = np.angle(fft_positive)
        phase_deg = phase_rad * 180 / np.pi
        
        return frequencies, phase_deg
    
    def detect_resonance_peaks(self, frequencies: np.ndarray, spl_db: np.ndarray, 
                              min_prominence: float = 6.0, 
                              min_distance: float = 10.0,
                              min_height: Optional[float] = None,
                              max_peaks: int = 20) -> Dict:
        """
        检测并提取共振峰特征
        
        Parameters
        ----------
        frequencies : np.ndarray
            频率数组 (Hz)
        spl_db : np.ndarray
            声压级数组 (dB SPL)
        min_prominence : float, optional
            最小峰值突出度 (dB)，默认6.0dB
        min_distance : float, optional
            相邻峰值间最小频率间隔 (Hz)，默认10.0Hz
        min_height : float, optional
            峰值最小高度 (dB SPL)，None表示自动计算
        max_peaks : int, optional
            最大检测峰值数量，默认20
            
        Returns
        -------
        Dict
            包含共振峰信息的字典
            
        Notes
        -----
        该方法识别频谱中显著的共振峰，这些峰值代表建筑结构
        最容易发生共振并对声音产生放大效应的频率点。
        """
        from scipy.signal import find_peaks
        
        # 计算频率分辨率
        freq_resolution = frequencies[1] - frequencies[0]
        
        # 转换距离参数为索引间隔
        min_distance_idx = max(1, int(min_distance / freq_resolution))
        
        # 自动计算最小高度阈值
        if min_height is None:
            # 使用中位数 + 1.5倍标准差作为阈值
            min_height = np.median(spl_db) + 1.5 * np.std(spl_db)
        
        # 检测峰值
        peak_indices, peak_properties = find_peaks(
            spl_db,
            height=min_height,           # 最小高度
            prominence=min_prominence,   # 最小突出度  
            distance=min_distance_idx    # 最小距离
        )
        
        # 限制峰值数量
        if len(peak_indices) > max_peaks:
            # 按突出度排序，保留最显著的峰值
            prominences = peak_properties['prominences']
            sorted_indices = np.argsort(prominences)[::-1]
            selected_indices = sorted_indices[:max_peaks]
            peak_indices = peak_indices[selected_indices]
            # 同时更新突出度数组
            peak_properties['prominences'] = peak_properties['prominences'][selected_indices]
            # 重新按频率排序
            freq_sort_idx = np.argsort(peak_indices)
            peak_indices = peak_indices[freq_sort_idx]
            peak_properties['prominences'] = peak_properties['prominences'][freq_sort_idx]
        
        # 提取峰值信息
        resonance_peaks = []
        for i, peak_idx in enumerate(peak_indices):
            # 安全地获取突出度值
            prominence_value = 0
            try:
                if i < len(peak_properties['prominences']):
                    prominence_value = peak_properties['prominences'][i]
            except (IndexError, KeyError):
                prominence_value = 0
            
            peak_info = {
                'index': peak_idx,
                'center_frequency': frequencies[peak_idx],  # 中心频率 (Hz)
                'peak_spl': spl_db[peak_idx],              # 峰值声压级 (dB)
                'prominence': prominence_value,             # 峰值突出度 (dB)
                'rank': i + 1  # 排名（按频率从低到高）
            }
            resonance_peaks.append(peak_info)
        
        # 计算统计信息
        if resonance_peaks:
            center_frequencies = [peak['center_frequency'] for peak in resonance_peaks]
            peak_spls = [peak['peak_spl'] for peak in resonance_peaks]
            
            stats = {
                'total_peaks': len(resonance_peaks),
                'frequency_range': (min(center_frequencies), max(center_frequencies)),
                'mean_frequency': np.mean(center_frequencies),
                'std_frequency': np.std(center_frequencies),
                'spl_range': (min(peak_spls), max(peak_spls)), 
                'mean_spl': np.mean(peak_spls),
                'std_spl': np.std(peak_spls),
                'dominant_peak': resonance_peaks[np.argmax(peak_spls)]  # 最强峰值
            }
        else:
            stats = {
                'total_peaks': 0,
                'frequency_range': (0, 0),
                'mean_frequency': 0,
                'std_frequency': 0,
                'spl_range': (0, 0),
                'mean_spl': 0,
                'std_spl': 0,
                'dominant_peak': None
            }
        
        result = {
            'resonance_peaks': resonance_peaks,
            'statistics': stats,
            'detection_parameters': {
                'min_prominence': min_prominence,
                'min_distance': min_distance,
                'min_height': min_height,
                'max_peaks': max_peaks
            }
        }
        
        print(f"\n🎯 共振峰检测结果:")
        print(f"   检测到 {stats['total_peaks']} 个显著共振峰")
        if stats['total_peaks'] > 0:
            print(f"   频率范围: {stats['frequency_range'][0]:.1f} - {stats['frequency_range'][1]:.1f} Hz")
            print(f"   声压级范围: {stats['spl_range'][0]:.1f} - {stats['spl_range'][1]:.1f} dB SPL")
            if stats['dominant_peak']:
                print(f"   主导峰值: {stats['dominant_peak']['center_frequency']:.2f} Hz, {stats['dominant_peak']['peak_spl']:.1f} dB")
        
        return result
    
    def plot_resonance_peaks(self, frequencies: np.ndarray, spl_db: np.ndarray,
                           resonance_result: Dict,
                           freq_range: Optional[Tuple[float, float]] = None,
                           save_path: Optional[str] = None,
                           show_plot: bool = False,
                           subdir: str = None) -> None:
        """
        绘制共振峰分析图
        
        Parameters
        ----------
        frequencies : np.ndarray
            频率数组
        spl_db : np.ndarray 
            声压级数组
        resonance_result : Dict
            共振峰检测结果
        freq_range : Tuple[float, float], optional
            频率显示范围
        save_path : str, optional
            保存路径
        show_plot : bool, optional
            是否显示图片
        subdir : str, optional
            子目录名
        """
        plt.figure(figsize=(16, 10))
        
        # 主频谱图
        plt.subplot(2, 2, (1, 2))  # 占据上方两个位置
        
        # 绘制频谱曲线
        plt.plot(frequencies, spl_db, 'b-', linewidth=1.0, alpha=0.7, label='Frequency Spectrum')
        
        # 标记所有共振峰
        resonance_peaks = resonance_result['resonance_peaks']
        if resonance_peaks:
            peak_freqs = [peak['center_frequency'] for peak in resonance_peaks]
            peak_spls = [peak['peak_spl'] for peak in resonance_peaks]
            
            # 绘制峰值点
            plt.scatter(peak_freqs, peak_spls, c='red', s=80, 
                       marker='o', edgecolors='darkred', linewidth=2,
                       label=f'Resonance Peaks ({len(resonance_peaks)})', zorder=5)
            
            # 标注前5个最显著的峰值
            sorted_peaks = sorted(resonance_peaks, key=lambda x: x['peak_spl'], reverse=True)
            for i, peak in enumerate(sorted_peaks[:5]):
                plt.annotate(
                    f"{peak['center_frequency']:.1f}Hz\n{peak['peak_spl']:.1f}dB",
                    xy=(peak['center_frequency'], peak['peak_spl']),
                    xytext=(10, 20),
                    textcoords='offset points',
                    fontsize=9,
                    ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1', color='red')
                )
        
        plt.xlabel('Frequency (Hz)', fontsize=12, fontfamily='Times New Roman')
        plt.ylabel('Sound Pressure Level (dB SPL)', fontsize=12, fontfamily='Times New Roman')
        plt.title('Resonance Peaks Analysis', fontsize=14, fontweight='bold', fontfamily='Times New Roman')
        
        if freq_range:
            plt.xlim(freq_range)
        else:
            plt.xlim([0, frequencies[-1]])
        
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        
        # 峰值分布直方图
        plt.subplot(2, 2, 3)
        if resonance_peaks:
            peak_freqs = [peak['center_frequency'] for peak in resonance_peaks]
            plt.hist(peak_freqs, bins=min(10, len(peak_freqs)), 
                    alpha=0.7, color='skyblue', edgecolor='navy')
            plt.xlabel('Frequency (Hz)', fontsize=10, fontfamily='Times New Roman')
            plt.ylabel('Number of Peaks', fontsize=10, fontfamily='Times New Roman')
            plt.title('Peak Frequency Distribution', fontsize=12, fontfamily='Times New Roman')
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'No Peaks Detected', 
                    transform=plt.gca().transAxes, ha='center', va='center',
                    fontsize=12, color='gray')
            plt.title('Peak Frequency Distribution', fontsize=12, fontfamily='Times New Roman')
        
        # 峰值强度分析
        plt.subplot(2, 2, 4)
        if resonance_peaks:
            peak_spls = [peak['peak_spl'] for peak in resonance_peaks]
            peak_freqs = [peak['center_frequency'] for peak in resonance_peaks]
            
            # 气泡图：频率 vs 声压级，气泡大小表示重要性
            sizes = [(spl - min(peak_spls) + 1) * 50 for spl in peak_spls]
            scatter = plt.scatter(peak_freqs, peak_spls, s=sizes, 
                                alpha=0.6, c=peak_spls, cmap='viridis')
            
            # 添加颜色条
            cbar = plt.colorbar(scatter)
            cbar.set_label('SPL (dB)', fontsize=9)
            
            plt.xlabel('Frequency (Hz)', fontsize=10, fontfamily='Times New Roman')
            plt.ylabel('Peak SPL (dB)', fontsize=10, fontfamily='Times New Roman')
            plt.title('Peak Intensity vs Frequency', fontsize=12, fontfamily='Times New Roman')
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'No Peaks Detected', 
                    transform=plt.gca().transAxes, ha='center', va='center',
                    fontsize=12, color='gray')
            plt.title('Peak Intensity vs Frequency', fontsize=12, fontfamily='Times New Roman')
        
        plt.tight_layout()
        
        # 保存图片
        if save_path:
            full_save_path = self._get_output_path(save_path, subdir) if not os.path.dirname(save_path) else save_path
            plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 共振峰分析图已保存: {full_save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def plot_phase_spectrum(self, frequencies: np.ndarray, phase_deg: np.ndarray,
                           freq_range: Optional[Tuple[float, float]] = None,
                           save_path: Optional[str] = None,
                           show_plot: bool = False,
                           subdir: str = None) -> None:
        """
        绘制相位谱图
        
        Parameters
        ----------
        frequencies : np.ndarray
            频率数组
        phase_deg : np.ndarray
            相位数组（度）
        freq_range : Tuple[float, float], optional
            频率显示范围 (min_freq, max_freq)
        save_path : str, optional
            保存路径，None表示不保存
        show_plot : bool, optional
            是否显示图片，默认False
        """
        plt.figure(figsize=(12, 6))
        plt.plot(frequencies, phase_deg, 'g-', linewidth=0.8, alpha=0.8)
        
        plt.xlabel('Frequency (Hz)', fontsize=12, fontfamily='Times New Roman')
        plt.ylabel('Phase (degrees)', fontsize=12, fontfamily='Times New Roman')
        plt.title('Phase Spectrum Analysis', fontsize=14, fontfamily='Times New Roman')
        
        if freq_range:
            plt.xlim(freq_range)
        else:
            plt.xlim([0, frequencies[-1]])
        
        plt.ylim([-180, 180])
        plt.grid(True, alpha=0.3)
        
        # 添加相位统计信息
        phase_std = np.std(phase_deg)
        plt.text(0.02, 0.98, f'Phase Std: {phase_std:.2f}°', 
                transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            full_save_path = self._get_output_path(save_path, subdir) if not os.path.dirname(save_path) else save_path
            plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 相位谱图已保存: {full_save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def analyze_spectrogram(self, signal: np.ndarray, sample_rate: int,
                           window_length: Optional[int] = None,
                           overlap_ratio: float = 0.75) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        计算时频谱图
        
        Parameters
        ----------
        signal : np.ndarray
            时域信号
        sample_rate : int
            采样率 (Hz)
        window_length : int, optional
            窗长度，None则自动计算
        overlap_ratio : float, optional
            重叠比例，默认0.75
            
        Returns
        -------
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            频率数组、时间数组、时频谱矩阵
        """
        # 自动计算窗长度
        if window_length is None:
            # 选择合适的窗长度，通常为信号长度的1/10到1/20
            window_length = min(len(signal) // 10, int(0.1 * sample_rate))
            # 确保是2的幂次，提高效率
            window_length = 2 ** int(np.log2(window_length))
        
        # 计算重叠长度
        overlap_length = int(window_length * overlap_ratio)
        
        # 使用Hamming窗 (导入scipy.signal模块)
        from scipy import signal as sp_signal
        window = sp_signal.windows.hamming(window_length)
        
        # 计算时频谱
        frequencies, times, Sxx = sp_signal.spectrogram(
            signal,
            fs=sample_rate,
            window=window,
            noverlap=overlap_length,
            nfft=window_length,
            scaling='density'
        )
        
        return frequencies, times, Sxx
    
    def plot_spectrogram(self, frequencies: np.ndarray, times: np.ndarray, 
                        Sxx: np.ndarray, freq_range: Optional[Tuple[float, float]] = None,
                        save_path: Optional[str] = None, show_plot: bool = False,
                        subdir: str = None) -> None:
        """
        绘制时频谱图
        
        Parameters
        ----------
        frequencies : np.ndarray
            频率数组
        times : np.ndarray
            时间数组
        Sxx : np.ndarray
            时频谱矩阵
        freq_range : Tuple[float, float], optional
            频率显示范围 (min_freq, max_freq)
        save_path : str, optional
            保存路径，None表示不保存
        show_plot : bool, optional
            是否显示图片，默认False
        """
        plt.figure(figsize=(12, 8))
        
        # 转换为dB尺度
        Sxx_db = 10 * np.log10(Sxx + 1e-12)  # 添加小值避免log(0)
        
        plt.pcolormesh(times, frequencies, Sxx_db, shading='auto', cmap='jet')
        
        plt.xlabel('Time (s)', fontsize=12, fontfamily='Times New Roman')
        plt.ylabel('Frequency (Hz)', fontsize=12, fontfamily='Times New Roman')
        plt.title('Time-Frequency Spectrogram', fontsize=14, fontfamily='Times New Roman')
        
        if freq_range:
            plt.ylim(freq_range)
        else:
            plt.ylim([0, frequencies[-1]])
        
        # 添加颜色条
        cbar = plt.colorbar()
        cbar.set_label('Power Spectral Density (dB/Hz)', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            full_save_path = self._get_output_path(save_path, subdir) if not os.path.dirname(save_path) else save_path
            plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 时频谱图已保存: {full_save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def analyze_wav_file(self, wav_file_path: str, 
                        max_freq: Optional[float] = None,
                        window_type: str = 'hann') -> Dict:
        """
        分析单个WAV文件
        
        Parameters
        ----------
        wav_file_path : str
            WAV文件路径
        max_freq : float, optional
            最大显示频率 (Hz)，None表示显示全部
        window_type : str, optional
            窗函数类型
            
        Returns
        -------
        Dict
            分析结果字典
        """
        filename = os.path.basename(wav_file_path)
        print(f"\n🎵 分析文件: {filename}")
        print("-" * 50)
        
        try:
            # 加载音频
            signal, sr = self.load_wav_file(wav_file_path)
            
            print(f"✅ 文件加载成功:")
            print(f"   采样率: {sr:,} Hz")
            print(f"   信号长度: {len(signal):,} 点")
            print(f"   时长: {len(signal)/sr:.3f} 秒")
            
            # 转换为频谱
            frequencies, spl_db = self.signal_to_spectrum(signal, sr, window_type)
            
            # 限制频率范围
            if max_freq is not None:
                freq_mask = frequencies <= max_freq
                frequencies = frequencies[freq_mask]
                spl_db = spl_db[freq_mask]
            
            # 统计信息
            print(f"\n📈 频谱统计:")
            print(f"   频率范围: {frequencies[0]:.3f} - {frequencies[-1]:.1f} Hz")
            print(f"   频率点数: {len(frequencies):,}")
            print(f"   声压级范围: {spl_db.min():.1f} - {spl_db.max():.1f} dB SPL")
            
            # 找到峰值频率
            peak_idx = np.argmax(spl_db)
            peak_freq = frequencies[peak_idx]
            peak_spl = spl_db[peak_idx]
            
            print(f"   峰值频率: {peak_freq:.2f} Hz")
            print(f"   峰值声压级: {peak_spl:.1f} dB SPL")
            
            # 检测共振峰
            resonance_result = self.detect_resonance_peaks(
                frequencies, spl_db,
                min_prominence=6.0,    # 6dB突出度阈值
                min_distance=10.0,     # 10Hz最小间隔
                max_peaks=15           # 最多15个峰值
            )
            
            return {
                'file_path': wav_file_path,
                'filename': filename,
                'sample_rate': sr,
                'signal': signal,  # 添加原始信号数据
                'signal_length': len(signal),
                'duration': len(signal) / sr,
                'frequencies': frequencies,
                'spl_db': spl_db,
                'peak_frequency': peak_freq,
                'peak_spl': peak_spl,
                'resonance_peaks': resonance_result,  # 添加共振峰检测结果
                'success': True
            }
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return {
                'file_path': wav_file_path,
                'filename': filename,
                'success': False,
                'error': str(e)
            }
    
    def plot_spectrum(self, analysis_result: Dict, 
                     freq_range: Optional[Tuple[float, float]] = None,
                     spl_range: Optional[Tuple[float, float]] = None,
                     save_path: Optional[str] = None,
                     show_plot: bool = False,
                     subdir: str = None) -> None:
        """
        绘制频谱图
        
        Parameters
        ----------
        analysis_result : Dict
            分析结果
        freq_range : Tuple[float, float], optional
            频率显示范围 (min_freq, max_freq)
        spl_range : Tuple[float, float], optional
            声压级显示范围 (min_spl, max_spl)
        save_path : str, optional
            保存路径，None表示不保存
        show_plot : bool, optional
            是否显示图片，默认False
        """
        if not analysis_result['success']:
            print(f"❌ 无法绘制频谱图: {analysis_result.get('error', '分析失败')}")
            return
        
        frequencies = analysis_result['frequencies']
        spl_db = analysis_result['spl_db']
        filename = analysis_result['filename']
        
        plt.figure(figsize=(12, 8))
        
        # 绘制频谱曲线
        plt.plot(frequencies, spl_db, 'b-', linewidth=0.8, alpha=0.8)
        
        # 标记峰值点
        peak_freq = analysis_result['peak_frequency']
        peak_spl = analysis_result['peak_spl']
        plt.plot(peak_freq, peak_spl, 'ro', markersize=8, 
                label=f'Peak: {peak_freq:.2f} Hz, {peak_spl:.1f} dB')
        
        # 设置坐标轴
        plt.xlabel('Frequency (Hz)', fontsize=12, fontfamily='Times New Roman')
        plt.ylabel('Sound Pressure Level (dB SPL)', fontsize=12, fontfamily='Times New Roman')
        plt.title(f'Frequency Spectrum Analysis - {filename}', 
                 fontsize=14, fontfamily='Times New Roman')
        
        # 设置显示范围
        if freq_range:
            plt.xlim(freq_range)
        else:
            plt.xlim([0, frequencies[-1]])
            
        if spl_range:
            plt.ylim(spl_range)
        
        # 网格和图例
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        
        # 添加频率分辨率信息
        freq_res = frequencies[1] - frequencies[0]
        plt.text(0.02, 0.98, f'Frequency Resolution: {freq_res:.4f} Hz', 
                transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # 保存图片
        if save_path:
            full_save_path = self._get_output_path(save_path, subdir) if not os.path.dirname(save_path) else save_path
            plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 频谱图已保存: {full_save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def comprehensive_analysis(self, analysis_result: Dict,
                              freq_range: Optional[Tuple[float, float]] = None,
                              time_range: Optional[float] = None,
                              save_prefix: Optional[str] = None,
                              show_plot: bool = False,
                              subdir: str = None) -> None:
        """
        执行全面的综合分析（时域+频域+相位+时频）
        
        Parameters
        ----------
        analysis_result : Dict
            分析结果字典
        freq_range : Tuple[float, float], optional
            频率显示范围 (min_freq, max_freq)
        time_range : float, optional
            时域显示的最大时长（秒）
        save_prefix : str, optional
            保存文件的前缀，None表示不保存
        show_plot : bool, optional
            是否显示图片，默认False
        """
        if not analysis_result['success']:
            print(f"❌ 无法进行综合分析: {analysis_result.get('error', '分析失败')}")
            return
        
        signal = analysis_result['signal']
        sr = analysis_result['sample_rate']
        filename = analysis_result['filename']
        frequencies = analysis_result['frequencies']
        spl_db = analysis_result['spl_db']
        
        print(f"\n🔍 开始综合分析: {filename}")
        print("-" * 60)
        
        # 创建综合分析图
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle(f'Comprehensive Acoustic Analysis - {filename}', 
                    fontsize=16, fontfamily='Times New Roman')
        
        # 1. 时域分析 (左上)
        plt.subplot(2, 2, 1)
        time_axis = np.arange(len(signal)) / sr
        if time_range is not None:
            max_samples = int(time_range * sr)
            if len(signal) > max_samples:
                signal_display = signal[:max_samples]
                time_axis_display = time_axis[:max_samples]
            else:
                signal_display = signal
                time_axis_display = time_axis
        else:
            signal_display = signal
            time_axis_display = time_axis
        
        plt.plot(time_axis_display, signal_display, 'b-', linewidth=0.8, alpha=0.8)
        plt.xlabel('Time (s)', fontsize=10, fontfamily='Times New Roman')
        plt.ylabel('Amplitude', fontsize=10, fontfamily='Times New Roman')
        plt.title('Time Domain', fontsize=12, fontfamily='Times New Roman')
        plt.grid(True, alpha=0.3)
        
        # 添加时域统计
        rms_value = np.sqrt(np.mean(signal**2))
        peak_value = np.max(np.abs(signal))
        plt.text(0.02, 0.98, f'RMS: {rms_value:.4f}\nPeak: {peak_value:.4f}', 
                transform=plt.gca().transAxes, fontsize=8,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # 2. 频域分析 (右上)
        plt.subplot(2, 2, 2)
        if freq_range:
            freq_mask = frequencies <= freq_range[1]
            freq_display = frequencies[freq_mask]
            spl_display = spl_db[freq_mask]
        else:
            freq_display = frequencies
            spl_display = spl_db
        
        plt.plot(freq_display, spl_display, 'r-', linewidth=0.8, alpha=0.8)
        
        # 标记峰值
        peak_freq = analysis_result['peak_frequency']
        peak_spl = analysis_result['peak_spl']
        if freq_range is None or peak_freq <= freq_range[1]:
            plt.plot(peak_freq, peak_spl, 'ro', markersize=6, 
                    label=f'Peak: {peak_freq:.2f} Hz')
            plt.legend(fontsize=8)
        
        plt.xlabel('Frequency (Hz)', fontsize=10, fontfamily='Times New Roman')
        plt.ylabel('SPL (dB)', fontsize=10, fontfamily='Times New Roman')
        plt.title('Frequency Spectrum', fontsize=12, fontfamily='Times New Roman')
        plt.grid(True, alpha=0.3)
        
        # 3. 相位分析 (左下)
        plt.subplot(2, 2, 3)
        phase_frequencies, phase_deg = self.analyze_phase_spectrum(signal, sr)
        
        if freq_range:
            phase_mask = phase_frequencies <= freq_range[1]
            phase_freq_display = phase_frequencies[phase_mask]
            phase_display = phase_deg[phase_mask]
        else:
            phase_freq_display = phase_frequencies
            phase_display = phase_deg
        
        plt.plot(phase_freq_display, phase_display, 'g-', linewidth=0.8, alpha=0.8)
        plt.xlabel('Frequency (Hz)', fontsize=10, fontfamily='Times New Roman')
        plt.ylabel('Phase (degrees)', fontsize=10, fontfamily='Times New Roman')
        plt.title('Phase Spectrum', fontsize=12, fontfamily='Times New Roman')
        plt.ylim([-180, 180])
        plt.grid(True, alpha=0.3)
        
        # 添加相位统计
        phase_std = np.std(phase_display)
        plt.text(0.02, 0.98, f'Phase Std: {phase_std:.2f}°', 
                transform=plt.gca().transAxes, fontsize=8,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        # 4. 时频分析 (右下)
        plt.subplot(2, 2, 4)
        spec_freqs, spec_times, Sxx = self.analyze_spectrogram(signal, sr)
        
        # 转换为dB尺度
        Sxx_db = 10 * np.log10(Sxx + 1e-12)
        
        plt.pcolormesh(spec_times, spec_freqs, Sxx_db, shading='auto', cmap='jet')
        plt.xlabel('Time (s)', fontsize=10, fontfamily='Times New Roman')
        plt.ylabel('Frequency (Hz)', fontsize=10, fontfamily='Times New Roman')
        plt.title('Time-Frequency Spectrogram', fontsize=12, fontfamily='Times New Roman')
        
        if freq_range:
            plt.ylim([0, freq_range[1]])
        else:
            plt.ylim([0, spec_freqs[-1]])
        
        # 添加小型颜色条
        cbar = plt.colorbar()
        cbar.set_label('PSD (dB/Hz)', fontsize=9)
        
        plt.tight_layout()
        
        # 保存综合分析图
        if save_prefix:
            save_path = f"{save_prefix}_comprehensive_analysis.png"
            full_save_path = self._get_output_path(save_path, subdir)
            plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 综合分析图已保存: {full_save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        # 分别保存各个分析图
        if save_prefix:
            print(f"\n📊 生成独立分析图...")
            
            # 时域图
            self.plot_time_domain(signal, sr, max_duration=time_range,
                                 save_path=f"{save_prefix}_time_domain.png",
                                 show_plot=False, subdir=subdir)
            
            # 相位图  
            self.plot_phase_spectrum(phase_frequencies, phase_deg, 
                                   freq_range=freq_range,
                                   save_path=f"{save_prefix}_phase_domain.png",
                                   show_plot=False, subdir=subdir)
            
            # 时频图
            self.plot_spectrogram(spec_freqs, spec_times, Sxx,
                                freq_range=freq_range,
                                save_path=f"{save_prefix}_spectrogram.png",
                                show_plot=False, subdir=subdir)
            
            # 共振峰分析图
            if 'resonance_peaks' in analysis_result and analysis_result['resonance_peaks']:
                self.plot_resonance_peaks(
                    frequencies, spl_db, analysis_result['resonance_peaks'],
                    freq_range=freq_range,
                    save_path=f"{save_prefix}_resonance_peaks.png",
                    show_plot=False, subdir=subdir
                )
        
        print(f"🎉 综合分析完成!")
    
    def batch_analyze_directory(self, data_dir: str = "data", 
                               max_freq: Optional[float] = 2000,
                               plot_individual: bool = True,
                               plot_comparison: bool = False,
                               comprehensive_analysis: bool = False,
                               time_range: Optional[float] = 1.0) -> Dict[str, List[Dict]]:
        """
        批量分析目录中的所有WAV文件
        
        Parameters
        ----------
        data_dir : str, optional
            数据目录，默认"data"
        max_freq : float, optional
            最大分析频率，默认2000Hz
        plot_individual : bool, optional
            是否绘制单独的频谱图
        plot_comparison : bool, optional
            是否绘制对比图，默认False（已禁用）
        comprehensive_analysis : bool, optional
            是否进行综合分析（时域+频域+相位+时频），默认False
        time_range : float, optional
            时域分析的显示时长（秒），默认1.0秒
            
        Returns
        -------
        Dict[str, List[Dict]]
            所有分析结果
        """
        print("🎯 批量频谱分析开始...")
        print("=" * 60)
        
        if not os.path.exists(data_dir):
            print(f"❌ 数据目录不存在: {data_dir}")
            return {}
        
        all_results = {}
        
        # 遍历所有子目录
        subdirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        subdirs.sort()
        
        for subdir in subdirs:
            subdir_path = os.path.join(data_dir, subdir)
            wav_files = glob.glob(os.path.join(subdir_path, "*.wav"))
            wav_files.sort()
            
            if not wav_files:
                continue
            
            print(f"\n📁 处理目录: {subdir}")
            subdir_results = []
            
            for wav_file in wav_files:
                # 分析单个文件
                result = self.analyze_wav_file(wav_file, max_freq)
                subdir_results.append(result)
                
                # 绘制单独频谱图
                if plot_individual and result['success']:
                    save_name = f"{subdir}_{result['filename'][:-4]}_frequency_domain.png"
                    self.plot_spectrum(result, 
                                     freq_range=(0, max_freq),
                                     save_path=save_name,
                                     show_plot=False,
                                     subdir=subdir)
                    
                    # 绘制共振峰分析图
                    if 'resonance_peaks' in result and result['resonance_peaks']:
                        self.plot_resonance_peaks(
                            result['frequencies'], result['spl_db'], result['resonance_peaks'],
                            freq_range=(0, max_freq) if max_freq else None,
                            save_path=f"{subdir}_{result['filename'][:-4]}_resonance_peaks.png",
                            show_plot=False,
                            subdir=subdir
                        )
                
                # 执行综合分析
                if comprehensive_analysis and result['success']:
                    save_prefix = f"{subdir}_{result['filename'][:-4]}"
                    self.comprehensive_analysis(
                        result,
                        freq_range=(0, max_freq) if max_freq else None,
                        time_range=time_range,
                        save_prefix=save_prefix,
                        show_plot=False,
                        subdir=subdir
                    )
            
            all_results[subdir] = subdir_results
        
        # 绘制对比图
        if plot_comparison:
            self.plot_comparison_spectra(all_results, max_freq, show_plot=False)
        
        return all_results
    
    def plot_comparison_spectra(self, all_results: Dict[str, List[Dict]], 
                               max_freq: Optional[float] = None,
                               show_plot: bool = False) -> None:
        """
        绘制对比频谱图
        
        Parameters
        ----------
        all_results : Dict[str, List[Dict]]
            所有分析结果
        max_freq : float, optional
            最大显示频率
        show_plot : bool, optional
            是否显示图片，默认False
        """
        print(f"\n📊 生成对比频谱图...")
        
        # 收集成功的分析结果
        successful_results = []
        for subdir, results in all_results.items():
            for result in results:
                if result['success']:
                    successful_results.append((subdir, result))
        
        if len(successful_results) == 0:
            print("❌ 没有成功的分析结果用于对比")
            return
        
        # 创建对比图
        plt.figure(figsize=(16, 10))
        
        # 子图1: 所有频谱叠加
        plt.subplot(2, 2, 1)
        colors = plt.cm.tab10(np.linspace(0, 1, len(successful_results)))
        
        for i, (subdir, result) in enumerate(successful_results):
            frequencies = result['frequencies']
            spl_db = result['spl_db']
            
            if max_freq:
                freq_mask = frequencies <= max_freq
                frequencies = frequencies[freq_mask]
                spl_db = spl_db[freq_mask]
            
            label = f"{subdir}_{result['filename'][:-4]}"
            plt.plot(frequencies, spl_db, color=colors[i], 
                    linewidth=1.0, alpha=0.8, label=label)
        
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('SPL (dB)')
        plt.title('All Spectra Comparison')
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 子图2: 按目录分组的平均频谱
        plt.subplot(2, 2, 2)
        
        dir_averages = {}
        for subdir in all_results.keys():
            successful_in_dir = [r for r in all_results[subdir] if r['success']]
            if successful_in_dir:
                # 计算该目录的平均频谱
                all_spl = []
                common_freqs = None
                
                for result in successful_in_dir:
                    freqs = result['frequencies']
                    spl = result['spl_db']
                    
                    if max_freq:
                        freq_mask = freqs <= max_freq
                        freqs = freqs[freq_mask]
                        spl = spl[freq_mask]
                    
                    if common_freqs is None:
                        common_freqs = freqs
                    
                    # 插值到统一频率轴
                    spl_interp = np.interp(common_freqs, freqs, spl)
                    all_spl.append(spl_interp)
                
                if all_spl:
                    avg_spl = np.mean(all_spl, axis=0)
                    dir_averages[subdir] = (common_freqs, avg_spl)
        
        # 绘制目录平均频谱
        for i, (subdir, (freqs, avg_spl)) in enumerate(dir_averages.items()):
            plt.plot(freqs, avg_spl, linewidth=2.0, 
                    label=f'{subdir} (avg)', marker='o', markersize=3, alpha=0.8)
        
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('SPL (dB)')
        plt.title('Average Spectra by Directory')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # 子图3: 峰值频率统计
        plt.subplot(2, 2, 3)
        
        peak_freqs = []
        peak_spls = []
        labels = []
        
        for subdir, result in successful_results:
            peak_freqs.append(result['peak_frequency'])
            peak_spls.append(result['peak_spl'])
            labels.append(f"{subdir}_{result['filename'][:-4]}")
        
        x_pos = np.arange(len(peak_freqs))
        bars = plt.bar(x_pos, peak_spls, color=colors[:len(peak_freqs)], alpha=0.8)
        
        # 在柱上标注频率
        for i, (freq, spl) in enumerate(zip(peak_freqs, peak_spls)):
            plt.text(i, spl + 1, f'{freq:.1f}Hz', 
                    ha='center', va='bottom', fontsize=8, rotation=45)
        
        plt.xlabel('Files')
        plt.ylabel('Peak SPL (dB)')
        plt.title('Peak Frequency & SPL')
        plt.xticks(x_pos, labels, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        # 子图4: 频率分辨率信息
        plt.subplot(2, 2, 4)
        plt.axis('off')
        
        # 统计信息文本
        info_text = "分析统计信息:\n\n"
        info_text += f"总文件数: {len(successful_results)}\n"
        info_text += f"目标频率分辨率: {self.target_freq_resolution:.3f} Hz\n\n"
        
        # 各文件的实际分辨率
        info_text += "实际频率分辨率:\n"
        for subdir, result in successful_results[:10]:  # 只显示前10个
            freqs = result['frequencies']
            actual_res = freqs[1] - freqs[0] if len(freqs) > 1 else 0
            info_text += f"{subdir}_{result['filename'][:-4]}: {actual_res:.4f} Hz\n"
        
        if len(successful_results) > 10:
            info_text += f"... (共{len(successful_results)}个文件)\n"
        
        plt.text(0.1, 0.9, info_text, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        comparison_save_path = self._get_output_path('data_analysis_comparison.png')
        plt.savefig(comparison_save_path, dpi=300, bbox_inches='tight')
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        print(f"✅ 对比分析图已保存: {comparison_save_path}")


def main():
    """
    主函数：执行WAV文件频谱分析
    """
    print("🎵 WAV文件频谱分析工具")
    print("=" * 80)
    print("功能：时域信号 → 频谱图（频率精确到0.01Hz，声压级单位dB）")
    print()
    
    # 分析模式选择
    print("📋 请选择分析模式:")
    print("1. 💼 批量分析 (分析data目录中的所有WAV文件)")
    print("2. 📁 单个文件分析 (分析指定的WAV文件)")
    print("3. 🎯 演示分析 (使用示例文件)")
    
    try:
        choice = input("\n请输入选择 (1/2/3): ").strip()
    except KeyboardInterrupt:
        print("\n👋 分析已取消")
        return
    
    if choice == "1":
        # 批量分析模式
        print("\n🔄 启动批量分析模式...")
        batch_analysis_mode()
        
    elif choice == "2":
        # 单个文件分析模式
        print("\n📁 启动单个文件分析模式...")
        single_file_analysis_mode()
        
    elif choice == "3":
        # 演示模式
        print("\n🎯 启动演示分析模式...")
        demo_analysis_mode()
        
    else:
        print("❌ 无效选择，请输入 1、2 或 3")
        return


def batch_analysis_mode():
    """
    批量分析模式
    """
    # 创建分析器
    analyzer = SpectrumAnalyzer(target_freq_resolution=0.01)
    
    # 检查数据目录
    if not os.path.exists("data"):
        print("❌ 未找到data目录")
        return
    
    # 批量分析
    results = analyzer.batch_analyze_directory(
        data_dir="data",
        max_freq=2000,  # 分析0-2000Hz范围
        plot_individual=True,   # 绘制单独频谱图
        plot_comparison=False,   # 不绘制对比图
        comprehensive_analysis=False,  # 综合分析（时域+频域+相位+时频）
        time_range=1.0  # 时域显示1秒
    )
    
    # 统计结果
    total_files = sum(len(subdir_results) for subdir_results in results.values())
    successful_files = sum(len([r for r in subdir_results if r['success']]) 
                          for subdir_results in results.values())
    
    print(f"\n🎉 批量分析完成!")
    print(f"📊 处理文件: {total_files} 个")
    print(f"✅ 成功分析: {successful_files} 个")
    print(f"📈 成功率: {successful_files/total_files*100:.1f}%")
    
    print(f"\n📁 生成的文件 (按数据文件夹分别保存在 ana_res/ 目录下):")
    print(f"   各子目录/*_frequency_domain.png - 频谱图")
    print(f"   各子目录/*_resonance_peaks.png - 共振峰分析图")


def single_file_analysis_mode():
    """
    单个文件分析模式
    """
    try:
        # 获取文件路径
        file_path = input("📁 请输入WAV文件路径: ").strip()
        
        if not file_path:
            print("❌ 未输入文件路径")
            return
            
        # 移除可能的引号
        file_path = file_path.strip('"\'')
        
        # 询问分析参数
        print("\n⚙️ 分析参数设置:")
        
        try:
            max_freq_input = input("🔊 最大分析频率 (Hz, 默认2000): ").strip()
            max_freq = float(max_freq_input) if max_freq_input else 2000.0
        except ValueError:
            max_freq = 2000.0
        
        comprehensive_input = input("🔍 是否进行综合分析 (y/n, 默认y): ").strip().lower()
        comprehensive = comprehensive_input not in ['n', 'no', '否']
        
        save_prefix = input("💾 保存文件前缀 (可选, 默认自动): ").strip()
        if not save_prefix:
            save_prefix = None
        
        # 执行分析
        result = analyze_single_wav_file(
            wav_file_path=file_path,
            max_freq=max_freq,
            comprehensive=comprehensive,
            save_prefix=save_prefix
        )
        
        if result['success']:
            print(f"\n🎉 单个文件分析完成!")
        else:
            print(f"❌ 分析失败: {result.get('error', '未知错误')}")
            
    except KeyboardInterrupt:
        print("\n👋 分析已取消")
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")


def demo_analysis_mode():
    """
    演示分析模式
    """
    print("🎯 演示模式 - 自动寻找示例文件进行分析")
    
    # 寻找示例文件
    demo_file = None
    search_paths = ["data", ".", "examples", "samples"]
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.wav'):
                        demo_file = os.path.join(root, file)
                        break
                if demo_file:
                    break
        if demo_file:
            break
    
    if not demo_file:
        print("❌ 未找到可用于演示的WAV文件")
        print("💡 建议:")
        print("   - 在data目录中放置WAV文件")
        print("   - 或使用选项2手动指定文件路径")
        return
    
    print(f"📁 找到演示文件: {demo_file}")
    print("🔍 使用默认参数进行综合分析...")
    
    # 执行演示分析
    result = analyze_single_wav_file(
        wav_file_path=demo_file,
        max_freq=2000,
        comprehensive=True,
        save_prefix="demo"
    )
    
    if result['success']:
        print(f"\n🎉 演示分析完成!")
        print("\n📚 分析结果说明:")
        print("   🎵 频谱图显示频率与声压级的关系")
        print("   📊 综合分析包含时域、频域、相位、时频四个维度")
        print("   🔍 关键指标:")
        print(f"     - 峰值频率: {result['peak_frequency']:.2f} Hz")
        print(f"     - 峰值声压级: {result['peak_spl']:.1f} dB SPL")
        print(f"     - 频率分辨率: {result['frequencies'][1] - result['frequencies'][0]:.4f} Hz")
    else:
        print(f"❌ 演示分析失败: {result.get('error', '未知错误')}")
    
    print(f"\n🔍 分析结果说明:")
    print(f"   横轴: 频率 (Hz)")
    print(f"   纵轴: 声压级 (dB SPL)")
    print(f"   频率分辨率: 0.01 Hz (目标值)")
    print(f"   参考声压: 20 μPa")
    
    print(f"\n✨ 功能特性:")
    print(f"   🕐 时域分析 - 波形图和统计信息")
    print(f"   📐 相位分析 - 频率-相位关系")
    print(f"   🎵 时频分析 - 谱图显示时变频谱")
    print(f"   📊 综合分析 - 四合一分析图表")


def analyze_single_wav_file(wav_file_path: str, 
                           max_freq: Optional[float] = 2000,
                           comprehensive: bool = True,
                           save_prefix: Optional[str] = None,
                           auto_subdir: bool = True) -> Dict:
    """
    分析单个WAV文件的完整功能
    
    Parameters
    ----------
    wav_file_path : str
        WAV文件路径
    max_freq : float, optional
        最大分析频率 (Hz)，默认2000Hz
    comprehensive : bool, optional
        是否进行综合分析（时域+频域+相位+时频），默认True
    save_prefix : str, optional
        保存文件前缀，None则自动生成
    auto_subdir : bool, optional
        是否自动按数据文件夹创建子目录，默认True
        
    Returns
    -------
    Dict
        分析结果字典
    """
    print("🎵 单个WAV文件声学分析")
    print("=" * 60)
    
    if not os.path.exists(wav_file_path):
        print(f"❌ 文件不存在: {wav_file_path}")
        return {'success': False, 'error': 'File not found'}
    
    # 创建分析器
    analyzer = SpectrumAnalyzer(target_freq_resolution=0.01)
    
    # 分析文件
    print(f"📁 分析文件: {os.path.basename(wav_file_path)}")
    result = analyzer.analyze_wav_file(wav_file_path, max_freq)
    
    if not result['success']:
        print(f"❌ 分析失败: {result.get('error', '未知错误')}")
        return result
    
    # 自动生成保存前缀
    if save_prefix is None:
        basename = os.path.splitext(os.path.basename(wav_file_path))[0]
        save_prefix = f"single_{basename}"
    
    # 自动提取数据文件夹名称
    subdir = None
    if auto_subdir:
        subdir = analyzer._extract_data_folder_name(wav_file_path)
        print(f"📁 自动识别数据文件夹: {subdir}")
    
    print(f"\n📊 开始绘制分析图表...")
    
    # 绘制频谱图
    analyzer.plot_spectrum(
        result, 
        freq_range=(0, max_freq) if max_freq else None,
        save_path=f"{save_prefix}_frequency_spectrum.png",
        show_plot=False,
        subdir=subdir
    )
    
    # 绘制共振峰分析图
    if 'resonance_peaks' in result and result['resonance_peaks']:
        analyzer.plot_resonance_peaks(
            result['frequencies'], result['spl_db'], result['resonance_peaks'],
            freq_range=(0, max_freq) if max_freq else None,
            save_path=f"{save_prefix}_resonance_peaks.png",
            show_plot=False,
            subdir=subdir
        )
    
    if comprehensive:
        # 执行综合分析
        print(f"🔍 执行综合分析...")
        analyzer.comprehensive_analysis(
            result,
            freq_range=(0, max_freq) if max_freq else None,
            time_range=1.0,  # 时域显示前1秒
            save_prefix=save_prefix,
            show_plot=False,
            subdir=subdir
        )
        
        print(f"\n✅ 综合分析完成！")
        if subdir:
            print(f"📁 生成的文件 (保存在 {analyzer.output_dir}/{subdir}/ 目录下):")
        else:
            print(f"📁 生成的文件 (保存在 {analyzer.output_dir}/ 目录下):")
        print(f"   {save_prefix}_frequency_spectrum.png - 频谱图")
        print(f"   {save_prefix}_comprehensive_analysis.png - 四合一综合分析图")
        print(f"   {save_prefix}_time_domain.png - 时域分析图")
        print(f"   {save_prefix}_phase_domain.png - 相位谱图")
        print(f"   {save_prefix}_spectrogram.png - 时频谱图")
        if 'resonance_peaks' in result and result['resonance_peaks']:
            print(f"   {save_prefix}_resonance_peaks.png - 共振峰分析图")
    else:
        print(f"\n✅ 频谱分析完成！")
        print(f"📁 生成的文件:")
        print(f"   {save_prefix}_frequency_spectrum.png - 频谱图")
        if 'resonance_peaks' in result and result['resonance_peaks']:
            print(f"   {save_prefix}_resonance_peaks.png - 共振峰分析图")
    
    # 显示关键分析结果
    print(f"\n🔍 分析结果摘要:")
    print(f"   文件时长: {result['duration']:.3f} 秒")
    print(f"   采样率: {result['sample_rate']:,} Hz")
    print(f"   峰值频率: {result['peak_frequency']:.2f} Hz")
    print(f"   峰值声压级: {result['peak_spl']:.1f} dB SPL")
    print(f"   频率范围: {result['frequencies'][0]:.3f} - {result['frequencies'][-1]:.1f} Hz")
    print(f"   频率分辨率: {result['frequencies'][1] - result['frequencies'][0]:.4f} Hz")
    
    # 显示共振峰统计信息
    if 'resonance_peaks' in result and result['resonance_peaks']:
        resonance_stats = result['resonance_peaks']['statistics']
        print(f"\n🎯 共振峰特征提取:")
        print(f"   检测到共振峰: {resonance_stats['total_peaks']} 个")
        if resonance_stats['total_peaks'] > 0:
            print(f"   频率分布: {resonance_stats['frequency_range'][0]:.1f} - {resonance_stats['frequency_range'][1]:.1f} Hz")
            print(f"   声压级分布: {resonance_stats['spl_range'][0]:.1f} - {resonance_stats['spl_range'][1]:.1f} dB SPL")
            print(f"   平均频率: {resonance_stats['mean_frequency']:.1f} Hz")
            if resonance_stats['dominant_peak']:
                dominant = resonance_stats['dominant_peak']
                print(f"   主导共振峰: {dominant['center_frequency']:.1f} Hz, {dominant['peak_spl']:.1f} dB SPL")
    
    return result


def example_comprehensive_analysis():
    """
    综合分析功能的使用示例
    """
    print("🎯 综合分析功能演示")
    print("=" * 50)
    
    # 创建分析器
    analyzer = SpectrumAnalyzer(target_freq_resolution=0.01)
    
    # 检查数据目录
    if not os.path.exists("data"):
        print("❌ 未找到data目录，无法演示")
        return
    
    # 找到第一个WAV文件进行演示
    wav_file = None
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith('.wav'):
                wav_file = os.path.join(root, file)
                break
        if wav_file:
            break
    
    if not wav_file:
        print("❌ 未找到WAV文件进行演示")
        return
    
    print(f"📁 使用文件: {os.path.basename(wav_file)}")
    
    # 分析单个文件
    result = analyzer.analyze_wav_file(wav_file, max_freq=2000)
    
    if result['success']:
        # 执行综合分析
        print("\n🔍 执行综合分析...")
        analyzer.comprehensive_analysis(
            result,
            freq_range=(0, 2000),  # 频率范围 0-2000Hz
            time_range=0.5,        # 时域显示前0.5秒
            save_prefix="demo",    # 保存文件前缀
            show_plot=False
        )
        
        print("\n✅ 演示完成！")
        print(f"📁 生成的文件 (保存在 {analyzer.output_dir}/ 目录下):")
        print("   demo_comprehensive_analysis.png - 四合一综合分析图")
        print("   demo_time_domain.png - 时域分析图")
        print("   demo_phase_domain.png - 相位谱图")
        print("   demo_spectrogram.png - 时频谱图")
    else:
        print(f"❌ 分析失败: {result.get('error', '未知错误')}")


def quick_analyze(wav_file_path: str, comprehensive: bool = True, auto_subdir: bool = True) -> Dict:
    """
    快速分析单个WAV文件的便捷函数
    
    Parameters
    ----------
    wav_file_path : str
        WAV文件路径
    comprehensive : bool, optional
        是否进行综合分析，默认True
    auto_subdir : bool, optional
        是否自动按数据文件夹创建子目录，默认True
        
    Returns
    -------
    Dict
        分析结果字典
        
    Examples
    --------
    >>> # 基本分析
    >>> result = quick_analyze("path/to/audio.wav")
    >>> # 只做频谱分析
    >>> result = quick_analyze("path/to/audio.wav", comprehensive=False)
    >>> # 不自动创建子目录
    >>> result = quick_analyze("path/to/audio.wav", auto_subdir=False)
    """
    return analyze_single_wav_file(
        wav_file_path=wav_file_path,
        max_freq=2000,
        comprehensive=comprehensive,
        save_prefix=None,
        auto_subdir=auto_subdir
    )


def analyze_resonance_peaks_only(wav_file_path: str, 
                                min_prominence: float = 6.0,
                                min_distance: float = 10.0,
                                max_freq: float = 2000,
                                save_prefix: Optional[str] = None) -> Dict:
    """
    专门进行共振峰分析的便捷函数
    
    Parameters
    ----------
    wav_file_path : str
        WAV文件路径
    min_prominence : float, optional
        最小峰值突出度 (dB)，默认6.0dB
    min_distance : float, optional
        相邻峰值间最小频率间隔 (Hz)，默认10.0Hz
    max_freq : float, optional
        最大分析频率 (Hz)，默认2000Hz
    save_prefix : str, optional
        保存文件前缀，None则自动生成
        
    Returns
    -------
    Dict
        包含详细共振峰信息的分析结果
        
    Examples
    --------
    >>> # 基本共振峰分析
    >>> result = analyze_resonance_peaks_only("data/S1R1/record1.wav")
    >>> # 自定义参数的共振峰分析
    >>> result = analyze_resonance_peaks_only("data/S1R1/record1.wav", 
    ...                                      min_prominence=8.0, 
    ...                                      min_distance=15.0)
    """
    print("🎯 专门共振峰分析模式")
    print("=" * 50)
    
    # 创建分析器
    analyzer = SpectrumAnalyzer(target_freq_resolution=0.01)
    
    # 基础频谱分析
    result = analyzer.analyze_wav_file(wav_file_path, max_freq)
    
    if not result['success']:
        return result
    
    # 自动生成保存前缀
    if save_prefix is None:
        basename = os.path.splitext(os.path.basename(wav_file_path))[0]
        save_prefix = f"resonance_{basename}"
    
    # 提取数据文件夹名称
    subdir = analyzer._extract_data_folder_name(wav_file_path)
    
    # 重新进行共振峰检测（使用自定义参数）
    resonance_result = analyzer.detect_resonance_peaks(
        result['frequencies'], result['spl_db'],
        min_prominence=min_prominence,
        min_distance=min_distance,
        max_peaks=20
    )
    
    # 更新结果
    result['resonance_peaks'] = resonance_result
    
    # 绘制共振峰分析图
    analyzer.plot_resonance_peaks(
        result['frequencies'], result['spl_db'], resonance_result,
        freq_range=(0, max_freq),
        save_path=f"{save_prefix}_analysis.png",
        show_plot=False,
        subdir=subdir
    )
    
    # 输出详细的共振峰信息
    print(f"\n🎯 共振峰详细信息:")
    resonance_peaks = resonance_result['resonance_peaks']
    if resonance_peaks:
        print(f"{'排名':<4} {'中心频率(Hz)':<12} {'声压级(dB)':<12} {'突出度(dB)':<12}")
        print("-" * 50)
        for peak in resonance_peaks:
            print(f"{peak['rank']:<4} {peak['center_frequency']:<12.2f} "
                  f"{peak['peak_spl']:<12.1f} {peak['prominence']:<12.1f}")
    
    print(f"\n✅ 共振峰分析完成！")
    print(f"📁 生成文件: {save_prefix}_analysis.png")
    
    return result


if __name__ == "__main__":
    main()
    
    # 使用示例：
    # 
    # 1. 运行主程序（交互式选择模式）:
    #    python wav_to_spectrum_analyzer.py
    #
    # 2. 快速分析单个文件（编程方式）:
    #    from wav_to_spectrum_analyzer import quick_analyze
    #    result = quick_analyze("path/to/your/audio.wav")
    #
    # 3. 高级单个文件分析（编程方式）:
    #    from wav_to_spectrum_analyzer import analyze_single_wav_file
    #    result = analyze_single_wav_file("path/to/your/audio.wav", 
    #                                   max_freq=4000, 
    #                                   comprehensive=True,
    #                                   save_prefix="my_analysis")
    #
    # 4. 专门共振峰分析（编程方式）:
    #    from wav_to_spectrum_analyzer import analyze_resonance_peaks_only
    #    result = analyze_resonance_peaks_only("path/to/your/audio.wav",
    #                                         min_prominence=6.0,
    #                                         min_distance=10.0)
    #
    # 5. 运行综合分析演示:
    #    example_comprehensive_analysis()
