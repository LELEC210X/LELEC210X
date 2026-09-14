/*
 * config.h
 */

#ifndef INC_CONFIG_H_
#define INC_CONFIG_H_

#include <stdio.h>

// Runtime parameters
#define MAIN_APP 0 // Acquire audio samples, compute melspectrogram and transfer data
#define EVAL_RADIO 1 // Send packets for telecom testing purposes
#define RUN_CONFIG MAIN_APP // Choose here the config to run

// In continuous mode, we start continuous acquisition on button press.
// In non-continuous mode, we send a single packet on button press.
#define CONTINUOUS_ACQ 0

// Spectrogram parameters
#define SAMPLES_PER_MELVEC 512
#define MELVEC_LENGTH 20
#define N_MELVECS 20

// Radio parameters -- used in Drivers/S2LP/*
#define ENABLE_RADIO 1
#define BASE_FREQ 868000000 // Carrier frequency, in Hz
#define DATARATE 50000 // Data rate in 2FSK, in bit/s
#define FREQDEV DATARATE/4 // Frequency deviation, in Hz
#define PA_LEVEL 0 // Tx output power, in dBm

// Enable performance measurements
#define PERF_COUNT 1

// Enable debug print through UART
#define DEBUGP 1

// Encapsulate printf to prevent wasting resources in string formatting if not needed
#if DEBUGP
#define DEBUG_PRINT(...) do{ printf(__VA_ARGS__ ); } while( 0 )
#else
#define DEBUG_PRINT(...) do{ } while ( 0 )
#endif

#endif /* INC_CONFIG_H_ */
