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


def preamble_detect_energy(y, L, threshold):
    """
    Simple chunk-based energy detector for preamble detection.

    The input is divided into non-overlapping chunks of length L (the
    filter/integration length). A chunk whose summed amplitude exceeds
    threshold * L is considered to contain signal energy, indicating a
    preamble. Returns the sample index at the end of the first hit chunk.

    Parameters
    ----------
    y         : complex64 array of received samples
    L         : chunk length (also used as integration window, in samples)
    threshold : per-sample amplitude threshold

    Returns
    -------
    (detected: bool, position: int or None)

    """
    n_chunks = len(y) // L
    if n_chunks == 0:
        return False, None, 0, 0

    # Sum the magnitude over each chunk and compare to the threshold
    chunk_sums = (np.abs(y[: n_chunks * L]) ** 2).reshape(n_chunks, L).sum(axis=1)
    hits = np.flatnonzero(chunk_sums > threshold)
    if hits.size:
        # Report the last sample of the first chunk that exceeded the threshold
        return True, int(hits[0] * L + (L - 1)), len(hits), n_chunks
    return False, None, 0, n_chunks


class preamble_detect(gr.basic_block):
    """
    GNU Radio block implementing preamble detection for the LELEC210X packet format.

    The block operates in two modes:

    Detection mode (rem_samples == 0):
        Scans incoming samples for a preamble. Two strategies are supported:
        - Energy detector (ideal_detect == 0): uses preamble_detect_energy(),
          which looks for a chunk of samples whose total energy exceeds a threshold.
        - Ideal detection (ideal_detect != 0): uses the ground-truth tag injected
          by the transmitter block (simulation only).
        On detection, the block switches to passthrough mode and attaches tags
        carrying the detection latency and (if available) the estimated noise power.

    Passthrough mode (rem_samples > 0):
        Streams the samples belonging to the detected packet directly to the output
        without further processing, until all samples_to_pass samples have been
        forwarded. The downstream synchronization block then takes over.

    In simulation mode, false alarms (detections without a corresponding transmitter
    tag, or with an offset outside the preamble window) are counted and suppressed.

    The block also supports an on-demand noise power query: when query_estimation()
    is called, the next call to general_work() computes N0*Bf (noise power times
    receive bandwidth) from the idle samples and publishes it via a PMT tag.
    """

    def __init__(
        self,
        common_params,
        threshold,
        enable,
        filter_len,
        simulation,
        ideal_detect,
        query,
        sim_tag_delay,
    ):
        p = parse_common_params(common_params)
        self.drate = p["data_rate"]
        self.fdev = p["fdev"]
        self.fsamp = p["samp_rate"]

        self.packet_len = p["packet_len"]  # in bytes
        self.preamble_len = p["preamble_len"]  # in bytes

        self.osr = p["oversampling"]
        self.threshold = threshold
        self.enable = enable

        self.ideal_detect = ideal_detect

        self.detection_attempt = 0
        self.detection_found = 0

        self.simulation = simulation

        # Number of samples in the preamble field (bits * osr)
        self.samples_preambles = 8 * self.osr * self.preamble_len
        # Total samples to pass downstream per packet (+1 byte guard + 1 sample margin)
        self.samples_to_pass = 8 * self.osr * (self.packet_len + 1) + self.osr

        self.nb_packet = 0
        self.pkt_id = 0

        # filter_len doubles as the energy integration window for preamble_detect_energy
        self.filter_len = filter_len

        self.sim_tag_delay = sim_tag_delay

        # Counts how many more samples still need to be forwarded for the current packet
        self.rem_samples = 0

        # Stored noise power estimate (N0*Bf) used when tagging detected packets (SDR mode)
        self.n0Bf = 0
        self.do_a_query = 0

        gr.basic_block.__init__(
            self,
            name="Preamble detection",
            in_sig=[np.complex64],
            out_sig=[np.complex64],
        )

        self.gr_version = gr.version()

        self.tags = None
        # Tags are manually re-mapped so automatic propagation is disabled
        self.set_tag_propagation_policy(gr.TPP_DONT)

        self.logger = logging.getLogger("preamble")

    def forecast(self, noutput_items, ninputs):
        """
        Forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            # Require at least a full preamble worth of input so the energy
            # detector always has enough context, plus the filter overlap region.
            ninput_items_required[i] = max(
                noutput_items + 2 * self.filter_len, self.samples_preambles
            )
        return ninput_items_required

    def query_estimation(self, query):
        # External trigger: on the next general_work() call, estimate the noise
        # power from the available idle (no-signal) samples.
        if query == 1:
            self.mean_noise_est = 0
            self.do_a_query = 1

    def set_enable(self, enable):
        self.enable = enable

    def set_threshold(self, threshold):
        self.threshold = threshold

    def stop(self):
        if self.simulation:
            if self.ideal_detect == 0:
                self.logger.info(
                    f"[DETECT] {self.nb_packet} packets detected. Threshold exceeded {self.detection_found} times over {self.detection_attempt} attempts => {self.detection_found / self.detection_attempt:.4e} pfa "
                )
            else:
                self.logger.info(f"[DETECT] {self.nb_packet} packets detected.")
        else:
            self.logger.info(f"[DETECT] {self.nb_packet} packets detected")
        return True

    def general_work(self, input_items, output_items):

        ret_val = 0

        # --- PASSTHROUGH MODE ---
        # A preamble was already detected in a previous call; stream remaining samples
        if self.rem_samples > 0:
            N = len(output_items[0])  # available space at output
            n_out = min(self.rem_samples, N)

            output_items[0][:n_out] = input_items[0][:n_out]

            self.rem_samples -= n_out

            self.consume_each(n_out)
            return n_out

        # --- DETECTION MODE ---
        else:
            N = len(output_items[0])  # - len(output_items[0]) % self.filter_len
            # Read slightly beyond N to give the energy detector a full integration window
            y = input_items[0][: N + (2 * self.filter_len)]

            if self.enable == 1:
                # In simulation mode, latch the transmitter's ground-truth tags when present
                tags = self.get_tags_in_window(0, 0, N + self.filter_len)
                if tags:
                    self.tags = tags

                detect = False
                pos = None

                # Energy-based detection
                if self.ideal_detect == 0:
                    detect, pos, n_found, n_trials = preamble_detect_energy(
                        y, self.filter_len, self.threshold
                    )
                    self.detection_attempt += n_trials
                    self.detection_found += n_found

                # Ideal detection: use the transmitter tag as the ground truth start
                elif self.tags:
                    detect = True
                    pos = tags[0].offset - self.nitems_read(0) + self.sim_tag_delay

                # --- False-alarm suppression in simulation ---
                # In simulation, a detection is only valid if a transmitter tag exists
                # and the detected position falls within the preamble window.
                if (detect) & (self.simulation):
                    if self.tags is None:
                        # No tag from the transmitter → pure false alarm
                        detect = False
                        pos = None
                    else:
                        detection_offset = pos + self.nitems_read(0)
                        detection_latency = detection_offset - (
                            self.tags[0].offset + self.sim_tag_delay
                        )
                        if (detection_latency < 0) | (
                            detection_latency >= self.samples_preambles
                        ):
                            # Detection fell outside the valid preamble window
                            detect = False
                            pos = None
                            if detection_latency < 0:
                                # Detected before the packet even started: skip to just before it
                                self.consume_each(
                                    self.tags[0].offset - self.nitems_read(0) - 1
                                )
                                self.tags = None
                                return 0
                            self.tags = None

                if detect:
                    self.nb_packet += 1

                    self.rem_samples = self.samples_to_pass

                    # Cap to the packet's own length: a large scan window
                    # (N - pos) can otherwise overshoot a short packet,
                    # driving rem_samples negative and corrupting both the
                    # passthrough and the power estimate below.
                    n_out = max(min(N - pos, self.rem_samples), 0)

                    # --- Attach metadata tags to the first sample of the packet ---
                    # abs_offset is the output stream position for this packet's start,
                    # defined as a contiguous counter so downstream blocks can identify packets.
                    #######################################################
                    abs_offset = self.pkt_id * self.samples_to_pass

                    if self.tags:
                        # Forward the transmitter's ground-truth tags (CFO, STO, amp, …)
                        for tag in self.tags:
                            self.add_item_tag(0, abs_offset, tag.key, tag.value)

                        # Compute and tag detection latency for performance evaluation
                        detection_offset = pos + self.nitems_read(0)
                        detection_latency = detection_offset - (
                            self.tags[0].offset + self.sim_tag_delay
                        )

                        key_detection_lat = pmt.intern("detection_latency")
                        val_detection_lat = pmt.from_long(detection_latency)

                        self.add_item_tag(
                            0, abs_offset, key_detection_lat, val_detection_lat
                        )

                    if (self.simulation == 0) and (self.n0Bf != 0):
                        # In hardware mode, attach the most recent noise power estimate
                        # so that packet_stats can compute the per-packet SNR.
                        key_detection_n0Bf = pmt.intern("est_noise_power")
                        val_detection_n0Bf = pmt.from_double(self.n0Bf)
                        self.add_item_tag(
                            0, abs_offset, key_detection_n0Bf, val_detection_n0Bf
                        )

                    self.pkt_id += 1
                    #######################################################

                    output_items[0][:n_out] = input_items[0][pos : pos + n_out]

                    self.rem_samples -= n_out

                    ret_val = n_out

                    self.tags = None
                    self.consume_each(pos + n_out)
                    return ret_val

                elif (
                    pos is None or pos > N
                ):  # no preamble found: the whole scanned window is
                    ret_val = 0

            # --- On-demand noise power estimation ---
            # Triggered by query_estimation(); uses the current input window (which should
            # be idle, i.e., no signal present) to estimate N0*Bf as the mean signal power.
            if self.do_a_query == 1:
                len_noise_estimate = input_items[0][:].size
                self.n0Bf = (
                    np.dot(input_items[0][:], input_items[0][:].conj()).real
                    / len_noise_estimate
                )
                self.logger.info(
                    f"[DETECT-NOISE-ESTIMATE] N0xBf : {10 * np.log10(self.n0Bf):.2f}dB =  {np.sqrt(self.n0Bf):.2e} STD,  Calc. on {len_noise_estimate} samples"
                )
                self.do_a_query = 0

            self.consume_each(N)
            return ret_val
