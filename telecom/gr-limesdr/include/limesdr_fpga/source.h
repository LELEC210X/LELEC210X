/* -*- c++ -*- */
/*
 * Copyright 2019 Lime Microsystems <info@limemicro.com>
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_LIMESDR_FPGA_SOURCE_H
#define INCLUDED_LIMESDR_FPGA_SOURCE_H

#include <gnuradio/sync_block.h>
#include <limesdr_fpga/api.h>

namespace gr {
namespace limesdr_fpga {

/*!
 * \brief <+description of block+>
 * \ingroup limesdr
 *
 */
class LIMESDR_FPGA_API source : virtual public gr::sync_block
{
public:
    typedef boost::shared_ptr<source> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of limesdr::source.
     *
     * To avoid accidental use of raw pointers, limesdr::source's
     * constructor is in a private implementation
     * class. limesdr::source::make is the public interface for
     * creating new instances.
     * @param serial Device serial number. Cannot be left blank.
     *
     * @param channel_mode Channel and mode selection A(1), B(2), (A+B)MIMO(3).
     *
     * @param filename Path to file if file switch is turned on.
     *
     * @param align_ch_phase Perform MIMO phase alignment by calling AlignRxRF()
     * as described in
     * https://github.com/myriadrf/LMS7002M-docs/blob/master/LimeSDR-USB_channel_alignment_v01r00.pdf
     *
     * @return a new limesdr source block object
     */
    static sptr make(std::string serial,
                     int channel_mode,
                     const std::string& filename,
                     bool align_ch_phase);

    /**
     * Set center frequency
     *
     * @param   freq Frequency to set in Hz
     *
     * @param   chan Channel (not used)
     *
     * @return  actual center frequency in Hz
     */
    virtual double set_center_freq(double freq, size_t chan = 0) = 0;

    /**
     * Set which antenna is used
     *
     * @param   antenna Antenna to set: None(0), LNAH(1), LNAL(2), LNAW(3), AUTO(255)
     *
     * @param   channel  Channel selection: A(LMS_CH_0),B(LMS_CH_1).
     */
    virtual void set_antenna(int antenna, int channel = 0) = 0;

    /**
     * Set NCO (numerically controlled oscillator).
     * By selecting NCO frequency
     * configure NCO. When NCO frequency is 0, NCO is off.
     *
     * @param   nco_freq       NCO frequency in Hz.
     *
     * @param   channel        Channel index.
     */
    virtual void set_nco(float nco_freq, int channel) = 0;

    /**
     * Set analog filters.
     *
     * @param   analog_bandw  Channel filter bandwidth in Hz.
     *
     * @param   channel  Channel selection: A(LMS_CH_0),B(LMS_CH_1).
     *
     * @return actual filter bandwidth in Hz
     */
    virtual double set_bandwidth(double analog_bandw, int channel = 0) = 0;

    /**
     * Set digital filters (GFIR).
     *
     * @param   digital_bandw  Channel filter bandwidth in Hz.
     *
     * @param   channel  Channel selection: A(LMS_CH_0),B(LMS_CH_1).
     */
    virtual void set_digital_filter(double digital_bandw, int channel) = 0;

    /**
     * Set the combined gain value in dB
     *
     * @note actual gain depends on LO frequency and analog LPF configuration and
     * resulting output signal level may be different when those values are changed
     *
     * @param   gain_dB        Desired gain: [0,73] dB
     *
     * @param   channel        Channel selection: A(LMS_CH_0),B(LMS_CH_1).
     *
     * @return actual gain in dB
     */
    virtual unsigned set_gain(unsigned gain_dB, int channel = 0) = 0;

    /**
     * Set the same sample rate for both channels.
     *
     * @param   rate  Sample rate in S/s.
     *
     * @return actual sample rate in S/s
     */
    virtual double set_sample_rate(double rate) = 0;

    /**
     * Set oversampling for both channels.
     *
     * @param oversample Oversampling value (0 (default),1,2,4,8,16,32).
     */
    virtual void set_oversampling(int oversample) = 0;

    /**
     * Perform device calibration.
     *
     * @param   bandw Set calibration bandwidth in Hz.
     *
     * @param   channel  Channel selection: A(LMS_CH_0),B(LMS_CH_1).
     */
    virtual void calibrate(double bandw, int channel = 0) = 0;

    /**
     * Set stream buffer size
     *
     * @param   size FIFO buffer size in samples
     */
    virtual void set_buffer_size(uint32_t size) = 0;

    /**
     * Set TCXO DAC.
     * @note Care must be taken as this parameter is returned to default value only after
     * power off.
     * @note LimeSDR-Mini default value is 180 range is [0,255]
     * LimeSDR-USB default value is 125 range is [0,255]
     * LimeSDR-PCIe default value is 134 range is [0,255]
     * LimeNET-Micro default value is 30714 range is [0,65535]
     *
     * @param   dacVal		   DAC value (0-65535)
     */
    virtual void set_tcxo_dac(uint16_t dacVal = 125) = 0;

    /**
     * Write LMS register
     *
     * Writes a parameter by calling LMS_WriteLMSReg()
     *
     * @param   address		   Address
     * @param   val                Value
     */
    virtual void write_lms_reg(uint32_t address, uint16_t val) = 0;

     /**
     * Enable the Preamble Detector in the datapath.
     *
     * @param   device_number  Device number from the list of LMS_GetDeviceList.
     * @param   dspcfg_preamble_en Default value is 0
     * @param   dspcfg_PASSTHROUGH_LEN  Default value is 100 range is [1,1024]
     * @param   dspcfg_THRESHOLD  Default value is 100 range is [1,65535]
     */
    virtual void set_dspcfg_preamble( uint16_t dspcfg_PASSTHROUGH_LEN = 100u, uint8_t dspcfg_THRESHOLD = 100u, int dspcfg_preamble_en = 0) = 0;

    virtual uint32_t get_dspcfg_long_sum() = 0;

    virtual uint32_t get_dspcfg_short_sum() = 0;
};

} // namespace limesdr
} // namespace gr

#endif /* INCLUDED_LIMESDR_FPGA_SOURCE_H */
