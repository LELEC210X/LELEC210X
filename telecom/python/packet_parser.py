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


def reflect_data(x, width):
    """
    Bit-reverse an integer x of the given bit width.

    Some CRC standards (e.g. CRC-16/IBM) specify that input bytes and/or the
    final CRC register are bit-reflected before use. This function implements
    the bit-reversal by swapping pairs, then nibbles, then bytes, etc.
    See: https://stackoverflow.com/a/20918545
    """
    if width == 8:
        x = ((x & 0x55) << 1) | ((x & 0xAA) >> 1)
        x = ((x & 0x33) << 2) | ((x & 0xCC) >> 2)
        x = ((x & 0x0F) << 4) | ((x & 0xF0) >> 4)
    elif width == 16:
        x = ((x & 0x5555) << 1) | ((x & 0xAAAA) >> 1)
        x = ((x & 0x3333) << 2) | ((x & 0xCCCC) >> 2)
        x = ((x & 0x0F0F) << 4) | ((x & 0xF0F0) >> 4)
        x = ((x & 0x00FF) << 8) | ((x & 0xFF00) >> 8)
    elif width == 32:
        x = ((x & 0x55555555) << 1) | ((x & 0xAAAAAAAA) >> 1)
        x = ((x & 0x33333333) << 2) | ((x & 0xCCCCCCCC) >> 2)
        x = ((x & 0x0F0F0F0F) << 4) | ((x & 0xF0F0F0F0) >> 4)
        x = ((x & 0x00FF00FF) << 8) | ((x & 0xFF00FF00) >> 8)
        x = ((x & 0x0000FFFF) << 16) | ((x & 0xFFFF0000) >> 16)
    else:
        raise ValueError("Unsupported width")
    return x


_crc_table_cache = {}


def _build_crc_table(n, poly):
    """
    Pre-compute the CRC lookup table for an n-bit CRC with generator polynomial poly.

    For each of the 256 possible byte values, the table stores the CRC remainder
    that the bit-serial algorithm would produce for that byte alone (starting from
    crc=0). Built once per (n, poly) pair and cached so repeated calls are free.
    """
    # Classic byte-wise CRC lookup table: table[byte] is what the
    # bit-serial algorithm below would produce for a single input byte
    # starting from crc=0. Built once per (n, poly) pair.
    g = 1 << n | poly
    table = [0] * 256
    for byte in range(256):
        crc = byte << (n - 8)
        for _ in range(8):
            crc <<= 1
            if crc & (1 << n):
                crc ^= g
        table[byte] = crc & ((1 << n) - 1)
    return table


def crc_poly(data, n, poly, crc=0, ref_in=False, ref_out=False, xor_out=0):
    """
    Table-driven byte-serial CRC computation.

    Processes one byte of data per iteration using a pre-computed lookup table,
    which is equivalent to the classic bit-serial shift-register algorithm but
    8× faster. The optional ref_in / ref_out flags implement bit-reflection of
    the input bytes and the final CRC register, respectively, as required by
    certain CRC standards (e.g., CRC-16/IBM uses both).

    Reference (bit-serial version):
        https://gist.github.com/Lauszus/6c787a3bc26fea6e842dfb8296ebd630
    """
    # Table-driven CRC: one lookup per byte instead of 8 shift/XOR steps
    # per bit. Numerically identical to the original bit-serial version
    # available @ https://gist.github.com/Lauszus/6c787a3bc26fea6e842dfb8296ebd630
    key = (n, poly)
    table = _crc_table_cache.get(key)
    if table is None:
        table = _build_crc_table(n, poly)
        _crc_table_cache[key] = table

    mask = (1 << n) - 1
    shift = n - 8
    for d in data:
        if ref_in:
            d = reflect_data(d, 8)
        idx = ((crc >> shift) ^ d) & 0xFF
        crc = ((crc << 8) ^ table[idx]) & mask

    # Reverse the output if the flag is true
    if ref_out:
        crc = reflect_data(crc, n)

    # Return the CRC value
    return crc ^ xor_out


def symbols_to_bytes(symbols):
    """
    Pack an array of bits (one bit per element) into bytes (uint8).

    Bits are grouped MSB-first in groups of 8. Any trailing bits that do
    not fill a complete byte are discarded.
    """
    symbols = np.asarray(symbols)
    n_bytes = len(symbols) // 8
    if n_bytes == 0:
        return np.array([], dtype=np.uint8)

    return np.packbits(symbols[: n_bytes * 8].astype(np.uint8))


