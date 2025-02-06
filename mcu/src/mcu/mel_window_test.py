import pickle
import time
from typing import Optional, List

import numpy as np
import sklearn.base

# PyQt imports
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGroupBox, QPushButton,
    QLabel, QHBoxLayout
)

# Matplotlib imports
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.animation import FuncAnimation

# =============================================================================
# BACKEND CLASSES
# =============================================================================

class MelModelManager:
    """
    Loads and verifies the classification model and its associated parameters.
    """
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

        # Default parameters from the database
        self.current_mel_length = self.db.get_item("MEL Settings", "mel_length").value
        self.current_mel_number = self.db.get_item("MEL Settings", "mel_number").value
        self.current_feature_length = self.current_mel_length * self.current_mel_number

        self.current_model = None
        self.current_model_dict = {}
        self.classes: List[str] = []
        self.num_classes = 10

        self.load_model()

    def load_model(self):
        """Load the model dictionary from file and verify the settings."""
        model_path = self.db.get_item("Classifier Settings", "model_path").value
        try:
            with open(model_path, "rb") as f:
                self.current_model_dict = pickle.load(f)
        except Exception as e:
            self.current_model_dict = {}
            self.logger.error(f"Error loading the model: {e}")

        if not isinstance(self.current_model_dict, dict):
            self.logger.error("Error loading the model: Not a dictionary")
            self.current_model = None
            return

        self.current_model = self.current_model_dict.get("model", None)
        if self.current_model is None:
            self.logger.error("No model loaded, please load a model in the settings")
            return

        self.logger.info(f"Model loaded from {model_path}")
        # Overwrite default parameters if provided by the model
        self.current_mel_length = self.current_model_dict.get("mel_len", self.current_mel_length)
        self.current_mel_number = self.current_model_dict.get("mel_num", self.current_mel_number)
        self.current_feature_length = self.current_mel_length * self.current_mel_number
        self.classes = self.current_model_dict.get("classes", [f"Class {i}" for i in range(10)])
        self.num_classes = len(self.classes)

        # Verify that the model parameters match the current settings
        if (self.current_model_dict.get("mel_len") != self.current_mel_length or
            self.current_model_dict.get("mel_num") != self.current_mel_number):
            self.logger.error("Model parameters do not match the current MEL parameters")
            self.current_model = None

        if "classes" not in self.current_model_dict:
            self.logger.error("Model does not have specified classes")
            self.current_model = None


class MelDataBuffer:
    """
    Maintains a rolling buffer of MEL data frames and their classification probabilities.
    """
    def __init__(self, feature_length: int, num_classes: int, max_history: int):
        self.feature_length = feature_length
        self.num_classes = num_classes
        self.max_history = max_history
        self.reset_buffer()

    def reset_buffer(self):
        """Initialize the buffer with empty data."""
        self.historic_data = [
            {"data": np.zeros(self.feature_length), "class_proba": np.zeros(self.num_classes)}
            for _ in range(self.max_history)
        ]

    def update_max_history(self, new_max_history: int):
        """Adjust the buffer length if the maximum history setting changes."""
        self.max_history = new_max_history
        current_length = len(self.historic_data)
        if current_length > new_max_history:
            self.historic_data = self.historic_data[:new_max_history]
        elif current_length < new_max_history:
            additional = new_max_history - current_length
            self.historic_data.extend(
                [{"data": np.zeros(self.feature_length), "class_proba": np.zeros(self.num_classes)}
                 for _ in range(additional)]
            )

    def add_data(self, data: np.ndarray):
        """Insert new data at the beginning of the buffer."""
        self.historic_data.insert(0, {"data": data, "class_proba": np.zeros(self.num_classes)})
        self.historic_data = self.historic_data[:self.max_history]


