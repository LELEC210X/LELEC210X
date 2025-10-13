# ruff: noqa: N806
import click
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import firwin, freqz
from scipy.special import erfc

from .chain import Chain


def add_delay(chain: Chain, x: np.ndarray, tau: float) -> tuple[np.ndarray, int]:
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


def add_cfo(chain: Chain, x: np.ndarray, cfo: float) -> np.ndarray:
    """Add a frequency offset on the signal x."""
    fs = chain.bit_rate * chain.osr_rx

    t = np.arange(len(x)) / fs  # Time vector
    y = np.exp(1j * 2 * np.pi * cfo * t) * x
    return y


@click.command()
@click.option(
    "-c",
    "--chain-name",
    default="telecom.chain.BasicChain",
    show_default=True,
    help="Chain to simulate, in the form 'module.ClassName'.",
)
@click.option(
    "-s",
    "--seed",
    default=1234,
    show_default=True,
    help="Random seed. Same seed => same results.",
)
def main(chain_name: str, seed: int):  # noqa: C901
    """
    Simulate the communication chain provided, for several SNRs.
    Compute and display the different metrics to evaluate the performances.
    """
    mod_path, class_name = chain_name.rsplit(".", 1)
    chain_mod = __import__(mod_path, fromlist=[class_name])
    chain: Chain = getattr(chain_mod, class_name)()
    EsN0s_dB = chain.EsN0_range

    R = chain.osr_rx
    B = chain.bit_rate
    fs = B * R

    # Error counters/metric initialisation
    snr_est = np.zeros((len(EsN0s_dB), 2))
    bit_errors = np.zeros(len(EsN0s_dB))
    packet_errors = np.zeros(len(EsN0s_dB))
    cfo_err = np.zeros(len(EsN0s_dB))
    sto_err = np.zeros(len(EsN0s_dB))
    preamble_misdetect = np.zeros(len(EsN0s_dB))  # Preamble miss detection (not found)
    preamble_false_detect = np.zeros(
        len(EsN0s_dB)
    )  # Preamble false detection (found in noise)

    # Transmitted signals that are independent of the payload bits
    x_pr = chain.modulate(chain.preamble)  # Modulated signal containing preamble
    x_sync = chain.modulate(chain.sync_word)  # Modulated signal containing sync_word
    x_noise = np.zeros(
        chain.payload_len * chain.osr_tx
    )  # Padding some zeros before the packets

    # Lowpass filter taps
    if chain.numtaps != 0:
        taps = firwin(chain.numtaps, chain.cutoff, fs=fs)

    rng = np.random.default_rng(seed)

    # For loop on the number of packets to send
    for n in range(chain.n_packets):
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
            cfo = rng.uniform(low=chain.cfo_range[0], high=chain.cfo_range[1])
        else:
            cfo = chain.cfo_val
        y_cfo = add_cfo(chain, y, cfo)  # Frequency offset addition

        # Normalized noise generation
        w = (rng.normal(size=y.size) + 1j * rng.normal(size=y.size)) / np.sqrt(
            2
        )  # Normalized complex normal vector CN(0, 1)

        # For loop on the SNRs
        for k, EsN0_dB in enumerate(EsN0s_dB):
            # Add noise
            EsN0 = 10 ** (EsN0_dB / 10.0)
            noise = w * np.sqrt(chain.osr_rx / EsN0)
            y_noisy = y_cfo + noise

            # Low-pass filtering
            if chain.numtaps != 0:
                y_filt = np.convolve(y_noisy, taps, mode="same")
            else:
                y_filt = y_noisy

            ## Preamble detection stage
            if chain.ideal_preamble_detect:
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

                snr_est[k, 0] += (
                    np.var(
                        y_noisy[
                            chain.payload_len * chain.osr_rx + chain.osr_tx : -(
                                2 * chain.osr_tx
                            )
                        ]
                    )
                    - np.var(noise)
                ) / np.var(noise)
                snr_est[k, 1] += 1

                y_detect = y_filt[detect_idx:]
                ## Synchronization stage
                # CFO estimation and correction
                if chain.ideal_cfo_estimation:
                    cfo_hat = cfo
                else:
                    cfo_hat = chain.cfo_estimation(y_detect)

                t = np.arange(len(y_detect)) / (B * R)
                y_sync = np.exp(-1j * 2 * np.pi * cfo_hat * t) * y_detect

                # STO estimation and correction
                if chain.ideal_sto_estimation:
                    if (
                        chain.ideal_preamble_detect
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
                    chain.ideal_sto_estimation and chain.ideal_preamble_detect
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

    # Metrics
    BER = bit_errors / chain.payload_len / chain.n_packets
    PER = packet_errors / chain.n_packets
    RMSE_cfo = np.sqrt(cfo_err / chain.n_packets) / B
    RMSE_sto = np.sqrt(sto_err / chain.n_packets) * B
    preamble_mis = preamble_misdetect / chain.n_packets
    preamble_false = preamble_false_detect / chain.n_packets

    # Theoretical curves - normalization

    if chain.numtaps != 0:
        Cu = np.correlate(taps, taps, mode="full")  # such that Cu[len(taps)-1] = 1
        sum_Cu = 0
        for r in range(0, R):
            for rt in range(0, R):
                sum_Cu += Cu[len(taps) - 1 + r - rt]
        shift_SNR_out = 10 * np.log10(R**2 / sum_Cu)
        # Filter correlation
        _fig, ax = plt.subplots(1, 2, constrained_layout=True, figsize=(10, 4))
        ax[0].plot(np.arange(len(Cu)), Cu)
        ax[0].plot(np.arange(len(Cu)), np.abs(Cu))
        ax[0].grid(True)
        ax[0].set_title("Correlation")
        # Filter transfer function
        w, h = freqz(taps)
        f = w * fs * 0.5 / np.pi
        ax[1].set_title("FIR response")
        ax[1].plot(f, 20 * np.log10(abs(h)), "b")
        ax[1].set_ylabel("Amplitude (dB)", color="b")
        ax[1].set_xlabel("Frequency (Hz)")
        ax2 = ax[1].twinx()
        angles = np.unwrap(np.angle(h))
        ax2.plot(f, angles, "g")
        ax2.set_ylabel("Angle (radians)", color="g")
        ax2.grid(True)
        ax2.axis("tight")
    else:
        shift_SNR_out = 10 * np.log10(chain.osr_rx)

    EsN0_th = np.arange(EsN0s_dB[0], EsN0s_dB[-1])
    SNR_th = EsN0_th - 10 * np.log10(chain.osr_rx) + shift_SNR_out

    BER_th = 0.5 * erfc(np.sqrt(10 ** (SNR_th / 10.0) / 2))
    BER_th_BPSK = 0.5 * erfc(np.sqrt(10 ** (SNR_th / 10.0)))
    BER_th_noncoh = 0.5 * np.exp(-(10 ** (SNR_th / 10.0)) / 2)

    _fig, ax = plt.subplots(1, 2, constrained_layout=True, figsize=(10, 4))
    ax[0].plot(EsN0s_dB, BER, "-s", label="Simulation")
    ax[0].plot(EsN0_th, BER_th, label="AWGN Th. FSK")
    ax[0].plot(EsN0_th, BER_th_noncoh, label="AWGN Th. FSK non-coh.")
    ax[0].plot(EsN0_th, BER_th_BPSK, label="AWGN Th. BPSK")
    ax[0].set_ylabel("BER")
    ax[0].set_xlabel("$E_{s}/N_{0}$ [dB]")
    ax[0].set_yscale("log")
    ax[0].set_ylim((1e-6, 1))
    ax[0].set_xlim((EsN0s_dB[0], EsN0s_dB[-1]))
    ax[0].grid(True)
    ax[0].set_title("Average Bit Error Rate")
    ax[0].legend()
    # Packet error rate
    ax[1].plot(EsN0s_dB, PER, "-s", label="Simulation")
    ax[1].plot(EsN0_th, 1 - (1 - BER_th) ** chain.payload_len, label="AWGN Th. FSK")
    ax[1].plot(
        SNR_th,
        1 - (1 - BER_th_noncoh) ** chain.payload_len,
        label="AWGN Th. FSK non-coh.",
    )
    ax[1].plot(
        SNR_th, 1 - (1 - BER_th_BPSK) ** chain.payload_len, label="AWGN Th. BPSK"
    )
    ax[1].set_ylabel("PER")
    ax[1].set_xlabel("$E_{s}/N_{0}$ [dB]")
    ax[1].set_yscale("log")
    ax[1].set_ylim((1e-6, 1))
    ax[1].set_xlim((EsN0s_dB[0], EsN0s_dB[-1]))
    ax[1].grid(True)
    ax[1].set_title("Average Packet Error Rate")
    ax[1].legend()

    # Preamble metrics
    _fig, ax = plt.subplots(1, 3, constrained_layout=True, figsize=(10, 4))
    ax[0].plot(EsN0s_dB, preamble_mis * 100, "-s", label="Miss-detection")
    ax[0].plot(EsN0s_dB, preamble_false * 100, "-s", label="False-detection")
    ax[0].set_title("Preamble detection error ")
    ax[0].set_ylabel("[%]")
    ax[0].set_xlabel("$E_{s}/N_{0}$ [dB]")
    ax[0].set_ylim([-1, 101])
    ax[0].grid()
    ax[0].legend()
    # RMSE CFO
    ax[1].semilogy(EsN0s_dB, RMSE_cfo, "-s")
    ax[1].set_title("RMSE CFO")
    ax[1].set_ylabel("RMSE [-]")
    ax[1].set_xlabel("$E_{s}/N_{0}$ [dB]")
    ax[1].grid()
    # RMSE STO
    ax[2].semilogy(EsN0s_dB, RMSE_sto, "-s")
    ax[2].set_title("RMSE STO")
    ax[2].set_ylabel("RMSE [-]")
    ax[2].set_xlabel("$E_{s}/N_{0}$ [dB]")
    ax[2].grid()

    plt.show()

    # Save simulation outputs (for later post-processing, building new figures,...)
    filename = "./telecom/python/telecom/sim_outputs"
    save_var = np.column_stack(
        (
            EsN0s_dB,
            BER,
            PER,
            RMSE_cfo,
            RMSE_sto,
            preamble_mis,
            preamble_false,
        )
    )
    np.savetxt(f"{filename}.csv", save_var, delimiter="\t")

    # Read file:
    # data = np.loadtxt('test.csv')
    # SNRs_dB = data[:,0]
    # ...


if __name__ == "__main__":
    main()
