import matplotlib.pyplot as plt
import numpy as np
from chain import Chain
from scipy.signal import firwin, freqz
from scipy.special import erfc
from tqdm import tqdm
import os
import argparse
from chain import BasicChain


def add_delay(chain: Chain, x: np.ndarray, tau: float):
    """
    Apply the channel between TX and RX, handling the different oversampling factors
    and the addition of a delay.
    """
    fs = chain.bit_rate * chain.osr_rx  # Receiver sampling frequency
    sto_int = np.floor(tau * fs).astype(int)  # Integer delay (on the received samples)
    sto_frac = tau * fs - sto_int  # Fractional delay, remaining

    R = int(chain.osr_tx / chain.osr_rx)
    idx = np.floor(
        sto_frac * R
    ).astype(
        int
    )  # Index of best sample (available in transmitted signal oversampled at TX) depicting the fractional delay

    y = np.concatenate(
        (np.zeros(sto_int), x[idx::R])
    )  # Received signal with 0's from integer delay and sampling starting at the fractional delay

    return y, np.mod(sto_int, chain.osr_rx)


def add_cfo(chain: Chain, x: np.ndarray, cfo: float):
    """
    Add a frequency offset on the signal x.
    """
    fs = chain.bit_rate * chain.osr_rx

    t = np.arange(len(x)) / fs  # Time vector
    y = np.exp(1j * 2 * np.pi * cfo * t) * x
    return y


