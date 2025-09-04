#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAV文件频谱分析专用工具
=====================

将时域WAV信号转换为高精度频谱图
横轴：频率（精确到0.01Hz）
纵轴：声压级（dB）

主要功能：
- 高精度FFT分析
- 声压级计算（dB）
- 频率分辨率优化
- 批量处理WAV文件
- 专业频谱图绘制
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from typing import Tuple, List, Dict, Optional
from scipy.io import wavfile
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
    频谱分析器类
    
    专门用于将WAV时域信号转换为高精度频谱图
    支持精确到0.01Hz的频率分辨率
    """
    
    def __init__(self, target_freq_resolution: float = 0.01):
        """
        初始化频谱分析器
        
        Parameters
        ----------
        target_freq_resolution : float, optional
            目标频率分辨率 (Hz)，默认0.01Hz
        """
        self.target_freq_resolution = target_freq_resolution
        self.reference_pressure = 20e-6  # 参考声压 20μPa (空气中的标准)
        
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
            
            return {
                'file_path': wav_file_path,
                'filename': filename,
                'sample_rate': sr,
                'signal_length': len(signal),
                'duration': len(signal) / sr,
                'frequencies': frequencies,
                'spl_db': spl_db,
                'peak_frequency': peak_freq,
                'peak_spl': peak_spl,
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
                     save_path: Optional[str] = None) -> None:
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
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ 频谱图已保存: {save_path}")
        
        plt.show()
    
    def batch_analyze_directory(self, data_dir: str = "data", 
                               max_freq: Optional[float] = 2000,
                               plot_individual: bool = True,
                               plot_comparison: bool = True) -> Dict[str, List[Dict]]:
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
            是否绘制对比图
            
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
                    save_name = f"spectrum_{subdir}_{result['filename'][:-4]}.png"
                    self.plot_spectrum(result, 
                                     freq_range=(0, max_freq),
                                     save_path=save_name)
            
            all_results[subdir] = subdir_results
        
        # 绘制对比图
        if plot_comparison:
            self.plot_comparison_spectra(all_results, max_freq)
        
        return all_results
    
    def plot_comparison_spectra(self, all_results: Dict[str, List[Dict]], 
                               max_freq: Optional[float] = None) -> None:
        """
        绘制对比频谱图
        
        Parameters
        ----------
        all_results : Dict[str, List[Dict]]
            所有分析结果
        max_freq : float, optional
            最大显示频率
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
        plt.savefig('spectrum_comparison_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✅ 对比分析图已保存: spectrum_comparison_analysis.png")


def main():
    """
    主函数：执行WAV文件频谱分析
    """
    print("🎵 WAV文件频谱分析工具")
    print("=" * 80)
    print("功能：时域信号 → 频谱图（频率精确到0.01Hz，声压级单位dB）")
    print()
    
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
        plot_comparison=True    # 绘制对比图
    )
    
    # 统计结果
    total_files = sum(len(subdir_results) for subdir_results in results.values())
    successful_files = sum(len([r for r in subdir_results if r['success']]) 
                          for subdir_results in results.values())
    
    print(f"\n🎉 分析完成!")
    print(f"📊 处理文件: {total_files} 个")
    print(f"✅ 成功分析: {successful_files} 个")
    print(f"📈 成功率: {successful_files/total_files*100:.1f}%")
    
    print(f"\n📁 生成的文件:")
    print(f"   spectrum_*.png - 各文件的频谱图")
    print(f"   spectrum_comparison_analysis.png - 对比分析图")
    
    print(f"\n🔍 分析结果说明:")
    print(f"   横轴: 频率 (Hz)")
    print(f"   纵轴: 声压级 (dB SPL)")
    print(f"   频率分辨率: 0.01 Hz (目标值)")
    print(f"   参考声压: 20 μPa")


if __name__ == "__main__":
    main()
