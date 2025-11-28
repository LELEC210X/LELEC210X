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
    """Non-coherent demodulator."""
    nb_syms = len(y) // R  # Number of CPFSK symbols in y

    # Group symbols together, in a matrix.
    # Each row contains the R samples over one symbol period
    y = np.resize(y, (nb_syms, R))

    # === TO DO: generate the reference waveforms used for the correlation ===
    fd = Fdev       # frequency deviation Δf
    T = 1.0 / B              # symbol period

    # For n = 0...R-1, generate reference signals for bits "0" and "1"
    n = np.arange(R)
    ref1 = np.exp(-1j * 2 * np.pi * fd * n * T / R)  # waveform for bit=1
    ref0 = np.exp(+1j * 2 * np.pi * fd * n * T / R)  # waveform for bit=0

    # === TO DO: compute the correlations with the two reference waveforms (r0 and r1) ===
    # vectorized correlation: compute dot product of each row with ref1/ref0
    # y has shape (nb_syms, R), ref* has shape (R,)
    # result r1_vec[k] = sum_j y[k,j] * ref1[j]
    r1_vec = (y * ref1).sum(axis=1) / R
    r0_vec = (y * ref0).sum(axis=1) / R

    # Decide based on magnitude comparison
    bits_hat = (np.abs(r1_vec) > np.abs(r0_vec)).astype(int)

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

    def forecast(self, noutput_items, ninputs):
        """
        Forecast is only called from a general block
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
