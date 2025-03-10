import datetime
import pathlib as pathl
import sys
import time
from typing import Optional

import click
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import sklearn
import soundfile as sf
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt6 import QtGui
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from serial.tools import list_ports

from .__version__ import __version__
from .libraries import database_utils as dbu
from .libraries import logging_utils as logu
from .libraries import serial_utils as seru
from .model_trainer import (
    load_model,
)


class GUIParamWindow(QMainWindow):
    """Parameters GUI window for the application"""

    def __init__(self, db: dbu.ContentDatabase, log: logu.ContentLogger):
        super().__init__()

        self.db = db
        self.log = log

        # Create the main window
        self.setWindowTitle(
            f"{self.db.get_item('_hidden', 'appname').value} - Parameters Window"
        )
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
        self.title = QLabel("Parameters Window")
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

    def __init__(
        self,
        db: dbu.ContentDatabase,
        log: logu.ContentLogger,
        ser: seru.SerialController,
        base_data=None,
    ):
        super().__init__()

        self.db = db
        self.log = log
        self.ser = ser
        self.logger = log.logger

        self.audio_data = np.zeros(12000)
        self.prefix_message_handler(
            self.db.get_item("Audio Settings", "serial_prefix").value, message=base_data
        )

        self.ser.data_received_prefix.connect(self.prefix_message_handler)

        # Create the main window
        self.setWindowTitle(
            f"{self.db.get_item('_hidden', 'appname').value} - Audio Window"
        )
        self.setGeometry(100, 100, 800, 600)

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Freeze the audio data
        self.audio_freeze = False

        # Create the UI
        self.create_ui()

    def update_audio_data(self, data):
        self.audio_freeze = self.db.get_item("Audio Settings", "audio_freeze").value
        if not self.audio_freeze:
            print("Updating audio data")
            self.audio_data = data
        if self.db.get_item("Audio Settings", "auto_save").value:
            self.save_audio_data_npy(self.audio_data)

    def prefix_message_handler(self, prefix, message):
        print(prefix)
        if prefix == self.db.get_item("Audio Settings", "serial_prefix").value:
            array_hex = bytes.fromhex(message)
            audio_vec = np.frombuffer(
                array_hex, dtype=np.dtype(np.int16).newbyteorder("<")
            )
            self.update_audio_data((audio_vec / (2**11)) - 0.5)

    def create_ui(self):
        # Add title to the window
        self.title = QLabel("Audio Window")
        self.title.setFont(QtGui.QFont("Arial", 20))
        self.main_layout.addWidget(self.title)

        # Add a FPS counter
        self.fps_counter = QLabel("FPS: 0")
        self.main_layout.addWidget(self.fps_counter)
        self.current_time = time.time()

        # Add Demo Box for data spawning and testing
        if True:
            self.demo_box = QGroupBox("Demo Box")
            self.demo_box.setCheckable(True)
            self.demo_box.setChecked(False)
            self.demo_box.setFixedHeight(15)
            self.demo_box_layout = QVBoxLayout()
            self.demo_box.setLayout(self.demo_box_layout)
            self.demo_box.toggled.connect(
                lambda state: self.demo_box.setFixedHeight(15)
                if not state
                else self.demo_box.setFixedHeight(100)
            )
            self.main_layout.addWidget(self.demo_box)

            self.demo_super_spawn = QPushButton("Push Random Audio Data")

            def super_spawn():
                self.update_audio_data((np.random.rand(12000) * 2 - 1) * 1 / 2)

            self.demo_super_spawn.clicked.connect(super_spawn)
            self.demo_box_layout.addWidget(self.demo_super_spawn)

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
        (self.line_audio,) = self.ax_audio.plot([], [], animated=True)
        (self.line_fft,) = self.ax_fft.plot([], [], animated=True)

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
            interval=1 / TARGET_FPS * 1000,
            blit=True,
            save_count=1,
        )
        self.anim_fft = FuncAnimation(
            self.fig_fft,
            self._update_fft_plot,
            init_func=self._init_fft_plot,
            interval=1 / TARGET_FPS * 1000,
            blit=True,
            save_count=1,
        )

        # Add the save button
        self.save_button_widget = QWidget()
        self.save_button_layout = QHBoxLayout()
        self.save_button_widget.setLayout(self.save_button_layout)
        self.save_button_npy = QPushButton("Save Audio Data (NPY/CSV/TXT)")
        self.save_button_npy.clicked.connect(
            lambda: self.save_audio_data_npy(self.audio_data)
        )
        self.save_button_layout.addWidget(self.save_button_npy)
        self.main_layout.addWidget(self.save_button_widget)
        self.save_button_audio = QPushButton("Save Audio Data (WAV/FLAC/OGG/MP3)")
        self.save_button_audio.clicked.connect(
            lambda: self.save_audio_data_wav(self.audio_data)
        )
        self.save_button_layout.addWidget(self.save_button_audio)
        self.save_button_plots = QPushButton("Save Plots")
        self.save_button_layout.addWidget(self.save_button_plots)

        # Add the ability to freeze the audio data and auto save it
        self.freeze_widget_group = QWidget()
        self.freeze_widget_layout = QHBoxLayout()
        self.freeze_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.freeze_widget_group.setLayout(self.freeze_widget_layout)
        self.freeze_checkbox = self.db.get_item(
            "Audio Settings", "audio_freeze"
        ).gen_widget_full()
        self.freeze_widget_layout.addWidget(self.freeze_checkbox)
        self.freeze_checkbox.setStyleSheet("padding: 0px; margin: 0px;")

        self.auto_save_checkbox = self.db.get_item(
            "Audio Settings", "auto_save"
        ).gen_widget_full()
        self.freeze_widget_layout.addWidget(self.auto_save_checkbox)
        self.auto_save_checkbox.setStyleSheet("padding: 0px; margin: 0px;")

        self.main_layout.addWidget(self.freeze_widget_group)

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
        freqs = np.fft.fftshift(np.fft.fftfreq(len(fft_data), 1 / 44100))
        self.line_fft.set_data(freqs, fft_data)

        # Update FPS
        current_time = time.time()
        fps = 1 / max((current_time - self.current_time), 1e-16)
        self.current_time = current_time
        self.fps_counter.setText(f"FPS: {fps:.2f}")
        return (self.line_fft,)

    def _get_audio_file_name(self):
        prefix = self.db.get_item("Audio Settings", "file_prefix").value
        time_stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        folder = self.db.get_item("Folder Settings", "audio path").value
        # Gen folder if not yet created
        pathl.Path(folder).mkdir(parents=True, exist_ok=True)
        return f"{folder}/{prefix}_{time_stamp}"

    def save_audio_data_npy(self, data=None):
        file_name = self._get_audio_file_name()
        file_extension_raw = self.db.get_item("Audio Settings", "raw_file_type").value
        file_extension_raw = file_extension_raw[1][file_extension_raw[0]]
        file_name_raw = f"{file_name}.{file_extension_raw}"
        if file_extension_raw == "npy":
            np.save(file_name_raw, data)
        elif file_extension_raw == "csv":
            np.savetxt(file_name_raw, data, delimiter=",")
        elif file_extension_raw == "txt":
            np.savetxt(file_name_raw, data)
        else:
            self.logger.error(f"Unknown file extension {file_extension_raw}")
        self.logger.info(f"Saved audio data to {file_name_raw}")

    def save_audio_data_wav(self, data=None):
        file_name = self._get_audio_file_name()
        file_extension_audio = self.db.get_item("Audio Settings", "audio_format").value
        file_extension_audio = file_extension_audio[1][file_extension_audio[0]]
        file_name_audio = f"{file_name}.{file_extension_audio}"
        if file_extension_audio == "wav":
            wav.write(file_name_audio, 44100, data)
        elif file_extension_audio == "flac":
            sf.write(file_name_audio, data, 44100, "FLAC")
        elif file_extension_audio == "ogg":
            sf.write(file_name_audio, data, 44100, "OGG")
        elif file_extension_audio == "mp3":
            sf.write(file_name_audio, data, 44100, "MP3")
        else:
            self.logger.error(f"Unknown file extension {file_extension_audio}")
        self.logger.info(f"Saved audio data to {file_name_audio}")


