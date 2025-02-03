# Writen by Group E 2024-2025
# For the course LELEC2102/3

# Standard library imports
import logging
import os
import sys
from shutil import rmtree
import pathlib as pathl
import datetime
from threading import Lock
from typing import Optional
import time
from typing import Any, Optional, Dict, List, Type, Callable, Literal
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Third party imports
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

# Local application imports
from databaseV3 import *
import databaseV3_initialization as db_init
from loggingUtils import ContentLogger
from serialUtils import SerialController

###############
## Constants ##
###############

# TODO : Add the constants here

##############################
## Structure Syncronization ##
##############################

@dataclass
class AppClassElements:
    """Class to store the different classes that all windows and threads need to have access to"""
    database: ContentDatabase
    logger: logging.Logger
    logging_controller: ContentLogger
    serial_controller: SerialController

@dataclass
class AppWindowElements:
    """Class to store the different windows that all windows so we can access them and remove them"""
    main_windows: Dict[str, QMainWindow]
    parameter_windows: Dict[str, QMainWindow]
    audio_windows: Dict[str, QMainWindow]
    mel_windows: Dict[str, QMainWindow]
    class_sync_elem: AppClassElements

class AppElements:
    """Class to store the different windows and classes that all windows and threads need to have access to"""
    windows: AppWindowElements
    classes: AppClassElements

    def __init__(self):
        self.windows = AppWindowElements(
            main_windows={},
            parameter_windows={},
            audio_windows={},
            mel_windows={},
            class_sync_elem=self.classes
        )
        self.classes = AppClassElements(
            database=None,
            logger=None,
            logging_controller=None,
            serial_controller=None
        )

    def remove_window(self, window_type: Literal["main", "parameter", "audio", "mel"], window_id: str):
        """Remove a window from the sync"""
        if window_type == "main":
            self.windows.main_windows.pop(window_id)
        elif window_type == "parameter":
            self.windows.parameter_windows.pop(window_id)
        elif window_type == "audio":
            self.windows.audio_windows.pop(window_id)
        elif window_type == "mel":
            self.windows.mel_windows.pop(window_id)
        else:
            raise ValueError(f"Unknown window type {window_type}")
        
    def add_window(self, window_type: Literal["main", "parameter", "audio", "mel"], window_id: str, window: QMainWindow):
        """Add a window to the sync"""
        if window_type == "main":
            self.windows.main_windows[window_id] = window
        elif window_type == "parameter":
            self.windows.parameter_windows[window_id] = window
        elif window_type == "audio":
            self.windows.audio_windows[window_id] = window
        elif window_type == "mel":
            self.windows.mel_windows[window_id] = window
        else:
            raise ValueError(f"Unknown window type {window_type}")
    
    def get_window(self, window_type: Literal["main", "parameter", "audio", "mel"], window_id: str) -> Optional[QMainWindow]:
        """Get a window from the sync"""
        if window_type == "main":
            return self.windows.main_windows.get(window_id)
        elif window_type == "parameter":
            return self.windows.parameter_windows.get(window_id)
        elif window_type == "audio":
            return self.windows.audio_windows.get(window_id)
        elif window_type == "mel":
            return self.windows.mel_windows.get(window_id)
        else:
            raise ValueError(f"Unknown window type {window_type}")
        
###################
## Audio Window  ##
###################

# TODO : Add the audio window here

#################
## Mel Window  ##
#################

# TODO : Add the mel window here

class GUI_MEL_Window(QMainWindow):
    """
    Class to create the MEL window
    """
    def __init__(self, data_struct: AppElements, window_id: str):
        super().__init__()
        self.data_struct = data_struct
        self.window_id = window_id
        self.initUI()


##################
## Main Program ##
##################

if "__main__" == __name__:
    # Set up matplotlib
    plt.style.use("fast")
    matplotlib.use("Qt5Agg")

    # Create the syncronization structure
    app_elements = AppElements()

    # Add the logger
    app_elements.classes.logging_controller = ContentLogger(
        name=__name__,
        file_path="uart_logs.log", # TODO : Change the file path
        use_file=True,
    )
    app_elements.classes.logger = app_elements.classes.logging_controller.logger
    logging.debug("Logger initialized")

    # Add the database
    app_elements.classes.database = db_init.generate_database()
    logging.debug("Database initialized")

    # Add the serial controller
    app_elements.classes.serial_controller = SerialController(app_elements.classes.logger)
    logging.debug("Serial controller initialized")

    # Spawn the TEMP application
    app = QApplication(sys.argv)
    window = app_elements.classes.database.open_parameter_window("window 1")
    app_elements.add_window("parameter", "window 1", window)
    window.show()
    sys.exit(app.exec())

