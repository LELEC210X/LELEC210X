/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2026 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "adc.h"
#include "dma.h"
#include "spi.h"
#include "tim.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "config.h"
#include "arm_math.h"
#include "usart.h"
#include "utils.h"
#include "s2lp.h"
#include "acquisition.h"
#include "computation.h"
#include "transfer.h"
#include "eval_radio.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
// From acquisition
extern volatile uint16_t *samples_buf_to_process;
extern volatile uint8_t processing_signal;
// From computation
extern q15_t mel_vectors[N_MELVECS][MELVEC_LENGTH];
extern volatile uint8_t cur_melvec;
// From transfer
extern uint8_t packet[PACKET_LENGTH];
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	if (GPIO_Pin == B1_Pin) { // User button
#if (RUN_CONFIG == EVAL_RADIO)
		eval_radio_continue();
#else // MAIN_APP
		if (acquisition_start()) {
			DEBUG_PRINT("Acquisition already running, not started\r\n");
		} else {
			DEBUG_PRINT("Acquisition started\r\n");
		}
#endif // RUN_CONFIG
	}
	else if (GPIO_Pin == RADIO_INT_Pin) { // S2LP radio
		S2LP_IRQ_Handler();
	}
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

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_SPI1_Init();
  MX_TIM3_Init();
  MX_ADC1_Init();
  /* USER CODE BEGIN 2 */
#if DEBUGP
	MX_LPUART1_UART_Init();
	DEBUG_PRINT("Hello :)\r\n");
#endif
#if ENABLE_RADIO
  HAL_StatusTypeDef err = S2LP_Init(&hspi1);
  if (err)  {
	  DEBUG_PRINT("[S2LP] Error while initializing: %u\r\n", err);
	  Error_Handler();
  } else {
	  DEBUG_PRINT("[S2LP] Init OK\r\n");
  }
#endif
#if (RUN_CONFIG == EVAL_RADIO)
  eval_radio_start();
#else // MAIN_APP
  DEBUG_PRINT("Press the blue button to start acquisition.\r\n");
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
	while (1)
	{
		if (processing_signal) {
			melvec_compute((q15_t *)samples_buf_to_process, mel_vectors[cur_melvec]);
			processing_signal = 0;
			if (++cur_melvec == N_MELVECS) { // all melvec computed
				cur_melvec = 0;
				acquisition_stop();
				print_melvectors();
				make_packet();
				send_packet();
#if CONTINUOUS_ACQ
				acquisition_start();
#endif // CONTINUOUS_ACQ
			}
		}
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
	}
#endif // RUN_CONFIG == EVAL_RADIO
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
  RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_11;
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

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
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
	__disable_irq();
	DEBUG_PRINT("Entering error Handler\r\n");
	while (1)
	{
		// Blink LED3 (red)
		HAL_GPIO_WritePin(GPIOB, LD3_Pin, GPIO_PIN_SET);
		for (volatile int i=0; i < SystemCoreClock/200; i++);
		HAL_GPIO_WritePin(GPIOB, LD3_Pin, GPIO_PIN_RESET);
		for (volatile int i=0; i < SystemCoreClock/200; i++);
	}
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
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
