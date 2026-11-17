import numpy as np
import pmt
from gnuradio import gr
import time

from .utils import logging, parse_common_params


# ---------------------------------------------------------------------------
# Bit-reflection helper (used by CRC routines that require reflected I/O)
# ---------------------------------------------------------------------------

def reflect_data(x, width):
    # See: https://stackoverflow.com/a/20918545
    if width == 8:
        x = ((x & 0x55) << 1) | ((x & 0xAA) >> 1)
        x = ((x & 0x33) << 2) | ((x & 0xCC) >> 2)
        x = ((x & 0x0F) << 4) | ((x & 0xF0) >> 4)
    elif width == 16:
        x = ((x & 0x5555) << 1) | ((x & 0xAAAA) >> 1)
        x = ((x & 0x3333) << 2) | ((x & 0xCCCC) >> 2)
        x = ((x & 0x0F0F) << 4) | ((x & 0xF0F0) >> 4)
        x = ((x & 0x00FF) << 8) | ((x & 0xFF00) >> 8)
    elif width == 32:
        x = ((x & 0x55555555) << 1) | ((x & 0xAAAAAAAA) >> 1)
        x = ((x & 0x33333333) << 2) | ((x & 0xCCCCCCCC) >> 2)
        x = ((x & 0x0F0F0F0F) << 4) | ((x & 0xF0F0F0F0) >> 4)
        x = ((x & 0x00FF00FF) << 8) | ((x & 0xFF00FF00) >> 8)
        x = ((x & 0x0000FFFF) << 16) | ((x & 0xFFFF0000) >> 16)
    else:
        raise ValueError("Unsupported width")
    return x


# ---------------------------------------------------------------------------
# CRC-8/SMBUS computation (bit-serial version, used by the legacy sender)
# ---------------------------------------------------------------------------

def crc_poly(data, n, poly, crc=0, ref_in=False, ref_out=False, xor_out=0):
    # See : https://gist.github.com/Lauszus/6c787a3bc26fea6e842dfb8296ebd630
    g = 1 << n | poly  # Generator polynomial

    # Loop over the data
    for d in data:
        # Reverse the input byte if the flag is true
        if ref_in:
            d = reflect_data(d, 8)

        # XOR the top byte in the CRC with the input byte
        crc ^= d << (n - 8)

        # Loop over all the bits in the byte
        for _ in range(8):
            # Start by shifting the CRC, so we can check for the top bit
            crc <<= 1

            # XOR the CRC if the top bit is 1
            if crc & (1 << n):
                crc ^= g

    # Reverse the output if the flag is true
    if ref_out:
        crc = reflect_data(crc, n)

    # Return the CRC value
    return crc ^ xor_out


# ---------------------------------------------------------------------------
# CP-FSK modulator
# ---------------------------------------------------------------------------

def modulate(bits, B, R, Fdev):
    """
    Continuous-Phase FSK modulator (vectorized cumulative-phase form).

    Generates a complex baseband waveform for a stream of binary symbols.
    Each bit is transmitted over R samples at symbol rate B. The frequency
    deviation Fdev shifts the instantaneous frequency by ±Fdev around the
    carrier. The continuous-phase constraint ensures the phase is never
    discontinuous at symbol transitions, which limits the signal bandwidth.

    Parameters
    ----------
    bits : array of 0/1 bit values
    B    : symbol (bit) rate [Hz]
    R    : oversampling ratio (samples per symbol at the TX sample rate)
    Fdev : frequency deviation [Hz]

    Returns
    -------
    x : complex64 baseband waveform, length = len(bits)*R
    """
    f = Fdev / B
    h = 2*f  # Modulation index

    bits = np.asarray(bits)
    signs = np.where(bits, 1.0, -1.0)  # +1 for bit=1, -1 for bit=0

    # Cumulative phase at the *start* of each symbol (phase_shifts[0] = 0).
    # Each symbol advances the phase by h*pi = pi * 2f, maintaining continuity.
    phase_shifts = np.concatenate(([0.0], np.cumsum(h * np.pi * signs)))[:-1]

    # Intra-symbol linear phase ramp (same for every symbol, scaled by ±1)
    ph = 2 * np.pi * np.arange(R) / R * f

    # Combine per-symbol starting phase with the intra-symbol ramp in one broadcast
    total_phase = phase_shifts[:, None] + signs[:, None] * ph[None, :]

    return np.exp(1j * total_phase).astype(np.complex64).reshape(-1)



# ---------------------------------------------------------------------------
# Packet builder: payload → CRC → modulated waveform
# ---------------------------------------------------------------------------

