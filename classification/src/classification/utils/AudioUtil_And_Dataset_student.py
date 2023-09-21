import os

os.chdir(os.path.dirname(__file__))  # go to current file directory

import matplotlib.pyplot as plt
import numpy as np

"Sound processing"
import random

import librosa
import sounddevice as sd
import soundfile as sf
from scipy import signal
from scipy.signal import fftconvolve

#-----------------------------------------------------------------------------
"""
Synthesis of the classes in :
- AudioUtil : util functions to process an audio signal
- SoundDS : Create a dataset object
"""
#-----------------------------------------------------------------------------

def getclass ( sound, format='.wav' ) :
    """Get class name of a sound path directory.
    Note: this function is only compatible with ESC-50 dataset path organization.
    """
    L = len(format)

    folders = sound.split(os.path.sep)
    if (folders[-1][-L:] == format):
        return folders[-2].split('-')[1]
    else:
        return folders[-1].split('-')[1]

def getname ( sound ) :
    """
    Get name of a sound from its path directory.
    """
    return os.path.sep.join(sound.split(os.path.sep)[-2:])

def gen_allpath(folder=os.path.join(os.path.dirname(os.getcwd()), 'dataset')):
    """
    Create a matrix with path names of height H=50classes and W=40sounds per class
    and an array with all class names.
    """
    classpath = [ f.path for f in os.scandir(folder) if f.is_dir() ]
    classpath = sorted(classpath)

    allpath = [None]*len(classpath)
    classnames = [None]*len(classpath)
    for ind, val in enumerate(classpath):
        classnames[ind] = getclass(val).strip()
        sublist = [f.path for f in os.scandir(val)]
        allpath[ind] = sublist

    allpath = np.array(allpath)
    return classnames, allpath

class AudioUtil:
    """
    Define a new class with util functions to process an audio signal.
    """

    # ----------------------------
    # Load an audio file. Return the signal as a tensor and the sample rate
    # ----------------------------
    @staticmethod
    def open(audio_file):
        sig, sr = sf.read(audio_file)
        if sig.ndim > 1:
            sig = sig[:, 0]
        return (sig, sr)

    # ----------------------------
    # Play an audio file.
    # ----------------------------
    @staticmethod
    def play(audio):
        sig, sr = audio
        sd.play(sig, sr)

    # ----------------------------
    # Normalize the energy of the signal
    # ----------------------------
    @staticmethod
    def normalize(audio, target_dB=52):
        sig, sr = audio
        sign = sig/np.sqrt(np.sum(np.abs(sig) ** 2))
        C = np.sqrt(10 ** (target_dB / 10))
        sign *= C
        return (sign, sr)

    # ----------------------------
    # Resample to target sampling frequency
    # ----------------------------
    @staticmethod
    def resample(aud, newsr=11025):
        sig, sr = aud

        ### TO COMPLETE
        return (resig, newsr)

    # ----------------------------
    # Pad (or truncate) the signal to a fixed length 'max_ms' in milliseconds
    # ----------------------------
    @staticmethod
    def pad_trunc(aud, max_ms):
        sig, sr = aud
        sig_len = len(sig)
        max_len = int(sr * max_ms / 1000)

        if sig_len > max_len:
            # Truncate the signal to the given length at random position
            # begin_len = random.randint(0, max_len)
            begin_len = 0
            sig = sig[begin_len:begin_len+max_len]

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

    # ----------------------------
    # Shifts the signal to the left or right by some percent. Values at the end
    # are 'wrapped around' to the start of the transformed signal.
    # ----------------------------
    @staticmethod
    def time_shift(aud, shift_limit=0.4):
        sig, sr = aud
        sig_len = len(sig)
        shift_amt = int(random.random() * shift_limit * sig_len)
        return (np.roll(sig, shift_amt), sr)

    # ----------------------------
    # Augment the audio signal by scaling it by a random factor.
    # ----------------------------
    @staticmethod
    def scaling(aud, scaling_limit=5):
        sig, sr = aud

        ### TO COMPLETE
        return aud

    # ----------------------------
    # Augment the audio signal by adding gaussian noise.
    # ----------------------------
    @staticmethod
    def add_noise(aud, sigma=0.05):
        sig, sr = aud
        return aud

    # ----------------------------
    # Add echo to the audio signal by convolving it with an impulse response.
    # The taps are regularly spaced in time and each is twice smaller than the previous one.
    # ----------------------------
    @staticmethod
    def echo(aud, nechos=2):
        sig, sr = aud
        sig_len = len(sig)
        echo_sig = np.zeros(sig_len)
        echo_sig[0] = 1
        echo_sig[(np.arange(nechos) / nechos * sig_len).astype(int)] = (
            1 / 2
        ) ** np.arange(nechos)

        sig = fftconvolve(sig, echo_sig, mode="full")[:sig_len]
        return (sig, sr)

    # ----------------------------
    # Filter the audio signal with a provided filter.
    # Note the filter is given for positive frequencies only and is thus symmetrized in the function. 
    # ----------------------------
    @staticmethod
    def filter(aud, filt):
        sig, sr = aud

        ### TO COMPLETE
        return (sig, sr)

    # ----------------------------
    # Augment the audio signal by adding another one in background.
    # ----------------------------
    @staticmethod
    def add_bg(aud, allpath, num_sources=1, max_ms=5000, amplitude_limit=0.1):
        """
        Adds up sounds uniformly chosen at random to aud.

        Inputs
        aud:  [2-tuple, (1D audio signal, sampling frequency)]
        allpath: [2D str list, size:(n_classes, n_sounds), contains the paths to each sound]
        num_sources : [int, number of sounds added in background]
        max_ms : [float, duration of aud in milliseconds, necessary to pad_trunc]
        amplitude_limit: [float, maximum ratio between amplitudes of additional sounds and sound of interest]

        Outputs
          aud_bg:  [2-tuple, (1D audio signal with additional sounds in background, sampling frequency)]
        """

        sig, sr = aud

        ### TO COMPLETE

        return aud

    # ----------------------------
    # Generate a Spectrogram
    # ----------------------------
    @staticmethod
    def specgram(aud, Nft=512, fs2=11025):
        ### TO COMPLETE
        # stft /= float(2**8)
        return stft

    # ----------------------------
    # Get the hz2mel conversion matrix
    # ----------------------------
    @staticmethod
    def get_hz2mel(fs2=11025, Nft=512, Nmel=20):
        mels = librosa.filters.mel(sr=fs2, n_fft=Nft, n_mels=Nmel)
        mels = mels[:, :-1]
        mels = mels / np.max(mels)

        return mels

    # ----------------------------
    # Generate a Melspectrogram
    # ----------------------------
    @staticmethod
    def melspectrogram(aud, Nmel=20, Nft=512, fs2=11025):
        ### TO COMPLETE

        return melspec

    # ----------------------------
    # Augment the Spectrogram by masking out some sections of it in both the frequency
    # dimension (ie. horizontal bars) and the time dimension (vertical bars) to prevent
    # overfitting and to help the model generalise better. The masked sections are
    # replaced with the mean value.
    # ----------------------------
    @staticmethod
    def spectro_aug_timefreq_masking(
        spec, max_mask_pct=0.1, n_freq_masks=1, n_time_masks=1
    ):
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