class packet_parser(gr.basic_block):
    """
    GNU Radio block that extracts and validates one payload per call.

    Packet structure (in bytes):
        [ preamble | sync_word | payload | CRC ]
              hdr_len              payload_len  crc_len

    For each call, the block:
    1. Converts the incoming bit stream back to bytes.
    2. Locates the sync word boundary within the header by cross-correlating
       the received header bits (mapped to ±1) with the expected sync word.
       This corrects residual STO misalignment up to a few bits.
    3. Extracts payload and CRC bytes starting from the detected sync word end.
    4. Verifies the CRC-8/SMBUS checksum (poly=0x07, init=0xFF).
    5. Emits the payload (regardless of CRC outcome) and attaches tags:
       - all upstream tags (CFO, STO, signal power, ground truth from generator)
       - "crc_ok" (1 = pass, 0 = fail)
       - "payload_start" (bit index where the payload began, for STO analysis)

    Input  : uint8 stream (one bit per sample, from the demodulation block)
    Output : vectors of uint8 of length payload_len (one vector per packet)
    """

    def __init__(self, common_params):
        p = parse_common_params(common_params)
        self.hdr_len = p["hdr_len"]
        self.payload_len = p["payload_len"]
        self.crc_len = p["crc_len"]
        self.address = p["sync_word"]
        self.nb_packet = 0
        self.nb_error = 0

        self.pkt_id = 0
        self.rec_pkt_id = 0

        self.packet_len = self.hdr_len + self.payload_len + self.crc_len

        gr.basic_block.__init__(
            self,
            name="packet_parser",
            in_sig=[np.uint8],
            out_sig=[(np.uint8, self.payload_len)],
        )
        self.logger = logging.getLogger("parser")

        self.gr_version = gr.version()

        # Tags are manually forwarded from input to output; disable auto-propagation
        self.set_tag_propagation_policy(gr.TPP_DONT)

    def forecast(self, noutput_items, ninputs):
        """
        Forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            # One extra byte guard (+1) in case the sync word correlation shifts
            # the packet start by a few bits within the header.
            ninput_items_required[i] = (self.packet_len + 1) * 8

        return ninput_items_required

    def stop(self):
        self.logger.info(
            f"[PARSER] {self.nb_packet} packets received with {self.nb_error} error(s)"
        )
        return True

    def general_work(self, input_items, output_items):
        # Process at most one packet per call
        input_samples = input_items[0][: (self.packet_len + 1) * 8]

        # --- Bit stream → byte stream ---
        input_bytes = symbols_to_bytes(input_samples)

        # Expand back to individual bits for the correlation-based sync word search
        b = np.unpackbits(input_bytes)  # bytes to bits

        # --- Sync word search within the header ---
        # Map bits from {0,1} to {-1,+1} to centre the correlation output at zero.
        # The peak of the cross-correlation indicates where the sync word ends in
        # the received bit sequence, compensating for any residual STO misalignment.
        b_hdr = b[: self.hdr_len * 8]
        v = np.abs(
            np.correlate(b_hdr * 2 - 1, np.array(self.address) * 2 - 1, mode="full")
        )
        # i is the bit index where the payload begins (just after the sync word peak)
        i = min(np.argmax(v) + 1, self.hdr_len * 8)

        # --- Extract payload and CRC bytes ---
        b_pkt = b[i : i + (self.payload_len + self.crc_len) * 8]
        pkt_bytes = np.packbits(b_pkt)

        payload = pkt_bytes[0 : self.payload_len]
        crc = pkt_bytes[self.payload_len : self.payload_len + self.crc_len]

        if len(payload) != self.payload_len:
            self.logger.info(
                f"[PARSER] Array length error : {len(input_bytes)} -- {len(pkt_bytes)} -- {len(payload)} -- {len(output_items[0][0])} ---Bits : {i} => {i + (self.payload_len + self.crc_len) * 8}"
            )

        output_items[0][0] = payload

        # --- CRC-8/SMBUS verification ---
        # Parameters: n=8, poly=0x07, init=0xFF, ref_in=False, ref_out=False, xor_out=0
        # This matches the CRC used by the AT86RF215 transceiver and the transmitter block.
        crc_verif = crc_poly(
            bytearray(payload),
            8,
            0x07,
            crc=0xFF,
            ref_in=False,
            ref_out=False,
            xor_out=0,
        )

        self.nb_packet += 1
        is_correct = all(crc == crc_verif)

        # --- Tag forwarding ---
        # Forward every tag found on the input (ID, cfo, sto, amp, snr,
        # payload_id from the generator; est_cfo, est_sto, est_sig_pow
        # from synchronization) onto this block's own output stream, at
        # the offset of the output item this call produces below, plus
        # this block's own "crc_ok" verdict. A downstream stats block
        # (e.g. LELEC210X_packet_stats) reads all of this from the output
        # tags rather than from this block's internals.
        #######################################################
        in_tags = self.get_tags_in_window(0, 0, 1)
        out_offset = self.nitems_written(0)
        for tag in in_tags:
            self.add_item_tag(0, out_offset, tag.key, tag.value)

        self.add_item_tag(
            0, out_offset, pmt.intern("crc_ok"), pmt.from_long(is_correct)
        )
        # payload_start records the bit offset used for extraction, enabling STO RMSE analysis
        self.add_item_tag(0, out_offset, pmt.intern("payload_start"), pmt.from_long(i))
        #######################################################

        if not is_correct:
            self.nb_error += 1

        self.consume_each((self.packet_len + 1) * 8)

        # Always emit the (attempted) payload downstream, whether or not
        # the CRC passed - a stats block needs to see every packet that
        # made it this far to tell "wrong" apart from "never detected".
        return 1
