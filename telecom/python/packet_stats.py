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

import os

import numpy as np
import pmt
from gnuradio import gr

from .utils import logging, parse_common_params
from . import stats_plots


class packet_stats(gr.sync_block):
    """
    Sink block that registers one record per packet coming out of
    LELEC210X_packet_parser: everything the tags on that stream carry
    (crc_ok, est_cfo, est_sto, est_sig_pow from synchronization/parser,
    and - if present - the ground truth ID, cfo, sto, amp, esn0,
    payload_id from LELEC210X_packet_generator), plus a bit-error count
    reconstructed from (seed, payload_id) when payload_id is available.

    SNR estimation
    --------------
    Es/N0 is estimated from the signal power measured by the synchronization
    block and the noise power estimated by onQuery_noise_estimation:
        Es/N0 = (P_sig - P_noise * ENBW/fsamp) / (P_noise/fsamp) / drate
    where ENBW is the equivalent noise bandwidth of the receiver filter.

    Ground-truth-dependent fields (payload_id, true cfo/sto/esn0, bit
    errors, missed-detection rate) are simply left blank when the
    generator's tags aren't present, e.g. wired up to a real receive
    chain with no packet_generator.

    On stop(), when ground truth is available, the performance per
    Es/N0 is saved as <out_prefix>_summary.csv (one row per Es/N0) together with
    the SNR plots as PNG images. The per-packet records are saved as
    <out_prefix>.csv only if save_full_trace is set.
    out_prefix is the file name (with optional directory) without
    extension.
    """

    def __init__(self, common_params, seed, print_log, reduced_print,
                 EsN0_min, EsN0_max, n_EsN0, sim_noise_power, enbw,
                 packets_per_esn0, out_prefix, save_full_trace=0,
                 payload_random=1, sdr_expected_payload=None, simulation=0):
        p = parse_common_params(common_params)
        gr.sync_block.__init__(
            self,
            name='packet_stats',
            in_sig=[(np.uint8, p["payload_len"])],
            out_sig=None,
        )
        self.simulation      = simulation
        self.pkt_rec_number  = 0
        self.correct_pkt_rec = 0

        # --- Common radio parameters ---
        self.payload_len = p["payload_len"]
        self.hdr_len     = p["hdr_len"]
        self.drate       = p["data_rate"]
        self.fsamp       = p["samp_rate"]
        self.osr         = p["oversampling"]

        # --- Simulation sweep parameters ---
        self.seed            = int(seed)
        self.print_log       = print_log
        self.reduced_print   = reduced_print
        self.EsN0_min        = EsN0_min
        self.EsN0_max        = EsN0_max
        self.n_esn0          = n_EsN0
        self.sim_noise_power = sim_noise_power
        # Equivalent noise bandwidth of the receiver filter [Hz], used to
        # convert the measured noise power (in-band) to a spectral density N0.
        self.enbw            = enbw

        if sdr_expected_payload is not None:
            self.sdr_expected_payload = np.mod(np.array(sdr_expected_payload), 255).astype(np.uint8)

        # Expected number of transmissions per distinct SNR value (the
        # packet_generator's own "Npackets" parameter, which is a
        # per-SNR count): used as the denominator for missed-detection
        # rate. <= 0 disables that plot (e.g. no packet_generator).
        self.packets_per_esn0 = int(packets_per_esn0)
        self.out_prefix       = out_prefix
        self.save_full_trace  = bool(save_full_trace)
        self.payload_random   = payload_random

        self.records  = []
        self.logger   = logging.getLogger("pktStats")
        self.est_n0_ok = None


    def set_reduced_print(self, reduced_print):
        self.reduced_print = reduced_print

    def set_print_log(self, print_log):
        self.print_log = print_log

    def set_noise_power(self, sim_noise_power):
        self.logger.info("[STATS] Noise power has changed")
        self.sim_noise_power = sim_noise_power


    def work(self, input_items, output_items):
        """
        Process one batch of decoded payloads.

        Each input item is one payload vector, tagged with the metadata
        accumulated along the receive chain (CFO/STO estimates, CRC verdict,
        ground-truth impairments from the generator).  One record is built
        per payload and appended to self.records for later export.
        """
        in0   = input_items[0]
        n     = len(in0)
        n_read = self.nitems_read(0)

        for i in range(n):
            payload = np.asarray(in0[i], dtype=np.uint8)
            tags    = self.get_tags_in_window(0, i, i + 1)

            # Collect all PMT tags into a plain dict for easy field lookup
            info = {}
            for tag in tags:
                info[pmt.to_python(tag.key)] = pmt.to_python(tag.value)

            record = self._build_record(n_read + i, payload, info)
            self.records.append(record)

            if self.print_log:
                msg = f"[STATS] pkt {record['pkt_rec_number']:3d}: correct={record['crc_ok']}"

                if not self.reduced_print:
                    if record["est_cfo"] is not None:
                        msg += f", CFO_est={record['est_cfo']:8.2f}Hz"
                    if record["est_sto"] is not None:
                        msg += f", STO_est={record['est_sto']:8.2f}"

                if record["est_esn0_db"] is not None:
                    msg += f", SNR_est={record['est_esn0_db']:5.2f}dB"
                else:
                    msg += f", No SNR est. (probably no noise power estimation)"

                if not self.reduced_print:
                    msg += f", {self.correct_pkt_rec:3d} correct packets over {self.pkt_rec_number:3d}"

                self.logger.info(msg)

        return n


    def _build_record(self, offset, payload, info):
        """
        Build a single-packet statistics record from the decoded payload and
        its associated tag dictionary.

        The record contains both raw measurements (est_cfo, est_sto, etc.)
        and derived metrics (est_esn0_db, cfo_error, sto_error, bit_errors).
        Fields that require ground truth (true_cfo, payload_id, etc.) are set
        to None when the packet_generator's tags are absent.
        """
        record = {
            "offset":            offset,
            "id":                info.get("ID"),
            "pkt_rec_number":    self.pkt_rec_number,
            "payload_id":        info.get("payload_id"),

            "crc_ok":            info.get("crc_ok"),

            "est_cfo":           info.get("est_cfo"),
            "est_sto":           info.get("est_sto"),
            "est_sig_pow":       info.get("est_sig_pow"),

            "true_cfo":          info.get("cfo"),
            "true_sto":          info.get("sto"),
            "true_amp":          info.get("amp"),
            "true_esn0":         info.get("esn0"),

            "detection_latency": info.get("detection_latency"),
            "payload_start":     info.get("payload_start"),

            "est_noise_power":   info.get("est_noise_power"),
        }

        # --- Estimate Es/N0 from receiver measurements ---
        # SNR estimated purely from what the receiver measured (signal
        # power from synchronization, noise power from the callback),
        # independent of any ground truth.
        record["est_esn0_db"] = None

        if record["est_sig_pow"] is not None:
            p_sig, n0 = None, None

            if self.simulation:
                # In simulation the noise power is known from the generator parameters.
                # Subtract the in-band noise contribution from the signal power estimate,
                # then normalize by the noise spectral density per sample.
                p_sig = record["est_sig_pow"] - (self.sim_noise_power) * (self.enbw / self.fsamp)
                n0    = self.sim_noise_power / self.fsamp

            elif record["est_noise_power"] is not None:
                # In hardware mode the noise power is measured before the packet arrives.
                p_sig = record["est_sig_pow"] - record["est_noise_power"]
                n0    = record["est_noise_power"] / self.enbw

            if (p_sig is not None) and (n0 is not None):
                # Es/N0 = (signal energy per symbol) / (noise PSD)
                esn0_lin = (p_sig / self.drate) / n0
                record["est_esn0_db"] = 10 * np.log10(esn0_lin)

        if (self.est_n0_ok == 1) and (record["est_esn0_db"] is None):
            self.logger.info("[STATS] est n0 issue : %d, %d, %d" % (
                record["est_noise_power"] is None,
                record["est_sig_pow"] is None,
                record["est_esn0_db"] is None))

        # --- CFO estimation error (MSE contribution) ---
        # Only meaningful when both the true and estimated CFO are available.
        if record["true_cfo"] is not None and record["est_cfo"] is not None:
            record["cfo_error"] = (record["est_cfo"] - record["true_cfo"])**2
        else:
            record["cfo_error"] = None

        # --- STO estimation error ---
        # The total timing error combines the preamble detection latency,
        # the synchronization block's STO estimate, and the frame start
        # found by the parser's sync-word correlation.
        if (record["detection_latency"] is not None) and \
           (record["est_sto"] is not None) and \
           (record["payload_start"] is not None):
            record["sto_error"] = (
                ((self.hdr_len * 8 * self.osr)
                 - record["detection_latency"]
                 - record["est_sto"]
                 - (record["payload_start"] * self.osr)) / self.osr
            )**2
        else:
            record["sto_error"] = None

        # --- Bit error count vs. ground-truth payload ---
        record["bit_errors"] = None
        record["n_bits"]     = None

        if record["payload_id"] is not None:
            # Reconstruct the exact payload sent by regenerating the same RNG state
            if self.payload_random:
                truth_rng     = np.random.default_rng((self.seed, int(record["payload_id"])))
                truth_payload = truth_rng.integers(256, size=self.payload_len).astype(np.uint8)
            else:
                truth_payload = (np.mod(np.arange(0, self.payload_len), 255)).astype(np.uint8)

            record["bit_errors"] = int(np.sum(np.unpackbits(payload) != np.unpackbits(truth_payload)))
            record["n_bits"]     = self.payload_len * 8

        elif self.sdr_expected_payload is not None:
            # Hardware mode with a known fixed payload
            record["bit_errors"] = int(np.sum(np.unpackbits(payload) != np.unpackbits(self.sdr_expected_payload)))
            record["n_bits"]     = self.payload_len * 8

        if record["crc_ok"] == 1:
            self.correct_pkt_rec += 1

        self.pkt_rec_number += 1
        return record


    def stop(self):
        self._save_and_plot()
        return True


    def _save_and_plot(self):
        """Export statistics to CSV and generate performance plots."""
        if not self.records:
            self.logger.info("[STATS] No packets received, nothing to save.")
            return

        try:
            import pandas as pd
        except ImportError:
            self.logger.error("[STATS] pandas is not available: cannot save the dataframe or plots.")
            return

        df = pd.DataFrame(self.records)

        out_dir = os.path.dirname(self.out_prefix)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        # --- Optionally save the full per-packet trace ---
        if self.save_full_trace:
            csv_path = f"{self.out_prefix}_trace.csv"
            df.to_csv(csv_path, index=False)
            #csv_path = f"{self.out_prefix}_trace_errors.csv"
            #df[df['crc_ok'] == 0].to_csv(csv_path, index=False)
            self.logger.info(f"[STATS] Saved {len(df)} packet records to {csv_path}")

        # --- Print summary ---
        n_received = len(df)
        n_correct  = int(df["crc_ok"].sum())
        summary    = f"[STATS] {n_received} packets received, {n_correct} correct"
        if df["n_bits"].notna().any():
            n_bits       = int(df["n_bits"].dropna().sum())
            n_bit_errors = int(df["bit_errors"].dropna().sum())
            summary += f", overall BER={n_bit_errors / n_bits:.3e} ({n_bit_errors}/{n_bits} bits)"
        self.logger.info(summary)

        # --- CFO histogram ---
        stats_plots.plot_cfo_histogram(df, self.out_prefix, save_fig=True, logger=self.logger, close=True)

        if self.simulation and not df["true_esn0"].notna().any():
            self.logger.info("[STATS] No ground-truth SNR tags found (no packet_generator?): skipping summary and SNR plots.")
            return

        # --- Per-Es/N0 performance summary and plots ---
        summary = stats_plots.compute_summary(
            df, self.simulation, self.payload_len, self.drate, self.fsamp,
            self.packets_per_esn0, self.EsN0_min, self.EsN0_max, self.n_esn0
        )

        summary_path = f"{self.out_prefix}.csv"
        summary.to_csv(summary_path, index=False)
        self.logger.info(f"[STATS] Saved per-Es/N0 summary to {summary_path}")

        stats_plots.plot_summary(summary, self.out_prefix, save_fig=True, logger=self.logger, close=True)
