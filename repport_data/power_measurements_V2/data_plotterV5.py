import json
import sys
import csv
import os
import pandas as pd
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import numpy as np
import plotly.graph_objects as go
from PyQt6.QtCore import QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QGroupBox, QVBoxLayout, QListWidget, QToolBar, QFormLayout, QSpinBox, QDoubleSpinBox

import librosa


# CONSTANTS



# GLOBAL VARIABLES
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "\\"
PLOTS_FOLDER   = os.path.join(os.getcwd(), "Plots")
POWER_FORMULAS = {
    "P=CH1*(CH1-CH2)/R": lambda ch1, ch2, r: ch1 * (ch1 - ch2) / r,
    "P=CH1*CH2/R": lambda ch1, ch2, r: ch1 * ch2 / r,
    "P=CH1*CH2": lambda ch1, ch2, r: ch1 * ch2,
    "P=CH1^2/R": lambda ch1, ch2, r: ch1**2 / r,
    "P=CH1^2": lambda ch1, ch2, r: ch1**2,
    "P=CH1": lambda ch1, ch2, r: ch1,
}

@dataclass
class ChannelMetadata:
    name: str
    probe_attenuation: float
    voltage_per_adc: float
    time_interval: float
    pk_pk: float
    frequency: Optional[float] = None
    period: Optional[float] = None

class OscilloscopeCSVProcessor:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.metadata: Dict[str, ChannelMetadata] = {}
        self.data = None
        self.time = None
        self._process_file()

    def _extract_value(self, text: str) -> float:
        """Extract numerical value from text with units"""
        multipliers = {
            'u': 1e-6,
            'm': 1e-3,
            'k': 1e3,
            'M': 1e6
        }
        
        match = re.match(r'([-+]?\d*\.?\d+)([umkM])?([VHz])?', text)
        if match:
            value, unit_prefix, _ = match.groups()
            value = float(value)
            if unit_prefix:
                value *= multipliers[unit_prefix]
            return value
        return float(text) if text.replace('.','').isdigit() else None

    def _parse_metadata(self, header_lines: list) -> Dict[str, ChannelMetadata]:
        """Parse header metadata for each channel"""
        channels = {}
        current_channels = header_lines[0].split(',')[1:]
        
        for line in header_lines[1:7]:  # Process metadata rows
            key, *values = line.strip().split(',')
            key = key.strip(' :')
            
            for ch_name, value in zip(current_channels, values):
                if ch_name not in channels:
                    channels[ch_name] = {}
                
                processed_value = self._extract_value(value) if value != '?' else None
                channels[ch_name][key.lower().replace(' ', '_')] = processed_value

        # Create ChannelMetadata objects
        return {
            ch_name: ChannelMetadata(
                name=ch_name,
                probe_attenuation=ch_data['probe_attenuation'],
                voltage_per_adc=ch_data['voltage_per_adc'],
                time_interval=ch_data['time_interval'],
                pk_pk=ch_data['pk-pk'],
                frequency=ch_data['frequency'],
                period=ch_data['period']
            ) for ch_name, ch_data in channels.items()
        }

    def _process_file(self):
        """Process the CSV file and extract data"""
        with open(self.file_path, 'r') as f:
            header_lines = []
            for _ in range(7):
                header_lines.append(f.readline().strip())
            
            self.metadata = self._parse_metadata(header_lines)
            
            # Read the actual data
            df = pd.read_csv(self.file_path, skiprows=8)
            self.data = df
            self.time = np.arange(len(df)) * list(self.metadata.values())[0].time_interval

    def get_channel_data(self, channel: str) -> Tuple[np.ndarray, np.ndarray]:
        """Get processed data for a specific channel"""
        if channel not in self.metadata:
            raise ValueError(f"Channel {channel} not found in data")
        
        voltage_data = self.data[f"{channel}_Voltage(mV)"].values * 1e-3  # Convert to V
        return self.time, voltage_data

    def to_signal(self, channel: str, plots_folder: str) -> 'Signal':
        """Convert channel data to Signal class instance"""
        from data_plotterV5 import Signal  # Import here to avoid circular imports
        
        time, voltage = self.get_channel_data(channel)
        return Signal(signal=voltage, time=time, plots_folder=plots_folder)

    @property
    def available_channels(self) -> list:
        """List available channels"""
        return list(self.metadata.keys())

    def get_metadata(self, channel: str) -> ChannelMetadata:
        """Get metadata for specific channel"""
        return self.metadata[channel]

