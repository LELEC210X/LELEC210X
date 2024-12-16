# plot_manager.py
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import matplotlib
from typing import Dict
import numpy as np

#plt.style.use('seaborn-darkgrid')  # Scientific style

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
        # Convert pixels to inches for matplotlib
        w_inches = width / self.dpi
        h_inches = height / self.dpi
        fig = Figure(figsize=(w_inches, h_inches), dpi=self.dpi)
        return FigureCanvasQTAgg(fig)

    def calculate_plot_dimensions(self, container_width: int, container_height: int, 
                                target_ratio: tuple) -> tuple[int, int]:
        """Calculate plot dimensions to fit container while maintaining aspect ratio"""
        target_width, target_height = target_ratio
        ratio = target_width / target_height
        
        # Calculate dimensions that fit the container
        if container_width / container_height > ratio:
            # Container is wider than target ratio - fit to height
            height = container_height
            width = int(height * ratio)
        else:
            # Container is taller than target ratio - fit to width
            width = container_width
            height = int(width / ratio)
            
        return width, height

    def create_voltage_plot(self, signals: Dict, width: int, height: int, for_export: bool = False):
        canvas = self.create_canvas(width, height)
        ax = canvas.figure.add_subplot(111)
        
        for filename, channels in signals.items():
            for channel_name, signal in channels.items():
                ax.plot(signal.time, signal.processed_signal, 
                       label=f"{filename} - {channel_name}")
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (V)')
        ax.set_title('Voltage Signals')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')  # Automatically find best location inside plot
        
        if for_export:
            canvas.figure.tight_layout(pad=0.1)  # Tight borders for export
        else:
            canvas.figure.tight_layout(pad=0.5)  # More padding for UI
            
        return canvas

    def create_power_plot(self, signals: Dict, power_calc, width: int, height: int, for_export: bool = False):
        canvas = self.create_canvas(width, height)
        ax = canvas.figure.add_subplot(111)
        
        for filename, channels in signals.items():
            if "CH1" in channels and "CH2" in channels:
                power = power_calc(channels["CH1"], channels["CH2"])
                ax.plot(channels["CH1"].time, power, label=f"{filename} - Power")
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Power (W)')
        ax.set_title('Power')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')  # Automatically find best location inside plot
        
        if for_export:
            canvas.figure.tight_layout(pad=0.1)  # Tight borders for export
        else:
            canvas.figure.tight_layout(pad=0.5)  # More padding for UI
            
        return canvas