class GUIMELWindow(QMainWindow):
    """MEL GUI window for the application and the classifier"""

    def __init__(
        self,
        db: dbu.ContentDatabase,
        log: logu.ContentLogger,
        ser: seru.SerialController,
        base_data=None,
    ):
        super().__init__()

        self.db = db
        self.log = log
        self.ser = ser
        self.logger = log.logger

        self.current_mel_length = self.db.get_item("MEL Settings", "mel_length").value
        self.current_mel_number = self.db.get_item("MEL Settings", "mel_number").value
        self.current_feature_length = self.current_mel_length * self.current_mel_number
        self.max_hist_length = self.db.get_item(
            "MEL Settings", "max_history_length"
        ).value

        # Load the current model
        self.current_model_path = self.db.get_item(
            "Classifier Settings", "model_path"
        ).value
        # Structure of the model :
        #  {"model": AbstractModelWrapper, "mel_len": int, "mel_num": int, "classes": List[str]}
        try:
            self.current_model_dict = load_model(self.current_model_path)
            if self.current_model_dict is None:
                self.logger.error("Error loading the model : No model found")
            else:
                self.current_model_dict = self.current_model_dict.to_dict()
        except Exception as e:
            self.current_model_dict = {}
            self.logger.error(f"Error loading the model : {e}")
        if type(self.current_model_dict) != dict:
            self.current_model = None
            self.current_model_dict = {}
            self.logger.error("Error loading the model : Not a dictionary")

        self.current_model = None
        if "model" in self.current_model_dict:
            self.current_model = self.current_model_dict["model"]

        # Check if the model is loaded
        if self.current_model is None:
            self.logger.error(
                "No model loaded, please select a model in the classification settings, or use >> rye run model-trainer << to train a model"
            )
            self.current_model = None
        else:
            self.logger.info(f"Model loaded from {self.current_model_path}")
            # Load the rest of the parameters
            self.current_mel_length = self.current_model_dict.get("mel_len", 20)
            self.current_mel_number = self.current_model_dict.get("mel_num", 20)
            self.current_feature_length = (
                self.current_mel_length * self.current_mel_number
            )
            self.classes = self.current_model_dict.get(
                "classes", [f"Class {i}" for i in range(10)]
            )
            self.num_classes = len(self.classes)

        # Verify the model parameters
        if self.current_model is not None:
            if (
                self.current_model_dict["mel_len"] != self.current_mel_length
                or self.current_model_dict["mel_num"] != self.current_mel_number
            ):
                self.logger.error(
                    f"Model parameters do not match the current MEL parameters : {self.current_model_dict['mel_len']} != {self.current_mel_length} or {self.current_model_dict['mel_num']} != {self.current_mel_number}"
                )
                self.current_model = None
            if "classes" not in self.current_model_dict:
                self.logger.error("Model does not have specified classes")
                self.current_model = None

        self.num_classes = (
            len(self.current_model_dict["classes"])
            if self.current_model is not None
            else 10
        )

        # Create the data : list[dict<"data": np.ndarray, "class_proba": np.ndarray]
        self.historic_data = [
            {
                "data": np.zeros(self.current_feature_length),
                "class_proba": np.zeros(self.num_classes),
            }
            for _ in range(self.max_hist_length)
        ]
        if base_data is not None and type(base_data) == np.ndarray:
            self.add_data(base_data)

        self.ser.data_received_prefix.connect(self.prefix_message_handler)

        # Create the main window
        self.setWindowTitle(
            f"{self.db.get_item('_hidden', 'appname').value} - MEL Window"
        )
        self.setGeometry(100, 100, 800, 600)

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Add demo box for data spawning and testing
        if True:
            self.demo_box = QGroupBox("Demo Box")
            self.demo_box.setCheckable(True)
            self.demo_box.setChecked(False)
            self.demo_box.setFixedHeight(15)
            self.demo_box_layout = QVBoxLayout()
            self.demo_box.setLayout(self.demo_box_layout)
            self.demo_box.toggled.connect(
                lambda state: self.demo_box.setFixedHeight(15)
                if not state
                else self.demo_box.setFixedHeight(100)
            )
            self.main_layout.addWidget(self.demo_box)

            self.demo_super_spawn = QPushButton("Push Random Mel Data")
            self.demo_super_spawn.clicked.connect(
                lambda: self.add_data(
                    np.random.randint(0, 2**16, self.current_feature_length)
                )
            )
            self.demo_box_layout.addWidget(self.demo_super_spawn)

            self.demo_super_spawn = QPushButton(
                "Push Random Mel and Random Class Data (if no model)"
            )
            self.demo_super_spawn.clicked.connect(
                lambda: self.add_data(
                    np.random.randint(0, 2**16, self.current_feature_length)
                )
            )
            self.demo_super_spawn.clicked.connect(
                lambda: self.historic_data[0].update(
                    {
                        "class_proba": np.random.rand(self.num_classes)
                        if self.historic_data[0]["class_proba"].sum() == 0
                        else self.historic_data[0]["class_proba"]
                    }
                )
            )
            self.demo_box_layout.addWidget(self.demo_super_spawn)

        # Create the UI
        self.create_ui()

    def add_data(self, data):
        if not self.db.get_item("MEL Settings", "mel_freeze").value:
            max_history = self.db.get_item("MEL Settings", "max_history_length").value
            self.historic_data = [
                {"data": data, "class_proba": np.zeros(self.num_classes)}
            ] + self.historic_data[:-1]
            if len(self.historic_data) > max_history:
                self.historic_data = self.historic_data[:max_history]
            elif len(self.historic_data) < max_history:
                self.historic_data = self.historic_data + [
                    {
                        "data": np.zeros(self.current_feature_length),
                        "class_proba": np.zeros(self.num_classes),
                    }
                    for _ in range(max_history - len(self.historic_data))
                ]

        # Classify the data
        if self.current_model is not None:
            # Take the lastest data
            data = self.historic_data[0]["data"]
            # Classify the data
            self.current_model: Optional[sklearn.base.BaseEstimator]
            class_proba = self.current_model.predict(data.reshape(1, -1))
            self.historic_data[0].update({"class_proba": class_proba[0]})

        # If auto_save
        if self.db.get_item("MEL Settings", "auto_save").value:
            self.save_mel_data(single=True)

    def prefix_message_handler(self, prefix, message):
        if prefix == self.db.get_item("MEL Settings", "serial_prefix").value:
            # Message is a packet of mel data
            if len(message) >= 2 * self.current_feature_length:
                message = message[16:-32]

            # Convert the message to a mel vector
            array_hex = bytes.fromhex(message)
            mel_vec = np.frombuffer(
                array_hex, dtype=np.dtype(np.uint16).newbyteorder("<")
            )
            self.add_data(mel_vec)

    def create_ui(self):
        # Add title to the window
        self.title = QLabel("MEL Window")
        self.title.setFont(QtGui.QFont("Arial", 20))
        self.main_layout.addWidget(self.title)

        # Add a FPS counter
        self.fps_counter = QLabel("FPS: 0")
        self.main_layout.addWidget(self.fps_counter)
        self.current_time = time.time()

        # Say if the model is loaded
        if self.current_model is not None:
            self.model_loaded = QLabel("Model Loaded : " + str(self.current_model_path))
            self.model_loaded.setStyleSheet("color: green")
        else:
            self.model_loaded = QLabel("No Model Loaded")
            self.model_loaded.setStyleSheet("color: red")
        self.main_layout.addWidget(self.model_loaded)

        # Add a text that is invisible if there are no errors on the hist graph
        self.error_text = QLabel("Error : ")
        self.error_text.setStyleSheet("color: red")
        self.error_text.setVisible(False)
        self.main_layout.addWidget(self.error_text)

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
        self.mel_rect = Rectangle(
            (-1.125 + 0.5, -0.025),
            1.05,
            1.05,
            linewidth=1,
            edgecolor="red",
            facecolor="none",
        )

        self.mel_pcolors = []
        self.setup_mel_plots()

        self.db.get_item("MEL Settings", "max_history_length").register_callback(
            self.setup_mel_plots
        )

        # Setup the graph for the classifier
        self.class_ax.set_title("Classifier Probabilities")
        self.class_ax.set_xlabel("Classes")
        self.class_ax.set_ylabel("Probability")
        self.class_ax.set_xlim(-0.5, 9.5)
        self.class_ax.set_ylim(-0.05, 1.05)
        self.class_ax.autoscale(enable=False, axis="both")

        self.classes = self.current_model_dict.get(
            "classes", [f"Class {i}" for i in range(self.num_classes)]
        )
        self.num_classes = len(self.classes)
        self.class_histogram = self.class_ax.hist(
            self.classes,
            bins=len(self.classes),
            weights=np.zeros(len(self.classes)),
            align="mid",
            rwidth=0.5,
            color="blue",
        )

        self.hist_ax.set_title("Classifier History")
        self.hist_ax.set_xlabel("Time Frames")
        self.hist_ax.set_ylabel("Probability")
        self.hist_ax.set_xlim(-9, 0)
        self.hist_ax.set_ylim(-0.05, 1.45)
        self.hist_ax.autoscale(enable=False, axis="both")

        self.hist_lines = []
        for i in range(len(self.classes)):
            (line,) = self.hist_ax.plot([], [], animated=True, label=self.classes[i])
            self.hist_lines.append(line)

        # Place a external legend
        self.hist_ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        self.fig_class_history.subplots_adjust(
            left=0.15, right=0.75, top=0.9, bottom=0.2
        )

        # Add the animation
        TARGET_FPS = self.db.get_item("Plot Settings", "framerate").value
        self.anim_mel = FuncAnimation(
            self.fig_mel,
            self._update_mel_plot,
            init_func=self._init_mel_plot,
            interval=1 / TARGET_FPS * 1000,
            blit=True,
            save_count=1,
        )

        self.anim_class = FuncAnimation(
            self.fig_classifier,
            self._update_class_plot,
            init_func=self._init_class_plot,
            interval=1 / TARGET_FPS * 1000,
            blit=True,
            save_count=1,
        )

        self.anim_hist_class = FuncAnimation(
            self.fig_class_history,
            self._update_hist_class_plot,
            init_func=self._init_hist_class_plot,
            interval=1 / TARGET_FPS * 1000,
            blit=True,
            save_count=1,
        )

        # Add the save group
        self.save_group = QGroupBox("Additional Options")
        self.save_group_layout = QGridLayout()
        self.save_group.setLayout(self.save_group_layout)

        # Add the mel saving options (for the melvectors and the class probabilities raw data)
        self.auto_save_mel = self.db.get_item(
            "MEL Settings", "auto_save"
        ).gen_widget_full()
        self.save_group_layout.addWidget(self.auto_save_mel, 0, 0)
        self.mel_freeze = self.db.get_item(
            "MEL Settings", "mel_freeze"
        ).gen_widget_full()
        self.save_group_layout.addWidget(self.mel_freeze, 0, 1)
        self.save_melbox = QPushButton("Save Mel Data (NPY)")
        self.save_group_layout.addWidget(self.save_melbox, 1, 0)
        self.save_melbox.clicked.connect(self.save_mel_data)

        self.main_layout.addWidget(self.save_group)

    def setup_mel_plots(self, number_of_bins=10):
        self.mel_pcolors = []
        self.mel_ax.clear()
        self.mel_ax.set_title("MEL Spectrogram")
        self.mel_ax.set_xlabel("Time Frames")
        self.mel_ax.set_ylabel("Mel Frequency Bins")
        self.mel_ax.set_xlim(-number_of_bins * 1.1 + 0.4, 0.1 + 0.5)
        self.mel_ax.set_ylim(-0.05, 1.05)
        self.mel_ax.autoscale(enable=False, axis="both")
        self.mel_ax.set_xticks(np.arange(-number_of_bins, 1, 1))

        for i in range(number_of_bins):
            offset = -1.1
            X, Y = np.meshgrid(
                np.linspace(0, 1, self.current_mel_number),
                np.linspace(0, 1, self.current_mel_length),
            )
            image = self.mel_ax.pcolormesh(
                X + i * offset - 1.1 + 0.5,
                Y,
                np.zeros((self.current_mel_length, self.current_mel_number)),
                vmin=0,
                vmax=(2**16),
                cmap="viridis",
                shading="auto",  # Avoid gridlines
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
                data: np.ndarray = self.historic_data[i]["data"]
            else:
                data = np.zeros(self.current_feature_length)
            raveled_data = data.reshape(
                self.current_mel_length, self.current_mel_number
            ).T.ravel()
            image.set_array(raveled_data)

        # FPS counter
        current_time = time.time()
        fps = 1 / max((current_time - self.current_time), 1e-16)
        self.current_time = current_time
        self.fps_counter.setText(f"FPS: {fps:.2f}")

        return self.mel_pcolors + [self.mel_rect]

    def _init_class_plot(self):
        """Initialize class plot for blitting."""
        self.class_histogram = self.class_ax.hist(
            self.classes,
            bins=self.num_classes,
            weights=np.zeros(self.num_classes),
            align="mid",
            rwidth=0.5,
            color="blue",
            edgecolor="black",
        )
        # Make the class titles vertical
        self.class_ax.set_xticks(np.arange(0, self.num_classes, 1))
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
                rect.set_color("red")
            else:
                rect.set_color("blue")

        return self.class_histogram[2]

    def _init_hist_class_plot(self):
        """Initialize class history plot for blitting."""
        for line in self.hist_lines:
            line.set_data([], [])
        return self.hist_lines

    def _update_hist_class_plot(self, frame):
        """Update class history plot for animation."""
        for i, line in enumerate(self.hist_lines):
            try:
                line.set_data(
                    -np.arange(0, len(self.historic_data)),
                    [data["class_proba"][i] for data in self.historic_data],
                )
            except Exception as e:
                self.error_text.setVisible(True)
                self.error_text.setText(f"Classifier History Error (suppressed) : {e}")

        return self.hist_lines

    def save_mel_data(self, single=False):
        if not single:
            # Get the file name
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Mel Data",
                str(pathl.Path(__file__).parent),
                "NPY Files (*.npy)",
            )
            if file_name:
                self.logger.info(f"Saving mel data to {file_name}")
                np.save(file_name, self.historic_data)
        else:
            # Get the file name
            file_name = self._get_mel_file_name()
            self.logger.info(f"Auto saving mel data to {file_name}")
            np.save(file_name, [self.historic_data[0]])

    def _get_mel_file_name(self):
        prefix = self.db.get_item("MEL Settings", "file_prefix").value
        time_stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        folder = self.db.get_item("Folder Settings", "mel path").value
        # Gen folder if not yet created
        pathl.Path(folder).mkdir(parents=True, exist_ok=True)
        return f"{folder}/{prefix}_{time_stamp}"


