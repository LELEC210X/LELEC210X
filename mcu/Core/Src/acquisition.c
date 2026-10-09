/*
 * acquisition.c
 */

#include "acquisition.h"

#include "main.h"
#include "config.h"

// Exported variables
volatile uint16_t *samples_buf_to_process; // Pointer to one of the two buffers
volatile uint8_t is_processing = 0; // State variable to signal main loop and prevent timing constraint violation

// Local variables
static volatile uint16_t samples_double_buf[2*SAMPLES_PER_MELVEC]; // Double buffer for raw samples
static volatile uint16_t *samples_buf[2] = {&samples_double_buf[0], &samples_double_buf[SAMPLES_PER_MELVEC]}; // These are simply pointers to first and middle point of double buf
static volatile uint8_t is_acq_running = 0; // State variable to prevent re-entering acquisition start or stop

// External variables
extern ADC_HandleTypeDef hadc1;

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

	// TODO P2b : use HAL functions to start the acquisition.

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

	// TODO P2c : use HAL functions to stop the acquisition.

	is_acq_running = 0;
	return 0;
}


/*
 * @brief Print samples as hexadecimal bytes, with a prefix.
 * @param[in]   samples  array of samples to print
 * @param[out]  length   length of that array (in number of samples)
 */
void print_raw_samples(uint16_t *samples, size_t length)
{
	DEBUG_PRINT("RAW:HEX:");
	for (size_t i=0; i < length; ++i) {
		DEBUG_PRINT("%04x", samples[i]);
	}
	DEBUG_PRINT("\r\n");
}

/*
 * @brief Callback when one of the two buffers is ready for processing.
 * @param[in]  buf_cplt  Buffer ready index (0 or 1).
 * @note This function and the callbacks below will be used in P2b.
 */
static void process_samples_buf(int buf_cplt)
{
	if (is_processing) { // check if the other buffer is still processing
		DEBUG_PRINT("Error : Samples buffer full (timing constraint violation)\r\n");
		Error_Handler();
	}
	samples_buf_to_process = samples_buf[buf_cplt];
	is_processing = 1;
}

void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc)
{
	process_samples_buf(0);
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
	process_samples_buf(1);
}
