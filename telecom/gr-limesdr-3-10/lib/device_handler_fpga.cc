/* -*- c++ -*- */
/*
 * Copyright 2018 Lime Microsystems info@limemicro.com
 *
 * This software is free software; you can redistribute it and/or modify
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

#include "device_handler_fpga.h"
#include "logging_fpga.h"

#include <lime/LMS7002M_parameters.h>

#include <gnuradio/logger.h>

#include <boost/format.hpp>

#include <stdexcept>

device_handler_fpga::device_handler_fpga()
{
    gr::configure_default_loggers(d_logger, d_debug_logger, "device_handler_fpga");
    set_limesuite_logger();
}

device_handler_fpga::~device_handler_fpga() { delete list; }

void device_handler_fpga::error(int device_number)
{
    GR_LOG_WARN(d_logger, LMS_GetLastErrorMessage());;
    if (this->device_vector[device_number].address != NULL)
        close_all_devices();
}

lms_device_t* device_handler_fpga::get_device(int device_number)
{
    return this->device_vector[device_number].address;
}

int device_handler_fpga::open_device(std::string& serial)
{
    set_limesuite_logger();

    int device_number = 0;
    std::string search_name;

    // Print device and library information only once
    if (list_read == false) {
        GR_LOG_INFO(d_logger, "##################");
        GR_LOG_INFO(d_logger, boost::format("LimeSuite version: %s") % LMS_GetLibraryVersion());
        GR_LOG_INFO(d_logger, boost::format("gr-limesdr_fpga version: %s") % GR_LIMESDR_FPGA_VER);
        GR_LOG_INFO(d_logger, "##################");

        device_count = LMS_GetDeviceList(list);
        if (device_count < 1) {
            throw std::runtime_error("device_handler_fpga::open_device(): No Lime devices found.");
        }
        GR_LOG_INFO(d_logger, "Device list:");

        for (int i = 0; i < device_count; i++) {
            GR_LOG_INFO(d_logger, boost::format("Device %d: %s") % i % list[i]);
            device_vector.push_back(device());
        }
        GR_LOG_INFO(d_logger, "##################");
        list_read = true;
    }

    auto device_to_serial = [](const std::string &device_string)
    {
        size_t first = device_string.find("serial=") + 7;
        size_t end = device_string.find(",", first);
        return device_string.substr(first, end - first);
    };

    if (serial.empty()) {
        GR_LOG_INFO(d_logger, "device_handler_fpga::open_device(): no serial number. Using first device in the list.");
        GR_LOG_INFO(d_logger, "Use \"LimeUtil --find\" in terminal to find preferred device serial.");

        device_number = 0;
        serial = device_to_serial(list[0]);
    } else {
        auto device_iter = std::find_if(
            &list[0],
            &list[device_count],
            [&](const lms_info_str_t device_string)
            {
                return (serial == device_to_serial(device_string));
            });

        if(device_iter == &list[device_count]) {
            close_all_devices();
            throw std::invalid_argument("Unable to find LMS device with serial "+serial);
        }

        device_number = device_iter - &list[0];
        serial = device_to_serial(*device_iter);
    }

    // If device slot is empty, open and initialize device
    if (device_vector[device_number].address == NULL) {
        if (LMS_Open(&device_vector[device_number].address, list[device_number], NULL) != LMS_SUCCESS)
            throw std::runtime_error("device_handler_fpga::open_device(): failed to open device " + serial);

        LMS_Init(device_vector[device_number].address);
        const lms_dev_info_t* info =
            LMS_GetDeviceInfo(device_vector[device_number].address);

        GR_LOG_INFO(
            d_logger,
            boost::format("Using device: %s (%s) GW: %s FW: %s")
                % info->deviceName
                % serial
                % info->gatewareVersion
                % info->firmwareVersion);
        GR_LOG_INFO(d_logger, "##################");

        ++open_devices; // Count open devices
    }
    // If device is open do nothing
    else {
        GR_LOG_INFO(
            d_logger,
            boost::format("Previously connected device number %d from the list is used.")
                % device_number);
        GR_LOG_INFO(d_logger, "##################");
    }
    set_limesuite_logger();

    return device_number; // return device number to identify
                          // device_vector[device_number].address connection in other
                          // functions
}

void device_handler_fpga::close_device(int device_number, int block_type)
{
    // Check if other block finished and close device
    if (device_vector[device_number].source_flag == false ||
        device_vector[device_number].sink_flag == false) {
        if (device_vector[device_number].address != NULL) {
            GR_LOG_INFO(d_logger, "##################");
            if (LMS_Reset(this->device_vector[device_number].address) != LMS_SUCCESS)
                error(device_number);
            if (LMS_Close(this->device_vector[device_number].address) != LMS_SUCCESS)
                error(device_number);
            GR_LOG_INFO(
                d_logger,
                boost::format("device_handler_fpga::close_device(): disconnected from device number %d.")
                    % device_number);
            device_vector[device_number].address = NULL;
            GR_LOG_INFO(d_logger, "##################");
        }
    }
    // If two blocks used switch one block flag and let other block finish work
    // Switch flag when closing device
    switch (block_type) {
    case 1:
        device_vector[device_number].source_flag = false;
        break;
    case 2:
        device_vector[device_number].sink_flag = false;
        break;
    }
}

void device_handler_fpga::close_all_devices()
{
    if (close_flag == false) {
        for (int i = 0; i <= open_devices; i++) {
            if (this->device_vector[i].address != NULL) {
                LMS_Reset(this->device_vector[i].address);
                LMS_Close(this->device_vector[i].address);
            }
        }
        close_flag = true;
    }
}

void device_handler_fpga::check_blocks(int device_number,
                                  int block_type,
                                  int channel_mode,
                                  const std::string& filename)
{
    // Get each block settings
    switch (block_type) {
    case 1: // Source block
        if (device_vector[device_number].source_flag == true) {
            close_all_devices();
            throw std::invalid_argument(
                "ERROR: device_handler_fpga::check_blocks(): only one LimeSuite "
                "Source (RX) block is allowed per device.");
        } else {
            device_vector[device_number].source_flag = true;
            device_vector[device_number].source_channel_mode = channel_mode;
            device_vector[device_number].source_filename = filename;
        }
        break;

    case 2: // Sink block
        if (device_vector[device_number].sink_flag == true) {
            throw std::invalid_argument(
                "ERROR: device_handler_fpga::check_blocks(): only one LimeSuite "
                "Sink (TX) block is allowed per device.");
        } else {
            device_vector[device_number].sink_flag = true;
            device_vector[device_number].sink_channel_mode = channel_mode;
            device_vector[device_number].sink_filename = filename;
        }
        break;

    default:
        close_all_devices();
        throw std::invalid_argument(str(
            boost::format("device_handler_fpga::check_blocks(): internal error, incorrect block_type value %d.")
                % block_type));
    }

    // Check block settings which must match
    if (device_vector[device_number].source_flag &&
        device_vector[device_number].sink_flag) {
        // Chip_mode must match in blocks with the same serial
        if (device_vector[device_number].source_channel_mode !=
            device_vector[device_number].sink_channel_mode) {

            close_all_devices();
            throw std::invalid_argument(str(
                boost::format("device_handler_fpga::check_blocks(): channel mismatch in LimeSuite "
                              "Source (RX) (%d) and LimeSuite Sink (TX) (%d)")
                    % device_vector[device_number].source_channel_mode
                    % device_vector[device_number].sink_channel_mode));
        }

        // When file_switch is 1 check filename match throughout the blocks with the same
        // serial
        if (device_vector[device_number].source_filename !=
            device_vector[device_number].sink_filename) {

            close_all_devices();
            throw std::invalid_argument(str(
                boost::format("device_handler_fpga::check_blocks(): file must match in LimeSuite "
                              "Source (RX) (%s) and LimeSuite Sink (TX) (%s)")
                    % device_vector[device_number].source_filename
                    % device_vector[device_number].sink_filename));
        }
    }
}

void device_handler_fpga::settings_from_file(int device_number,
                                        const std::string& filename,
                                        int* pAntenna_tx)
{
    if (LMS_LoadConfig(device_handler_fpga::getInstance().get_device(device_number),
                       filename.c_str()))
        device_handler_fpga::getInstance().error(device_number);

    // Set LimeSDR-Mini switches based on .ini file
    int antenna_rx = LMS_PATH_NONE;
    int antenna_tx[2] = { LMS_PATH_NONE };
    antenna_tx[0] = LMS_GetAntenna(
        device_handler_fpga::getInstance().get_device(device_number), LMS_CH_TX, LMS_CH_0);
    /* Don't print error message for the mini board */
    suppress_limesuite_logging();
    antenna_tx[1] = LMS_GetAntenna(
        device_handler_fpga::getInstance().get_device(device_number), LMS_CH_TX, LMS_CH_1);
    // Restore our logging
    set_limesuite_logger();
    antenna_rx = LMS_GetAntenna(
        device_handler_fpga::getInstance().get_device(device_number), LMS_CH_RX, LMS_CH_0);

    if (pAntenna_tx != nullptr) {
        pAntenna_tx[0] = antenna_tx[0];
        pAntenna_tx[1] = antenna_tx[1];
    }

    LMS_SetAntenna(device_handler_fpga::getInstance().get_device(device_number),
                   LMS_CH_TX,
                   LMS_CH_0,
                   antenna_tx[0]);
    LMS_SetAntenna(device_handler_fpga::getInstance().get_device(device_number),
                   LMS_CH_RX,
                   LMS_CH_0,
                   antenna_rx);
}

