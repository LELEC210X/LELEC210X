from typing import Optional

import numpy as np
from scipy.signal import savgol_filter

BIT_RATE = 50e3
PREAMBLE = [int(bit) for bit in f"{0xAAAAAAAA:0>32b}"]
SYNC_WORD = [int(bit) for bit in f"{0x3E2A54B7:0>32b}"]


class Chain:

    def __init__(
        self, *,
        name: str = "",
        # Communication parameters
        bit_rate: float = BIT_RATE,
        freq_dev: float = BIT_RATE / 4,
        osr_tx: int = 64,
        osr_rx: int = 8,
        preamble: list[int] = PREAMBLE,
        sync_word: list[int] = SYNC_WORD,
        payload_len: int = 50,  # Number of bits per packet
        # Simulation parameters
        n_packets: int = 100,  # Number of sent packets
        # Channel parameters
        sto_val: float = 0,
        sto_range: float = 1 / BIT_RATE,  # defines the delay range when random
        cfo_val: float = 0,
        cfo_range: float = (
            # defines the CFO range when random (in Hz) #(1000 in old repo)
            1000
        ),
        cfo_Moose_N: int = 4,
        snr_range: list[int] = list(range(-10, 35)),
        # Lowpass filter parameters
        numtaps: int = 31,
        cutoff: float = 150e3,
        bypass_preamble_detect: bool = False,
        bypass_cfo_estimation: bool = False,
        bypass_sto_estimation: bool = False,
        **kwargs
    ):
        self.name = name
        self.bit_rate = bit_rate
        self.freq_dev = freq_dev
        self.osr_rx = osr_rx
        self.osr_tx = osr_tx
        self.preamble = preamble
        self.sync_word = sync_word
        self.payload_len = payload_len
        self.n_packets = n_packets
        self.sto_val = sto_val
        self.sto_range = sto_range
        self.cfo_val = cfo_val
        self.cfo_range = cfo_range
        self.cfo_Moose_N = cfo_Moose_N
        self.snr_range = snr_range
        self.numtaps = numtaps
        if cutoff == 0.0:
            self.cutoff = BIT_RATE * self.osr_rx / 2.0001  # or 2*BIT_RATE,...
        else:
            self.cutoff = cutoff
        self.bypass_preamble_detect = bypass_preamble_detect
        self.bypass_cfo_estimation = bypass_cfo_estimation
        self.bypass_sto_estimation = bypass_sto_estimation
    

    def get_json(self):
        chain_json = {
            'bit_rate': self.bit_rate,
            'freq_dev': self.freq_dev,
            'osr_rx': self.osr_rx,
            'osr_tx': self.osr_tx,
            'payload_len': self.payload_len,
            'n_packets': self.n_packets,
            'sto_val': self.sto_val,
            'sto_range': self.sto_range,
            'cfo_val': self.cfo_val,
            'cfo_range': self.cfo_range,
            'cfo_Moose_N': self.cfo_Moose_N,
            'bypass_preamble_detect': self.bypass_preamble_detect,
            'bypass_cfo_estimation': self.bypass_cfo_estimation,
            'bypass_sto_estimation': self.bypass_sto_estimation
        }
        return chain_json

    # Tx methods

    def modulate(self, bits: np.array, print_TX=False, print_x_k=False) -> np.array:
        """
        Modulates a stream of bits of size N
        with a given TX oversampling factor R (osr_tx).

        Uses Continuous-Phase FSK modulation.

        :param bits: The bit stream, (N,).
        :param print_TX: If True, prints the transmitted bit array.
        :param print_x_k: If True, prints the x[k] array in polar representation.
        :return: The modulates bit sequence, (N * R,).
        """

        if print_TX:
            print(f"bits at transmitter : {bits}\n")

        fd = self.freq_dev  # Frequency deviation, Delta_f
        B = self.bit_rate  # B=1/T
        h = 2 * fd / B  # Modulation index
        R = self.osr_tx  # Oversampling factor

        x = np.zeros(len(bits) * R, dtype=np.complex64)
        ph = 2 * np.pi * fd * (np.arange(R) / R) / \
            B  # Phase of reference waveform

        phase_shifts = np.zeros(
            len(bits) + 1
        )  # To store all phase shifts between symbols
        phase_shifts[0] = 0  # Initial phase

        for i, b in enumerate(bits):
            x[i * R: (i + 1) * R] = np.exp(1j * phase_shifts[i]) * np.exp(
                1j * (1 if b else -1) * ph
            )  # Sent waveforms, with starting phase coming from previous symbol
            phase_shifts[i + 1] = phase_shifts[i] + h * np.pi * (
                1 if b else -1
            )  # Update phase to start with for next symbol

            if print_x_k:
                print(f"bit [{i}] : {b}")
                print(f'--> x[{i}] : {np.abs(x[i * R]):.2f} arg '
                      f'{np.angle(x[i * R]) / np.pi * 180:.2f}°  ...  '
                      f'{np.abs(x[(i + 1) * R - 1]):.2f}'
                      f'arg {np.angle(x[(i + 1) * R - 1]) / np.pi * 180:.2f}°\n')

        return x

    # Rx methods
    def preamble_detect(self, y: np.array) -> Optional[int]:
        """
        Detects the preamlbe in a given received signal.

        :param y: The received signal, (N * R,).
        :return: The index where the preamble starts,
            or None if not found.
        """
        raise NotImplementedError

    def cfo_estimation(self, y: np.array) -> float:
        """
        Estimates the CFO based on the received signal.

        :param y: The received signal, (N * R,).
        :return: The estimated CFO.
        """
        raise NotImplementedError

    def sto_estimation(self, y: np.array) -> float:
        """
        Estimates the STO based on the received signal.

        :param y: The received signal, (N * R,).
        :return: The estimated STO.
        """
        raise NotImplementedError

    def demodulate(self, y: np.array, print_RX=False, print_y_k=False) -> np.array:
        """
        Demodulates the received signal.

        :param y: The received signal, (N * R,).
        :param print_RX: If True, prints the received bit array.
        :param print_y_k: If True, prints the y[k] array in polar representation.
        :return: The signal, after demodulation.
        """
        raise NotImplementedError


