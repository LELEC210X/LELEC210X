from typing import Optional

import numpy as np

BIT_RATE = 50e3
PREAMBLE = np.array([int(bit) for bit in f"{0xAAAAAAAA:0>32b}"])
SYNC_WORD = np.array([int(bit) for bit in f"{0x3E2A54B7:0>32b}"])


class Chain:
    name = ""

    ## Communication parameters
    bit_rate = BIT_RATE
    freq_dev = BIT_RATE / 2

    osr_tx = 64
    osr_rx = 8

    preamble = PREAMBLE
    sync_word = SYNC_WORD

    payload_len = 50  # Number of bits per packet

    ## Simulation parameters
    n_packets = 1000  # Number of sent packets

    ## Channel parameters
    sto_val = 0
    sto_range = 10 / BIT_RATE  # defines the delay range when random

    cfo_val = 0
    cfo_range = 10000  # defines the CFO range when random (in Hz) #(1000 in old repo)

    snr_range = np.arange(-10, 25)

    ## Lowpass filter parameters
    numtaps = 100
    cutoff =  freq_dev + BIT_RATE
    #cutoff = BIT_RATE * osr_rx / 2.0001  # or 2*BIT_RATE,...

    ## Tx methods

    def modulate(self, bits: np.array) -> np.array:
        """
        Modulates a stream of bits of size N
        with a given TX oversampling factor R (osr_tx).

        Uses Continuous-Phase FSK modulation.

        :param bits: The bit stream, (N,).
        :return: The modulates bit sequence, (N * R,).
        """
        fd = self.freq_dev  # Frequency deviation, Delta_f
        B = self.bit_rate  # B=1/T
        h = 2 * fd / B  # Modulation index
        R = self.osr_tx  # Oversampling factor

        x = np.zeros(len(bits) * R, dtype=np.complex64)
        ph = 2 * np.pi * fd * (np.arange(R) / R) / B  # Phase of reference waveform

        phase_shifts = np.zeros(
            len(bits) + 1
        )  # To store all phase shifts between symbols
        phase_shifts[0] = 0  # Initial phase

        for i, b in enumerate(bits):
            x[i * R : (i + 1) * R] = np.exp(1j * phase_shifts[i]) * np.exp(
                1j * (1 if b else -1) * ph
            )  # Sent waveforms, with starting phase coming from previous symbol
            phase_shifts[i + 1] = phase_shifts[i] + h * np.pi * (
                1 if b else -1
            )  # Update phase to start with for next symbol

        return x

    ## Rx methods
    bypass_preamble_detect = False

    def preamble_detect(self, y: np.array) -> Optional[int]:
        """
        Detects the preamlbe in a given received signal.

        :param y: The received signal, (N * R,).
        :return: The index where the preamble starts,
            or None if not found.
        """
        raise NotImplementedError

    bypass_cfo_estimation = True

    def cfo_estimation(self, y: np.array) -> float:
        """
        Estimates the CFO based on the received signal.

        :param y: The received signal, (N * R,).
        :return: The estimated CFO.
        """
        raise NotImplementedError

    bypass_sto_estimation = True

    def sto_estimation(self, y: np.array) -> float:
        """
        Estimates the STO based on the received signal.

        :param y: The received signal, (N * R,).
        :return: The estimated STO.
        """
        raise NotImplementedError

    def demodulate(self, y: np.array) -> np.array:
        """
        Demodulates the received signal.

        :param y: The received signal, (N * R,).
        :return: The signal, after demodulation.
        """
        raise NotImplementedError


