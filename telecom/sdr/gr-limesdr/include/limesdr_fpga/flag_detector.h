/* -*- c++ -*- */
/*
 * Copyright 2025 LELEC210X.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_LIMESDR_FPGA_FLAG_DETECTOR_H
#define INCLUDED_LIMESDR_FPGA_FLAG_DETECTOR_H

#include <gnuradio/block.h>
#include <limesdr_fpga/api.h>

namespace gr {
namespace limesdr_fpga {

/*!
 * \brief <+description of block+>
 * \ingroup flagDetector
 *
 */
class LIMESDR_FPGA_API flag_detector : virtual public gr::block
{
public:
    typedef std::shared_ptr<flag_detector> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of flagDetector::flag_detector.
     *
     * To avoid accidental use of raw pointers, flagDetector::flag_detector's
     * constructor is in a private implementation
     * class. flagDetector::flag_detector::make is the public interface for
     * creating new instances.
     */
    static sptr make(bool enable, float threshold, int burst_len);

    virtual void set_enable( bool enable=false) = 0;
};

} // namespace limesdr_fpga
} // namespace gr

#endif /* INCLUDED_LIMESDR_FPGA_FLAG_DETECTOR_H */
