import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import time

# ------------------------------
# 1. Approximate Mel Conversion Functions
# ------------------------------

def true_mel(f):
    """True mel conversion for reference."""
    return 2595 * np.log10(1 + f / 700)

def approximate_mel(f):
    """
    Approximate frequency-to-mel conversion via piecewise linear segments.
    
    Breakpoint at 700 Hz:
      For f < 700:
          m = (m_break / 700)*f,
      For f >= 700:
          m = m_break + slope_high*(f - 700),
    where m_break = true_mel(700) (~781) and m_max = true_mel(8000) (~2840).
    """
    f_break = 700.0
    f_max   = 8000.0
    m_break = true_mel(f_break)
    m_max   = true_mel(f_max)
    
    slope_low  = m_break / f_break
    slope_high = (m_max - m_break) / (f_max - f_break)
    
    f = np.asarray(f, dtype=np.float64)
    m = np.empty_like(f)
    
    mask = f < f_break
    m[mask] = slope_low * f[mask]
    m[~mask] = m_break + slope_high * (f[~mask] - f_break)
    
    return m

def approximate_mel_inverse(m):
    """
    Inverse of approximate_mel.
    
    For m < m_break, f = m / slope_low.
    For m >= m_break, f = (m - m_break) / slope_high + 700.
    """
    f_break = 700.0
    f_max   = 8000.0
    m_break = true_mel(f_break)
    m_max   = true_mel(f_max)
    
    slope_low  = m_break / f_break
    slope_high = (m_max - m_break) / (f_max - f_break)
    
    m = np.asarray(m, dtype=np.float64)
    f = np.empty_like(m)
    
    mask = m < m_break
    f[mask] = m[mask] / slope_low
    f[~mask] = (m[~mask] - m_break) / slope_high + f_break
    return f

# ------------------------------
# 2. Filter Bank Construction
# ------------------------------

