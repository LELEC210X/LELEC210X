/* -*- c++ -*- */
/*
 * Copyright 2025 LELEC210X.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_LIMESDR_FPGA_FLAG_DETECTOR_IMPL_H
#define INCLUDED_LIMESDR_FPGA_FLAG_DETECTOR_IMPL_H


#include <limesdr_fpga/flag_detector.h>

namespace gr {
namespace limesdr_fpga {

class flag_detector_impl : public flag_detector
{
private:
    bool d_enable;
    float d_threshold;
    int d_burst_len;
    bool d_triggered;
    int d_remaining;

public:
    flag_detector_impl(bool enable, float threshold, int burst_len);
    ~flag_detector_impl();

    // Where all the action really happens
    void forecast(int noutput_items, gr_vector_int &ninput_items_required);
    
    int general_work(int noutput_items,
             gr_vector_int &ninput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);

    void set_enable( bool enable);
};

} // namespace limesdr_fpga
} // namespace gr

#endif /* INCLUDED_LIMESDR_FPGA_FLAG_DETECTOR_IMPL_H */
