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
import pmt
from gnuradio import gr

from .utils import logging


class onQuery_noise_estimation(gr.basic_block):
    """
    On-demand noise power estimator for the SDR receive chain.

    This block acts as a sink (no output signal) that normally discards all
    incoming samples. When triggered by a call to query_estimation(), it
    switches into estimation mode: it accumulates n_est batches of n_samples
    each, computes the noise power (variance of the complex baseband signal)
    for each batch, averages them, and publishes the final estimate on the
    "NoisePow" message port as a PMT double.

    The variance of a zero-mean complex baseband signal equals the total noise
    power N0 * Bf, where Bf is the receiver bandwidth. The preamble_detect block
    reads this estimate back via its own n0Bf attribute and attaches it to each
    detected packet as an "est_noise_power" tag, enabling per-packet SNR estimation
    in packet_stats.

    Estimation should be triggered only when no signal is present (between packets),
    so that the receiver is measuring noise alone.

    Input  : complex64 stream (baseband samples from the receiver front-end)
    Output : none (sink block); result is published on message port "NoisePow"
    """

    def query_estimation(self, query):
        """
        Trigger the noise estimation process.

        Call this method (e.g., from a GRC callback or a GUI button) when the
        channel is idle. Setting query=1 arms the estimator so that the next
        n_est * n_samples incoming samples are used for the measurement.
        """
        if query == 1:
            self.est_counter = 1
            self.mean_noise_est = 0
            self.do_a_query = 1

    def __init__(self, n_samples, n_est, query, osr):
        self.osr = osr
        self.n_samples = n_samples  # samples per estimation batch
        self.n_est = n_est          # number of batches to average
        self.mean_noise_est = 0
        self.est_counter = 1
        self.noise_est = None
        self.do_a_query = 0
        self.last_print = 0.0

        gr.basic_block.__init__(
            self, name="Noise Estimation", in_sig=[np.complex64], out_sig=None
        )
        self.logger = logging.getLogger("noise")
        # Output message port: publishes the averaged noise power estimate
        self.message_port_register_out(pmt.intern("NoisePow"))

        self.gr_version = gr.version()

    def forecast(self, noutput_items, ninputs):
        """
        Forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            ninput_items_required[i] = self.n_samples

        return ninput_items_required

    def general_work(self, input_items, output_items):

        # --- Passthrough mode: no estimation requested ---
        # Simply discard all incoming samples to keep the GR scheduler running.
        if self.do_a_query == 0:
            self.consume_each(len(input_items[0]))

        # --- Estimation mode: measure noise power from current batch ---
        else:
            y = input_items[0]
            dc_offset = np.mean(y)
            # Noise power = variance of the complex baseband signal.
            # For a zero-mean process this equals E[|y|^2].
            # np.var computes E[|y - mean(y)|^2], which also removes any residual DC offset.
            self.noise_est = np.var(y)
            self.consume_each(len(y))
            self.mean_noise_est = self.mean_noise_est + self.noise_est
            self.logger.info(
                f"estimated noise power: {self.noise_est:.2e} ({10 * np.log10(self.noise_est):.2f}dB, Noise std : {np.sqrt(self.noise_est):.2e},  DC offset: {np.abs(dc_offset):.2e}, calc. on {len(y)} samples)"
            )

            if self.est_counter == self.n_est:
                # All n_est batches collected: publish the averaged estimate
                mean_noisP = self.mean_noise_est / self.est_counter
                PMT_msg = pmt.from_double(mean_noisP)
                # Publish on "NoisePow" so that preamble_detect (or any other
                # subscribed block) can receive the estimate via message passing.
                self.message_port_pub(pmt.intern("NoisePow"), PMT_msg)

                self.logger.info(
                    f"===== > Final estimated noise power: {mean_noisP:.2e} ({10 * np.log10(mean_noisP):.2f}dB, Noise std : {np.sqrt(mean_noisP):.2e})"
                )
                # Reset state; arm again only on the next query_estimation() call
                self.est_counter = 1
                self.mean_noise_est = 0
                self.do_a_query = 0

            else:
                # More batches needed: increment counter and wait for next call
                self.est_counter = self.est_counter + 1

        return 0
