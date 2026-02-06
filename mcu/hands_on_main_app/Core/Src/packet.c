/*
 * packet.c
 */

#include "aes_ref.h"
#include "config.h"
#include "packet.h"
#include "main.h"
#include "utils.h"

const uint8_t AES_Key[16]  = {
                            0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00,
							0x00,0x00,0x00,0x00};

void tag_cbc_mac(uint8_t *tag, const uint8_t *msg, size_t msg_len) {
    // Buffer de 16 octets (état AES)
    uint32_t statew[4] = {0};
    uint8_t *state = (uint8_t*) statew;
    size_t i, j;

    // CBC-MAC nécessite des blocs complets
    if (msg_len % 16 != 0) {
        return; // ou gérer une erreur
    }

    // Initialisation : IV = 0^128 (déjà fait par statew = {0})

    // Pour chaque bloc de 16 octets
    for (i = 0; i < msg_len; i += 16) {

        // XOR du bloc courant avec l'état précédent
        for (j = 0; j < 16; j++) {
            state[j] ^= msg[i + j];
        }

        // Chiffrement AES du bloc
        aes_encrypt(state);
    }

    // Le dernier état est le tag
    for (j = 0; j < 16; j++) {
        tag[j] = state[j];
    }
}


// Assumes payload is already in place in the packet
int make_packet(uint8_t *packet, size_t payload_len, uint8_t sender_id, uint32_t serial) {
	size_t packet_len = PACKET_HEADER_LENGTH + payload_len + PACKET_TAG_LENGTH;

	// Reserved = 0
	packet[0] = 0x00;

	// Emitter ID (use the correct argument!)
	packet[1] = sender_id;

	// Payload length (2 bytes big-endian)
	packet[2] = (payload_len >> 8) & 0xFF;
	packet[3] = (payload_len     ) & 0xFF;

	// Packet serial (4 bytes big-endian)
	packet[4] = (serial >> 24) & 0xFF;
	packet[5] = (serial >> 16) & 0xFF;
	packet[6] = (serial >> 8 ) & 0xFF;
	packet[7] = (serial      ) & 0xFF;

	// Tag is currently wrong on purpose (future exercise)
	tag_cbc_mac(packet + payload_len + PACKET_HEADER_LENGTH,
	            packet,
	            payload_len + PACKET_HEADER_LENGTH);

	return packet_len;
}