void device_handler_fpga::enable_channels(int device_number, int channel_mode, bool direction)
{
    GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::enable_channels(): ");
    if (channel_mode < 2) {

        if (LMS_EnableChannel(device_handler_fpga::getInstance().get_device(device_number),
                              direction,
                              channel_mode,
                              true) != LMS_SUCCESS)
            device_handler_fpga::getInstance().error(device_number);
        GR_LOG_INFO(
            d_logger,
            boost::format("SISO CH%d set for device number %d.")
                % channel_mode
                % device_number);

        if (direction)
            rfe_device.tx_channel = channel_mode;
        else
            rfe_device.rx_channel = channel_mode;

        if (rfe_device.rfe_dev) {
            update_rfe_channels();
        }
    } else if (channel_mode == 2) {
        if (LMS_EnableChannel(device_handler_fpga::getInstance().get_device(device_number),
                              direction,
                              LMS_CH_0,
                              true) != LMS_SUCCESS)
            device_handler_fpga::getInstance().error(device_number);
        if (LMS_EnableChannel(device_handler_fpga::getInstance().get_device(device_number),
                              direction,
                              LMS_CH_1,
                              true) != LMS_SUCCESS)
            device_handler_fpga::getInstance().error(device_number);

        GR_LOG_INFO(
            d_logger,
            boost::format("MIMO mode set for device number %d.")
                % device_number);
    }
}

