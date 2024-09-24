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


class flag_detector(gr.basic_block):
    """
    docstring for block flag_detector
    """

    def __init__(self, drate, fsamp, packet_len, enable):
        self.drate = drate
        self.fsamp = fsamp
        self.packet_len = packet_len  # in bytes
        self.osr = int(fsamp / drate)
        self.rem_samples = 0
        self.flag = 0.95
        self.enable = enable

        self.filter_len = (
            8 * self.osr
        )  # Number of samples ahead that the block needs to read to output a sample
        # Remaining number of samples that go to output when the block is
        # transparent (i.e., when a preamble is detected)
        self.rem_samples = 0

        gr.basic_block.__init__(
            self,
            name="Preamble detection",
            in_sig=[np.complex64],
            out_sig=[np.complex64],
        )

    def forecast(self, noutput_items, ninput_items_required):
        """
        input items are samples (with oversampling factor)
        output items are samples (with oversampling factor)
        """
        ninput_items_required[0] = noutput_items

    def general_work(self, input_items, output_items):
        if self.rem_samples > 0:  # We are processing a previously detected packet
            N = len(output_items[0])  # available space at output
            n_out = min(self.rem_samples, N)

            # the block is transparent, i.e., all input goes to output
            output_items[0][:n_out] = input_items[0][:n_out]
            self.consume_each(n_out)

            self.rem_samples -= n_out
            return n_out
        else:
            N = len(output_items[0])
            y = input_items[0][:N]

            if self.enable == 1:
                pos = np.argmax(np.real(y))
                if np.real(y[pos]) < self.flag or np.imag(y[pos]) < self.flag:
                    pos = None
                else:
                    pos = pos + 1

            else:
                pos = 0

            if (
                pos is None
            ):  # no preamble found, we discard the processed samples (no output_items)
                self.consume_each(N)
                return 0

            # A window corresponding to the length of a full packet + 1 byte + 1 symbol
            # is transferred to the output
            self.rem_samples = 8 * self.osr * (self.packet_len + 1) + self.osr

            n_out = min(N - pos, self.rem_samples)
            output_items[0][:n_out] = input_items[0][pos : (pos + n_out)]
            self.consume_each(N)

            self.rem_samples -= n_out
            return n_out
