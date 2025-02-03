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
    QSpinBox,
    QTabWidget,
    QSpacerItem,
    QLineEdit,
    QGroupBox,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6 import QtGui, QtCore
from serial.tools import list_ports
from scipy import fft

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib

# Custom modules
import databaseUtils as dbu
import loggingUtils as logu
import serialUtils as seru

class GUIParamWindow(QMainWindow):
    """Parameters GUI window for the application"""

    def __init__(self, db: dbu.ContentDatabase, log: logu.ContentLogger):
        super().__init__()

        self.db = db
        self.log = log

        # Create the main window
        self.setWindowTitle(f"{self.db.get_item('_hidden', 'appname').value} - Parameters Window")
        self.setGeometry(100, 100, 800, 600)

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Create the UI
        self.create_ui()

    def create_ui(self):
        # Add title to the window
        self.title = QLabel(f"Parameters Window")
        self.title.setFont(QtGui.QFont("Arial", 20))
        self.main_layout.addWidget(self.title)

        # Create the tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create the tabs
        with self.db.lock:
            for category_name, category in self.db.db.items():
                if category_name[0] != "_":
                    self.create_tab(category_name, category)

    def create_tab(self, category_name: str, category: any):
        # Create the tab
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)
        self.tab_widget.addTab(tab, category_name)

        # Create the group boxes
        for item_name, item in category.items():
            if item_name[0] != "_":
                widget = item.gen_widget_full()
                if widget is not None:
                    tab_layout.addWidget(widget)

        # Add a stretch to the end (Push upwards)
        tab_layout.addStretch()