class MelBackend:
    """
    Orchestrates the model manager and data buffer as well as classification.
    Also handles serial messages.
    """
    def __init__(self, db, logger, serial_controller, base_data: Optional[np.ndarray] = None):
        self.db = db
        self.logger = logger
        self.serial_controller = serial_controller

        # Create model manager using DB settings
        self.model_manager = MelModelManager(db, logger)

        # Set up the feature length and max history based on settings
        self.current_mel_length = self.model_manager.current_mel_length
        self.current_mel_number = self.model_manager.current_mel_number
        self.current_feature_length = self.model_manager.current_feature_length
        max_history = self.db.get_item("MEL Settings", "max_history_length").value

        # Ensure we have a valid number of classes even if no model is loaded
        self.num_classes = self.model_manager.num_classes if self.model_manager.current_model else 10

        self.data_buffer = MelDataBuffer(self.current_feature_length, self.num_classes, max_history)
        if base_data is not None and isinstance(base_data, np.ndarray):
            self.add_data(base_data)

        # Connect the serial message signal to the handler
        self.serial_controller.data_received_prefix.connect(self.prefix_message_handler)

    def add_data(self, data: np.ndarray):
        """
        Add new MEL data to the buffer (if not frozen) and classify the latest frame.
        """
        # Only update if MEL data is not frozen
        if not self.db.get_item("MEL Settings", "mel_freeze").value:
            self.data_buffer.add_data(data)

        # Run classification if a valid model is loaded
        if self.model_manager.current_model is not None:
            latest_data = self.data_buffer.historic_data[0]["data"]
            try:
                # Reshape and classify
                class_proba = self.model_manager.current_model.predict_proba(latest_data.reshape(1, -1))
                self.data_buffer.historic_data[0]["class_proba"] = class_proba[0]
            except Exception as e:
                self.logger.error(f"Error during classification: {e}")

    def prefix_message_handler(self, prefix: str, message: str):
        """
        Handle incoming serial messages, decode the data and add it to the buffer.
        """
        expected_prefix = self.db.get_item("MEL Settings", "serial_prefix").value
        if prefix == expected_prefix:
            try:
                array_hex = bytes.fromhex(message)
                # Interpret the byte data as little-endian unsigned 16-bit values
                mel_vec = np.frombuffer(array_hex, dtype=np.dtype(np.uint16).newbyteorder("<"))
                # If there is extra data (e.g. a CBC MAC), trim it off
                if len(mel_vec) > self.current_feature_length:
                    mel_vec = mel_vec[:-12]  # TODO: fix the trimming logic properly
                self.add_data(mel_vec)
            except Exception as e:
                self.logger.error(f"Error processing serial message: {e}")

# =============================================================================
# FRONTEND: THE GUI WINDOW
# =============================================================================

