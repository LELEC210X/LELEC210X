/*
 * utils.c
 */

#include "config.h"
#include "main.h"


#if PERF_COUNT

static volatile uint8_t counting_cycles = 0;
void start_cycle_count() {
	uint32_t prim = __get_PRIMASK();
	__disable_irq();
	if (counting_cycles) {
		DEBUG_PRINT("Tried re-entrant cycle counting.\r\n");
		Error_Handler();
	} else {
		counting_cycles = 1;
	}
	if (!prim) {
		__enable_irq();
	}
	DWT->CTRL |= 1 ; // enable the counter
	DWT->CYCCNT = 0; // reset the counter
}
void stop_cycle_count(char *s) {
	uint32_t res = DWT->CYCCNT;
	counting_cycles = 0;
	printf("[PERF] ");
	printf(s);
	printf(" %lu cycles.\r\n", res);
}

#else

void start_cycle_count() {}
void stop_cycle_count(char *s) {}

#endif // PERF_COUNT


#if DEBUGP
// Redirect printf calls through UART by overriding the weak _write function
extern UART_HandleTypeDef hlpuart1;
int _write(int file, char *ptr, int len)
{
	UNUSED(file);
	HAL_UART_Transmit(&hlpuart1, (uint8_t *) ptr, len, HAL_MAX_DELAY);
	return len;
}
#endif // DEBUGP
