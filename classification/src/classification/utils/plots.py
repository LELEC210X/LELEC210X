import matplotlib.pyplot as plt
import numpy as np

"For confusion matrix plot"
from seaborn import heatmap
from sklearn.metrics import confusion_matrix

# -----------------------------------------------------------------------------
"""
Synthesis of the functions in :

- show_confusion_matrix : plot confusion matrix.
- plot_audio : Plot an audiosignal in time and frequency
- plot_specgram : Plot a spectrogram (2D matrix)
- plot_decision_boundary : Plot decision boundary of a classifier.
"""
# -----------------------------------------------------------------------------


def show_confusion_matrix(y_predict, y_true, classnames, title=""):
    """
    From target labels and prediction arrays, sort them appropriately and plot confusion matrix.
    The arrays can contain either ints or str quantities, as long as classnames contains all the elements present in them.
    """
    # # Reorder the prediction array
    # labels = np.zeros_like(y_predict)
    # for i in np.arange(len(classnames)):
    #     mask = [None]*len(y_predict)
    #     for j in np.arange(len(mask)):
    #         mask[j] = (y_predict[j] == classnames[i])
    #     labels[mask] = mode(y_true2[mask])[0]

    plt.figure(figsize=(3, 3))
    confmat = confusion_matrix(y_true, y_predict)
    heatmap(
        confmat.T,
        square=True,
        annot=True,
        fmt="d",
        cbar=False,
        xticklabels=classnames,
        yticklabels=classnames,
        ax=plt.gca(),
    )
    plt.xlabel("True label")
    plt.ylabel("Predicted label")
    plt.title(title)
    plt.show()
    return None


def plot_audio(audio, audio_down, fs=44100, fs_down=11025):
    """
    Plot the temporal and spectral representations of the original audio signal and its downsampled version
    """
    M = fs // fs_down  # Downsampling factor

    L = len(audio)
    L_down = len(audio_down)

    frequencies = np.arange(-L // 2, L // 2, dtype=np.float64) * fs / L
    frequencies_down = (
        np.arange(-L_down // 2, L_down // 2, dtype=np.float64) * fs_down / L_down
    )
    spectrum = np.fft.fftshift(np.fft.fft(audio))
    spectrum_down = np.fft.fftshift(np.fft.fft(audio_down))

    fig = plt.figure(figsize=(12, 4))
    ax1 = fig.add_axes([0.0, 0.0, 0.42, 0.9])
    ax2 = fig.add_axes([0.54, 0.0, 0.42, 0.9])

    ax1.plot(np.arange(L) / fs, audio, "b", label="Original")
    ax1.plot(np.arange(L_down) / fs_down, audio_down, "r", label="Downsampled")
    ax1.legend()
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Amplitude [-]")
    ax1.set_title("Temporal signal")

    ax2.plot(frequencies, np.abs(spectrum), "b", label="Original")
    ax2.plot(
        frequencies_down, np.abs(spectrum_down) * M, "r", label="Downsampled", alpha=0.5
    )  # energy scaling by M
    ax2.legend()
    ax2.set_xlabel("Frequency [Hz]")
    ax2.set_ylabel("Amplitude [-]")
    ax2.set_title("Modulus of FFT")
    plt.show()

    plt.figure(figsize=(12, 4))
    plt.plot(np.arange(L) / fs, audio, ".-b", label="Original")
    plt.plot(np.arange(L_down) / fs_down, audio_down, ".-r", label="Downsampled")
    plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude [-]")
    plt.title("Zoom on Temporal signal")
    plt.xlim([1, 1.0025])


def plot_specgram(
    specgram,
    ax,
    is_mel=False,
    title=None,
    xlabel="Time [s]",
    ylabel="Frequency [Hz]",
    cmap="jet",
    cb=True,
    tf=None,
    invert=True,
):
    """Plot a spectrogram (2D matrix) in a chosen axis of a figure.
    Inputs:
        - specgram = spectrogram (2D array)
        - ax       = current axis in figure
        - title
        - xlabel
        - ylabel
        - cmap
        - cb       = show colorbar if True
        - tf       = final time in xaxis of specgram
    """
    if tf is None:
        tf = specgram.shape[1]

    if is_mel:
        ylabel = "Frequency [Mel]"
        im = ax.imshow(
            specgram, cmap=cmap, aspect="auto", extent=[0, tf, specgram.shape[0], 0]
        )
    else:
        im = ax.imshow(
            specgram,
            cmap=cmap,
            aspect="auto",
            extent=[0, tf, int(specgram.size / tf), 0],
        )
    if invert:
        ax.invert_yaxis()
    fig = plt.gcf()
    if cb:
        fig.colorbar(im, ax=ax)
    # cbar.set_label('log scale', rotation=270)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    return None


def plot_decision_boundaries(
    X, y, model, ax=None, legend="", title="", s=20, N=40, cm="brg", edgc="k"
):
    """
    Plot decision boundaries of a classifier in 2D, and display true labels.
    The labels y must be numerical values.
    """
    if ax is None:
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_axes([0.0, 0.0, 0.9, 1.0])
    ax.set_aspect("equal", adjustable="box")
    # Plot the decision boundary.
    n = 80
    one_axis = np.linspace(np.min(X), np.max(X), n)
    grid = np.meshgrid(one_axis, one_axis)
    fv = np.array(grid).reshape(2, n**2).T

    ax.contourf(grid[0], grid[1], model.predict(fv).reshape(n, n), cmap=cm, alpha=0.5)
    scatterd = ax.scatter(X[:, 0], X[:, 1], c=y, cmap=cm, edgecolors=edgc, s=s)
    ax.set_title(title)
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    handles, labels = scatterd.legend_elements(prop="colors")
    ax.legend(handles, legend)