void device_handler_fpga::set_samp_rate(int device_number, double& rate)
{
    GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_samp_rate(): ");
    if (LMS_SetSampleRate(device_handler_fpga::getInstance().get_device(device_number),
                          rate,
                          0) != LMS_SUCCESS)
        device_handler_fpga::getInstance().error(device_number);
    double host_value;
    double rf_value;
    if (LMS_GetSampleRate(device_handler_fpga::getInstance().get_device(device_number),
                          LMS_CH_RX,
                          LMS_CH_0,
                          &host_value,
                          &rf_value))
        device_handler_fpga::getInstance().error(device_number);

    GR_LOG_INFO(
        d_logger,
        boost::format("Set sampling rate: %f MS/s.") % (host_value / 1e6));
    rate = host_value; // Get the real rate back
}

void device_handler_fpga::set_oversampling(int device_number, int oversample)
{
    if (oversample == 0 || oversample == 1 || oversample == 2 || oversample == 4 ||
        oversample == 8 || oversample == 16 || oversample == 32) {
        GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_oversampling(): ");
        double host_value;
        double rf_value;
        if (LMS_GetSampleRate(device_handler_fpga::getInstance().get_device(device_number),
                              LMS_CH_RX,
                              LMS_CH_0,
                              &host_value,
                              &rf_value))
            device_handler_fpga::getInstance().error(device_number);

        if (LMS_SetSampleRate(device_handler_fpga::getInstance().get_device(device_number),
                              host_value,
                              oversample) != LMS_SUCCESS)
            device_handler_fpga::getInstance().error(device_number);

        GR_LOG_INFO(
            d_logger,
            boost::format("Set oversampling: %d.") % oversample);
    } else {
        close_all_devices();
        throw std::invalid_argument(
            "device_handler_fpga::set_oversampling(): valid oversample values are: "
            "0,1,2,4,8,16,32.");
    }
}

