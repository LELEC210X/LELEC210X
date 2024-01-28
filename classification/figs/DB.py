"""
Author : Olivier Leblanc - UCLouvain
Date : 19/09/2022

Code description :
__________________
Show spectrogram of a noise.

"""
import matplotlib.pyplot as plt
import numpy as np

from classification.utils.audio import AudioUtil
from classification.utils.plots import plot_specgram

fs_down = 11025  # Hz
n = 220544  # number of samples
"Compute the melspecgrams"
sig = 1e-2
noise = sig * np.random.randn(n)
audio = noise, fs_down
spec_noise = AudioUtil.specgram(audio)
melspec_noise = AudioUtil.melspectrogram(audio)

"Plot"
fig = plt.figure(figsize=(6, 4))
plot_specgram(
    np.log(spec_noise),
    ax=fig.gca(),
    is_mel=False,
    title="Specgram of noise",
    tf=n / fs_down,
)

fig2 = plt.figure(figsize=(6, 4))
plot_specgram(
    np.log(melspec_noise), ax=fig2.gca(), is_mel=True, title="Noise", tf=n / fs_down
)
plt.savefig("noise.png")
plt.show()
