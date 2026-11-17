/*
 * eval_radio.h
 */

#ifndef INC_EVAL_RADIO_H_
#define INC_EVAL_RADIO_H_


#include "arm_math.h"
#include "config.h"

// Radio evaluation parameters
#define INIT_PA_LEVEL 0 // initial Tx transmit power, in dBm
#define INIT_N_PACKETS 100 // number of packets transmitted for each Tx power level

#define PAYLOAD_LEN 100 // payload length of the transmitted packets
#define PACKET_DELAY 1000 // delay between two packets, in milliseconds

// Behavior
#define BLINK_LED    1 // enable the toggling of the led between each packet transmission

// Exported variable
extern volatile uint8_t btn_press;

// Exported function prototype
void eval_radio_start(void);

#endif /* INC_EVAL_RADIO_H_ */
