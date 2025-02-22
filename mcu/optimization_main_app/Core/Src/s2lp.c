
#include <stdio.h>
#include <string.h>
#include "retarget.h"
#include "s2lp.h"
#include "s2lp_regs.h"
#include "config.h"

#include "main.h"

// S2LP_Send fails at non-zero optimization levels.
#pragma GCC optimize("O0")

SPI_HandleTypeDef *gSPI;
volatile uint8_t packet_sent = 0;
volatile uint8_t fifo_almost_empty = 0;
volatile uint8_t underflow = 0;

volatile uint16_t n_chunks_tx = 0;

HAL_StatusTypeDef S2LP_Command(uint8_t cmd, S2LPStatus *status)
{
	uint8_t TxBuf[2] = {0x80, cmd};
	uint8_t RxBuf[2];

	__disable_irq();
	HAL_GPIO_WritePin(RADIO_S2LP_CSN_GPIO_Port, RADIO_S2LP_CSN_Pin, GPIO_PIN_RESET);
	HAL_StatusTypeDef err = HAL_SPI_TransmitReceive(gSPI, TxBuf, RxBuf, 2, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(RADIO_S2LP_CSN_GPIO_Port, RADIO_S2LP_CSN_Pin, GPIO_PIN_SET);
	__enable_irq();

	memcpy(status, &RxBuf[0], 2);
	return err;
}

HAL_StatusTypeDef S2LP_ReadReg(uint8_t addr, uint8_t *retval, S2LPStatus *status)
{
	uint8_t TxBuf[] = {0x01, addr, 0x0};
	uint8_t RxBuf[3];

	__disable_irq();
	HAL_GPIO_WritePin(RADIO_S2LP_CSN_GPIO_Port, RADIO_S2LP_CSN_Pin, GPIO_PIN_RESET);
	HAL_StatusTypeDef err = HAL_SPI_TransmitReceive(gSPI, TxBuf, RxBuf, 3, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(RADIO_S2LP_CSN_GPIO_Port, RADIO_S2LP_CSN_Pin, GPIO_PIN_SET);
	__enable_irq();

	if (status != NULL)
		memcpy(status, &RxBuf[0], 2);
	if (retval != NULL)
		*retval = RxBuf[2];
	return err;
}

HAL_StatusTypeDef S2LP_WriteReg(uint8_t addr, uint8_t val, S2LPStatus *status)
{
	uint8_t TxBuf[] = {0x00, addr, val};
	uint8_t RxBuf[3];

	__disable_irq();
	HAL_GPIO_WritePin(RADIO_S2LP_CSN_GPIO_Port, RADIO_S2LP_CSN_Pin, GPIO_PIN_RESET);
	HAL_StatusTypeDef err = HAL_SPI_TransmitReceive(gSPI, TxBuf, RxBuf, 3, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(RADIO_S2LP_CSN_GPIO_Port, RADIO_S2LP_CSN_Pin, GPIO_PIN_SET);
	__enable_irq();

	if (status != NULL)
		memcpy(status, &RxBuf[0], 2);
	return err;
}

HAL_StatusTypeDef S2LP_WriteTxFIFO(uint8_t *chunk, uint8_t chunk_len, S2LPStatus *status)
{
	uint8_t TxBuf[FIFO_CHUNK_SIZE+2];
	uint8_t RxBuf[FIFO_CHUNK_SIZE+2];
	TxBuf[0] = 0;
	TxBuf[1] = 0xFF;
	memcpy((void *)&TxBuf[2], (void *)chunk, chunk_len);

	__disable_irq();
	HAL_GPIO_WritePin(RADIO_S2LP_CSN_GPIO_Port, RADIO_S2LP_CSN_Pin, GPIO_PIN_RESET);
	HAL_StatusTypeDef err = HAL_SPI_TransmitReceive(gSPI, TxBuf, RxBuf, chunk_len+2, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(RADIO_S2LP_CSN_GPIO_Port, RADIO_S2LP_CSN_Pin, GPIO_PIN_SET);
	__enable_irq();

	if (status != NULL)
		memcpy(status, &RxBuf[0], 2);
	return err;
}

HAL_StatusTypeDef S2LP_Send(uint8_t *payload, uint16_t pay_len)
{
	S2LPStatus radio_status;
	HAL_StatusTypeDef err;

	// Flush the Tx FIFO
	S2LP_Command(CMD_FLUSHTXFIFO, &radio_status);
	if (radio_status.MC_STATE != MC_STATE_READY) {
		DEBUG_PRINT("[S2LP] Error: radio is not ready\r\n");
		return HAL_BUSY;
	}
	// Reset global interrupt variables
	packet_sent = 0;
	underflow = 0;
	fifo_almost_empty = 0;

	// Set the packet length
	S2LP_WriteReg(PCKTLEN1_ADDR, (uint8_t) (pay_len >> 8), NULL);
	S2LP_WriteReg(PCKTLEN0_ADDR, (uint8_t) (pay_len & 0xFF), NULL);

	// Switch to lock Tx state
	while (radio_status.MC_STATE != MC_STATE_LOCKON) {
		err = S2LP_Command(CMD_LOCKTX, &radio_status);
		if (err) {
			DEBUG_PRINT("[S2LP] Error: cannot lock on Tx\r\n");
			return HAL_ERROR;
		}
	}

	// Fill Tx FIFO with payload chunks
	uint8_t sending = 0;
	uint16_t n_chunks = (pay_len / FIFO_CHUNK_SIZE) + (pay_len % FIFO_CHUNK_SIZE != 0);

	uint16_t free_chunks = FIFO_SIZE / FIFO_CHUNK_SIZE;

	for(uint16_t i=0; i < n_chunks; i++) {
		if (underflow) {
			DEBUG_PRINT("[S2LP] Error: Tx FIFO overflow or underflow!\r\n");
			err = S2LP_ReadReg(0, NULL, &radio_status); // fetch radio state
			if (!err) {
				S2LP_PrintStatus(&radio_status);
			} else {
				DEBUG_PRINT("[S2LP] Error: unable to fetch radio status!\r\n");
			}
			return HAL_ERROR;
		}

		while (free_chunks == 0) {
			if (!sending) {// if FIFO is full and we are not sending yet ...
				S2LP_Command(CMD_TX, &radio_status); // start the transmission
				sending = 1;
			}

			__WFI();
			if (fifo_almost_empty) {
				free_chunks = FIFO_SIZE/FIFO_CHUNK_SIZE - FIFO_EMPTY_THRESH;
				fifo_almost_empty = 0;
			}
		}

		uint8_t chunk_len = (i == n_chunks-1) ? pay_len-(n_chunks-1)*FIFO_CHUNK_SIZE : FIFO_CHUNK_SIZE;
		err = S2LP_WriteTxFIFO(&payload[i*FIFO_CHUNK_SIZE], chunk_len, &radio_status);
		if (err) {
			DEBUG_PRINT("[S2LP] Error: cannot fill Tx FIFO\r\n");
			return HAL_ERROR;
		}
		free_chunks--;
	}

	// Start transmission (for short payloads)
	if (!sending) {
		S2LP_Command(CMD_TX, &radio_status);
	}

	while (!packet_sent) {
		__WFI(); // wait until packet has been fully transmitted
	}

	DEBUG_PRINT("[S2LP] Packet transmitted!\r\n");
	return HAL_OK;
}

void S2LP_PrintStatus(S2LPStatus *status)
{
	DEBUG_PRINT("=== S2LP Status ===\r\n");
	DEBUG_PRINT("  MC_STATE: ");
	switch (status->MC_STATE) {
		case (MC_STATE_READY):
			DEBUG_PRINT("READY");
			break;
		case (MC_STATE_STANDBY):
			DEBUG_PRINT("STANDBY");
			break;
		case (MC_STATE_SLEEP):
			DEBUG_PRINT("SLEEP");
			break;
		case (MC_STATE_SLEEP_NOFIFO):
			DEBUG_PRINT("SLEEP");
			break;
		case (MC_STATE_LOCKON):
			DEBUG_PRINT("LOCKON");
			break;
		case (MC_STATE_RX):
			DEBUG_PRINT("RX");
			break;
		case (MC_STATE_LOCK_ST):
			DEBUG_PRINT("LOCK_ST");
			break;
		case (MC_STATE_TX):
			DEBUG_PRINT("TX");
			break;
		case (MC_STATE_SYNTH_SETUP):
			DEBUG_PRINT("SYNTH_SETUP");
			break;
		default:
			DEBUG_PRINT("UNKNOWN");
			break;
	}
	DEBUG_PRINT("\r\n");
	DEBUG_PRINT("  XO_ON=%u, ERROR_LOCK=%u, RX_fifo_empty=%u, TX_FIFO_FULL=%u\r\n",
			status->XO_ON, status->ERROR_LOCK, status->RX_FIFO_EMPTY, status->TX_FIFO_FULL);
	DEBUG_PRINT("  ANT_SELECT=%u, RCCAL_OK=%u, RES=%u\r\n", status->ANT_SELECT, status->RCCAL_OK, status->RESERVED);
}


/**
* @brief  Returns the charge pump word for a given VCO frequency.
* @param  cp_isel pointer to the charge pump register value.
* @param  pfd_split pointer to the pfd register value.
* @param  lFc channel center frequency expressed in Hz (from 779 MHz to 915 MHz)
* @retval uint8_t Charge pump word.
*/
void S2LP_PLLConf(int32_t lFc)
{
  uint32_t vcofreq, lFRef;
  uint8_t BFactor = 4; // 779-915 MHz range
  uint8_t refdiv = 1; // REFDIV=0 (XO_RCO_CONF0) by default
  uint8_t cp_isel, pfd_split;

  /* Calculates the syntheziser band select */
  uint64_t tgt1,tgt2,tgt;
  uint32_t synth;

  tgt = (((uint64_t)lFc)<<19)*(BFactor*refdiv);
  synth=(uint32_t)(tgt/XTAL_FREQ);
  tgt1 = (uint64_t)XTAL_FREQ*(synth);
  tgt2 = (uint64_t)XTAL_FREQ*(synth+1);

  synth=((tgt2-tgt)<(tgt-tgt1))?(synth+1):(synth);

  /* Calculates the VCO frequency VCOFreq = lFc*B */
  vcofreq = lFc*BFactor;

  /* Calculates the reference frequency clock */
  lFRef = XTAL_FREQ/refdiv;

  /* Set the correct charge pump word */
  if (vcofreq >= VCO_CENTER_FREQ) {
    if (lFRef > S2LP_DIG_DOMAIN_XTAL_THRESH) {
      cp_isel = 0x02;
      pfd_split = 0;
    }
    else {
      cp_isel = 0x01;
      pfd_split = 1;
    }
  }
  else {
    if (lFRef > S2LP_DIG_DOMAIN_XTAL_THRESH) {
      cp_isel = 0x03;
      pfd_split = 0;
    }
    else {
      cp_isel = 0x02;
      pfd_split = 1;
    }
  }

  //DEBUG_PRINT("SYNT: %lu, cp_ise=%u, pfd_split=%u\r\n", synth, cp_isel, pfd_split);

  uint8_t SYNT3 = (uint8_t) ((cp_isel << 5) | (synth >> 24));
  uint8_t SYNT2 = (uint8_t) ((synth >> 16) & 0xFF);
  uint8_t SYNT1 = (uint8_t) ((synth >> 8) & 0xFF);
  uint8_t SYNT0 = (uint8_t) ((synth >> 0) & 0xFF);

  uint8_t SYNTH_CONFIG2 = 0xD0 + (pfd_split << 2);

  S2LP_WriteReg(SYNT3_ADDR, SYNT3, NULL);
  S2LP_WriteReg(SYNT2_ADDR, SYNT2, NULL);
  S2LP_WriteReg(SYNT1_ADDR, SYNT1, NULL);
  S2LP_WriteReg(SYNT0_ADDR, SYNT0, NULL);
  S2LP_WriteReg(SYNTH_CONFIG2_ADDR, SYNTH_CONFIG2, NULL);
}

uint32_t ComputeDatarate(uint16_t cM, uint8_t cE)
{
  uint32_t f_dig=XTAL_FREQ;
  uint64_t dr;

  if(f_dig>S2LP_DIG_DOMAIN_XTAL_THRESH) {
    f_dig >>= 1;
  }

  if(cE==0) {
    dr=((uint64_t)f_dig*cM);
    return (uint32_t)(dr>>32);
  }

  dr=((uint64_t)f_dig)*((uint64_t)cM+65536);

  return (uint32_t)(dr>>(33-cE));
}

void SearchDatarateME(uint32_t lDatarate, uint16_t* pcM, uint8_t* pcE)
{
  uint32_t lDatarateTmp, f_dig=XTAL_FREQ;
  uint8_t uDrE;
  uint64_t tgt1,tgt2,tgt;

  if(f_dig>S2LP_DIG_DOMAIN_XTAL_THRESH) {
    f_dig >>= 1;
  }

  /* Search the exponent value */
  for(uDrE = 0; uDrE != 12; uDrE++) {
    lDatarateTmp = ComputeDatarate(0xFFFF, uDrE);
    if(lDatarate<=lDatarateTmp)
      break;
  }
  (*pcE) = (uint8_t)uDrE;

  if(uDrE==0) {
    tgt=((uint64_t)lDatarate)<<32;
    (*pcM) = (uint16_t)(tgt/f_dig);
    tgt1=(uint64_t)f_dig*(*pcM);
    tgt2=(uint64_t)f_dig*((*pcM)+1);
  }
  else {
    tgt=((uint64_t)lDatarate)<<(33-uDrE);
    (*pcM) = (uint16_t)((tgt/f_dig)-65536);
    tgt1=(uint64_t)f_dig*((*pcM)+65536);
    tgt2=(uint64_t)f_dig*((*pcM)+1+65536);
  }


  (*pcM)=((tgt2-tgt)<(tgt-tgt1))?((*pcM)+1):(*pcM);

}

uint32_t ComputeFreqDeviation(uint8_t cM, uint8_t cE, uint8_t bs, uint8_t refdiv)
{
  uint32_t f_xo=XTAL_FREQ;

  if(cE==0) {
    return (uint32_t)(((uint64_t)f_xo*cM)>>22);
  }

  return (uint32_t)(((uint64_t)f_xo*(256+cM))>>(23-cE));
}

void SearchFreqDevME(uint32_t lFDev, uint8_t* pcM, uint8_t* pcE)
{
  uint8_t uFDevE, bs = 4, refdiv = 1;
  uint32_t lFDevTmp;
  uint64_t tgt1,tgt2,tgt;

  /* Search the exponent of the frequency deviation value */
  for(uFDevE = 0; uFDevE != 12; uFDevE++) {
    lFDevTmp = ComputeFreqDeviation(255, uFDevE, bs, refdiv);
    if(lFDev<lFDevTmp)
      break;
  }
  (*pcE) = (uint8_t)uFDevE;

  if(uFDevE==0)
  {
    tgt=((uint64_t)lFDev)<<22;
    (*pcM)=(uint32_t)(tgt/XTAL_FREQ);
    tgt1=(uint64_t)XTAL_FREQ*(*pcM);
    tgt2=(uint64_t)XTAL_FREQ*((*pcM)+1);
  }
  else
  {
    tgt=((uint64_t)lFDev)<<(23-uFDevE);
    (*pcM)=(uint32_t)(tgt/XTAL_FREQ)-256;
    tgt1=(uint64_t)XTAL_FREQ*((*pcM)+256);
    tgt2=(uint64_t)XTAL_FREQ*((*pcM)+1+256);
  }

  (*pcM)=((tgt2-tgt)<(tgt-tgt1))?((*pcM)+1):(*pcM);
}

/**
* @brief  Set the modulation type, datarate and frequency deviation.
* @param  Datarate expressed in bps. This value shall be in the range
*         [100 500000].
*         Frequency deviation expressed in Hz.
* @retval None.
*/
void S2LP_SetModulation(uint8_t mod_type, uint32_t datarate, uint32_t fdev)
{
  uint8_t dr_e;
  uint16_t dr_m;
  uint8_t uFDevM, uFDevE;

  /* Calculates the datarate mantissa and exponent */
  SearchDatarateME(datarate, &dr_m, &dr_e);
  /* Calculates the frequency deviation mantissa and exponent */
  SearchFreqDevME(fdev, &uFDevM, &uFDevE);

  S2LP_WriteReg(MOD4_ADDR, (uint8_t)(dr_m >> 8), NULL);
  S2LP_WriteReg(MOD3_ADDR, (uint8_t)dr_m, NULL);
  S2LP_WriteReg(MOD2_ADDR, mod_type | dr_e, NULL);

  S2LP_WriteReg(MOD0_ADDR, uFDevM, NULL);
  S2LP_WriteReg(MOD1_ADDR, uFDevE, NULL);
}

void S2LP_SetPALeveldBm(int32_t lPowerdBm)
{
  uint8_t paLevelValue;
  if(lPowerdBm> 14)
  {
    paLevelValue = 1;
  }
  else {
    paLevelValue = (uint8_t)((int32_t)29-2*lPowerdBm);
  }

  S2LP_WriteReg(PA_POWER0_ADDR, 0, NULL);
  S2LP_WriteReg(PA_CONFIG1_ADDR+1, 0, NULL); // disable degeneration mode
  S2LP_WriteReg(PA_CONFIG1_ADDR, 0, NULL); // disable Tx Bessel FIR
  S2LP_WriteReg(PA_POWER1_ADDR, paLevelValue, NULL);
}

HAL_StatusTypeDef S2LP_Sleep(void)
{
	S2LPStatus radio_status;
	HAL_StatusTypeDef err = S2LP_ReadReg(0, NULL, &radio_status); // fetch radio state

	while (radio_status.MC_STATE != MC_STATE_SLEEP && radio_status.MC_STATE != MC_STATE_SLEEP_NOFIFO) {
		err = S2LP_Command(CMD_SLEEP, &radio_status);
		if (err) {
			DEBUG_PRINT("[S2LP] Error: cannot enter sleep mode\r\n");
			return HAL_ERROR;
		}
	}

	return HAL_OK;
}

HAL_StatusTypeDef S2LP_WakeUp(void)
{
	S2LPStatus radio_status;
	HAL_StatusTypeDef err = S2LP_ReadReg(0, NULL, &radio_status); // fetch radio state

	while (radio_status.MC_STATE != MC_STATE_READY) {
		err = S2LP_Command(CMD_READY, &radio_status);
		if (err) {
			DEBUG_PRINT("[S2LP] Error: cannot enter ready mode\r\n");
			return HAL_ERROR;
		}
	}

	return HAL_OK;
}

HAL_StatusTypeDef S2LP_Init(SPI_HandleTypeDef *spi_handle)
{
	gSPI = spi_handle;
	uint32_t ncycles_start = HAL_RCC_GetHCLKFreq()/9600;

	__disable_irq();
	HAL_GPIO_WritePin(RADIO_SDN_GPIO_Port, RADIO_SDN_Pin, GPIO_PIN_RESET); // Power up S2LP
	for(uint32_t i=0; i < ncycles_start; i++) // Wait for S2LP to start
		asm volatile("nop");
	__enable_irq();

	S2LP_WriteReg(GPIO0_CONF_ADDR, 3, NULL); // Set GPIO as interrupt line
	S2LP_WriteReg(IRQ_MASK0_ADDR, 0x80 | 0x20 | 0x04, NULL); // Enable "Tx Data sent" and "TX FIFO almost full" interrupts
	S2LP_WriteReg(IRQ_MASK1_ADDR, 0x01, NULL); // Enable "TX FIFO almost empty" interrupt
	S2LP_WriteReg(IRQ_MASK2_ADDR, 0x00, NULL);
	S2LP_WriteReg(IRQ_MASK3_ADDR, 0x00, NULL);
	S2LP_WriteReg(FIFO_CONFIG0_ADDR, FIFO_EMPTY_THRESH * FIFO_CHUNK_SIZE, NULL);

	// Change sync word bytes
	S2LP_WriteReg(SYNC3_ADDR, 0xB7, NULL);
	S2LP_WriteReg(SYNC2_ADDR, 0x54, NULL);
	S2LP_WriteReg(SYNC1_ADDR, 0x2A, NULL);
	S2LP_WriteReg(SYNC0_ADDR, 0x3E, NULL);

	// PLL and PA configuration
	S2LP_PLLConf(BASE_FREQ);
	S2LP_SetPALeveldBm(PA_LEVEL);

	// Modulation and packet configuration
	S2LP_SetModulation(MOD_2FSK, DATARATE, FREQDEV);
	S2LP_WriteReg(PCKTCTRL1_ADDR, 0x20, NULL); // No whitening, CRC with poly 0x07
	S2LP_WriteReg(PCKTCTRL3_ADDR, 0x00, NULL); // Enable basic packet structure

	S2LPStatus radio_status;
	uint8_t rco_conf;
	HAL_StatusTypeDef err = S2LP_ReadReg(XO_RCO_CONF1_ADDR, &rco_conf, &radio_status); // fetch radio state
	if (err) {
		return err;
	} else if (rco_conf != 0x45) {
		DEBUG_PRINT("[S2LP] Error: XO_RCO_CONF1 register is invalid (0x%X instead of 0x45), faulty SPI bus?\r\n", rco_conf);
		return HAL_ERROR;
	}

	if (radio_status.MC_STATE != MC_STATE_READY) {
		DEBUG_PRINT("[S2LP] Error: radio is not ready after initialization\r\n");
		return HAL_ERROR;
	}

	return HAL_OK;
}

void S2LP_IRQ_Handler(void)
{
	uint8_t irq_status1, irq_status0;
	S2LP_ReadReg(IRQ_STATUS1_ADDR, &irq_status1, NULL);
	S2LP_ReadReg(IRQ_STATUS0_ADDR, &irq_status0, NULL);

	if (irq_status1 & 0x01) // TX FIFO almost empty
		fifo_almost_empty = 1;

	if (irq_status0 & 0x20) // TX/RX FIFO underflow or overflow
		underflow = 1;

	if (irq_status0 & 0x04) // Packet transmitted
		packet_sent = 1;
}
