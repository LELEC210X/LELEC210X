import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.signal import firwin, freqz
from scipy.special import erfc
from telecom.hands_on_simulation.chain import Chain


shift_SNR_out: float
shift_SNR_filter: float
SNRs_dB: np.ndarray[float]
BER: np.ndarray[float]
PER: np.ndarray[float]
preamble_mis: np.ndarray[float]
preamble_false: np.ndarray[float]
RMSE_cfo: np.ndarray[float]
RMSE_sto: np.ndarray[float]


def get_SNRs_est():
    global SNRs_dB, shift_SNR_out, shift_SNR_filter
    return SNRs_dB + shift_SNR_out - shift_SNR_filter


def get_BER():
    global BER
    return BER


def get_PER():
    global PER
    return PER


def get_preamble_mis():
    global preamble_mis
    return preamble_mis


def get_preamble_false():
    global preamble_false
    return preamble_false


def get_RMSE_cfo():
    global RMSE_cfo
    return RMSE_cfo


def get_RMSE_sto():
    global RMSE_sto
    return RMSE_sto


def plot_FIR(chain: Chain, **plot_kwargs):

    R = chain.osr_rx
    B = chain.bit_rate
    fs = B * R

    # Lowpass filter taps
    taps = firwin(chain.numtaps, chain.cutoff, fs=fs)

    # Plot dashboard
    fig, ax1 = plt.subplots(**plot_kwargs)
    fig.canvas.manager.set_window_title("Simulation: FIR response")
    w, h = freqz(taps)
    f = w * fs * 0.5 / np.pi
    ax1.set_title("FIR response")
    ax1.plot(f, 20 * np.log10(abs(h)), "b")
    ax1.set_ylabel("Amplitude (dB)", color="b")
    ax1.set_xlabel("Frequency (Hz)")
    ax2 = ax1.twinx()
    angles = np.unwrap(np.angle(h))
    ax2.plot(f, angles, "g")
    ax2.set_ylabel("Angle (radians)", color="g")
    ax2.grid(True)
    ax2.axis("tight")

    return fig


