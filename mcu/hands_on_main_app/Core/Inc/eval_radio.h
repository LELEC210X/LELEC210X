/*
 * eval_radio.h
 */

#ifndef INC_EVAL_RADIO_H_
#define INC_EVAL_RADIO_H_

// Radio evaluation parameters
#define MIN_PA_LEVEL -15 // initial Tx transmit power, in dBm
#define MAX_PA_LEVEL 20 // final Tx transmit power, in dBm
#define N_PACKETS 200 // number of packets transmitted for each Tx power level
#define PAYLOAD_LEN 50 // payload length of the transmitted packets
#define PACKET_DELAY 6 // :uint16: delay between two packets, equal to PACKET_DELAY * 100 milliseconds

void eval_radio(void);

#endif /* INC_EVAL_RADIO_H_ */
