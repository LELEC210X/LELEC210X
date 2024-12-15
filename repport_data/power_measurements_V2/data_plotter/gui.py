# gui.py
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPen  # Add missing imports
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Optional, Dict
import sys
import os
import numpy as np
from pathlib import Path
import logging
from data_types import SignalData
from csv_processor import OscilloscopeCSVProcessor
from signal_processor import SignalProcessor
from datetime import datetime
from plot_manager import PlotManager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from dataclasses import dataclass

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

class FileLoader(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, files):
        super().__init__()
        self.files = files

    def run(self):
        results = {}
        for i, file in enumerate(self.files):
            try:
                processor = OscilloscopeCSVProcessor(Path(file))
                results[Path(file).name] = processor.signals
                self.progress.emit(int((i + 1) / len(self.files) * 100))
            except Exception as e:
                self.error.emit(f"Error loading {file}: {str(e)}")
        self.finished.emit(results)

# Update SignalSettings class
class SignalSettings:
    def __init__(self):
        self.start_trim = 0.0  # As percentage
        self.end_trim = 100.0  # As percentage
        self.smoothing = 1
        self.time_offset = 0.0
        self.voltage_offsets = {"CH1": 0.0, "CH2": 0.0}  # Per-channel offsets

class SignalViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal Viewer")
        self.setMinimumSize(1200, 800)  # Set minimum window size
        self.signals: Dict[str, SignalData] = {}
        self.loaded_files: Dict[str, Dict[str, SignalData]] = {}
        self.plot_manager = PlotManager()
        self.signal_settings: Dict[str, SignalSettings] = {}
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Left panel (File selection) - 20% width
        left_panel = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMinimumWidth(250)
        
        # File controls
        file_group = QGroupBox("Files")
        file_layout = QVBoxLayout()
        
        # File control buttons
        button_layout = QHBoxLayout()
        load_btn = QPushButton("Load Files")
        load_btn.clicked.connect(self.load_files)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_files)
        deselect_btn = QPushButton("Deselect All")
        deselect_btn.clicked.connect(self.deselect_all_files)
        
        button_layout.addWidget(load_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(deselect_btn)
        
        # Add save plot buttons
        save_btns_layout = QHBoxLayout()
        save_voltage_btn = QPushButton("Save Voltage Plot")
        save_power_btn = QPushButton("Save Power Plot")
        save_both_btn = QPushButton("Save Both Plots")
        
        save_voltage_btn.clicked.connect(lambda: self.export_plot('voltage'))
        save_power_btn.clicked.connect(lambda: self.export_plot('power'))
        save_both_btn.clicked.connect(lambda: self.export_plot('both'))
        
        save_btns_layout.addWidget(save_voltage_btn)
        save_btns_layout.addWidget(save_power_btn)
        save_btns_layout.addWidget(save_both_btn)
        
        file_layout.addLayout(save_btns_layout)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.file_list.itemSelectionChanged.connect(self.update_selected_signals)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Aspect ratio selector
        aspect_layout = QHBoxLayout()
        aspect_layout.addWidget(QLabel("Aspect Ratio:"))
        self.aspect_ratio = QComboBox()
        self.aspect_ratios = {
            "16:9": (1920, 1080),
            "4:3": (1600, 1200),
            "1:1": (1500, 1500),
            "3:2": (1800, 1200),
            "2:1": (2000, 1000),
            "21:9": (2560, 1080)
        }
        self.aspect_ratio.addItems(self.aspect_ratios.keys())
        self.aspect_ratio.setCurrentText("16:9")
        self.aspect_ratio.currentTextChanged.connect(self.update_plots)
        aspect_layout.addWidget(self.aspect_ratio)
        
        # Add everything to file layout
        file_layout.addLayout(button_layout)
        file_layout.addWidget(self.file_list)
        file_layout.addWidget(self.progress_bar)
        file_layout.addLayout(aspect_layout)
        file_group.setLayout(file_layout)
        
        # Add file group to left panel
        left_panel.addWidget(file_group)
        
        # Add power calculation controls
        power_group = QGroupBox("Power Calculation")
        power_layout = QFormLayout()
        
        # Power formula selector
        self.power_combo = QComboBox()
        self.power_combo.addItems([
            "P=CH1*CH2",
            "P=CH1*(CH1-CH2)/R",
            "P=CH1*CH2/R",
            "P=CH1^2/R",
            "P=CH1^2"
        ])
        power_layout.addRow("Formula:", self.power_combo)
        
        # Resistance input
        self.resistance = QDoubleSpinBox()
        self.resistance.setRange(0.001, 1e6)  # 1mΩ to 1MΩ
        self.resistance.setDecimals(3)
        self.resistance.setValue(1.0)
        self.resistance.setSuffix(" Ω")
        self.resistance.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        power_layout.addRow("Resistance:", self.resistance)
        
        # Add power flip checkbox
        self.power_flip = QCheckBox("Invert Power")
        self.power_flip.stateChanged.connect(self.update_plots)
        power_layout.addRow("", self.power_flip)
        
        power_group.setLayout(power_layout)
        
        # Add power group to left panel after file group
        left_panel.addWidget(power_group)
        
        # Middle panel (Plots) - 60% width
        plot_panel = QVBoxLayout()
        plot_widget = QWidget()
        plot_widget.setLayout(plot_panel)
        
        # Initialize plot containers with layouts
        self.voltage_plot_container = QWidget()
        voltage_layout = QVBoxLayout(self.voltage_plot_container)
        self.voltage_plot_container.setLayout(voltage_layout)
        
        self.power_plot_container = QWidget()
        power_layout = QVBoxLayout(self.power_plot_container)
        self.power_plot_container.setLayout(power_layout)
        
        plot_panel.addWidget(self.voltage_plot_container)
        plot_panel.addWidget(self.power_plot_container)
        plot_widget.setMinimumWidth(600)
        
        # Right panel (Settings) - 25% width
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setMinimumWidth(300)  # Increased width
        
        # Signal settings scroll area with compact style
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.settings_widget = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_widget)
        self.settings_layout.setSpacing(5)  # Reduce spacing
        self.settings_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        scroll.setWidget(self.settings_widget)
        right_layout.addWidget(scroll)

        # Add all panels to main layout with proper stretching
        layout.addWidget(left_widget, stretch=2)
        layout.addWidget(plot_widget, stretch=5)
        layout.addWidget(right_panel, stretch=3)

    def load_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select CSV Files",
            "",
            "CSV Files (*.csv)"
        )
        
        if files:
            self.progress_bar.setVisible(True)
            self.file_list.clear()  # Clear existing items
            for file in files:
                self.file_list.addItem(Path(file).name)
            
            self.loader = FileLoader(files)
            self.loader.progress.connect(self.update_progress)
            self.loader.finished.connect(self.on_files_loaded)
            self.loader.error.connect(self.show_error)
            self.loader.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_files_loaded(self, results):
        self.loaded_files = results  # Store all loaded files
        self.update_selected_signals()  # Update signals based on selection
        self.update_settings_panel()
        self.progress_bar.setVisible(False)

    def update_selected_signals(self):
        """Update signals based on selected files in list"""
        self.signals.clear()  # Clear current signals
        
        # Get selected items
        selected_items = [item.text() for item in self.file_list.selectedItems()]
        
        # If nothing selected, select all
        if not selected_items:
            selected_items = [self.file_list.item(i).text() 
                            for i in range(self.file_list.count())]
        
        # Update signals with selected files
        for filename in selected_items:
            if filename in self.loaded_files:
                self.signals[filename] = self.loaded_files[filename]
        
        self.update_plots()

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    # Update signal processing in update_plots method
    def update_plots(self):
        if not self.signals:
            return
            
        try:
            display_signals = {}
            for filename, channels in self.signals.items():
                display_signals[filename] = {}
                settings = self.signal_settings.get(filename, SignalSettings())
                
                for channel_name, signal in channels.items():
                    # 1. Create fresh copy with ALIGNED time and signal arrays
                    time = signal.time.copy()
                    processed_signal = signal.raw_signal.copy()
                    
                    # Ensure arrays have same length
                    min_len = min(len(time), len(processed_signal))
                    time = time[:min_len]
                    processed_signal = processed_signal[:min_len]
                    
                    # 2. Apply voltage offset
                    voltage_offset = settings.voltage_offsets.get(channel_name, 0.0)
                    processed_signal -= voltage_offset
                    
                    # 3. Apply smoothing
                    if settings.smoothing > 1:
                        window_size = min(settings.smoothing, len(processed_signal))
                        if window_size > 1:
                            window = np.ones(window_size) / window_size
                            processed_signal = np.convolve(processed_signal, window, mode='same')
                            
                    # 4. Apply trimming 
                    total_points = len(processed_signal)
                    start_idx = int((settings.start_trim / 100.0) * total_points)
                    end_idx = int((settings.end_trim / 100.0) * total_points)
                    
                    if start_idx >= end_idx or start_idx >= total_points:
                        start_idx = 0
                        end_idx = total_points
                    
                    # Keep trimmed arrays aligned
                    processed_signal = processed_signal[start_idx:end_idx]
                    time = time[start_idx:end_idx]

                    # 5. Apply time offset
                    if len(time) > 0:  # Check if arrays not empty
                        time = time - time[0] + settings.time_offset
                        
                        # 6. Create new SignalData with processed arrays
                        display_signal = SignalData(
                            raw_signal=signal.raw_signal,
                            time=time,
                            metadata=signal.metadata,
                            processed_signal=processed_signal
                        )
                        
                        display_signals[filename][channel_name] = display_signal

            if display_signals:
                self._update_plot_widgets(display_signals)
                
        except Exception as e:
            logger.error(f"Error updating plots: {str(e)}", exc_info=True)
            self.show_error(f"Error updating plots: {str(e)}")

    def _update_plot_widgets(self, display_signals):
        """Update plot widgets with processed display signals"""
        # Clear existing plots
        for item in self.voltage_plot_container.findChildren(FigureCanvasQTAgg):
            item.deleteLater()
        for item in self.power_plot_container.findChildren(FigureCanvasQTAgg):
            item.deleteLater()
            
        # Create new plots using display signals
        target_ratio = self.aspect_ratios[self.aspect_ratio.currentText()]
        v_width = self.voltage_plot_container.width()
        v_height = self.voltage_plot_container.height()
        plot_width, plot_height = self.plot_manager.calculate_plot_dimensions(
            v_width, v_height, target_ratio)
            
        voltage_canvas = self.plot_manager.create_voltage_plot(
            display_signals, plot_width, plot_height)
        power_canvas = self.plot_manager.create_power_plot(
            display_signals, self.calculate_power, plot_width, plot_height)
            
        self.voltage_plot_container.layout().addWidget(voltage_canvas)
        self.power_plot_container.layout().addWidget(power_canvas)

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.update_plots()

    def calculate_power(self, ch1: SignalData, ch2: SignalData) -> np.ndarray:
        """Calculate power based on selected formula and resistance"""
        formula = self.power_combo.currentText()
        r = self.resistance.value()
        
        try:
            if formula == "P=CH1*CH2":
                power = ch1.processed_signal * ch2.processed_signal
            elif formula == "P=CH1*(CH1-CH2)/R":
                power = ch1.processed_signal * (ch1.processed_signal - ch2.processed_signal) / r
            elif formula == "P=CH1*CH2/R":
                power = ch1.processed_signal * ch2.processed_signal / r
            elif formula == "P=CH1^2/R":
                power = ch1.processed_signal ** 2 / r
            elif formula == "P=CH1^2":
                power = ch1.processed_signal ** 2
            else:
                logger.error(f"Unknown power formula: {formula}")
                return np.zeros_like(ch1.processed_signal)
            
            # Apply power flip if enabled
            if self.power_flip.isChecked():
                power = -power
                
            return power
                
        except Exception as e:
            logger.error(f"Error calculating power: {str(e)}")
            return np.zeros_like(ch1.processed_signal)

    def refresh_files(self):
        """Refresh file list with CSVs in current directory"""
        self.file_list.clear()
        current_dir = Path.cwd()
        csv_files = list(current_dir.glob("*.csv"))
        
        for file in csv_files:
            self.file_list.addItem(file.name)

    def showEvent(self, event):
        """Override showEvent to refresh files when window opens"""
        super().showEvent(event)
        self.refresh_files()

    def deselect_all_files(self):
        """Deselect all files in the list"""
        self.file_list.clearSelection()
        self.update_selected_signals()

    def create_plot_layout(self, title: str, y_axis_title: str) -> dict:
        """Create common layout settings for plots"""
        # Get current aspect ratio dimensions
        width, height = self.aspect_ratios[self.aspect_ratio.currentText()]
        
        return {
            'title': {
                'text': title,
                'font': {'size': 24, 'family': 'Arial'},
                'x': 0.5,
                'xanchor': 'center'
            },
            'xaxis': {
                'title': 'Time (s)',
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'lightgray',
                'titlefont': {'size': 20, 'family': 'Arial'},
                'tickfont': {'size': 16}
            },
            'yaxis': {
                'title': y_axis_title,
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'lightgray',
                'titlefont': {'size': 20, 'family': 'Arial'},
                'tickfont': {'size': 16}
            },
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'width': width,
            'height': height,
            'margin': {'l': 80, 'r': 20, 't': 60, 'b': 60},
            'showlegend': True,
            'legend': {
                'x': 1.02,
                'y': 0.98,
                'xanchor': 'left',
                'yanchor': 'top',
                'bgcolor': 'rgba(255,255,255,0.8)',
                'bordercolor': 'lightgray',
                'borderwidth': 1,
                'font': {'size': 14, 'family': 'Arial'}
            }
        }

    def create_voltage_plot(self) -> go.Figure:
        """Create voltage plot figure"""
        # Scientific color palette
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        fig = make_subplots(rows=1, cols=1)
        
        for i, (filename, channels) in enumerate(self.signals.items()):
            for channel_name, signal in channels.items():
                fig.add_trace(
                    go.Scatter(
                        x=signal.time,
                        y=signal.processed_signal,
                        name=f"{filename} - {channel_name}",
                        line={'color': colors[i % len(colors)], 'width': 2},
                        opacity=0.8
                    )
                )
        
        fig.update_layout(
            **self.create_plot_layout("Voltage Signals", "Voltage (V)")
        )
        return fig

    def create_power_plot(self) -> go.Figure:
        """Create power plot figure"""
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        fig = make_subplots(rows=1, cols=1)
        
        for i, (filename, channels) in enumerate(self.signals.items()):
            if "CH1" in channels and "CH2" in channels:
                power = self.calculate_power(channels["CH1"], channels["CH2"])
                fig.add_trace(
                    go.Scatter(
                        x=channels["CH1"].time,
                        y=power,
                        name=f"{filename} - Power",
                        line={'color': colors[i % len(colors)], 'width': 2},
                        opacity=0.8
                    )
                )
        
        fig.update_layout(
            **self.create_plot_layout("Power", "Power (W)")
        )
        return fig

    def export_plot(self, plot_type: str):
        """Export plots to PDF and PNG"""
        if not self.signals:
            QMessageBox.warning(self, "Warning", "No data to export!")
            return
            
        try:
            save_dir = QFileDialog.getExistingDirectory(
                self, "Select Export Directory", "",
                QFileDialog.Option.ShowDirsOnly
            )
            
            if save_dir:
                save_dir = Path(save_dir)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                width, height = self.aspect_ratios[self.aspect_ratio.currentText()]
                
                if plot_type in ['voltage', 'both']:
                    canvas = self.plot_manager.create_voltage_plot(
                        self.signals, width, height, for_export=True)
                    canvas.figure.savefig(
                        save_dir / f"voltage_plot_{timestamp}.png", 
                        dpi=300, bbox_inches='tight', pad_inches=0.1)
                    canvas.figure.savefig(
                        save_dir / f"voltage_plot_{timestamp}.pdf",
                        bbox_inches='tight', pad_inches=0.1)
                    
                if plot_type in ['power', 'both']:
                    canvas = self.plot_manager.create_power_plot(
                        self.signals, self.calculate_power, width, height)
                    canvas.figure.savefig(
                        save_dir / f"power_plot_{timestamp}.png", dpi=300)
                    canvas.figure.savefig(
                        save_dir / f"power_plot_{timestamp}.pdf")
                    
                QMessageBox.information(self, "Success", "Plots exported successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export plots: {str(e)}")

    # Update create_signal_settings method
    def create_signal_settings(self, signal_name: str):
        if signal_name not in self.signal_settings:
            self.signal_settings[signal_name] = SignalSettings()
        
        group = QGroupBox(signal_name)
        layout = QVBoxLayout()
        
        # Trim controls
        trim_group = QGroupBox("Trimming")
        trim_layout = QGridLayout()
        
        # Add spinboxes for precise control
        start_spin = QDoubleSpinBox()
        start_spin.setRange(0, 100)
        start_spin.setDecimals(1)
        start_spin.setSingleStep(0.1)
        start_spin.setValue(self.signal_settings[signal_name].start_trim)
        
        end_spin = QDoubleSpinBox()
        end_spin.setRange(0, 100)
        end_spin.setDecimals(1)
        end_spin.setSingleStep(0.1)
        end_spin.setValue(self.signal_settings[signal_name].end_trim)
        
        range_slider = RangeSlider(0.0, 100.0)
        range_slider.setRange(
            self.signal_settings[signal_name].start_trim,
            self.signal_settings[signal_name].end_trim
        )
        
        def update_range_from_slider(values):
            start, end = values
            start_spin.setValue(start)
            end_spin.setValue(end)
            self.signal_settings[signal_name].start_trim = start
            self.signal_settings[signal_name].end_trim = end
            self.update_plots()
        
        def update_range_from_spin():
            start = start_spin.value()
            end = end_spin.value()
            if start < end:
                range_slider.setRange(start, end)
                self.signal_settings[signal_name].start_trim = start
                self.signal_settings[signal_name].end_trim = end
                self.update_plots()
        
        range_slider.valueChanged.connect(update_range_from_slider)
        start_spin.valueChanged.connect(update_range_from_spin)
        end_spin.valueChanged.connect(update_range_from_spin)
        
        trim_layout.addWidget(QLabel("Start:"), 0, 0)
        trim_layout.addWidget(start_spin, 0, 1)
        trim_layout.addWidget(QLabel("End:"), 1, 0)
        trim_layout.addWidget(end_spin, 1, 1)
        trim_layout.addWidget(range_slider, 2, 0, 1, 2)
        trim_group.setLayout(trim_layout)
        
        # Smoothing slider
        smooth_group = QGroupBox("Smoothing")
        smooth_layout = QVBoxLayout()
        smooth_slider = QSlider(Qt.Orientation.Horizontal)
        smooth_slider.setRange(1, 100)
        smooth_slider.setValue(self.signal_settings[signal_name].smoothing)
        
        # Smoothing value label
        smooth_value = QLabel(f"Smoothing: {self.signal_settings[signal_name].smoothing}")
        smooth_slider.valueChanged.connect(
            lambda v: [
                smooth_value.setText(f"Smoothing: {v}"),
                self.update_signal_setting(signal_name, 'smoothing', v)
            ]
        )
        
        smooth_layout.addWidget(smooth_slider)
        smooth_layout.addWidget(smooth_value)
        smooth_group.setLayout(smooth_layout)
        
        # Offset inputs
        offset_group = QGroupBox("Offsets")
        offset_layout = QFormLayout()
        
        time_offset = QDoubleSpinBox()
        time_offset.setRange(-10, 10)  # Limit range to ±10 seconds
        time_offset.setDecimals(6)     # Microsecond precision
        time_offset.setSingleStep(0.000001)  # 1µs steps
        time_offset.setValue(self.signal_settings[signal_name].time_offset)
        time_offset.valueChanged.connect(
            lambda v: self.update_signal_setting(signal_name, 'time_offset', v)
        )
        
        # Create voltage offset controls per channel
        voltage_offsets = {}
        for channel in ["CH1", "CH2"]:
            voltage_offsets[channel] = QDoubleSpinBox()
            voltage_offsets[channel].setRange(-1000, 1000)
            voltage_offsets[channel].setValue(
                self.signal_settings[signal_name].voltage_offsets.get(channel, 0.0)
            )
            voltage_offsets[channel].valueChanged.connect(
                lambda v, ch=channel: self.update_voltage_offset(signal_name, ch, v)
            )
            offset_layout.addRow(f"{channel} Voltage Offset:", voltage_offsets[channel])
        
        offset_layout.addRow("Time Offset:", time_offset)
        offset_group.setLayout(offset_layout)
        
        # Add all groups to main layout with compact spacing
        layout.addWidget(trim_group)
        layout.addWidget(smooth_group)
        layout.addWidget(offset_group)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        group.setLayout(layout)
        return group

    # Add new method for voltage offset updates
    def update_voltage_offset(self, signal_name: str, channel: str, value: float):
        if signal_name in self.signal_settings:
            self.signal_settings[signal_name].voltage_offsets[channel] = value
            # Use QTimer to debounce updates
            if hasattr(self, '_update_timer'):
                self._update_timer.stop()
            self._update_timer = QTimer()
            self._update_timer.setSingleShot(True)
            self._update_timer.timeout.connect(self._delayed_update)
            self._update_timer.start(100)

    def update_signal_setting(self, signal_name: str, setting: str, value: float):
        if signal_name in self.signal_settings:
            setattr(self.signal_settings[signal_name], setting, value)
            # Use QTimer to debounce updates
            if hasattr(self, '_update_timer'):
                self._update_timer.stop()
            self._update_timer = QTimer()
            self._update_timer.setSingleShot(True)
            self._update_timer.timeout.connect(self._delayed_update)
            self._update_timer.start(100)  # 100ms delay

    def _delayed_update(self):
        try:
            self.process_signals()
            self.update_plots()
        except Exception as e:
            self.show_error(f"Error updating plots: {str(e)}")

    def update_settings_panel(self):
        # Clear existing settings
        while self.settings_layout.count():
            item = self.settings_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add settings for each selected file
        for filename in self.signals.keys():
            settings_group = self.create_signal_settings(filename)
            self.settings_layout.addWidget(settings_group)
        
        self.settings_layout.addStretch()

    def process_signals(self):
        for filename, channels in self.signals.items():
            if filename in self.signal_settings:
                settings = self.signal_settings[filename]
                for channel_name, channel in channels.items():
                    processor = SignalProcessor(channel)
                    # Use channel-specific voltage offset
                    voltage_offset = settings.voltage_offsets.get(channel_name, 0.0)
                    processor.process_signal(
                        start_trim=settings.start_trim,
                        end_trim=settings.end_trim,
                        window_size=settings.smoothing,
                        voltage_offset=voltage_offset,  # Use per-channel offset
                        time_offset=settings.time_offset
                    )

