import json
import random
import sys
import csv
import os

import numpy as np
import plotly.graph_objects as go
from PyQt6.QtCore import QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QGroupBox, QVBoxLayout, QListWidget, QToolBar, QFormLayout, QSpinBox, QDoubleSpinBox

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "\\"
PLOTS_FOLDER = os.path.join(os.getcwd(), "Plots")
os.makedirs(os.path.join(PLOTS_FOLDER, "png"), exist_ok=True)
os.makedirs(os.path.join(PLOTS_FOLDER, "pdf"), exist_ok=True)

# Read CSV Data
def read_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        metadata = {}
        data = []
        for row in reader:
            if not row:
                continue
            if row[0].strip() == 'index':
                header = row
                break
            else:
                key = row[0].strip()
                values = row[1:]
                metadata[key] = values
        for row in reader:
            if not row:
                continue
            try:
                data.append([float(x) for x in row])
            except ValueError:
                continue
    data = np.array(data)
    return metadata, header, data

power_formulas = {
    "P = ch1*(ch1 - ch2)/R": lambda ch1, ch2, r: ch1 * (ch1 - ch2) / r,
    "P = ch1*ch2/R": lambda ch1, ch2, r: ch1 * ch2 / r,
    "P = ch1**2/R": lambda ch1, ch2, r: ch1**2 / r,
    "P = ch2**2/R": lambda ch1, ch2, r: ch2**2 / r,
    "P = ch2*(ch2 - ch1)/R": lambda ch1, ch2, r: ch2 * (ch2 - ch1) / r,
}

def process_data(metadata, data, voltage_scaling_ch1=1.0, voltage_scaling_ch2 = 1.0, resistance = 100, power_formula="P = ch1*(ch1 - ch2)/R", flip_power=False, flip_ch1=False, flip_ch2=False):
    time_interval   = float(metadata["Time interval        :"][0].replace('uS', '')) * 1e-6
    voltage_per_adc = float(metadata["Voltage per ADC value:"][0].replace('mV', '')) * 1e-3
    
    time = data[:, 0] * time_interval
    ch1  = data[:, 1] * voltage_per_adc * voltage_scaling_ch1  # Convert to mV
    ch2  = data[:, 2] * voltage_per_adc * voltage_scaling_ch2  # Convert to mV
    
    #current = (ch1 - ch2) / resistance
    #power = ch1 * current  # Power in mW
    power = power_formulas[power_formula](ch1, ch2, resistance)
    
    return time, ch1, ch2, power