def run_sim(chain: Chain, filename="sim"):
    """
    Main function, running the simulations of the communication chain provided, for several SNRs.
    Compute and display the different metrics to evaluate the performances.
    """
    SNRs_dB = chain.snr_range
    R = chain.osr_rx
    B = chain.bit_rate
    fs = B * R

    # Error counters/metric initialisation
    bit_errors = np.zeros(len(SNRs_dB))
    packet_errors = np.zeros(len(SNRs_dB))
    cfo_err = np.zeros(len(SNRs_dB))
    sto_err = np.zeros(len(SNRs_dB))
    preamble_misdetect = np.zeros(len(SNRs_dB))  # Preamble miss detection (not found)
    preamble_false_detect = np.zeros(
        len(SNRs_dB)
    )  # Preamble false detection (found in noise)
    SNR_est_matrix = np.zeros((len(SNRs_dB), chain.n_packets))

    # Transmitted signals that are independent of the payload bits
    x_pr = chain.modulate(chain.preamble)  # Modulated signal containing preamble
    x_sync = chain.modulate(chain.sync_word)  # Modulated signal containing sync_word
    x_noise = np.zeros(
        chain.payload_len * chain.osr_tx
    )  # Padding some zeros before the packets

    # Lowpass filter taps
    taps = firwin(chain.numtaps, chain.cutoff, fs=fs)

    rng = np.random.default_rng()

    # For loop on the number of packets to send
    for n in tqdm(range(chain.n_packets)):
        # Random generation of payload bits
        bits = rng.integers(2, size=chain.payload_len)

        # Transmitted signal
        x_pay = chain.modulate(bits)  # Modulated signal with payload
        x = np.concatenate((x_noise, x_pr, x_sync, x_pay, np.zeros(chain.osr_tx)))

        # Channel application (without noise addition): delay and frequency offset
        if np.isnan(chain.sto_val):  # STO should be random
            tau = rng.random() * chain.sto_range
        else:
            tau = chain.sto_val

        y, sto_idx = add_delay(chain, x, tau)  # Delay addition
        start_idx = (
            int(tau * chain.osr_rx * B) + chain.payload_len * chain.osr_rx
        )  # Delay + noise in beginning, for STO metric

        if np.isnan(chain.cfo_val):  # CFO should be random
            cfo = rng.uniform(low=-chain.cfo_range, high=chain.cfo_range)
        else:
            cfo = chain.cfo_val
        y_cfo = add_cfo(chain, y, cfo)  # Frequency offset addition

        # Normalized noise generation
        w = (rng.normal(size=y.size) + 1j * rng.normal(size=y.size)) / np.sqrt(
            2
        )  # Normalized complex normal vector CN(0, 1)

        # For loop on the SNRs
        for k, SNR_dB in enumerate(SNRs_dB):
            # Add noise
            SNR = 10 ** (SNR_dB / 10.0)
            y_noisy = y_cfo + w * np.sqrt(1 / SNR)

            # Low-pass filtering
            y_filt = np.convolve(y_noisy, taps, mode="same")

            # SNR estimation
            noise_power_est = np.mean(
                np.abs(y_filt[0 : chain.payload_len * chain.osr_rx]) ** 2
            )
            signal_energy_est = (
                np.mean(np.abs(y_filt[-chain.payload_len * chain.osr_rx :]) ** 2)
                - noise_power_est
            )
            SNR_est = signal_energy_est / noise_power_est

            SNR_est_matrix[k, n] = SNR_est

            ## Preamble detection stage
            if chain.bypass_preamble_detect:
                detect_idx = start_idx
            else:
                detect_idx = chain.preamble_detect(y_filt)

            preamble_error = False
            if detect_idx is None:  # Misdetection of preamble
                preamble_misdetect[k] += 1
                errors = 0.5 * np.ones(len(bits))
                cfo_hat, tau_hat, detect_idx, start_frame = (
                    np.nan,
                    np.nan,
                    np.nan,
                    np.nan,
                )

            else:  # Found a preamble, can demodulate packet
                # Preamble metrics
                if (
                    detect_idx < start_idx - 4 * R
                ):  # False detection of preamble (found in noise)
                    preamble_false_detect[k] += 1
                    preamble_error = True
                elif (
                    detect_idx > start_idx + len(chain.preamble) * chain.osr_rx
                ):  # Misdetection of preamble (found in packet)
                    preamble_misdetect[k] += 1
                    preamble_error = True

                y_detect = y_filt[detect_idx:]

                ## Synchronization stage
                # CFO estimation and correction
                if chain.bypass_cfo_estimation:
                    cfo_hat = cfo
                else:
                    cfo_hat = chain.cfo_estimation(y_detect)

                t = np.arange(len(y_detect)) / (B * R)
                y_sync = np.exp(-1j * 2 * np.pi * cfo_hat * t) * y_detect

                # STO estimation and correction
                if chain.bypass_sto_estimation:
                    if (
                        chain.bypass_preamble_detect
                    ):  # In this case, starting index of preamble already contains sto
                        tau_hat = 0
                    else:
                        tau_hat = sto_idx
                else:
                    tau_hat = chain.sto_estimation(y_sync)

                y_sync = y_sync[tau_hat:]

                ## Demodulation and deframing stage
                bits_hat = chain.demodulate(y_sync)

                if (
                    chain.bypass_sto_estimation and chain.bypass_preamble_detect
                ):  # In this case, also assume perfect frame syncrhonization
                    start_frame = len(chain.preamble) + len(chain.sync_word)
                elif len(bits_hat) == 0:
                    preamble_error = True
                else:  # Frame synchronization
                    v = np.abs(
                        np.correlate(
                            bits_hat * 2 - 1,
                            np.array(chain.sync_word) * 2 - 1,
                            mode="full",
                        )
                    )
                    start_frame = np.argmax(v) + 1

                bits_hat_pay = bits_hat[
                    start_frame : start_frame + chain.payload_len
                ]  # Demodulated payload bits

                ## Computing performance metrics
                if len(bits) == len(bits_hat_pay) and not preamble_error:
                    errors = bits ^ bits_hat_pay

                else:  # if the number of demodulated symbols is incorrect
                    errors = 0.5 * np.ones(len(bits))  # flag all bits as wrong
            # end if preamble

            bit_errors[k] += np.sum(errors)
            packet_errors[k] += 1 if any(errors) else 0
            cfo_err[k] += (cfo - cfo_hat) ** 2
            sto_err[k] += (
                (
                    start_idx
                    + len(chain.preamble) * chain.osr_rx
                    + len(chain.sync_word) * chain.osr_rx
                )
                / (R * B)
                - (detect_idx + tau_hat + start_frame * chain.osr_rx) / (R * B)
            ) ** 2
    
    Cu = np.correlate(taps, taps, mode="full")  # such that Cu[len(taps)-1] = 1
    sum_Cu = 0
    for r in range(0, R):
        for rt in range(0, R):
            sum_Cu += Cu[len(taps) - 1 + r - rt]
    shift_SNR_out = 10 * np.log10(R**2 / sum_Cu)  # 10*np.log10(chain.osr_rx)
    
    # Metrics
    BER = bit_errors / chain.payload_len / chain.n_packets
    PER = packet_errors / chain.n_packets
    RMSE_cfo = np.sqrt(cfo_err / chain.n_packets) / B
    RMSE_sto = np.sqrt(sto_err / chain.n_packets) * B
    preamble_mis = preamble_misdetect / chain.n_packets
    preamble_false = preamble_false_detect / chain.n_packets
    
    # Save simulation outputs (for later post-processing, building new figures,...)
    save_var = np.column_stack(
        (
            SNRs_dB,
            SNRs_dB + shift_SNR_out,
            BER,
            PER,
            RMSE_cfo,
            RMSE_sto,
            preamble_mis,
            preamble_false,
            SNR_est_matrix
        )
    )
    
    if not os.path.exists("data"):
        os.makedirs("data")
    
    np.savetxt(f"data/{filename}.csv", save_var, delimiter=",", comments='',\
    header=f"SNR_o [dB],SNR_e [dB],BER,PER,RMSE cfo,RMSE sto,preamble miss rate,preamble false rate,SNR estimation matrix ({chain.n_packets} columns)")

