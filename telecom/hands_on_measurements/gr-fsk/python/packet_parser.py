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


def reflect_data(x, width):
    # See: https://stackoverflow.com/a/20918545
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


def crc_poly(data, n, poly, crc=0, ref_in=False, ref_out=False, xor_out=0):
    # See : https://gist.github.com/Lauszus/6c787a3bc26fea6e842dfb8296ebd630
    g = 1 << n | poly  # Generator polynomial

    # Loop over the data
    for d in data:
        # Reverse the input byte if the flag is true
        if ref_in:
            d = reflect_data(d, 8)

        # XOR the top byte in the CRC with the input byte
        crc ^= d << (n - 8)

        # Loop over all the bits in the byte
        for _ in range(8):
            # Start by shifting the CRC, so we can check for the top bit
            crc <<= 1

            # XOR the CRC if the top bit is 1
            if crc & (1 << n):
                crc ^= g

    # Reverse the output if the flag is true
    if ref_out:
        crc = reflect_data(crc, n)

    # Return the CRC value
    return crc ^ xor_out


class packet_parser(gr.basic_block):
    """
    docstring for block packet_parser
    """

    def __init__(self, hdr_len, payload_len, crc_len, address):
        self.hdr_len = hdr_len
        self.payload_len = payload_len
        self.crc_len = crc_len
        self.nb_packet = 0
        self.nb_error = 0

        self.packet_len = self.hdr_len + self.payload_len + self.crc_len
        self.address = address

        gr.basic_block.__init__(
            self,
            name="packet_parser",
            in_sig=[np.uint8],
            out_sig=[(np.uint8, self.payload_len)],
        )

    def forecast(self, noutput_items, ninput_items_required):
        ninput_items_required[0] = self.packet_len + 1  # in bytes

    def general_work(self, input_items, output_items):
        # we process maximum one packet at a time
        input_bytes = input_items[0][: self.packet_len + 1]
        self.consume_each(self.packet_len + 1)

        b = np.unpackbits(input_bytes)  # bytes to bits

        # print(b)

        b_hdr = b[: self.hdr_len * 8]
        v = np.abs(
            np.correlate(b_hdr * 2 - 1, np.array(self.address) * 2 - 1, mode="full")
        )
        i = np.argmax(v) + 1

        b_pkt = b[i : i + (self.payload_len + self.crc_len) * 8]
        pkt_bytes = np.packbits(b_pkt)

        payload = pkt_bytes[0 : self.payload_len]
        crc = pkt_bytes[self.payload_len : self.payload_len + self.crc_len]

        output_items[0][0] = payload

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
        if all(crc == crc_verif):
            print("[MAC] Packet demodulated: ", payload, crc)
            output_items[0][: self.payload_len] = payload
            print(
                "--- {} packets received with {} error(s) ---".format(
                    self.nb_packet, self.nb_error
                )
            )
            return 1
        else:
            print("[MAC] Error in CRC, packet dropped", payload, crc)
            self.nb_error += 1
            print(
                "--- {} packets received with {} error(s) ---".format(
                    self.nb_packet, self.nb_error
                )
            )
            return 0