double
device_handler_fpga::set_rf_freq(int device_number, bool direction, int channel, float rf_freq)
{
    double value = 0;

    if (rf_freq <= 0) {
        close_all_devices();
        throw std::invalid_argument("device_handler_fpga::set_rf_freq(): rf_freq must be more than 0 Hz.");
    } else {
        GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_rf_freq(): ");
        if (LMS_SetLOFrequency(device_handler_fpga::getInstance().get_device(device_number),
                               direction,
                               channel,
                               rf_freq) != LMS_SUCCESS)
            device_handler_fpga::getInstance().error(device_number);

        LMS_GetLOFrequency(device_handler_fpga::getInstance().get_device(device_number),
                           direction,
                           channel,
                           &value);

        std::string s_dir[2] = { "RX", "TX" };
        GR_LOG_INFO(
            d_logger,
            boost::format("RF frequency set [%s]: %f MHz.")
                % s_dir[direction]
                % (value / 1e6));
    }

    return value;
}

void device_handler_fpga::calibrate(int device_number,
                               int direction,
                               int channel,
                               double bandwidth)
{
    GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::calibrate(): ");
    double rf_freq = 0;
    LMS_GetLOFrequency(device_handler_fpga::getInstance().get_device(device_number),
                       direction,
                       channel,
                       &rf_freq);
    if (rf_freq > 31e6) // Normal calibration
        LMS_Calibrate(device_handler_fpga::getInstance().get_device(device_number),
                      direction,
                      channel,
                      bandwidth,
                      0);
    else { // Workaround
        LMS_SetLOFrequency(device_handler_fpga::getInstance().get_device(device_number),
                           direction,
                           channel,
                           50e6);
        LMS_Calibrate(device_handler_fpga::getInstance().get_device(device_number),
                      direction,
                      channel,
                      bandwidth,
                      0);
        LMS_SetLOFrequency(device_handler_fpga::getInstance().get_device(device_number),
                           direction,
                           channel,
                           rf_freq);
    }
}

void device_handler_fpga::set_antenna(int device_number,
                                 int channel,
                                 int direction,
                                 int antenna)
{
    GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_antenna(): ");
    LMS_SetAntenna(device_handler_fpga::getInstance().get_device(device_number),
                   direction,
                   channel,
                   antenna);
    int antenna_value = LMS_GetAntenna(
        device_handler_fpga::getInstance().get_device(device_number), direction, channel);

    std::string s_antenna[2][4] = { { "Auto(NONE)", "LNAH", "LNAL", "LNAW" },
                                    { "Auto(NONE)", "BAND1", "BAND2", "NONE" } };
    std::string s_dir[2] = { "RX", "TX" };
    GR_LOG_INFO(
        d_logger,
        boost::format("CH%d antenna set [%s]: %s.")
            % channel
            % s_dir[direction]
            % s_antenna[direction][antenna_value]);
}

