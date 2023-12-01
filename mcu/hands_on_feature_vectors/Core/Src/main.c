/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "adc.h"
#include "dma.h"
#include "usart.h"
#include "tim.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include "retarget.h"
#include "config.h"
#include "arm_math.h"
#include "spectrogram.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */
#define DEBUG 0
#define DEBUG_PRINT(...) do{ if (DEBUG) printf(__VA_ARGS__ ); } while( 0 )
/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
volatile uint8_t counting_cycles = 0;

volatile int state = 0;
volatile int bounce = 0;
volatile uint16_t ADCBuffer[2*SAMPLES_PER_MELVEC]; /* ADC write buffer (via DMA) */
volatile uint16_t* ADCDblBuffer[2] = {&ADCBuffer[0], &ADCBuffer[SAMPLES_PER_MELVEC]};

static volatile uint8_t cur_melvec = 0;

static q15_t *mel_vectors[N_MELVECS];
// Contiguous array in memory
static q15_t mel_vectors_flat[N_MELVECS * MELVEC_LENGTH];

char hex_encoded_buffer[sizeof(q15_t) * 2 * N_MELVECS * MELVEC_LENGTH + 1];
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
void hex_encode(char* s, const uint8_t* buf, size_t len);
void print_buffer(volatile uint16_t *buffer, size_t len);
uint32_t get_signal_power(uint16_t *buffer, size_t len);
void start_cycle_count();
void stop_cycle_count(char *s);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
	if ((GPIO_Pin == B1_Pin) & !bounce) {
		HAL_ADC_Start_DMA(&hadc1, (uint32_t *) ADCBuffer, 2 * SAMPLES_PER_MELVEC);
		HAL_TIM_Base_Start(&htim3);
		bounce = 1;
	}
}

void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc) {
	Spectrogram_Format((q15_t *)ADCDblBuffer[0]);
	Spectrogram_Compute((q15_t *)ADCDblBuffer[0], mel_vectors[cur_melvec]);
	cur_melvec++;
	DEBUG_PRINT("Half DMA.\r\n");
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
	Spectrogram_Format((q15_t *)ADCDblBuffer[1]);
	Spectrogram_Compute((q15_t *)ADCDblBuffer[1], mel_vectors[cur_melvec]);
	cur_melvec++;
	if (cur_melvec == N_MELVECS)
	{
		HAL_TIM_Base_Stop(&htim3);
		HAL_ADC_Stop_DMA(&hadc1);
		print_buffer(mel_vectors_flat, N_MELVECS * MELVEC_LENGTH);
		cur_melvec = 0;
	}
	bounce = 0;
	DEBUG_PRINT("All DMA.\r\n");
}

// Starts the cycle counter
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
	DWT->CTRL |= 1 ; // Enable the cycle counter
	DWT->CYCCNT = 0; // Reset the cycle counter
}

// Stop the cycle counter
// char *s allows to print a header (title of the measured block) before reporting the number of cycles
void stop_cycle_count(char *s) {
	uint32_t res = DWT->CYCCNT; // Read the cycle counter
	counting_cycles = 0;
	printf("[PERF] ");
	printf(s);
	printf(" %lu cycles.\r\n", res);
}

void hex_encode(char* s, const uint8_t* buf, size_t len) {
  s[2*len] = '\0'; // A string terminated by a zero char.
  for (size_t i=0; i<len; i++) {
      s[i*2  ] = "0123456789abcdef"[buf[i] >> 4];
      s[i*2+1] = "0123456789abcdef"[buf[i] & 0xF];
  }
}

void print_buffer(volatile uint16_t *buffer, size_t len) {
	hex_encode(hex_encoded_buffer, (uint8_t*)buffer, sizeof(uint16_t) * len);
	printf("DF:HEX:%s\r\n", hex_encoded_buffer);
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
  // Reshape the contiguous memory array in a 2D array.
  for (int i = 0; i < N_MELVECS; i++)
  {
	  mel_vectors[i] = &mel_vectors_flat[i*MELVEC_LENGTH];
  }
  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_LPUART1_UART_Init();
  MX_TIM3_Init();
  MX_ADC1_Init();
  /* USER CODE BEGIN 2 */
  RetargetInit(&hlpuart1);
  printf("Hello world!\r\n");
  state=0;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	HAL_GPIO_WritePin(LD1_GPIO_Port, LD1_Pin, GPIO_PIN_SET);
	HAL_Delay(500);
	HAL_GPIO_WritePin(LD1_GPIO_Port, LD1_Pin, GPIO_PIN_RESET);
	HAL_Delay(500);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
  RCC_OscInitStruct.MSIState = RCC_MSI_ON;
  RCC_OscInitStruct.MSICalibrationValue = 0;
  RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_10;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_MSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
