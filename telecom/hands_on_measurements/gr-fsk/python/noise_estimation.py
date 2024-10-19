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
from distutils.version import LooseVersion
from .utils import logging


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
        self.logger = logging.getLogger("noise")

        self.gr_version = gr.version()

        # Redefine function based on version
        if LooseVersion(self.gr_version) < LooseVersion("3.9.0"):
            self.forecast = self.forecast_v38
        else:
            self.forecast = self.forecast_v310

    def forecast_v38(self, noutput_items, ninput_items_required):
        ninput_items_required[0] = self.n_samples

    def forecast_v310(self, noutput_items, ninputs):
        """
        forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            ninput_items_required[i] = self.n_samples 

        return ninput_items_required

    def general_work(self, input_items, output_items):
        y = input_items[0]
        if time.time() - self.last_print >= 1.0:
            dc_offset = np.mean(y)
            self.noise_est = np.mean(np.abs(y - dc_offset) ** 2)
            self.logger.info(
                f"estimated noise power: {self.noise_est:.2e} ({10 * np.log10(self.noise_est):.2f}dB, Noise std : {np.sqrt(self.noise_est):.2e},  DC offset: {np.abs(dc_offset):.2e}, calc. on {len(y)} samples)"
            )
            self.last_print = time.time()

        self.consume_each(len(y))
        return 0