class RangeSlider(QWidget):
    valueChanged = pyqtSignal(tuple)

    def __init__(self, minimum=0.0, maximum=100.0):
        super().__init__()
        self.minimum = minimum
        self.maximum = maximum
        self.left_value = minimum
        self.right_value = maximum
        self.step = 0.1  # 0.1% steps
        
        self.setMinimumHeight(30)
        self.moving = None
        self.offset = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background line
        width = self.width() - 20  # Margin for handles
        height = self.height()
        
        painter.setPen(QPen(Qt.GlobalColor.gray, 2))
        painter.drawLine(10, height//2, width+10, height//2)
        
        # Calculate positions
        left_pos = self._value_to_pos(self.left_value)
        right_pos = self._value_to_pos(self.right_value)
        
        # Draw handles
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(left_pos-5, height//2-5, 10, 10)
        painter.drawEllipse(right_pos-5, height//2-5, 10, 10)
        
        # Draw selected range
        painter.setPen(QPen(Qt.GlobalColor.blue, 2))
        painter.drawLine(left_pos, height//2, right_pos, height//2)
        
    def _pos_to_value(self, pos):
        width = self.width() - 20
        relative_pos = (pos - 10) / width
        value = self.minimum + relative_pos * (self.maximum - self.minimum)
        # Round to nearest step
        return round(value / self.step) * self.step
        
    def _value_to_pos(self, value):
        width = self.width() - 20
        relative_value = (value - self.minimum) / (self.maximum - self.minimum)
        return int(10 + relative_value * width)
        
    def mousePressEvent(self, event):
        left_pos = self._value_to_pos(self.left_value)
        right_pos = self._value_to_pos(self.right_value)
        
        if abs(event.position().x() - left_pos) < 10:
            self.moving = 'left'
        elif abs(event.position().x() - right_pos) < 10:
            self.moving = 'right'
            
    def mouseMoveEvent(self, event):
        if self.moving:
            value = self._pos_to_value(event.position().x())
            value = max(self.minimum, min(self.maximum, value))
            
            if self.moving == 'left' and value < self.right_value:
                self.left_value = value
            elif self.moving == 'right' and value > self.left_value:
                self.right_value = value
                
            self.update()
            self.valueChanged.emit((self.left_value, self.right_value))
            
    def mouseReleaseEvent(self, event):
        self.moving = None

    def setRange(self, start, end):
        self.left_value = start
        self.right_value = end
        self.update()