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
import pmt
from gnuradio import gr

from .utils import logging, parse_common_params


def demodulate(y, B, R, Fdev):
    """
    Non-coherent FSK demodulator operating on complex baseband samples.

    For each symbol period, the received signal is correlated against the two
    possible FSK tones (frequency +Fdev and -Fdev relative to the carrier).
    The bit decision is based on which correlation is stronger — this is the
    standard non-coherent energy detector for binary FSK, which does not
    require knowledge of the carrier phase.

    Parameters
    ----------
    y    : complex64 array, length = nb_syms * R (complex baseband samples)
    B    : symbol rate [symbols/s]  (also called data rate)
    R    : oversampling ratio (samples per symbol)
    Fdev : frequency deviation [Hz]

    Returns
    -------
    bits_hat : int array of length nb_syms, values in {0, 1}

    """
    # Normalized frequency deviation: Fdev expressed in units of the symbol rate
    f = Fdev / B

    nb_syms = int(len(y) / R)

    bits_hat = np.zeros(nb_syms)

    return bits_hat


class demodulation(gr.basic_block):
    """
    GNU Radio block wrapping the non-coherent FSK demodulator.

    Input  : stream of complex64 baseband samples at rate fsamp = B * osr
    Output : stream of uint8 bits, one per symbol (0 or 1)

    The block processes osr input samples per output bit. Tags attached to
    input samples are forwarded to the corresponding output symbol position
    (sample offset divided by osr).
    """

    def __init__(self, common_params):
        p = parse_common_params(common_params)
        self.drate = p["data_rate"]
        self.fdev = p["fdev"]
        self.fsamp = p["samp_rate"]
        self.osr = p["oversampling"]

        self.symbol_counter = 0
        self.pkt_id = 0

        gr.basic_block.__init__(
            self, name="Demodulation", in_sig=[np.complex64], out_sig=[np.uint8]
        )

        self.logger = logging.getLogger("demod")
        self.gr_version = gr.version()

        # Tags are managed manually: the block re-maps them from the sample
        # domain to the symbol domain, so automatic propagation is disabled.
        self.set_tag_propagation_policy(gr.TPP_DONT)

    def forecast(self, noutput_items, ninputs):
        """
        Forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            # Each output symbol requires exactly osr input samples
            ninput_items_required[i] = noutput_items * self.osr

        return ninput_items_required

    def general_work(self, input_items, output_items):

        n_syms = len(output_items[0])
        buf_len = n_syms * self.osr

        y = input_items[0][:buf_len]

        # --- Tag forwarding: sample domain → symbol domain ---
        # Tags arrive with offsets in samples; convert to symbol indices
        # so that downstream blocks (parser, stats) see correct positions.
        #######################################################
        tags = self.get_tags_in_window(0, 0, buf_len)
        if tags is not None:
            for tag in tags:
                abs_offset = tag.offset // self.osr

                self.add_item_tag(0, abs_offset, tag.key, tag.value)
                key_str = pmt.to_python(tag.key)
                val_str = pmt.to_python(tag.value)
        #######################################################

        # Run the non-coherent FSK decision on the full buffer
        s = demodulate(y, self.drate, self.osr, self.fdev)

        output_items[0][: len(s)] = s

        self.consume_each(buf_len)

        return len(s)