####################################################################################################
class GUIMainWindow(QMainWindow):
    """Main GUI window for the application"""

    def __init__(
        self,
        db: dbu.ContentDatabase,
        log: logu.ContentLogger,
        ser: seru.SerialController,
    ):
        super().__init__()

        self.db = db
        self.log = log
        self.logger = log.logger
        self.ser = ser

        # Create the main window
        self.screen_resolution = self.screen().geometry()
        # print(f"Screen resolution: {self.screen_resolution}")
        self.setWindowTitle(
            f"{self.db.get_item('_hidden', 'appname').value} - Main Window"
        )
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
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import Settings",
            str(pathl.Path(__file__).parent),
            "NPY Files (*.npy)",
        )
        if file_name:
            self.logger.info(f"Importing settings from {file_name}")
            self.db.import_database(file_name)

    def export_settings(self):
        # Get the file name
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            str(pathl.Path(__file__).parent),
            "NPY Files (*.npy)",
        )
        if file_name:
            self.logger.info(f"Exporting settings to {file_name}")
            self.db.export_database(file_name)

    def open_params_window(self):
        self.logger.info("Opening the Parameters Window")
        self.params_window = GUIParamWindow(self.db, self.log)
        self.params_window.show()

    def open_audio_window(self, base_data=None):
        if not hasattr(self, "audio_window") or self.audio_window is None:
            self.logger.info("Opening the Audio Window")
            self.audio_window = GUIAudioWindow(self.db, self.log, self.ser, base_data)
            self.audio_window.closeEvent = lambda event: setattr(
                self, "audio_window", None
            )
            self.audio_window.show()

    def open_mel_window(self, base_data=None):
        if not hasattr(self, "mel_window") or self.mel_window is None:
            self.logger.info("Opening the MEL Window")
            self.mel_window = GUIMELWindow(self.db, self.log, self.ser, base_data)
            self.mel_window.closeEvent = lambda event: setattr(self, "mel_window", None)
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
        self.title = QLabel(
            f"{self.db.get_item('_hidden', 'appname').value} - v{self.db.get_item('_hidden', 'appversion').value}"
        )
        self.title.setFont(QtGui.QFont("Arial", 24))
        self.author = QLabel(f"Made by {self.db.get_item('_hidden', 'author').value}")
        self.description = QLabel(
            f"{self.db.get_item('_hidden', 'app_description').value}"
        )
        self.author.setFont(QtGui.QFont("Arial", 8))
        self.description.setFont(QtGui.QFont("Arial", 9))
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.author)
        self.main_layout.addWidget(self.description)

        # Add the serialport selection
        self.layout_serialport = QHBoxLayout()
        self.serialport_label = QLabel("Serial Port:")
        self.serialport_label.setFixedWidth(80)
        self.serialPortWidget = self.db.get_item(
            "Serial Settings", "port"
        ).gen_widget_element()
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
        self.write_message.setPlaceholderText(
            "Enter message to be sent to the serial port"
        )
        self.write_button = QPushButton("Write")
        self.write_button.setFixedWidth(100)
        self.write_button.clicked.connect(self.write_message_handler)
        self.layout_write.addWidget(self.write_label)
        self.layout_write.addWidget(self.write_message)
        self.layout_write.addWidget(self.write_button)
        self.main_layout.addLayout(self.layout_write)
        self.db.get_item("Serial Settings", "allowwrite").register_callback(
            self.write_box_state_callback
        )
        # Add the console clear button
        self.clear_button = QPushButton("Clear Console")
        self.clear_button.clicked.connect(self.console.clear)
        self.main_layout.addWidget(self.clear_button)

        # Trigger the first callbacks :
        self.refresh_ports()
        self.write_box_state_callback(
            self.db.get_item("Serial Settings", "allowwrite").value
        )

    def refresh_ports(self):
        comports = self.ser.available_ports()  # Dictionary of comports
        old_value = self.db.get_item("Serial Settings", "port").value
        self.db.get_item("Serial Settings", "port").set_value(
            (
                old_value[0],
                [
                    f"{device} - {description}"
                    for device, description in comports.items()
                ]
                if len(comports) > 0
                else ["-- No Ports Detected --"],
            )
        )

    def write_box_state_callback(self, state):
        the_state = bool(state)  # From the allowwrite checkbox
        if the_state:
            self.write_message.setEnabled(True)
            self.write_button.setEnabled(True)
            self.write_message.setPlaceholderText(
                "Enter message to be sent to the serial port"
            )
        else:
            self.write_message.setEnabled(False)
            self.write_button.setEnabled(False)
            self.write_message.setPlaceholderText(
                "Sending messages is disabled in settings"
            )

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
        else:
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
        # self.logger.error(message)
        pass

    def normal_message_handler(self, message):
        if message == "TERMINATE":
            return
        self.logger.info(message)
        print(f">>{message}")

    def prefix_message_handler(self, prefix, message):
        # Print to the log file the received data
        log_path = self.db.get_item("Folder Settings", "log path").value
        log_file = self.db.get_item("Logging Settings", "file_name").value
        log_message = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {prefix} : {message}"
        with open(str(log_path / log_file), "a") as f:
            f.write(log_message + "\n")
        print(
            f"Received {len(message)} bytes for prefix {prefix}, check the log file for the whole message"
        )
        self.logger.info(
            f"Received {len(message)} bytes for prefix {prefix}, check the log file for the whole message"
        )

        # self.logger.info(f"Received {len(message)} bytes for prefix {prefix}")
        if prefix == self.db.get_item("Serial Settings", "database_prefix").value:
            self.logger.info(f"New configuration received: {message}")
        elif prefix == self.db.get_item("Audio Settings", "serial_prefix").value:
            self.open_audio_window(message)
            # Print the received data only to the log file
            self.logger.debug(f"Received audio data: {message}")
        elif prefix == self.db.get_item("MEL Settings", "serial_prefix").value:
            self.open_mel_window(message)
            # Print the received data only to the log file
            self.logger.debug(f"Received MEL data: {message}")
        else:
            self.logger.warning(
                f"Unknown prefix {prefix} (message length: {len(message)})"
            )