class BasicChain(Chain):

    def __init__(self, *, name="Basic Tx/Rx chain", cfo_val=float('nan'), sto_val=float('nan'), **kwargs):

        super().__init__(name=name, cfo_val=cfo_val, sto_val=sto_val, **kwargs)

    def preamble_detect(self, y: np.array) -> Optional[int]:
        """
        Detects the preamble in a given received signal.
        Detects a preamble computing the received energy (average on a window).

        :param y: The received signal, (N * R,).
        :return: The index where the preamble starts,
            or None if not found.
        """
        L = 4 * self.osr_rx
        y_abs = np.abs(y)

        for i in range(0, int(len(y) / L)):
            sum_abs = np.sum(y_abs[i * L: (i + 1) * L])
            if sum_abs > (L - 1):  # fix threshold
                return i * L

        return None

    def cfo_estimation(self, y: np.array) -> float:
        """
        Estimates the CFO based on the received signal.
        Estimates CFO using Moose algorithm, on first samples of preamble.

        :param y: The received signal, (N * R,).
        :return: The estimated CFO.
        """
        # TO DO: extract 2 blocks of size N*R at the start of y

        # TO DO: apply the Moose algorithm on these two blocks to estimate the CFO
        N_Moose = self.cfo_Moose_N  # max should be total bits per preamble / 2
        R = self.osr_rx
        N_t = N_Moose * R
        T = 1 / self.bit_rate

        alpha_est = np.vdot(y[:N_t], y[N_t:2*N_t])

        cfo_est = np.angle(alpha_est) * R / (2 * np.pi * N_t * T)

        return cfo_est


    def sto_estimation(self, y: np.array) -> float:
        """
        Estimates the STO based on the received signal.
        Estimates symbol timing (fractional) based on phase shifts.

        :param y: The received signal, (N * R,).
        :return: The estimated STO.
        """
        R = self.osr_rx

        # Computation of derivatives of phase function
        phase_function = np.unwrap(np.angle(y))
        phase_derivative_1 = phase_function[1:] - phase_function[:-1]
        phase_derivative_2 = np.abs(
            phase_derivative_1[1:] - phase_derivative_1[:-1])

        sum_der_saved = -np.inf
        save_i = 0
        for i in range(0, R):
            sum_der = np.sum(phase_derivative_2[i::R])  # Sum every R samples

            if sum_der > sum_der_saved:
                sum_der_saved = sum_der
                save_i = i

        return np.mod(save_i + 1, R)

    def demodulate(self, y: np.array, print_RX=False, print_y_k=False) -> np.array:
        """
        Demodulates the received signal.
        Non-coherent demodulator.

        :param y: The received signal, (N * R,).
        :param print_RX: If True, prints the received bit array.
        :param print_y_k: If True, prints the y[k] array in polar representation.
        :return: The signal, after demodulation.
        """
        fd = self.freq_dev  # Frequency deviation, Delta_f
        R = self.osr_rx  # Receiver oversampling factor
        N = len(y) // R  # Number of CPFSK symbols in y
        T = 1 / self.bit_rate

        # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
        y = np.resize(y, (N, R))

        # TO DO: generate the reference waveforms used for the correlation
        # hint: look at what is done in modulate() in chain.py
        e_0 = np.exp(-1j * 2 * np.pi * fd * np.arange(R) * T / R)
        e_1 = np.exp(1j * 2 * np.pi * fd * np.arange(R) * T / R)

        # TO DO: compute the correlations with the two reference waveforms (r0 and r1)
        r0 = np.dot(y, np.conj(e_0)) / T
        r1 = np.dot(y, np.conj(e_1)) / T

        # TO DO: performs the decision based on r0 and r1
        bits_hat = (np.abs(r1) > np.abs(r0)).astype(int)

        if print_y_k:
            for k in range(N):
                print(f'y[{k}] : {np.abs(y[k][0]):.2f} arg '
                      f'{np.angle(y[k][0]) / np.pi * 180:.2f}°  ...  '
                      f'{np.abs(y[k][R - 1]):.2f} arg '
                      f'{np.angle(y[k][R - 1]) / np.pi * 180:.2f}°')
                print(f'--> r0[k] = {np.abs(r0[k]):.2f} arg '
                      f'{np.angle(r0[k]) / np.pi * 180:.2f}°, r1 = '
                      f'{np.abs(r1[k]):.2f} arg '
                      f'{np.angle(r1[k]) / np.pi * 180:.2f}°\n')
                print(f"--> bit [{k}] : {bits_hat[k]}")

        if print_RX:
            print(f"bits at receiver : {bits_hat}\n")

        return bits_hat