# ____________________________________________________________________________
class SoundDS:
    """
    Sound Dataset
    """

    def __init__(
        self,
        class_ids,
        Nft=512,
        nmel=20,
        duration=500,
        shift_pct=0.4,
        data_path=None,
        allpath_mat=None,
        normalize=False,
        data_aug=None,
        pca=None,
    ):
        self.class_ids = class_ids
        self.Nft = Nft
        self.nmel = nmel
        self.data_path = data_path
        self.allpath_mat = allpath_mat
        self.duration = duration  # ms
        self.sr = 11025
        self.shift_pct = shift_pct  # percentage of total
        self.normalize = normalize
        self.data_aug = data_aug
        self.data_aug_factor = 1
        if (isinstance(self.data_aug, list)):
            self.data_aug_factor += len(self.data_aug)
        else:
            self.data_aug = [self.data_aug]
        self.ncol = int(self.duration*self.sr /(1e3*self.Nft)) # number of columns in melspectrogram
        self.pca = pca

    # ----------------------------
    # Number of items in dataset
    # ----------------------------
    def __len__(self):
        return np.size(self.data_path)

    # ----------------------------
    # Get temporal signal of i'th item in dataset
    # ----------------------------
    def get_audiosignal(self, idx):

        # class_id = self.class_ids[idx] # Get the Class ID
        audio_file = self.data_path[idx]
        aud = AudioUtil.open(audio_file)
        aud = AudioUtil.resample(aud, self.sr)
        aud = AudioUtil.time_shift(aud, self.shift_pct)
        aud = AudioUtil.pad_trunc(aud, self.duration)
        if self.data_aug is not None:
            if "add_bg" in self.data_aug:
                aud = AudioUtil.add_bg(
                    aud,
                    self.allpath_mat,
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
        aud = (aud[0]/np.max(np.abs(aud[0])), aud[1])
        return aud

    # ----------------------------
    # Get i'th item in dataset
    # ----------------------------
    def __getitem__(self, idx):

        class_id = self.class_ids[idx]  # Get the Class ID

        aud = self.get_audiosignal(idx)
        sgram = AudioUtil.melspectrogram(aud, Nmel=self.nmel, Nft=self.Nft)
        if self.data_aug is not None:
            if "aug_sgram" in self.data_aug:
                sgram = AudioUtil.spectro_aug_timefreq_masking(
                    sgram, max_mask_pct=0.1, n_freq_masks=2, n_time_masks=2
                )

        sgram_crop = sgram[:, : self.ncol]
        fv = sgram_crop.flatten() #feature vector
        if (self.normalize):
            fv /= np.linalg.norm(fv)
        if (self.pca is not None):
            fv = self.pca.transform([fv])[0]
        return fv, class_id

    # ----------------------------
    # Play sound and display i'th item in dataset
    # ----------------------------
    def display(self, idx):
        aud = self.get_audiosignal(idx)
        AudioUtil.play(aud)
        plt.figure(figsize=(5, 4))
        plt.imshow(
            AudioUtil.melspectrogram(aud, Nmel=self.nmel, Nft=self.Nft),
            cmap="jet",
            origin="lower",
            aspect="auto",
        )
        plt.colorbar()
        plt.title(os.path.sep.join(self.data_path[idx].split(os.path.sep)[-2:]))
        plt.show()

    # ----------------------------
    # Modify the data augmentation options
    # ----------------------------
    def mod_data_aug(self, data_aug):
        self.data_aug = data_aug
        self.data_aug_factor = 1
        if (isinstance(self.data_aug, list)):
            self.data_aug_factor += len(self.data_aug)
        else:
            self.data_aug = [self.data_aug]