class GUIAudioWindow(QMainWindow):
    """Audio GUI window for the application"""

    def __init__(self, db: dbu.ContentDatabase, log: logu.ContentLogger, ser: seru.SerialController, base_data = None):
        super().__init__()

        self.db = db
        self.log = log
        self.ser = ser
        self.logger = log.logger

        self.audio_data = base_data

        self.ser.data_received_prefix.connect(self.prefix_message_handler)

        # Create the main window
        self.setWindowTitle(f"{self.db.get_item('_hidden', 'appname').value} - Audio Window")
        self.setGeometry(100, 100, 800, 600)

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Create the UI
        self.create_ui()

    def prefix_message_handler(self, prefix, message):
        if prefix == self.db.get_item("Audio Settings", "serial_prefix").value:
            self.audio_data = np.zeros(10240)
            # TODO : Change this to proper handling

    def create_ui(self):
        # Add title to the window
        self.title = QLabel(f"Audio Window")
        self.title.setFont(QtGui.QFont("Arial", 20))
        self.main_layout.addWidget(self.title)

        # Add a FPS counter
        self.fps_counter = QLabel("FPS: 0")
        self.main_layout.addWidget(self.fps_counter)
        self.current_time = time.time()

        # Create the 2 figures for the audio signal and FFT
        self.fig_audio = Figure(figsize=(8, 6))
        self.canvas_audio = FigureCanvasQTAgg(self.fig_audio)
        self.main_layout.addWidget(self.canvas_audio)

        self.fig_fft = Figure(figsize=(8, 6))
        self.canvas_fft = FigureCanvasQTAgg(self.fig_fft)
        self.main_layout.addWidget(self.canvas_fft)

        # Setup the layouts
        self.ax_audio = self.fig_audio.add_subplot(111)
        self.ax_fft = self.fig_fft.add_subplot(111)

        self.ax_audio.set_title("Audio Signal")
        self.ax_audio.set_xlabel("Time (s)")
        self.ax_audio.set_ylabel("Amplitude (%)")
        self.ax_audio.set_xlim(0, 1)
        self.ax_audio.set_ylim(-1, 1)
        self.ax_audio.grid(True)
        self.ax_audio.autoscale(enable=False, axis="both")
        
        self.ax_fft.set_title("FFT")
        self.ax_fft.set_xlabel("Frequency (Hz)")
        self.ax_fft.set_ylabel("Magnitude (dB)")
        self.ax_fft.set_xlim(-10500, 10500)
        self.ax_fft.set_ylim(-1, 100)
        self.ax_fft.grid(True)
        self.ax_fft.autoscale(enable=False, axis="both")

        # Add the signal to the plots
        self.line_audio, = self.ax_audio.plot([], [], animated=True)
        self.line_fft, = self.ax_fft.plot([], [], animated=True)

        # Make the plots slightly smaller
        self.fig_audio.tight_layout()
        self.fig_audio.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

        self.fig_fft.tight_layout()
        self.fig_fft.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

        # Set up animation using blit
        TARGET_FPS = self.db.get_item("Plot Settings", "framerate").value
        self.anim_audio = FuncAnimation(
            self.fig_audio,
            self._update_audio_plot,
            init_func=self._init_audio_plot,
            interval=1//TARGET_FPS*1000,
            blit=True,
            save_count=1
        )
        self.anim_fft = FuncAnimation(
            self.fig_fft,
            self._update_fft_plot,
            init_func=self._init_fft_plot,
            interval=1//TARGET_FPS*1000,
            blit=True,
            save_count=1
        )

        # TODO : Add the save buttons and the rest of the functionality

    def _init_audio_plot(self):
        """Initialize audio line for blitting."""
        self.line_audio.set_data([], [])
        return (self.line_audio,)

    def _init_fft_plot(self):
        """Initialize FFT line for blitting."""
        self.line_fft.set_data([], [])
        return (self.line_fft,)

    def _update_audio_plot(self, frame):
        """Update audio plot for animation."""
        # Update audio signal
        x = np.linspace(0, 1, len(self.audio_data))
        self.line_audio.set_data(x, self.audio_data)

        return (self.line_audio,)

    def _update_fft_plot(self, frame):
        """Update FFT plot for animation."""
        # Calculate FFT
        fft_data = np.abs(np.fft.fft(self.audio_data))
        fft_data = 20 * np.log10(fft_data + 1e-12)  # Avoid log(0)
        fft_data = np.fft.fftshift(fft_data)
        freqs = np.linspace(-10200, 10200, len(fft_data))
        self.line_fft.set_data(freqs, fft_data)

        # Update FPS
        current_time = time.time()
        fps = 1 / (current_time - self.current_time)
        self.current_time = current_time
        self.fps_counter.setText(f"FPS: {fps:.2f}")
        return (self.line_fft,)

class GUIMELWindow(QMainWindow):
    # nothing
    pass