def plot_BER_PER(chain: Chain, SNRs_dB: np.ndarray, BER: np.ndarray, PER: np.ndarray, **plot_kwargs):

    R = chain.osr_rx
    B = chain.bit_rate
    fs = B * R

    # Lowpass filter taps
    taps = firwin(chain.numtaps, chain.cutoff, fs=fs)

    # Theoretical curves - normalization
    Cu = np.correlate(taps, taps, mode="full")  # such that Cu[len(taps)-1] = 1
    sum_Cu = 0
    for r in range(0, R):
        for rt in range(0, R):
            sum_Cu += Cu[len(taps) - 1 + r - rt]
    global shift_SNR_out
    global shift_SNR_filter
    shift_SNR_out = 10 * np.log10(R**2 / sum_Cu)  # 10*np.log10(chain.osr_rx)
    shift_SNR_filter = 10 * np.log10(1 / np.sum(np.abs(taps) ** 2))

    SNR_th = np.arange(SNRs_dB[0], SNRs_dB[-1] + shift_SNR_out)
    BER_th = 0.5 * erfc(np.sqrt(10 ** (SNR_th / 10.0) / 2))
    BER_th_BPSK = 0.5 * erfc(np.sqrt(10 ** (SNR_th / 10.0)))
    BER_th_noncoh = 0.5 * np.exp(-(10 ** (SNR_th / 10.0)) / 2)

    # Bit error rate
    fig1, ax1 = plt.subplots(**plot_kwargs)
    fig1.canvas.manager.set_window_title("Simulation: BER")
    ax1.plot(SNRs_dB + shift_SNR_out, BER, "-s", label="Simulation")
    ax1.plot(SNR_th, BER_th, label="AWGN Th. FSK")
    ax1.plot(SNR_th, BER_th_noncoh, label="AWGN Th. FSK non-coh.")
    ax1.plot(SNR_th, BER_th_BPSK, label="AWGN Th. BPSK")
    ax1.set_ylabel("BER")
    ax1.set_xlabel("SNR$_{o}$ [dB]")
    ax1.set_yscale("log")
    ax1.set_ylim((1e-6, 1))
    ax1.set_xlim((0, chain.snr_range[len(chain.snr_range)-1]))
    ax1.grid(True)
    ax1.set_title("Average Bit Error Rate")
    ax1.legend()

    # add second axis
    bool_2_axis = True
    if bool_2_axis:
        ax2 = ax1.twiny()
        # ax2.set_xticks(SNRs_dB + shift_SNR_out)
        ax2.set_xticks(SNRs_dB - shift_SNR_filter + shift_SNR_out)
        ax2.set_xticklabels(
            (SNRs_dB - shift_SNR_filter + shift_SNR_out).astype(int))
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        ax2.spines["bottom"].set_position(("outward", 36))
        # ax2.set_xlabel('SNR [dB]')
        ax2.set_xlabel(r"$SNR_e$ [dB]")
        ax2.set_xlim(ax1.get_xlim())
        ax2.xaxis.label.set_color("b")
        ax2.tick_params(axis="x", colors="b")

    # Packet error rate
    fig2, ax3 = plt.subplots(**plot_kwargs)
    fig2.canvas.manager.set_window_title("Simulation: PER")
    ax3.plot(SNRs_dB + shift_SNR_out, PER, "-s", label="Simulation")
    ax3.plot(SNR_th, 1 - (1 - BER_th) **
             chain.payload_len, label="AWGN Th. FSK")
    ax3.plot(
        SNR_th,
        1 - (1 - BER_th_noncoh) ** chain.payload_len,
        label="AWGN Th. FSK non-coh.",
    )
    ax3.plot(SNR_th, 1 - (1 - BER_th_BPSK) **
             chain.payload_len, label="AWGN Th. BPSK")
    ax3.set_ylabel("PER")
    ax3.set_xlabel("SNR$_{o}$ [dB]")
    ax3.set_yscale("log")
    ax3.set_ylim((1e-6, 1))
    ax3.set_xlim((0, chain.snr_range[len(chain.snr_range)-1]))
    ax3.grid(True)
    ax3.set_title("Average Packet Error Rate")
    ax3.legend()

    # add second axis
    bool_2_axis = True
    if bool_2_axis:
        ax4 = ax3.twiny()
        # ax4.set_xticks(SNRs_dB + shift_SNR_out)
        ax4.set_xticks(SNRs_dB - shift_SNR_filter + shift_SNR_out)
        ax4.set_xticklabels(
            (SNRs_dB - shift_SNR_filter + shift_SNR_out).astype(int))
        ax4.xaxis.set_ticks_position("bottom")
        ax4.xaxis.set_label_position("bottom")
        ax4.spines["bottom"].set_position(("outward", 36))
        # ax4.set_xlabel('SNR [dB]')
        ax4.set_xlabel(r"$SNR_e$ [dB]")
        ax4.set_xlim(ax3.get_xlim())
        ax4.xaxis.label.set_color("b")
        ax4.tick_params(axis="x", colors="b")

    return (fig1, fig2, ax1, ax2, ax3, ax4)


def plot_preamble_metrics(SNRs_dB: np.ndarray, preamble_mis: np.ndarray, preamble_false: np.ndarray, **plot_kwargs):

    fig = plt.figure(**plot_kwargs)
    fig.canvas.manager.set_window_title("Simulation: Preamble Metrics")
    plt.plot(SNRs_dB, preamble_mis * 100, "-s", label="Miss-detection")
    plt.plot(SNRs_dB, preamble_false * 100, "-s", label="False-detection")
    plt.title("Preamble detection error ")
    plt.ylabel("[%]")
    plt.xlabel("SNR [dB]")
    plt.ylim([-1, 101])
    plt.grid()
    plt.legend()

    return fig


def plot_RMSE_cfo(SNRs_dB: np.ndarray, RMSE_cfo: np.ndarray, **plot_kwargs):

    fig = plt.figure(**plot_kwargs)
    fig.canvas.manager.set_window_title("Simulation: RMSE cfo")
    plt.semilogy(SNRs_dB, RMSE_cfo, "-s")
    plt.title("RMSE CFO")
    plt.ylabel("RMSE [-]")
    plt.xlabel("SNR [dB]")
    plt.grid()

    return fig


def plot_RMSE_sto(SNRs_dB: np.ndarray, RMSE_sto: np.ndarray, **plot_kwargs):

    fig = plt.figure(**plot_kwargs)
    fig.canvas.manager.set_window_title("Simulation: RMSE STO")
    plt.semilogy(SNRs_dB, RMSE_sto, "-s")
    plt.title("RMSE STO")
    plt.ylabel("RMSE [-]")
    plt.xlabel("SNR [dB]")
    plt.grid()

    return fig


