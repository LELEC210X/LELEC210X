#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


def cfo_estimation(y, B, R, Fdev):
    """
    Estimate CFO using Moose algorithm, on first samples of preamble
    """
    raise NotImplementedError


def sto_estimation(y, B, R, Fdev):
    """
    Estimate symbol timing (fractional) based on phase shifts
    """
    phase_function = np.unwrap(np.angle(y))
    phase_derivative_sign = phase_function[1:] - phase_function[:-1]
    sign_derivative = np.abs(phase_derivative_sign[1:] - phase_derivative_sign[:-1])

    sum_der_saved = -np.inf
    save_i = 0

    for i in range(0, R):
        sum_der = np.sum(sign_derivative[i::R])

        if sum_der > sum_der_saved:
            sum_der_saved = sum_der
            save_i = i

    return np.mod(save_i + 1, R)


class synchronization(gr.basic_block):
    """
    docstring for block synchronization
    """

    def __init__(self, drate, fdev, fsamp, hdr_len, packet_len, estimated_noise_power):
        self.drate = drate
        self.fdev = fdev
        self.fsamp = fsamp
        self.osr = int(fsamp / drate)
        self.hdr_len = hdr_len
        self.packet_len = packet_len  # in bytes
        self.estimated_noise_power = estimated_noise_power

        # Remaining number of samples in the current packet
        self.rem_samples = 0
        self.init_sto = 0
        self.cfo = 0.0
        self.t0 = 0.0
        self.power_est = None

        gr.basic_block.__init__(
            self, name="Synchronization", in_sig=[np.complex64], out_sig=[np.complex64]
        )

    def forecast(self, noutput_items, ninput_items_required):
        """
        input items are samples (with oversampling factor)
        output items are samples (with oversampling factor)
        """
        if self.rem_samples == 0:  # looking for a new packet
            ninput_items_required[0] = (
                self.hdr_len * 8 * self.osr
            )  # enough samples to find a header inside
        else:  # processing a previously found packet
            ninput_items_required[
                0
            ] = noutput_items  # pass remaining samples in packet to next block

    def general_work(self, input_items, output_items):
        if self.rem_samples == 0:  # new packet to process, compute the CFO and STO
            y = input_items[0][: self.hdr_len * 8 * self.osr]
            self.cfo = cfo_estimation(y, self.drate, self.osr, self.fdev)

            # Correct CFO in preamble
            t = np.arange(len(y)) / (self.drate * self.osr)
            y_cfo = np.exp(-1j * 2 * np.pi * self.cfo * t) * y
            self.t0 = t[-1]

            sto = sto_estimation(y_cfo, self.drate, self.osr, self.fdev)

            self.init_sto = sto
            self.power_est = None
            self.rem_samples = (self.packet_len + 1) * 8 * self.osr
            print(
                "[SYNC] New preamble detected @ {} (CFO {:.2f} Hz, STO {})".format(
                    self.nitems_read(0) + sto, self.cfo, sto
                )
            )

            self.consume_each(sto)  # drop *sto* samples to align the buffer
            return 0  # ... but we do not transmit data to the demodulation stage
        else:
            win_size = min(len(output_items[0]), self.rem_samples)
            y = input_items[0][:win_size]

            if self.power_est is None and win_size >= 256:
                self.power_est = np.mean(np.abs(y) ** 2)
                SNR_est = (
                    self.power_est - self.estimated_noise_power
                ) / self.estimated_noise_power
                print(
                    "[SYNC] Estimated SNR: {:.2f} dB ({} samples)".format(
                        10 * np.log10(SNR_est), len(y)
                    )
                )

            # Correct CFO before transferring samples to demodulation stage
            t = self.t0 + np.arange(1, len(y) + 1) / (self.drate * self.osr)
            y_corr = np.exp(-1j * 2 * np.pi * self.cfo * t) * y
            self.t0 = t[
                -1
            ]  # we keep the CFO correction continuous across buffer chunks

            output_items[0][:win_size] = y_corr

            self.rem_samples -= win_size
            if (
                self.rem_samples == 0
            ):  # Thow away the extra OSR samples from the preamble detection stage
                self.consume_each(win_size + self.osr - self.init_sto)
            else:
                self.consume_each(win_size)

            return win_size
