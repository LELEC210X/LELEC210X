import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import librosa.core
from dataclasses import dataclass
from typing import List



################## Mel Triangle ##################
# FIRST PART

# TODO : Fix the last bug, the fact that the area is not 1 in some representations, its just a factor 2 that is mysteriously somewhere
# I don't know how to fix this bug permanently, so i just added a small correcting factor in different functions

def hz_to_mel(f):
    return 2595 * np.log10(1 + f / 700)

def mel_to_hz(mel):
    return 700 * (10**(mel / 2595) - 1)

@dataclass
class MelTriangle:
    center: float
    width: float
    height: float

    @classmethod
    def from_points(cls, left: float, center: float, right: float):
        """Create triangle from three frequency points"""
        return cls(
            center=center,
            width = (right - left),
            height = 2 / (right - left)  # Area of triangle is 1
        )

    def position(self, x: float) -> float:
        return max(0, self.height * (1 - abs((x - self.center) / self.width))/2)

    def verify_area(self):
        return self.width * self.height /2
    
# Test the triangle class
fig, ax = plt.subplots(1, 1, figsize=(6, 6))
triangles = [
    MelTriangle.from_points(-1, 0, 1),
    MelTriangle.from_points(-3, 0, 4),
    MelTriangle.from_points(-0.5, 0, 0.5),
]
x = np.linspace(-5, 5, 1000)
for t in triangles:
    y = [t.position(f) for f in x]
    ax.plot(x, y)
    ax.annotate(f"Area: {t.verify_area():.2f}", (t.center, t.height), textcoords="offset points", xytext=(0, 0), ha='center')
ax.set_title("Mel Triangles")
ax.set_xlabel("Frequency")
ax.set_ylabel("Amplitude")
plt.show(block=False)


def mel_filter_bank_from_scratch(f_s: int, n_fft: int, n_mels: int) -> List[MelTriangle]:
    """Generate overlapping triangular mel filterbank"""
    # Create frequency points in mel scale
    f_min = 0
    f_max = f_s / 2
    mel_min = hz_to_mel(f_min)
    mel_max = hz_to_mel(f_max)
    
    # Get uniform points in mel scale
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = mel_to_hz(mel_points)
    
    # Create triangles with proper overlap
    mel_trigs = []
    for i in range(1, len(hz_points)-1):
        width = hz_points[i+1] - hz_points[i-1]
        center = hz_points[i]
        mel_trigs.append(MelTriangle(center, width/2, 2/width))
    return mel_trigs

