/*
 * eval_radio.c
 */

#include <adc_dblbuf.h>
#include "eval_radio.h"
#include "config.h"
#include "main.h"
#include "s2lp.h"


void eval_radio(void)
{
	DEBUG_PRINT("[DBG] Radio evaluation mode\r\n");

	uint8_t buf[PAYLOAD_LEN];
	for (uint16_t i=0; i < PAYLOAD_LEN; i++) {
		buf[i] = (uint8_t) (i & 0xFF);
	}

	for (int32_t lvl = MIN_PA_LEVEL; lvl <= MAX_PA_LEVEL; lvl++) {
		btn_press = 0;
		DEBUG_PRINT("=== Press button B1 to start evaluation at %ld dBm\r\n", lvl);
		while (!btn_press) {
			__WFI();
		}

		S2LP_SetPALeveldBm(lvl);
		DEBUG_PRINT("=== Configured PA level to %ld dBm, sending %d packets at this level\r\n", lvl, N_PACKETS);

		for (uint16_t i=0; i < N_PACKETS; i++) {
			HAL_StatusTypeDef err = S2LP_Send(buf, PAYLOAD_LEN);
			if (err) {
				Error_Handler();
			}

			for(uint16_t j=0; j < PACKET_DELAY; j++) {
				HAL_GPIO_WritePin(GPIOB, LD2_Pin, GPIO_PIN_SET);
				HAL_Delay(500);
				HAL_GPIO_WritePin(GPIOB, LD2_Pin, GPIO_PIN_RESET);
				HAL_Delay(500);
			}
		}
	}

	DEBUG_PRINT("=== Finished evaluation, reset the board to run again\r\n");
	while (1);
}
