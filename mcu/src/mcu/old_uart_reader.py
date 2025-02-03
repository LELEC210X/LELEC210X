"""
UART reader utilities, developed by the group E, 2024-2025.
"""

# Standard Library
import logging
import os
import sys
from shutil import rmtree

# Installed Libraries
import click
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as plts
import serial
import soundfile as sf
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from serial.tools import list_ports

# Constants
PRINT_PREFIX = "SND:HEX:"


# Set up logging
def setup_logging(log_level, log_file):
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="[%(asctime)s] %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler("uart_reader.log")
            if log_file
            else logging.StreamHandler()
        ],
    )


# Write data to serial port
def write_to_serial(ser: serial.Serial, data: str, logger_obj: logging.Logger):
    ser.write(data.encode("utf-8"))
    logger_obj.info(f"Sent data: {data}")


# Read data from serial port
def read_from_serial(ser: serial.Serial):
    if ser.in_waiting > 0:
        data = ser.readline().decode("utf-8").strip()
        return data
    return None


# Write audio data to file
def write_audio(
    signal: np.ndarray,
    sampling_frequency: int,
    audio_output_folder: str,
    audio_file_name: str,
    audio_output_type: str,
    overwrite: bool,
    logger_obj: logging.Logger,
):
    if signal is None or len(signal) == 0:
        logger_obj.error(
            f"No audio data to write for file {audio_file_name}.{audio_output_type.lower()}"
        )
        return
    # Normalize the audio data, convert to float64 and center around 0
    signal = np.asarray(signal, dtype=np.float64)
    signal = signal - np.mean(signal)
    signal /= np.max(np.abs(signal))

    # Write the audio data to file (overwrite if necessary)
    file_path = f"{audio_output_folder}/{audio_file_name}.{audio_output_type.lower()}"
    if not overwrite and os.path.exists(file_path):
        logger_obj.error(
            f"File {file_path} already exists. Set overwrite to True to overwrite the file."
        )
        while not overwrite and os.path.exists(file_path):
            audio_file_name += "_1"
            file_path = (
                f"{audio_output_folder}/{audio_file_name}.{audio_output_type.lower()}"
            )
    elif os.path.exists(file_path):
        os.remove(file_path)
    sf.write(file_path, signal, sampling_frequency)
    logger_obj.info(f">> Generated audio in {audio_output_type} format at {file_path}")


