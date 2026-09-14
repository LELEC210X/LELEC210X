/*
 * transfer.h
 */

#ifndef INC_TRANSFER_H_
#define INC_TRANSFER_H_

#include "arm_math.h"
#include "config.h"

#define HEADER_LENGTH (1+1+2+4)
#define PAYLOAD_LENGTH (sizeof(q15_t) * N_MELVECS * MELVEC_LENGTH)
#define TAG_LENGTH 16
#define PACKET_LENGTH (HEADER_LENGTH + PAYLOAD_LENGTH + TAG_LENGTH)

#define EMITTER_ID 0x00

// Exported variables
extern uint8_t packet[PACKET_LENGTH];

// Exported function prototypes
void make_packet(void);
void send_packet(void);


#endif /* INC_TRANSFER_H_ */
