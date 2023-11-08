import numpy as np
from scipy.fft import fft, fftfreq, fftshift
from matplotlib import pyplot as plt

def plot_time(sig_list, label_list, fs):
    plt.figure()
    for sig,label in zip(sig_list, label_list):
        plt.plot(np.arange(0,sig.shape[-1])/fs,sig,'.-',label=label)
        
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.draw()

def plot_freq(sig_list, label_list, fs, os=1, f_lim=None ):
    f,ax = plt.subplots(2,1,sharex=True)
    for sig,label in zip(sig_list, label_list):
        freq = fftshift(fftfreq(sig.shape[-1]*os))*fs/1000
        H = fftshift(fft(sig,n=sig.shape[-1]*os))
        ax[0].plot(freq,20*np.log10(np.abs(H)),label=label)
        ax[1].plot(freq,np.rad2deg(np.angle(H)),label=label)

    ax[0].set_ylim([-100, 10])
    ax[0].set_ylabel("Modulus (dB)")
    ax[0].set_ylim(-120, 20)
    if f_lim is not None:
        ax[0].set_xlim(-f_lim/1000, f_lim/1000)
        ax[1].set_xlim(-f_lim/1000, f_lim/1000)
    ax[1].set_ylabel("Phase (deg)")
    ax[1].set_xlabel("Frequency [kHz]")
    plt.legend()
    plt.draw()
