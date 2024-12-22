import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from tkinter import filedialog, Tk
import logging
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QSlider, QLabel)
from PyQt6.QtCore import Qt
import matplotlib.style as mplstyle

close_all = False

class CSVProcessor:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.metadata = {}
        self.time = None
        self.voltage_data = {}
        self._process_file()
        
    def _process_file(self):
        """Process the CSV file and extract data"""
        # Read metadata from header
        with open(self.file_path, 'r') as f:
            header_lines = [f.readline().strip() for _ in range(7)]
            
        # Get channel names from first line
        _, *channel_names = header_lines[0].strip().split(',')
        
        # Read actual data
        df = pd.read_csv(self.file_path, skiprows=8)
        
        # Extract time interval from metadata
        time_interval = float(header_lines[6].split(',')[1].replace('uS', '')) * 1e-6
        self.time = np.arange(len(df)) * time_interval
        
        # Extract voltage data for each channel
        for channel in channel_names:
            voltage_column = f"{channel}_Voltage(mV)"
            if voltage_column in df.columns:
                self.voltage_data[channel] = df[voltage_column].values * 1e-3  # Convert mV to V

class PlotWindow(QMainWindow):
    def __init__(self, file_info, processor, power, folder_path):
        super().__init__()
        self.file_info = file_info
        self.processor = processor
        self.power = power
        self.folder_path = folder_path
        mplstyle.use('fast')
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Energy consumption widget
        self.energy_widget = QWidget()
        self.energy_layout = QVBoxLayout(self.energy_widget)
        self.energy_layout.addWidget(QLabel(f"Energy consumption: {np.trapz(self.power)*1e-3:.2f} mJ"))
        layout.addWidget(self.energy_widget)

        # Plot widget setup
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        
        # Create and store matplotlib canvas
        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasQTAgg(self.fig)
        plot_layout.addWidget(self.canvas)
        
        # Navigation toolbar
        toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_layout.addWidget(toolbar)
        
        layout.addWidget(plot_widget)

        # Center time and store data
        self.centered_time = self.processor.time - self.processor.time[0]
        
        # Create plot
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot(self.centered_time, self.power)
        self.ax.tick_params(axis='both', which='major', labelsize=16)
        self.ax.set_xlabel("Time (s)", fontsize=24)
        self.ax.set_ylabel("Power (mW)", fontsize=24)
        self.ax.set_ylim(min(-0.2, np.min(self.power)), np.max(self.power)*1.1) # TODO : sum the -0.2 to the min value
        self.ax.grid(True)

        # Slider setup with safety bounds
        self.data_len = len(self.centered_time)
        
        slider_widget = QWidget()
        slider_layout = QVBoxLayout(slider_widget)
        
        # Start slider with value display
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start:"))
        self.start_slider = QSlider(Qt.Orientation.Horizontal)
        self.start_slider.setRange(0, self.data_len-2)  # Leave room for end
        self.start_value = QLabel("0")
        start_layout.addWidget(self.start_slider)
        start_layout.addWidget(self.start_value)
        slider_layout.addLayout(start_layout)
        
        # End slider with value display
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End:"))
        self.end_slider = QSlider(Qt.Orientation.Horizontal)
        self.end_slider.setRange(1, self.data_len-1)  # Must be after start
        self.end_slider.setValue(self.data_len-1)
        self.end_value = QLabel(str(self.data_len-1))
        end_layout.addWidget(self.end_slider)
        end_layout.addWidget(self.end_value)
        slider_layout.addLayout(end_layout)
        
        # Connect sliders with value updates
        self.start_slider.valueChanged.connect(self.on_start_changed)
        self.end_slider.valueChanged.connect(self.on_end_changed)
        
        layout.addWidget(slider_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset View")
        reset_btn.clicked.connect(self.reset_view)
        save_btn = QPushButton("Save Plot")
        save_btn.clicked.connect(self.save_plot)
        close_btn = QPushButton("Close All")
        close_btn.clicked.connect(self.close_all)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def on_start_changed(self, value):
        self.start_value.setText(str(value))
        if value < self.end_slider.value():
            self.update_plot()

    def on_end_changed(self, value):
        self.end_value.setText(str(value))
        if value > self.start_slider.value():
            self.update_plot()

    def update_plot(self):
        try:
            start_idx = self.start_slider.value()
            end_idx = self.end_slider.value()
            
            if start_idx >= end_idx or start_idx < 0 or end_idx >= self.data_len:
                return
                
            # Recenter time axis
            trimmed_time = self.centered_time[start_idx:end_idx]
            trimmed_time = trimmed_time - trimmed_time[0]

            self.line.set_data(trimmed_time, 
                              self.power[start_idx:end_idx])
            self.ax.relim()
            self.ax.autoscale_view()
            
            self.file_info['trim_start'] = start_idx
            self.file_info['trim_end'] = end_idx
            
            self.canvas.draw()

            # Update energy consumption
            energy = np.trapz(self.power[start_idx:end_idx]) * 1e-3
            self.energy_layout.itemAt(0).widget().setText(f"Energy consumption: {energy:.2f} mJ")
        except Exception as e:
            logging.error(f"Error updating plot: {str(e)}")

    def reset_view(self):
        self.start_slider.setValue(0)
        self.end_slider.setValue(self.data_len-1)

    def save_plot(self):
        save_dir = self.folder_path / 'plots'
        save_dir.mkdir(exist_ok=True)
        base_name = f"{self.file_info['filename'][:-4]}_trim_{self.file_info['trim_start']}_{self.file_info['trim_end']}"
        self.fig.savefig(save_dir / f"{base_name}.pdf", bbox_inches='tight')
        self.fig.savefig(save_dir / f"{base_name}.png", dpi=300, bbox_inches='tight')
        print(f"Saved plots to {save_dir} : {base_name}")
        print(f"Energy consumption: {np.trapz(self.power[self.file_info['trim_start']:self.file_info['trim_end']])} mJ")

    def close_all(self):
        global close_all
        close_all = True
        QApplication.quit()

def main():
    # Create root window and hide it
    root = Tk()
    root.withdraw()
    
    # Ask user to select folder
    folder_path = filedialog.askdirectory(title="Select Folder with CSV Files")
    if not folder_path:
        print("No folder selected")
        return
        
    folder_path = Path(folder_path)
    
    # Find all CSV files in folder
    csv_files = list(folder_path.glob('*.csv'))
    if not csv_files:
        print("No CSV files found in selected folder")
        return
        
    print("Found CSV files:")
    print("{")
    for i, file in enumerate(csv_files):
        print(f"    {i}: {{'filename': '{file.name}', 'trim_start' : 0, 'trim_end': -1}},")
    print("}")

    csv_files = {
        0: {'filename': 'data_30_000.csv', 'trim_start' : 0, 'trim_end': -1},
        1: {'filename': 'data_30_001.csv', 'trim_start' : 0, 'trim_end': -1},
        2: {'filename': 'data_30_002.csv', 'trim_start' : 0, 'trim_end': -1},
        3: {'filename': 'data_30_003.csv', 'trim_start' : 0, 'trim_end': -1},
        4: {'filename': 'data_30_004.csv', 'trim_start' : 0, 'trim_end': -1},
        5: {'filename': 'data_30_005.csv', 'trim_start' : 0, 'trim_end': -1},
        6: {'filename': 'data_30_006.csv', 'trim_start' : 0, 'trim_end': -1},
        7: {'filename': 'data_30_007.csv', 'trim_start' : 0, 'trim_end': -1},
        8: {'filename': 'data_30_008.csv', 'trim_start' : 0, 'trim_end': -1},
        9: {'filename': 'data_30_009.csv', 'trim_start' : 0, 'trim_end': -1},
        10: {'filename': 'data_30_010.csv', 'trim_start' : 0, 'trim_end': -1},
        11: {'filename': 'data_30_011.csv', 'trim_start' : 0, 'trim_end': -1},
        12: {'filename': 'data_30_012.csv', 'trim_start' : 0, 'trim_end': -1},
        13: {'filename': 'data_30_013.csv', 'trim_start' : 0, 'trim_end': -1},
        14: {'filename': 'data_30_014.csv', 'trim_start' : 0, 'trim_end': -1},
        15: {'filename': 'data_30_015.csv', 'trim_start' : 0, 'trim_end': -1},
        16: {'filename': 'data_30_016.csv', 'trim_start' : 0, 'trim_end': -1},
        17: {'filename': 'data_30_017.csv', 'trim_start' : 0, 'trim_end': -1},
        18: {'filename': 'data_30_018.csv', 'trim_start' : 0, 'trim_end': -1},
        19: {'filename': 'data_30_019.csv', 'trim_start' : 0, 'trim_end': -1},
        110: {'filename': 'data_31_000.csv', 'trim_start' : 0, 'trim_end': -1},
        111: {'filename': 'data_31_001.csv', 'trim_start' : 0, 'trim_end': -1},
        112: {'filename': 'data_31_002.csv', 'trim_start' : 0, 'trim_end': -1},
        113: {'filename': 'data_31_003.csv', 'trim_start' : 0, 'trim_end': -1},
        114: {'filename': 'data_31_004.csv', 'trim_start' : 0, 'trim_end': -1},
        115: {'filename': 'data_31_006.csv', 'trim_start' : 0, 'trim_end': -1},
    }

    R = 100.54
    OFFSET_CH1 = -6.0 * 100 * 1e-3 # 100mV per div
    OFFSET_CH2 =  0.0 * 1 # 1V per div
    ch1_voltage = lambda ch1: (ch1 - OFFSET_CH1)
    ch2_voltage = lambda ch2: (ch2 - OFFSET_CH2)
    mcu_current = lambda ch1: -ch1_voltage(ch1) / R
    mcu_voltage = lambda ch2, ch1: ch2_voltage(ch2) + ch1_voltage(ch1)
    power_formula = lambda ch1, ch2: mcu_current(ch1) * mcu_voltage(ch2, ch1)

    app = QApplication(sys.argv)
    mplstyle.use('fast')

    for i, file in csv_files.items():
        if close_all:
            break
        try:
            processor = CSVProcessor(folder_path / file['filename'])
            ch1 = processor.voltage_data['CH1']
            ch2 = processor.voltage_data['CH2']
            power = power_formula(ch1, ch2)*1000
            
            window = PlotWindow(file, processor, power, folder_path)
            window.show()
            app.exec()
            
        except Exception as e:
            logging.error(f"Error processing file {file['filename']}: {str(e)}")
            continue

if __name__ == "__main__":
    main()