/*
 * eval_radio.h
 */

#ifndef INC_EVAL_RADIO_H_
#define INC_EVAL_RADIO_H_

// Radio evaluation parameters
#define MIN_PA_LEVEL -16 // initial Tx transmit power, in dBm
#define MAX_PA_LEVEL -16 // final Tx transmit power, in dBm
#define N_PACKETS 5 // number of packets transmitted for each Tx power level
#define PAYLOAD_LEN 100 // payload length of the transmitted packets
#define PACKET_DELAY 1 // delay between two packets, in seconds

void eval_radio(void);

#endif /* INC_EVAL_RADIO_H_ */
