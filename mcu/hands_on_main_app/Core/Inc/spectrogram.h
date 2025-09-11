/*
 * feature_sel.h
 *
 *  Created on: Jun 4, 2021
 *      Author: math
 */

#ifndef INC_SPECTROGRAM_H_
#define INC_SPECTROGRAM_H_

#include "arm_math.h"

static inline float q15_to_float(q15_t x)
{
	float y;
	arm_q15_to_float(&x, &y, 1);
	return y;
}

static inline q15_t float_to_q15(float x)
{
	q15_t y;
	arm_float_to_q15(&x, &y, 1);
	return y;
}

// Convert 12-bit DC ADC samples to Q1.15 fixed point signal and remove DC component
void Spectrogram_Format(q15_t *buf);

// Compute spectrogram of samples into melvec. Modifies samples.
void Spectrogram_Compute(q15_t *samples, q15_t *melvector);

#endif /* INC_SPECTROGRAM_H_ */
