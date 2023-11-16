import struct

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.constant_time import bytes_eq


def tag_cbc_mac(msg, key):
    mode = modes.CBC(16 * b"\0")  # all-0 IV for CBC-MAC
    cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
    encryptor = cipher.encryptor()
    # zero padding is ok in this case, as length is encoded in the message
    padded_msg = msg + (-len(msg) % 16) * b"\0"
    ct = encryptor.update(padded_msg) + encryptor.finalize()
    return ct[-16:]


# Packet header format:
# - 1-byte version (0)
# - 1-byte source address
# - 2-byte (network byte order) payload length
# - 4-byte message id (network byte order) monotonically increasing.
# Packet format:
# - Packet header
# - Payload
# - 16-byte tag
PACKET_HEADER = struct.Struct("!BBHI")
HEADER_LEN = PACKET_HEADER.size
TAG_LEN = 16
MIN_LEN = HEADER_LEN + TAG_LEN


class InvalidPacket(ValueError):
    pass


class PacketUnwrapper:
    """Verify packet wire format, validate security properties and extract the
    payload.

    :param allowed_sender_ids: list of id of allowed senders
    :param starting_serial: dict mapping optionally each allowed sender to the
    first packet serial number we might receive from that sender
    """

    def __init__(
        self, key, allowed_senders, starting_serials=dict(), authenticate: bool = True
    ):
        self.key = key
        self.authenticate = authenticate
        # anything lower than the minimum allowed serial number is considered
        # to have already been received.
        self.senders_last_serial = {
            sender: starting_serials.get(sender, 0) - 1 for sender in allowed_senders
        }

    def unwrap_packet(self, packet):
        """Returns (sender, payload), or None if packet is not valid."""
        # Version check, we only know version 0
        if len(packet) < 1 or packet[0] != 0:
            raise InvalidPacket("Packet empty or wrong version.")
        # Validate min length for header decoding
        if len(packet) < MIN_LEN:
            raise InvalidPacket("Packet too short.")
        _version, sender, payload_length, serial = PACKET_HEADER.unpack(
            packet[:HEADER_LEN]
        )
        # Validate correct packet length w.r.t. payload
        if len(packet) != MIN_LEN + payload_length:
            raise InvalidPacket("Wrong payload length.")
        if self.authenticate:
            # Validate tag in constant time
            if not bytes_eq(
                tag_cbc_mac(packet[:-TAG_LEN], self.key), packet[-TAG_LEN:]
            ):
                raise InvalidPacket("Invalid authentication tag.")
            # Validate sender
            if sender not in self.senders_last_serial:
                raise InvalidPacket("Not authorized sender.")
            # Validate serial
            if self.senders_last_serial[sender] >= serial:
                raise InvalidPacket(f"Serial number non-incrementing ({serial}).")
            self.senders_last_serial[sender] = serial
        return (sender, packet[HEADER_LEN:-TAG_LEN])
