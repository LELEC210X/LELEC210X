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


def cfo_estimation(y, B, R, Fdev, N):
    # return 0
    """
    Estimate the carrier frequency offset (CFO) using the Moose algorithm.

    Parameters
    ----------
    y    : complex64 array, length >= 2 * N * R (preamble samples)
    B    : symbol rate [symbols/s]
    R    : oversampling ratio (samples per symbol)
    Fdev : frequency deviation [Hz]
    N    : parameter of the Moose algorithm

    Returns
    -------
    cfo : estimated frequency offset in Hz

    """
    return 0


def sto_estimation(y, B, R, Fdev, sync_word):
    """
    Estimate the symbol timing offset (STO) using the phase-derivative method.

    In CP-FSK, each symbol transition produces an instantaneous frequency
    jump (a phase discontinuity in the derivative of the unwrapped phase).
    These jumps are maximally aligned with the true symbol boundaries, so
    summing the second derivative of the phase at every R-th sample and
    scanning the R possible offsets reveals the optimal sampling instant.

    Parameters
    ----------
    y        : complex64 array (CFO-corrected preamble)
    B, R, Fdev : system parameters
    sync_word  : unused here, kept for API consistency

    Returns
    -------
    sto : estimated timing offset in samples (integer in [0, R))

    """
    phase_function = np.unwrap(np.angle(y))
    phase_derivative_sign = phase_function[1:] - phase_function[:-1]
    # Second derivative: peaks at instants where instantaneous frequency changes sign
    sign_derivative = np.abs(phase_derivative_sign[1:] - phase_derivative_sign[:-1])

    sum_der_saved = -np.inf
    save_i = 0

    # Test all R candidate sampling phases; pick the one that aligns most transitions
    for i in range(R):
        sum_der = np.sum(sign_derivative[i::R])

        if sum_der > sum_der_saved:
            sum_der_saved = sum_der
            save_i = i

    return np.mod(save_i + 1, R)


