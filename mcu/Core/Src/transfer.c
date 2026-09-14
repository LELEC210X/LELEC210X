/*
 * transfer.c
 */


#include "transfer.h"
#include "aes_ref.h"
#include "config.h"
#include "main.h"
#include "utils.h"
#include "s2lp.h"

// Exported variables
uint8_t packet[PACKET_LENGTH];

// Local variables
static uint32_t packet_serial = 0;
static const uint8_t AES_Key[16] = {0x00,0x00,0x00,0x00,
									0x00,0x00,0x00,0x00,
									0x00,0x00,0x00,0x00,
									0x00,0x00,0x00,0x00};

// External variables
extern q15_t mel_vectors[N_MELVECS][MELVEC_LENGTH];

/*
 * @brief Make the packet in memory by filling in the header, payload and tag.
 *
 * TODO :  Fill in the header and the tag by properly
 *         setting the fields with the following structure:
 *
 ***************************************************************************
 *    Field       	Length (bytes)      Encoding        Description
 ***************************************************************************
 *  r 					1 								Reserved, set to 0.
 * 	emitter_id 			1 					BE 			Unique id of the sensor node.
 *	payload_length 		2 					BE 			Length of payload (in bytes).
 *	packet_serial 		4 					BE 			Unique and incrementing packet serial id.
 *	payload 			any 							The spectrogram.
 *	tag 				16 								Message authentication code (MAC).
 *
 *	Note : BE refers to Big endian
 *		 	Use the structure 	packet[x] = y; 	to set a byte of the packet buffer
 *		 	To perform bit masking of the specific bytes you want to set, you can use
 *		 		- bitshift operator (>>),
 *		 		- and operator (&) with hex value, e.g. 0xFF
 *		 	This will be helpful when setting fields that are on multiple bytes.
 */
void make_packet(void)
{
	//// 1- Header ////
	// Initially, the whole packet header is set to 0s
	memset(packet, 0, HEADER_LENGTH);
	// TODO replace the memset by filling in each header field with the right value

	//// 2- Payload ////
	// BE encoding of each mel coef
	for (size_t i=0; i<N_MELVECS; i++) {
		for (size_t j=0; j<MELVEC_LENGTH; j++) {
			(packet+HEADER_LENGTH)[(i*MELVEC_LENGTH+j)*2]   = mel_vectors[i][j] >> 8;
			(packet+HEADER_LENGTH)[(i*MELVEC_LENGTH+j)*2+1] = mel_vectors[i][j] & 0xFF;
		}
	}

	//// 3- Tag ////
	// Generate a tag from the header+payload input message
	uint8_t *msg_in = packet;
	size_t msg_len = HEADER_LENGTH + PAYLOAD_LENGTH;
	uint8_t *tag = packet + msg_len;
	// Allocate a buffer of the key size to store the input and output of the AES function
	// uint32_t[4] is (32/8)*4 = 16 bytes long
	uint32_t statew[4] = {0};
	// state is a pointer to the start of the buffer
	uint8_t *state = (uint8_t*) statew;
    size_t i;

    // TODO : Complete the CBC-MAC_AES algorithm
    // using the AES implementation provided in Drivers/AES/aes_ref.h
    UNUSED(msg_in);
    UNUSED(msg_len);
    UNUSED(i);
    UNUSED(AES_Key);

    // Copy the result of CBC-MAC-AES to the tag.
    for (int j=0; j<16; j++) {
        tag[j] = state[j];
    }

    //// 4- Packet id increment ////
	packet_serial += 1;
	if (packet_serial == 0) {
		// Should not happen as packet_cnt is 32-bit and we send at most 1 packet per second.
		DEBUG_PRINT("Packet counter overflow.\r\n");
		Error_Handler();
	}
}

/*
 * @brief Send the packet via UART and/or S2LP radio
 */
void send_packet(void)
{
#if ENABLE_RADIO
	S2LP_Send(packet, PACKET_LENGTH);
#endif // ENABLE_RADIO

#if DEBUGP
	DEBUG_PRINT("PACKET:HEX:");
	for (size_t i=0; i<PACKET_LENGTH; i++) {
		DEBUG_PRINT("%02x", packet[i]);
	}
	DEBUG_PRINT("\r\n");
#endif // DEBUGP
}