double device_handler_fpga::set_analog_filter(int device_number,
                                         bool direction,
                                         int channel,
                                         double analog_bandw)
{
    double analog_value = 0;

    if (channel == 0 || channel == 1) {
        if (direction == LMS_CH_TX || direction == LMS_CH_RX) {
            GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_analog_filter(): ");
            LMS_SetLPFBW(device_handler_fpga::getInstance().get_device(device_number),
                         direction,
                         channel,
                         analog_bandw);

            LMS_GetLPFBW(device_handler_fpga::getInstance().get_device(device_number),
                         direction,
                         channel,
                         &analog_value);
        } else {
            close_all_devices();
            throw std::invalid_argument(
                "device_handler_fpga::set_analog_filter(): direction must be "
                "0(LMS_CH_RX) or 1(LMS_CH_TX).");
        }
    } else {
        close_all_devices();
        throw std::invalid_argument("device_handler_fpga::set_analog_filter(): channel must be 0 or 1.");
    }

    return analog_value;
}

double device_handler_fpga::set_digital_filter(int device_number,
                                          bool direction,
                                          int channel,
                                          double digital_bandw)
{
    if (channel == 0 || channel == 1) {
        if (direction == LMS_CH_TX || direction == LMS_CH_RX) {
            bool enable = (digital_bandw > 0) ? true : false;
            GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_digital_filter(): ");
            LMS_SetGFIRLPF(device_handler_fpga::getInstance().get_device(device_number),
                           direction,
                           channel,
                           enable,
                           digital_bandw);
            std::string s_dir[2] = { "RX", "TX" };
            const std::string msg_start = str(boost::format("Digital filter CH%d [%s]")
                % channel
                % s_dir[direction]);

            if (enable) {
                GR_LOG_INFO(d_logger,
                    boost::format("%s set: %f")
                        % msg_start
                        % (digital_bandw / 1e6));
            } else {
                GR_LOG_INFO(d_logger,
                    boost::format("%s disabled.")
                        % msg_start);
            }
        } else {
            close_all_devices();
            throw std::invalid_argument(
                "device_handler_fpga::set_digital_filter(): direction must be "
                "0(LMS_CH_RX) or 1(LMS_CH_TX).");
        }
    } else {
        close_all_devices();
        throw std::invalid_argument("device_handler_fpga::set_digital_filter(): channel must be 0 or 1.");
    }

    return digital_bandw;
}

unsigned
device_handler_fpga::set_gain(int device_number, bool direction, int channel, unsigned gain_dB)
{
    unsigned gain_value = 0;

    if (gain_dB >= 0 && gain_dB <= 73) {
        GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_gain(): ");

        std::cout << "Clearing running sum before changing gain " << std::endl;
        
        uint32_t short_sum = get_dspcfg_short_sum(device_number);
        uint32_t long_sum  = get_dspcfg_long_sum(device_number);
        std::cout << "Actual : Short = " << short_sum << " /  Long = " << long_sum << std::endl;
        set_dspcfg_clear_rs(device_number, 1);
        short_sum = get_dspcfg_short_sum(device_number);
        long_sum  = get_dspcfg_long_sum(device_number);
        std::cout << "Clear : Short = " << short_sum << " /  Long = " << long_sum << std::endl;

        LMS_SetGaindB(device_handler_fpga::getInstance().get_device(device_number),
                      direction,
                      channel,
                      gain_dB);

        std::string s_dir[2] = { "RX", "TX" };

        unsigned int gain_value;
        LMS_GetGaindB(device_handler_fpga::getInstance().get_device(device_number),
                      direction,
                      channel,
                      &gain_value);
        GR_LOG_INFO(
            d_logger,
            boost::format("CH%d gain set [%s]: %s.")
                % channel
                % s_dir[direction]
                % gain_value);

        set_dspcfg_clear_rs(device_number, 0);
        short_sum = get_dspcfg_short_sum(device_number);
        long_sum  = get_dspcfg_long_sum(device_number);
        std::cout << "Running : Short = " << short_sum << " /  Long = " << long_sum << std::endl;

    } else {
        close_all_devices();
        throw std::invalid_argument("device_handler_fpga::set_gain(): valid range [0, 73]");
    }

    return gain_value;
}

