/*
 * spectrogram.h
 *
 *  Created on: Oct 7, 2021
 *      Author: Teaching Assistants of LELEC210x
 */

#ifndef INC_SPECTROGRAM_H_
#define INC_SPECTROGRAM_H_

#include "arm_math.h"

// Convert 12-bit DC ADC samples to Q1.15 fixed point signal and remove DC component
void Spectrogram_Format(q15_t *buf);

// Compute spectrogram of samples and transform into MEL vectors.
void Spectrogram_Compute(q15_t *samples, q15_t *melvector);

#endif /* INC_SPECTROGRAM_H_ */
