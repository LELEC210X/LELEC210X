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

from distutils.version import LooseVersion

import numpy as np
from gnuradio import gr


def demodulate(y, B, R, Fdev):
    """
    Demodulates the received signal.
    Non-coherent demodulator.
    
    :param y: The received signal, (N * R,).
    :param B: Bitrate [bits/sec]
    :param R: oversample factor (typically = 8)
    :param Fdev: Frequency deviation [Hz] ( = Bitrate/4)
    :return: The signal, after demodulation.
    """
    N = len(y) // R  # Number of CPFSK symbols in y
    T = 1 / B # 1/B
    

    # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
    y = np.resize(y, (N, R))

    # generate the reference waveforms used for the correlation
    e_0 = np.exp(-1j * 2 * np.pi * Fdev * np.arange(R) * T / R)
    e_1 = np.exp(1j * 2 * np.pi * Fdev * np.arange(R) * T / R)

    # compute the correlations with the two reference waveforms (r0 and r1)
    r0 = np.dot(y, np.conj(e_0)) / T
    r1 = np.dot(y, np.conj(e_1)) / T
    
    # perform the decision based on r0 and r1
    bits_hat = (np.abs(r1) > np.abs(r0)).astype(int)
    
    return bits_hat


class demodulation(gr.basic_block):
    """
    docstring for block demodulation
    """

    def __init__(self, drate, fdev, fsamp, payload_len, crc_len):
        self.drate = drate
        self.fdev = fdev
        self.fsamp = fsamp
        self.frame_len = payload_len + crc_len
        self.osr = int(fsamp / drate)

        gr.basic_block.__init__(
            self, name="Demodulation", in_sig=[np.complex64], out_sig=[np.uint8]
        )

        self.gr_version = gr.version()

        # Redefine function based on version
        if LooseVersion(self.gr_version) < LooseVersion("3.9.0"):
            print("Compiling the Python codes for GNU Radio 3.8")
            self.forecast = self.forecast_v38
        else:
            print("Compiling the Python codes for GNU Radio 3.10")
            self.forecast = self.forecast_v310

    def forecast_v38(self, noutput_items, ninput_items_required):
        """
        input items are samples (with oversampling factor)
        output items are bytes
        """
        ninput_items_required[0] = noutput_items * self.osr * 8

    def forecast_v310(self, noutput_items, ninputs):
        """
        forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            ninput_items_required[i] = noutput_items * self.osr * 8

        return ninput_items_required

    def symbols_to_bytes(self, symbols):
        """
        Converts symbols (bits here) to bytes
        """
        if len(symbols) == 0:
            return []

        n_bytes = int(len(symbols) / 8)
        bitlists = np.array_split(symbols, n_bytes)
        out = np.zeros(n_bytes).astype(np.uint8)

        for i, l in enumerate(bitlists):
            for bit in l:
                out[i] = (out[i] << 1) | bit

        return out

    def general_work(self, input_items, output_items):
        n_syms = len(output_items[0]) * 8
        buf_len = n_syms * self.osr

        y = input_items[0][:buf_len]
        self.consume_each(buf_len)

        s = demodulate(y, self.drate, self.osr, self.fdev)
        b = self.symbols_to_bytes(s)
        output_items[0][: len(b)] = b

        return len(b)