class BasicChain(Chain):
    name = "Basic Tx/Rx chain"

    cfo_val, sto_val = np.nan, np.nan  # CFO and STO are random

    bypass_preamble_detect = False

    def preamble_detect(self, y):
        """
        Detect a preamble computing the received energy (average on a window).
        """
        L = 4 * self.osr_rx
        y_abs = np.abs(y)

        for i in range(0, int(len(y) / L)):
            sum_abs = np.sum(y_abs[i * L : (i + 1) * L])
            if sum_abs > (L - 1):  # fix threshold
                return i * L

        return None

    bypass_cfo_estimation = False

    def cfo_estimation(self, y):
        """
        Estimates CFO using Moose algorithm, on first samples of preamble.
        """
        # TO DO: extract 2 blocks of size N*R at the start of y
        R = self.osr_rx
        N = 2
        b1, b2 = y[0 : N * R], y[N * R : 2 * N * R]

        # TO DO: apply the Moose algorithm on these two blocks to estimate the CFO
        r = np.sum(b2 * np.conj(b1)) / (N * R)
        cfo_est = np.angle(r) / (2 * np.pi * N * R) * (self.bit_rate * R)

        return cfo_est

    bypass_sto_estimation = False

    def sto_estimation(self, y):
        """
        Estimates symbol timing (fractional) based on phase shifts.
        """
        R = self.osr_rx

        # Computation of derivatives of phase function
        phase_function = np.unwrap(np.angle(y))
        phase_derivative_1 = phase_function[1:] - phase_function[:-1]
        phase_derivative_2 = np.abs(phase_derivative_1[1:] - phase_derivative_1[:-1])

        sum_der_saved = -np.inf
        save_i = 0
        for i in range(0, R):
            sum_der = np.sum(phase_derivative_2[i::R])  # Sum every R samples

            if sum_der > sum_der_saved:
                sum_der_saved = sum_der
                save_i = i

        return np.mod(save_i + 1, R)

    def demodulate(self, y):
        """
        Non-coherent demodulator.
        """
        R = self.osr_rx  # Receiver oversampling factor
        nb_syms = len(y) // R  # Number of CPFSK symbols in y

        # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
        y = np.resize(y, (nb_syms, R))

        # TO DO: generate the reference waveforms used for the correlation
        # hint: look at what is done in modulate() in chain.py
        f = self.freq_dev / self.bit_rate
        ph = 2 * np.pi * np.arange(R) / R * f
        exp_f1 = np.conj(np.exp(+1j * ph))
        exp_f2 = np.conj(np.exp(-1j * ph))

        # TO DO: compute the correlations with the two reference waveforms (r0 and r1)
        r1 = np.abs(np.sum(y * exp_f1, 1) / R)
        r2 = np.abs(np.sum(y * exp_f2, 1) / R)

        # TO DO: performs the decision based on r0 and r1
        r = r1 - r2

        s_hat = np.sign(r)

        bits_hat = s_hat.astype(int)
        bits_hat[s_hat < 0] = 0

        return bits_hat


class TeachingChain(BasicChain):
    name = "Teaching Tx/Rx Chain"

    bypass_cfo_estimation = True

    def preamble_detect(self, y):
        """
        Detect a preamble using its temporal properties (repetition [1,0,1,0,...]).
        """
        N = 4
        R = self.osr_rx

        for i in range(0, int(len(y) / R) - 2 * N):
            b1 = y[i * R : (i + N) * R]
            b2 = y[(i + N) * R : (i + 2 * N) * R]

            r = np.sum(b2 * np.conj(b1)) / (N * R)
            if np.abs(r) > 0.9:
                return i * R
        return None

    bypass_cfo_estimation = True

    def cfo_estimation(self, y):
        """
        Estimates CFO using Moose algorithm, averaged on several estimations.
        """

        N = 4
        R = self.osr_rx

        b1, b2 = y[0 : N * R], y[N * R : 2 * N * R]
        r = np.sum(b2 * np.conj(b1)) / (N * R)
        cfo_1 = np.angle(r) / (2 * np.pi * N * R) * (self.bit_rate * R)

        b1, b2 = y[2 * N * R : 3 * N * R], y[3 * N * R : 4 * N * R]
        r = np.sum(b2 * np.conj(b1)) / (N * R)
        cfo_2 = np.angle(r) / (2 * np.pi * N * R) * (self.bit_rate * R)

        b1, b2 = y[4 * N * R : 5 * N * R], y[5 * N * R : 6 * N * R]
        r = np.sum(b2 * np.conj(b1)) / (N * R)
        cfo_3 = np.angle(r) / (2 * np.pi * N * R) * (self.bit_rate * R)

        return (cfo_1 + cfo_2 + cfo_3) / 3

    bypass_sto_estimation = True

    def sto_estimation(self, y):
        """
        Estimates symbol timing based on correlation with expected modulated sync word.
        """
        x_addr = self.modulate(self.sync_word, self.osr_rx)

        v = np.abs(np.correlate(y, x_addr, mode="full"))
        return np.argmax(v) - len(x_addr) + 1