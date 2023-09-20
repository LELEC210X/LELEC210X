%% Audio signal

rng(1); % Random seed
n = 5;

t = linspace(0,20,1000);
A = rand(1,n)*10;
w = rand(1,n)*5;
phi= rand(1,n)*2*pi;

sig = sum(A.*sin(kron(w,t')+phi), 2);

fig = figure(); hold on;
% plot(t, sig, 'k', 'LineWidth', 15.0);
subsample = 15;
stem(t(1:subsample:end), sig(1:subsample:end), 'k', 'LineWidth', 4.0);
set(gca,'xtick',[])
set(gca,'ytick',[])
set(gca, 'Position', [0,0,1,1]);

%% Low-pass filter

B=0.5;      %Beta value
Ts = 0.25;  %Sampling interval
N=200;     %Number of samples
t=-N*Ts:Ts:(N-1)*Ts;
%Formula
pt_RRC = ((sin(pi*t.*(1-B)) + 4*B*t.*cos(pi*t*(1+B))) ./ (pi*t.*(1-(4*B*t).^2)));
loc = isnan(pt_RRC);
pt_RRC(loc)=(pt_RRC(circshift(loc,1))+pt_RRC(circshift(loc,length(pt_RRC)-1)))/2 ;
% figure(); plot(pt_RRC); hold on;

fig=figure(); hold on;
plot(abs(fftshift(fft(pt_RRC))), 'k', 'LineWidth', 5.0);
set(gca,'xtick',[])
set(gca,'ytick',[])
set(gca, 'Position', [0,0,1,1]);
