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

from .utils import logging


class onQuery_noise_estimation(gr.basic_block):
    """
    docstring for block onQuery_noise_estimation
    """

    def query_estimation(self,query):
        self.do_a_query = query

    def __init__(self, n_samples, query):
        self.n_samples = n_samples
        self.noise_est = None
        self.do_a_query = 0
        self.last_print = 0.0

        gr.basic_block.__init__(
            self, name="Noise Estimation", in_sig=[np.complex64], out_sig=None
        )
        self.logger = logging.getLogger("noise")

    def forecast(self, noutput_items, ninput_items_required):
        ninput_items_required[0] = self.n_samples 

    def general_work(self, input_items, output_items):
        if (not self.do_a_query) : 
            self.consume_each(len(input_items[0]))
        else : 
            y = input_items[0]
            self.do_a_query = 0
            dc_offset = np.mean(y)
            self.noise_est = np.mean(np.abs(y - dc_offset) ** 2)
            self.consume_each(len(y))

            self.logger.info(
                f"estimated noise power: {self.noise_est:.2e} ({10 * np.log10(self.noise_est):.2f}dB, Noise std : {np.sqrt(self.noise_est):.2e},  DC offset: {np.abs(dc_offset):.2e}, calc. on {len(y)} samples)"
            )

        return 0
