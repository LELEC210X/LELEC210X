/*
 * config.h
 */

#ifndef INC_CONFIG_H_
#define INC_CONFIG_H_

#include <stdio.h>

// Runtime parameters
#define MAIN_APP 0
#define EVAL_RADIO 1

#define RUN_CONFIG EVAL_RADIO

// Radio parameters
#define ENABLE_RADIO 1

// General UART enable/disable (disable for low-power operation)
#define ENABLE_UART 1

// In continuous mode, we start and stop continuous acquisition on button press.
// In non-continuous mode, we send a single packet on button press.
#define CONTINUOUS_ACQ 1

// Spectrogram parameters
#define SAMPLES_PER_MELVEC 512
#define MELVEC_LENGTH 16
#define N_MELVECS 10*2

// Enable performance measurements
#define PERF_COUNT 1

// Enable debug print
#define DEBUGP 1

#if (DEBUGP == 1)
#define DEBUG_PRINT(...) do{ printf(__VA_ARGS__ ); } while( 0 )
#else
#define DEBUG_PRINT(...) do{ } while ( 0 )
#endif



#endif /* INC_CONFIG_H_ */
