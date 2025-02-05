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
from threading import Thread
import pickle

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
from matplotlib.patches import Rectangle
import matplotlib

import sklearn

# Custom modules
import databaseV2_for_V4 as dbu
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

        self.audio_data = base_data if base_data is not None and type(base_data) == np.ndarray else np.zeros(10240)

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
            interval=1/TARGET_FPS*1000,
            blit=True,
            save_count=1
        )
        self.anim_fft = FuncAnimation(
            self.fig_fft,
            self._update_fft_plot,
            init_func=self._init_fft_plot,
            interval=1/TARGET_FPS*1000,
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
        fps = 1 / max((current_time - self.current_time), 1e-16)
        self.current_time = current_time
        self.fps_counter.setText(f"FPS: {fps:.2f}")
        return (self.line_fft,)

class GUIMELWindow(QMainWindow):
    """MEL GUI window for the application and the classifier"""

    def __init__(self, db: dbu.ContentDatabase, log: logu.ContentLogger, ser: seru.SerialController, base_data = None):
        super().__init__()

        self.db = db
        self.log = log
        self.ser = ser
        self.logger = log.logger

        self.current_mel_length = self.db.get_item("MEL Settings", "mel_length").value
        self.current_mel_number = self.db.get_item("MEL Settings", "mel_number").value
        self.current_feature_length = self.current_mel_length * self.current_mel_number
        
        # Load the current model
        self.current_model_path = self.db.get_item("Classifier Settings", "model_path").value
        # Structure of the model :
        #  {"model": sklearn.BaseEstimator}
        try:
            self.current_model_dict = pickle.load(open(self.current_model_path, "rb"))
        except Exception as e:
            self.current_model_dict = {}
            self.logger.error(f"Error loading the model : {e}")
        if type(self.current_model_dict) != dict:
            self.current_model = None
            self.current_model_dict = {}
            self.logger.error(f"Error loading the model : Not a dictionary")

        self.current_model: Optional[sklearn.base.BaseEstimator] = self.current_model_dict.get("model", None)

        # Check if the model is loaded
        if self.current_model is None:
            self.logger.error("No model loaded, please load a model in the settings")
            self.current_model = None
        else:
            self.logger.info(f"Model loaded from {self.current_model_path}")

        # Verify the model parameters
        if self.current_model is not None:
            if self.current_model_dict["mel_len"] != self.current_mel_length or self.current_model_dict["mel_num"] != self.current_mel_number:
                self.logger.error(f"Model parameters do not match the current MEL parameters : {self.current_model_dict['mel_len']} != {self.current_mel_length} or {self.current_model_dict['mel_num']} != {self.current_mel_number}")
                self.current_model = None
            if "classes" not in self.current_model_dict:
                self.logger.error(f"Model does not have specified classes")
                self.current_model = None

        

        self.num_classes = len(self.current_model_dict["classes"]) if self.current_model is not None else 10

        # Create the data : list[dict<"data": np.ndarray, "class_proba": np.ndarray]
        self.historic_data = [{"data": np.zeros(self.current_feature_length), "class_proba": np.zeros(self.num_classes)} for _ in range(10)]
        if base_data is not None and type(base_data) == np.ndarray:
            self.add_data(base_data)

        self.ser.data_received_prefix.connect(self.prefix_message_handler)

        # Create the main window
        self.setWindowTitle(f"{self.db.get_item('_hidden', 'appname').value} - MEL Window")
        self.setGeometry(100, 100, 800, 600)

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Add demo box for data spawning and testing
        if True:
            self.demo_box = QGroupBox("Test Box")
            self.demo_box.setCheckable(True)
            self.demo_box.setChecked(True)
            self.demo_box_layout = QVBoxLayout()
            self.demo_box.setLayout(self.demo_box_layout)
            self.demo_box.toggled.connect(lambda state: self.demo_box.setFixedHeight(15) if not state else self.demo_box.setFixedHeight(100))
            self.main_layout.addWidget(self.demo_box)

            self.demo_super_spawn = QPushButton("Spawn Mel Data")
            self.demo_super_spawn.clicked.connect(lambda: self.add_data(np.random.rand(self.current_feature_length)))
            self.demo_box_layout.addWidget(self.demo_super_spawn)

            self.demo_super_spawn = QPushButton("Spawn Mel and Class Data")
            self.demo_super_spawn.clicked.connect(lambda: self.add_data(np.random.rand(self.current_feature_length)))
            self.demo_super_spawn.clicked.connect(
                lambda: self.historic_data[0].update({
                    "class_proba": np.random.rand(self.num_classes) if self.historic_data[0]["class_proba"].sum() == 0 else self.historic_data[0]["class_proba"]
                    }))
            self.demo_box_layout.addWidget(self.demo_super_spawn)

        # Create the UI
        self.create_ui()

    def add_data(self, data):
        if not self.db.get_item("MEL Settings", "mel_freeze").value:
            max_history = self.db.get_item("MEL Settings", "max_history_length").value
            self.historic_data = [{"data": data, "class_proba": np.zeros(self.num_classes)}] + self.historic_data[:-1]
            if len(self.historic_data) > max_history:
                self.historic_data = self.historic_data[:max_history]
            elif len(self.historic_data) < max_history:
                self.historic_data = self.historic_data + [{"data": np.zeros(self.current_feature_length), "class_proba": np.zeros(self.num_classes)} for _ in range(max_history-len(self.historic_data))]
            
        # Classify the data
        if self.current_model is not None:
            # Take the lastest data
            data = self.historic_data[0]["data"]
            # Classify the data
            self.current_model: Optional[sklearn.base.BaseEstimator]
            class_proba = self.current_model.predict_proba(data.reshape(1, -1))
            self.historic_data[0].update({"class_proba": class_proba[0]})

    def prefix_message_handler(self, prefix, message):
        if prefix == self.db.get_item("MEL Settings", "serial_prefix").value:
            array_hex = bytes.fromhex(message)
            mel_vec = np.frombuffer(array_hex, dtype=np.dtype(np.uint16).newbyteorder("<"))
            if len(mel_vec) > self.current_feature_length:
                mel_vec = mel_vec[:-12] # TODO : Fix this properly (12 is the CBC mac)
            self.add_data(mel_vec)

    def create_ui(self):
        # Add title to the window
        self.title = QLabel(f"MEL Window")
        self.title.setFont(QtGui.QFont("Arial", 20))
        self.main_layout.addWidget(self.title)

        # Add a FPS counter
        self.fps_counter = QLabel("FPS: 0")
        self.main_layout.addWidget(self.fps_counter)
        self.current_time = time.time()

        # Add the MEL graph
        self.fig_mel = Figure(figsize=(8, 6))
        self.canvas_mel = FigureCanvasQTAgg(self.fig_mel)
        self.main_layout.addWidget(self.canvas_mel)
        self.fig_mel.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
        self.fig_mel.tight_layout(pad=0.5)

        # Add the classifier graphs next to each other
        self.classifier_layout = QHBoxLayout()
        self.fig_classifier = Figure(figsize=(6, 6))
        self.canvas_classifier = FigureCanvasQTAgg(self.fig_classifier)
        self.classifier_layout.addWidget(self.canvas_classifier)

        self.fig_class_history = Figure(figsize=(8, 6))
        self.canvas_class_history = FigureCanvasQTAgg(self.fig_class_history)
        self.classifier_layout.addWidget(self.canvas_class_history)
        self.main_layout.addLayout(self.classifier_layout)

        # Setup the graphs
        self.mel_ax = self.fig_mel.add_subplot(111)
        self.class_ax = self.fig_classifier.add_subplot(111)
        self.hist_ax = self.fig_class_history.add_subplot(111)

        # Make a rectangle for the mel plot
        self.mel_rect = Rectangle((-1.125+0.5, -0.025), 1.05, 1.05, linewidth=1, edgecolor='red', facecolor='none')

        self.mel_pcolors = []
        self.setup_mel_plots()

        self.db.get_item("MEL Settings", "max_history_length").register_callback(self.setup_mel_plots)

        # Setup the graph for the classifier
        self.class_ax.set_title("Classifier Probabilities")
        self.class_ax.set_xlabel("Classes")
        self.class_ax.set_ylabel("Probability")
        self.class_ax.set_xlim(-0.5, 9.5)
        self.class_ax.set_ylim(-0.05, 1.05)
        self.class_ax.autoscale(enable=False, axis="both")

        self.classes = self.current_model_dict.get("classes", [f"Class {i}" for i in range(self.num_classes)])
        self.class_histogram = self.class_ax.hist(
            self.classes,
            bins=self.num_classes,
            weights=np.zeros(self.num_classes),
            align='mid',
            rwidth=0.5,
            color='blue',
        )

        self.hist_ax.set_title("Classifier History")
        self.hist_ax.set_xlabel("Time Frames")
        self.hist_ax.set_ylabel("Probability")
        self.hist_ax.set_xlim(-9, 0)
        self.hist_ax.set_ylim(-0.05, 1.45)
        self.hist_ax.autoscale(enable=False, axis="both")

        self.hist_lines = []
        for i in range(len(self.classes)):
            line, = self.hist_ax.plot([], [], animated=True, label=self.classes[i])
            self.hist_lines.append(line)

        # Place a external legend
        self.hist_ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        self.fig_class_history.subplots_adjust(left=0.15, right=0.75, top=0.9, bottom=0.2)

        # Add the animation
        TARGET_FPS = self.db.get_item("Plot Settings", "framerate").value
        self.anim_mel = FuncAnimation(
            self.fig_mel,
            self._update_mel_plot,
            init_func=self._init_mel_plot,
            interval=1/TARGET_FPS*1000,
            blit=True,
            save_count=1
        )

        self.anim_class = FuncAnimation(
            self.fig_classifier,
            self._update_class_plot,
            init_func=self._init_class_plot,
            interval=1/TARGET_FPS*1000,
            blit=True,
            save_count=1
        )

        self.anim_hist_class = FuncAnimation(
            self.fig_class_history,
            self._update_hist_class_plot,
            init_func=self._init_hist_class_plot,
            interval=1/TARGET_FPS*1000,
            blit=True,
            save_count=1
        )


    def setup_mel_plots(self, number_of_bins=10):
        self.mel_pcolors = []
        self.mel_ax.clear()
        self.mel_ax.set_title("MEL Spectrogram")
        self.mel_ax.set_xlabel("Time Frames")
        self.mel_ax.set_ylabel("Mel Frequency Bins")
        self.mel_ax.set_xlim(-number_of_bins*1.1 + 0.4, 0.1 + 0.5)
        self.mel_ax.set_ylim(-0.05, 1.05)
        self.mel_ax.autoscale(enable=False, axis="both")
        self.mel_ax.set_xticks(np.arange(-number_of_bins, 1, 1))

        for i in range(number_of_bins):
            offset = -1.1
            X, Y = np.meshgrid(np.linspace(0, 1, self.current_mel_number), np.linspace(0, 1, self.current_mel_length))
            image = self.mel_ax.pcolormesh(
                X + i*offset - 1.1 + 0.5, Y, np.zeros((self.current_mel_length, self.current_mel_number)),
                vmin=0,
                vmax=(2**16),
                cmap='viridis',
                shading='auto',  # Avoid gridlines
            )
            self.mel_pcolors.append(image)

        self.mel_ax.add_patch(self.mel_rect)

    def _init_mel_plot(self):
        """Initialize mel plot for blitting."""
        for image in self.mel_pcolors:
            image.set_array(np.zeros(self.current_feature_length).ravel())
        return self.mel_pcolors + [self.mel_rect]

    def _update_mel_plot(self, frame):
        """Update mel plot for animation."""
        for i, image in enumerate(self.mel_pcolors):
            if i < len(self.historic_data):
                data:np.ndarray = self.historic_data[i]["data"]
            else:
                data = np.zeros(self.current_feature_length)
            raveled_data = data.reshape(self.current_mel_length, self.current_mel_number).T.ravel()
            image.set_array(raveled_data)

        # FPS counter
        current_time = time.time()
        fps = 1 / max((current_time - self.current_time), 1e-16)
        self.current_time = current_time
        self.fps_counter.setText(f"FPS: {fps:.2f}")

        return self.mel_pcolors + [self.mel_rect]     

    def _init_class_plot(self):
        """Initialize class plot for blitting."""
        self.class_histogram = self.class_ax.hist(self.classes, bins=self.num_classes, weights=np.zeros(self.num_classes), align='mid', rwidth=0.5, color='blue', edgecolor='black')
        # Make the class titles vertical
        self.class_ax.set_xticklabels(self.classes, rotation=45)
        # Make the figure slightly smaller in height to compensate for the vertical labels
        self.fig_classifier.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)

        return (self.class_histogram[2][0],)
    
    def _update_class_plot(self, frame):
        """Update class plot for animation."""
        # Update class histogram
        if len(self.historic_data) > 0:
            class_proba = self.historic_data[0]["class_proba"]
        else:
            class_proba = np.zeros(self.num_classes)
        
        # Update the histogram
        for rect, h in zip(self.class_histogram[2], class_proba):
            rect.set_height(h)
        
        # Make red and add text to the highest bar
        max_class = np.argmax(class_proba)
        for i, rect in enumerate(self.class_histogram[2]):
            if i == max_class:
                rect.set_color('red')
            else:
                rect.set_color('blue')

        return self.class_histogram[2]

    def _init_hist_class_plot(self):
        """Initialize class history plot for blitting."""
        for line in self.hist_lines:
            line.set_data([], [])
        return self.hist_lines
    
    def _update_hist_class_plot(self, frame):
        """Update class history plot for animation."""
        for i, line in enumerate(self.hist_lines):
            line.set_data(-np.arange(0, len(self.historic_data)), [data["class_proba"][i] for data in self.historic_data])

        return self.hist_lines
    