class GUIMainWindow(QMainWindow):
    """Main GUI window for the application"""

    def __init__(self, db: dbu.ContentDatabase, log: logu.ContentLogger, ser: seru.SerialController):
        super().__init__()

        self.db = db
        self.log = log
        self.logger = log.logger
        self.ser = ser

        # Create the main window
        self.screen_resolution = self.screen().geometry()
        print(f"Screen resolution: {self.screen_resolution}")
        self.setWindowTitle(f"{self.db.get_item('_hidden', 'appname').value} - Main Window")
        self.setGeometry(100, 100, 800, 600)

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Create the menu bar
        self.create_menu_bar()

        # Create the UI
        self.create_ui()

        # Register the message handlers
        self.ser.data_received_normal.connect(self.normal_message_handler)
        self.ser.data_received_prefix.connect(self.prefix_message_handler)
        self.ser.error_occurred.connect(self.error_message_handler)
        self.ser.connection_state.connect(self.connection_status_handler)

    def create_menu_bar(self):
        # Create the menu bar
        self.menu_bar = self.menuBar()

        # Create the file menu
        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu_import = self.file_menu.addAction("Import Settings")
        self.file_menu_export = self.file_menu.addAction("Export Settings")
        self.file_menu.addSeparator()
        self.file_menu_exit = self.file_menu.addAction("Exit")

        # Create the windows menu
        self.windows_menu = self.menu_bar.addMenu("Windows")
        self.windows_menu_params = self.windows_menu.addAction("Parameters Window")
        self.windows_menu_audio = self.windows_menu.addAction("Audio Window")
        self.windows_menu_mel = self.windows_menu.addAction("MEL Window")

        # Create the help menu
        self.help_menu = self.menu_bar.addMenu("Help")
        self.help_menu_about = self.help_menu.addAction("About")

        # Connect actions
        self.file_menu_import.triggered.connect(self.import_settings)
        self.file_menu_export.triggered.connect(self.export_settings)
        self.file_menu_exit.triggered.connect(self.close)

        self.windows_menu_params.triggered.connect(self.open_params_window)
        self.windows_menu_audio.triggered.connect(lambda: self.open_audio_window(np.zeros(10240)))
        self.windows_menu_mel.triggered.connect(lambda: self.open_mel_window(np.zeros(10240))) # TODO : Change this to the MEL data

        self.help_menu_about.triggered.connect(self.show_about)

    def import_settings(self):
        # Get the file name
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Settings", pathl.Path(__file__).parent, "NPY Files (*.npy)")
        if file_name:
            self.logger.info(f"Importing settings from {file_name}")
            self.db.import_database(file_name)

    def export_settings(self):
        # Get the file name
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Settings", pathl.Path(__file__).parent, "NPY Files (*.npy)")
        if file_name:
            self.logger.info(f"Exporting settings to {file_name}")
            self.db.export_database(file_name)

    def open_params_window(self):
        self.logger.info("Opening the Parameters Window")
        self.params_window = GUIParamWindow(self.db, self.log)
        self.params_window.show()

    def open_audio_window(self, base_data = None):
        self.logger.info("Opening the Audio Window")
        self.audio_window = GUIAudioWindow(self.db, self.log, self.ser, base_data)
        self.audio_window.show()

    def open_mel_window(self, base_data = None):
        self.logger.info("Opening the MEL Window")
        self.mel_window = GUIMELWindow(self.db, self.log, self.ser, base_data)
        self.mel_window.show()

    def show_about(self):
        self.logger.info("Showing the About Dialog")
        texts = [
            f"{self.db.get_item('_hidden', 'appname').value} - v{self.db.get_item('_hidden', 'appversion').value}",
            f"Made by {self.db.get_item('_hidden', 'author').value}",
            f"{self.db.get_item('_hidden', 'app_description').value}",
        ]
        QMessageBox.about(self, "About", "\n".join(texts))

    def create_ui(self):
          # Add title to the window
        self.title = QLabel(f"{self.db.get_item('_hidden', 'appname').value} - v{self.db.get_item('_hidden', 'appversion').value}")
        self.title.setFont(QtGui.QFont("Arial", 24))
        self.author = QLabel(f"Made by {self.db.get_item('_hidden', 'author').value}")
        self.description = QLabel(f"{self.db.get_item('_hidden', 'app_description').value}")
        self.author.setFont(QtGui.QFont("Arial", 8))
        self.description.setFont(QtGui.QFont("Arial", 9))
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.author)
        self.main_layout.addWidget(self.description)

        # Add the serialport selection
        self.layout_serialport = QHBoxLayout()
        self.serialport_label = QLabel("Serial Port:")
        self.serialport_label.setFixedWidth(80)
        self.serialPortWidget = self.db.get_item("Serial Settings", "port").gen_widget_element()
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.setFixedWidth(100)
        self.refreshButton.clicked.connect(self.refresh_ports)
        self.layout_serialport.addWidget(self.serialport_label)
        self.layout_serialport.addWidget(self.serialPortWidget)
        self.layout_serialport.addWidget(self.refreshButton)
        self.main_layout.addLayout(self.layout_serialport)

        # Port status label
        self.port_status = QLabel("Port Status: Not Connected")
        self.main_layout.addWidget(self.port_status)
        self.port_status.setStyleSheet("color: red")

        # Add the Connect/Disonnect button
        self.connect_disconnect_button = QPushButton("Connect")
        self.connect_disconnect_button.clicked.connect(self.handle_connect_disconnect)
        self.main_layout.addWidget(self.connect_disconnect_button)

        # Add the console from the logging module
        self.console = self.log.gen_gui_console()
        self.main_layout.addWidget(self.console)

        # Add the write message
        self.layout_write = QHBoxLayout()
        self.write_label = QLabel("Write Message:")
        self.write_label.setFixedWidth(100)
        self.write_message = QLineEdit()
        self.write_message.setPlaceholderText("Enter message to be sent to the serial port")
        self.write_button = QPushButton("Write")
        self.write_button.setFixedWidth(100)
        self.write_button.clicked.connect(self.write_message_handler)
        self.layout_write.addWidget(self.write_label)
        self.layout_write.addWidget(self.write_message)
        self.layout_write.addWidget(self.write_button)
        self.main_layout.addLayout(self.layout_write)
        self.db.get_item("Serial Settings", "allowwrite").register_callback(self.write_box_state_callback)

        # Trigger the first callbacks : 
        self.refresh_ports()
        self.write_box_state_callback(self.db.get_item("Serial Settings", "allowwrite").value)

    def refresh_ports(self):
        comports = self.ser.available_ports() # Dictionary of comports
        old_value = self.db.get_item("Serial Settings", "port").value
        self.db.get_item("Serial Settings", "port").set_value((old_value[0], [f"{device} - {description}" for device, description in comports.items()] if len(comports) > 0 else ["-- No Ports Detected --"]))
    
    def write_box_state_callback(self, state):
        the_state = bool(state) # From the allowwrite checkbox
        if the_state:
            self.write_message.setEnabled(True)
            self.write_button.setEnabled(True)
            self.write_message.setPlaceholderText("Enter message to be sent to the serial port")
        else:
            self.write_message.setEnabled(False)
            self.write_button.setEnabled(False)
            self.write_message.setPlaceholderText("Sending messages is disabled in settings")

    def write_message_handler(self):
        if self.db.get_item("Serial Settings", "allowwrite").value:
            message = self.write_message.text()
            self.ser.write_message(message)
            self.write_message.clear()
        else:
            self.logger.error("Writing messages is disabled in settings")

    def handle_connect_disconnect(self):
        if self.ser.is_connected:
            self.ser.stop()
        else :
            port = self.db.get_item("Serial Settings", "port").value
            if len(port) == 0:
                self.logger.error("No port selected, please select a valid port")
                self.port_status.setText("Port Status: Invalid Port")
                self.port_status.setStyleSheet("color: orange")
                return
            port = port[1][port[0]].split(" - ")[0]
            baud = self.db.get_item("Serial Settings", "baud").value
            baud = int(baud[1][baud[0]])
            self.ser.try_start(port, baud)

    # Serial Handlers
    def connection_status_handler(self, status):    
        if status:
            self.connect_disconnect_button.setText("Disconnect")
            self.port_status.setText("Port Status: Connected")
            self.port_status.setStyleSheet("color: green")
        else:
            self.connect_disconnect_button.setText("Connect")
            self.port_status.setText("Port Status: Disconnected")
            self.port_status.setStyleSheet("color: red")

    def error_message_handler(self, message):
        #self.logger.error(message)
        pass

    def normal_message_handler(self, message):
        if message == "TERMINATE":
            return
        self.logger.info(f">>{message}")

    def prefix_message_handler(self, prefix, message):
        self.logger.info(f"Received {len(message)} bytes for prefix {prefix}")
        if prefix == "CFG:HEX:":
            self.logger.info(f"New configuration received: {message}")
        elif prefix == "SND:HEX:":
            self.logger.info(f"New audio data received of length {len(message)}")
            # Ill have to pass the message in the init of the window, so that it can be displayed
        elif prefix == "SND:MEL:":
            self.logger.info(f"New MEL data received of length {len(message)}")
        else:
            self.logger.warning(f"Unknown prefix {prefix}")