def plot_FIR(chain: Chain, **plot_kwargs):
    
    R = chain.osr_rx
    B = chain.bit_rate
    fs = B * R
    
    # Lowpass filter taps
    taps = firwin(chain.numtaps, chain.cutoff, fs=fs)
    
    # Plot dashboard
    fig, ax1 = plt.subplots(**plot_kwargs)
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
    shift_SNR_out = 10 * np.log10(R**2 / sum_Cu)  # 10*np.log10(chain.osr_rx)
    shift_SNR_filter = 10 * np.log10(1 / np.sum(np.abs(taps) ** 2))

    SNR_th = np.arange(SNRs_dB[0], SNRs_dB[-1] + shift_SNR_out)
    BER_th = 0.5 * erfc(np.sqrt(10 ** (SNR_th / 10.0) / 2))
    BER_th_BPSK = 0.5 * erfc(np.sqrt(10 ** (SNR_th / 10.0)))
    BER_th_noncoh = 0.5 * np.exp(-(10 ** (SNR_th / 10.0)) / 2)


    # Bit error rate
    fig1, ax = plt.subplots(**plot_kwargs)
    ax.plot(SNRs_dB + shift_SNR_out, BER, "-s", label="Simulation")
    ax.plot(SNR_th, BER_th, label="AWGN Th. FSK")
    ax.plot(SNR_th, BER_th_noncoh, label="AWGN Th. FSK non-coh.")
    ax.plot(SNR_th, BER_th_BPSK, label="AWGN Th. BPSK")
    ax.set_ylabel("BER")
    ax.set_xlabel("SNR$_{o}$ [dB]")
    ax.set_yscale("log")
    ax.set_ylim((1e-6, 1))
    ax.set_xlim((0, chain.snr_range[len(chain.snr_range)-1]))
    ax.grid(True)
    ax.set_title("Average Bit Error Rate")
    ax.legend()

    # add second axis
    bool_2_axis = True
    if bool_2_axis:
        ax2 = ax.twiny()
        # ax2.set_xticks(SNRs_dB + shift_SNR_out)
        ax2.set_xticks(SNRs_dB - shift_SNR_filter + shift_SNR_out)
        ax2.set_xticklabels(SNRs_dB)
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        ax2.spines["bottom"].set_position(("outward", 36))
        # ax2.set_xlabel('SNR [dB]')
        ax2.set_xlabel(r"$SNR_e$ [dB]")
        ax2.set_xlim(ax.get_xlim())
        ax2.xaxis.label.set_color("b")
        ax2.tick_params(axis="x", colors="b")

    # Packet error rate
    fig2, ax = plt.subplots(**plot_kwargs)
    ax.plot(SNRs_dB + shift_SNR_out, PER, "-s", label="Simulation")
    ax.plot(SNR_th, 1 - (1 - BER_th) ** chain.payload_len, label="AWGN Th. FSK")
    ax.plot(
        SNR_th,
        1 - (1 - BER_th_noncoh) ** chain.payload_len,
        label="AWGN Th. FSK non-coh.",
    )
    ax.plot(SNR_th, 1 - (1 - BER_th_BPSK) ** chain.payload_len, label="AWGN Th. BPSK")
    ax.set_ylabel("PER")
    ax.set_xlabel("SNR$_{o}$ [dB]")
    ax.set_yscale("log")
    ax.set_ylim((1e-6, 1))
    ax.set_xlim((0, chain.snr_range[len(chain.snr_range)-1]))
    ax.grid(True)
    ax.set_title("Average Packet Error Rate")
    ax.legend()

    # add second axis
    bool_2_axis = True
    if bool_2_axis:
        ax2 = ax.twiny()
        # ax2.set_xticks(SNRs_dB + shift_SNR_out)
        ax2.set_xticks(SNRs_dB - shift_SNR_filter + shift_SNR_out)
        ax2.set_xticklabels(SNRs_dB)
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        ax2.spines["bottom"].set_position(("outward", 36))
        # ax2.set_xlabel('SNR [dB]')
        ax2.set_xlabel(r"$SNR_e$ [dB]")
        ax2.set_xlim(ax.get_xlim())
        ax2.xaxis.label.set_color("b")
        ax2.tick_params(axis="x", colors="b")
    
    return (fig1, fig2)

