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
from databaseStruct import *
import database_initialization as db_init
import loggingUtils
import serialUtils

##################
## 1. Constants ##
##################

# TODO : Add the constants here




##################
## Main Program ##
##################

if "__main__" == __name__:
    # Set up matplotlib
    plt.style.use("fast")
    matplotlib.use("Qt5Agg")

    # Set up logging
    contentLogger = loggingUtils.ContentLogger(__name__, 'app_logs.log', True)
    
    # Setup the database
    database = db_init.generate_database()
    logging.debug("Database initialized")

    # Spawn the TEMP application
    app = QApplication(sys.argv)
    window = database.open_parameter_window("window 1")
    window.show()
    sys.exit(app.exec())

