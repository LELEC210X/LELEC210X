import random

import librosa
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import soundfile as sf
from numpy import ndarray
from scipy.signal import fftconvolve

# -----------------------------------------------------------------------------
"""
Synthesis of the classes in :
- AudioUtil : util functions to process an audio signal.
- Feature_vector_DS : Create a dataset class for the feature vectors.
"""
# -----------------------------------------------------------------------------


class AudioUtil:
    """
    Define a new class with util functions to process an audio signal.
    """

    def open(audio_file) -> tuple[ndarray, int]:
        """
        Load an audio file.

        :param audio_file: The path to the audio file.
        :return: The audio signal as a tuple (signal, sample_rate).
        """
        sig, sr = sf.read(audio_file)
        if sig.ndim > 1:
            sig = sig[:, 0]
        return (sig, sr)

    def play(audio):
        """
        Play an audio file.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        """
        sig, sr = audio
        sd.play(sig, sr)

    def normalize(audio, target_dB=52) -> tuple[ndarray, int]:
        """
        Normalize the energy of the signal.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param target_dB: The target energy in dB.
        """
        sig, sr = audio
        sign = sig / np.sqrt(np.sum(np.abs(sig) ** 2))
        C = np.sqrt(10 ** (target_dB / 10))
        sign *= C
        return (sign, sr)

    def resample(audio, newsr=11025) -> tuple[ndarray, int]:
        """
        Resample to target sampling frequency.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param newsr: The target sampling frequency.
        """
        sig, sr = audio

        ### TO COMPLETE

        return (resig, newsr)

    def pad_trunc(audio, max_ms) -> tuple[ndarray, int]:
        """
        Pad (or truncate) the signal to a fixed length 'max_ms' in milliseconds.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param max_ms: The target length in milliseconds.
        """
        sig, sr = audio
        sig_len = len(sig)
        max_len = int(sr * max_ms / 1000)

        if sig_len > max_len:
            # Truncate the signal to the given length at random position
            # begin_len = random.randint(0, max_len)
            begin_len = 0
            sig = sig[begin_len : begin_len + max_len]

        elif sig_len < max_len:
            # Length of padding to add at the beginning and end of the signal
            pad_begin_len = random.randint(0, max_len - sig_len)
            pad_end_len = max_len - sig_len - pad_begin_len

            # Pad with 0s
            pad_begin = np.zeros(pad_begin_len)
            pad_end = np.zeros(pad_end_len)

            # sig = np.append([pad_begin, sig, pad_end])
            sig = np.concatenate((pad_begin, sig, pad_end))

        return (sig, sr)

    def scaling(audio, scaling_limit=5) -> tuple[ndarray, int]:
        """
        Augment the audio signal by scaling it by a random factor.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param scaling_limit: The maximum scaling factor.
        """
        sig, sr = audio

        ### TO COMPLETE

        return audio

    def add_noise(audio, sigma=0.05) -> tuple[ndarray, int]:
        """
        Augment the audio signal by adding gaussian noise.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param sigma: Standard deviation of the gaussian noise.
        """
        sig, sr = audio

        ### TO COMPLETE

        return audio

    def echo(audio, nechos=2) -> tuple[ndarray, int]:
        """
        Add echo to the audio signal by convolving it with an impulse response. The taps are regularly spaced in time and each is twice smaller than the previous one.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param nechos: The number of echoes.
        """
        sig, sr = audio
        sig_len = len(sig)
        echo_sig = np.zeros(sig_len)
        echo_sig[0] = 1
        echo_sig[(np.arange(nechos) / nechos * sig_len).astype(int)] = (
            1 / 2
        ) ** np.arange(nechos)

        sig = fftconvolve(sig, echo_sig, mode="full")[:sig_len]
        return (sig, sr)

    def filter(audio, filt) -> tuple[ndarray, int]:
        """
        Filter the audio signal with a provided filter. Note the filter is given for positive frequencies only and is thus symmetrized in the function.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param filt: The filter to apply.
        """
        sig, sr = audio

        ### TO COMPLETE

        return (sig, sr)

    def add_bg(
        audio, dataset, num_sources=1, max_ms=5000, amplitude_limit=0.1
    ) -> tuple[ndarray, int]:
        """
        Adds up sounds uniformly chosen at random to audio.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param dataset: The dataset to sample from.
        :param num_sources: The number of sounds to add.
        :param max_ms: The maximum duration of the sounds to add.
        :param amplitude_limit: The maximum amplitude of the added sounds.
        """
        sig, sr = audio

        ### TO COMPLETE

        return audio

    def specgram(audio, Nft=512, fs2=11025) -> ndarray:
        """
        Compute a Spectrogram.

        :param aud: The audio signal as a tuple (signal, sample_rate).
        :param Nft: The number of points of the FFT.
        :param fs2: The sampling frequency.
        """
        ### TO COMPLETE
        # stft /= float(2**8)
        return stft

    def get_hz2mel(fs2=11025, Nft=512, Nmel=20) -> ndarray:
        """
        Get the hz2mel conversion matrix.

        :param fs2: The sampling frequency.
        :param Nft: The number of points of the FFT.
        :param Nmel: The number of mel bands.
        """
        mels = librosa.filters.mel(sr=fs2, n_fft=Nft, n_mels=Nmel)
        mels = mels[:, :-1]
        mels = mels / np.max(mels)

        return mels

    def melspectrogram(audio, Nmel=20, Nft=512, fs2=11025) -> ndarray:
        """
        Generate a Melspectrogram.

        :param audio: The audio signal as a tuple (signal, sample_rate).
        :param Nmel: The number of mel bands.
        :param Nft: The number of points of the FFT.
        :param fs2: The sampling frequency.
        """
        ### TO COMPLETE

        return melspec

    def spectro_aug_timefreq_masking(
        spec, max_mask_pct=0.1, n_freq_masks=1, n_time_masks=1
    ) -> ndarray:
        """
        Augment the Spectrogram by masking out some sections of it in both the frequency dimension (ie. horizontal bars) and the time dimension (vertical bars) to prevent overfitting and to help the model generalise better. The masked sections are replaced with the mean value.


        :param spec: The spectrogram.
        :param max_mask_pct: The maximum percentage of the spectrogram to mask out.
        :param n_freq_masks: The number of frequency masks to apply.
        :param n_time_masks: The number of time masks to apply.
        """
        Nmel, n_steps = spec.shape
        mask_value = np.mean(spec)
        aug_spec = np.copy(spec)  # avoids modifying spec

        freq_mask_param = max_mask_pct * Nmel
        for _ in range(n_freq_masks):
            height = int(np.round(random.random() * freq_mask_param))
            pos_f = np.random.randint(Nmel - height)
            aug_spec[pos_f : pos_f + height, :] = mask_value

        time_mask_param = max_mask_pct * n_steps
        for _ in range(n_time_masks):
            width = int(np.round(random.random() * time_mask_param))
            pos_t = np.random.randint(n_steps - width)
            aug_spec[:, pos_t : pos_t + width] = mask_value

        return aug_spec