def plot_preamble_metrics(SNRs_dB: np.ndarray, preamble_mis: np.ndarray, preamble_false: np.ndarray, **plot_kwargs):
    
    fig = plt.figure(**plot_kwargs)
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
    plt.semilogy(SNRs_dB, RMSE_cfo, "-s")
    plt.title("RMSE CFO")
    plt.ylabel("RMSE [-]")
    plt.xlabel("SNR [dB]")
    plt.grid()
    
    return fig

def plot_RMSE_sto(SNRs_dB: np.ndarray, RMSE_sto: np.ndarray, **plot_kwargs):
    
    fig = plt.figure(**plot_kwargs)
    plt.semilogy(SNRs_dB, RMSE_sto, "-s")
    plt.title("RMSE STO")
    plt.ylabel("RMSE [-]")
    plt.xlabel("SNR [dB]")
    plt.grid()
    
    return fig

def plot_SNR_est(SNRs_dB: np.ndarray, SNR_est_matrix: np.ndarray, **plot_kwargs):
    
    SNR_est_dB = 10*np.log10(np.abs(SNR_est_matrix.T))
    
    fig = plt.figure(**plot_kwargs)
    plt.boxplot(SNR_est_dB, showfliers=False)
    plt.plot(np.arange(len(SNRs_dB))+1, SNRs_dB, color="lightblue")
    plt.xticks((np.arange(len(SNRs_dB))+1)[::5], labels=SNRs_dB[::5])
    plt.title("Boxplot SNR estimations")
    plt.ylabel("SNR estimation [dB]")
    plt.xlabel("SNR [dB]")
    plt.grid()
    
    return fig

def plot_graphs(chain: Chain, FIR=False, save=True, show=True, **kwargs):
    
    plot_kwargs = dict(figsize=(8,6), dpi=300, layout="constrained")
    
    # Read file:
    try:
        filename = kwargs['filename']
        data = np.loadtxt(f"data/{filename}.csv", delimiter=",", skiprows=1)
    except:
        raise FileNotFoundError(f"No such data file found: data/{kwargs['filename']}.csv\nPlease call the function with filename=valid_filename")
        
    SNRs_dB = data[:,0].astype(int)
    _ = data[:,1]
    BER = data[:,2]
    PER = data[:,3]
    RMSE_cfo = data[:,4]
    RMSE_sto = data[:,5]
    preamble_mis = data[:,6]
    preamble_false = data[:,7]
    SNR_est_matrix = data[:,8:8+chain.n_packets]
    
    if not os.path.exists(f"graphs/{filename}"):
        os.makedirs(f"graphs/{filename}")
    
    if FIR:
        FIR_fig = plot_FIR(chain, **plot_kwargs)
    BER_fig, PER_fig = plot_BER_PER(chain, SNRs_dB, BER, PER, **plot_kwargs)
    if not chain.bypass_preamble_detect:
        preamble_metrics_fig = plot_preamble_metrics(SNRs_dB, preamble_mis, preamble_false, **plot_kwargs)
    if not chain.bypass_cfo_estimation:
        RMSE_cfo_fig = plot_RMSE_cfo(SNRs_dB, RMSE_cfo, **plot_kwargs)
    if not chain.bypass_sto_estimation:
        RMSE_sto_fig = plot_RMSE_sto(SNRs_dB, RMSE_sto, **plot_kwargs)
    SNR_est_fig = plot_SNR_est(SNRs_dB, SNR_est_matrix, **plot_kwargs)
        
    if save:
        if FIR:
            R = chain.osr_rx
            B = chain.bit_rate
            fs = B * R
            FIR_fig.savefig(f"graphs/FIR_response_numtaps_{chain.numtaps}_cutoff_{chain.cutoff:.0f}_fs_{fs:.0f}.png")
        BER_fig.savefig(f"graphs/{filename}/BER.png")
        PER_fig.savefig(f"graphs/{filename}/PER.png")
        if not chain.bypass_preamble_detect:
            preamble_metrics_fig.savefig(f"graphs/{filename}/preamble_metrics.png")
        if not chain.bypass_cfo_estimation:
            RMSE_cfo_fig.savefig(f"graphs/{filename}/RMSE_cfo.png")
        if not chain.bypass_sto_estimation:
            RMSE_sto_fig.savefig(f"graphs/{filename}/RMSE_sto.png")
        SNR_est_fig.savefig(f"graphs/{filename}/SNR_est.png")
    
    if show:
        plt.show()

