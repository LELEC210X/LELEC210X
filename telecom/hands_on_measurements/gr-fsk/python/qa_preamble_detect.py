#!/usr/bin/env python
#
# Copyright 2021 UCLouvain.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import matplotlib.pyplot as plt
import numpy as np
from gnuradio import blocks, gr, gr_unittest
from preamble_detect import preamble_detect


def gr_cast(x):
    return [complex(z) for z in x]


class qa_preamble_detect(gr_unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_001_t(self):
        fsamp = 400e3
        drate = 50e3
        fdev = drate / 2
        packet_len = 509

        y = np.fromfile("../misc/fsk_trace.mat", dtype=np.complex64)
        y = y * 2
        int(fsamp / drate)
        t = np.arange(len(y)) / fsamp
        cfo_fix = 14750
        y = y * np.exp(-1j * 2 * np.pi * cfo_fix * t)

        tb = gr.top_block()

        source = blocks.vector_source_c(gr_cast(y))
        detector = preamble_detect(drate, fdev, fsamp, packet_len)
        sink = blocks.vector_sink_c()

        tb.connect(source, detector)
        tb.connect(detector, sink)

        tb.run()
        y_out = sink.data()
        tb.stop()

        plt.plot(np.abs(y))
        plt.show()
        plt.plot(np.abs(y_out))
        plt.show()

        """
        hdr_len = 8 * 8 * int(fsamp / drate)
        y_pr = y_out[:hdr_len]
        sync_word = [0,1] * 16
        sto, cfo = sync_moose(y_pr, drate, int(fsamp / drate), fdev, sync_word) # ... estimate the offsets
        print(sto, cfo)
        """


def mod_cpfsk(bits, B, R, Fdev):
    f = Fdev / B
    h = 2 * f  # Modulation index

    x = np.zeros(len(bits) * R, dtype=np.complex64)
    ph = 2 * np.pi * np.arange(R) / R * f  # Linear phase of unmodulated symbol

    phase_shifts = np.zeros(len(bits) + 1)
    phase_shifts[0] = 0  # Initial phase
    for i, b in enumerate(bits):
        x[i * R : (i + 1) * R] = np.exp(1j * phase_shifts[i]) * np.exp(
            1j * (1 if b else -1) * ph
        )
        phase_shifts[i + 1] = phase_shifts[i] + h * np.pi * (
            1 if b else -1
        )  # Update phase to start with for next symbol

    return x


def sync_moose(y, B, R, Fdev, addr):
    # CFO estimation
    N = 4
    b1, b2 = y[0 : N * R], y[N * R : 2 * N * R]

    r = np.sum(b2 * np.conj(b1)) / (N * R)
    cfo_hat = np.angle(r) / (2 * np.pi * N * R) * (B * R)

    # STO estimation
    x_addr = mod_cpfsk(addr, B, R, Fdev)

    t = np.arange(len(y)) / (B * R)
    y_cfo = np.exp(-1j * 2 * np.pi * cfo_hat * t) * y

    v = np.abs(np.correlate(y_cfo, x_addr, mode="valid"))
    addr_idx = np.argmax(v) + len(x_addr)

    plt.plot(np.real(y))
    plt.plot(np.imag(y))
    plt.show()

    fig, axs = plt.subplots(3)
    axs[0].plot(v)
    axs[1].plot(np.angle(y_cfo))
    axs[2].plot(np.abs(y_cfo))
    plt.show()

    fig, axs = plt.subplots(2)
    axs[0].plot(np.real(y_cfo))
    axs[1].plot(np.imag(y_cfo))
    plt.show()

    return addr_idx, cfo_hat


if __name__ == "__main__":
    gr_unittest.run(qa_preamble_detect)