class OptimizedChain(BasicChain):

    def __init__(
        self, *, name="Basic Tx/Rx chain",
        cfo_Moose_N_list: list[int] = [2, 4, 8, 16],
        **kwargs
    ):
        
        super().__init__(**kwargs)
        self.name=name
        self.freq_dev=BIT_RATE/2
        self.cfo_Moose_N_list = cfo_Moose_N_list
    

    def get_json(self):
        chain_json = super().get_json()
        chain_json['cfo_Moose_N_list'] = self.cfo_Moose_N_list
        return chain_json
  

    def cfo_estimation(self, y: np.array) -> float:
        """
        Estimates the CFO based on the received signal.
        Estimates CFO using Moose algorithm, on first samples of preamble.

        :param y: The received signal, (N * R,).
        :return: The estimated CFO.
        """
        N_Moose_list = self.cfo_Moose_N_list  # max should be total bits per preamble / 2
        R = self.osr_rx
        B = self.bit_rate
        T = 1 / B

        first_est = True
        cfo_est_off = 0.
        for N_Moose in N_Moose_list:
            N_t = N_Moose * R
            alpha_est = np.vdot(y[:N_t], y[N_t:2*N_t])
            new_cfo_est = np.angle(alpha_est) * R / (2 * np.pi * N_t * T)

            if first_est:
                first_est = not first_est
            elif abs(cfo_est - new_cfo_est) > 1/(2*N_Moose*T): # Ambiguity detected
                cfo_est_off += np.sign(cfo_est) * 1 / (N_Moose*T)
            cfo_est = new_cfo_est
        
        return cfo_est + cfo_est_off
    

    def sto_estimation(self, y: np.array) -> float:
        """
        Estimates the STO based on the received signal.
        Estimates symbol timing (fractional) based on phase shifts.

        :param y: The received signal, (N * R,).
        :return: The estimated STO.
        """
        R = self.osr_rx

        # Computation of derivatives of phase function
        phase_function = np.unwrap(np.angle(y))
        phase_function_smooth = savgol_filter(phase_function, window_length=5, polyorder=3)
        phase_derivative_1 = savgol_filter(phase_function, window_length=5, polyorder=3, deriv=1)
        phase_derivative_2 = np.abs(savgol_filter(phase_function, window_length=5, polyorder=3, deriv=2))
        
        sum_der_saved = -np.inf
        save_i = 0
        for i in range(0, R):
            sum_der = np.sum(phase_derivative_2[i::R])  # Sum every R samples

            if sum_der > sum_der_saved:
                sum_der_saved = sum_der
                save_i = i

        return np.mod(save_i + 1, R)

        
