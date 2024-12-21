import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from tkinter import filedialog, Tk
import logging

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
    }

    R = 100.54
    OFFSET_CH1 = -6.0 * 100 * 1e-3 # 100mV per div
    OFFSET_CH2 =  0.0 * 1 # 1V per div
    ch1_voltage = lambda ch1: (ch1 - OFFSET_CH1)
    ch2_voltage = lambda ch2: (ch2 - OFFSET_CH2)
    mcu_current = lambda ch1: -ch1_voltage(ch1) / R
    mcu_voltage = lambda ch2, ch1: ch2_voltage(ch2) + ch1_voltage(ch1)
    power_formula = lambda ch1, ch2: mcu_current(ch1) * mcu_voltage(ch2, ch1)

    for i, file in csv_files.items():
        try:
            processor = CSVProcessor(folder_path / file['filename'])
            ch1 = processor.voltage_data['CH1']
            ch2 = processor.voltage_data['CH2']
            power = power_formula(ch1, ch2)*1000
            
            plt.figure()
            plt.plot(processor.time, power)
            plt.xlabel("Time (s)")
            plt.ylabel("Power (mW)")
            plt.title(f"Power Consumption - {file['filename']}")
            plt.ylim(0, np.max(power) * 1.1)
            plt.grid()
            plt.show()
        except Exception as e:
            logging.error(f"Error processing file {file['filename']}: {str(e)}")
            continue

if __name__ == "__main__":
    main()