class Feature_vector_DS:
    """
    Dataset of Feature vectors.
    """

    def __init__(
        self,
        dataset,
        Nft=512,
        nmel=20,
        duration=500,
        normalize=False,
        data_aug=None,
        pca=None,
        step=np.inf,
    ):
        self.dataset = dataset
        self.Nft = Nft
        self.nmel = nmel
        self.duration = duration  # ms
        self.sr = 11025
        self.normalize = normalize
        self.data_aug = data_aug
        self.data_aug_factor = 1
        if isinstance(self.data_aug, list):
            self.data_aug_factor += len(self.data_aug)
        else:
            self.data_aug = [self.data_aug]
        self.ncol = int(
            self.duration * self.sr / (1e3 * self.Nft)
        )  # number of columns in melspectrogram
        self.pca = pca
        self.step = step

    def __len__(self) -> int:
        """
        Number of items in dataset.
        """
        return len(self.dataset) * self.data_aug_factor

    def get_audiosignal(self, cls_index: tuple[str, int]) -> tuple[ndarray, int]:
        """
        Get temporal signal of i'th item in dataset.

        :param cls_index: Class name and index.
        """
        audio_file = self.dataset[cls_index]
        aud = AudioUtil.open(audio_file)
        aud = AudioUtil.resample(aud, self.sr)

        if self.data_aug is not None:
            if "add_bg" in self.data_aug:
                aud = AudioUtil.add_bg(
                    aud,
                    self.dataset,
                    num_sources=1,
                    max_ms=self.duration,
                    amplitude_limit=0.1,
                )
            if "echo" in self.data_aug:
                aud = AudioUtil.add_echo(aud)
            if "noise" in self.data_aug:
                aud = AudioUtil.add_noise(aud, sigma=0.05)
            if "scaling" in self.data_aug:
                aud = AudioUtil.scaling(aud, scaling_limit=5)

        # aud = AudioUtil.normalize(aud, target_dB=10)
        aud = (aud[0] / np.max(np.abs(aud[0])), aud[1])
        return aud

    def __getitem__(self, cls_index: tuple[str, int]) -> tuple[ndarray, int]:
        """
        Get i'th item in dataset.

        :param cls_index: Class name and index.
        """
        aud = self.get_audiosignal(cls_index)
        sgram = AudioUtil.melspectrogram(aud, Nmel=self.nmel, Nft=self.Nft)
        if self.data_aug is not None:
            if "aug_sgram" in self.data_aug:
                sgram = AudioUtil.spectro_aug_timefreq_masking(
                    sgram, max_mask_pct=0.1, n_freq_masks=2, n_time_masks=2
                )

        return sgram

    def display(self, cls_index: tuple[str, int], show_features=False):
        """
        Play sound and display i'th item in dataset.

        :param cls_index: Class name and index.
        """
        audio = self.get_audiosignal(cls_index)
        AudioUtil.play(audio)
        plt.figure(figsize=(2 + 2 * len(audio[0]) / self.sr, 3))
        sgram = AudioUtil.melspectrogram(audio, Nmel=self.nmel, Nft=self.Nft)
        plt.imshow(
            sgram,
            cmap="jet",
            origin="lower",
            aspect="auto",
        )
        plt.colorbar()

        if show_features:
            indexes = np.arange(0, len(sgram[0]) - self.ncol, self.step)
            for start in indexes:
                # (x, y) = lower left corner of rectangle
                rect = patches.Rectangle(
                    (start, 0),  # x, y
                    self.ncol,  # width
                    self.nmel - 1,  # height
                    linewidth=2,
                    edgecolor="magenta",
                    facecolor="none",
                    alpha=1,
                )
                plt.gca().add_patch(rect)

        plt.title(audio)
        plt.title(self.dataset.__getname__(cls_index))
        plt.show()

    def get_feature_vectors(self) -> tuple[ndarray, ndarray]:
        """
        Returns all feature vectors and their labels.
        """
        classnames = self.dataset.list_classes()

        y = []
        X = []

        for class_idx, classname in enumerate(classnames):
            for s in range(self.data_aug_factor):
                for idx in range(self.dataset.naudio[classname]):
                    sgram = self[classname, idx]
                    fv = self.treat_spec(sgram)

                    X += list(fv)
                    y += [classname] * len(fv)

        return np.array(X), np.array(y)

    def mod_data_aug(self, data_aug=[]) -> None:
        """
        Modify the data augmentation options.

        :param data_aug: The new data augmentation options.
        """
        self.data_aug = data_aug
        if not isinstance(self.data_aug, list):
            self.data_aug = [self.data_aug]

        self.data_aug_factor = 1 + len(self.data_aug)

    def treat_spec(self, sgram):
        """
        Turns a melspectrogram into a feature vector.

        :param sgram: The melspectrogram to treat.
        """
        indexes = np.arange(0, len(sgram[0]) - self.ncol, self.step, dtype=int)
        sgrams = [sgram[:, i : i + self.ncol] for i in indexes]
        sgrams = np.array(sgrams)

        fv = sgrams.reshape(sgrams.shape[0], -1)  # feature vector

        if self.normalize:
            fv /= np.linalg.norm(fv, axis=1, keepdims=True)

        if self.pca is not None:
            fv = np.array([self.pca.transform([i])[0] for i in fv])

        return fv
