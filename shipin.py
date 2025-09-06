"""
声波信号分析工具
==============

该模块提供信号的时域、频域、相位和时频分析功能
包含时域图、频域图、相位图和时频图的绘制

主要功能：
- 时域信号分析与可视化
- 频域FFT分析与可视化
- 相位频率分析
- 时频谱图分析
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import loadmat
from typing import Tuple, Optional, Union
import os


class SignalAnalyzer:
    """
    信号分析器类
    
    用于对声波信号进行时域、频域、相位和时频分析
    支持多种输入格式：MATLAB .mat文件、numpy数组、WAV音频文件
    
    Attributes
    ----------
    sampling_step : float
        采样步长 (秒)
    sampling_freq : float
        采样频率 (Hz)
    time_data : np.ndarray
        时间轴数据
    signal_data : np.ndarray
        信号数据
    """
    
    def __init__(self, sampling_step: float = 1e-6):
        """
        初始化信号分析器
        
        Parameters
        ----------
        sampling_step : float, optional
            采样步长，默认为1微秒
        """
        self.sampling_step = sampling_step
        self.sampling_freq = 1 / sampling_step
        self.time_data: Optional[np.ndarray] = None
        self.signal_data: Optional[np.ndarray] = None
        
    def load_data_from_mat(self, mat_file_path: str, te_var_name: str = 'Te') -> None:
        """
        从MATLAB .mat文件加载数据
        
        Parameters
        ----------
        mat_file_path : str
            .mat文件路径
        te_var_name : str, optional
            MATLAB变量名，默认为'Te'
        """
        try:
            mat_data = loadmat(mat_file_path)
            te_data = mat_data[te_var_name]
            self._process_te_data(te_data)
        except Exception as e:
            print(f"加载数据失败: {e}")
            raise
            
    def load_data_from_arrays(self, time_array: np.ndarray, signal_array: np.ndarray) -> None:
        """
        直接从数组加载数据
        
        Parameters
        ----------
        time_array : np.ndarray
            时间数组
        signal_array : np.ndarray
            信号数组
        """
        te_data = np.column_stack((time_array, signal_array))
        self._process_te_data(te_data)
        
    def load_data_from_wav(self, wav_file_path: str, max_duration: float = 1.0) -> None:
        """
        从WAV音频文件加载数据
        
        Parameters
        ----------
        wav_file_path : str
            WAV音频文件路径
        max_duration : float, optional
            最大加载时长（秒），默认1秒
        """
        try:
            # 优先使用librosa
            try:
                import librosa
                signal, sr = librosa.load(wav_file_path, sr=None, mono=True)
            except ImportError:
                # 备用方案：使用scipy
                from scipy.io import wavfile
                sr, signal = wavfile.read(wav_file_path)
                # 归一化
                if signal.dtype == np.int16:
                    signal = signal.astype(np.float32) / 32768.0
                elif signal.dtype == np.int32:
                    signal = signal.astype(np.float32) / 2147483648.0
                # 转单声道
                if len(signal.shape) > 1:
                    signal = np.mean(signal, axis=1)
            
            # 限制时长
            max_samples = int(max_duration * sr)
            if len(signal) > max_samples:
                signal = signal[:max_samples]
            
            # 生成时间轴
            time_array = np.arange(len(signal)) / sr
            
            # 加载数据
            self.load_data_from_arrays(time_array, signal)
            print(f"✓ WAV文件加载成功: {os.path.basename(wav_file_path)}")
            print(f"  原始采样率: {sr:,} Hz")
            print(f"  时长: {len(signal)/sr:.3f} 秒")
            print(f"  数据点数: {len(signal):,}")
            
        except Exception as e:
            print(f"❌ WAV文件加载失败: {e}")
            print("💡 建议安装: pip install librosa")
            raise
        
    def _process_te_data(self, te_data: np.ndarray) -> None:
        """
        处理Te数据，进行插值和预处理
        
        Parameters
        ----------
        te_data : np.ndarray
            原始时间-信号数据，形状为 (N, 2)
        """
        # 生成采样时间段 (0到1秒)
        tt = np.arange(0, 1 + self.sampling_step, self.sampling_step)
        
        # 线性插值采样数据
        self.signal_data = np.interp(tt, te_data[:, 0], te_data[:, 1])
        self.time_data = tt
        
        # 去直流分量
        self.signal_data = self.signal_data - np.mean(self.signal_data)
        
    def plot_time_domain(self, figure_num: int = 1, save_path: str = None) -> None:
        """
        绘制时域图
        
        Parameters
        ----------
        figure_num : int, optional
            图形编号，默认为1
        save_path : str, optional
            保存路径，如果提供则保存图片而不显示
        """
        if self.time_data is None or self.signal_data is None:
            raise ValueError("数据未加载，请先调用load_data方法")
            
        plt.figure(figure_num, figsize=(5, 2.5))
        plt.plot(self.time_data, self.signal_data)
        plt.xlim([0, 1])
        plt.xlabel('Time (s)', fontfamily='Times New Roman', fontsize=6)
        plt.ylabel('Current (A)', fontfamily='Times New Roman', fontsize=6)
        plt.title('Time Domain', fontsize=6, fontfamily='Times New Roman')
        plt.tick_params(labelsize=6)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(figure_num)
        
    def plot_frequency_domain(self, figure_num: int = 2, freq_limit: float = 4000, save_path: str = None) -> None:
        """
        绘制频域图
        
        Parameters
        ----------
        figure_num : int, optional
            图形编号，默认为2
        freq_limit : float, optional
            频率显示上限，默认为4000Hz
        save_path : str, optional
            保存路径，如果提供则保存图片而不显示
        """
        if self.signal_data is None:
            raise ValueError("数据未加载，请先调用load_data方法")
            
        N = len(self.signal_data) - 1
        
        # 计算FFT
        Y = np.fft.fft(self.signal_data, N)
        mag = 2 / N * np.abs(Y)
        
        # 频率轴
        fn = np.arange(0, N//2 + 1) * self.sampling_freq / N
        
        plt.figure(figure_num, figsize=(6, 4))
        plt.plot(fn, mag[:N//2 + 1])
        plt.xlim([0, freq_limit])
        plt.xlabel('Frequency (Hz)', fontfamily='Times New Roman', fontsize=6)
        plt.ylabel('Magnitude', fontfamily='Times New Roman', fontsize=6)
        plt.title('Frequency Domain', fontsize=6, fontfamily='Times New Roman')
        plt.tick_params(labelsize=6)
        plt.box(True)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(figure_num)
        
    def plot_phase_domain(self, figure_num: int = 3, freq_limit: float = 4000, save_path: str = None) -> None:
        """
        绘制相位图
        
        Parameters
        ----------
        figure_num : int, optional
            图形编号，默认为3
        freq_limit : float, optional
            频率显示上限，默认为4000Hz
        save_path : str, optional
            保存路径，如果提供则保存图片而不显示
        """
        if self.signal_data is None:
            raise ValueError("数据未加载，请先调用load_data方法")
            
        N = len(self.signal_data) - 1
        
        # 计算FFT和相位
        Y = np.fft.fft(self.signal_data, N)
        phase = np.angle(Y) * 180 / np.pi
        
        # 频率轴
        fn = np.arange(0, N//2 + 1) * self.sampling_freq / N
        
        plt.figure(figure_num, figsize=(10, 4))
        plt.plot(fn, phase[:N//2 + 1])
        plt.xlim([0, freq_limit])
        plt.xlabel('Frequency (Hz)', fontfamily='Times New Roman', fontsize=6)
        plt.ylabel('Phase (°)', fontfamily='Times New Roman', fontsize=6)
        plt.title('Phase Domain', fontsize=6, fontfamily='Times New Roman')
        plt.tick_params(labelsize=6)
        plt.box(True)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(figure_num)
        
    def plot_spectrogram(self, figure_num: int = 4, freq_limit: float = 600, 
                        nfft: int = 40000, save_path: str = None) -> None:
        """
        绘制时频图(谱图)
        
        Parameters
        ----------
        figure_num : int, optional
            图形编号，默认为4
        freq_limit : float, optional
            频率显示上限，默认为600Hz
        nfft : int, optional
            FFT长度，默认为40000
        save_path : str, optional
            保存路径，如果提供则保存图片而不显示
        """
        if self.signal_data is None or self.time_data is None:
            raise ValueError("数据未加载，请先调用load_data方法")
            
        # 计算时频谱
        window = signal.windows.hamming(nfft)
        overlap = int(nfft * 0.95)
        
        f, t, Sxx = signal.spectrogram(
            self.signal_data, 
            fs=self.sampling_freq,
            window=window,
            noverlap=overlap,
            nfft=nfft
        )
        
        plt.figure(figure_num, figsize=(5, 3))
        plt.pcolormesh(t, f, np.abs(Sxx), shading='auto', cmap='jet')
        plt.ylim([0, freq_limit])
        plt.ylabel('Frequency (Hz)', fontfamily='Times New Roman', fontsize=7.5)
        plt.xlabel('Time (s)', fontfamily='Times New Roman', fontsize=7.5)
        plt.tick_params(labelsize=7.5)
        plt.colorbar(label='Magnitude')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(figure_num)
        
    def analyze_all(self, show_plots: bool = True, save_dir: str = None, file_prefix: str = "signal") -> None:
        """
        执行完整的信号分析，绘制所有图形
        
        Parameters
        ----------
        show_plots : bool, optional
            是否显示图形，默认为True
        save_dir : str, optional
            保存目录，如果提供则保存图片到该目录
        file_prefix : str, optional
            保存文件的前缀，默认为"signal"
        """
        if self.signal_data is None:
            raise ValueError("数据未加载，请先调用load_data方法")
            
        print("开始信号分析...")
        
        # 确保保存目录存在
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        # 绘制时域图
        print("绘制时域图...")
        time_save_path = None
        if save_dir:
            time_save_path = os.path.join(save_dir, f"{file_prefix}_time_domain.png")
        self.plot_time_domain(save_path=time_save_path)
        
        # 绘制频域图  
        print("绘制频域图...")
        freq_save_path = None
        if save_dir:
            freq_save_path = os.path.join(save_dir, f"{file_prefix}_frequency_domain.png")
        self.plot_frequency_domain(save_path=freq_save_path)
        
        # 绘制相位图
        print("绘制相位图...")
        phase_save_path = None
        if save_dir:
            phase_save_path = os.path.join(save_dir, f"{file_prefix}_phase_domain.png")
        self.plot_phase_domain(save_path=phase_save_path)
        
        # 绘制时频图
        print("绘制时频图...")
        spec_save_path = None
        if save_dir:
            spec_save_path = os.path.join(save_dir, f"{file_prefix}_spectrogram.png")
        self.plot_spectrogram(save_path=spec_save_path)
        
        if show_plots and not save_dir:
            plt.show()
            
        print("信号分析完成!")


def create_sample_data() -> Tuple[np.ndarray, np.ndarray]:
    """
    创建示例数据用于测试
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        时间数组和信号数组
    """
    # 创建示例信号：多个频率分量的组合
    t = np.linspace(0, 1, 1000)
    signal_data = (np.sin(2 * np.pi * 50 * t) + 
                  0.5 * np.sin(2 * np.pi * 120 * t) + 
                  0.3 * np.sin(2 * np.pi * 300 * t) +
                  0.1 * np.random.randn(len(t)))
    return t, signal_data


if __name__ == "__main__":
    """
    主程序入口：演示信号分析功能
    """
    # 创建信号分析器实例
    analyzer = SignalAnalyzer()
    
    # 数据加载优先级：WAV文件 > .mat文件 > 示例数据
    data_loaded = False
    
    # 1. 尝试加载WAV文件
    wav_file_path = None
    if os.path.exists("data"):
        # 查找第一个可用的WAV文件
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith('.wav'):
                    wav_file_path = os.path.join(root, file)
                    break
            if wav_file_path:
                break
    
    if wav_file_path:
        try:
            print(f"发现WAV文件，加载: {wav_file_path}")
            analyzer.load_data_from_wav(wav_file_path)
            data_loaded = True
        except Exception as e:
            print(f"加载WAV文件失败: {e}")
    
    # 2. 尝试加载.mat文件
    if not data_loaded:
        mat_file_path = "/Users/nanpipro/Documents/gitlocal/soundwave-analysis-py/data样例.mat"
        if os.path.exists(mat_file_path):
            try:
                print("加载.mat文件数据...")
                analyzer.load_data_from_mat(mat_file_path)
                data_loaded = True
            except Exception as e:
                print(f"加载.mat文件失败: {e}")
    
    # 3. 使用示例数据
    if not data_loaded:
        print("使用示例数据...")
        t_sample, signal_sample = create_sample_data()
        analyzer.load_data_from_arrays(t_sample, signal_sample)
    
    # 执行完整分析
    analyzer.analyze_all()
