import numpy as np

# import torch
# from DL_model import *

# -----------------------------------------------------------------------------
"""
Synthesis of the functions in :

- accuracy : Compute the accuracy between prediction and ground truth.
- fixed_to_float(x,e) : Convert signal from integer fixed format to floating point.
- float2fixed : Convert signal from float format to integer fixed point, here q15_t.
- fixed2binary : convert int in q15_t format into a 16-bit binary string.
- resize_and_fix_origin : Pads sig to reach length `L`, and shift it in order to cancel phase.
- convole : compute the convolution through Fourier transform
- correlate : Compute the correlation through Fourier transform
- threshold : Threshold an audio signal based on its energy per packet of Nft samples
- quantize  : quantize a signal on n-bits
- flatten : Flattens a multidimensional array into a 1D array
- STFT_subsamp : compute an undersampled STFT
- STFT : compute an averaged compressed STFT
- load_model : Load pretrained model
- eval_model : Run inference on trained model with the validation set
"""
# -----------------------------------------------------------------------------


def accuracy(prediction, target):
    """
    Compute the accuracy between prediction and ground truth.
    """

    return np.sum(prediction == target) / len(prediction)


def fixed_to_float(x, e):
    """Convert signal from integer fixed format to floating point."""
    c = abs(x)
    sign = 1
    if x < 0:
        # convert back from two's complement
        c = x - 1
        c = ~c
        sign = -1
    f = (1.0 * c) / (2**e)
    f = f * sign
    return f


def float2fixed(audio, maxval=1, q=15):
    """Convert signal from float format to integer fixed point, here q15_t.
    Divide by this maximal value to increase range.
    In q15_t, the first bit is for the sign and the 15 others are for quantization of the signal from 0 to 1
    """
    return (np.round((audio / maxval) * (2**q - 1))).astype(int)


def fixed_to_binary(sig, q=15):
    """Convert int in q15_t format into a 16-bit binary string."""
    val = 2 ** (q - 1)
    binary = [
        (int)((-1) ** (np.sign(sig) + 1)),
    ]
    sig = np.abs(sig)
    while val >= 1:
        boolean = (int)(sig > val)
        binary += [
            boolean,
        ]
        sig -= boolean * val
        val = val // 2
    return "".join([str(item) for item in binary])


def resize_and_fix_origin(sig, L):
    """Pads sig to reach length `L`, and shift it in order to cancel phase.
    This is based on the assumption that the sig is centered in space.
    """
    pad = L - len(sig)
    # shift less if sig is even, to start with 2 central items
    shift = (len(sig) - 1) // 2
    sig = np.pad(sig, (0, pad))
    sig = np.roll(sig, -shift)
    return sig


def convolve(sig1, sig2):
    """
    Compute the convolution through Fourier transform
    """
    sig1fft = np.fft.fft(sig1)
    sig2fft = np.fft.fft(resize_and_fix_origin(sig2, len(sig1)))
    return np.fft.ifft(sig2fft * sig1fft).real


def correlate(sig1, sig2, sig1fft, sig2fft):
    """
    Compute the correlation through Fourier transform
    """
    L1 = len(sig1)
    L2 = len(sig2)
    if L1 > L2:
        sig2 = resize_and_fix_origin(sig2, L1)
        sig2fft = np.fft.fft(sig2)
    else:
        sig1 = resize_and_fix_origin(sig1, L2)
        sig1fft = np.fft.fft(sig1)

    return np.fft.ifft(sig2fft * np.conj(sig1fft)).real


def threshold(sig, thres=8, Nft=512):
    """
    Threshold an audio signal based on its energy per packet of Nft samples.
    Inputs:
        - sig : 1D array for the audio signal
        - thres : the threshold value for the energy, must change with Nft
        - Nft : Number of samples to compute the energy
    Output:
        - thresholded : the thresholded signal
    """

    "Crop the signal"
    inddiff = len(sig) % Nft
    if inddiff != 0:
        sig = sig[:-inddiff]

    "Threshold the signal"
    tempmat = np.reshape(np.abs(sig) ** 2, (int(len(sig) / Nft), Nft))
    tempvec = np.sum(tempmat, axis=1)
    thresholded = sig * np.repeat(tempvec > thres, Nft)
    return thresholded


