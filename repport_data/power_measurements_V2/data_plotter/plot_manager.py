# plot_manager.py
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import matplotlib
from typing import Dict
import numpy as np

plt.style.use('seaborn-darkgrid')  # Scientific style

class PlotManager:
    def __init__(self, dpi=100):
        self.dpi = dpi
        plt.rcParams.update({
            'font.size': 10,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })

    def create_canvas(self, width, height):
        fig = Figure(figsize=(width/self.dpi, height/self.dpi), dpi=self.dpi)
        return FigureCanvasQTAgg(fig)

    def create_voltage_plot(self, signals: Dict, width: int, height: int):
        canvas = self.create_canvas(width, height)
        ax = canvas.figure.add_subplot(111)
        
        for filename, channels in signals.items():
            for channel_name, signal in channels.items():
                ax.plot(signal.time, signal.processed_signal, 
                       label=f"{filename} - {channel_name}")
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (V)')
        ax.set_title('Voltage Signals')
        ax.grid(True)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        canvas.figure.tight_layout()
        return canvas

    def create_power_plot(self, signals: Dict, power_calc, width: int, height: int):
        canvas = self.create_canvas(width, height)
        ax = canvas.figure.add_subplot(111)
        
        for filename, channels in signals.items():
            if "CH1" in channels and "CH2" in channels:
                power = power_calc(channels["CH1"], channels["CH2"])
                ax.plot(channels["CH1"].time, power, label=f"{filename} - Power")
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Power (W)')
        ax.set_title('Power')
        ax.grid(True)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        canvas.figure.tight_layout()
        return canvas
