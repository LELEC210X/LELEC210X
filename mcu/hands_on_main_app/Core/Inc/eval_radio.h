/*
 * eval_radio.h
 */

#ifndef INC_EVAL_RADIO_H_
#define INC_EVAL_RADIO_H_

// Radio evaluation parameters
#define MIN_PA_LEVEL -16 // initial Tx transmit power, in dBm
#define MAX_PA_LEVEL  0  // final Tx transmit power, in dBm
#define STEP_PA_LEVEL 0  // step for TX transmit increase, in dBm. 0 means MIN_PA_LEVEL is always kept
#define N_PACKETS 100 // number of packets transmitted for each Tx power level
#define PAYLOAD_LEN 100 // payload length of the transmitted packets
#define PACKET_DELAY 1000 // delay between two packets, in milliseconds

// Behavior
#define BLINK_LED    0 // enable the toggling of the led between each packet transmission

void eval_radio(void);

#endif /* INC_EVAL_RADIO_H_ */