def compute_approx_mel_filters(num_filters, fmin, fmax, fs, nfft):
    """
    Compute a mel filter bank using the approximate mel conversion.
    
    Steps:
      a. Compute m_min and m_max (using approximate_mel).
      b. Equally space (num_filters+2) points in the mel domain.
      c. Convert these points back to Hz using approximate_mel_inverse.
      d. Convert Hz to FFT bin indices.
      e. For each filter (i=1..num_filters), define a triangular filter
         with left=bin[i-1], center=bin[i], and right=bin[i+1].
    
    Returns:
      filters: 2D array of shape (num_filters, nfft//2 + 1)
      freq_centers: center frequencies (Hz) for each filter.
    """
    # a. Compute mel endpoints using the approximate conversion.
    m_min = approximate_mel(fmin)
    m_max = approximate_mel(fmax)
    
    # b. Equally spaced points in mel domain.
    mel_points = np.linspace(m_min, m_max, num_filters + 2)
    # c. Convert back to Hz.
    freq_points = approximate_mel_inverse(mel_points)
    
    # d. Convert Hz to FFT bin indices.
    bin_indices = np.floor((freq_points / fs) * nfft).astype(int)
    
    filters = np.zeros((num_filters, nfft//2 + 1))
    freq_centers = []
    
    for i in range(1, num_filters+1):
        left = bin_indices[i-1]
        center = bin_indices[i]
        right = bin_indices[i+1]
        freq_centers.append(freq_points[i])
        
        if center == left or right == center:
            continue
        
        # Rising slope:
        filters[i-1, left:center] = (np.arange(left, center) - left) / (center - left)
        # Falling slope:
        filters[i-1, center:right] = (right - np.arange(center, right)) / (right - center)
        # Normalize filter to unit area.
        filt_sum = np.sum(filters[i-1])
        if filt_sum > 0:
            filters[i-1] /= filt_sum
            
    return filters, np.array(freq_centers)

# ------------------------------
# 3. Generate Synthetic Signal and Spectrogram
# ------------------------------

def generate_synthetic_signal(duration_sec=2.0, fs=16000):
    """Generate a test signal: two sine waves and a frequency sweep."""
    t = np.linspace(0, duration_sec, int(fs * duration_sec), endpoint=False)
    sig = 0.5 * np.sin(2 * np.pi * 300 * t) + 0.3 * np.sin(2 * np.pi * 1000 * t)
    sweep = np.sin(2 * np.pi * (200 + (3000-200) * t / duration_sec) * t)
    sig += 0.2 * sweep
    return sig, t

def compute_spectrogram(signal, nfft=512, hop_length=256):
    """Compute magnitude spectrogram using an STFT."""
    stft = librosa.stft(signal, n_fft=nfft, hop_length=hop_length, window='hann')
    return np.abs(stft)

# ------------------------------
# 4. Main Comparison Code and Side-by-Side Graphs
# ------------------------------

if __name__ == '__main__':
    # Parameters
    num_filters = 40
    fmin = 0
    fmax = 8000
    fs = 16000
    nfft = 512
    hop_length = 256

    # ---------------------------
    # Compute Filter Banks
    # ---------------------------
    # Approximate filter bank using our implementation:
    filters_approx, mel_freqs_approx = compute_approx_mel_filters(num_filters, fmin, fmax, fs, nfft)
    
    # Librosa filter bank (note: librosa uses a slightly different mel scale)
    filters_librosa = librosa.filters.mel(sr=fs, n_fft=nfft, n_mels=num_filters, fmin=fmin, fmax=fmax)
    mel_freqs_librosa = librosa.mel_frequencies(n_mels=num_filters, fmin=fmin, fmax=fmax)
    
    # ---------------------------
    # Generate Signal and Spectrogram
    # ---------------------------
    signal, t = generate_synthetic_signal(duration_sec=2.0, fs=fs)
    spec = compute_spectrogram(signal, nfft=nfft, hop_length=hop_length)
    
    # Compute mel spectrograms:
    mel_spec_approx = np.dot(filters_approx, spec)
    mel_spec_librosa = np.dot(filters_librosa, spec)
    
    # ---------------------------
    # Prepare Mel Conversion Comparison Data
    # ---------------------------
    freqs = np.linspace(0, fmax, 8001)
    mel_true_vals = true_mel(freqs)
    mel_approx_vals = approximate_mel(freqs)
    # Librosa's mel_frequencies function provides the center frequencies for each filter;
    # for a continuous curve, we use the true_mel conversion as Librosa’s formula is slightly different.
    
    # ---------------------------
    # Plot Side-by-Side Comparison Graphs
    # ---------------------------
    fig, axs = plt.subplots(3, 2, figsize=(14, 12))
    plt.subplots_adjust(hspace=0.4, wspace=0.3)
    
    # Row 1: Filter Bank Triangles (Plot a subset: every 5th filter)
    fft_bins = np.arange(nfft//2 + 1)
    for i in range(0, num_filters, 5):
        axs[0, 0].plot(fft_bins, filters_librosa[i], label=f'Filter {i}')
        axs[0, 1].plot(fft_bins, filters_approx[i], label=f'Filter {i}')
    axs[0, 0].set_title('Librosa Filter Bank (Subset)')
    axs[0, 1].set_title('Approximate Filter Bank (Subset)')
    for ax in axs[0]:
        ax.set_xlabel('FFT Bin')
        ax.set_ylabel('Normalized Amplitude')
        ax.legend(fontsize=8)
        ax.grid(True)
    
    # Row 2: Mel Spectrograms
    # Librosa mel spectrogram
    img1 = librosa.display.specshow(librosa.amplitude_to_db(mel_spec_librosa, ref=np.max),
                                     sr=fs, hop_length=hop_length, x_axis='time', y_axis='mel',
                                     ax=axs[1, 0])
    axs[1, 0].set_title('Librosa Mel Spectrogram')
    fig.colorbar(img1, ax=axs[1, 0], format='%+2.0f dB')
    
    # Approximate mel spectrogram
    img2 = librosa.display.specshow(librosa.amplitude_to_db(mel_spec_approx, ref=np.max),
                                     sr=fs, hop_length=hop_length, x_axis='time', y_axis='mel',
                                     ax=axs[1, 1])
    axs[1, 1].set_title('Approximate Mel Spectrogram')
    fig.colorbar(img2, ax=axs[1, 1], format='%+2.0f dB')
    
    # Row 3: Mel Conversion Comparison
    # Left: True vs. Librosa (using librosa.mel_frequencies on a dense grid)
    # (Librosa does not provide a continuous function; here we approximate by comparing the center frequencies.)
    axs[2, 0].plot(mel_freqs_librosa, label='Librosa Mel Centers', marker='o', linestyle='--')
    axs[2, 0].plot(approximate_mel(mel_freqs_librosa), label='Approx True Mel at Librosa Centers', marker='x')
    axs[2, 0].set_title('Librosa: Center Frequencies vs. True Mel')
    axs[2, 0].set_xlabel('Filter Index')
    axs[2, 0].set_ylabel('Mel Value')
    axs[2, 0].legend(fontsize=8)
    axs[2, 0].grid(True)
    
    # Right: True Mel vs. Approximate Mel (continuous curves)
    axs[2, 1].plot(freqs, mel_true_vals, label='True Mel', linewidth=2)
    axs[2, 1].plot(freqs, mel_approx_vals, '--', label='Approximate Mel', linewidth=2)
    axs[2, 1].set_title('Mel Conversion: True vs. Approximate')
    axs[2, 1].set_xlabel('Frequency (Hz)')
    axs[2, 1].set_ylabel('Mel Value')
    axs[2, 1].legend(fontsize=8)
    axs[2, 1].grid(True)
    
    plt.suptitle("Side-by-Side Comparison: Librosa vs. Approximate Implementation", fontsize=16)
    plt.show()