def plot_SNR_est(SNRs_dB: np.ndarray, SNR_est_matrix: np.ndarray, **plot_kwargs):

    SNR_est_dB = 10*np.log10(np.abs(SNR_est_matrix.T))
    fig = plt.figure(**plot_kwargs)
    fig.canvas.manager.set_window_title("Simulation: SNR estimation")
    plt.boxplot(SNR_est_dB, showfliers=False, positions=SNRs_dB)
    plt.plot(SNRs_dB, SNRs_dB, color="lightblue")
    plt.xticks(SNRs_dB[::5], labels=SNRs_dB[::5])
    fig.suptitle("Boxplot SNR estimations")
    plt.title('Simulation')
    plt.ylabel("SNR estimation [dB]")
    plt.xlabel("$SNR_e$ [dB]")
    plt.grid()

    return fig


def plot_graphs(chain: Chain, FIR=False, SNR_est=True, sim_id=None, save=True, show=True, **kwargs):

    # Read file:
    try:
        data = np.loadtxt(os.path.dirname(__file__)+f"/data/{sim_id}.csv", delimiter=",", skiprows=1)
    except:
        raise FileNotFoundError(
            f"No such data file found: data/{sim_id}.csv\n"
                "Please call the function with sim_id=valid_sim_id")

    global SNRs_dB
    global BER
    global PER
    global preamble_mis
    global preamble_false
    global RMSE_cfo
    global RMSE_sto
    SNRs_dB = data[:, 0]
    _ = data[:, 1]
    BER = data[:, 2]
    PER = data[:, 3]
    RMSE_cfo = data[:, 4]
    RMSE_sto = data[:, 5]
    preamble_mis = data[:, 6]
    preamble_false = data[:, 7]
    SNR_est_matrix = data[:, 8:8+chain.n_packets]

    if SNR_est:
        SNR_est = SNR_est_matrix.size != 0

    plot_kwargs = dict(figsize=(8, 6), layout="constrained")

    if FIR:
        FIR_fig = plot_FIR(chain, **plot_kwargs)
    BER_fig, PER_fig, _, _, _, _ = plot_BER_PER(
        chain, SNRs_dB, BER, PER, **plot_kwargs)
    if not chain.bypass_preamble_detect:
        preamble_metrics_fig = plot_preamble_metrics(
            SNRs_dB, preamble_mis, preamble_false, **plot_kwargs)
    if not chain.bypass_cfo_estimation:
        RMSE_cfo_fig = plot_RMSE_cfo(SNRs_dB, RMSE_cfo, **plot_kwargs)
    if not chain.bypass_sto_estimation:
        RMSE_sto_fig = plot_RMSE_sto(SNRs_dB, RMSE_sto, **plot_kwargs)
    if SNR_est:
        SNR_est_fig = plot_SNR_est(SNRs_dB, SNR_est_matrix, **plot_kwargs)

    if save:
        curdir = os.path.dirname(__file__)
        if not os.path.exists(curdir+f"/graphs/{sim_id}"):
            os.makedirs(curdir+f"/graphs/{sim_id}")
        if FIR:
            R = chain.osr_rx
            B = chain.bit_rate
            fs = B * R
            FIR_fig.savefig(curdir+
                f"/graphs/FIR_response_numtaps_{chain.numtaps}_cutoff_"
                f"{chain.cutoff:.0f}_fs_{fs:.0f}.pdf", dpi=300)
        BER_fig.savefig(curdir+f"/graphs/{sim_id}/BER.pdf", dpi=300)
        PER_fig.savefig(curdir+f"/graphs/{sim_id}/PER.pdf", dpi=300)
        if not chain.bypass_preamble_detect:
            preamble_metrics_fig.savefig(curdir+
                f"/graphs/{sim_id}/preamble_metrics.pdf", dpi=300)
        if not chain.bypass_cfo_estimation:
            RMSE_cfo_fig.savefig(curdir+f"/graphs/{sim_id}/RMSE_cfo.pdf", dpi=300)
        if not chain.bypass_sto_estimation:
            RMSE_sto_fig.savefig(curdir+f"/graphs/{sim_id}/RMSE_sto.pdf", dpi=300)
        if SNR_est:
            SNR_est_fig.savefig(curdir+f"/graphs/{sim_id}/SNR_est.pdf", dpi=300)

    if show:
        plt.show()
