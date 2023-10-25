/*
 * s2lp.h
 */

#ifndef INC_S2LP_H_
#define INC_S2LP_H_

// === Communication parameters
#define BASE_FREQ 868000000 // Carrier frequency, in Hz
#define DATARATE 50000 // Data rate in 2FSK, in bit/s
#define FREQDEV DATARATE/4 // Frequency deviation, in Hz
#define PA_LEVEL -16 // Default Tx output power, in dBm
// === END of communication parameters

#define XTAL_FREQ 50000000
#define VCO_CENTER_FREQ 3600000000
#define S2LP_DIG_DOMAIN_XTAL_THRESH 30000000
#define FIFO_SIZE 128
#define FIFO_CHUNK_SIZE 8 // This value *MUST* be a power of 2, up to FIFO_SIZE/4
#define FIFO_EMPTY_THRESH 4 // in number of FIFO chunks

typedef enum {
  MC_STATE_READY             =0x00,  /*!< READY */
  MC_STATE_SLEEP_NOFIFO      =0x01,  /*!< SLEEP NO FIFO RETENTION */
  MC_STATE_STANDBY           =0x02,  /*!< STANDBY */
  MC_STATE_SLEEP             =0x03,  /*!< SLEEP */
  MC_STATE_LOCKON            =0x0C,  /*!< LOCKON */
  MC_STATE_RX                =0x30,  /*!< RX */
  MC_STATE_LOCK_ST           =0x14,  /*!< LOCK_ST */
  MC_STATE_TX                =0x5C,  /*!< TX */
  MC_STATE_SYNTH_SETUP       =0x50   /*!< SYNTH_SETUP */
} S2LPState;

typedef struct {
  uint8_t ERROR_LOCK: 1;     /*!< RCO calibration error */
  uint8_t RX_FIFO_EMPTY: 1;  /*!< RX FIFO is empty */
  uint8_t TX_FIFO_FULL: 1;   /*!< TX FIFO is full */
  uint8_t ANT_SELECT: 1;     /*!< Currently selected antenna */
  uint8_t RCCAL_OK: 1;       /*!< RCO successfully terminated */
  uint8_t RESERVED: 3;               /*!< This 3 bits field are reserved and equal to 2 */
  uint8_t XO_ON:1;           /*!< XO is operating state */
  S2LPState MC_STATE: 7;     /*!< The state of the Main Controller of S2LP @ref S2LPState */
} S2LPStatus;

typedef enum
{
  CMD_TX =  ((uint8_t)(0x60)),                    /*!< Start to transmit; valid only from READY */
  CMD_RX =  ((uint8_t)(0x61)),                    /*!< Start to receive; valid only from READY */
  CMD_READY =  ((uint8_t)(0x62)),                 /*!< Go to READY; valid only from STANDBY or SLEEP or LOCK */
  CMD_STANDBY =  ((uint8_t)(0x63)),               /*!< Go to STANDBY; valid only from READY */
  CMD_SLEEP = ((uint8_t)(0x64)),                  /*!< Go to SLEEP; valid only from READY */
  CMD_LOCKRX = ((uint8_t)(0x65)),                 /*!< Go to LOCK state by using the RX configuration of the synth; valid only from READY */
  CMD_LOCKTX = ((uint8_t)(0x66)),                 /*!< Go to LOCK state by using the TX configuration of the synth; valid only from READY */
  CMD_SABORT = ((uint8_t)(0x67)),                 /*!< Force exit form TX or RX states and go to READY state; valid only from TX or RX */
  CMD_LDC_RELOAD = ((uint8_t)(0x68)),             /*!< LDC Mode: Reload the LDC timer with the value stored in the  LDC_PRESCALER / COUNTER  registers; valid from all states  */
  CMD_RCO_CALIB =  ((uint8_t)(0x69)),             /*!< Start (or re-start) the RCO calibration */
  CMD_SRES = ((uint8_t)(0x70)),                   /*!< Reset of all digital part, except SPI registers */
  CMD_FLUSHRXFIFO = ((uint8_t)(0x71)),            /*!< Clean the RX FIFO; valid from all states */
  CMD_FLUSHTXFIFO = ((uint8_t)(0x72)),            /*!< Clean the TX FIFO; valid from all states */
  CMD_SEQUENCE_UPDATE =  ((uint8_t)(0x73)),       /*!< Autoretransmission: Reload the Packet sequence counter with the value stored in the PROTOCOL[2] register valid from all states */
} _S2LP_CMD;

typedef enum {
  MOD_NO_MOD       = 0x70, /*!< CW modulation selected */
  MOD_2FSK         = 0x00, /*!< 2-FSK modulation selected */
  MOD_4FSK         = 0x10, /*!< 4-FSK modulation selected */
  MOD_2GFSK_BT05   = 0xA0, /*!< G2FSK modulation selected with BT = 0.5 */
  MOD_2GFSK_BT1    = 0x20, /*!< G2FSK modulation selected with BT = 1 */
  MOD_4GFSK_BT05   = 0xB0, /*!< G4FSK modulation selected with BT = 0.5 */
  MOD_4GFSK_BT1    = 0x30, /*!< G4FSK modulation selected with BT = 1 */
  MOD_ASK_OOK      = 0x50, /*!< OOK modulation selected. */
  MOD_POLAR        = 0x60, /*!< OOK modulation selected. */
} ModulationSelect;

HAL_StatusTypeDef S2LP_Command(uint8_t cmd, S2LPStatus *status);
HAL_StatusTypeDef S2LP_ReadReg(uint8_t addr, uint8_t *retval, S2LPStatus *status);
HAL_StatusTypeDef S2LP_WriteReg(uint8_t addr, uint8_t val, S2LPStatus *status);
void S2LP_PrintStatus(S2LPStatus *status);
void S2LP_PLLConf(int32_t lFc);
void S2LP_SetPALeveldBm(int32_t lPowerdBm);
HAL_StatusTypeDef S2LP_Init(SPI_HandleTypeDef *spi_handle);
void S2LP_IRQ_Handler(void);
HAL_StatusTypeDef S2LP_Send(uint8_t *payload, uint16_t pay_len);
HAL_StatusTypeDef S2LP_Sleep(void);
HAL_StatusTypeDef S2LP_WakeUp(void);

#endif /* INC_S2LP_H_ */
