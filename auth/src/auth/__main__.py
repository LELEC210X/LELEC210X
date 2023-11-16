from typing import Optional

import click
import serial
import zmq

from . import packet

PRINT_PREFIX = "DF:HEX:"


def parse_packet(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX) :])
    else:
        return None


def hex_to_bytes(ctx: click.Context, param: click.Parameter, value: str) -> bytes:
    return bytes.fromhex(value)


@click.group()
@click.option(
    "-i",
    "--input",
    "_input",
    default=None,
    type=click.File("r"),
    help="Where to read the input stream. If not specified, read from TCP address. You can pass '-' to read from stdin.",
)
@click.option(
    "-o",
    "--output",
    default="-",
    type=click.File("w"),
    help="Where to read the input stream. Default to '-', a.k.a. stdout.",
)
@click.option(
    "--tcp-address",
    default="tcp://127.0.0.1:10000",
    envvar="TCP_ADDRESS",
    show_default=True,
    show_envvar=True,
    help="TCP address to be used to read the input stream.",
)
@click.option(
    "-k",
    "--auth-key",
    default=32 * "0",
    envvar="AUTH_KEY",
    callback=hex_to_bytes,
    show_default=True,
    show_envvar=True,
    help="Authentification key (hex string).",
)
@click.option(
    "-l",
    "--melvec-len",
    default=32,
    envvar="MELVEC_LEN",
    type=click.IntRange(min=0),
    show_default=True,
    show_envvar=True,
    help="Length of one Mel vector.",
)
@click.option(
    "-n",
    "--nul-melvecs",
    default=32,
    envvar="NUM_MELVECS",
    type=click.IntRange(min=0),
    show_default=True,
    show_envvar=True,
    help="Number of Mel vectors per packet.",
)
@click.option("-q", "--quiet", is_flag=True, help="Whether output should be quiet.")
def main(
    _input: Optional[click.File],
    output: Optional[click.File],
    tcp_address: str,
    auth_key: bytes,
    melvec_len: int,
    num_melvecs: int,
    quiet: bool,
) -> None:
    """
    Parse packets from the MCU and perform authentication.
    """
    print("key:", auth_key.hex())
    unwrapper = packet.PacketUnwrapper(
        key=auth_key,
        allowed_senders=[
            0,
        ],
        authenticate=True,
    )

    if args.output:
        f_out = open(args.output, "w")

    if args.input == None:
        # Read messages from zmq GNU Radio interface
        def reader():
            context = zmq.Context()
            socket = context.socket(zmq.SUB)

            socket.setsockopt(zmq.SUBSCRIBE, b"")
            socket.setsockopt(zmq.CONFLATE, 1)  # last msg only.

            socket.connect("tcp://127.0.0.1:10000")
            while True:
                msg = socket.recv(2 * melvec_len * num_melvecs)
                if args.output:
                    f_out.write(PRINT_PREFIX + msg.hex() + "\n")
                yield msg

    elif args.input.startswith("/dev/tty"):
        # Read messages from serial interface
        def reader():
            ser = serial.Serial(port=_input, baudrate=115200)
            ser.reset_input_buffer()
            ser.read_until(b"\n")
            while True:
                line = ser.read_until(b"\n").decode("ascii").strip()
                if args.output:
                    f_out.write(line + "\n")
                if not args.quiet:
                    print("#", line)
                try:
                    packet = parse_packet(line)
                except ValueError:
                    print("Warning: invalid packet line:", line)
                else:
                    if packet is not None:
                        yield packet

    else:
        # Read messages from file
        def reader():
            f = open(args.input)
            for line in f.readlines():
                line = line.strip()
                if args.output:
                    f_out.write(line + "\n")
                if not args.quiet:
                    print("#", line)
                packet = parse_packet(line)
                if packet is not None:
                    yield packet
                    if args.display:
                        input("Press ENTER to process next packet")

    input_stream = reader()
    for msg in input_stream:
        try:
            sender, payload = unwrapper.unwrap_packet(msg)
        except packet.InvalidPacket as e:
            print("Invalid packet received:", e.args[0])
            print("\t", PRINT_PREFIX + msg.hex())
            continue

        print(f"From {sender}, received packet {payload.hex()}")
