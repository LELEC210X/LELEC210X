"""
uart-reader.py
ELEC PROJECT - 210x
"""

import argparse

import numpy as np
import serial
import soundfile as sf
from serial.tools import list_ports
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

PRINT_PREFIX = "SND:HEX:"
FREQ_SAMPLING = 10200
VAL_MAX_ADC = 4096
VDD = 3.3


def parse_buffer(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX) :])
    else:
        print(line)
        return None


def reader(port=None):
    ser = serial.Serial(port=port, baudrate=115200)
    while True:
        line = ""
        while not line.endswith("\n"):
            line += ser.read_until(b"\n", size=1042).decode("ascii")
        line = line.strip()
        buffer = parse_buffer(line)
        if buffer is not None:
            dt = np.dtype(np.uint16)
            dt = dt.newbyteorder("<")
            buffer_array = np.frombuffer(buffer, dtype=dt)

            yield buffer_array


def generate_audio(buf, file_name):
    buf = np.asarray(buf, dtype=np.float64)
    buf = buf - np.mean(buf)
    buf /= max(abs(buf))
    sf.write("audio_files/" + file_name + ".wav", buf, FREQ_SAMPLING)


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--port", help="Port for serial communication")
    args = argParser.parse_args()
    print("uart-reader launched...\n")

    if args.port is None:
        print(
            "No port specified, here is a list of serial communication port available"
        )
        print("================")
        port = list(list_ports.comports())
        for p in port:
            print(p.device)
        print("================")
        print("Launch this script with [-p PORT_REF] to access the communication port")

    else:
        input_stream = reader(port=args.port)
        msg_counter = 0

        fig = make_subplots(rows=1, cols=1)
        fig.update_layout(title="Real-time Acquisition", xaxis_title="Time (s)", yaxis_title="Voltage (mV)")

        for msg in input_stream:
            print(f"Acquisition #{msg_counter}")

            buffer_size = len(msg)
            times = np.linspace(0, buffer_size - 1, buffer_size) * 1 / FREQ_SAMPLING
            voltage_mV = msg * VDD / VAL_MAX_ADC * 1e3

            fig.data = []  # Clear previous data
            fig.add_trace(go.Scatter(x=times, y=voltage_mV, mode='lines', name=f"Acquisition #{msg_counter}"))

            pio.show(fig, renderer="browser")

            generate_audio(msg, f"acq-{msg_counter}")

            msg_counter += 1