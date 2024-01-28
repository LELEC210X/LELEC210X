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


import time

import numpy as np
from gnuradio import gr


class noise_estimation(gr.basic_block):
    """
    docstring for block noise_estimation
    """

    def __init__(self, n_samples):
        self.n_samples = n_samples
        self.noise_est = None
        self.last_print = 0.0

        gr.basic_block.__init__(
            self, name="Noise Estimation", in_sig=[np.complex64], out_sig=None
        )

    def forecast(self, noutput_items, ninput_items_required):
        ninput_items_required[0] = self.n_samples

    def general_work(self, input_items, output_items):
        y = input_items[0]
        if time.time() - self.last_print >= 1.0:
            self.noise_est = np.mean(np.abs(y) ** 2)
            print(
                "[NOISE] Estimated noise power: {} ({}dB, {} samples)".format(
                    self.noise_est, 10 * np.log10(self.noise_est), len(y)
                )
            )
            self.last_print = time.time()

        self.consume_each(len(y))
        return 0
