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
        return bytes.fromhex(line[len(PRINT_PREFIX):])
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


def plot_fft(signal, sampling_rate):
    """Calculer et retourner les fréquences et la magnitude de la FFT (sans la composante DC)"""
    n = len(signal)
    fft_values = np.fft.fft(signal)
    fft_values = np.abs(fft_values)[:n // 2]  # Magnitude de la FFT
    freqs = np.fft.fftfreq(n, 1 / sampling_rate)[:n // 2]  # Fréquences associées

    # Exclure la composante DC (fréquence 0)
    freqs = freqs[1:]
    fft_values = fft_values[1:]

    return freqs, fft_values


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

        # Création d'un sous-plot avec 2 graphiques (temporel + FFT)
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Signal temporel", "FFT du signal"))

        fig.update_layout(title="Acquisition en Temps Réel", xaxis_title="Temps (s)", yaxis_title="Voltage (mV)")
        fig.update_yaxes(title_text="Voltage (mV)", row=1, col=1)
        fig.update_yaxes(title_text="Magnitude FFT", row=2, col=1)
        fig.update_xaxes(title_text="Temps (s)", row=1, col=1)
        fig.update_xaxes(title_text="Fréquence (Hz)", row=2, col=1)

        for msg in input_stream:
            print(f"Acquisition #{msg_counter}")

            # Acquisition en domaine temporel
            buffer_size = len(msg)
            times = np.linspace(0, buffer_size - 1, buffer_size) * 1 / FREQ_SAMPLING
            voltage_mV = msg * VDD / VAL_MAX_ADC * 1e3

            # Calcul de la FFT
            freqs, fft_magnitude = plot_fft(voltage_mV, FREQ_SAMPLING)

            # Mise à jour des sous-plots
            fig.data = []  # Effacer les données précédentes
            # Tracé temporel
            fig.add_trace(go.Scatter(x=times, y=voltage_mV, mode='lines', name=f"Acquisition #{msg_counter}"), row=1, col=1)
            # Tracé FFT sans composante DC
            fig.add_trace(go.Scatter(x=freqs, y=fft_magnitude, mode='lines', name=f"FFT #{msg_counter}"), row=2, col=1)

            # Affichage des graphiques
            pio.show(fig, renderer="browser")

            # Générer le fichier audio
            generate_audio(msg, f"acq-{msg_counter}")

            msg_counter += 1