def parse_args(arg_list: list[str] = None):
    
    parser = argparse.ArgumentParser(usage="run python sim.py [OPTIONAL_ARGUMENTS] [OPTIONAL_BYPASSES]")
    parser.add_argument("-f", "--force_simulation", action="store_true", help="if set, force simulation and replace any existing datafile corresponding to simulation parameters")
    parser.add_argument("--no_show", "--dont_show_graphs", action="store_true", help="if set, don't show matplotlib graphs")
    parser.add_argument("--no_save", "--dont_save_graphs", action="store_true", help="if set, don't save matplotlib graphs")
    parser.add_argument("--FIR", action="store_true", default=False, help="if set, generates the FIR graph of chain")
    parser.add_argument("-p", "--payload_len", type=int, default=50, help="payload length of chain - default to 50")
    parser.add_argument("-n", "--n_packets", type=int, default=100, help="number of packets of chain - default to 100")
    parser.add_argument("-m", "--cfo_Moose_N", type=int, default=4, help="N parameter in Moose algorithm - max value is #bits in preamble / 2 - default to 4")
    parser.add_argument("-r", "--cfo_range", type=int, default=1e3, help="CFO range- max value should be Bitrate / (2 * cfo_Moose_N) - default to 1e3")
    parser.add_argument("-d", "--bypass_preamble_detect", action="store_true", help="if set, bypass preamble detection")
    parser.add_argument("-c", "--bypass_cfo_estimation", action="store_true", help="if set, bypass CFO estimation")
    parser.add_argument("-s", "--bypass_sto_estimation", action="store_true", help="if set, bypass STO estimation")
    
    
    args = parser.parse_args(arg_list)
    return args

def main(arg_list: list[str] = None):
    
    args = parse_args(arg_list)
    
    # Change the chain parameters here, for example:
    # args.bypass_preamble_detect = True
    # args.bypass_cfo_estimation = True
    # args.bypass_sto_estimation = True
    # args.payload_len = 100
    # args.n_packets = 100_000
    # args.cfo_Moose_N = 16
    # args.cfo_range = 10_000
    
    # Change the simulation parameters here, for example:
    # args.force_simulation = True
    # args.FIR = True
    # args.no_show = True
    # args.no_save = True
    
    chain = BasicChain(**vars(args))
    
    filename = f"sim_p_{chain.payload_len}_n_{chain.n_packets}_" + \
            f"pre_det_{'OFF' if chain.bypass_preamble_detect else 'ON'}_" + \
            f"cfo_est_{'OFF' if chain.bypass_cfo_estimation else f'ON(N={chain.cfo_Moose_N},range={chain.cfo_range:.0f})'}_" + \
            f"sto_est_{'OFF' if chain.bypass_sto_estimation else 'ON'}"
    
    if (not os.path.isfile(f"data/{filename}.csv")) or args.force_simulation:
        run_sim(chain, filename=filename)
    if (not args.no_show) or (not args.no_save):
        plot_graphs(chain, filename=filename, show=not args.no_show, save=not args.no_save, FIR=args.FIR)

if __name__ == "__main__":
    main()    
