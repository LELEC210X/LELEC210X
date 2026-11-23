import threading

import numpy as np
import pmt
from gnuradio import gr

from .utils import logging, parse_common_params

# Fixed preamble (alternating 1-0 pattern) and sync word for the sender block.
preamble = np.array([int(bit) for bit in f"{0xAAAAAAAA:0>32b}"])
sync_word = np.array([int(bit) for bit in f"{0x3E2A54B7:0>32b}"])


# ---------------------------------------------------------------------------
# Bit-reflection helper (for CRC standards requiring reflected I/O)
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
# CRC-8/SMBUS (bit-serial version)
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
# CP-FSK modulator (symbol-by-symbol version, used by packet_sender)
# ---------------------------------------------------------------------------


def modulate(bits, B, R, Fdev):
    """
    Continuous-Phase FSK modulator (symbol-by-symbol loop form).

    Builds the complex baseband waveform for `bits` at oversampling ratio R
    and bit rate B, with frequency deviation Fdev. Phase is accumulated
    across symbol boundaries to enforce the continuous-phase property.
    """
    f = Fdev / B
    h = 2 * f  # Modulation index

    x = np.zeros(len(bits) * R, dtype=np.complex64)
    ph = 2 * np.pi * np.arange(R) / R * f  # Linear phase of unmodulated symbol

    phase_shifts = np.zeros(len(bits) + 1)
    phase_shifts[0] = 0  # Initial phase
    for i, b in enumerate(bits):
        # Apply the starting phase and modulate with the linear intra-symbol ramp
        x[i * R : (i + 1) * R] = np.exp(1j * phase_shifts[i]) * np.exp(
            1j * (1 if b else -1) * ph
        )
        # Advance the phase for the next symbol (maintains continuity)
        phase_shifts[i + 1] = phase_shifts[i] + h * np.pi * (1 if b else -1)

    return x


def packet_modulate(bits, B, R, Fdev):
    """
    Modulate a full packet: prepend preamble and sync word to the data bits.

    Returns the concatenated complex baseband waveform.
    """
    x_pr = modulate(preamble, B, R, Fdev)  # Modulated signal containing preamble
    x_sync = modulate(sync_word, B, R, Fdev)  # Modulated signal containing sync_word
    x_pay = modulate(bits, B, R, Fdev)  # Modulated signal with payload

    x = np.concatenate((x_pr, x_sync, x_pay))

    return x


# ===========================================================================
# GNU Radio block: packet_sender
# ===========================================================================


class packet_sender(gr.sync_block):
    """
    Source block that streams complex zeros continuously.

    On trigger, it queues exactly one fixed-length packet to be
    emitted in place of the zeros, starting as soon as possible in
    the output stream (mid-buffer if needed). While a packet is in
    flight, further triggers are ignored (the button press is a
    no-op until the current packet has finished).

    Two ways to trigger it:
      1. Call `.trigger()` directly, e.g. from a GRC variable/
         callback field, or from an external script driving an
         automated BER-vs-SNR sweep.
      2. Wire a "QT GUI Message Push Button" block's message output
         port to this block's "trig" message input port in GRC.

    Burst mode vs. continuous mode
    -------------------------------
    In continuous mode (burst_mode=False) the block always fills its
    output with zeros between packets, keeping the GR scheduler busy.
    In burst mode the block blocks (via threading.Event) until a trigger
    arrives, so no samples are produced at all while idle — suitable for
    half-duplex SDR use where silence on the TX chain is desired.

    Parameters
    ----------

    """

    def __init__(self, common_params, burst_mode, zero_samples):
        gr.sync_block.__init__(
            self,
            name="zero_packet_source",
            in_sig=None,
            out_sig=[np.complex64],
        )
        p = parse_common_params(common_params)
        self.payload_len = p["payload_len"]
        self.drate = p["data_rate"]
        self.osr = p["oversampling"]
        self.fdev = p["fdev"]

        # Number of zero samples appended after each packet (inter-packet guard)
        self.zero_samples = zero_samples

        self.burst_mode = burst_mode

        # --- Thread-safe trigger state ---
        self._lock = threading.Lock()
        self._pending = False  # a trigger has been received but not yet acted on
        self._sending = False  # a packet is currently being streamed
        self._pos = 0  # current position within self.packet

        # --- Build the fixed payload (counter pattern 0,1,...,254,0,1,...) ---
        self.payload_bytes = (np.mod(np.arange(0, self.payload_len), 255)).astype(
            np.uint8
        )

        # Compute CRC-8/SMBUS over the payload
        self.crc = crc_poly(
            bytearray(self.payload_bytes),
            8,
            0x07,
            crc=0xFF,
            ref_in=False,
            ref_out=False,
            xor_out=0,
        )

        # --- Modulate the full packet (payload + CRC) ---
        bytes_send = np.unpackbits(
            (np.append(self.payload_bytes, self.crc)).astype(np.uint8), bitorder="big"
        )
        self.packet = np.concatenate(
            (
                packet_modulate(bytes_send, self.drate, self.osr, self.fdev),
                np.zeros(self.zero_samples),
            )
        )
        self.packet_len = len(self.packet)

        self.logger = logging.getLogger("pktSender")

        # Wakes a work() call that's blocked waiting for a trigger
        # in burst_mode; also lets stop() interrupt that wait promptly.
        self._trig_event = threading.Event()
        self._stop_requested = False

        # Message-port trigger, for a QT GUI Message Push Button
        self.message_port_register_in(pmt.intern("trig"))
        self.set_msg_handler(pmt.intern("trig"), self._on_trig_msg)

    def _on_trig_msg(self, msg):
        # Any message on this port fires a trigger, regardless of payload
        self.logger.info("Trigger Received")
        self.trigger()

    def trigger(self):
        """Request that one packet be sent at the next opportunity."""
        with self._lock:
            if not self._sending:
                self._pending = True
        self._trig_event.set()

    def stop(self):
        self._stop_requested = True
        self._trig_event.set()
        return True

    def work(self, input_items, output_items):
        """
        Fill the output buffer with zeros, interrupted by a packet burst
        whenever a trigger is pending.

        The inner loop iterates until the output buffer is full, handling
        three mutually exclusive states:
          1. Pending trigger  → arm the sending state machine
          2. Sending          → stream packet samples into the output
          3. Idle             → fill with zeros (or block in burst mode)
        """
        out = output_items[0]
        n = len(out)
        idx = 0

        while idx < n:
            with self._lock:
                sending = self._sending
                pending = self._pending
                pos = self._pos

            # --- State 1: trigger received, arm the sender ---
            if not sending and pending:
                with self._lock:
                    self._sending = True
                    self._pending = False
                    self._pos = 0
                continue

            # --- State 2: stream packet samples ---
            if sending:
                take = min(len(self.packet) - pos, n - idx)
                out[idx : idx + take] = self.packet[pos : pos + take]
                idx += take
                pos += take
                with self._lock:
                    self._pos = pos
                    if pos >= self.packet_len:
                        # Packet fully transmitted
                        self._sending = False
                        self._pos = 0
                continue

            # --- State 3: idle — no packet in flight, no pending trigger ---
            if self.burst_mode:
                if idx > 0:
                    # Deliver what we already produced this call; the
                    # scheduler will call work() again for the rest.
                    return idx
                # Block (no busy-spin) until triggered or stopped.
                self._trig_event.wait(timeout=0.05)
                self._trig_event.clear()
                if self._stop_requested:
                    return -1  # WORK_DONE
                return 0
            else:
                # Continuous mode: fill the remainder of the buffer with zeros
                out[idx:n] = 0
                idx = n

        return n