def packet_generate(payload_len, B, R, Fdev, rng, x_pr, x_sync):
    """
    Build one complete CP-FSK packet: preamble + sync word + payload + CRC.

    The payload bytes are either drawn from `rng` (random mode) or filled
    with a deterministic counter pattern (rng=None). The CRC appended to the
    payload allows the receiver to detect bit errors.

    Parameters
    ----------
    payload_len  : number of payload bytes
    B, R, Fdev   : modulation parameters (passed through to modulate())
    rng          : numpy Generator seeded with (seed, content_id), or None
    x_pr, x_sync : pre-modulated preamble and sync-word waveforms

    Returns
    -------
    crc           : uint8 CRC byte
    payload_bytes : array of uint8 payload bytes
    packet        : complex64 baseband waveform for the full packet
    """
    # --- Generate payload ---
    if rng is None:
        payload_bytes = (np.mod(np.arange(0, payload_len), 255)).astype(np.uint8)
        #payload_bytes =  ((X*np.ones(payload_len))).astype(np.uint8)
    else:
        payload_bytes = rng.integers(256, size=payload_len).astype(np.uint8)

    # --- Compute CRC-8/SMBUS over the payload ---
    crc = crc_poly(
        bytearray(payload_bytes),
        8,
        0x07,
        crc=0xFF,
        ref_in=False,
        ref_out=False,
        xor_out=0,
    )

    # --- Modulate payload + CRC bits ---
    bits_send = np.unpackbits((np.append(payload_bytes, crc)).astype(np.uint8), bitorder='big')
    modulated_payload = modulate(bits_send, B, R, Fdev)

    # --- Concatenate preamble + sync word + payload to form the full packet ---
    packet = np.concatenate((x_pr, x_sync, modulated_payload))

    return crc, payload_bytes, packet



# ===========================================================================
# GNU Radio block: packet_generator
# ===========================================================================

