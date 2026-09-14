/*
 * computation.h
 */

#ifndef INC_COMPUTATION_H_
#define INC_COMPUTATION_H_

#include "arm_math.h"
#include "config.h"

// Exported variables
extern q15_t mel_vectors[N_MELVECS][MELVEC_LENGTH];
extern volatile uint8_t cur_melvec;

// Exported function prototype
void melvec_compute(q15_t *samples, q15_t *melvec);
void print_melvectors(void);

#endif /* INC_COMPUTATION_H_ */
