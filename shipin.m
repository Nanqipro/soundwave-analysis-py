%% 时域图
figure(1);    %画图1
Ts=1*10^-6;   %采样步长
Fs=1/Ts;      %采样频率
tt=0:Ts:1;    %采样时间段
y=interp1(Te(:,1),Te(:,2),tt,'linear');  %采样数据 
plot(tt,y)    %画出采样的数据时域图    
y=y-mean(y);  %去直流分量
xlim([0,1])   %限制x范围
xlabel('时间(s)')  %X轴标题
ylabel('电流(A)')  %Y轴标题
title('\fontsize{6}\fontname{宋体}时域')      %设置图的标题
set(gca,'fontsize',6,'FontName','Times New Roman')%设置坐标轴字号
set(get(gca,'xlabel'),'FontName','宋体','fontsize',6)%设置x轴labal字体
set(get(gca,'ylabel'),'FontName','宋体','fontsize',6) %| 设置y轴labal字体
set(gca,'unit','centimeters','Position',[4 4 5 2.5]);%设置图的大小
%% 频域图
figure(2);
N =length(y)-1; %求出时域数据点的数量并减1
fs=Fs;          % 采样频率>2倍的信号频率%1e5
Y=fft(y,N);     %求FFT
mag=2/N*abs(Y);   % FFT的振幅 abs(Y)取模
phase=unwrap(angle(Y));  % FFT的相位 消除相位混乱
fn=(0:(N/2))*fs/(1*N);   % 频率轴上的离散频率点，起始于0频(对应直流成分)，终于Nyquist频率fs/2，共N/2+1个频率点
plot(fn,(mag(1:N/2+1))) 
xlim([0,4000])   %限定频率显示范围
xlabel('频率(Hz)')
box on
ylabel('幅值')
title('\fontsize{6}\fontname{宋体}频域')
set(gca,'fontsize',6,'FontName','Times New Roman')%设置坐标轴字号
set(get(gca,'xlabel'),'FontName','宋体','fontsize',6)%设置x轴labal字体
set(get(gca,'ylabel'),'FontName','宋体','fontsize',6) %| 设置y轴labal字体
set(gca,'unit','centimeters','Position',[4 4 6 4]);%设置图的大小
%% 相位图
figure(3);
pha=angle(Y)*180/pi;   %求相位
plot(fn,pha(1:N/2+1)); %plot画图
xlim([0,4000])   %限定频率显示范围
xlabel('频率(Hz)')
box on           %画出边框线
ylabel('角度/°')
title('\fontsize{6}\fontname{宋体}相频')
set(gca,'fontsize',6,'FontName','Times New Roman')%设置坐标轴字号
set(get(gca,'xlabel'),'FontName','宋体','fontsize',6)%设置x轴labal字体
set(get(gca,'ylabel'),'FontName','宋体','fontsize',6) %| 设置y轴labal字体
set(gca,'unit','centimeters','Position',[4 4 10 4]);%设置图的大小
%% 时频图
figure(4);
nfft=40000;%进行傅里叶变换的数据长度，越大频率分辨率越高，但离瞬时频率就越远；
asd=hamming(nfft);
[B,f,t]=spectrogram(y,hamming(nfft),nfft*0.95,nfft,fs); %spectrogram函数,y为信号，hamming(nfft)为窗函数大小，nfft*0.95为重叠的采样点数，nfft为傅里叶变换的点数，fs为采样频率
% f=f(f>0&f<1000);  %选定频率范围
% B=B(f>0&f<1000,:);  %选定幅值范围
pcolor(t,f,abs(B))   %彩图
ylim([0,600])       %限定Y轴显示范围
shading interp     %平滑处理
colormap jet       %选择色系
ylabel('Frequency (Hz)')
xlabel('Time (s)')
set(gca,'fontsize',7.5,'FontName','Times New Roman')%设置坐标轴字号
set(get(gca,'xlabel'),'FontName','Times New Roman','fontsize',7.5)%设置x轴labal字体
set(get(gca,'ylabel'),'FontName','Times New Roman','fontsize',7.5) %| 设置y轴labal字体
set(gca,'unit','centimeters','Position',[4 4 5 3]);%设置图的大小