void device_handler_fpga::set_nco(int device_number,
                             bool direction,
                             int channel,
                             float nco_freq)
{
    std::string s_dir[2] = { "RX", "TX" };
    GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_nco(): ");
    if (nco_freq == 0) {
        LMS_SetNCOIndex(device_handler_fpga::getInstance().get_device(device_number),
                        direction,
                        channel,
                        -1,
                        0);
        GR_LOG_INFO(
            d_logger,
            boost::format("NCO [%s] CH%d gain disabled.")
                % s_dir[direction]
                % channel);
    } else {
        double freq_value_in[16] = { nco_freq };
        int cmix_mode;

        if (nco_freq > 0)
            cmix_mode = 0;
        else if (nco_freq < 0)
            cmix_mode = 1;

        LMS_SetNCOFrequency(device_handler_fpga::getInstance().get_device(device_number),
                            direction,
                            channel,
                            freq_value_in,
                            0);
        LMS_SetNCOIndex(device_handler_fpga::getInstance().get_device(device_number),
                        direction,
                        channel,
                        0,
                        cmix_mode);
        std::string s_cmix[2] = { "UPCONVERT", "DOWNCONVERT" };
        std::string cmix_mode_string;

        double freq_value_out[16];
        double pho_value_out[16];
        LMS_GetNCOFrequency(device_handler_fpga::getInstance().get_device(device_number),
                            direction,
                            channel,
                            freq_value_out,
                            pho_value_out);
        GR_LOG_INFO(
            d_logger,
            boost::format("NCO [%s] CH%d: %f MHz (%f deg.)(%s).")
                % s_dir[direction]
                % channel
                % (freq_value_out[0] / 1e6)
                % pho_value_out[0]
                % s_cmix[cmix_mode]);
    }
}

void device_handler_fpga::disable_DC_corrections(int device_number)
{
    LMS_WriteParam(
        device_handler_fpga::getInstance().get_device(device_number), LMS7_DC_BYP_RXTSP, 1);
    LMS_WriteParam(
        device_handler_fpga::getInstance().get_device(device_number), LMS7_DCLOOP_STOP, 1);
}

void device_handler_fpga::set_tcxo_dac(int device_number, uint16_t dacVal)
{
    GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::set_txco_dac(): ");
    float_type dac_value = dacVal;

    LMS_WriteCustomBoardParam(device_handler_fpga::getInstance().get_device(device_number),
                              BOARD_PARAM_DAC,
                              dacVal,
                              NULL);

    LMS_ReadCustomBoardParam(device_handler_fpga::getInstance().get_device(device_number),
                             BOARD_PARAM_DAC,
                             &dac_value,
                             NULL);

    GR_LOG_INFO(d_logger, boost::format("VCTCXO DAC value set: %u") % dac_value);
}

void device_handler_fpga::set_rfe_device(rfe_dev_t* rfe_dev) { rfe_device.rfe_dev = rfe_dev; }

void device_handler_fpga::update_rfe_channels()
{
    if (rfe_device.rfe_dev) {
        GR_LOG_DEBUG(d_debug_logger, "device_handler_fpga::update_rfe_channels(): ");
        if (RFE_AssignSDRChannels(
                rfe_device.rfe_dev, rfe_device.rx_channel, rfe_device.tx_channel) != 0) {
            throw std::runtime_error("Failed to assign SDR channels");
        }
        GR_LOG_INFO(
            d_logger,
            boost::format("RFE RX channel: %d TX channel: %d")
                % rfe_device.rx_channel
                % rfe_device.tx_channel);
    } else {
        throw std::runtime_error("device_handler_fpga::update_rfe_channels(): no assigned RFE device");
    }
}

