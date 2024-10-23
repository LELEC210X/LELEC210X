/**
@file	fpga_register_map.h
@author Julien Verecken
@brief 	List of Custom FPGA control parameters
*/

#ifndef FPGA_REGISTER_MAP_H
#define FPGA_REGISTER_MAP_H
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DSPCFGparam(id) DSPCFG_ ## id

struct DSPCFGParameter
{
    uint16_t address;
    uint8_t msb;
    uint8_t lsb;
    uint16_t defaultValue;
    const char* name;
    const char* tooltip;
};

static const struct DSPCFGParameter DSPCFG_PASSTHROUGH_LEN = { 0x000b, 15, 0, 255, "" };
static const struct DSPCFGParameter DSPCFG_THRESHOLD       = { 0x000d, 7, 0, 12, "" };
static const struct DSPCFGParameter DSPCFG_CLEAR_RS   = { 0x000e, 1, 1, 0, "" };
static const struct DSPCFGParameter DSPCFG_PREAMBLE_EN = { 0x000e, 0, 0, 0, "" };
static const struct DSPCFGParameter DSPCFG_PREAMBLE_SHORT_SUM_MSB = { 0x000f, 15, 0, 0, "" };
static const struct DSPCFGParameter DSPCFG_PREAMBLE_SHORT_SUM_LSB = { 0x0010, 15, 0, 0, "" };
static const struct DSPCFGParameter DSPCFG_PREAMBLE_LONG_SUM_MSB = { 0x0011, 15, 0, 0, "" };
static const struct DSPCFGParameter DSPCFG_PREAMBLE_LONG_SUM_LSB = { 0x0012, 15, 0, 0, "" };
static const struct DSPCFGParameter DSPCFG_PREAMBLE_COUNT_MSB = { 0x0013, 15, 0, 0, "" };
static const struct DSPCFGParameter DSPCFG_PREAMBLE_COUNT_LSB = { 0x0014, 15, 0, 0, "" };

#ifdef __cplusplus
}
#endif

#endif
