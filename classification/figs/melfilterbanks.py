"""
    Author : Olivier Leblanc - UCLouvain
    Date : 26/09/2022

    Code description :
    __________________
    Show mel filterbanks.

"""

import os

import librosa
import matplotlib.pyplot as plt
import numpy as np

os.chdir(os.path.dirname(__file__))  # go to current file directory

Nft = 512
fs = 11025  # Hz
n_mels = 20

mel = librosa.filters.mel(sr=fs, n_fft=Nft, n_mels=n_mels)
mel = mel[:, :-1]
"Normalization"
mel = mel / np.max(mel)

fig = plt.figure(figsize=(6, 6))
ax = fig.gca()
colors = plt.cm.jet(np.linspace(0, 1, mel.shape[0]))
for line in range(mel.shape[0]):
    ax.plot(mel[line, :], color=colors[line])
plt.title("Mel filterbanks")
plt.savefig("images/mel_filterbanks.svg")
plt.show()
