# gui.py
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QThread, pyqtSignal
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

logger = logging.getLogger(__name__)

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

class SignalViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal Viewer")
        self.signals: Dict[str, SignalData] = {}
        self.loaded_files: Dict[str, Dict[str, SignalData]] = {}  # Store loaded files separately
        self.power_formula = "P=CH1*CH2/R"
        self.resistance = 100.0
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Left panel
        left_panel = QVBoxLayout()
        
        # File selection group
        file_group = QGroupBox("Files")
        file_layout = QVBoxLayout()
        
        # File list buttons layout
        file_buttons = QHBoxLayout()
        load_btn = QPushButton("Load Files")
        load_btn.clicked.connect(self.load_files)
        deselect_btn = QPushButton("Deselect All")
        deselect_btn.clicked.connect(self.deselect_all_files)
        file_buttons.addWidget(load_btn)
        file_buttons.addWidget(deselect_btn)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        
        file_layout.addLayout(file_buttons)
        file_layout.addWidget(self.file_list)
        
        # Export buttons
        export_group = QGroupBox("Export Plots")
        export_layout = QVBoxLayout()
        
        export_voltage_btn = QPushButton("Export Voltage Plot")
        export_voltage_btn.clicked.connect(lambda: self.export_plot('voltage'))
        export_power_btn = QPushButton("Export Power Plot")
        export_power_btn.clicked.connect(lambda: self.export_plot('power'))
        export_both_btn = QPushButton("Export Both Plots")
        export_both_btn.clicked.connect(lambda: self.export_plot('both'))
        
        export_layout.addWidget(export_voltage_btn)
        export_layout.addWidget(export_power_btn)
        export_layout.addWidget(export_both_btn)
        export_group.setLayout(export_layout)
        
        file_layout.addWidget(export_group)
        file_group.setLayout(file_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        file_layout.addWidget(self.progress_bar)
        
        # Controls
        controls_group = QGroupBox("Controls")
        controls_layout = QFormLayout()
        
        self.voltage_offset = QDoubleSpinBox()
        self.voltage_scale = QDoubleSpinBox()
        self.voltage_scale.setValue(1.0)
        self.resistance = QDoubleSpinBox()
        self.resistance.setRange(0.001, 1e6)  # Allow values from 1mΩ to 1MΩ
        self.resistance.setDecimals(3)  # 3 decimal places
        self.resistance.setValue(1.0)
        self.resistance.setSuffix(" Ω")  # Add units
        self.resistance.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        
        self.power_combo = QComboBox()
        self.power_combo.addItems([
            "P=CH1*CH2",
            "P=CH1*(CH1-CH2)/R",
            "P=CH1*CH2/R",
            "P=CH1^2/R",
            "P=CH1^2"
        ])
        
        controls_layout.addRow("Voltage Offset:", self.voltage_offset)
        controls_layout.addRow("Voltage Scale:", self.voltage_scale)
        controls_layout.addRow("Resistance (Ω):", self.resistance)
        controls_layout.addRow("Power Formula:", self.power_combo)
        
        update_btn = QPushButton("Update Plots")
        update_btn.clicked.connect(self.update_plots)
        controls_layout.addRow(update_btn)
        
        controls_group.setLayout(controls_layout)
        
        left_panel.addWidget(file_group)
        left_panel.addWidget(controls_group)
        
        # Add plot settings group
        plot_settings = QGroupBox("Plot Settings")
        plot_layout = QFormLayout()
        
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
        
        plot_layout.addRow("Aspect Ratio:", self.aspect_ratio)
        plot_settings.setLayout(plot_layout)
        
        # Add to layout
        left_panel.addWidget(plot_settings)
        
        # Right panel with plots
        right_panel = QVBoxLayout()
        self.voltage_plot = QWebEngineView()
        self.power_plot = QWebEngineView()
        right_panel.addWidget(self.voltage_plot)
        right_panel.addWidget(self.power_plot)
        
        # Add panels to main layout
        layout.addLayout(left_panel, stretch=1)
        layout.addLayout(right_panel, stretch=3)
        
        self.setGeometry(100, 100, 1200, 800)

        # Add selection change handler
        self.file_list.itemSelectionChanged.connect(self.update_selected_signals)

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

    def update_plots(self):
        if not self.signals:
            return
            
        # Create voltage plot
        voltage_fig = make_subplots(rows=1, cols=1)
        
        for filename, channels in self.signals.items():
            for channel_name, signal in channels.items():
                voltage_fig.add_trace(
                    go.Scatter(
                        x=signal.time,
                        y=signal.processed_signal,
                        name=f"{filename} - {channel_name}"
                    )
                )
        
        voltage_fig.update_layout(
            title="Voltage Signals",
            xaxis_title="Time (s)",
            yaxis_title="Voltage (V)"
        )
        
        # Create power plot
        power_fig = make_subplots(rows=1, cols=1)
        
        for filename, channels in self.signals.items():
            if "CH1" in channels and "CH2" in channels:
                power = self.calculate_power(channels["CH1"], channels["CH2"])
                power_fig.add_trace(
                    go.Scatter(
                        x=channels["CH1"].time,
                        y=power,
                        name=f"{filename} - Power"
                    )
                )
        
        power_fig.update_layout(
            title="Power",
            xaxis_title="Time (s)",
            yaxis_title="Power (W)"
        )
        
        # Update plots
        self.voltage_plot.setHtml(voltage_fig.to_html(include_plotlyjs='cdn'))
        self.power_plot.setHtml(power_fig.to_html(include_plotlyjs='cdn'))

    def calculate_power(self, ch1: SignalData, ch2: SignalData) -> np.ndarray:
        """Calculate power based on selected formula and resistance"""
        formula = self.power_combo.currentText()
        r = self.resistance.value()
        
        try:
            if formula == "P=CH1*CH2":
                return ch1.processed_signal * ch2.processed_signal
            elif formula == "P=CH1*(CH1-CH2)/R":
                return ch1.processed_signal * (ch1.processed_signal - ch2.processed_signal) / r
            elif formula == "P=CH1*CH2/R":
                return ch1.processed_signal * ch2.processed_signal / r
            elif formula == "P=CH1^2/R":
                return ch1.processed_signal ** 2 / r
            elif formula == "P=CH1^2":
                return ch1.processed_signal ** 2
            else:
                logger.error(f"Unknown power formula: {formula}")
                return np.zeros_like(ch1.processed_signal)
                
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
                
                # Get current dimensions
                width, height = self.aspect_ratios[self.aspect_ratio.currentText()]
                
                # Configure plot export settings
                config = {
                    'width': width,
                    'height': height,
                    'scale': 4  # Higher resolution for export
                }
                
                if plot_type in ['voltage', 'both']:
                    voltage_fig = self.create_voltage_plot()
                    voltage_fig.write_image(
                        str(save_dir / f"voltage_plot_{timestamp}.png"),
                        **config
                    )
                    voltage_fig.write_image(
                        str(save_dir / f"voltage_plot_{timestamp}.pdf"),
                        **config
                    )
                    
                if plot_type in ['power', 'both']:
                    power_fig = self.create_power_plot()
                    power_fig.write_image(
                        str(save_dir / f"power_plot_{timestamp}.png"),
                        **config
                    )
                    power_fig.write_image(
                        str(save_dir / f"power_plot_{timestamp}.pdf"),
                        **config
                    )
                    
                QMessageBox.information(self, "Success", "Plots exported successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export plots: {str(e)}")