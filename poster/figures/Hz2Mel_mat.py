import librosa  # For audio signal computations as MFCC
import matplotlib.pyplot as plt
import numpy as np

Nmel = 20
Nft = 512
fs_down = 11025

"Obtain the Hz2Mel transformation matrix"
mels = librosa.filters.mel(sr=fs_down, n_fft=Nft, n_mels=Nmel)
mels = mels[:, :-1]
mels = mels / np.max(mels)  # Normalization

"Plot"
plt.figure(figsize=(5, 4))
plt.imshow(mels, aspect="auto", cmap="binary")
plt.gca().invert_yaxis()
plt.colorbar()
plt.axis("off")
plt.subplots_adjust(top=0.98, bottom=0.02, right=1, left=0, hspace=0, wspace=0)
plt.show()
