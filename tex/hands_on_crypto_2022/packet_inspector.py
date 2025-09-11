import argparse
import struct

import serial
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.constant_time import bytes_eq

PRINT_PREFIX = "DF:HEX:"


def parse_packet(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        try:
            return bytes.fromhex(line[len(PRINT_PREFIX) :])
        except ValueError as e:
            raise ValueError("Bad packet format: " + repr(line)) from e

    else:
        return None


def serial_reader(args):
    ser = serial.Serial(port=args.input, baudrate=args.baudrate)
    ser.reset_input_buffer()
    while True:
        # This loop is a workaround for limitation in Serial.read_until.
        line = b""
        while not line.endswith(b"\n"):
            line += ser.read_until(b"\n", 256)
        line = line.decode("ascii").strip()
        try:
            packet = parse_packet(line)
        except ValueError as e:
            print("Bad packet:", e)
        else:
            if packet is not None:
                yield packet


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
# - 2-byte (BE) payload length
# - 4-byte message id (BE) monotonically increasing.
# Packet format:
# - Packet header
# - Payload
# - 16-byte tag
PACKET_HEADER = struct.Struct("!BBHI")
HEADER_LEN = PACKET_HEADER.size
TAG_LEN = 16
MIN_LEN = HEADER_LEN + TAG_LEN


def main():
    parser = argparse.ArgumentParser(description="Parse incoming packets.")
    parser.add_argument(
        "--input",
        action="store",
        type=str,
        help="Input stream to read from (serial device).",
        required=True,
    )
    parser.add_argument(
        "--baudrate",
        action="store",
        type=int,
        default=115200,
        help="Serial device baudrate.",
    )
    parser.add_argument(
        "--key", action="store", type=str, help="MAC key, encoded in hex."
    )
    args = parser.parse_args()

    if args.key is not None:
        key = bytes.fromhex(args.key)
        if len(key) != 16:
            raise ValueError("key parameter has wrong length")

    input_stream = serial_reader(args)

    for packet in input_stream:
        print("Received packet:", packet.hex())
        if len(packet) < 1 or packet[0] != 0:
            print("  Packet empty or wrong version.")
            continue
        if len(packet) < MIN_LEN:
            print("  Packet too short.")
            continue
        version, sender, payload_length, serial_nb = PACKET_HEADER.unpack(
            packet[:HEADER_LEN]
        )
        print("  Version:", version)
        print("  Sender:", sender)
        print("  payload length:", payload_length)
        print("  serial number:", serial_nb)
        if len(packet) != MIN_LEN + payload_length:
            print("  Wrong payload length.")
            continue
        print("  Authentication tag:", packet[-TAG_LEN:])
        if args.key is not None:
            if bytes_eq(tag_cbc_mac(packet[:-TAG_LEN], key), packet[-TAG_LEN:]):
                print("  Authentication SUCCESSFUL")
            else:
                print("  Authentication FAILED")
        else:
            print("  Authentication NOT AVAILABLE")


if __name__ == "__main__":
    main()
