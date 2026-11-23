import collections
import socket
import threading

import numpy as np
from gnuradio import gr


class tcp_source(gr.sync_block):
    """
    TCP source reading interleaved int16 I/Q samples and outputting complex64.

    Cross-platform (Windows/Linux) replacement for network.tcp_source +
    interleaved_short_to_complex, fused into one block with a background
    reader thread so socket I/O never blocks the GR scheduler.

    The hardware (e.g., AT86RF215 on the LELEC210X board) streams raw I/Q data
    over a TCP connection as pairs of 16-bit integers: [I0, Q0, I1, Q1, …].
    Each pair represents one complex baseband sample. This block:
      1. Maintains a background thread (_net_loop) that continuously reads raw
         bytes from the socket into a deque (producer side).
      2. In work(), drains the deque into a contiguous buffer (consumer side),
         converts int16 pairs to float32, assembles complex64 samples, and
         applies an optional amplitude scale factor.

    The deque acts as a lock-protected FIFO between the network thread and the
    GR scheduler thread. Its maximum size (_max_buffered) limits memory use and
    triggers oldest-data dropping if the GR graph cannot keep up.

    Parameters
    ----------
    host       : IP address of the hardware streaming server
    port       : TCP port
    scale      : divide I and Q values by this factor (ADC full-scale normalization)
    swap_iq    : swap I and Q channels if the hardware wiring is inverted
    big_endian : use big-endian byte order for the int16 samples

    """

    def __init__(
        self, host="192.168.1.2", port=2103, scale=1, swap_iq=False, big_endian=False
    ):
        gr.sync_block.__init__(
            self, name="LELEC210X_tcp_source", in_sig=None, out_sig=[np.complex64]
        )
        self._host = host
        self._port = port
        self._scale = scale
        self._swap_iq = swap_iq
        # np dtype carries the byte order, so frombuffer() does the endianness
        # swap as part of the read itself, no separate pass over the data.
        self._dtype = np.dtype(np.int16).newbyteorder(">" if big_endian else "<")

        self._sock = None
        self._thread = None
        self._stop = threading.Event()

        # Condition variable protecting the deque; work() waits on it when empty
        self._cond = threading.Condition()
        self._chunks = collections.deque()  # deque of raw byte chunks from the network
        self._chunks_len = 0  # total bytes currently buffered
        self._max_buffered = 1 << 22  # 4 MiB soft cap to bound memory usage

    def start(self):
        self._sock = socket.create_connection((self._host, self._port))
        self._stop.clear()
        # Start the producer thread as a daemon so it exits automatically
        # when the main process ends.
        self._thread = threading.Thread(target=self._net_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._stop.set()
        if self._sock is not None:
            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._sock.close()
        with self._cond:
            self._cond.notify_all()  # wake up work() immediately if it's waiting
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        return True

    def _net_loop(self):
        """
        Producer thread: reads raw bytes from the TCP socket and appends them
        to the deque. If the buffer exceeds _max_buffered, the oldest chunks
        are dropped to prevent unbounded memory growth (the GR graph is too slow).
        """
        while not self._stop.is_set():
            try:
                data = self._sock.recv(65536)
            except OSError:
                break
            if not data:
                break
            with self._cond:
                self._chunks.append(data)
                self._chunks_len += len(data)
                # Backpressure: drop old data if the consumer (work()) is lagging
                while self._chunks_len > self._max_buffered:
                    dropped = self._chunks.popleft()
                    self._chunks_len -= len(dropped)
                self._cond.notify()

    def _take_bytes_locked(self, nbytes):
        """
        Consumer-side helper: drain up to nbytes from the deque into a contiguous
        buffer (called with self._cond held).

        The returned length is aligned down to a multiple of 4 bytes because one
        I/Q sample is exactly 4 bytes (2 bytes I + 2 bytes Q). Returning a partial
        sample would corrupt the int16 unpacking in work().
        """
        n = min(nbytes, self._chunks_len)
        n -= n % 4  # align to one complete I/Q pair (4 bytes)
        if n == 0:
            return b""
        out = bytearray(n)
        filled = 0
        while filled < n:
            chunk = self._chunks[0]
            take = min(len(chunk), n - filled)
            out[filled : filled + take] = chunk[:take]
            filled += take
            if take == len(chunk):
                self._chunks.popleft()
            else:
                self._chunks[0] = chunk[take:]
        self._chunks_len -= n
        return bytes(out)

    def work(self, input_items, output_items):
        """
        Convert raw int16 interleaved I/Q bytes to complex64 samples.

        Each output sample requires 4 input bytes: [I_lo, I_hi, Q_lo, Q_hi]
        (little-endian) or [I_hi, I_lo, Q_hi, Q_lo] (big-endian). After unpacking
        to float32, the samples are scaled by 1/scale and assembled into complex64.
        If no data is available yet, work() briefly sleeps on the condition variable
        instead of busy-spinning to avoid wasting CPU in the GR scheduler.
        """
        out = output_items[0]
        need = 4 * len(out)  # bytes needed for a full output buffer

        with self._cond:
            raw = self._take_bytes_locked(need)
            if not raw and not self._stop.is_set():
                # nothing available: sleep here instead of spinning in the scheduler
                self._cond.wait(timeout=0.05)
                raw = self._take_bytes_locked(need)

        if not raw:
            return 0

        # Unpack interleaved int16 pairs to float32, then reshape to (N, 2) columns [I, Q]
        shorts = np.frombuffer(raw, dtype=self._dtype).astype(np.float32).reshape(-1, 2)
        i, q = (
            (shorts[:, 1], shorts[:, 0])
            if self._swap_iq
            else (shorts[:, 0], shorts[:, 1])
        )

        n_out = i.shape[0]
        # Assemble complex64 and normalize to [-1, +1] using the provided scale factor
        out[:n_out] = (i + 1j * q) / (self._scale)
        return n_out
