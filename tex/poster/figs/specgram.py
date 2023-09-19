import os
import sys

import matplotlib.pyplot as plt
import numpy as np

os.chdir(os.path.dirname(__file__))  # go to current file directory


def updir(d, n):
    for _ in range(n):
        d = os.path.dirname(d)
    return d


sys.path.append(updir(os.getcwd(), 3))  # add utils dir

from classification.dataset import AudioUtil, gen_allpath, specgram

classnames, allpath_mat = gen_allpath(
    folder=r"C:\Users\leblanco.OASIS\Documents\IngeCivilPHD\Teaching\LELEC2103\Dataset_ESC-50"
)

sound = allpath_mat[0, 10]
audio = AudioUtil.open(sound)

audio2 = AudioUtil.resample(audio, 11025)
audio2 = AudioUtil.pad_trunc(audio2, 5000)
spec = np.abs(specgram(audio2[0], Nft=128)) ** 2
melspec = AudioUtil.melspectrogram(audio2, Nft=128, fs2=11025, Nmel=50)

fig = plt.figure()
plt.imshow(np.log(spec), aspect="auto", cmap="binary")
plt.axis("off")
plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

fig = plt.figure()
plt.imshow(np.log(melspec), aspect="auto", cmap="binary")
plt.axis("off")
plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
plt.show()