class synchronization(gr.basic_block):
    """
    GNU Radio block performing CFO and STO estimation and correction.

    The block processes one packet at a time and operates in two phases:

    Phase 1 — Header processing (rem_samples == 0):
        Called once per new packet. Reads the preamble/header samples and:
        - Optionally applies a known coarse CFO pre-correction before estimation.
        - Estimates the residual CFO with the Moose algorithm (enable_Moose).
        - Estimates the symbol timing offset with the phase-derivative method (enable_STO_est).
        - Estimates received signal power (excluding the first and last symbol).
        - Attaches all estimates as tags (est_cfo, est_sto, est_sig_pow) for downstream blocks.
        Returns 0 (no output yet); the STO samples are consumed to align the stream.

    Phase 2 — CFO-corrected passthrough (rem_samples > 0):
        Streams the remaining packet samples to the output after applying a
        sample-by-sample CFO correction: y_corr[n] = y[n] * exp(-j*2π*cfo*t[n]).
        The time axis t is maintained across work() calls so the phase is continuous.
        When the last chunk is emitted, osr-sto extra samples are discarded to
        undo the sub-symbol timing shift introduced by the preamble detector.

    Input  : complex64 stream (packet samples from preamble_detect)
    Output : complex64 stream (CFO-corrected packet samples, header stripped)
    """

    def __init__(
        self, common_params, enable_STO_est, enable_Moose, N_Moose, cfo_precorrection
    ):
        p = parse_common_params(common_params)
        self.drate = p["data_rate"]
        self.fdev = p["fdev"]
        self.fsamp = p["samp_rate"]
        self.osr = p["oversampling"]
        self.hdr_len = p["hdr_len"]
        self.packet_len = p["packet_len"]  # in bytes
        self.sync_word = p["sync_word"]  # in bytes
        self.estimated_noise_power = None
        self.N_Moose = N_Moose
        self.enable_Moose = enable_Moose
        self.enable_STO_est = enable_STO_est
        self.cfo_precorrection = cfo_precorrection

        self.nb_packet = 0
        self.pkt_id = 0
        self.rec_pkt_id = 0

        # Total samples per packet transmitted by the upstream preamble_detect block
        self.samples_to_pass = (self.packet_len + 1) * 8 * self.osr
        # Remaining number of samples in the current packet
        self.rem_samples = 0
        self.sto = 0
        self.cfo = 0.0
        # Continuous time reference maintained across work() calls for CFO rotation
        self.t0 = 0.0
        self.estimated_signal_power = 0

        # Pre-computed time axis (in seconds) for the CFO rotation phasor
        self.ramp = np.arange(0, self.samples_to_pass) / (self.drate * self.osr)

        gr.basic_block.__init__(
            self, name="Synchronization", in_sig=[np.complex64], out_sig=[np.complex64]
        )
        self.logger = logging.getLogger("sync")

        self.gr_version = gr.version()

        # Tags are manually forwarded; automatic propagation is disabled
        self.set_tag_propagation_policy(gr.TPP_DONT)

    def forecast(self, noutput_items, ninputs):
        """
        Forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            if self.rem_samples == 0:  # looking for a new packet
                ninput_items_required[i] = self.hdr_len * 8 * self.osr
            else:  # processing a previously found packet
                # pass remaining samples in packet to next block; the last chunk
                # also discards osr - sto extra samples, which must be available.
                # Never ask for more than what remains of the packet, or the last
                # chunk would wait for the next packet to be detected.
                ninput_items_required[i] = (
                    min(noutput_items, self.rem_samples) + self.osr - self.sto
                )
        return ninput_items_required

    def stop(self):
        self.logger.info(f"[SYNC] {self.nb_packet} packets detected")
        return True

    def general_work(self, input_items, output_items):

        x = input_items[0][:]

        # =====================================================================
        # PHASE 1: New packet — estimate CFO and STO from the preamble/header
        # =====================================================================
        if self.rem_samples == 0:
            self.cfo = 0
            self.sto = 0

            # --- Read upstream tags at the packet boundary ---
            # detection_latency (from preamble_detect) gives a coarse STO estimate
            # when Moose/STO estimators are disabled; "cfo" carries a hardware
            # pre-estimate (e.g. from a crystal offset calibration).
            #######################################################
            offset = 0
            tags = self.get_tags_in_window(0, 0, 1)
            for tag in tags:
                if (pmt.to_python(tag.key) == "detection_latency") and (
                    self.enable_STO_est == 0
                ):
                    # Convert detection latency to a sub-symbol timing correction
                    self.sto = (
                        (self.osr) - (pmt.to_python(tag.value) % (self.osr))
                    ) % (self.osr)

                if (pmt.to_python(tag.key) == "cfo") and (self.enable_Moose == 0):
                    self.cfo = pmt.to_python(tag.value)
            #######################################################

            # --- Estimate CFO and STO on the preamble samples ---
            self.nb_packet += 1

            n_preamble_samples = self.hdr_len * 8 * self.osr
            y = input_items[0][offset:n_preamble_samples]

            if self.enable_Moose:
                # Pre-correction: remove known coarse offset before the Moose estimator
                # so its unambiguous range is centred on the residual error.
                y_pre_corrected = y * np.exp(
                    -1j * 2 * np.pi * self.cfo_precorrection * self.ramp[: len(y)]
                )
                self.cfo = self.cfo_precorrection + cfo_estimation(
                    y_pre_corrected, self.drate, self.osr, self.fdev, self.N_Moose
                )

            if self.enable_STO_est:
                # CFO-correct the preamble before STO estimation to avoid frequency
                # offsets biasing the phase-derivative metric.
                y_cfo = y * np.exp(-1j * 2 * np.pi * self.cfo * self.ramp[: len(y)])
                self.sto = int(
                    sto_estimation(
                        y_cfo, self.drate, self.osr, self.fdev, self.sync_word
                    )
                )

            # --- Signal power estimation ---
            # Computed on the packet body (excluding first and last symbol guard),
            # used by packet_stats to compute the per-packet SNR estimate.
            y_power = x[
                (8 * self.osr) : min(len(x), self.samples_to_pass) - (8 * self.osr)
            ]
            self.estimated_signal_power = (
                np.dot(y_power, y_power.conj()).real / y_power.size
            )

            if self.estimated_signal_power is None:
                self.logger.info("[SYNC] Power estimation error is None")
            elif self.estimated_signal_power <= 0:
                self.logger.info(
                    f"[SYNC] Power estimation error {self.estimated_signal_power:.6f} "
                )

            # --- Attach estimation results as tags ---
            # abs_offset is a monotonically increasing output position counter
            # used to anchor tags for downstream blocks.
            #######################################################
            abs_offset = self.pkt_id * self.samples_to_pass
            self.pkt_id += 1

            # Forward upstream tags (ground truth from simulator, noise power, …)
            for tag in tags:
                self.add_item_tag(0, abs_offset, tag.key, tag.value)

            key_sig = pmt.intern("est_sig_pow")
            key_cfo = pmt.intern("est_cfo")
            key_sto = pmt.intern("est_sto")
            val_sig = pmt.from_double(self.estimated_signal_power)
            val_cfo = pmt.from_double(self.cfo)
            val_sto = pmt.from_long(self.sto)
            self.add_item_tag(0, abs_offset, key_sig, val_sig)
            self.add_item_tag(0, abs_offset, key_cfo, val_cfo)
            self.add_item_tag(0, abs_offset, key_sto, val_sto)
            #######################################################

            self.rem_samples = self.samples_to_pass
            self.t0 = 0

            # Consume the STO fractional samples to align the output stream
            # to the nearest symbol boundary before entering passthrough mode.
            self.consume_each(self.sto)
            return 0

        # =====================================================================
        # PHASE 2: Passthrough with per-sample CFO frequency correction
        # =====================================================================
        else:
            win_size = min(len(output_items[0]), self.rem_samples)

            # Advance the continuous time axis; t[0] starts one sample after t0
            # to avoid applying t=0 (zero rotation) at a packet boundary.
            t = self.t0 + np.arange(1, win_size + 1) / (self.drate * self.osr)
            self.t0 = t[-1]

            # Apply the CFO correction phasor: rotate each sample by -2π*cfo*t
            # to bring the carrier back to DC in the demodulated baseband.
            y_corr = (x[:win_size]) * np.exp(-1j * 2 * np.pi * self.cfo * t)

            output_items[0][:win_size] = y_corr

            self.rem_samples -= win_size

            if (
                self.rem_samples == 0
            ):  # Throw away the extra OSR samples from the preamble detection stage
                self.consume_each(win_size + self.osr - self.sto)
            else:
                self.consume_each(win_size)

            return win_size
