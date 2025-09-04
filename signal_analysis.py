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
        
    def plot_time_domain(self, figure_num: int = 1) -> None:
        """
        绘制时域图
        
        Parameters
        ----------
        figure_num : int, optional
            图形编号，默认为1
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
        
    def plot_frequency_domain(self, figure_num: int = 2, freq_limit: float = 4000) -> None:
        """
        绘制频域图
        
        Parameters
        ----------
        figure_num : int, optional
            图形编号，默认为2
        freq_limit : float, optional
            频率显示上限，默认为4000Hz
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
        
    def plot_phase_domain(self, figure_num: int = 3, freq_limit: float = 4000) -> None:
        """
        绘制相位图
        
        Parameters
        ----------
        figure_num : int, optional
            图形编号，默认为3
        freq_limit : float, optional
            频率显示上限，默认为4000Hz
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
        
    def plot_spectrogram(self, figure_num: int = 4, freq_limit: float = 600, 
                        nfft: int = 40000) -> None:
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
        plt.pcolormesh(t, f, np.abs(Sxx), shading='auto')
        plt.ylim([0, freq_limit])
        plt.ylabel('Frequency (Hz)', fontfamily='Times New Roman', fontsize=7.5)
        plt.xlabel('Time (s)', fontfamily='Times New Roman', fontsize=7.5)
        plt.tick_params(labelsize=7.5)
        plt.colormap('jet')
        plt.tight_layout()
        
    def analyze_all(self, show_plots: bool = True) -> None:
        """
        执行完整的信号分析，绘制所有图形
        
        Parameters
        ----------
        show_plots : bool, optional
            是否显示图形，默认为True
        """
        if self.signal_data is None:
            raise ValueError("数据未加载，请先调用load_data方法")
            
        print("开始信号分析...")
        
        # 绘制时域图
        print("绘制时域图...")
        self.plot_time_domain()
        
        # 绘制频域图  
        print("绘制频域图...")
        self.plot_frequency_domain()
        
        # 绘制相位图
        print("绘制相位图...")
        self.plot_phase_domain()
        
        # 绘制时频图
        print("绘制时频图...")
        self.plot_spectrogram()
        
        if show_plots:
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
    
    # 检查是否存在.mat文件，否则使用示例数据
    mat_file_path = "/Users/nanpipro/Documents/gitlocal/soundwave-analysis-py/data样例.mat"
    
    if os.path.exists(mat_file_path):
        try:
            print("加载.mat文件数据...")
            analyzer.load_data_from_mat(mat_file_path)
        except Exception as e:
            print(f"加载.mat文件失败，使用示例数据: {e}")
            t_sample, signal_sample = create_sample_data()
            analyzer.load_data_from_arrays(t_sample, signal_sample)
    else:
        print("未找到.mat文件，使用示例数据...")
        t_sample, signal_sample = create_sample_data()
        analyzer.load_data_from_arrays(t_sample, signal_sample)
    
    # 执行完整分析
    analyzer.analyze_all()
