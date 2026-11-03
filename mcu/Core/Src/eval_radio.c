/*
 * eval_radio.c
 */

#include "eval_radio.h"
#include "config.h"
#include "main.h"
#include "spi.h"
#include "s2lp.h"
#include "utils.h"

#include <string.h>

static volatile uint16_t n_packets  = INIT_N_PACKETS;
static volatile  int16_t pa_lvl		= INIT_PA_LEVEL;

volatile uint8_t btn_press;

extern UART_HandleTypeDef hlpuart1;

#define RX_BUF_LEN 64
static uint8_t  rx_byte;
static uint8_t  rx_buf[RX_BUF_LEN];
static uint16_t rx_idx = 0;
static volatile uint8_t cmd_ready = 0;

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  if (huart->Instance == LPUART1)
  {
    if (rx_byte == '\n' && (!cmd_ready)) // 
    {
		rx_buf[rx_idx] = '\0';
		cmd_ready = 1;
      	rx_idx = 0;
    }
    else if (rx_idx < RX_BUF_LEN - 1)   	
      	rx_buf[rx_idx++] = (char)rx_byte;
    else
      	rx_idx = 0;                            // line too long: drop it
    
    HAL_UART_Receive_IT(&hlpuart1, &rx_byte, 1);   // re-arm
  }
}

static void process_command(uint8_t *buffer)
{
	char key[8];
	long val;
	char end;

	// Format: "<LETTERS> <int>", e.g. "NPKT 10".
	// The trailing %c catches garbage: we want exactly 2 fields.
	int n = sscanf((char *)buffer, "%7[A-Za-z] %ld %c", key, &val, &end);

	if (n != 2){
		DEBUG_PRINT("ERR syntax: expected <LETTERS> <int>, e.g. NPKT 10\r\n");
		return;
	}

	if ((strcmp(key, "NPKT") == 0) || (strcmp(key, "N") == 0)) {
		n_packets = (uint16_t)val;
	}
	else if ((strcmp(key, "PA") == 0) || (strcmp(key, "P") == 0)) {
		pa_lvl = (int16_t)val;
	}
	else {
		DEBUG_PRINT("ERR unknown command '%s' (use NPKT or PA)\r\n", key);
	}
}

void eval_radio_start(void)
{
	DEBUG_PRINT("[DBG] Radio evaluation mode\r\n");
	#if ENABLE_RADIO
		DEBUG_PRINT("[S2LP] Radio already init\r\n");
	#else
	HAL_StatusTypeDef err = S2LP_Init(&hspi1);
	if (err)  {
		DEBUG_PRINT("[S2LP] Error while initializing: %u\r\n", err);
		Error_Handler();
	} else {
		DEBUG_PRINT("[S2LP] Init OK\r\n");
	}
	#endif
	
  	HAL_UART_Receive_IT(&hlpuart1, &rx_byte, 1);

	uint8_t buf[PAYLOAD_LEN];
	for (uint16_t i=0; i < PAYLOAD_LEN; i++) {
		buf[i] = (uint8_t) (i & 0xFF);
	}

	while(1) {
		btn_press = 0;
		DEBUG_PRINT("=== Press button B1 to send %d packets at %d dBm\r\n", n_packets, pa_lvl);
		while (!btn_press) {
			
			__WFI();
			if (cmd_ready==1) {
				process_command(rx_buf);
				cmd_ready = 0;
				DEBUG_PRINT("=== Press button B1 to send %d packets at %d dBm\r\n", n_packets, pa_lvl);
			} 
		}

		DEBUG_PRINT("=== Start sending === \r\n");
		S2LP_SetPALeveldBm(pa_lvl);

		for (uint16_t i=0; i < n_packets; i++) {
			HAL_StatusTypeDef err = S2LP_Send(buf, PAYLOAD_LEN);
			if (err) {
				Error_Handler();
			}

			if (BLINK_LED==1){
				HAL_GPIO_WritePin(GPIOB, LD2_Pin, GPIO_PIN_SET);
				HAL_Delay(PACKET_DELAY>>1);
				HAL_GPIO_WritePin(GPIOB, LD2_Pin, GPIO_PIN_RESET);
				HAL_Delay(PACKET_DELAY>>1);
			} else{
				HAL_Delay(PACKET_DELAY);
			}
		}
	}

	DEBUG_PRINT("=== Finished evaluation, reset the board to run again\r\n");
	while (1);
}
