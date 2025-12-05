# ruff: noqa: N806
import numpy as np

BIT_RATE = 50e3
PREAMBLE = np.array([int(bit) for bit in f"{0xAAAAAAAA:0>32b}"])
SYNC_WORD = np.array([int(bit) for bit in f"{0x3E2A54B7:0>32b}"])

FPGA_FIR_TAPS =  np.array([-0.001201261290430126, 0.0020488944185569607, -0.0020751053507837938, 4.910806933254215E-18, 0.004754535968663148, -0.00987450755161552, 0.00995675888032359, -1.4391882903962387E-17, -0.018922538981281996, 0.036214375130954504, -0.03468641976116993, 2.4803862788187382E-17, 0.06848299151299582, -0.15293237705130486, 0.22297239138994396, 0.7505245253702963, 0.22297239138994396, -0.15293237705130486, 0.06848299151299582, 2.4803862788187385E-17, -0.034686419761169936, 0.036214375130954504, -0.018922538981282003, -1.4391882903962393E-17, 0.00995675888032359, -0.009874507551615532, 0.004754535968663151, 4.910806933254215E-18, -0.0020751053507837946, 0.0020488944185569607, -0.001201261290430126])  # Example coefficients

class Chain:
    name: str = ""

    # Communication parameters
    bit_rate: float = BIT_RATE
    freq_dev: float = BIT_RATE / 4

    osr_tx: int = 64
    osr_rx: int = 8

    preamble: np.ndarray = PREAMBLE
    sync_word: np.ndarray = SYNC_WORD

    payload_len: int = 8 * 100  # Number of bits per packet

    # Simulation parameters
    n_packets: int = 100  # Number of sent packets

    # Channel parameters
    sto_val: float = 0
    sto_range: float = 10 / BIT_RATE  # defines the delay range when random

    cfo_val: float = np.nan
    cfo_range: tuple[float, float] = (
        8_000,
        10_000,  # defines the CFO range when random (in Hz) #(1000 in old repo)
    )

    EsN0_range: np.ndarray = np.arange(0, 30, 1)

    # Lowpass filter parameters
    taps   : np.ndarray = FPGA_FIR_TAPS #specify None to make the simulator recompute the filter based on below spec
    numtaps: int = 100
    cutoff : float = 150e3  # BIT_RATE * osr_rx / 2.0001  # or 2*BIT_RATE,...

    # Tx methods

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

    # Rx methods
    ideal_preamble_detect: bool = False
 
    use_dynamic_ppd: bool = False

    def preamble_detect(self, y: np.array) -> int | None:
        """
        Detect the preamble in a given received signal with hard thresholding.

        :param y: The received signal, (N * R,).
        :return: The index where the preamble starts,
            or None if not found.
        """
        raise NotImplementedError
    
    def preamble_detect_ppd(self, y: np.array) -> int | None:
        """
        Detect the preamble in a given received signal with sofft thresholding.

        :param y: The received signal, (N * R,).
        :return: The index where the preamble starts,
            or None if not found.
        """
        raise NotImplementedError

    ideal_cfo_estimation: bool = False

    def cfo_estimation(self, y: np.array) -> float:
        """
        Estimates the CFO based on the received signal.

        :param y: The received signal, (N * R,).
        :return: The estimated CFO.
        """
        raise NotImplementedError

    ideal_sto_estimation: bool = False

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

    ideal_preamble_detect = True

    use_dynamic_ppd       = True

    def preamble_detect_ppd(self, y):
        """Detect a preamble computing the received energy (average on a window)."""
        long_term_sum_W = 256
        short_term_sum_W = 32

        K = 5 * (short_term_sum_W / long_term_sum_W)

        long_window = np.ones(long_term_sum_W)
        short_window = np.ones(short_term_sum_W)

        yabs = np.abs(y)
        ylen = len(y)
        long_sum = np.convolve(yabs, long_window, mode="full")
        short_sum = np.convolve(yabs, short_window, mode="full")

        long_sum = long_sum[long_term_sum_W:ylen]
        short_sum = short_sum[long_term_sum_W + short_term_sum_W - 1 :]

        detection = short_sum > (long_sum * K)
        detected_indices = np.where(detection)[0]
        first_idx = (
            (detected_indices[0] + long_term_sum_W + short_term_sum_W)
            if detected_indices.size > 0
            else None
        )
        return first_idx

    def preamble_detect(self, y):
        """Detect a preamble computing the received energy (average on a window)."""
        L = 4 * self.osr_rx
        y_abs = np.abs(y)

        for i in range(0, int(len(y) / L)):
            sum_abs = np.sum(y_abs[i * L : (i + 1) * L])
            if sum_abs > (L - 1):  # fix threshold
                return i * L

        return None

    ideal_cfo_estimation = True

    def cfo_estimation(self, y):
        """Estimates CFO using Moose algorithm, on first samples of preamble."""
        # TO DO: extract 2 blocks of size N*R at the start of y
        N = 4  # You can change this value if needed
        # TO DO: apply the Moose algorithm on these two blocks to estimate the CFO
        cfo_est = 0

        return cfo_est

    ideal_sto_estimation = True

    def sto_estimation(self, y):
        """Estimates symbol timing (fractional) based on phase shifts."""
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
        """Non-coherent demodulator."""
        R = self.osr_rx  # Receiver oversampling factor
        nb_syms = len(y) // R  # Number of CPFSK symbols in y

        # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
        y = np.resize(y, (nb_syms, R))

        # TO DO: generate the reference waveforms used for the correlation
        # hint: look at what is done in modulate() in chain.py

        # TO DO: compute the correlations with the two reference waveforms (r0 and r1)

        # TO DO: performs the decision based on r0 and r1

        bits_hat = np.zeros(nb_syms, dtype=int)

        return bits_hat