def quantize(sig, n=8):
    """Quantize a signal with n bits.
    Inputs :
        - sig = signal, 1D or 2D array
        - n   = number of bits for quantization
    Outputs :
        - quantized = the quantized signal
    """
    xmin = np.min(sig)
    xmax = np.max(sig)

    normed = (sig - xmin) / (xmax - xmin)

    numbins = 2**n  # 2^n
    Delta = 1 / (2**n + 1)  # spacing between the bins
    bins = Delta / 2 + np.linspace(-Delta / 2, 1 - Delta / 2, numbins)

    if sig.ndim == 1:  # signal is 1D
        mat = np.reshape(np.repeat(normed, numbins), (len(sig), numbins))
    elif sig.ndim == 2:  # signal is 2D
        mat = np.repeat(normed, numbins)
        mat = mat.reshape(sig.shape[0], sig.shape[1], numbins)
    dists = (mat - bins) ** 2
    bests = np.argmin(dists, axis=sig.ndim)
    quantized_normed = bins[bests]
    quantized = xmin + (xmax - xmin) * quantized_normed
    return quantized


def flatten(thelist, flat_list=[]):
    """
    Flattens a multidimensional array into a 1D array
    """
    for elem in thelist:
        if isinstance(elem, list):
            flatten(elem, flat_list)
        else:
            flat_list.append(elem)

    return flat_list


def STFT_subsamp(sig, L=8, L2=10, window="hanning"):
    """
    This function aims to compute an undersampled STFT of sig.
    But it takes only some specific spectral samples instead of averaging between those.
        Inputs : sig : the 1D audio signal
                   L : number of time samples
                  L2 : number of frequency samples
              window : the window used for reducing spectrum artifacts
        Output : mat : the STFT matrix
    """
    N = len(sig)
    N_FT = int(np.floor(N / L))

    if window == "hanning":
        w = np.hanning(N_FT)
    elif window == "blackman":
        w = np.blackman(N_FT)
    else:
        w = np.ones(N_FT)

    y = np.kron(np.ones(L), w) * sig[: N_FT * L]
    ymat = np.reshape(y, (N_FT, L), "F")

    mat = np.zeros((L2, L), dtype=complex)
    for i in np.arange(L2):
        tempmat = ymat[i::L2, :]
        mat[i, :] = np.sum(tempmat, axis=0)
    mat = np.fft.fft(mat, axis=0)
    return mat


def STFT(sig, L=8, L2=10, window="hanning"):
    """
    This function aims to compute an undersampled STFT of sig.
        Inputs : sig : the 1D audio signal
                   L : number of time samples
                  L2 : number of frequency samples
              window : the window used for reducing spectrum artifacts
        Outputs : mat : the STFT matrix
    """

    N = len(sig)
    # Pad signal s.t. its length N is a multiple of L*L2
    sig = np.pad(sig, (0, L * L2 - N % (L * L2)), "constant", constant_values=0)
    N = len(sig)
    N_FT = int(N / L)
    if window == "hanning":
        w = np.hanning(N_FT)
    elif window == "blackman":
        w = np.blackman(N_FT)
    else:
        w = np.ones(N_FT)
    temp = 1 - np.exp(
        -1j * 2 * np.pi * np.kron(np.ones(int(N / L2)), np.arange(L2)) / L2
    )
    temp2 = 1 - np.exp(-1j * 2 * np.pi * np.kron(np.ones(L), np.arange(N_FT)) / N_FT)
    temp3 = temp / temp2
    temp3[np.isnan(temp3)] = 1
    temp3[np.isinf(temp3)] = 1
    y = np.kron(np.ones(L), w) * sig[: N_FT * L] * temp3 * L / N_FT
    ymat = np.reshape(y, (N_FT, L), "F")

    mat = np.zeros((L2, L), dtype=complex)
    for i in np.arange(L2):
        tempmat = ymat[i::L2, :]
        mat[i, :] = np.sum(tempmat, axis=0)
    mat = np.fft.fft(mat, axis=0)
    return mat


def load_model(model_path):
    """
    Load pretrained model
        Inputs : model_path : string
        Outputs : myModel
    """

    myModel = torch.load(model_path)
    # myModel.float()
    myModel.eval()

    return myModel


def eval_model(model, fv, gt=0):
    """
    Run inference on trained model with the validation set
        Inputs : model :
                 fv    :
                 gt    : ground truth
        Outputs : /
    """
    myds = SoundDS([gt], melspec=fv)
    dl = torch.utils.data.DataLoader(myds, batch_size=1, shuffle=False)

    y_predict, y_true = inference(model, dl, batch_size=1)

    print("Prediction : {} ".format(y_predict))
    print("Ground truth : {}".format(y_true))