####################################################################################################
# Database Initialization
####################################################################################################


def database_init(db: dbu.ContentDatabase):
    # Add the Hidden group
    db.create_category("_hidden")
    db.add_item(
        "_hidden",
        "appname",
        db.ConstantText("App Name", "UART Reader", "The name of the application"),
    )
    db.add_item(
        "_hidden",
        "appversion",
        db.ConstantText("App Version", __version__, "The version of the application"),
    )
    db.add_item(
        "_hidden",
        "author",
        db.ConstantText(
            "Author", "Groupe E 2024-2025", "The author of the application"
        ),
    )
    db.add_item(
        "_hidden",
        "app_description",
        db.ConstantText(
            "App Description",
            "This application reads data from a Serial port and displays it in a GUI, and handles certain prefixes.",
            "The description of the application",
        ),
    )

    # Folder Settings
    db.create_category("Folder Settings")
    base_path = pathl.Path(__file__).parent
    second_path = base_path.parent / "data"
    db.add_item(
        "Folder Settings",
        "app path",
        db.Folder("App Path", base_path, "The path to the application"),
    )
    db.add_item(
        "Folder Settings",
        "log path",
        db.Folder("Log Path", base_path, "The path to the log file"),
    )
    db.add_item(
        "Folder Settings",
        "db path",
        db.Folder(
            "Database Path", second_path / "db_saves", "The path to the database file"
        ),
    )
    db.add_item(
        "Folder Settings",
        "audio path",
        db.Folder("Audio Path", second_path / "audio", "The path to the audio file"),
    )
    db.add_item(
        "Folder Settings",
        "mel path",
        db.Folder("MEL Path", second_path / "mel", "The path to the MEL file"),
    )
    db.add_item(
        "Folder Settings",
        "plot path",
        db.Folder("Plot Path", second_path / "plots", "The path to the plot file"),
    )

    # Serial Settings
    db.create_category("Serial Settings")
    comports = list_ports.comports()
    db.add_item(
        "Serial Settings",
        "port",
        db.ChoiceBox(
            "Port",
            (
                0,
                [port.device for port in comports]
                if len(comports) > 0
                else ["-- No Ports Detected --"],
            ),
            "The port to use for the serial connection",
        ),
    )
    db.add_item(
        "Serial Settings",
        "baud",
        db.ChoiceBox(
            "Baud Rate",
            (0, ["115200", "9600", "4800", "2400", "1200", "600", "300"]),
            "The baud rate to use for the serial connection",
        ),
    )
    db.add_item(
        "Serial Settings",
        "freeze",
        db.Boolean("Freeze", False, "Freeze the serial connection"),
    )
    db.add_item(
        "Serial Settings",
        "freezebuffering",
        db.Boolean(
            "Freeze Buffering",
            False,
            "To buffer or not the freezed data to avoid data loss, at the cost of possible memory overflow",
        ),
    )
    db.add_item(
        "Serial Settings",
        "allowwrite",
        db.Boolean(
            "Allow Write", False, "Allow sending messages through the serial port"
        ),
    )
    db.add_item(
        "Serial Settings",
        "database_prefix",
        db.Text(
            "Database Prefix",
            "CFG:HEX:",
            "The prefix to use to update the database from the connected device",
        ),
    )

    # Logging Settings
    db.create_category("Logging Settings")
    db.add_item(
        "Logging Settings",
        "loglevel",
        db.ChoiceBox(
            "Log Level",
            (1, ["DEBUG", "TRACE", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]),
            "The level of logging to use",
        ),
    )
    db.add_item(
        "Logging Settings",
        "logformat",
        db.ChoiceBox(
            "Log Format",
            (
                0,
                [
                    "[%(asctime)s] %(levelname)-9s: %(message)s",
                    "%(levelname)-9s: %(message)s",
                    "%(message)s",
                ],
            ),
            "The format of the log messages",
        ),
    )
    db.add_item(
        "Logging Settings",
        "logdatefmt",
        db.ChoiceBox(
            "Log Date Format",
            (0, ["%Y-%m-%d %H:%M:%S", "%H:%M:%S"]),
            "The format of the date in the log messages",
        ),
    )
    db.add_item(
        "Logging Settings",
        "use_file",
        db.Boolean("Use File", True, "Use a file for logging"),
    )
    db.add_item(
        "Logging Settings",
        "file_name",
        db.Text("File Name", "uart_logs.log", "The name of the log file"),
    )

    # Plot Settings
    db.create_category("Plot Settings")
    db.add_item(
        "Plot Settings",
        "limit_framerate",
        db.Boolean("Limit Framerate", False, "Limit the framerate of the plots"),
    )
    db.add_item(
        "Plot Settings",
        "framerate",
        db.Integer(
            "Framerate",
            30,
            "The target framerate of the plots to avoid over-consumption of resources",
        ),
    )
    db.add_item(
        "Plot Settings",
        "number_saves",
        db.RangeInt(
            "Number Of Save Types",
            (2, 1, 3),
            "The number of different save types to use",
        ),
    )
    db.add_item(
        "Plot Settings",
        "first_format",
        db.ChoiceBox(
            "First Format",
            (0, ["pdf", "png", "html", "jpg", "jpeg", "svg"]),
            "The format to save the plots in",
        ),
    )
    db.add_item(
        "Plot Settings",
        "second_format",
        db.ChoiceBox(
            "Second Format",
            (1, ["pdf", "png", "html", "jpg", "jpeg", "svg"]),
            "The format to save the plots in",
        ),
    )
    db.add_item(
        "Plot Settings",
        "third_format",
        db.ChoiceBox(
            "Third Format",
            (2, ["pdf", "png", "html", "jpg", "jpeg", "svg"]),
            "The format to save the plots in",
        ),
    )
    db.add_item(
        "Plot Settings",
        "plot_prefix",
        db.Text(
            "Plot Prefix",
            "plot",
            "The prefix to use for the plot files before adding the timestamp",
        ),
    )

    # Audio Settings
    db.create_category("Audio Settings")
    db.add_item(
        "Audio Settings",
        "serial_prefix",
        db.Text(
            "Serial Prefix",
            "SND:HEX:",
            "The prefix to use for the audio data serial communication",
        ),
    )
    db.add_item(
        "Audio Settings",
        "nucleo_sample_rate",
        db.SuffixFloat(
            "Nucleo Sample Rate", (10240, "Hz"), "The sample rate of the Nucleo board"
        ),
    )
    db.add_item(
        "Audio Settings",
        "file_prefix",
        db.Text(
            "File Prefix",
            "audio",
            "The prefix to use for the audio files before adding the timestamp",
        ),
    )
    db.add_item(
        "Audio Settings",
        "audio_format",
        db.ChoiceBox(
            "Audio Format",
            (0, ["wav", "flac", "ogg", "mp3"]),
            "The format to save the audio files in",
        ),
    )
    db.add_item(
        "Audio Settings",
        "file_frequency",
        db.SuffixFloat(
            "File Frequency", (44100, "Hz"), "The frequency to save the audio files in"
        ),
    )
    db.add_item(
        "Audio Settings",
        "auto_save",
        db.Boolean("Auto Save", False, "Automatically save the audio files"),
    )
    db.add_item(
        "Audio Settings",
        "audio_freeze",
        db.Boolean("Audio Freeze", False, "Freeze the audio data"),
    )
    db.add_item(
        "Audio Settings",
        "save_data_raw",
        db.Boolean(
            "Save Data Raw", False, "Save the raw data as well as the audio data"
        ),
    )
    db.add_item(
        "Audio Settings",
        "save_data_plot",
        db.Boolean(
            "Save Data Plot", False, "Save the data as a plot as well as the audio data"
        ),
    )
    db.add_item(
        "Audio Settings",
        "raw_file_type",
        db.ChoiceBox(
            "Raw File Type",
            (0, ["npy", "csv", "txt"]),
            "The format to save the raw data in",
        ),
    )

    # MEL Settings
    db.create_category("MEL Settings")
    db.add_item(
        "MEL Settings",
        "serial_prefix",
        db.Text(
            "Serial Prefix",
            "DF:HEX:",
            "The prefix to use for the MEL data serial communication",
        ),
    )
    db.add_item(
        "MEL Settings",
        "file_prefix",
        db.Text(
            "File Prefix",
            "mel",
            "The prefix to use for the MEL files before adding the timestamp",
        ),
    )
    db.add_item(
        "MEL Settings",
        "max_history_length",
        db.Integer(
            "Max History Length",
            10,
            "The maximum number of data points to keep in the history",
        ),
    )
    db.add_item(
        "MEL Settings",
        "mel_length",
        db.Integer("MEL Length", 20, "The length of the MEL vectors"),
    )
    db.add_item(
        "MEL Settings",
        "mel_number",
        db.Integer("MEL Number", 20, "The number of MEL vectors in the feature vector"),
    )
    # TODO: Add more MEL settings
    db.add_item(
        "MEL Settings",
        "auto_save",
        db.Boolean("Auto Save", False, "Automatically save the MEL files"),
    )
    db.add_item(
        "MEL Settings",
        "mel_freeze",
        db.Boolean("MEL Freeze", False, "Freeze the MEL data"),
    )
    db.add_item(
        "MEL Settings",
        "save_data_raw",
        db.Boolean("Save Data Raw", False, "Save the raw data as well as the MEL data"),
    )
    db.add_item(
        "MEL Settings",
        "save_data_plot",
        db.Boolean(
            "Save Data Plot", False, "Save the data as a plot as well as the MEL data"
        ),
    )
    db.add_item(
        "MEL Settings",
        "raw_file_type",
        db.ChoiceBox(
            "Raw File Type",
            (0, ["npy", "csv", "txt"]),
            "The format to save the raw data in",
        ),
    )

    # Classifier Settings
    db.create_category("Classifier Settings")
    db.add_item(
        "Classifier Settings",
        "model_path",
        db.File(
            "Model Path",
            base_path.parent / "uart_reader" / "model.pickle",
            "The path to the model file",
        ),
    )
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
    db.get_item("Serial Settings", "freezebuffering").register_callback(
        change_buffering
    )

    # Change write allowed
    def change_write(value):
        ser.set_write_allow(value)

    change_write(db.get_item("Serial Settings", "allowwrite").value)
    db.get_item("Serial Settings", "allowwrite").register_callback(change_write)

    prefixes = [
        db.get_item("Audio Settings", "serial_prefix"),
        db.get_item("MEL Settings", "serial_prefix"),
        db.get_item("Serial Settings", "database_prefix"),
    ]

    def change_prefixes(value):
        ser.unregister_all_prefixes()
        for prefix in prefixes:
            ser.register_prefix(prefix.value)

    change_prefixes(None)
    for prefix in prefixes:
        prefix.register_callback(change_prefixes)


