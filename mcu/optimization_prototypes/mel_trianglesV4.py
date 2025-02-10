import numpy as np
import matplotlib.pyplot as plt

TEST = 1

################## Mel Approximation ##################
def hz_to_mel(f):   return 2595 * np.log10(1 + f / 700)
def mel_to_hz(mel): return 700 * (10**(mel / 2595) - 1)

def mel_approximation(f):
    if f < 1000:
        return f*1000/hz_to_mel(1000)
    else:
        return hz_to_mel(f)

# Test the mel approximation
if TEST < 1:
    fmin = 0
    fmax = 13000
    n_mels = 20

    hz_points = np.linspace(fmin, fmax, int(fmax-fmin))
    mel_points = np.array([hz_to_mel(f) for f in hz_points])
    mel_approx_points = np.array([mel_approximation(f) for f in hz_points])

    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    ax.plot(hz_points, mel_points, label="True Mel")
    ax.plot(hz_points, mel_approx_points, label="Approximation")
    ax.set_title("Mel Approximation")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Mel")
    ax.legend()
    plt.show()

################## Triangular Filter ##################

"""
triangles = [
    <len: 4 ; [1,2,2,1]>,
    <len: 8 ; [1,2,3,2,1,0,0,0]>,
    <len: 8 ; [1,2,3,3,2,1,0,0]>,
    <len: 8 ; [1,2,3,4,3,2,1,0]>,
    <len: 8 ; [1,2,3,4,4,3,2,1]>,
    <len: 16 ;[1,2,3,4,5,4,3,2,1,0,0,0,0,0,0,0]>,
    ...
]
"""

def gen_triangle_buffer(
        ptr_list: np.ndarray, 
        buffer_list: np.ndarray, 
        ptr_list_len: int,
        buffer_list_len: int,
        f_sample: int,
        num_fft: int,
        num_mel: int):
    mel_max = hz_to_mel(f_sample/2)
    mel_min = 0
    mel_points = np.linspace(mel_min, mel_max, num_mel + 1)
    hz_points = np.array([mel_to_hz(m) for m in mel_points])
    max_trig_size = int( np.round(2 * (hz_points[-1] - hz_points[-2]) * num_fft / f_sample))
    
    triangles = np.zeros(num_mel * max_trig_size, dtype=float)
    triangle_sizes = np.zeros(num_mel, dtype=int)
    triangle_offsets = np.zeros(num_mel, dtype=int)

    for i in range(1, num_mel):
        triangle_sizes[i] = (hz_points[i+1] - hz_points[i-1]) * num_fft / f_sample
        triangle_offsets[i] = int( np.round(hz_points[i-1] * num_fft / f_sample))
        for j in range(triangle_sizes[i]):
            if j < triangle_sizes[i]//2:
                triangles[i*max_trig_size + j] = j/triangle_sizes[i]
            else:
                triangles[i*max_trig_size + j] = 1 - j/triangle_sizes[i]
            triangles[i*max_trig_size + j] = int(triangles[i*max_trig_size + j] * 2**16 / triangle_sizes[i])

    return triangles, triangle_sizes, triangle_offsets

