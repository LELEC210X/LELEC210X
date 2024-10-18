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

import numpy as np
from gnuradio import gr


def demodulate(y, B, R, Fdev):
    """
    Non-coherent demodulator.
    """
    nb_syms = len(y) // R  # Number of CPFSK symbols in y

    # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
    y = np.resize(y, (nb_syms, R))

    # TO DO: generate the reference waveforms used for the correlation
    # hint: look at what is done in modulate() in chain.py
    f = Fdev / B
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

    #def forecast(self, noutput_items, ninputs):
    #    """
    #    forecast is only called from a general block
    #    this is the default implementation
    #    """
    #    ninput_items_required = [0] * ninputs
    #    for i in range(ninputs):
    #        ninput_items_required[i] = noutput_items + \
    #            self.gateway.history() - 1
    #    return ninput_items_required

    def forecast(self, noutput_items, ninputs):
        """
        forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            ninput_items_required[i] = noutput_items * self.osr * 8

        return ninput_items_required
    
#    def forecast(self, noutput_items, ninput_items_required):
#        """
#        input items are samples (with oversampling factor)
#        output items are bytes
#        """
#        ninput_items_required[0] = noutput_items * self.osr * 8

    def general_work(self, input_items, output_items):
        n_syms = len(output_items[0]) * 8
        buf_len = n_syms * self.osr

        y = input_items[0][:buf_len]
        self.consume_each(buf_len)

        s = demodulate(y, self.drate, self.osr, self.fdev)
        b = self.symbols_to_bytes(s)
        output_items[0][: len(b)] = b

        return len(b)