####################################################################################################
# Database Initialization
####################################################################################################

def database_init(db: dbu.ContentDatabase):
    # Add the Hidden group
    db.create_category("_hidden")
    db.add_item("_hidden", "appname", db.ConstantText("App Name", "UART Reader", "The name of the application"))
    db.add_item("_hidden", "appversion", db.ConstantText("App Version", "4.1", "The version of the application"))
    db.add_item("_hidden", "author", db.ConstantText("Author", "Groupe E 2024-2025", "The author of the application"))
    db.add_item("_hidden", "app_description", db.ConstantText("App Description", "This application reads data from a Serial port and displays it in a GUI, and handles certain prefixes.", "The description of the application"))
    
    # Folder Settings
    db.create_category("Folder Settings")
    base_path = pathl.Path(__file__).parent
    second_path = base_path.parent/"data"
    db.add_item("Folder Settings", "app path", db.Folder("App Path", base_path, "The path to the application"))
    db.add_item("Folder Settings", "log path", db.Folder("Log Path", base_path, "The path to the log file"))
    db.add_item("Folder Settings", "db path", db.Folder("Database Path", second_path/"db_saves", "The path to the database file"))
    db.add_item("Folder Settings", "audio path", db.Folder("Audio Path", second_path/"audio", "The path to the audio file"))
    db.add_item("Folder Settings", "mel path", db.Folder("MEL Path", second_path/"mel", "The path to the MEL file"))
    db.add_item("Folder Settings", "plot path", db.Folder("Plot Path", second_path/"plots", "The path to the plot file"))


    # Serial Settings
    db.create_category("Serial Settings")
    comports = list_ports.comports()
    db.add_item("Serial Settings", "port", db.ChoiceBox("Port", (0,[port.device for port in comports] if len(comports) > 0 else ["-- No Ports Detected --"]), "The port to use for the serial connection"))
    db.add_item("Serial Settings", "baud", db.ChoiceBox("Baud Rate", (0,["115200", "9600", "4800", "2400", "1200", "600", "300"]), "The baud rate to use for the serial connection"))
    db.add_item("Serial Settings", "freeze", db.Boolean("Freeze", False, "Freeze the serial connection"))
    db.add_item("Serial Settings", "freezebuffering", db.Boolean("Freeze Buffering", False, "To buffer or not the freezed data to avoid data loss, at the cost of possible memory overflow"))
    db.add_item("Serial Settings", "allowwrite", db.Boolean("Allow Write", False, "Allow sending messages through the serial port"))
    db.add_item("Serial Settings", "database_prefix", db.Text("Database Prefix", "CFG:HEX:", "The prefix to use to update the database from the connected device"))

    # Logging Settings
    db.create_category("Logging Settings")
    db.add_item("Logging Settings", "loglevel", db.ChoiceBox("Log Level", (1,["DEBUG", "TRACE", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]), "The level of logging to use"))
    db.add_item("Logging Settings", "logformat", db.ChoiceBox("Log Format", (0,["[%(asctime)s] %(levelname)-9s: %(message)s", "%(levelname)-9s: %(message)s", "%(message)s"]), "The format of the log messages"))
    db.add_item("Logging Settings", "logdatefmt", db.ChoiceBox("Log Date Format", (0,["%Y-%m-%d %H:%M:%S", "%H:%M:%S"]), "The format of the date in the log messages"))
    db.add_item("Logging Settings", "use_file", db.Boolean("Use File", True, "Use a file for logging"))
    db.add_item("Logging Settings", "file_name", db.Text("File Name", "uart_logs.log", "The name of the log file"))
    db.add_item("Logging Settings", "logbackupcount", db.Integer("Log Backup Count", 3, "The number of log files to keep"))
    db.add_item("Logging Settings", "logmaxsize", db.SuffixFloat("Log Max Size", (1e4, "B"), "The maximum size of the log file before it is rotated"))

    # Plot Settings
    db.create_category("Plot Settings")
    db.add_item("Plot Settings", "limit_framerate", db.Boolean("Limit Framerate", False, "Limit the framerate of the plots"))
    db.add_item("Plot Settings", "framerate", db.Integer("Framerate", 30, "The target framerate of the plots to avoid over-consumption of resources"))
    db.add_item("Plot Settings", "number_saves", db.RangeInt("Number Of Save Types", (2, 1, 3), "The number of different save types to use"))
    db.add_item("Plot Settings", "first_format", db.ChoiceBox("First Format", (0,["pdf", "png", "html" ,"jpg", "jpeg", "svg"]), "The format to save the plots in"))
    db.add_item("Plot Settings", "second_format", db.ChoiceBox("Second Format", (1,["pdf", "png", "html" ,"jpg", "jpeg", "svg"]), "The format to save the plots in"))
    db.add_item("Plot Settings", "third_format", db.ChoiceBox("Third Format", (2,["pdf", "png", "html" ,"jpg", "jpeg", "svg"]), "The format to save the plots in"))
    db.add_item("Plot Settings", "plot_prefix", db.Text("Plot Prefix", "plot", "The prefix to use for the plot files before adding the timestamp"))

    # Audio Settings
    db.create_category("Audio Settings")
    db.add_item("Audio Settings", "serial_prefix", db.Text("Serial Prefix", "SND:HEX:", "The prefix to use for the audio data serial communication"))
    db.add_item("Audio Settings", "nucleo_sample_rate", db.SuffixFloat("Nucleo Sample Rate", (10240, "Hz"), "The sample rate of the Nucleo board"))
    db.add_item("Audio Settings", "file_prefix", db.Text("File Prefix", "audio", "The prefix to use for the audio files before adding the timestamp"))
    db.add_item("Audio Settings", "audio_format", db.ChoiceBox("Audio Format", (0,["wav", "flac", "ogg", "mp3"]), "The format to save the audio files in"))
    db.add_item("Audio Settings", "file_frequency", db.SuffixFloat("File Frequency", (44100, "Hz"), "The frequency to save the audio files in"))
    db.add_item("Audio Settings", "file_channels", db.Integer("File Channels", 1, "The number of channels to save the audio files in"))
    db.add_item("Audio Settings", "auto_save", db.Boolean("Auto Save", False, "Automatically save the audio files"))
    db.add_item("Audio Settings", "audio_freeze", db.Boolean("Audio Freeze", False, "Freeze the audio data"))
    db.add_item("Audio Settings", "save_data_raw", db.Boolean("Save Data Raw", False, "Save the raw data as well as the audio data"))
    db.add_item("Audio Settings", "save_data_plot", db.Boolean("Save Data Plot", False, "Save the data as a plot as well as the audio data"))
    db.add_item("Audio Settings", "raw_file_type", db.ChoiceBox("Raw File Type", (0,["npy", "csv", "txt"]), "The format to save the raw data in"))

    # MEL Settings
    db.create_category("MEL Settings")
    db.add_item("MEL Settings", "serial_prefix", db.Text("Serial Prefix", "SND:MEL:", "The prefix to use for the MEL data serial communication"))
    db.add_item("MEL Settings", "file_prefix", db.Text("File Prefix", "mel", "The prefix to use for the MEL files before adding the timestamp"))
    # TODO: Add more MEL settings
    db.add_item("MEL Settings", "auto_save", db.Boolean("Auto Save", False, "Automatically save the MEL files"))
    db.add_item("MEL Settings", "mel_freeze", db.Boolean("MEL Freeze", False, "Freeze the MEL data"))
    db.add_item("MEL Settings", "save_data_raw", db.Boolean("Save Data Raw", False, "Save the raw data as well as the MEL data"))
    db.add_item("MEL Settings", "save_data_plot", db.Boolean("Save Data Plot", False, "Save the data as a plot as well as the MEL data"))
    db.add_item("MEL Settings", "raw_file_type", db.ChoiceBox("Raw File Type", (0,["npy", "csv", "txt"]), "The format to save the raw data in"))

    # Classifier Settings
    db.create_category("Classifier Settings")
    db.add_item("Classifier Settings", "model_path", db.File("Model Path", base_path.parent/"models" / "model.pkl", "The path to the model file"))
    # TODO: Add more classifier settings