void device_handler_fpga::write_lms_reg(int device_number, uint32_t address, uint16_t val)
{
    LMS_WriteLMSReg(
        device_handler_fpga::getInstance().get_device(device_number), address, val);
}


int device_handler_fpga::modify_spi_reg_bits(lms_device_t *device, const DSPCFGParameter &param, const uint16_t value)
{
    return modify_spi_reg_bits(device, param.address, param.msb, param.lsb, value);
}

int device_handler_fpga::modify_spi_reg_bits(lms_device_t *device, const uint16_t address, const uint8_t msb, const uint8_t lsb, const uint16_t value) {
    
    uint16_t spiDataReg;
    if (LMS_ReadFPGAReg(device, address, &spiDataReg) != LMS_SUCCESS) { //read current SPI reg data
        return -1;
    }
    
    uint16_t spiMask = (~(~0u << (msb - lsb + 1))) << (lsb); // creates bit mask
    spiDataReg = (spiDataReg & (~spiMask)) | ((value << lsb) & spiMask);//clear bits

    return LMS_WriteFPGAReg(device, address, spiDataReg); //write modified data back to SPI reg
}

int device_handler_fpga::read_spi_reg_bits(lms_device_t *device, const DSPCFGParameter &param)
{
    return read_spi_reg_bits(device, param.address, param.msb, param.lsb);
}

int device_handler_fpga::read_spi_reg_bits(lms_device_t *device, const uint16_t address, const uint8_t msb, const uint8_t lsb) {
    
    uint16_t spiDataReg;
    if (LMS_ReadFPGAReg(device, address, &spiDataReg) != LMS_SUCCESS) { //read current SPI reg data
        return -1;
    }
    
    uint16_t spiMask = (~(~0u << (msb - lsb + 1))) << (lsb); // creates bit mask
    spiDataReg = (spiDataReg & spiMask) >> lsb; //clear bits

    return spiDataReg;
}

void device_handler_fpga::set_gpio_dir(int device_number, uint8_t dir)
{
  LMS_GPIODirWrite(device_handler_fpga::getInstance().get_device(device_number), &dir, 1);
}

void device_handler_fpga::write_gpio(int device_number, uint8_t out)
{
  LMS_GPIOWrite(device_handler_fpga::getInstance().get_device(device_number), &out, 1);
}

uint8_t device_handler_fpga::read_gpio(int device_number)
{
  uint8_t res;

  LMS_GPIORead(device_handler_fpga::getInstance().get_device(device_number), &res, 1);

  return res;
}

