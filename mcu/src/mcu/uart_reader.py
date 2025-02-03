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
        self.app_name = "UART Reader"
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
        self.gui_default_window_size = (1280, 720)

        # Plotting settings
        self.plot_name_prefix = "plot"
        self.plot_name_postfix_timestamp = True
        self.plot_save_types = ["pdf", "png"]
        self.plot_save_all_types = True
        self.plot_save_folder_base = self.app_folder / "plots"

        # Serial settings
        self.serial_port = None
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
        self.audio_file_types = ["wav", "ogg", "mp3", "flac"]
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
        self.menu_help_about.triggered.connect(self.about)


        # Create the serial console (temporary ui)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.base_layout.addWidget(self.console)

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

    def about(self):
        """
        Show the about message.
        """
        self.logger.debug("Showing the about message")
        about_text = f"{self.settings.app_name} - {self.settings.app_version}\n\n{self.settings.app_description}\n\nDeveloped by {self.settings.app_author}"
        QMessageBox.about(self, "About", about_text)

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