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
from gnuradio import gr

from .utils import logging


class tutorial(gr.basic_block):
    """
    docstring for block tutorial
    """

    def __init__(self, offset):

        self.offset = offset

        gr.basic_block.__init__(
            self,
            name="Preamble detection",
            in_sig=[np.complex64],
            out_sig=[np.complex64],
        )

        self.gr_version = gr.version()

        self.tags = None
        self.set_tag_propagation_policy(gr.TPP_DONT)

        self.logger = logging.getLogger("tutorial")

    def forecast(self, noutput_items, ninputs):
        """
        Forecast is only called from a general block
        this is the default implementation
        """
        ninput_items_required = [0] * ninputs
        for i in range(ninputs):
            ninput_items_required[i] = noutput_items
        return ninput_items_required

    def set_offset(self, offset):
        self.logger.info(f"[Tutorial] Offset variable changed to {offset:.2f}")
        self.offset = offset

    def stop(self):
        self.logger.info("[Tutorial] End of flowgraph, stop function reached")
        return True

    def general_work(self, input_items, output_items):

        # Never produce more than the output buffer can hold (nor consume more than we produce)
        nitems = min(len(input_items[0]), len(output_items[0]))

        output_items[0][:nitems] = input_items[0][:nitems] + (
            self.offset + 1j * self.offset
        )

        self.consume_each(nitems)

        return nitems
