"""
UART reader utilities, developed by the group E, 2024-2025.
"""

import logging
import os
import signal
import threading
import tkinter as tk
from shutil import rmtree
from tkinter import messagebox, scrolledtext, ttk

import click
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import serial
import soundfile as sf
from plotly.subplots import make_subplots
from serial.tools import list_ports

# Default values
PRINT_PREFIX = "SND:HEX:"
DEFAULT_PORT_INDEX = 1  # Change this if the default port is not the first one

# Global variables
logging.basicConfig(filename="uart_reader.log", level=logging.INFO)
logger = logging.getLogger(__name__)
global_audio_folder = "audio_files"
aquisition_counter = 0

global_freq_sampling = 10200
global_baudrate = 115200
global_val_max_adc = 4096
global_vdd = 3.3


def write_audio(buf, file_name, local_logger=logger):
    global global_audio_folder, global_freq_sampling
    buf = np.asarray(buf, dtype=np.float64)
    buf = buf - np.mean(buf)
    buf /= max(abs(buf))
    # Check if the buffer is empty, and if the folder exists
    if len(buf) == 0:
        local_logger.error(
            "Audio buffer is empty, aborting audio file creation \n\t >>> %s", file_name
        )
        return
    if not os.path.exists(global_audio_folder):
        os.makedirs(global_audio_folder)
    sf.write(f"{global_audio_folder}/{file_name}.wav", buf, global_freq_sampling)
    local_logger.info("Audio file created \n\t >>> %s", file_name)


def plot_signal_and_fft(signal, sampling_rate, local_logger=logger):
    global aquisition_counter, global_vdd, global_val_max_adc
    buffer_size = len(signal)
    times = np.linspace(0, buffer_size - 1, buffer_size) * 1 / sampling_rate
    voltage_mV = signal * global_vdd / global_val_max_adc * 1000

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
            x=times,
            y=voltage_mV,
            mode="lines",
            name=f"Acquisition #{aquisition_counter}",
        ),
        row=1,
        col=1,
    )
    # Plot FFT without DC component
    fig.add_trace(
        go.Scatter(
            x=freqs, y=fft_values, mode="lines", name=f"FFT #{aquisition_counter}"
        ),
        row=2,
        col=1,
    )

    # Show plots
    pio.show(fig, renderer="browser")

    aquisition_counter += 1


def read_serial(port, baudrate=global_baudrate, local_logger=logger):
    global aquisition_counter, global_freq_sampling
    """Reads the serial data and processes it for the console mode."""
    with serial.Serial(port, baudrate) as ser:
        local_logger.info(f"Connected to {port} with baudrate {baudrate}")
        while not stop_event.is_set():
            line = ser.readline().decode("ascii").strip()
            if line.startswith(PRINT_PREFIX):
                buffer = bytes.fromhex(line[len(PRINT_PREFIX) :])
                dt = np.dtype(np.uint16)
                dt = dt.newbyteorder("<")
                buffer_array = np.frombuffer(buffer, dtype=dt)

                local_logger.info(f"Aquisition Number : {aquisition_counter}")
                local_logger.info(
                    f">Aquisition Memory: {len(line) - len(PRINT_PREFIX)} bytes"
                )
                local_logger.info(f">Aquisition Size  : {len(buffer_array)} samples")

                # Generate audio file
                write_audio(signal, f"acq-{aquisition_counter}", local_logger)
                # Plot signal and FFT
                plot_signal_and_fft(buffer_array, global_freq_sampling, local_logger)
            else:
                local_logger.info(f"{line}")
    # Disconnect
    local_logger.info("Disconnected")


class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, ui_console):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Console it will log to
        self.ui_console = ui_console

        # Configure tags for different log levels
        self.ui_console.tag_config("INFO", foreground="black")
        self.ui_console.tag_config("WARNING", foreground="orange")
        self.ui_console.tag_config("ERROR", foreground="red")

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.ui_console.configure(state="normal")
            if record.levelno == logging.INFO:
                self.ui_console.insert(tk.END, msg + "\n", "INFO")
            elif record.levelno == logging.WARNING:
                self.ui_console.insert(tk.END, msg + "\n", "WARNING")
            elif record.levelno == logging.ERROR:
                self.ui_console.insert(tk.END, msg + "\n", "ERROR")
            self.ui_console.configure(state="disabled")

        # This is necessary because we can't modify the Text from other threads
        self.ui_console.after(0, append)