# Test the triangle buffer
if TEST < 2:
    f_sample = 16000
    num_fft = 1024
    num_mel = 20
    # Draw a 2D matrix image of the triangle buffer
    triangle_buffer, triangle_sizes, triangle_offsets = gen_triangle_buffer(
        None,
        None,
        0,
        0,
        f_sample,
        num_fft,
        num_mel)

    # Compare the triangle to librosa
    import librosa.display
    import librosa
    # Create mel filter bank
    mel_filter_bank = librosa.filters.mel(sr=f_sample, n_fft=num_fft, n_mels=num_mel)

    ########################################################

    # Prepare triangle buffer matrix (assumed reshaped as num_mel rows)
    triangle_matrix = triangle_buffer.reshape(num_mel, -1)
    # Prepare the librosa matrix for comparison (already computed)
    max_size_librosa = np.max(np.sum(mel_filter_bank > 0, axis=1))
    librosa_mel = np.zeros((num_mel, max_size_librosa))
    for i in range(num_mel):
        position = np.where(mel_filter_bank[i] > 0)[0]
        librosa_mel[i, :len(position)] = mel_filter_bank[i, position]

    # Determine common width for error calculation
    common_width = min(triangle_matrix.shape[1], librosa_mel.shape[1])
    trig_matrix_norm = triangle_matrix[:, :common_width] / np.max(triangle_matrix, axis=1)[:, None]
    librosa_matrix_norm = librosa_mel[:, :common_width] / np.max(librosa_mel, axis=1)[:, None]
    error_matrix = np.abs(trig_matrix_norm - librosa_matrix_norm)

    # Create figure with three subplots side by side
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

    # Plot triangle buffer
    librosa.display.specshow(triangle_matrix, x_axis='linear', ax=ax1)
    ax1.set_title("Triangle Buffer")
    ax1.set_xlabel("Frequency slots")
    ax1.set_ylabel("Mel")

    # Plot librosa mel filter bank
    librosa.display.specshow(librosa_mel, x_axis='linear', ax=ax2)
    ax2.set_title("Librosa Mel Filter Bank")
    ax2.set_xlabel("Frequency slots")
    ax2.set_ylabel("Mel")

    # Plot error graph (absolute difference) on the common region
    librosa.display.specshow(error_matrix, x_axis='linear', ax=ax3)
    ax3.set_title("Error (Absolute Difference)")
    ax3.set_xlabel("Frequency slots")
    ax3.set_ylabel("Mel")
    ax3.collections[0].set_cmap('hot')

    # Add colorbars to each subplot
    fig.colorbar(ax1.collections[0], ax=ax1, orientation='horizontal')
    fig.colorbar(ax2.collections[0], ax=ax2, orientation='horizontal')
    fig.colorbar(ax3.collections[0], ax=ax3, orientation='horizontal')

    plt.tight_layout()

    ########################################################

    # Create figure with three subplots side by side
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

    # Plot the Librosa Mel Filter Bank on the left subplot
    librosa.display.specshow(mel_filter_bank, x_axis='linear', ax=ax1)
    ax1.set_title("Librosa Mel Filter Bank")
    ax1.set_xlabel("Frequency slots")
    ax1.set_ylabel("Mel")
    fig.colorbar(ax1.collections[0], ax=ax1, orientation='horizontal')

    # Prepare triangles matrix for displaying the triangle buffer data
    triangles = np.zeros((num_mel, num_fft // 2))
    max_size_trig = len(triangle_buffer) // num_mel
    for i in range(num_mel):
        size = triangle_sizes[i]
        offset = triangle_offsets[i]
        triangles[i, offset:offset+size] = triangle_buffer[i * max_size_trig : i * max_size_trig + size]

    # Plot the triangle buffer on the middle subplot
    librosa.display.specshow(triangles, x_axis='linear', ax=ax2)
    ax2.set_title("Triangle Buffer")
    ax2.set_xlabel("Frequency slots")
    ax2.set_ylabel("Mel")
    fig.colorbar(ax2.collections[0], ax=ax2, orientation='horizontal')

    # Determine common width for error calculation and compute error matrix
    common_width = min(mel_filter_bank.shape[1], triangles.shape[1])
    mel_filter_norm = mel_filter_bank[:, :common_width] / np.max(mel_filter_bank, axis=1)[:, None]
    triangles_norm = triangles[:, :common_width] / np.max(triangles, axis=1)[:, None]
    error_matrix = np.abs(mel_filter_norm - triangles_norm)

    # Plot the error matrix on the right subplot
    librosa.display.specshow(error_matrix, x_axis='linear', ax=ax3)
    ax3.set_title("Error (Absolute Difference)")
    ax3.set_xlabel("Frequency slots")
    ax3.set_ylabel("Mel")
    ax3.collections[0].set_cmap('hot')
    fig.colorbar(ax3.collections[0], ax=ax3, orientation='horizontal')

    plt.tight_layout()
    plt.show()

