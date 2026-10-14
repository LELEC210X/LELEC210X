/*
 * acquisition.c
 */

#include "acquisition.h"

#include "main.h"
#include "config.h"

// Exported variables
volatile uint16_t *samples_buf_to_process; // Pointer to the buffer to process
volatile uint8_t is_processing = 0; // State variable to signal main loop and prevent timing constraint violation

// Local variables
static uint16_t samples_single_buf[10000]; // Single buffer for raw samples
static volatile uint8_t is_acq_running = 0; // State variable to prevent re-entering acquisition start or stop

// External variables
extern ADC_HandleTypeDef hadc1;
extern TIM_HandleTypeDef htim3;

/*
 * @brief Start the acquisition of audio samples.
 * @retval 0 if success, 1 if acquisition is already running.
 * @note This function will be implemented and used in P2b.
 */
int acquisition_start(void)
{
	if (is_acq_running) {
		return 1;
	}
	is_acq_running = 1;

	// TODO P2b

	return 0;
}

/*
 * @brief Stop the acquisition of audio samples.
 * @retval 0 if success, 1 if acquisition is already stopped.
 * @note This function will be implemented and used in P2c.
 */
int acquisition_stop(void)
{
	if (!is_acq_running) {
		return 1;
	}

	// TODO P2b

	is_acq_running = 0;
	return 0;
}


/*
 * @brief Print samples as hexadecimal bytes, with a prefix.
 * @param[in]   samples  array of samples to print
 * @param[in]   length   length of that array (in number of samples)
 */
void print_raw_samples(uint16_t *samples, size_t length)
{
#if DEBUGP
	DEBUG_PRINT("RAW:HEX:");
	for (size_t i=0; i < length; ++i) {
		DEBUG_PRINT("%04x", samples[i]);
	}
	DEBUG_PRINT("\r\n");
#endif // DEBUGP
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
	// TODO P2b
}