class DynamicPlotlyGraphApp(QMainWindow):
    def __init__(self, metadata, data):
        super().__init__()
        self.setWindowTitle("Oscilloscope Data Viewer")
        self.current_folder = CURRENT_FOLDER
        self.metadata = metadata
        self.raw_data = data

        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left panel - File List with multi-selection
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.update_file_list()
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        left_panel = QGroupBox("CSV Files")
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.file_list)
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(200)

        # Center panel - Plot and Toolbar
        center_panel = QWidget()
        center_layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QToolBar()
        save_btn = toolbar.addAction("Save Plot")
        save_btn.triggered.connect(self.save_plot)
        toolbar.addAction(save_btn)
        
        # Plot
        self.web_view = QWebEngineView()
        center_layout.addWidget(toolbar)
        center_layout.addWidget(self.web_view)
        center_panel.setLayout(center_layout)

        # Right panel - Dynamic Signal Controls
        self.right_panel = QGroupBox("Signal Controls")
        self.right_layout = QVBoxLayout()
        self.right_panel.setLayout(self.right_layout)
        self.right_panel.setMaximumWidth(300)
        
        # Dictionary to store controls and data for each graph
        self.graph_controls = {}  # {filename: {controls: {...}, data: {...}}}

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(center_panel)
        main_layout.addWidget(self.right_panel)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Initialize plot
        self.time, self.ch1, self.ch2, self.power = process_data(metadata, data)
        
        # Store original data for reference
        self.original_time = self.time.copy()
        self.original_power = self.power.copy()

        # Create the initial graph
        self.init_graph()

        # Remove timer setup since we don't need dynamic updates
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_graph)
        # self.timer.start(1000 // 60)

    def create_control_group(self, filename):
        """Create control group for a single graph"""
        group = QGroupBox(filename)
        layout = QVBoxLayout()
        
        # Trimming controls
        trim_group = QGroupBox("Trim")
        trim_layout = QFormLayout()
        trim_start = QSpinBox()
        trim_end = QSpinBox()
        trim_layout.addRow("Start:", trim_start)
        trim_layout.addRow("End:", trim_end)
        trim_group.setLayout(trim_layout)
        
        # Shift controls
        shift_group = QGroupBox("Shift")
        shift_layout = QFormLayout()
        shift_x = QDoubleSpinBox()
        shift_y = QDoubleSpinBox()
        shift_layout.addRow("X:", shift_x)
        shift_layout.addRow("Y:", shift_y)
        shift_group.setLayout(shift_layout)
        
        # Scale controls
        scale_group = QGroupBox("Scale")
        scale_layout = QFormLayout()
        scale_x = QDoubleSpinBox()
        scale_y = QDoubleSpinBox()
        scale_x.setValue(1.0)
        scale_y.setValue(1.0)
        scale_layout.addRow("X:", scale_x)
        scale_layout.addRow("Y:", scale_y)
        scale_group.setLayout(scale_layout)
        
        layout.addWidget(trim_group)
        layout.addWidget(shift_group)
        layout.addWidget(scale_group)
        group.setLayout(layout)
        
        controls = {
            'trim_start': trim_start,
            'trim_end': trim_end,
            'shift_x': shift_x,
            'shift_y': shift_y,
            'scale_x': scale_x,
            'scale_y': scale_y
        }
        
        # Connect control signals
        for control in controls.values():
            control.valueChanged.connect(lambda: self.update_signal(filename))
            
        return group, controls

    def on_selection_changed(self):
        """Handle changes in file selection"""
        selected_items = self.file_list.selectedItems()
        selected_files = [item.text() for item in selected_items]
        
        # Remove controls for deselected files
        current_files = list(self.graph_controls.keys())
        for filename in current_files:
            if filename not in selected_files:
                self.graph_controls[filename]['group'].deleteLater()
                del self.graph_controls[filename]
        
        # Add controls for newly selected files
        for filename in selected_files:
            if filename not in self.graph_controls:
                # Load data
                file_path = os.path.join(self.current_folder, filename)
                metadata, _, raw_data = read_csv(file_path)
                time, ch1, ch2, power = process_data(metadata, raw_data)
                
                # Create controls
                group, controls = self.create_control_group(filename)
                self.right_layout.addWidget(group)
                
                # Store controls and data
                self.graph_controls[filename] = {
                    'group': group,
                    'controls': controls,
                    'data': {
                        'time': time,
                        'power': power,
                        'original_time': time.copy(),
                        'original_power': power.copy()
                    }
                }
        
        self.update_plot()

    def update_plot(self):
        """Update plot with all selected traces"""
        self.fig = go.Figure()
        
        for filename, graph_data in self.graph_controls.items():
            controls = graph_data['controls']
            data = graph_data['data']
            
            # Apply modifications
            start = controls['trim_start'].value()
            end = controls['trim_end'].value() or len(data['original_time'])
            shift_x = controls['shift_x'].value()
            shift_y = controls['shift_y'].value()
            scale_x = controls['scale_x'].value()
            scale_y = controls['scale_y'].value()
            
            time = data['original_time'][start:end] * scale_x + shift_x
            power = data['original_power'][start:end] * scale_y + shift_y
            
            self.fig.add_scatter(x=time, y=power, mode='lines', name=filename)
        
        html = self.fig.to_html(full_html=True, include_plotlyjs='cdn', div_id='my-plot')
        self.web_view.setHtml(html)

    def update_signal(self, filename):
        """Update a single signal and refresh plot"""
        if filename in self.graph_controls:
            self.update_plot()

    def update_file_list(self):
        """Update the file list with CSV files from current directory"""
        self.file_list.clear()
        for file in os.listdir(self.current_folder):
            if file.endswith('.csv'):
                self.file_list.addItem(file)

    def load_csv_file(self, item):
        """Load selected CSV file and update plot"""
        file_path = os.path.join(self.current_folder, item.text())
        self.metadata, _, self.raw_data = read_csv(file_path)
        self.time, self.ch1, self.ch2, self.power = process_data(self.metadata, self.raw_data)
        
        # Update original data
        self.original_time = self.time.copy()
        self.original_power = self.power.copy()
        
        self.init_graph()

    def init_graph(self):
        # Create a basic Plotly figure
        self.fig = go.Figure()
        self.fig.add_scatter(x=self.time, y=self.power, mode='lines', name='Power (mW)')

        # Generate the initial HTML with a unique div id
        html = self.fig.to_html(full_html=True, include_plotlyjs='cdn', div_id='my-plot')

        # Set the HTML content
        self.web_view.setHtml(html)

    def save_plot(self):
        """Save the current plot as both PNG and PDF"""
        import datetime
        
        # Generate timestamp for unique filenames
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as PNG
        png_path = os.path.join(PLOTS_FOLDER, "png", f"plot_{timestamp}.png")
        self.fig.write_image(png_path)
        
        # Save as PDF
        pdf_path = os.path.join(PLOTS_FOLDER, "pdf", f"plot_{timestamp}.pdf")
        self.fig.write_image(pdf_path)

if __name__ == "__main__":
    metadata, header, data = read_csv(os.path.join(CURRENT_FOLDER, "data_27_000.csv"))
    app = QApplication(sys.argv)
    window = DynamicPlotlyGraphApp(metadata, data)
    window.show()
    sys.exit(app.exec())