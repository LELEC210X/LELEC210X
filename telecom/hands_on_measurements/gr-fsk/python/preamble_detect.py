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


def preamble_detect_energy(y, L, threshold):
    """
    Preamble detection.
    """
    y_abs = np.abs(y)
    for i in range(0, int(len(y) / L)):
        sum_abs = np.sum(y_abs[i * L : (i + 1) * L])
        if sum_abs > threshold * L:
            return i * L + 20

    return None


class preamble_detect(gr.basic_block):
    """
    docstring for block preamble_detect
    """

    def __init__(self, drate, fdev, fsamp, packet_len, threshold, enable):
        self.drate = drate
        self.fdev = fdev
        self.fsamp = fsamp
        self.packet_len = packet_len  # in bytes
        self.osr = int(fsamp / drate)
        self.threshold = threshold
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

        self.gr_version = gr.version()

        # Redefine function based on version
        if LooseVersion(self.gr_version) < LooseVersion("3.9.0"):
            self.forecast = self.forecast_v38
        else:
            self.forecast = self.forecast_v310

    def forecast_v38(self, noutput_items, ninput_items_required):
        ninput_items_required[0] = max(
            noutput_items + self.filter_len, 2 * self.filter_len
        )

    def forecast_v310(self, noutput_items, ninputs):
        """
        forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            ninput_items_required[i] = max(
                noutput_items + self.filter_len, 2 * self.filter_len
            )

        return ninput_items_required

    def set_enable(self, enable):
        self.enable = enable

    def set_threshold(self, threshold):
        self.threshold = threshold

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
            N = len(output_items[0]) - len(output_items[0]) % self.filter_len
            if self.enable == 1:
                y = input_items[0][: N + self.filter_len]
                pos = preamble_detect_energy(y, self.filter_len, self.threshold)

                if (
                    pos is None
                ):  # no preamble found, we discard the processed samples (no output_items)
                    self.consume_each(N)
                    return 0
                if (
                    pos > N
                ):  # in this case, n_out below is < 0. Consume samples and recompute later
                    self.consume_each(N)
                    return 0

                # A window corresponding to the length of a full packet + 1 byte + 1 symbol
                # is transferred to the output
                self.rem_samples = 8 * self.osr * (self.packet_len + 1) + self.osr

                n_out = N - pos

                output_items[0][:n_out] = input_items[0][pos:N]
                self.consume_each(N)

                self.rem_samples -= n_out

                return n_out

            else:
                self.consume_each(N)
                return 0
