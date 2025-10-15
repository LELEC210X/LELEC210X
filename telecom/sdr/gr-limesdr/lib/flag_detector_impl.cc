/* -*- c++ -*- */
/*
 * Copyright 2025 LELEC210X.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "flag_detector_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace limesdr_fpga {

using input_type = gr_complex;
using output_type = gr_complex;
flag_detector::sptr flag_detector::make(bool enable, float threshold, int burst_len)
{
    return gnuradio::make_block_sptr<flag_detector_impl>(enable, threshold, burst_len);
}


/*
 * The private constructor
 */
flag_detector_impl::flag_detector_impl(bool enable, float threshold, int burst_len)
    : gr::block("flag_detector",
                        gr::io_signature::make(1, 1, sizeof(gr_complex)),
                        gr::io_signature::make(1, 1, sizeof(gr_complex))),
      d_enable(enable),
      d_threshold(threshold),
      d_burst_len(burst_len),
      d_triggered(false),
      d_remaining(0)
{
}

/*
 * Our virtual destructor.
 */
flag_detector_impl::~flag_detector_impl() {}

void flag_detector_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
    // conservative: to produce N outputs we ask for at least N inputs
    // (we may consume more inputs if many are dropped)
    if (ninput_items_required.size() >= 1)
        ninput_items_required[0] = noutput_items;
}

int flag_detector_impl::general_work(int noutput_items,
                             gr_vector_int &ninput_items,
                             gr_vector_const_void_star& input_items,
                             gr_vector_void_star& output_items)
{
    const gr_complex *in = reinterpret_cast<const gr_complex *>(input_items[0]);
    gr_complex *out = reinterpret_cast<gr_complex *>(output_items[0]);

    int ninput = ninput_items[0];

    int in_idx = 0;
    int out_idx = 0;

    if (d_enable){

        while (in_idx < ninput && out_idx < noutput_items) {
            const gr_complex &s = in[in_idx];
            if (!d_triggered) {
                if (std::abs(s.real()) > d_threshold || std::abs(s.imag()) > d_threshold) {
                    d_triggered = true;
                    d_remaining = d_burst_len;
                }
            } else {
                out[out_idx++] = s;
                d_remaining--;
                if (d_remaining <= 0) {
                    d_triggered = false;
                }
            }
            in_idx++;
        }
        consume_each(in_idx);
        return out_idx;
    } else {
        consume_each(ninput);
        return 0;
    }

    // Tell runtime system how many output items we produced.
}

void flag_detector_impl::set_enable( bool enable=false){
    d_enable = enable;
}

} /* namespace limesdr_fpga */
} /* namespace gr */
