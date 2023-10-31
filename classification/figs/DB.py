"""
    Author : Olivier Leblanc - UCLouvain
    Date : 19/09/2022

    Code description :
    __________________
    Show spectrogram of a noise.

"""
<<<<<<< refs/remotes/upstream/main
import matplotlib.pyplot as plt
import numpy as np

from classification.utils.audio import AudioUtil
from classification.utils.plots import plot_specgram
=======
import os
import sys

os.chdir(os.path.dirname(__file__))  # go to current file directory
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), "utils"))  # add utils dir

import matplotlib.pyplot as plt
import numpy as np

"Self created functions"
from sound_processing_fun import melspecgram, specgram
from utils import plot_specgram

# from DL_model import *
>>>>>>> Revert "enlever le chain de argu"

fs_down = 11025  # Hz
n = 220544  # number of samples
"Compute the melspecgrams"
sig = 1e-2
noise = sig * np.random.randn(n)
<<<<<<< refs/remotes/upstream/main
audio = noise, fs_down
spec_noise = AudioUtil.specgram(audio)
melspec_noise = AudioUtil.melspectrogram(audio)
=======
spec_noise = specgram(noise)
melspec_noise = melspecgram(noise)
>>>>>>> Revert "enlever le chain de argu"

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
<<<<<<< refs/remotes/upstream/main
plt.savefig("noise.png")
=======
plt.savefig("../figs/images/noise.png")
>>>>>>> Revert "enlever le chain de argu"
plt.show()
