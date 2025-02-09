import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import librosa.core
import time

TEST = 2
if TEST == 1:
    ############################################
    # Triangle function

    def triangle_branchless(x: float, center: float, width: float, height: float) -> float:
        return max(0, height - abs(x - center) / width)

    # Draw triangle function
    x = np.linspace(0, 10, 1000)
    y = np.array([triangle_branchless(i, 5, 2, 1) for i in x])
    plt.plot(x, y)
    plt.title("Triangle function")
    plt.show(block=False)

    ############################################
    ## Librosa Mel Filter Bank

    sr = 22050
    n_fft = 2048
    n_mels = 40

    # Create Mel filter bank using librosa
    mel_fb = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=n_mels)

    ############################################
    ## Compare side by side the librosa matrix represented as a plot, compared to the triangle representation

    # First figure
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    for i in range(n_mels):
        ax[0].plot(mel_fb[i], label=f"Filter {i}")
    ax[0].set_title("Mel Filter Bank (Librosa Representation)")
    ax[0].set_xlabel("Frequency Bin")
    ax[0].set_ylabel("Amplitude")
    ax[0].grid(True)

    # Second figure
    freq_res = sr / n_fft
    mel_fb_center = np.argmax(mel_fb, axis=1) * freq_res
    mel_fb_width_bins = np.sum(mel_fb > 0, axis=1)
    mel_fb_half_width = (mel_fb_width_bins * sr / n_mels) /2 # TODO: FIX THIS
    mel_fb_height = np.max(mel_fb, axis=1)

    x_end = sr / 2
    x = np.linspace(0, x_end, n_fft//2 + 1)
    for i in range(n_mels):
        y = np.array([triangle_branchless(j, mel_fb_center[i], mel_fb_half_width[i], mel_fb_height[i]) for j in x])
        ax[1].plot(x, y, label=f"Filter {i}")
    ax[1].set_title("Mel Filter Bank (Triangle Representation)")
    ax[1].set_xlabel("Frequency Bin")
    ax[1].set_ylabel("Amplitude")
    ax[1].grid(True)

    plt.tight_layout()
    plt.show(block=False)


    ############################################
    ## Compare side by side the librosa matrix and the triangle representation matrix

    # Regenerate the mel filter bank matrix
    def mel_filter_bank(n_fft: int, sr: int, n_mels: int, centers: np.ndarray, half_widths: np.ndarray, heights: np.ndarray) -> np.ndarray:
        """
        Reconstruct a mel filter bank from its triangle parameters.
        """
        # Create a frequency axis in Hz
        x_end = sr / 2
        x = np.linspace(0, x_end, n_fft//2 + 1)
        
        mel_fb_reconstructed = np.zeros((n_mels, len(x)))
        for i in range(n_mels):
            mel_fb_reconstructed[i] = np.array(
                [triangle_branchless(j, centers[i], half_widths[i], heights[i]) for j in x]
            )
        return mel_fb_reconstructed

    # First figure
    fig, ax = plt.subplots(1,2, figsize=(10, 6))
    librosa.display.specshow(mel_fb, x_axis='linear', y_axis='mel', sr=sr, ax=ax[0])
    ax[0].set_title("Mel Filter Bank (librosa)")
    ax[0].set_xlabel("Frequency Bin")
    ax[0].set_ylabel("Mel Filter")
    ax[0].grid(False)

    # Second figure
    mel_fb_regen = mel_filter_bank(n_fft, sr, n_mels, mel_fb_center, mel_fb_half_width, mel_fb_height)
    librosa.display.specshow(mel_fb_regen, x_axis='linear', y_axis='mel', sr=sr, ax=ax[1])
    ax[1].set_title("Mel Filter Bank (Triangle Representation)")
    ax[1].set_xlabel("Frequency Bin")
    ax[1].set_ylabel("Mel Filter")
    ax[1].grid(False)

    plt.show(block=False)

    ############################################
    ## Librosa per triangle analysis

    # Matplotlib window with buttons to switch between matrix lines (where values are not zero)
    # Has statistics on the area of the triangle, the center, the width, the height, and the sum of the triangle
    # The grid is fine, and there is a fine graduation

    # Import matplotlib buttons
    from matplotlib.widgets import Button

    # Create a figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    main_plot = ax.plot(mel_fb[0], label="Filter 0")[0]
    ax.set_title("Mel Filter Bank (Librosa Representation)")
    ax.set_xlabel("Frequency Bin")
    ax.set_ylabel("Amplitude")
    ax.grid(True)
    ax.legend()

    # Create a button to switch between filters
    ax_button = plt.axes([0.7, 0.01, 0.1, 0.05])
    button = Button(ax_button, 'Next Filter', color='lightblue', hovercolor='0.975')

    # Create a text box to display statistics
    ax_text = plt.axes([0.1, 0.01, 0.5, 0.05])
    text = ax_text.text(0.5, 0.5, "", ha='center', va='center')

    # Create a function to update the plot
    def update_plot(filter_idx):
        # Grab only the values where the triangle is not zero
        data = mel_fb[filter_idx]
        data = data[data > 0]
        main_plot.set_data(np.arange(data.shape[0]), data)
        ax.set_title(f"Mel Filter Bank (Librosa Representation) - Filter {filter_idx}")
        ax.legend()
        ax.set_xlim(0, data.shape[0])
        plt.draw()

    # Create a function to update the text box
    def update_text(filter_idx):
        center = mel_fb_center[filter_idx]
        half_width = mel_fb_half_width[filter_idx]
        height = mel_fb_height[filter_idx]
        area = np.sum(mel_fb[filter_idx]) * freq_res
        text.set_text(f"Center: {center:.2f} Hz, Width: {half_width*2:.2f} Hz, Height: {height:.2f}, Area: {area:.2f}")
        plt.draw()

    # Create a function to update the plot and the text box
    def update_all(filter_idx):
        # Only keep values where the triangle is not zero
        update_plot(filter_idx)
        update_text(filter_idx)

    # Create a function to switch to the next filter
    def next_filter(event):
        global filter_idx
        filter_idx = (filter_idx + 1) % n_mels
        update_all(filter_idx)

    # Connect the button to the function
    button.on_clicked(next_filter)

    # Initialize the filter index
    filter_idx = 0
    update_all(filter_idx)

    plt.show(block=False)

    ############################################
    ## Find the series of the frequencies used by librosa as the center of the triangle

    # Convert Hz to mel scale
    def hz_to_mel(f):
        return 2595 * np.log10(1 + f / 700)

    # Convert mel to Hz scale  
    def mel_to_hz(mel):
        return 700 * (10**(mel / 2595) - 1)

    # Create proper x axes and data
    n_points = 1000
    max_freq = sr / 2

    # Generate frequency points
    freq_axis = np.linspace(0, max_freq, n_points)
    mel_axis = hz_to_mel(freq_axis)

    # Get mel filter centers in Hz
    centers_hz = mel_fb_center

    # Fit polynomial to centers
    x_for_fit = np.linspace(0, n_mels-1, n_mels)
    center_fit = np.polyfit(x_for_fit, centers_hz, 3)
    center_fit_fn = np.poly1d(center_fit)
    fit_points = center_fit_fn(x_for_fit)

    # Plot everything on Hz scale
    plt.figure(figsize=(12, 6))

    # Plot actual filter centers
    plt.scatter(range(n_mels), centers_hz, 
            label="Actual Filter Centers", 
            color='blue', alpha=0.6)

    # Plot polynomial fit
    plt.plot(x_for_fit, fit_points, 
            label="Polynomial Fit", 
            color='red', linestyle='--')

    # Plot true mel scale
    mel_points = np.linspace(0, hz_to_mel(max_freq), n_points)
    hz_points = mel_to_hz(mel_points)
    plt.plot(np.linspace(0, n_mels-1, n_points), hz_points, 
            label="True Mel Scale", 
            color='green')

    plt.title("Mel Filter Bank Center Frequencies")
    plt.xlabel("Mel Filter Index")
    plt.ylabel("Frequency (Hz)")
    plt.legend()
    plt.grid(True)
    plt.show(block=False)

############################################
## Generate the positions (centers) of the triangles using the proper mel scale
# Lets do it from scratch, and compare the results

def hz_to_mel(f):
    return 2595 * np.log10(1 + f / 700)

def mel_to_hz(mel):
    return 700 * (10**(mel / 2595) - 1)

from dataclasses import dataclass
from typing import List

@dataclass
class MelTriangle:
    center: float
    width: float
    height: float

    @classmethod
    def from_points(cls, left: float, center: float, right: float):
        """Create triangle from three frequency points"""
        width = (right - left) / 2  # Half the total width
        height = 2.0 / width  # Height for unit area
        return cls(center, width, height)

    def position(self, x: float) -> float:
        return max(0, self.height - abs(x - self.center) / self.width)

    def verify_area(self):
        return self.width * self.height

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
        mel_trigs.append(MelTriangle.from_points(
            hz_points[i-1],  # Left point
            hz_points[i],    # Center point
            hz_points[i+1]   # Right point
        ))
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
plt.show(block=False)

# Plot the librosa mel filter bank using the same plotting function
mel_fb = librosa.filters.mel(sr=f_s, n_fft=n_fft, n_mels=n_mels)
mel_fb_center = np.argmax(mel_fb, axis=1) * f_s / n_fft
mel_fb_width_bins = np.sum(mel_fb > 0, axis=1)
mel_fb_half_width = (mel_fb_width_bins * f_s / n_mels) / 2
mel_fb_height = np.max(mel_fb, axis=1)
mel_trigs_librosa = [MelTriangle(c, w, h) for c, w, h in zip(mel_fb_center, mel_fb_half_width, mel_fb_height)]
fig = plot_mel_filterbank(mel_trigs_librosa, f_s, n_fft)
plt.show(block=True)