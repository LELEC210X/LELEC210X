/*
 * acquisition.h
 */

#ifndef INC_ACQUISITION_H_
#define INC_ACQUISITION_H_

#include "main.h"

// Exported variables
extern volatile uint16_t *samples_buf_to_process;
extern volatile uint8_t is_processing;

// Exported function prototypes
int acquisition_start(void);
int acquisition_stop(void);
void print_raw_samples(uint16_t *samples, size_t length);

#endif /* INC_ACQUISITION_H_ */
