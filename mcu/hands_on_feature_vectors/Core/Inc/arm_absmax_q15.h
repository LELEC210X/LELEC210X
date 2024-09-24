/*
 * arm_absmax_q15.h
 *
 *  Created on: Sep 23, 2021
 *      Author: marconi
 */

#ifndef INC_ARM_ABSMAX_Q15_H_
#define INC_ARM_ABSMAX_Q15_H_

#include "arm_math.h"

/**
 * @brief Maximum value of absolute values of a Q15 vector.
 * @param[in]  pSrc       points to the input buffer
 * @param[in]  blockSize  length of the input vector
 * @param[out] pResult    maximum value returned here
 * @param[out] pIndex     index of maximum value returned here
 */
  void arm_absmax_q15(
  const q15_t * pSrc,
        uint32_t blockSize,
        q15_t * pResult,
        uint32_t * pIndex);


#endif /* INC_ARM_ABSMAX_Q15_H_ */