class Signal:
    def __init__(self, signal: np.array, time: np.array, plots_folder: str):
        self.signal = signal
        self.time = time
        self.plots_folder = plots_folder
        self.get_spectrograms()

    # Save the processed data
    def __save_plot_format(self, fig, name, format="png"):
        fig.write_image(os.path.join(self.plots_folder, format, name + "." + format))

    def save_plot(self, fig, name):
        os.makedirs(os.path.join(self.plots_folder, "png"), exist_ok=True)
        os.makedirs(os.path.join(self.plots_folder, "pdf"), exist_ok=True)
        
        self.__save_plot_format(fig, name, "png")
        self.__save_plot_format(fig, name, "pdf")

    def __dict__(self):
        return {
            "signal": self.signal,
            "time": self.time,
            "fft": self.fft,
            "melspectrogram": self.melspectrogram,
            "spectrogram": self.spectrogram
        }

    def save_waveform(self, name):
        os.makedirs(os.path.join(self.plots_folder, "waveforms"), exist_ok=True)
        np.save(os.path.join(self.plots_folder, "waveforms", name + ".npy"), {"signal": self.signal, "time": self.time})

    # Spectrograms
    def __get_fft(self):
        self.fft = np.fft.fft(self.signal)
    
    def __get_melspectrogram(self):
        self.melspectrogram = librosa.feature.melspectrogram(y=self.signal, sr=1/(self.time[1] - self.time[0]))
    
    def __get_spectrogram(self):
        self.spectrogram = np.abs(librosa.stft(self.signal))

    def get_spectrograms(self):
        self.__get_fft()
        self.__get_melspectrogram()
        self.__get_spectrogram()

    # Signal processing
    def trimming_function(self, start_trim: int = 0, end_trim: int = 0):
        self.signal = self.signal[start_trim:-end_trim]
        self.time = self.time[start_trim:-end_trim]

    def moving_average(self, window_size: int = 1):
        self.signal = np.convolve(self.signal, np.ones(window_size), 'valid') / window_size

    def offset_correction(self, voltage_offset: float = 0.0, time_offset: float = 0.0):
        self.signal -= voltage_offset
        self.time -= time_offset

    def scale_correction(self, voltage_scale: float = 1.0, time_scale: float = 1.0):
        self.signal *= voltage_scale
        self.time *= time_scale

    def process_signal(self, start_trim: int = 0, end_trim: int = 0, window_size: int = 1, voltage_offset: float = 0.0, time_offset: float = 0.0, voltage_scale: float = 1.0, time_scale: float = 1.0):
        self.trimming_function(start_trim, end_trim)
        self.offset_correction(voltage_offset, time_offset)
        self.scale_correction(voltage_scale, time_scale)
        self.moving_average(window_size)
        # Update the spectrograms
        self.get_spectrograms()

def signals_to_power(signal1: Signal, signal2: Signal, resistance: float, formula: str, invert_channels: bool = False, invert_result: bool = False):
    if invert_channels:
        signal1, signal2 = signal2, signal1
    power = POWER_FORMULAS[formula](signal1.signal, signal2.signal, resistance)
    if invert_result:
        power = -power
    return power

def read_csv_hantek(file_path: str):
    def process_header(name:str):
        return name.replace("(", "").replace(")", "").replace("/", "_per_").replace(":", "").replace("=", "").replace("?", "").replace("!", "").replace(";", "").replace(",", "").replace(".", "").replace("'", "").trim().replace(" ", "_").lower()
    with open(file_path) as file:
        reader = csv.reader(file)
        header = {}
        data = []
        found_data = False
        for i, row in enumerate(reader):
            if row[0] == "index":
                found_data = True
            else:
                if not found_data:
                    header[process_header(row[0])] = row[1]
                else:
                    data.append(row)
    time_array = np.array([float(row[0]) for row in data])
    data_array = np.array([[float(row[i]) for i in range(1, len(row))] for row in data[1:]])
    time_array *= header["time_interval"]

    signal = Signal(np.array(data[1:]), np.array(data[0]), PLOTS_FOLDER)



# Application
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Plotter")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.signals = []
        self.signals_list = QListWidget()
        self.signals_list.itemClicked.connect(self.signal_selected)
        self.layout.addWidget(self.signals_list)

        self.toolbar = QToolBar()
        self.layout.addWidget(self.toolbar)

        self.plot_view = QWebEngineView()
        self.layout.addWidget(self.plot_view)

        self.signal_selected()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())