class UARTReaderApp:
    def __init__(self, root, port=None, baudrate=global_baudrate, freq_sampling=global_freq_sampling, val_max_adc=global_val_max_adc, vdd=global_vdd, logging_enabled=False, auto_delete_audio=False):
        self.root = root
        self.root.title("UART Reader")

        self.port_var = tk.StringVar(value="--no COM--")
        self.baudrate_var = tk.IntVar(value=baudrate)
        self.freq_sampling_var = tk.IntVar(value=freq_sampling)
        self.val_max_adc_var = tk.IntVar(value=val_max_adc)
        self.vdd_var = tk.DoubleVar(value=vdd)
        self.log_var = tk.BooleanVar(value=logging_enabled)
        self.auto_delete_audio_var = tk.BooleanVar(value=auto_delete_audio)

        self.log_var.trace_add("write", self.on_log_var_change)
        self.auto_delete_audio_var.trace_add(
            "write", self.on_auto_delete_audio_var_change
        )

        self.create_widgets()
        self.serial_connection = None
        self.serial_thread = None
        self.stop_thread = threading.Event()
        self.current_port = None

        self.ui_console_handler = TextHandler(self.console)
        self.ui_logger = logging.getLogger("UARTReaderApp")
        self.ui_logger.addHandler(self.ui_console_handler)

        if port:
            self.port_var.set(port)
            self.connect()

    def on_log_var_change(self, *args):
        logging_enabled = self.log_var.get()
        # Add the logic to handle the change in logging_enabled
        if logging_enabled:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        logger.info(f"Logging enabled: {logging_enabled}")

    def on_auto_delete_audio_var_change(self, *args):
        auto_delete_audio = self.auto_delete_audio_var.get()
        # Add the logic to handle the change in auto_delete_audio
        logger.info(
            f"Auto delete audio: {auto_delete_audio}\n Audio files will be deleted at each connection (and names will be reset)"
        )

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

        ttk.Label(frame, text="vdd:").grid(row=5, column=0, sticky=tk.W)
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

    def serial_worker(self):
        read_serial(self.port_var.get(), self.baudrate_var.get(), self.ui_logger)

    def connect(self):
        global aquisition_counter
        port = self.port_var.get().split()[0]
        baudrate = self.baudrate_var.get()

        if self.port_var.get() == "--no COM--":
            self.ui_logger.error("Please select a COM port")
            return

        if self.current_port and self.current_port != port:
            if not messagebox.askyesno(
                "Switch Connection", f"Do you want to switch connection to {port}?"
            ):
                return

        # Auto delete audio files if the option is enabled
        if self.auto_delete_audio_var.get():
            rmtree("audio_files")
            os.makedirs("audio_files")
            aquisition_counter = 0

        try:
            self.serial_connection = serial.Serial(port=port, baudrate=baudrate)
            self.current_port = port
            self.connect_button.config(text="Disconnect")
            self.status_label.config(
                text=f"Status: Connected > {port}", foreground="green"
            )
            self.ui_logger.info(f"Connected to {port} with baudrate {baudrate}")
            self.stop_thread.clear()
            self.serial_thread = threading.Thread(target=self.serial_worker)
            self.serial_thread.start()
        except serial.SerialException as e:
            self.connect_button.config(text="Connect")
            self.status_label.config(text="Status: Disconnected", foreground="red")
            self.ui_logger.error(f"Error connecting to {port}: {e}")

    def disconnect(self):
        self.stop_thread.set()
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.join(timeout=1)
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
            except Exception as e:
                self.ui_logger.error(f"Error closing connection: {e}")
        self.current_port = None
        self.connect_button.config(text="Connect")
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.ui_logger.info("Disconnected")

    def on_closing(self):
        self.stop_thread.set()
        if self.serial_thread and self.serial_thread.is_alive():
            # Kill the thread if it's still running
            self.serial_thread.join(timeout=1)
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
            except Exception as e:
                self.ui_logger.error(f"Error closing connection: {e}")
        self.root.destroy()


def launch_gui(port=None, baudrate=global_baudrate, freq_sampling=global_freq_sampling, val_max_adc=global_val_max_adc, vdd=global_vdd, logging_enabled=False, auto_delete_audio=False):
    logger.info("Launching GUI")
    root = tk.Tk()
    app = UARTReaderApp(root, port, baudrate, freq_sampling, val_max_adc, vdd, logging_enabled, auto_delete_audio)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


stop_event = threading.Event()


def signal_handler(sig, frame):
    print("Interrupt received, stopping...")
    stop_event.set()


@click.command()
@click.option(
    "-p", "--port", default=None, type=int, help="Port for serial communication"
)
@click.option(
    "-b",
    "--baudrate",
    default=115200,
    type=int,
    help="Baudrate for serial communication",
)
@click.option(
    "-f", "--freq-sampling", default=10200, type=int, help="Sampling frequency"
)
@click.option("-m", "--max-adc", default=4096, type=int, help="Max ADC value")
@click.option("-v", "--vdd", default=3.3, type=float, help="vdd value")
@click.option(
    "-l", "--log", is_flag=True, type=bool, default=False, help="Enable debug logging"
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
    "-a",
    "--audio-folder",
    default="audio_files",
    type=str,
    help="Folder for audio files",
)
@click.option(
    "-g",
    "--gui",
    is_flag=True,
    type=bool,
    default=False,
    help="Launch the GUI (overrides other options)",
)
def main(
    port,
    baudrate,
    freq_sampling,
    max_adc,
    vdd,
    log,
    auto_delete,
    audio_folder,
    gui,
):
    """
    UART reader utiliy.

    Developed by the group E, 2024-2025.
    """
    global global_freq_sampling, global_baudrate, global_val_max_adc, global_vdd, global_audio_folder

    # Register the signal handler (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("UART Reader Application Launching, use --help for help\n")

    # Set the global variables
    global_freq_sampling = freq_sampling
    global_baudrate = baudrate
    global_val_max_adc = max_adc
    global_vdd = vdd
    global_audio_folder = audio_folder

    if port:
        # Console mode: read the serial data from the specified port
        logger.info(
            "Console mode activated, to stop, press 'Ctrl+C' then wait for a new serial input to close\n"
        )

        # Make a audio folder if it doesn't exist
        if auto_delete:
            rmtree("audio_files")

        # Enable logging if the flag is set
        if log:
            logger.setLevel(logging.DEBUG)  # Enable logging

        # Start the GUI if the flag is set
        if gui:
            launch_gui(
                port=port,
                baudrate=baudrate,
                freq_sampling=freq_sampling,
                vdd=vdd,
                logging_enabled=log,
                auto_delete_audio=auto_delete,
            )
        else:
            # Console mode: start reading serial data from the specified port
            read_serial(port.strip())

    else:
        # GUI mode: open the application window
        launch_gui(baudrate=baudrate, freq_sampling=freq_sampling, val_max_adc=max_adc, vdd=vdd, logging_enabled=log, auto_delete_audio=auto_delete)


if __name__ == "__main__":
    main()
