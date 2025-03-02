import numpy as np
from scipy.signal import firwin
from tqdm import tqdm
import os
import json
from telecom.hands_on_simulation.chain import Chain, BasicChain, OptimizedChain
from telecom.hands_on_simulation.load_simdata import (parse_args, register_simulation,
                            find_simulation, simdata_path, load_chain)
from telecom.hands_on_simulation.sim_utils import plot_graphs


def add_delay(chain: Chain, x: np.ndarray, tau: float):
    """
    Apply the channel between TX and RX, handling the different oversampling factors
    and the addition of a delay.
    """
    fs = chain.bit_rate * chain.osr_rx  # Receiver sampling frequency
    # Integer delay (on the received samples)
    sto_int = np.floor(tau * fs).astype(int)
    sto_frac = tau * fs - sto_int  # Fractional delay, remaining

    R = int(chain.osr_tx / chain.osr_rx)
    idx = np.floor(
        sto_frac * R
    ).astype(
        int
        # Index of best sample (available in transmitted signal oversampled at TX) depicting the fractional delay
    )

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


def run_sim(chain: Chain, sim_id):
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
    # Preamble miss detection (not found)
    preamble_misdetect = np.zeros(len(SNRs_dB))
    preamble_false_detect = np.zeros(
        len(SNRs_dB)
    )  # Preamble false detection (found in noise)
    SNR_est_matrix = np.zeros((len(SNRs_dB), chain.n_packets))

    # Transmitted signals that are independent of the payload bits
    # Modulated signal containing preamble
    x_pr = chain.modulate(chain.preamble)
    # Modulated signal containing sync_word
    x_sync = chain.modulate(chain.sync_word)
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
        x = np.concatenate(
            (x_noise, x_pr, x_sync, x_pay, np.zeros(chain.osr_tx)))

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
                np.abs(y_filt[0: chain.payload_len * chain.osr_rx]) ** 2
            )
            signal_energy_est = (
                np.mean(
                    np.abs(y_filt[-chain.payload_len * chain.osr_rx:]) ** 2)
                - noise_power_est
            )
            SNR_est = signal_energy_est / noise_power_est

            SNR_est_matrix[k, n] = SNR_est

            # Preamble detection stage
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

                # Synchronization stage
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

                # Demodulation and deframing stage
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
                    start_frame: start_frame + chain.payload_len
                ]  # Demodulated payload bits

                # Computing performance metrics
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

    np.savetxt(simdata_path+sim_id+'.csv', save_var, delimiter=",", comments='',
               header=f"SNR_o [dB],SNR_e [dB],BER,PER,RMSE cfo,RMSE sto,preamble miss rate,preamble false rate,SNR estimation matrix ({chain.n_packets} columns)")


def main(arg_list: list[str] = None):

    sim_params, chain_params = parse_args(arg_list)

    # Change the chain parameters here, for example:
    # chain_params.payload_len = 50
    # chain_params.n_packets = 100
    # chain_params.cfo_Moose_N = 2
    # chain_params.cfo_range = 10_000
    # chain_params.bypass_preamble_detect = True
    # chain_params.bypass_cfo_estimation = True
    # chain_params.bypass_sto_estimation = True

    # Change the simulation parameters here, for example:
    # sim_params.force_simulation = True
    # sim_params.basic = True
    # sim_params.sim_id = 1
    # sim_params.no_show = True
    # sim_params.no_save = True
    # sim_params.FIR = True 

    chain: Chain
    chain_class: str
    sim_id: str = None
    if sim_params.sim_id:
        sim_id = f'simulation_{sim_params.sim_id:04d}'
        chain, chain_class = load_chain(sim_id)
    else:
        if sim_params.basic:
            chain_class = 'BasicChain'
            chain = BasicChain(**vars(chain_params))
        else:
            chain_class = 'OptimizedChain'
            chain = OptimizedChain(**vars(chain_params))
            # You can also change the chain parameters here
            # chain.cfo_val=8_000,

    sim_details = find_simulation(chain.get_json(), chain_class=chain_class)
    if not any(status == 'completed' for *_, status in sim_details) or sim_params.force_simulation:
        if sim_id is None:
            sim_id = register_simulation(chain.get_json(), chain_class, status='completed')
        else:
            register_simulation(chain.get_json(), chain_class, sim_id=sim_id, status='completed')
        run_sim(chain, sim_id)
    else:
        sim_id = next((sim_id for sim_id, _, status in sim_details if status == 'completed'), None)

    if not sim_params.no_show or not sim_params.no_save:
        plot_graphs(chain, sim_id=sim_id, show=not sim_params.no_show,
                    save=not sim_params.no_save, FIR=sim_params.FIR)


if __name__ == "__main__":
    main()