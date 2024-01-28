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
from gnuradio import blocks, gr, gr_unittest
from preamble_detect import preamble_detect
from synchronization import synchronization


def gr_cast(x):
    return [complex(z) for z in x]


class qa_synchronization(gr_unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_001_t(self):
        fsamp = 400e3
        drate = 50e3
        fdev = drate / 2
        packet_len = 509

        y = np.fromfile("../misc/fsk_trace.mat", dtype=np.complex64)
        y = y * 2
        int(fsamp / drate)
        t = np.arange(len(y)) / fsamp
        cfo_fix = 14750
        y = y * np.exp(-1j * 2 * np.pi * cfo_fix * t)

        tb = gr.top_block()
        source = blocks.vector_source_c(y)
        detector = preamble_detect(drate, fdev, fsamp, packet_len)
        sync = synchronization(drate, fdev, fsamp, packet_len)
        sink = blocks.vector_sink_c()

        tb.connect(source, detector)
        tb.connect(detector, sync)
        tb.connect(sync, sink)

        tb.run()
        y_out = sink.data()
        tb.stop()

        print(len(y_out))


if __name__ == "__main__":
    gr_unittest.run(qa_synchronization)