void device_handler_fpga::set_dspcfg_preamble(int device_number, uint16_t dspcfg_PASSTHROUGH_LEN, uint8_t dspcfg_THRESHOLD, int dspcfg_preamble_en) { 
    std::cout << "INFO: device_handler_fpga::set_dspcfg_preamble(): ";
    if (modify_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number),DSPCFGparam(PREAMBLE_EN), dspcfg_preamble_en) != LMS_SUCCESS) {
        std::cout
            << "ERROR: device_handler_fpga::set_dspcfg_preamble_en(): cannot modify the register"
            << std::endl;
    }
    if (dspcfg_preamble_en) {
        std::cout << "Preamble Detector Enabled" << std::endl;
        set_dspcfg_clear_rs(device_number, 1);
        
        set_dspcfg_PASSTHROUGH_LEN(device_number, dspcfg_PASSTHROUGH_LEN);
        set_dspcfg_THRESHOLD(device_number, dspcfg_THRESHOLD);
        
        set_dspcfg_clear_rs(device_number, 0);
    
        uint16_t spiDataRegX;
        spiDataRegX = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PASSTHROUGH_LEN); 
        std::cout << "Passthrough length: " << spiDataRegX << std::endl;
        
        uint16_t spiDataRegThresh;
        spiDataRegThresh = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_THRESHOLD); 
        std::cout << "Detection threshold: " << spiDataRegThresh << std::endl;
        
        
        //sum-count
        uint32_t spiDataReg;
        uint16_t spiDataReg_MSB;
        uint16_t spiDataReg_LSB;
        spiDataReg_MSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_SHORT_SUM_MSB);
        spiDataReg_LSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_SHORT_SUM_LSB);
    	spiDataReg = ((uint32_t) spiDataReg_MSB) << 16 | ((uint32_t) spiDataReg_LSB);
        std::cout << "Short sum: " << spiDataReg << std::endl;

        spiDataReg_MSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_LONG_SUM_MSB);
        spiDataReg_LSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_LONG_SUM_LSB);
    	spiDataReg = ((uint32_t) spiDataReg_MSB) << 16 | ((uint32_t) spiDataReg_LSB);
        std::cout << "Long sum: " << spiDataReg << std::endl;
        
        spiDataReg_MSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_COUNT_MSB);
        spiDataReg_LSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_COUNT_LSB);
        spiDataReg = ((uint32_t) spiDataReg_MSB) << 16 | ((uint32_t) spiDataReg_LSB);
        std::cout << "count: " << spiDataReg << std::endl;
    }
}

void device_handler_fpga::set_dspcfg_PASSTHROUGH_LEN(int device_number, uint16_t dspcfg_PASSTHROUGH_LEN) {
    if (modify_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number),DSPCFGparam(PASSTHROUGH_LEN), dspcfg_PASSTHROUGH_LEN) != LMS_SUCCESS) {
        std::cout
            << "ERROR: device_handler_fpga::set_dspcfg_PASSTHROUGH_LEN(): cannot modify the register"
            << std::endl;
    }
}

void device_handler_fpga::set_dspcfg_THRESHOLD(int device_number, uint8_t dspcfg_THRESHOLD) {
    if (modify_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number),DSPCFGparam(THRESHOLD), dspcfg_THRESHOLD & 0xff) != LMS_SUCCESS) {
        std::cout
            << "ERROR: device_handler_fpga::set_dspcfg_THRESHOLD(): cannot modify the register"
            << std::endl;
    }
}

void device_handler_fpga::set_dspcfg_clear_rs(int device_number, int setting) {
    if (modify_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number),DSPCFGparam(CLEAR_RS), setting) != LMS_SUCCESS) {
        std::cout
            << "ERROR: device_handler_fpga::set_dspcfg_clear_rs(): cannot modify the register"
            << std::endl;
    }
}

uint32_t device_handler_fpga::get_dspcfg_short_sum(int device_number) {
        //sum-count
        uint32_t spiDataReg;
        uint16_t spiDataReg_MSB;
        uint16_t spiDataReg_LSB;
        spiDataReg_MSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_SHORT_SUM_MSB);
        spiDataReg_LSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_SHORT_SUM_LSB);
    	spiDataReg = ((uint32_t) spiDataReg_MSB) << 16 | ((uint32_t) spiDataReg_LSB);

        return spiDataReg;
}

uint32_t device_handler_fpga::get_dspcfg_long_sum(int device_number) {
        //sum-count
        uint32_t spiDataReg;
        uint16_t spiDataReg_MSB;
        uint16_t spiDataReg_LSB;
        spiDataReg_MSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_LONG_SUM_MSB);
        spiDataReg_LSB = read_spi_reg_bits(device_handler_fpga::getInstance().get_device(device_number), DSPCFG_PREAMBLE_LONG_SUM_LSB);
    	spiDataReg = ((uint32_t) spiDataReg_MSB) << 16 | ((uint32_t) spiDataReg_LSB);

        return spiDataReg;
}