class GUIMELWindow(QMainWindow):
    """
    PyQt window that displays MEL data and classifier outputs.
    Uses the MelBackend to obtain and process data.
    """
    def __init__(self, db, logger, serial_controller, base_data: Optional[np.ndarray] = None):
        super().__init__()
        self.db = db
        self.logger = logger

        # Create backend instance to manage data and classification
        self.backend = MelBackend(db, logger, serial_controller, base_data)

        # Window setup
        appname = self.db.get_item('_hidden', 'appname').value
        self.setWindowTitle(f"{appname} - MEL Window")
        self.setGeometry(100, 100, 800, 600)
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Optionally add a demo/test box to spawn data manually
        self.create_demo_box()

        # Setup the UI elements and plots
        self.create_ui()

        # For FPS counter timing
        self.current_time = time.time()

    # ----------------------------
    # Frontend (UI) helper methods
    # ----------------------------

    def create_demo_box(self):
        """Creates a collapsible box with buttons to spawn demo data."""
        self.demo_box = QGroupBox("Test Box")
        self.demo_box.setCheckable(True)
        self.demo_box.setChecked(True)
        self.demo_box_layout = QVBoxLayout()
        self.demo_box.setLayout(self.demo_box_layout)
        self.demo_box.toggled.connect(
            lambda state: self.demo_box.setFixedHeight(15) if not state else self.demo_box.setFixedHeight(100)
        )
        self.main_layout.addWidget(self.demo_box)

        btn_spawn = QPushButton("Spawn Mel Data")
        btn_spawn.clicked.connect(
            lambda: self.backend.add_data(np.random.rand(self.backend.current_feature_length))
        )
        self.demo_box_layout.addWidget(btn_spawn)

        btn_spawn2 = QPushButton("Spawn Mel and Class Data")
        btn_spawn2.clicked.connect(
            lambda: self.backend.add_data(np.random.rand(self.backend.current_feature_length))
        )
        # Also update the first frame's class probabilities randomly if not already set.
        btn_spawn2.clicked.connect(
            lambda: self.backend.data_buffer.historic_data[0].update({
                "class_proba": np.random.rand(self.backend.num_classes)
                if self.backend.data_buffer.historic_data[0]["class_proba"].sum() == 0
                else self.backend.data_buffer.historic_data[0]["class_proba"]
            })
        )
        self.demo_box_layout.addWidget(btn_spawn2)

    def create_ui(self):
        """Create and layout all UI elements including plots and counters."""
        # Title label
        self.title = QLabel("MEL Window")
        self.title.setFont(QtGui.QFont("Arial", 20))
        self.main_layout.addWidget(self.title)

        # FPS counter
        self.fps_counter = QLabel("FPS: 0")
        self.main_layout.addWidget(self.fps_counter)

        # ---------------------
        # MEL Spectrogram Plot
        # ---------------------
        self.fig_mel = Figure(figsize=(8, 6))
        self.canvas_mel = FigureCanvasQTAgg(self.fig_mel)
        self.main_layout.addWidget(self.canvas_mel)
        self.fig_mel.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
        self.fig_mel.tight_layout(pad=0.5)
        self.mel_ax = self.fig_mel.add_subplot(111)

        # A rectangle overlay on the MEL plot
        self.mel_rect = Rectangle((-0.625, -0.025), 1.05, 1.05,
                                  linewidth=1, edgecolor='red', facecolor='none')

        # The number of bins for the spectrogram is determined by the max history setting.
        max_history = self.db.get_item("MEL Settings", "max_history_length").value
        self.setup_mel_plots(max_history)

        # --------------------------
        # Classifier and History Plots
        # --------------------------
        self.classifier_layout = QHBoxLayout()

        # Classifier probability bar chart
        self.fig_classifier = Figure(figsize=(6, 6))
        self.canvas_classifier = FigureCanvasQTAgg(self.fig_classifier)
        self.classifier_layout.addWidget(self.canvas_classifier)

        # History plot (probability vs. time frames)
        self.fig_class_history = Figure(figsize=(8, 6))
        self.canvas_class_history = FigureCanvasQTAgg(self.fig_class_history)
        self.classifier_layout.addWidget(self.canvas_class_history)
        self.main_layout.addLayout(self.classifier_layout)

        self.class_ax = self.fig_classifier.add_subplot(111)
        self.hist_ax = self.fig_class_history.add_subplot(111)

        self.setup_classifier_plot()
        self.setup_history_plot()

        # ---------------------
        # Animations for plots
        # ---------------------
        TARGET_FPS = self.db.get_item("Plot Settings", "framerate").value
        interval_ms = 1000 / TARGET_FPS
        self.anim_mel = FuncAnimation(
            self.fig_mel,
            self._update_mel_plot,
            init_func=self._init_mel_plot,
            interval=interval_ms,
            blit=True,
            save_count=1
        )
        self.anim_class = FuncAnimation(
            self.fig_classifier,
            self._update_class_plot,
            init_func=self._init_class_plot,
            interval=interval_ms,
            blit=True,
            save_count=1
        )
        self.anim_hist_class = FuncAnimation(
            self.fig_class_history,
            self._update_hist_class_plot,
            init_func=self._init_hist_class_plot,
            interval=interval_ms,
            blit=True,
            save_count=1
        )

        # Update the MEL plot if max history changes (assumes your db item supports callbacks)
        self.db.get_item("MEL Settings", "max_history_length").register_callback(
            lambda val: self.setup_mel_plots(val)
        )

    # ---------------------
    # MEL Plot Methods
    # ---------------------
    def setup_mel_plots(self, number_of_bins: int):
        """Setup the MEL spectrogram plot with a given number of bins (history frames)."""
        self.mel_pcolors = []
        self.mel_ax.clear()
        self.mel_ax.set_title("MEL Spectrogram")
        self.mel_ax.set_xlabel("Time Frames")
        self.mel_ax.set_ylabel("Mel Frequency Bins")
        self.mel_ax.set_xlim(-number_of_bins * 1.1 + 0.4, 0.1 + 0.5)
        self.mel_ax.set_ylim(-0.05, 1.05)
        self.mel_ax.autoscale(enable=False, axis="both")
        self.mel_ax.set_xticks(np.arange(-number_of_bins, 1, 1))

        # Create a pcolormesh for each history bin
        for i in range(number_of_bins):
            offset = -1.1
            X, Y = np.meshgrid(
                np.linspace(0, 1, self.backend.current_mel_number),
                np.linspace(0, 1, self.backend.current_mel_length)
            )
            image = self.mel_ax.pcolormesh(
                X + i * offset - 1.1 + 0.5,
                Y,
                np.zeros((self.backend.current_mel_length, self.backend.current_mel_number)),
                vmin=0,
                vmax=(2 ** 16),
                cmap='viridis',
                shading='auto'  # Avoid gridlines
            )
            self.mel_pcolors.append(image)

        self.mel_ax.add_patch(self.mel_rect)

    def _init_mel_plot(self):
        """Initialize the MEL plot for blitting."""
        for image in self.mel_pcolors:
            image.set_array(np.zeros(self.backend.current_feature_length).ravel())
        return self.mel_pcolors + [self.mel_rect]

    def _update_mel_plot(self, frame):
        """Update the MEL spectrogram with the latest buffered data."""
        for i, image in enumerate(self.mel_pcolors):
            if i < len(self.backend.data_buffer.historic_data):
                data = self.backend.data_buffer.historic_data[i]["data"]
            else:
                data = np.zeros(self.backend.current_feature_length)
            reshaped = data.reshape(self.backend.current_mel_length, self.backend.current_mel_number).T
            image.set_array(reshaped.ravel())

        # Update FPS counter
        now = time.time()
        fps = 1 / max(now - self.current_time, 1e-16)
        self.current_time = now
        self.fps_counter.setText(f"FPS: {fps:.2f}")

        return self.mel_pcolors + [self.mel_rect]

    # ---------------------------
    # Classifier Plot Methods
    # ---------------------------
    def setup_classifier_plot(self):
        """Set up the bar chart that displays classifier probabilities."""
        self.class_ax.set_title("Classifier Probabilities")
        self.class_ax.set_xlabel("Classes")
        self.class_ax.set_ylabel("Probability")
        self.class_ax.set_xlim(-0.5, self.backend.num_classes - 0.5)
        self.class_ax.set_ylim(-0.05, 1.05)
        self.class_ax.autoscale(enable=False, axis="both")
        # Use model classes if available; otherwise, use defaults.
        self.classes = (self.backend.model_manager.classes
                        if self.backend.model_manager.current_model
                        else [f"Class {i}" for i in range(self.backend.num_classes)])
        self.class_histogram = self.class_ax.hist(
            self.classes,
            bins=self.backend.num_classes,
            weights=np.zeros(self.backend.num_classes),
            align='mid',
            rwidth=0.5,
            color='blue',
        )
        self.class_ax.set_xticklabels(self.classes, rotation=45)
        self.fig_classifier.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)

    def _init_class_plot(self):
        """Initialize the classifier bar chart for blitting."""
        return (self.class_histogram[2][0],)

    def _update_class_plot(self, frame):
        """Update the classifier bar chart using the latest classification probabilities."""
        if len(self.backend.data_buffer.historic_data) > 0:
            class_proba = self.backend.data_buffer.historic_data[0]["class_proba"]
        else:
            class_proba = np.zeros(self.backend.num_classes)

        # Update each bar’s height and color
        for rect, h in zip(self.class_histogram[2], class_proba):
            rect.set_height(h)
        max_class = np.argmax(class_proba)
        for i, rect in enumerate(self.class_histogram[2]):
            rect.set_color('red' if i == max_class else 'blue')
        return self.class_histogram[2]

    # ---------------------------
    # History Plot Methods
    # ---------------------------
    def setup_history_plot(self):
        """Set up the line plots that show classifier probability history."""
        self.hist_ax.set_title("Classifier History")
        self.hist_ax.set_xlabel("Time Frames")
        self.hist_ax.set_ylabel("Probability")
        self.hist_ax.set_xlim(-9, 0)
        self.hist_ax.set_ylim(-0.05, 1.45)
        self.hist_ax.autoscale(enable=False, axis="both")
        self.hist_lines = []
        for i in range(self.backend.num_classes):
            label = (self.backend.model_manager.classes[i]
                     if self.backend.model_manager.current_model
                     else f"Class {i}")
            line, = self.hist_ax.plot([], [], animated=True, label=label)
            self.hist_lines.append(line)
        self.hist_ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        self.fig_class_history.subplots_adjust(left=0.15, right=0.75, top=0.9, bottom=0.2)

    def _init_hist_class_plot(self):
        """Initialize the history plot for blitting."""
        for line in self.hist_lines:
            line.set_data([], [])
        return self.hist_lines

    def _update_hist_class_plot(self, frame):
        """Update the history plot with the latest classifier probabilities over time."""
        for i, line in enumerate(self.hist_lines):
            # Create x values from negative indices (latest frame is at index 0)
            data_points = [d["class_proba"][i] for d in self.backend.data_buffer.historic_data]
            line.set_data(-np.arange(len(data_points)), data_points)
        return self.hist_lines

# =============================================================================
# MAIN FUNCTION
# =============================================================================

import databaseV2_for_V4 as dbu
import loggingUtils as logu
import serialUtils as seru
import pathlib as pathl



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
    comports = []
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
    db.add_item("Classifier Settings", "model_path", db.File("Model Path", base_path.parent/"mcu"/ "model.pickle", "The path to the model file"))
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

def main():
    """Main function to run the MEL window."""
    import sys
    from PyQt5.QtWidgets import QApplication

    # Create the application
    app = QApplication(sys.argv)

    # Create the logger
    logger = logu.ContentLogger("MEL Window", "", False)
    tru_log = logger.logger

    # Create the database
    db = dbu.ContentDatabase(database_init, tru_log,  False)

    # Create the serial controller
    serial_controller = seru.SerialController(tru_log)

    # Create the window
    window = GUIMELWindow(db, tru_log, serial_controller)

    # Show the window
    window.show()

    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