class packet_generator(gr.sync_block):
    """
    Source block that autonomously and periodically transmits a
    fixed number of packets, then stops the flowgraph.

    Every packet carries the same payload, but a fresh carrier
    frequency offset (CFO), drawn uniformly from
    [cfo_min, cfo_max) for each transmission, is applied to it.
    Packets are separated by zero_samples_fixed +
    Uniform[0, zero_samples_rand] samples of silence.

    Once `Npackets` packets have been emitted, the block signals end
    of stream (WORK_DONE), which stops the flowgraph.

    EsN0 sweep
    ----------
    The block sweeps over n_EsN0 linearly spaced SNR values between
    EsN0_min and EsN0_max (dB). For each distinct payload content, the
    same impaired waveform (CFO, STO) is replayed at every SNR step, only
    rescaling the amplitude. This avoids re-running modulation per step.
    The TX amplitude realizing a target Es/N0 is:
        amp = noise_std * 10^(EsN0_dB/20) / sqrt(OSR_RX)
    where noise_std is the AWGN standard deviation added downstream.

    Tags
    ----
    At the first sample of each packet, the block attaches PMT tags:
    ID, payload_id, cfo, sto, offset, amp, esn0 — which the downstream
    packet_stats block uses as ground truth for performance evaluation.
    """

    def __init__(self, common_params, Npackets,
                 EsN0_min, EsN0_max, n_EsN0, noise_std,
                 osr_tx, add_sto,
                 cfo_min, cfo_max,
                 zero_samples_fixed, zero_samples_rand, payload_random, pkt_regen, seed):
        gr.sync_block.__init__(
            self,
            name='packet_generator',
            in_sig=None,
            out_sig=[np.complex64],
        )

        self.start_time     = time.time()
        self.payload_random = payload_random
        self.pkt_regen      = pkt_regen

        # --- Parse common radio parameters ---
        p = parse_common_params(common_params)
        self.payload_len = p["payload_len"]
        self.drate      = p["data_rate"]
        self.osr_rx     = p["oversampling"]
        self.osr_tx     = osr_tx
        self.osr_t_r    = int(self.osr_tx / self.osr_rx)
        self.fdev       = p["fdev"]
        self.fsamp      = p["samp_rate"]

        self.hdr_len      = p["hdr_len"]
        self.sync_word    = p["sync_word"]
        self.preamble_len = p["preamble_len"]
        # Preamble: alternating 10101010… bit pattern (0xAA repeated)
        self.preamble     = np.array([int(bit) for bit in f"{0xAA:0>8b}"] * self.preamble_len)

        # --- CFO impairment range ---
        self.cfo_min = cfo_min
        self.cfo_max = cfo_max
        self._cfo    = 0

        # --- STO (Symbol Timing Offset) impairment ---
        # If add_sto is set, a fractional timing offset (in samples) is drawn
        # for each new payload and applied by down-sampling from osr_tx to osr_rx.
        self.add_sto = add_sto
        self.sto         = 0
        self.sto_idx     = 0
        if (self.add_sto == 1) and (self.osr_tx >= self.osr_rx):
            self.used_osr = self.osr_tx
        else:
            self.used_osr = self.osr_rx

        self._amp = 1

        # --- EsN0 sweep: pre-compute amplitude for each SNR step ---
        # EsN0_lin = (amp^2 / noise_std^2)*OSR_RX  =>  amp = noise_std * (10^(EsN0_dB/20))/np.sqrt(OSR_RX)
        self.EsN0_min  = EsN0_min
        self.EsN0_max  = EsN0_max
        self.n_esn0    = n_EsN0
        self.noise_std = noise_std

        self.esn0_values = np.linspace(self.EsN0_min, self.EsN0_max, self.n_esn0, endpoint=True)
        if len(self.esn0_values) == 0:
            self.esn0_values = np.array([self.EsN0_min])

        # Total transmissions = Npackets per EsN0 step × number of EsN0 steps
        self.Npackets    = int(Npackets) * self.n_esn0

        self._esn0_idx = 0
        self._esn0     = self.esn0_values[0]
        self._impaired_packet = None

        # --- Gap (silence) parameters ---
        self.zero_samples_fixed = int(zero_samples_fixed)
        self.zero_samples_rand  = int(zero_samples_rand)

        # --- Reproducible payload generation ---
        # Each distinct payload is generated from rng((seed, content_id)), making
        # it reproducible independently of draw order.  The receiver reconstructs
        # the same payload given (seed, payload_id) to count bit errors.
        self.seed = int(seed)
        self._content_id = 0
        self._payload_id = 0

        self.rng              = np.random.default_rng(1234)  # STO draws only
        self.zero_samples_rng = np.random.default_rng(5678)

        # --- Pre-modulate preamble and sync word (invariant across packets) ---
        # Preamble & sync-word waveforms only depend on (drate, used_osr, fdev),
        # which never change over the block's lifetime: modulate them once instead
        # of redoing it on every single packet.
        self.x_pr   = modulate(self.preamble,   self.drate, self.used_osr, self.fdev)
        self.x_sync = modulate(self.sync_word,  self.drate, self.used_osr, self.fdev)

        self.logger = logging.getLogger("pktGenerator")

        # Pre-generate the first packet if pkt_regen is disabled or payload is not random
        if (self.pkt_regen == 0) or (not self.payload_random):
            if self.payload_random:
                payload_rng = np.random.default_rng((self.seed, self._content_id))
            else:
                payload_rng = None

            self.crc, self.payload_bytes, self.packet = packet_generate(
                self.payload_len, self.drate, self.used_osr, self.fdev, payload_rng,
                self.x_pr, self.x_sync,
            )

        # --- Internal streaming state machine ---
        # work() is the sole reader/writer of this state (no other
        # thread touches it), so no locking is needed around it.
        self._n_sent         = 0
        self._in_gap         = True   # start with a silence gap before the first packet
        self._pos            = 0
        self._current_chunk  = self._draw_gap_chunk()


    def _draw_packet_chunk(self):
        """
        Prepare the next impaired packet waveform for transmission.

        On the first EsN0 step of a new payload (esn0_idx == 0), a fresh
        payload is generated and channel impairments (CFO rotation, STO
        sub-sampling) are applied.  For subsequent EsN0 steps the same
        impaired waveform is reused — only the amplitude changes.
        """
        if self._esn0_idx == 0:
            # New payload + channel impairment (CFO, STO): drawn once
            # per regeneration, then replayed unchanged (bar amplitude)
            # for every EsN0 value in the sweep below - this is what
            # avoids re-running modulation/CRC/CFO-rotation once per
            # EsN0 step.
            if (self.pkt_regen) and (self.payload_random):
                payload_rng = np.random.default_rng((self.seed, self._content_id))
                self.crc, self.payload_bytes, self.packet = packet_generate(
                    self.payload_len, self.drate, self.used_osr, self.fdev, payload_rng,
                    self.x_pr, self.x_sync,
                )
                self._payload_id  = self._content_id
                self._content_id += 1

            drawn_packet = self.packet

            # Apply a random fractional STO by selecting a sub-sampled version
            # of the TX waveform (simulates a timing offset at the receiver)
            if self.add_sto:
                sto          = self.rng.random()  # Draw a fractional STO, 1 being a symbol
                self.sto     = sto / (self.drate * self.osr_rx)
                self.sto_idx = np.round(sto * self.used_osr / self.osr_rx).astype(int)
                drawn_packet = drawn_packet[self.sto_idx::int(self.used_osr / self.osr_rx)]

            # Apply a random CFO by multiplying with a complex exponential
            self._cfo  = np.random.uniform(self.cfo_min, self.cfo_max)
            n          = np.arange(len(drawn_packet))
            rotation   = np.exp(1j * 2 * np.pi * self._cfo * n / self.fsamp).astype(np.complex64)
            self._impaired_packet = (drawn_packet).astype(np.complex64) * rotation

        # --- Scale to the target EsN0 for this sweep step ---
        self._esn0 = self.esn0_values[self._esn0_idx]
        self._amp  = np.sqrt((self.noise_std**2) * (10 ** (self._esn0 / 10)) / self.osr_rx)

        # Advance the EsN0 index (wraps back to 0 after the last step)
        self._esn0_idx = (self._esn0_idx + 1) % self.n_esn0

        sent_packet = (self._amp * self._impaired_packet)

        return sent_packet.astype(np.complex64)


    def _draw_gap_chunk(self, given_size=None):
        """Return a zero-filled silence gap of fixed + random length."""
        if given_size is None:
            gap_len = self.zero_samples_fixed + np.random.randint(0, self.zero_samples_rand + 1)
        else:
            gap_len = given_size

        return np.zeros(gap_len, dtype=np.complex64)


    def work(self, input_items, output_items):
        """
        Stream packets separated by silence gaps into the output buffer.

        The state machine alternates between two modes:
          - Gap mode  (_in_gap=True) : fills output with zeros
          - Packet mode (_in_gap=False): fills output with the impaired packet

        Tags marking the start of each packet are attached at the first
        sample of the packet (pos==0 in packet mode).
        """
        n   = len(output_items[0])
        idx = 0

        n_written = self.nitems_written(0)

        while idx < n:
            n_sent = self._n_sent
            in_gap = self._in_gap
            pos    = self._pos
            chunk  = self._current_chunk

            # --- Stop condition: all packets have been sent ---
            if (n_sent >= self.Npackets) and (not in_gap):
                end_time   = time.time()
                total_time = end_time - self.start_time
                self.logger.info(f"Packet Generator : total exec time : {total_time:.4f} s, sent {n_sent} packets")
                return -1  # WORK_DONE

            # Copy as many samples as the output buffer and chunk both allow
            take = min(len(chunk) - pos, n - idx)
            output_items[0][idx:idx + take] = chunk[pos:pos + take]

            # --- Attach ground-truth tags at the first sample of each packet ---
            if ((not in_gap) and (pos == 0)):
                abs_offset = n_written + idx

                key_id         = pmt.intern("ID")
                key_payload_id = pmt.intern("payload_id")
                key_cfo        = pmt.intern("cfo")
                key_sto_frac   = pmt.intern("sto")
                key_offset     = pmt.intern("offset")
                key_amp        = pmt.intern("amp")
                key_esn0       = pmt.intern("esn0")

                val_id         = pmt.from_long(n_sent)
                val_payload_id = pmt.from_long(self._payload_id)
                val_cfo        = pmt.from_double(self._cfo)
                val_sto_frac   = pmt.from_double(self.sto)
                val_offset     = pmt.from_double(abs_offset)
                val_amp        = pmt.from_double(self._amp)
                val_esn0       = pmt.from_double(self._esn0)

                self.add_item_tag(0, abs_offset, key_id,         val_id)
                self.add_item_tag(0, abs_offset, key_payload_id, val_payload_id)
                self.add_item_tag(0, abs_offset, key_cfo,        val_cfo)
                self.add_item_tag(0, abs_offset, key_sto_frac,   val_sto_frac)
                self.add_item_tag(0, abs_offset, key_offset,     val_offset)
                self.add_item_tag(0, abs_offset, key_amp,        val_amp)
                self.add_item_tag(0, abs_offset, key_esn0,       val_esn0)

            idx += take
            pos += take

            # --- Chunk exhausted: transition between gap and packet modes ---
            if pos >= len(chunk):
                if in_gap:
                    # Gap finished → load the next packet
                    self._in_gap        = False
                    self._pos           = 0
                    self._current_chunk = self._draw_packet_chunk()
                else:
                    # Packet finished → load the next gap
                    self._n_sent += 1
                    self._pos     = 0
                    self._in_gap  = True
                    if (self._n_sent < self.Npackets):
                        self._current_chunk = self._draw_gap_chunk()
                    else:
                        # Last packet done: produce one more silent chunk so the
                        # scheduler keeps calling work() until WORK_DONE is returned
                        self._current_chunk = np.zeros(len(self._current_chunk), dtype=np.complex64)
            else:
                self._pos = pos

        return n