####################################################################################################
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
        self.windows_menu_audio.triggered.connect(self.open_audio_window)
        self.windows_menu_mel.triggered.connect(self.open_mel_window)

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
        if not hasattr(self, "audio_window") or self.audio_window is None:
            self.logger.info("Opening the Audio Window")
            self.audio_window = GUIAudioWindow(self.db, self.log, self.ser, base_data)
            self.audio_window.show()

    def open_mel_window(self, base_data = None):
        if not hasattr(self, "mel_window") or self.mel_window is None:
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
        #self.logger.info(f"Received {len(message)} bytes for prefix {prefix}")
        if prefix == self.db.get_item("Serial Settings", "database_prefix").value:
            self.logger.info(f"New configuration received: {message}")
        elif prefix == self.db.get_item("Audio Settings", "serial_prefix").value:
            self.logger.info(f"New audio data received of length {len(message)}")
            # Ill have to pass the message in the init of the window, so that it can be displayed
            self.open_audio_window(message)
        elif prefix == self.db.get_item("MEL Settings", "serial_prefix").value:
            self.logger.info(f"New MEL data received of length {len(message)}")
            self.open_mel_window(message)
        else:
            self.logger.warning(f"Unknown prefix {prefix} (message length: {len(message)})")

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
    db.add_item("MEL Settings", "serial_prefix", db.Text("Serial Prefix", "DF:HEX:", "The prefix to use for the MEL data serial communication"))
    db.add_item("MEL Settings", "file_prefix", db.Text("File Prefix", "mel", "The prefix to use for the MEL files before adding the timestamp"))
    db.add_item("MEL Settings", "max_history_length", db.Integer("Max History Length", 10, "The maximum number of data points to keep in the history"))
    db.add_item("MEL Settings", "mel_length", db.Integer("MEL Length", 20, "The length of the MEL vectors"))
    db.add_item("MEL Settings", "mel_number", db.Integer("MEL Number", 20, "The number of MEL vectors in the feature vector"))
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

