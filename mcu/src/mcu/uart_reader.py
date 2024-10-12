"""
uart-reader.py
ELEC PROJECT - 210x
"""

import os
import signal
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

import click
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import serial
import soundfile as sf
from plotly.subplots import make_subplots
from serial.tools import list_ports

###################### MODIFY BELOW THIS LINE #####################
####################################################################

# Default values
PRINT_PREFIX = "SND:HEX:"
FREQ_SAMPLING = 10200
DEFAULT_BAUDRATE = 115200
VAL_MAX_ADC = 4096
VDD = 3.3
LOG_ENABLED = False
AUTO_DELETE_AUDIO = False
DEFAULT_PORT_INDEX = 1  # Change this if the default port is not the first one

###################### DO NOT MODIFY BELOW THIS LINE #####################
##########################################################################


def generate_audio(buf, file_name):
    buf = np.asarray(buf, dtype=np.float64)
    buf = buf - np.mean(buf)
    buf /= max(abs(buf))
    sf.write("audio_files/" + file_name + ".wav", buf, FREQ_SAMPLING)


msg_counter = 0


def plot_signal_and_fft(signal, sampling_rate):
    global msg_counter
    buffer_size = len(signal)
    times = np.linspace(0, buffer_size - 1, buffer_size) * 1 / sampling_rate
    voltage_mV = signal * VDD / VAL_MAX_ADC * 1e3

    # Calculate FFT
    n = len(voltage_mV)
    fft_values = np.fft.fft(voltage_mV)
    fft_values = np.abs(fft_values)[: n // 2]  # Magnitude of the FFT
    freqs = np.fft.fftfreq(n, 1 / sampling_rate)[: n // 2]  # Associated frequencies

    # Exclude the DC component (frequency 0)
    freqs = freqs[1:]
    fft_values = fft_values[1:]

    # Create subplot with 2 graphs (time-domain + FFT)
    fig = make_subplots(
        rows=2, cols=1, subplot_titles=("Time-Domain Signal", "Signal FFT")
    )

    fig.update_layout(
        title="Real-Time Acquisition",
        xaxis_title="Time (s)",
        yaxis_title="Voltage (mV)",
    )
    fig.update_yaxes(title_text="Voltage (mV)", row=1, col=1)
    fig.update_yaxes(title_text="FFT Magnitude", row=2, col=1)
    fig.update_xaxes(title_text="Time (s)", row=1, col=1)
    fig.update_xaxes(title_text="Frequency (Hz)", row=2, col=1)

    # Plot time-domain signal
    fig.add_trace(
        go.Scatter(
            x=times, y=voltage_mV, mode="lines", name=f"Acquisition #{msg_counter}"
        ),
        row=1,
        col=1,
    )
    # Plot FFT without DC component
    fig.add_trace(
        go.Scatter(x=freqs, y=fft_values, mode="lines", name=f"FFT #{msg_counter}"),
        row=2,
        col=1,
    )

    # Show plots
    pio.show(fig, renderer="browser")

    # Generate audio file
    generate_audio(signal, f"acq-{msg_counter}")

    msg_counter += 1


def print_and_save_data(data):
    if LOG_ENABLED:
        with open("uart_reader.log", "w") as f:
            f.write(data)
    print(data)


def read_serial(port, baudrate=DEFAULT_BAUDRATE):
    """Reads the serial data and processes it for the console mode."""
    try:
        with serial.Serial(port, baudrate) as ser:
            print_and_save_data(f"Connected to {port} with baudrate {baudrate}")
            while not stop_event.is_set():
                line = ser.readline().decode("ascii").strip()
                if line.startswith(PRINT_PREFIX):
                    buffer = bytes.fromhex(line[len(PRINT_PREFIX) :])
                    dt = np.dtype(np.uint16)
                    dt = dt.newbyteorder("<")
                    buffer_array = np.frombuffer(buffer, dtype=dt)
                    print_and_save_data(f"Aquisition Number : {msg_counter}")
                    print_and_save_data(
                        f">Aquisition Memory: {len(line) - len(PRINT_PREFIX)} bytes"
                    )
                    print_and_save_data(
                        f">Aquisition Size  : {len(buffer_array)} samples"
                    )
                    plot_signal_and_fft(buffer_array, FREQ_SAMPLING)
                else:
                    print_and_save_data(f"{line}")
    except Exception as e:
        print_and_save_data(f"Error: {e}")
        sys.exit(1)
    finally:
        print_and_save_data("Disconnected")


class UARTReaderApp:
    def __init__(self, root, port=None):
        self.root = root
        self.root.title("UART Reader")

        self.port_var = tk.StringVar(value="--no COM--")
        self.baudrate_var = tk.IntVar(value=DEFAULT_BAUDRATE)
        self.freq_sampling_var = tk.IntVar(value=FREQ_SAMPLING)
        self.val_max_adc_var = tk.IntVar(value=VAL_MAX_ADC)
        self.vdd_var = tk.DoubleVar(value=VDD)
        self.log_var = tk.BooleanVar(value=LOG_ENABLED)
        self.auto_delete_audio_var = tk.BooleanVar(value=AUTO_DELETE_AUDIO)

        self.create_widgets()
        self.serial_connection = None
        self.serial_thread = None
        self.stop_thread = threading.Event()
        self.current_port = None

        if port:
            self.port_var.set(port)
            self.connect()

        if LOG_ENABLED:
            with open("uart_reader.log", "w") as f:
                f.write("UART Reader Application Log\n")

        if not os.path.exists("audio_files"):
            os.makedirs("audio_files")
        if AUTO_DELETE_AUDIO:
            for file in os.listdir("audio_files"):
                os.remove(os.path.join("audio_files", file))

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        credits_frame = ttk.Frame(frame, padding="5")
        credits_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Label(
            credits_frame,
            text="UART Reader Application for LELEC210x",
            font=("Helvetica", 16),
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(
            credits_frame, text="Developed by Group E 2024", font=("Helvetica", 7)
        ).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(
            credits_frame,
            text="How to use: Select COM port and click Connect",
            font=("Helvetica", 10),
        ).grid(row=3, column=0, sticky=tk.W)

        ttk.Label(frame, text="Select COM Port:").grid(row=1, column=0, sticky=tk.W)
        self.port_combobox = ttk.Combobox(frame, textvariable=self.port_var)
        self.refresh_ports()
        self.port_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E))

        if len(self.port_combobox["values"]) > 1:
            self.port_combobox.current(DEFAULT_PORT_INDEX)

        self.refresh_button = ttk.Button(
            frame, text="Refresh", command=self.refresh_ports
        )
        self.refresh_button.grid(row=1, column=2, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Baudrate:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.baudrate_var).grid(
            row=2, column=1, sticky=(tk.W, tk.E)
        )

        ttk.Label(frame, text="Frequency Sampling:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.freq_sampling_var).grid(
            row=3, column=1, sticky=(tk.W, tk.E)
        )

        ttk.Label(frame, text="Max ADC Value:").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.val_max_adc_var).grid(
            row=4, column=1, sticky=(tk.W, tk.E)
        )

        ttk.Label(frame, text="VDD:").grid(row=5, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.vdd_var).grid(
            row=5, column=1, sticky=(tk.W, tk.E)
        )

        ttk.Checkbutton(frame, text="Enable Logging", variable=self.log_var).grid(
            row=6, column=0, columnspan=2, sticky=tk.W
        )
        ttk.Checkbutton(
            frame, text="Auto Delete Audio Files", variable=self.auto_delete_audio_var
        ).grid(row=6, column=1, columnspan=2, sticky=tk.W)

        self.connect_button = ttk.Button(
            frame, text="Connect", command=self.toggle_connection
        )
        self.connect_button.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(
            frame, text="Status: Disconnected", foreground="red"
        )
        self.status_label.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.console = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, width=50, height=10
        )
        self.console.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def print_stuff(self, stuff, type="data"):
        if type == "error":
            self.console.insert(tk.END, stuff + "\n", "error")
            self.console.tag_config("error", foreground="red")
        elif type == "data":
            self.console.insert(tk.END, stuff + "\n", "data")
        self.console.see(tk.END)
        # Additional print to console and log file
        print(stuff)
        if self.log_var.get():
            with open("uart_reader.log", "a") as f:
                f.write(stuff + "\n")

    def refresh_ports(self):
        ports = ["--no COM--"] + [
            f"{port.device} ({port.description})" for port in list_ports.comports()
        ]
        self.port_combobox["values"] = ports

    def toggle_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        port = self.port_var.get().split()[0]
        if self.port_var.get() == "--no COM--":
            self.print_stuff("Please select a COM port", "error")
            return

        if self.current_port and self.current_port != port:
            if not messagebox.askyesno(
                "Switch Connection", f"Do you want to switch connection to {port}?"
            ):
                return

        baudrate = self.baudrate_var.get()
        freq_sampling = self.freq_sampling_var.get()
        val_max_adc = self.val_max_adc_var.get()
        vdd = self.vdd_var.get()
        log_enabled = self.log_var.get()

        try:
            self.serial_connection = serial.Serial(port=port, baudrate=baudrate)
            self.current_port = port
            self.connect_button.config(text="Disconnect")
            self.status_label.config(
                text=f"Status: Connected > {port}", foreground="green"
            )
            self.print_stuff(f"Connected to {port}")
            self.stop_thread.clear()
            self.serial_thread = threading.Thread(target=self.read_serial)
            self.serial_thread.start()
        except Exception as e:
            self.connect_button.config(text="Connect")
            self.status_label.config(text="Status: Disconnected", foreground="red")
            self.print_stuff(f"Error: {e}", "error")

    def disconnect(self):
        self.stop_thread.set()
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=1)
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
            except Exception as e:
                self.print_stuff(f"Error closing connection: {e}", "error")
        self.current_port = None
        self.connect_button.config(text="Connect")
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.print_stuff("Disconnected")

    def read_serial(self):
        while not self.stop_thread.is_set():
            if self.serial_connection and self.serial_connection.is_open:
                try:
                    line = self.serial_connection.readline().decode("ascii").strip()
                    if line:
                        buffer = self.parse_buffer(line)
                        if buffer is not None:
                            dt = np.dtype(np.uint16)
                            dt = dt.newbyteorder("<")
                            buffer_array = np.frombuffer(buffer, dtype=dt)
                            self.print_stuff(f"Aquisition Number \t: {msg_counter}")
                            self.print_stuff(
                                f">Aquisition Memory\t: {len(line) - len(PRINT_PREFIX)} bytes"
                            )
                            self.print_stuff(
                                f">Aquisition Size  \t: {len(buffer_array)} samples"
                            )
                            plot_signal_and_fft(buffer_array, FREQ_SAMPLING)
                except Exception as e:
                    self.print_stuff(f"Error: {e}", "error")
                    self.disconnect()
                    return
            else:
                break

    def parse_buffer(self, line):
        if line.startswith(PRINT_PREFIX):
            return bytes.fromhex(line[len(PRINT_PREFIX) :])
        else:
            self.print_stuff(line)
            return None

    def on_closing(self):
        self.stop_thread.set()
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=1)
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
            except Exception as e:
                self.print_stuff(f"Error closing connection: {e}", "error")
        self.root.destroy()