@click.command()
@click.option(
    "--logfile",
    default="../uart_logs.log",
    help="Log file to write to",
)
@click.option("--opaudio", is_flag=True, help="Open the audio window")
@click.option("--opmel", is_flag=True, help="Open the MEL window")
@click.option("--modelfile", default="None", help="Classifier model to use")
@click.option("--mel_length", default=20, help="Length of the MEL vectors")
@click.option(
    "--mel_number", default=20, help="Number of MEL vectors in the feature vector"
)
@click.option("--automel", is_flag=True, help="Automatically save the MEL files")
@click.option("--autoaudio", is_flag=True, help="Automatically save the audio files")
def main(
    logfile: str,
    opaudio: bool,
    opmel: bool,
    modelfile: str,
    mel_length: int,
    mel_number: int,
    automel: bool,
    autoaudio: bool,
):
    print("Starting the application ...")
    # Create the main application
    app = QApplication(sys.argv)

    # Set plotting style to blit with an option, and fast
    plt.style.use("fast")
    matplotlib.use("Qt5Agg")

    # Create the logger
    logelem = logu.ContentLogger(__name__, logfile, True)

    # Create the database
    db = dbu.ContentDatabase(database_init, logelem.logger, False)

    ## DB config from CLI
    db.get_item("MEL Settings", "mel_length").set_value(mel_length)
    db.get_item("MEL Settings", "mel_number").set_value(mel_number)
    db.get_item("MEL Settings", "auto_save").set_value(automel)
    db.get_item("Audio Settings", "auto_save").set_value(autoaudio)
    if modelfile != "None":
        db.get_item("Classifier Settings", "model_path").set_value(modelfile)

    # Create the serial controller
    ser = seru.SerialController(logelem.logger)

    # Create the main window
    main_window = GUIMainWindow(db, logelem, ser)
    main_window.show()

    # Connect the database to the logger
    connect_db_to_log(db, logelem)

    # Connect the database to the serial controller
    connect_db_to_ser(db, ser)

    # Open the audio window if requested
    if opaudio:
        main_window.open_audio_window()

    # Open the MEL window if requested
    if opmel:
        main_window.open_mel_window()

    # Execute the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