def connect_db_to_log(db: dbu.ContentDatabase, log: logu.ContentLogger):
    # Change level
    def change_level(value):
        log.change_level(value[1][value[0]])
    change_level(db.get_item("Logging Settings", "loglevel").value)
    db.get_item("Logging Settings", "loglevel").register_callback(change_level)

    # Change formats
    def change_format(value):
        log.change_formatter(value[1][value[0]])
    change_format(db.get_item("Logging Settings", "logformat").value)
    db.get_item("Logging Settings", "logformat").register_callback(change_format)

    # Change date format
    def change_date_format(value):
        log.change_formatter(None, value[1][value[0]])
    change_date_format(db.get_item("Logging Settings", "logdatefmt").value)
    db.get_item("Logging Settings", "logdatefmt").register_callback(change_date_format)

    # Change file
    def change_file(value):
        log.change_file_path(str(value))
    change_file(db.get_item("Logging Settings", "file_name").value)
    db.get_item("Logging Settings", "file_name").register_callback(change_file)

    # Toggle file logging TODO

def connect_db_to_ser(db: dbu.ContentDatabase, ser: seru.SerialController):
    # Change freeze and buffering
    def change_freeze(value):
        ser.set_freeze(value, db.get_item("Serial Settings", "freezebuffering").value)
    change_freeze(db.get_item("Serial Settings", "freeze").value)
    db.get_item("Serial Settings", "freeze").register_callback(change_freeze)

    # Change freeze and buffering
    def change_buffering(value):
        ser.set_freeze(db.get_item("Serial Settings", "freeze").value, value)
    change_buffering(db.get_item("Serial Settings", "freezebuffering").value)
    db.get_item("Serial Settings", "freezebuffering").register_callback(change_buffering)

    # Change write allowed
    def change_write(value):
        ser.set_write_allow(value)
    change_write(db.get_item("Serial Settings", "allowwrite").value)
    db.get_item("Serial Settings", "allowwrite").register_callback(change_write)

    prefixes = [
        db.get_item("Audio Settings", "serial_prefix"),
        db.get_item("MEL Settings", "serial_prefix"),
        db.get_item("Serial Settings", "database_prefix")
    ]
    def change_prefixes(value):
        ser.unregister_all_prefixes()
        for prefix in prefixes:
            ser.register_prefix(prefix.value)
    change_prefixes(None)
    for prefix in prefixes:
        prefix.register_callback(change_prefixes)

####################################################################################################
# Main execution
####################################################################################################

@click.command()
@click.option("--cli", is_flag=True, help="Run the command line interface instead of the GUI")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--port", default=None, help="Serial port to use")
@click.option("--baud", default=115200, help="Baud rate to use")
@click.option("--log", default=pathl.Path(__file__).parent/"uart_logs.log", help="Log file to write to")
def main(cli: bool, debug: bool, port: Optional[str], baud: int, log: str):
    # Create the main application
    app = QApplication(sys.argv)

    # Set plotting style to blit with an option, and fast
    plt.style.use("fast")
    matplotlib.use("Qt5Agg")

    # Create the logger
    logelem = logu.ContentLogger(__name__, "uart_logs.log", True)

    # Create the database
    db = dbu.ContentDatabase(database_init, logelem.logger, False)

    # Create the serial controller
    ser = seru.SerialController(logelem.logger)

    # Create the main window
    main_window = GUIMainWindow(db, logelem, ser)
    main_window.show()

    # Connect the database to the logger
    connect_db_to_log(db, logelem)

    # Connect the database to the serial controller
    connect_db_to_ser(db, ser)

    # Execute the application
    sys.exit(app.exec())

####################################################################################################
# Main Entry Point
if __name__ == "__main__":
    main()

