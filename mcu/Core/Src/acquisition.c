/*
 * acquisition.c
 */

#include "acquisition.h"

#include "main.h"
#include "config.h"

// Exported variables
volatile uint16_t *samples_buf_to_process; // Pointer to one of the two buffers
volatile uint8_t processing_signal = 0; // State variable to signal main loop and prevent timing constraint violation

// Local variables
static volatile uint16_t samples_double_buf[2*SAMPLES_PER_MELVEC]; // Double buffer for raw samples
static volatile uint16_t *samples_buf[2] = {&samples_double_buf[0], &samples_double_buf[SAMPLES_PER_MELVEC]}; // These are simply pointers to first and middle point of double buf
static volatile uint8_t is_acq_running = 0; // State variable to prevent re-entering acquisition start or stop

// External variables
extern ADC_HandleTypeDef hadc1;
extern TIM_HandleTypeDef htim3;

/*
 * @brief Start the acquisition of audio samples
 * @retval 0 if success, 1 if acquisition is already running
 */
int acquisition_start(void)
{
	if (is_acq_running) {
		return 1;
	}
	is_acq_running = 1;
	if (HAL_ADCEx_Calibration_Start(&hadc1, ADC_SINGLE_ENDED) != HAL_OK) {
		DEBUG_PRINT("Error calibrating ADC\r\n");
		Error_Handler();
	}
	if (HAL_ADC_Start_DMA(&hadc1, (uint32_t *)samples_double_buf, 2*SAMPLES_PER_MELVEC) != HAL_OK) {
		DEBUG_PRINT("Error starting ADC\r\n");
		Error_Handler();
	}
	if (HAL_TIM_Base_Start(&htim3) != HAL_OK) {
		DEBUG_PRINT("Error starting TIM3\r\n");
		Error_Handler();
	}
	return 0;
}

/*
 * @brief Stop the acquisition of audio samples
 * @retval 0 if success, 1 if acquisition is already stopped
 */
int acquisition_stop(void)
{
	if (!is_acq_running) {
		return 1;
	}
	if (HAL_TIM_Base_Stop(&htim3) != HAL_OK) {
		DEBUG_PRINT("Error stopping TIM3\r\n");
		Error_Handler();
	}
	if (HAL_ADC_Stop_DMA(&hadc1) != HAL_OK) {
		DEBUG_PRINT("Error stopping ADC\r\n");
		Error_Handler();
	}
	is_acq_running = 0;
	return 0;
}

static void process_samples_buf(int buf_cplt)
{
	if (processing_signal) { // check if the other buffer is still processing
		DEBUG_PRINT("Error : Samples buffer full (timing constraint violation)\r\n");
		Error_Handler();
	}
	samples_buf_to_process = samples_buf[buf_cplt];
	processing_signal = 1;
}

void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc)
{
	process_samples_buf(0);
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
	process_samples_buf(1);
}