def launch_gui():
    root = tk.Tk()
    app = UARTReaderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


stop_event = threading.Event()


def signal_handler(sig, frame):
    print("Interrupt received, stopping...")
    stop_event.set()


@click.command()
@click.option(
    "-p", "--port", default=None, type=str, help="Port for serial communication"
)
@click.option(
    "-b",
    "--baudrate",
    default=DEFAULT_BAUDRATE,
    type=int,
    help="Baudrate for serial communication",
)
@click.option(
    "-f", "--freq-sampling", default=FREQ_SAMPLING, type=int, help="Sampling frequency"
)
@click.option("-m", "--max-adc", default=VAL_MAX_ADC, type=int, help="Max ADC value")
@click.option("-v", "--vdd", default=VDD, type=float, help="VDD value")
@click.option(
    "-l", "--log", is_flag=True, type=bool, default=False, help="Enable logging"
)
@click.option(
    "-d",
    "--auto-delete",
    is_flag=True,
    type=bool,
    default=False,
    help="Auto delete audio files",
)
@click.option(
    "-g",
    "--gui",
    is_flag=True,
    type=bool,
    default=False,
    help="Launch the GUI (overrides other options)",
)
def main(port, baudrate, freq_sampling, max_adc, vdd, log, auto_delete, gui):
    # Register the signal handler (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    print("UART Reader Application Launching, use --help for help\n")

    if port:
        # Console mode: read the serial data from the specified port
        print(
            "Console mode activated, to stop, press 'Ctrl+C' then wait for a new serial input to close\n"
        )
        DEFAULT_BAUDRATE = baudrate
        FREQ_SAMPLING = freq_sampling
        VAL_MAX_ADC = max_adc
        VDD = vdd
        LOG_ENABLED = log
        AUTO_DELETE_AUDIO = auto_delete
        if gui:
            launch_gui()
        else:
            # Console mode: start reading serial data from the specified port
            read_serial(port.strip())

            # Make a audio folder if it doesn't exist
            if not os.path.exists("audio_files"):
                os.makedirs("audio_files")
            if AUTO_DELETE_AUDIO:
                for file in os.listdir("audio_files"):
                    os.remove(os.path.join("audio_files", file))

            if LOG_ENABLED:
                with open("uart_reader.log", "w") as f:
                    f.write("UART Reader Application Log\n")
    else:
        # GUI mode: open the application window
        launch_gui()


if __name__ == "__main__":
    main()