# Update plotting code
def plot_mel_filterbank(mel_trigs: List[MelTriangle], f_s: int, n_fft: int):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot centers
    centers = [t.center for t in mel_trigs]
    ax1.scatter(range(len(centers)), centers, label="Filter Centers")
    
    # Plot mel scale
    x = np.linspace(0, len(centers)-1, 1000)
    mel_points = np.linspace(0, hz_to_mel(f_s/2), 1000)
    hz_points = mel_to_hz(mel_points)
    ax1.plot(x, hz_points, 'g--', label="Mel Scale")
    ax1.set_title("Filter Center Frequencies")
    ax1.set_xlabel("Filter Index")
    ax1.set_ylabel("Frequency (Hz)")
    ax1.grid(True)
    ax1.legend()
    
    # Plot triangles
    x = np.linspace(0, f_s/2, n_fft//2 + 1)
    for i, t in enumerate(mel_trigs):
        y = [t.position(f) for f in x]
        ax2.plot(x, y, alpha=0.5)
    ax2.set_title("Mel Filterbank")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Amplitude")
    ax2.grid(True)
    
    plt.tight_layout()
    return fig

# Generate the mel filter bank from scratch
f_s = 22050
n_fft = 2048
n_mels = 40
mel_trigs = mel_filter_bank_from_scratch(f_s, n_fft, n_mels)

# Plot the centers, then the triangles
fig = plot_mel_filterbank(mel_trigs, f_s, n_fft)
fig.suptitle("Mel Filter Bank from Scratch")
plt.show(block=False)

# Plot the librosa mel filter bank using the same plotting function
mel_fb = librosa.filters.mel(sr=f_s, n_fft=n_fft, n_mels=n_mels)
mel_fb_center = np.argmax(mel_fb, axis=1) * f_s / n_fft
mel_fb_width_bins = np.sum(mel_fb > 0, axis=1)
mel_fb_half_width = (mel_fb_width_bins * f_s/n_fft) / 2
mel_fb_height = np.max(mel_fb, axis=1)
mel_trigs_librosa = [MelTriangle(c, w, h) for c, w, h in zip(mel_fb_center, mel_fb_half_width, mel_fb_height)]
fig = plot_mel_filterbank(mel_trigs_librosa, f_s, n_fft)
fig.suptitle("Librosa Mel Filter Bank")
plt.show(block=False)


################## Mel Transform ##################
## SECOND PART

def mel_transform(x: np.ndarray, mel_trigs: List[MelTriangle]) -> np.ndarray:
    """Apply mel transform to signal"""
    # The algorithm is to consider 3 buckets at a time (different triangles)
    # For each bucket, we compute the weighted sum of the signal using triangles not equal to 0
    
    mel_bins = np.zeros(len(mel_trigs))
    current_bins = np.arange(3)
    latest_bin = current_bins[-1] # The last bin is the one that was added

    # For each sample, compute the weight of the sample in the 3 triangles that we are considering
    for i, sample in enumerate(x):
        # For each triangle we are considering, compute the weight of the sample
        for current_mel_idx in current_bins:
            sample_weight = mel_trigs[current_mel_idx].position(sample)
            # Add the weight to the corresponding mel bin
            if sample_weight != 0:
                mel_bins[current_mel_idx] += sample_weight
            else:
                # If the weight is 0, we need to consider the next triangle
                current_mel_idx = latest_bin + 1
                latest_bin = current_mel_idx

    # Normalize the mel bins
    mel_bins /= np.sum(mel_bins)
    return mel_bins

def dumb_mel_transform(x: np.ndarray, mel_trigs: List[MelTriangle], f_s: int, n_fft: int) -> np.ndarray:
    """Apply mel transform to signal"""
    # Just consider all triangles at once, and compute the weighted sum of the signal

    mel_bins = np.zeros(len(mel_trigs))
    sampling_rate = f_s / n_fft

    for i, sample in enumerate(x):
        for j, t in enumerate(mel_trigs):
            mel_bins[j] += t.position(i*sampling_rate) * sample

    return mel_bins

# Create a sound signal (for fft)
y, sr = librosa.load(librosa.ex('trumpet'))
n_fft = 2048

# Generate the triangle filter bank
mel_trigs = mel_filter_bank_from_scratch(sr, n_fft, 40)

# Compute the mel spectrogram using librosa (for comparison)
librosa_mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft, n_mels=40)

# Compute our triangle-based mel spectrogram
triangle_mel = np.zeros(librosa_mel.shape)
fft_y = librosa.core.stft(y, n_fft=n_fft)
for i in range(librosa_mel.shape[1]):
    mel_spec = dumb_mel_transform(np.abs(fft_y[:, i]), mel_trigs, sr, n_fft)
    triangle_mel[:, i] = mel_spec

# Plot the mel spectrogram
fig, ax = plt.subplots(2, 2, figsize=(15, 6))
librosa.display.waveshow(y, sr=sr, ax=ax[0, 0])
D = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=n_fft)), ref=np.max)
librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log', ax=ax[0, 1])
librosa.display.specshow(librosa.power_to_db(librosa_mel, ref=np.max), sr=sr, x_axis='time', ax=ax[1, 0])
librosa.display.specshow(librosa.power_to_db(triangle_mel, ref=np.max), sr=sr, x_axis='time', ax=ax[1, 1])
ax[0, 0].set_title("Original Signal")
ax[0, 1].set_title("Original Signal FFT")
ax[1, 0].set_title("Mel (librosa)")
ax[1, 1].set_title("Mel (triangles)")
plt.tight_layout()
plt.show(block=True)
