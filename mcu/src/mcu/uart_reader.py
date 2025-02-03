"""
UART reader utilities, developed by the group E, 2024-2025.
"""

# Standard Library
import logging
import os
import sys
from shutil import rmtree
import pathlib as pathl
import datetime
from threading import Lock
from queue import Queue
from typing import Optional
import time

# Installed Libraries
import click
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as plts
from serial import Serial, SerialException
import soundfile as sf
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QGridLayout,
    QTabWidget,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from serial.tools import list_ports

import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Local
#from mcu.src.mcu import user_classifier


###############################################################################
# Settings

class APP_Settings():
    """
    Class to store the settings of the application.

    Must be accessed using a thread lock or similar
    """
    def __init__(self):
        # App stuff
        self.app_folder = pathl.Path(__file__).parent
        self.app_name = "UART Console App for LELEC210x"
        self.app_version = "0.2.0"
        self.app_author = "Group E, 2024-2025"
        self.app_description = "UART reader utilities."
        
        # Logging settings
        self.logging_level = logging.DEBUG
        self.logging_format = "[%(asctime)s] %(levelname)-9s: %(message)s"
        self.logging_date_format = "%Y-%m-%d %H:%M:%S"
        self.logging_use_file = True
        self.logging_file = self.app_folder / "uart_reader.log"
        self.logging_file_max_size = 1024 * 1024 # 1 MB
        self.logging_file_backup_count = 3

        # GUI settings
        self.gui_use_fixed_FPS = False
        self.gui_update_rate = 60 # FPS
        self.gui_max_samples = 1024
        self.gui_use_plotly = False
        self.gui_use_matplotlib_blit = False
        self.gui_min_window_size = (800, 600)
        self.gui_default_window_size = (1280//2, 720) # Read only

        # Plotting settings
        self.plot_name_prefix = "plot"
        self.plot_name_postfix_timestamp = True
        self.plot_save_types = ["pdf", "png"]
        self.plot_save_all_types = True
        self.plot_save_folder_base = self.app_folder / "plots"

        # Serial settings
        self.serial_port = "-- No serial port --"
        self.serial_baud_rate = 115200 # bps
        self.serial_timeout = 1
        self.serial_allow_write = False
        self.serial_freeze = False

        # Nucleo board settings
        self.nucleo_config_serial_prefix = "CFG:HEX:"
        self.nucleo_sample_rate = 10240 # Hz

        # Audio settings
        self.audio_serial_prefix = "SND:HEX:"
        self.audio_folder = self.app_folder / "audio"
        self.audio_file_name_prefix = "audio"
        self.audio_file_types = ["wav", "ogg", "mp3", "flac"] # [0, ["wav", "ogg", "mp3", "flac"]] --> Drop down menu
        self.audio_file_type = self.audio_file_types[0]
        self.audio_file_freq = 44100 # Hz
        self.audio_file_channels = 1
        self.audio_file_dtype = "int16"
        self.audio_file_save_numpy = False
        self.audio_file_save_plots = False
        self.audio_file_auto_save = False
        self.audio_file_auto_clear = False

        # Mel spectrogram settings
        self.mel_serial_prefix = "MEL:HEX:"
        self.mel_vector_size = 20
        self.mel_vector_num = 20
        self.mel_samples = 512
        self.mel_history_max_mem = 20 # Max in memory
        self.mel_history_max_shown = 10 # Max shown
        self.mel_autosave = False # As numpy file (dictionary)
        self.mel_file_name_prefix = "mel"
        self.mel_autosave_folder = self.app_folder / "mel_spectrograms"
        self.mel_autosave_plots = False
        self.mel_autosave_numpy = False
        self.mel_autosave_clear = False

        # User classifier settings
        self.classifier_use = False
        self.classifier_file_pickle = self.app_folder / "user_classifier.pkl" # If found, load
        self.classifier_file_numpy = self.app_folder / "user_classifier.npy" # If found, load (secondary)
        self.classifier_file_auto_save = False # As numpy file (dictionary)
        self.classifier_file_auto_save_mel = True
        self.classifier_file_auto_save_plots = False
        self.classifier_use_mel_history = False # Requires the use of the .npy with a dictionary and "history_len" key
        self.classifier_history_max_shown = 10 # Max shown

###############################################################################
# Logging

# Custom levels
LOGGING_GOOD = 25

def setup_logging(settings):
    """
    Setup the logging system.
    """
    # Create the logger
    logger = logging.getLogger(settings.app_name)
    logger.setLevel(settings.logging_level)

    # Add a GOOD level for the logger
    logging.addLevelName(LOGGING_GOOD, "GOOD")
    def good(self, message, *args, **kws):
        if self.isEnabledFor(LOGGING_GOOD):
            self._log(LOGGING_GOOD, message, args, **kws)
    logging.Logger.good = good

    # Create the formatter
    formatter = logging.Formatter(settings.logging_format, settings.logging_date_format)

    # Create the console handler (CLI)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create the file handler
    if settings.logging_use_file:
        file_handler = logging.FileHandler(settings.logging_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Return the logger
    return logger

class QTextEditLogger(logging.Handler):
    """
    Custom logging handler that writes to a QTextEdit widget on the GUI.
    """
    def __init__(self, text_edit: QTextEdit, settings: APP_Settings):
        super().__init__()
        self.text_edit = text_edit
        self.app_settings = settings

    STYLES = {
        logging.INFO:       "color: black",
        LOGGING_GOOD:       "color: green",
        logging.DEBUG:      "color: blue",
        logging.WARNING:    "color: orange",
        logging.ERROR:      "color: red",
        logging.CRITICAL:   "color: red; font-weight: bold",
    }

    HAS_RECORD_NAME = {
        logging.INFO:       False,
        LOGGING_GOOD:       False,
        logging.DEBUG:      True,
        logging.WARNING:    True,
        logging.ERROR:      True,
        logging.CRITICAL:   True,
    }

    def emit(self, record: logging.LogRecord):
        msg = record.getMessage()
        line = (f"<span style='{self.STYLES.get(record.levelno, '')}; white-space: pre'>",
                f"[{datetime.datetime.fromtimestamp(record.created).strftime(self.app_settings.logging_date_format)}] ", # Date
                f" {record.levelname} " if self.HAS_RECORD_NAME.get(record.levelno, True) else " ", # Level
                f">> {msg}",
                "</span>")
        # Append to the text edit if its smaller than 500 lines
        if self.text_edit.document().blockCount() < 500:
            self.text_edit.append("".join(line))

def test_logging(logger: logging.Logger):
    for i in range(2):
            logger.info(f"Test log {i}")
            logger.debug(f"Test log {i}")
            logger.warning(f"Test log {i}")
            logger.error(f"Test log {i}")
            logger.critical(f"Test log {i}")
            logger.good(f"Test log {i}")

###############################################################################
# Serial

def get_available_ports():
    """
    Get the available serial ports.
    """
    return [f"{port.device} - {port.description}" for port in list_ports.comports()]

class SerialReader(QThread):
    """
    Thread-safe serial port reader with queued writing capability.
    
    Signals:
        data_received (str): Emitted when data is received from serial port
        connection_state (bool): Emitted when connection state changes
        error_occurred (str): Emitted when an error occurs
    """
    data_received = pyqtSignal(str)
    connection_state = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, settings, logger: logging.Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self._serial: Optional[Serial] = None
        self._running = False
        self._write_queue = Queue()
        self._lock = Lock()
        self._buffer_size = 1024 * 8
        self._thread_id = None

    @property
    def is_connected(self) -> bool:
        """Check if serial port is connected and operational"""
        with self._lock:
            return self._serial is not None and self._serial.is_open

    def try_start(self) -> bool:
        """Attempt to start the serial reader thread safely"""
        try:
            if self._thread_id is not None:
                self.logger.warning("Thread already running")
                return False

            if self.settings.serial_port == "-- No serial port --":
                return False

            self._running = True
            self.start()
            return True

        except Exception as e:
            self.logger.error(f"Failed to start serial reader: {e}")
            return False

    def run(self) -> None:
        """Main thread loop"""
        try:
            self._thread_id = QThread.currentThreadId()
            self._connect()
            self._read_loop()
        except Exception as e:
            self._handle_error(f"Thread error: {e}")
        finally:
            self._thread_id = None
            self._cleanup()

    def _connect(self) -> None:
        """Connect to serial port"""
        try:
            port = self.settings.serial_port.split(" - ")[0]
            
            with self._lock:
                if self._serial is not None:
                    return

                self._serial = Serial(
                    port=port,
                    baudrate=self.settings.serial_baud_rate,
                    timeout=self.settings.serial_timeout,
                    write_timeout=1.0
                )
                
            self.logger.good(f"Connected to {self.settings.serial_port}")
            self.connection_state.emit(True)
            
        except Exception as e:
            self._cleanup()
            raise RuntimeError(f"Connection failed: {e}")


    def _check_connection(self) -> bool:
        """Check if connection is still alive"""
        try:
            with self._lock:
                if not self._serial:
                    return False
                # Try to get port status - will fail if disconnected
                self._serial.in_waiting
                return True
        except (SerialException, OSError):
            return False
    
    def _read_loop(self) -> None:
        """Main reading loop with connection monitoring"""
        while self._running:
            try:
                # Check connection status
                if not self._check_connection():
                    self._handle_error("Serial port disconnected unexpectedly")
                    break

                # Process write queue
                if not self._write_queue.empty() and self.settings.serial_allow_write:
                    self._process_write_queue()

                # Read available data with timeout
                try:
                    if self._serial.in_waiting > 0 and not self.settings.serial_freeze:
                        data = self._serial.readline(self._buffer_size)
                        if data:
                            decoded = data.decode("ascii").strip()
                            self.data_received.emit(decoded)
                except (SerialException, OSError) as e:
                    self._handle_error(f"Serial port error: {e}")
                    break
                except UnicodeDecodeError as e:
                    self.logger.warning(f"Decode error: {e}")
                    continue
                
                # Small sleep to prevent CPU hogging
                time.sleep(0.001)
                
            except Exception as e:
                self._handle_error(f"Unexpected error in read loop: {e}")
                break

    def _process_write_queue(self) -> None:
        """Process pending write operations"""
        try:
            while not self._write_queue.empty():
                data = self._write_queue.get_nowait()
                with self._lock:
                    if self._serial and self._serial.is_open:
                        self._serial.write(data.encode("ascii"))
                self._write_queue.task_done()
        except Exception as e:
            self.logger.error(f"Write error: {e}")

    def send_data(self, data: str) -> None:
        """
        Queue data to be sent over serial port.
        
        Args:
            data (str): Data to send
        """
        if not data:
            return
        self.logger.debug(f"Queueing data: {data}")
        self._write_queue.put(data)

    def stop(self) -> bool:
        """Stop thread safely"""
        try:
            if self._thread_id is None:
                return True

            self.logger.debug("Stopping reader")
            self._running = False

            # Close serial port
            with self._lock:
                if self._serial:
                    try:
                        self._serial.close()
                    except:
                        pass
                    self._serial = None

            # Wait for thread to finish
            if QThread.currentThread() != self:
                if not self.wait(1000):
                    self.terminate()
                    self.wait(500)

            return True

        except Exception as e:
            self.logger.error(f"Stop error: {e}")
            return False

    def _cleanup(self) -> None:
        """Clean up resources"""
        with self._lock:
            if self._serial:
                try:
                    self._serial.close()
                except:
                    pass
                self._serial = None

            while not self._write_queue.empty():
                try:
                    self._write_queue.get_nowait()
                except:
                    pass

        self._running = False
        self.connection_state.emit(False)

    def _handle_error(self, message: str) -> None:
        """Handle errors uniformly"""
        self.logger.error(message)
        self.error_occurred.emit(message)
        self.data_received.emit("CONNECTION_TERMINATED")
        self.stop()

###############################################################################
# GUI

class GUI_ParametersWindow(QMainWindow):
    def __init__(self, settings, logger: logging.Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger

        self.logger.debug("Creating the parameters window")
        self.setWindowTitle("Parameters")
        self.resize(640, 480)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.create_gui()

    def create_collection_widget(self, value, key):
        """Create widget for list/tuple types"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for i, item in enumerate(value):
            edit = QLineEdit(str(item))
            edit.setFixedWidth(50)
            edit.textChanged.connect(
                lambda text, k=key, idx=i: self.update_collection_item(k, idx, text))
            layout.addWidget(edit)
        
        layout.addStretch()
        return container

    def create_gui(self):
        """Create the GUI with categorized settings"""
        self.logger.debug("Creating the GUI")
        
        categories = {}
        for key, value in self.settings.__dict__.items():
            if key.startswith(("__", "app_")):
                continue
            category = key.split("_")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append((key, value))

        for category, settings in categories.items():
            scroll = QScrollArea()
            container = QWidget()
            scroll.setWidget(container)
            scroll.setWidgetResizable(True)
            
            grid_layout = QGridLayout(container)
            grid_layout.setVerticalSpacing(2)
            grid_layout.setHorizontalSpacing(10)
            grid_layout.setContentsMargins(5, 5, 5, 5)

            for row, (key, value) in enumerate(settings):
                label = QLabel(key)
                label.setMinimumWidth(150)
                grid_layout.addWidget(label, row, 0)

                if isinstance(value, bool):
                    widget = QCheckBox()
                    widget.setChecked(value)
                    widget.stateChanged.connect(
                        lambda state, k=key: self.update_setting(k, state))
                elif isinstance(value, (tuple, list)):
                    widget = self.create_collection_widget(value, key)
                elif isinstance(value, (int, float)):
                    widget = QLineEdit(str(value))
                    widget.textChanged.connect(
                        lambda text, k=key: self.update_setting(k, text))
                elif isinstance(value, (str, pathl.Path)):
                    widget = QLineEdit(str(value))
                    widget.textChanged.connect(
                        lambda text, k=key: self.update_setting(k, text))
                else:
                    continue

                grid_layout.addWidget(widget, row, 1)

            grid_layout.setRowStretch(grid_layout.rowCount(), 1)
            grid_layout.setColumnStretch(1, 1)
            
            self.tab_widget.addTab(scroll, category.capitalize())

    def update_collection_item(self, key, index, value):
        """Update individual item in collection setting"""
        try:
            current_value = getattr(self.settings, key)
            new_value = list(current_value)
            
            # Convert value to correct type based on existing item
            orig_type = type(current_value[index])
            if orig_type == int:
                value = int(value)
            elif orig_type == float:
                value = float(value)
            
            new_value[index] = value
            
            # Convert back to original type (tuple if needed)
            if isinstance(current_value, tuple):
                new_value = tuple(new_value)
                
            setattr(self.settings, key, new_value)
            self.logger.debug(f"Updated collection {key}[{index}] to {value}")
        except Exception as e:
            self.logger.error(f"Error updating collection {key}[{index}]: {e}")

    def update_setting(self, key, value):
        """Update a setting."""
        self.logger.debug(f"Updating setting {key} to {value}")
        try:
            setting_type = type(getattr(self.settings, key))
            
            if setting_type == bool:
                value = bool(int(value))
            elif setting_type == int:
                value = int(value)
            elif setting_type == float:
                value = float(value)
            elif setting_type == pathl.Path:
                value = pathl.Path(value)
            elif setting_type in (tuple, list):
                return  # Handled by update_collection_item
            else:
                value = str(value)

            setattr(self.settings, key, value)
        except Exception as e:
            self.logger.error(f"Error updating setting {key} to {value}: {e}")

class GUI_AudioWindow(QMainWindow):
    """
    Audio window of the application.
    """
    def __init__(self, settings, logger: logging.Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger

        # Create the audio window
        self.logger.debug("Creating the audio window")
        self.setWindowTitle("Audio")
        self.resize(640, 480)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.base_layout = QVBoxLayout()
        self.central_widget.setLayout(self.base_layout)

        # Create the GUI
        self.create_gui()

    def create_gui(self):
        """
        Create the GUI.
        """
        self.logger.debug("Creating the GUI")

        # Create the buttons
        self.button_record = QPushButton("Record")
        self.button_record.clicked.connect(self.record_audio)
        self.button_play = QPushButton("Play")
        self.button_play.clicked.connect(self.play_audio)
        self.button_save = QPushButton("Save")
        self.button_save.clicked.connect(self.save_audio)
        self.button_clear = QPushButton("Clear")
        self.button_clear.clicked.connect(self.clear_audio)
        self.base_layout.addWidget(self.button_record)
        self.base_layout.addWidget(self.button_play)
        self.base_layout.addWidget(self.button_save)
        self.base_layout.addWidget(self.button_clear)

        # Create the audio console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.base_layout.addWidget(self.console)

    def record_audio(self):
        """
        Record audio.
        """
        self.logger.debug("Recording audio")

    def play_audio(self):
        """
        Play audio.
        """
        self.logger.debug("Playing audio")

    def save_audio(self):
        """
        Save audio.
        """
        self.logger.debug("Saving audio")

    def clear_audio(self):
        """
        Clear audio.
        """
        self.logger.debug("Clearing audio")

class GUI_MelWindow(QMainWindow):
    """
    Mel spectrogram window of the application.
    """
    def __init__(self, settings, logger: logging.Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger

        # Create the mel spectrogram window
        self.logger.debug("Creating the mel spectrogram window")
        self.setWindowTitle("Mel Spectrogram")
        self.resize(640, 480)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.base_layout = QVBoxLayout()
        self.central_widget.setLayout(self.base_layout)

        # Create the GUI
        self.create_gui()

    def create_gui(self):
        """
        Create the GUI.
        """
        self.logger.debug("Creating the GUI")

        # Create the buttons
        self.button_record = QPushButton("Record")
        self.button_record.clicked.connect(self.record_mel)
        self.button_save = QPushButton("Save")
        self.button_save.clicked.connect(self.save_mel)
        self.button_clear = QPushButton("Clear")
        self.button_clear.clicked.connect(self.clear_mel)
        self.base_layout.addWidget(self.button_record)
        self.base_layout.addWidget(self.button_save)
        self.base_layout.addWidget(self.button_clear)

        # Create the mel console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.base_layout.addWidget(self.console)

    def record_mel(self):
        """
        Record mel spectrogram.
        """
        self.logger.debug("Recording mel spectrogram")

    def save_mel(self):
        """
        Save mel spectrogram.
        """
        self.logger.debug("Saving mel spectrogram")

    def clear_mel(self):
        """
        Clear mel spectrogram.
        """
        self.logger.debug("Clearing mel spectrogram")

class GUI_MainWindow(QMainWindow):
    """
    Main window of the application.
    """
    def __init__(self, settings, logger: logging.Logger):
        super().__init__()
        self.settings = settings
        self.logger = logger

        # Create the main window
        self.logger.debug("Creating the main window")
        self.setWindowTitle(f"{self.settings.app_name} - {self.settings.app_version}")
        self.resize(*self.settings.gui_default_window_size)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.base_layout = QVBoxLayout()
        self.central_widget.setLayout(self.base_layout)

        # Create the GUI
        self.create_gui()

        # Create the serial reader thread
        self.serial_reader = SerialReader(self.settings, self.logger)
        self.serial_reader.error_occurred.connect(self._handle_connection_error)
        self.serial_reader.connection_state.connect(self._handle_connection_state)

        # Add the console handler (GUI)
        handler = QTextEditLogger(self.console, self.settings)
        self.logger.addHandler(handler)

        # Test logging
        # test_logging(self.logger)

    def create_gui(self):
        """
        Create the GUI.
        """
        self.logger.debug("Creating the GUI")

        # Create the menu
        self.create_menu_bar()

        # Create the Title
        self.title = QLabel(f"{self.settings.app_name} - v{self.settings.app_version}")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold")
        self.base_layout.addWidget(self.title)
        self.autors = QLabel(f"Developed by {self.settings.app_author}")
        self.autors.setStyleSheet("font-size: 10px")
        self.base_layout.addWidget(self.autors)

        # Create grid layout for controls
        control_grid = QGridLayout()
        control_grid.setVerticalSpacing(2)
        control_grid.setHorizontalSpacing(10)
        control_grid.setContentsMargins(5, 5, 5, 5)
        self.base_layout.addLayout(control_grid)

        # >> Add Serial Port controls <<
        row = 0
        # Label
        self.serial_port_label = QLabel("Serial Port:")
        self.serial_port_label.setMinimumWidth(130)
        control_grid.addWidget(self.serial_port_label, row, 0)

        # Combo box
        self.serial_port_combo = QComboBox()
        self.serial_port_combo.currentIndexChanged.connect(self.update_serial_port_settings)
        control_grid.addWidget(self.serial_port_combo, row, 1)

        # Refresh button
        self.serial_port_refresh = QPushButton("Refresh")
        self.serial_port_refresh.setFixedWidth(100)
        self.serial_port_refresh.clicked.connect(self.update_serial_port)
        control_grid.addWidget(self.serial_port_refresh, row, 2)

        # Set column stretching
        control_grid.setColumnStretch(1, 1)

        # Initialize combo box
        self.serial_port_combo.addItems(["-- No serial port --"])
        self.update_serial_port()
        if self.serial_port_combo.count() > 1:
            self.serial_port_combo.setCurrentIndex(1)

        # >> Serial connect <<
        # Connect button
        self.serial_connect = QPushButton("Connect")
        self.serial_connect.clicked.connect(self.toggle_serial)        
        self.base_layout.addWidget(self.serial_connect)
        # Status Text
        self.serial_status = QLabel("Status: Disconnected")
        self.serial_status.setStyleSheet("color: red")
        self.base_layout.addWidget(self.serial_status)

        # Add console at the bottom
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(200)
        self.base_layout.addWidget(self.console)

        # UART write text box
        self.grid_uart_write = QGridLayout()
        self.grid_uart_write.setVerticalSpacing(2)
        self.grid_uart_write.setHorizontalSpacing(10)
        self.grid_uart_write.setContentsMargins(5, 5, 5, 5)
        self.base_layout.addLayout(self.grid_uart_write)
        self.label_uart_write = QLabel("UART Write:")
        self.label_uart_write.setMinimumWidth(130)
        self.grid_uart_write.addWidget(self.label_uart_write, 0, 0)
        self.text_uart_write = QLineEdit()
        self.grid_uart_write.addWidget(self.text_uart_write, 0, 1)
        self.button_uart_write = QPushButton("Send")
        self.button_uart_write.clicked.connect(self.send_uart)
        self.grid_uart_write.addWidget(self.button_uart_write, 0, 2)

        # Add a clear button
        self.clear_button = QPushButton("Clear Console")
        self.clear_button.clicked.connect(self.console.clear)
        self.base_layout.addWidget(self.clear_button)

    def create_menu_bar(self):
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("&File")
        self.menu_file_exit = self.menu_file.addAction("&Exit")
        self.menu_file_exit.triggered.connect(self.close)
        self.menu_parameters = self.menu.addMenu("&Parameters")
        self.menu_parameters_edit = self.menu_parameters.addAction("&Edit Parameters")
        self.menu_parameters_edit.triggered.connect(self.open_parameters_window)
        self.menu_view = self.menu.addMenu("&View")
        self.menu_view_audio = self.menu_view.addAction("&Audio")
        self.menu_view_audio.triggered.connect(self.open_audio_window)
        self.menu_view_mel = self.menu_view.addAction("&Mel Spectrogram")
        self.menu_view_mel.triggered.connect(self.open_mel_window)
        self.menu_help = self.menu.addMenu("&Help")
        self.menu_help_about = self.menu_help.addAction("&About")
        self.menu_help_about.triggered.connect(self.open_about)

    def open_parameters_window(self):
        """
        Open the parameters window.
        """
        self.logger.debug("Opening the parameters window")
        self.parameters_window = GUI_ParametersWindow(self.settings, self.logger)
        self.parameters_window.show()

    def open_audio_window(self):
        """
        Open the audio window.
        """
        self.logger.debug("Opening the audio window")
        self.audio_window = GUI_AudioWindow(self.settings, self.logger)
        self.audio_window.show()

    def open_mel_window(self):
        """
        Open the mel spectrogram window.
        """
        self.logger.debug("Opening the mel spectrogram window")
        self.mel_window = GUI_MelWindow(self.settings, self.logger)
        self.mel_window.show()

    def open_about(self):
        """
        Show the about message.
        """
        self.logger.debug("Showing the about message")
        about_text = f"{self.settings.app_name} - {self.settings.app_version}\n\n{self.settings.app_description}\n\nDeveloped by {self.settings.app_author}"
        QMessageBox.about(self, "About", about_text)

    def update_serial_port_settings(self):
        """
        Update the serial port settings.
        """
        self.settings.serial_port = self.serial_port_combo.currentText()

    def update_serial_port(self):
        """
        Update the serial port.
        """
        self.logger.debug("Updating the serial port")
        old_port = self.serial_port_combo.currentText()
        self.serial_port_combo.clear()
        ports = ["-- No serial port --"] + [
            f"{port.device} - {port.description}" for port in list_ports.comports()
        ]
        self.serial_port_combo.addItems(ports)
        if old_port == "-- No serial port --" and len(ports) > 1:
            self.serial_port_combo.setCurrentIndex(1)
            self.update_serial_port_settings()
        elif old_port in ports:
            self.serial_port_combo.setCurrentText(old_port)
            self.update_serial_port_settings()
    
    def _handle_connection_error(self, error_message: str) -> None:
        """Handle unexpected serial connection errors"""
        self.logger.error(f"Serial connection error: {error_message}")
        self._update_ui_state(connected=False, error=True)
        QMessageBox.critical(self, "Connection Error", error_message)
        self.update_serial_port()

    def _handle_connection_state(self, connected: bool) -> None:
        """Handle connection state changes from serial reader"""
        if not connected and self.serial_reader.is_connected:
            # Unexpected disconnect
            self.logger.warning("Unexpected serial port disconnect")
            self._update_ui_state(connected=False, error=True)
            QMessageBox.warning(self, "Connection Lost", 
                            "Serial port disconnected unexpectedly")

    def toggle_serial(self) -> None:
        """Toggle the serial connection state between connected and disconnected."""
        try:
            if self.serial_reader.is_connected:
                # Disconnect sequence
                self.logger.debug("Initiating serial port disconnect")
                self._update_ui_state(connecting=True)
                
                if not self.serial_reader.stop():
                    raise RuntimeError("Failed to stop serial reader")
                    
                self._update_ui_state(connected=False)
                self.logger.good("Serial port disconnected successfully")
                
            else:
                # Connect sequence
                self.logger.debug("Initiating serial port connection")
                self._update_ui_state(connecting=True)
                
                if not self.serial_reader.try_start():
                    raise RuntimeError("Failed to start serial reader")
                    
                self._update_ui_state(connected=True)
                self.logger.debug("Serial port connected successfully")
                
        except Exception as e:
            self.logger.error(f"Serial toggle failed: {e}")
            self._update_ui_state(connected=False, error=True)
            QMessageBox.critical(self, "Error", f"Serial connection error: {e}")

    def _update_ui_state(self, connected: bool = False, 
                        connecting: bool = False, 
                        error: bool = False) -> None:
        """Update UI elements based on connection state."""
        try:
            # Update button state
            self.serial_connect.setEnabled(not connecting)
            self.serial_connect.setText("Disconnect" if connected else "Connect")
            
            # Update status indicator
            if connecting:
                status = "Status: Transitioning..."
                color = "color: orange"
            elif error:
                status = "Status: Error - Disconnected"
                color = "color: red; font-weight: bold"
            else:
                status = f"Status: {'Connected' if connected else 'Disconnected'}"
                color = f"color: {'green' if connected else 'red'}"
            
            self.serial_status.setText(status)
            self.serial_status.setStyleSheet(color)
            
            # Update other UI elements
            self.serial_port_combo.setEnabled(not connected)
            self.serial_port_refresh.setEnabled(not connected)
            
            # Update write UI elements
            self.text_uart_write.setEnabled(connected)
            self.button_uart_write.setEnabled(connected)
            
        except Exception as e:
            self.logger.error(f"Failed to update UI state: {e}")

    def send_uart(self):
        """
        Send UART data.
        """
        data = self.text_uart_write.text()
        self.logger.info(f"Sending UART data: {data}")
        self.text_uart_write.clear()

    def closeEvent(self, event):
        """
        Close the application.
        """
        self.logger.debug("Closing the application")
        event.accept()

###############################################################################
# Main

if __name__ == "__main__":
    # Settings
    settings = APP_Settings()

    # Logging
    logger = setup_logging(settings)

    # GUI
    app = QApplication(sys.argv)
    main_window = GUI_MainWindow(settings, logger)
    main_window.show()
    sys.exit(app.exec())