# Plot data using Plotly
def plot_data_and_fft(
    signal: np.ndarray,
    sampling_frequency: int,
    vdd: float,
    max_adc_value: int,
    plot_output_type: str,
    plot_name: str,
    logger_obj: logging.Logger,
):
    if signal is None or len(signal) == 0:
        logger_obj.error("No audio data to plot")
        return
    # Calculate the time and voltage values
    signal_size = len(signal)
    time = np.linspace(0, signal_size - 1, signal_size) * 1 / sampling_frequency
    voltage_mV = signal * vdd / max_adc_value * 1000

    # Calculate FFT
    n = len(voltage_mV)
    fft_values = np.fft.fft(voltage_mV)
    fft_values = np.abs(fft_values)[: n // 2]  # Magnitude of the FFT
    freqs = np.fft.fftfreq(n, 1 / sampling_frequency)[
        : n // 2
    ]  # Associated frequencies
    # Exclude the DC component (frequency 0)
    freqs = freqs[1:]
    fft_values = fft_values[1:]

    # Plot the data
    fig = plts.make_subplots(rows=2, cols=1, vertical_spacing=0.02)
    fig.add_trace(go.Scatter(x=time, y=voltage_mV, name="Voltage (mV)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=freqs, y=fft_values, name="FFT"), row=2, col=1)
    fig.update_layout(title_text=f"Audio Data and FFT for {plot_name}")
    fig.update_xaxes(title_text="Time (s)", row=1, col=1)
    fig.update_xaxes(title_text="Frequency (Hz)", row=2, col=1)
    fig.update_yaxes(title_text="Voltage (mV)", row=1, col=1)
    fig.update_yaxes(title_text="Magnitude", row=2, col=1)

    if plot_output_type == "FILE":
        fig.write_html(f"{plot_name}.html")
        logger_obj.info(f">> Plot saved to {plot_name}.html")
    else:
        fig.show()
        logger_obj.info(">> Plot displayed in browser")


# Process a data buffer into signal data
def process_sound_buffer(sound_buffer: str) -> np.ndarray:
    buffer = bytes.fromhex(sound_buffer[len(PRINT_PREFIX) :])
    dt = np.dtype(np.uint16)
    dt = dt.newbyteorder("<")
    return np.frombuffer(buffer, dtype=dt)


# Thread for reading serial data
class SerialReader(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port: str, baudrate: int, logger_obj: logging.Logger):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.is_running = False
        self.logger_obj = logger_obj

    def run(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate)
            self.is_running = True
            self.logger_obj.info(f"Connected to {self.port} at {self.baudrate} baud.")
            while self.is_running:
                if self.serial.in_waiting > 0:
                    data = self.serial.readline().decode("ascii").strip()
                    self.data_received.emit(data)

        except serial.SerialException as e:
            self.logger_obj.error(e)
            self.data_received.emit("TERMINATE")
            self.stop()
        finally:
            if self.serial:
                self.serial.close()
                self.logger_obj.info("Serial port closed.")

    def stop(self):
        self.is_running = False


# GUI application
class SerialGUIApp(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.aquisition_counter = 0

        # Set up logging
        self.logger = logging.getLogger(__name__)

        self.initUI()

        # Set up the logging handler for the console output
        self.log_handler = self.GUILoggingHandler(self.console_output)
        self.log_handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(self.log_handler)

    class GUILoggingHandler(logging.Handler):
        def __init__(self, console_output):
            super().__init__()
            self.console_output = console_output

        def emit(self, record: str):
            exploded = self.format(record).split(": ")
            output_message = (
                exploded[0] if len(exploded) == 1 else "".join(exploded[1:])
            )
            # Make it red if its an error
            if record.levelno >= logging.ERROR:
                self.console_output.append(
                    f"<font color='red'>Error: {output_message}</font>"
                )
            else:
                self.console_output.append(output_message)
            # Scroll to the bottom
            self.console_output.ensureCursorVisible()

    def h_layout_box(self, layout: QVBoxLayout) -> QHBoxLayout:
        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        return h_layout

    def h_layout_stretch(self, h_layout: QHBoxLayout):
        h_layout.setStretch(0, 2)
        h_layout.setStretch(1, 6)
        h_layout.setStretch(2, 1)

    def initUI(self):
        self.setWindowTitle("Serial Console App")
        self.resize(600, 400)

        # Layout
        layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        # Credits and Instructions
        self.credits_label = QLabel("UART Console App for LELEC210x")
        self.author_label = QLabel("Developed by Group E 2024 - 2025")
        layout.addWidget(self.credits_label)
        layout.addWidget(self.author_label)
        self.instructions_label = QLabel(
            " How to use : Select a Serial Port and press Connect"
        )
        layout.addWidget(self.instructions_label)

        self.credits_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.author_label.setStyleSheet("font-size: 10px; font-style: italic;")
        self.instructions_label.setStyleSheet("font-size: 14px;")

        # Serial Port Dropdown
        h_serial_layout = self.h_layout_box(layout)
        self.port_label = QLabel("Serial Port")
        self.port_dropdown = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_ports)
        h_serial_layout.addWidget(self.port_label)
        h_serial_layout.addWidget(self.port_dropdown)
        h_serial_layout.addWidget(self.refresh_button)
        self.h_layout_stretch(h_serial_layout)

        # Select the first port by default (if available)
        self.refresh_ports()
        if self.port_dropdown.count() > 1:
            self.port_dropdown.setCurrentIndex(1)

        # Baudrate Input
        h_baudrate_layout = self.h_layout_box(layout)
        h_baudrate_layout.addWidget(QLabel("Baudrate"))
        self.baudrate_input = QLineEdit()
        self.baudrate_input.setText(str(self.settings["baudrate"]))
        h_baudrate_layout.addWidget(self.baudrate_input)
        h_baudrate_layout.addWidget(QLabel())
        self.h_layout_stretch(h_baudrate_layout)

        # Sampling Frequency Input
        h_sampling_layout = self.h_layout_box(layout)
        h_sampling_layout.addWidget(QLabel("Sampling Frequency"))
        self.sampling_input = QLineEdit()
        self.sampling_input.setText(str(self.settings["sampling_frequency"]))
        h_sampling_layout.addWidget(self.sampling_input)
        h_sampling_layout.addWidget(QLabel("Hz"))
        self.h_layout_stretch(h_sampling_layout)

        # Max ADC Value Input
        h_max_adc_layout = self.h_layout_box(layout)
        h_max_adc_layout.addWidget(QLabel("Max ADC Value"))
        self.max_adc_input = QLineEdit()
        self.max_adc_input.setText(str(self.settings["max_adc_value"]))
        h_max_adc_layout.addWidget(self.max_adc_input)
        h_max_adc_layout.addWidget(QLabel())
        self.h_layout_stretch(h_max_adc_layout)

        # VDD Input
        h_vdd_layout = self.h_layout_box(layout)
        h_vdd_layout.addWidget(QLabel("VDD"))
        self.vdd_input = QLineEdit()
        self.vdd_input.setText(str(self.settings["vdd"]))
        h_vdd_layout.addWidget(self.vdd_input)
        h_vdd_layout.addWidget(QLabel("V"))
        self.h_layout_stretch(h_vdd_layout)

        # Plot Output Type Dropdown
        h_plot_layout = self.h_layout_box(layout)
        h_plot_layout.addWidget(QLabel("Plot Output Type"))
        self.plot_dropdown = QComboBox()
        self.plot_dropdown.addItems(["WEB", "FILE"])
        h_plot_layout.addWidget(self.plot_dropdown)
        h_plot_layout.addWidget(QLabel())
        self.h_layout_stretch(h_plot_layout)

        # Audio Output Type Dropdown
        h_audio_layout = self.h_layout_box(layout)
        h_audio_layout.addWidget(QLabel("Audio Output Type"))
        self.audio_dropdown = QComboBox()
        self.audio_dropdown.addItems(["WAV", "OGG"])
        h_audio_layout.addWidget(self.audio_dropdown)
        h_audio_layout.addWidget(QLabel())
        self.h_layout_stretch(h_audio_layout)

        # Audio Output Folder Input
        h_audio_folder_layout = self.h_layout_box(layout)
        h_audio_folder_layout.addWidget(QLabel("Audio Output Folder"))
        self.audio_folder_input = QLineEdit()
        self.audio_folder_input.setText(self.settings["audio_output_folder"])
        self.audio_folder_input.setReadOnly(True)
        h_audio_folder_layout.addWidget(self.audio_folder_input)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        h_audio_folder_layout.addWidget(self.browse_button)
        self.h_layout_stretch(h_audio_folder_layout)

        # Overwrite Audio Checkbox
        h_overwrite_layout = self.h_layout_box(layout)
        self.overwrite_checkbox = QCheckBox("Overwrite Audio")
        self.overwrite_checkbox.setChecked(self.settings["overwrite_audio"])
        h_overwrite_layout.addWidget(QLabel(""))
        h_overwrite_layout.addWidget(self.overwrite_checkbox)
        self.clear_audio_button = QPushButton("Clear Audio Folder")
        self.clear_audio_button.clicked.connect(self.clear_audio_folder)
        h_overwrite_layout.addWidget(self.clear_audio_button)
        self.h_layout_stretch(h_overwrite_layout)

        # Connect Button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_serial)
        layout.addWidget(self.connect_button)

        # Status Label
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

        # Console Output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(200)
        layout.addWidget(self.console_output)

        # Serial Reader Thread
        self.serial_thread = None

    def refresh_ports(self):
        old_port = self.port_dropdown.currentText()
        self.port_dropdown.clear()
        ports = ["-- No COM --"] + [
            f"{port.device} - {port.description}" for port in list_ports.comports()
        ]
        self.port_dropdown.addItems(ports)
        if old_port == "-- No COM --" and len(ports) > 1:
            self.port_dropdown.setCurrentIndex(1)
        elif old_port in ports:
            self.port_dropdown.setCurrentText(old_port)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder", self.settings["audio_output_folder"]
        )
        if folder:
            self.audio_folder_input.setText(folder)
            self.settings["audio_output_folder"] = folder
            # Create the audio output folder if it doesn't exist
            if not os.path.exists(folder):
                os.makedirs(folder)
        else:
            self.logger.error("No folder selected")

    def clear_audio_folder(self):
        # Make a verification dialog
        dialog = QMessageBox()
        dialog.setWindowTitle("Clear Audio Folder")
        dialog.setText("Are you sure you want to clear the audio folder?")
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        if dialog.exec() == QMessageBox.StandardButton.Yes:
            rmtree(self.settings["audio_output_folder"])
            self.logger.info("Audio folder cleared.")
        else:
            self.logger.info("Audio folder not cleared.")
            return
        # Recreate the audio folder
        os.makedirs(self.settings["audio_output_folder"])

    def connect_serial(self):
        port = self.port_dropdown.currentText()
        # Check if a port is selected
        if port == "-- No COM --":
            self.logger.error(
                "No COM port selected, please select a COM port (refreshed)."
            )
            self.refresh_ports()
            return
        else:
            port = port.split(" - ")[0]
        # If the port is already connected, disconnect it
        if self.serial_thread:
            self.disconnect_serial()
        # Create a new serial thread
        baudrate = int(self.baudrate_input.text())
        self.serial_thread = SerialReader(port, baudrate, self.logger)
        self.serial_thread.data_received.connect(
            self.update_console
        )  # HACK here is where the data is reflected
        self.status_label.setText(f"Status: Connected > {port}")
        self.status_label.setStyleSheet("color: green;")
        self.connect_button.setText("Disconnect")
        try:
            self.connect_button.clicked.disconnect(self.connect_serial)
            self.connect_button.clicked.disconnect(self.disconnect_serial)
        except TypeError:
            pass
        self.connect_button.clicked.connect(self.disconnect_serial)
        # Start reading data
        self.serial_thread.start()

    def disconnect_serial(self):
        # Check if the serial thread is running
        if not self.serial_thread:
            self.logger.error("No serial thread running.")
            return
        # Disconnect the serial port
        try:
            self.connect_button.clicked.disconnect(self.disconnect_serial)
            self.connect_button.clicked.disconnect(self.connect_serial)
        except TypeError:
            pass
        self.connect_button.setDisabled(True)
        # Stop the serial thread
        self.serial_thread.stop()
        self.serial_thread.wait()
        # Update the UI
        self.status_label.setText("Status: Disconnected")
        self.status_label.setStyleSheet("color: red;")
        self.connect_button.setText("Connect")
        self.connect_button.clicked.connect(self.connect_serial)
        self.connect_button.setEnabled(True)

    # Update the console output, process the sound buffer and write the audio
    def update_console(self, message: str):
        if message == "TERMINATE":
            self.disconnect_serial()
            self.refresh_ports()
        elif message.startswith(PRINT_PREFIX):
            # Process the sound buffer
            data = process_sound_buffer(message)
            self.aquisition_counter += 1
            plot_name = f"Audio Plot {self.aquisition_counter}"

            # Log general information
            self.logger.info(f">> Aquisition {self.aquisition_counter} completed")
            self.logger.info(
                f">> Aquisition size of {len(data)} samples encoded in {len(message) - len(PRINT_PREFIX)} bytes"
            )

            # Plot and write audio
            plot_data_and_fft(
                data,
                self.settings["sampling_frequency"],
                self.settings["vdd"],
                self.settings["max_adc_value"],
                self.settings["plot_output_type"],
                plot_name,
                self.logger,
            )
            write_audio(
                data,
                self.settings["sampling_frequency"],
                self.settings["audio_output_folder"],
                f"audio_{self.aquisition_counter}",
                self.settings["audio_output_type"],
                self.settings["overwrite_audio"],
                self.logger,
            )
        else:
            # self.console_output.append(message)  #HACK Covered by the custom handler
            self.logger.info(f"Received data: {message}")


# CLI application logic
def run_cli(settings: dict):
    # Set up logging
    logger = logging.getLogger(__name__)

    # Console information
    logger.info("===============================================")
    logger.info("         UART Console App for LELEC210x         ")
    logger.info("      ~ Developed by Group E 2024 - 2025 ~     ")
    logger.info("   ~ To exit the application, press Ctrl+C ~   ")
    logger.info("===============================================")

    # Connect to the serial port
    port = settings["port"]
    baudrate = settings["baudrate"]
    try:
        ser = serial.Serial(port, baudrate)
        logger.info(f"Connected to {port} at {baudrate} baud.")
    except serial.SerialException as e:
        logger.error(e)
        return

    # Read data from the serial port
    while True:
        data = read_from_serial(ser)
        if data:
            if data.startswith(PRINT_PREFIX):
                # Process the sound buffer
                sound_data = process_sound_buffer(data)
                plot_name = f"Audio Plot {settings['sampling_frequency']}Hz"
                # Log general information
                logger.info(
                    f">> Aquisition size of {len(sound_data)} samples encoded in {len(data) - len(PRINT_PREFIX)} bytes"
                )
                # Plot and write audio
                plot_data_and_fft(
                    sound_data,
                    settings["sampling_frequency"],
                    settings["vdd"],
                    settings["max_adc_value"],
                    settings["plot_output_type"],
                    plot_name,
                    logger,
                )
                write_audio(
                    sound_data,
                    settings["sampling_frequency"],
                    settings["audio_output_folder"],
                    f"audio_{settings['sampling_frequency']}Hz",
                    settings["audio_output_type"],
                    settings["overwrite_audio"],
                    logger,
                )
            else:
                logger.info(f"{data}")


@click.command()
@click.option(
    "-p",
    "--port",
    default="-- No COM --",
    type=str,
    help="The serial port to read data from.",
)
@click.option(
    "-b",
    "--baudrate",
    default=115200,
    type=int,
    help="The baudrate of the serial port.",
)
@click.option(
    "-s",
    "--sampling-frequency",
    default=10200,
    help="The sampling frequency of the ADC.",
)
@click.option(
    "-m",
    "--max-adc-value",
    default=4096,
    type=int,
    help="The maximum value of the ADC.",
)
@click.option(
    "-v", "--vdd", default=3.3, type=float, help="The voltage of the power supply."
)
@click.option(
    "-o",
    "--plot-output-type",
    default="WEB",
    type=click.Choice(["WEB", "FILE"]),
    help="The type of output for the plot.",
)
@click.option(
    "-l",
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="The level of logging.",
)
@click.option(
    "-f",
    "--log-file",
    is_flag=True,
    help="Whether to log to a file (Not modifiable at runtime).",
)
@click.option(
    "-w",
    "--overwrite-audio",
    is_flag=True,
    help="Whether to overwrite the audio folder.",
)
@click.option(
    "-a",
    "--audio-output-type",
    default="WAV",
    type=click.Choice(["WAV", "OGG"]),
    help="The type of output for the audio.",
)
@click.option(
    "-d",
    "--audio-output-folder",
    default="audio_files",
    type=str,
    help="The folder to save the audio files.",
)
@click.option("-c", "--cli", is_flag=True, help="Whether to run the CLI application.")
def main(
    port: str,
    baudrate: int,
    sampling_frequency: int,
    max_adc_value: int,
    vdd: float,
    plot_output_type: str,
    log_level: str,
    log_file: bool,
    overwrite_audio: bool,
    audio_output_type: str,
    audio_output_folder: str,
    cli: bool,
):
    settings = {
        "port": port,
        "baudrate": baudrate,
        "sampling_frequency": sampling_frequency,
        "max_adc_value": max_adc_value,
        "vdd": vdd,
        "plot_output_type": plot_output_type,
        "log_level": log_level,
        "log_file": log_file,
        "overwrite_audio": overwrite_audio,
        "audio_output_type": audio_output_type,
        "audio_output_folder": audio_output_folder,
    }

    # Create the audio output folder where the script is if it doesn't exist
    settings["audio_output_folder"] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), settings["audio_output_folder"]
    )
    if not os.path.exists(settings["audio_output_folder"]):
        os.makedirs(settings["audio_output_folder"])

    # Create the logger
    setup_logging(log_level, log_file)

    # Run the GUI or CLI application
    if not cli:
        app = QApplication(sys.argv)
        window = SerialGUIApp(settings)
        window.show()
        sys.exit(app.exec())
    else:
        run_cli(settings)


if __name__ == "__main__":
    main()
