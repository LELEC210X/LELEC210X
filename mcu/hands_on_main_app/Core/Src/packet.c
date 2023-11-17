/*
 * packet.c
 */

<<<<<<< refs/remotes/upstream/main
=======
#include <string.h>

>>>>>>> Revert "enlever le chain de argu"
#include "aes_ref.h"
#include "config.h"
#include "packet.h"
#include "main.h"
#include "utils.h"

<<<<<<< refs/remotes/upstream/main
const uint8_t AES_Key[16]  = {
                            0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00};

void tag_cbc_mac(uint8_t *tag, const uint8_t *msg, size_t msg_len) {
	// Allocate a buffer of the key size to store the input and result of AES
	// uint32_t[4] is 4*(32/8)= 16 bytes long
	uint32_t statew[4] = {0};
	// state is a pointer to the start of the buffer
	uint8_t *state = (uint8_t*) statew;
    size_t i;


    // TO DO : Complete the CBC-MAC_AES

	for (i = 0; i < msg_len-16; i +=16){
		for(size_t j = 0; j < 16; j++){
			*(state+j) = msg[i+j] ^ *(state+j);
		}
		AES128_encrypt(state, AES_Key);
	}
	for(size_t k = i; k < msg_len; k++){
		*(state+k-i) = msg[k] ^ *(state+k-i);
	}
	AES128_encrypt(state, AES_Key);
	


    // Copy the result of CBC-MAC-AES to the tag.
    for (int j=0; j<16; j++) {
        tag[j] = state[j];
    }
}

// Assumes payload is already in place in the packet
int make_packet(uint8_t *packet, size_t payload_len, uint8_t sender_id, uint32_t serial) {
    size_t packet_len = payload_len + PACKET_HEADER_LENGTH + PACKET_TAG_LENGTH;
	// reserved bite : one byte of 0 

    packet[0] = 0x00;

	packet[1] = sender_id;

	packet[2] = (payload_len >> 8) & 0xFF;

	packet[3] = (payload_len & 0xFF);

	packet[4] = (serial >> 24) & 0xFF; 

	packet[5] = (serial >> 16) & 0xFF; 

	packet[6] = (serial >> 8) & 0xFF; 

	packet[7] = serial & 0xFF;
    // So is the tag
	memset(packet + payload_len + PACKET_HEADER_LENGTH, 0, PACKET_TAG_LENGTH);

	// TO DO :  replace the two previous command by properly
	//			setting the packet header with the following structure :
	/***************************************************************************
	 *    Field       	Length (bytes)      Encoding        Description
	 ***************************************************************************
	 *  r 					1 								Reserved, set to 0.
	 * 	emitter_id 			1 					BE 			Unique id of the sensor node.
	 *	payload_length 		2 					BE 			Length of app_data (in bytes).
	 *	packet_serial 		4 					BE 			Unique and incrementing id of the packet.
	 *	app_data 			any 							The feature vectors.
	 *	tag 				16 								Message authentication code (MAC).
	 *
	 *	Note : BE refers to Big endian
	 *		 	Use the structure 	packet[x] = y; 	to set a byte of the packet buffer
	 *		 	To perform bit masking of the specific bytes you want to set, you can use
	 *		 		- bitshift operator (>>),
	 *		 		- and operator (&) with hex value, e.g.to perform 0xFF
	 *		 	This will be helpful when setting fields that are on multiple bytes.
	*/

	// For the tag field, you have to calculate the tag. The function call below is correct but
	// tag_cbc_mac function, calculating the tag, is not implemented.
    tag_cbc_mac(packet + payload_len + PACKET_HEADER_LENGTH, packet, payload_len + PACKET_HEADER_LENGTH);

=======
// Assumes payload is already in place in the packet
int make_packet(uint8_t *packet, size_t payload_len, uint8_t sender_id, uint32_t serial) {
    memset(packet, 0, PACKET_HEADER_LENGTH);
    memset(packet + payload_len + PACKET_HEADER_LENGTH, 0, PACKET_TAG_LENGTH);

    size_t packet_len = payload_len + PACKET_HEADER_LENGTH + PACKET_TAG_LENGTH;
>>>>>>> Revert "enlever le chain de argu"
    return packet_len;
}
