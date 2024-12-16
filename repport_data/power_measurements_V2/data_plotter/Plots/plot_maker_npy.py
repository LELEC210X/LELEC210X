import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QScrollArea, QPushButton, QGroupBox, QListWidget, QCheckBox, QSpinBox, QComboBox)
from PyQt6.QtCore import Qt

class MultiFileCustomizer(QMainWindow):
    def __init__(self, npy_files):
        super().__init__()
        self.npy_files = npy_files
        self.customizers = {}  # Store settings for each file
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Multi-File Plot Customizer")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel - File list and global controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for npy_file in self.npy_files:
            self.file_list.addItem(npy_file.name)
        self.file_list.itemSelectionChanged.connect(self.update_plot_panels)
        left_layout.addWidget(QLabel("NPY Files:"))
        left_layout.addWidget(self.file_list)
        
        # Global controls
        global_group = QGroupBox("Global Settings")
        global_layout = QVBoxLayout()
        
        # Plot layout selector
        layout_group = QHBoxLayout()
        layout_group.addWidget(QLabel("Plot Layout:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Separate Windows", "Vertical Stack", "Horizontal Stack"])
        layout_group.addWidget(self.layout_combo)
        global_layout.addLayout(layout_group)
        
        # Title controls
        title_group = QGroupBox("Plot Titles")
        title_layout = QVBoxLayout()
        
        # Global title
        global_title_layout = QHBoxLayout()
        global_title_layout.addWidget(QLabel("Global Title:"))
        self.global_title = QLineEdit("Power Measurements")
        global_title_layout.addWidget(self.global_title)
        title_layout.addLayout(global_title_layout)
        
        # Voltage title
        voltage_title_layout = QHBoxLayout()
        voltage_title_layout.addWidget(QLabel("Voltage Title:"))
        self.voltage_title = QLineEdit("Voltage Signals")
        voltage_title_layout.addWidget(self.voltage_title)
        title_layout.addLayout(voltage_title_layout)
        
        # Power title
        power_title_layout = QHBoxLayout()
        power_title_layout.addWidget(QLabel("Power Title:"))
        self.power_title = QLineEdit("Power")
        power_title_layout.addWidget(self.power_title)
        title_layout.addLayout(power_title_layout)
        
        title_group.setLayout(title_layout)
        global_layout.addWidget(title_group)
        
        self.sync_time = QCheckBox("Synchronize Time Axes")
        self.sync_time.setChecked(True)
        global_layout.addWidget(self.sync_time)
        
        # Plot size controls
        size_layout = QVBoxLayout()
        size_layout.addWidget(QLabel("Plot Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 2000)
        self.width_spin.setValue(700)
        self.width_spin.setSingleStep(50)
        size_layout.addWidget(self.width_spin)
        
        size_layout.addWidget(QLabel("Height per Plot:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(200, 1000)
        self.height_spin.setValue(500)
        self.height_spin.setSingleStep(50)
        size_layout.addWidget(self.height_spin)
        
        global_layout.addLayout(size_layout)
        global_group.setLayout(global_layout)
        left_layout.addWidget(global_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        plot_button = QPushButton("Plot Selected")
        save_button = QPushButton("Save Selected")
        plot_button.clicked.connect(self.plot_selected)
        save_button.clicked.connect(self.save_selected)
        button_layout.addWidget(plot_button)
        button_layout.addWidget(save_button)
        left_layout.addLayout(button_layout)
        
        layout.addWidget(left_panel)
        
        # Right panel - Scrollable plot customization area
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_widget = QWidget()
        self.right_layout = QVBoxLayout(right_widget)
        right_scroll.setWidget(right_widget)
        layout.addWidget(right_scroll)
        
        # Set panel sizes
        left_panel.setMaximumWidth(250)
        self.setMinimumSize(1000, 600)

    def create_file_panel(self, npy_file):
        data = np.load(npy_file, allow_pickle=True).item()
        panel = QGroupBox(npy_file.name)
        layout = QVBoxLayout()
        
        # File metadata
        meta_group = QGroupBox("File Information")
        meta_layout = QVBoxLayout()
        if 'plot_info' in data:
            for key, value in data['plot_info'].items():
                if key != 'export_time':
                    meta_layout.addWidget(QLabel(f"{key}: {value}"))
        meta_group.setLayout(meta_layout)
        layout.addWidget(meta_group)
        
        # Voltage signals
        voltage_group = QGroupBox("Voltage Signals")
        voltage_layout = QVBoxLayout()
        
        for filename, channels in data['voltage_signals'].items():
            file_group = QGroupBox(filename)
            file_layout = QVBoxLayout()
            
            for channel, signal in channels.items():
                channel_group = QGroupBox(channel)
                channel_layout = QVBoxLayout()
                
                # Signal controls
                name_layout = QHBoxLayout()
                name_layout.addWidget(QLabel("Label:"))
                name_entry = QLineEdit(f"{filename}-{channel}")
                name_layout.addWidget(name_entry)
                channel_layout.addLayout(name_layout)
                
                # Metadata display
                for key, value in signal['metadata'].items():
                    if isinstance(value, dict):
                        continue
                    channel_layout.addWidget(QLabel(f"{key}: {value}"))
                
                channel_group.setLayout(channel_layout)
                file_layout.addWidget(channel_group)
            
            file_group.setLayout(file_layout)
            voltage_layout.addWidget(file_group)
        
        voltage_group.setLayout(voltage_layout)
        layout.addWidget(voltage_group)
        
        # Power signals
        power_group = QGroupBox("Power Signals")
        power_layout = QVBoxLayout()
        
        for filename, signal in data['power_signals'].items():
            signal_group = QGroupBox(filename)
            signal_layout = QVBoxLayout()
            
            # Label control
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Label:"))
            name_entry = QLineEdit(f"Power-{filename}")
            name_layout.addWidget(name_entry)
            signal_layout.addLayout(name_layout)
            
            # Metadata display
            for key, value in signal['metadata'].items():
                signal_layout.addWidget(QLabel(f"{key}: {value}"))
            
            signal_group.setLayout(signal_layout)
            power_layout.addWidget(signal_group)
        
        power_group.setLayout(power_layout)
        layout.addWidget(power_group)
        
        panel.setLayout(layout)
        return panel

    def update_plot_panels(self):
        # Clear existing panels
        while self.right_layout.count():
            child = self.right_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Create panels for selected files
        for item in self.file_list.selectedItems():
            npy_file = next(f for f in self.npy_files if f.name == item.text())
            panel = self.create_file_panel(npy_file)
            self.right_layout.addWidget(panel)

    def make_plot(self):
        selected_files = [next(f for f in self.npy_files if f.name == item.text())
                         for item in self.file_list.selectedItems()]
        if not selected_files:
            return

        layout_type = self.layout_combo.currentText()
        
        if layout_type == "Separate Windows":
            for npy_file in selected_files:
                self._plot_single_file(npy_file)
        else:
            self._plot_combined(selected_files, layout_type)

    def _plot_single_file(self, npy_file):
        data = np.load(npy_file, allow_pickle=True).item()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.width_spin.value()/100, 
                                                      self.height_spin.value()/50))
        
        # Plot voltage signals
        for filename, channels in data['voltage_signals'].items():
            for channel, signal in channels.items():
                ax1.plot(signal['time'], signal['voltage'], 
                        label=f"{filename}-{channel}")
        
        ax1.set_title(f"{self.voltage_title.text()}")
        ax1.set_xlabel(data['plot_info']['time_axis'])
        ax1.set_ylabel(data['plot_info']['voltage_axis'])
        ax1.grid(True)
        ax1.legend()
        
        # Plot power signals
        for filename, signal in data['power_signals'].items():
            ax2.plot(signal['time'], signal['power'],
                    label=f"Power-{filename}")
        
        ax2.set_title(f"{self.power_title.text()}")
        ax2.set_xlabel(data['plot_info']['time_axis'])
        ax2.set_ylabel(data['plot_info']['power_axis'])
        ax2.grid(True)
        ax2.legend()
        
        fig.suptitle(f"{self.global_title.text()}")
        plt.tight_layout()

    def _plot_combined(self, selected_files, layout_type):
        n_files = len(selected_files)
        
        if layout_type == "Vertical Stack":
            fig = plt.figure(figsize=(self.width_spin.value()/100,
                                     self.height_spin.value()/100 * 2 * n_files))
            subplot_cols = 1
            subplot_rows = n_files * 2
        else:  # Horizontal Stack
            fig = plt.figure(figsize=(self.width_spin.value()/100 * n_files,
                                     self.height_spin.value()/100))
            subplot_cols = n_files
            subplot_rows = 2
        
        axes = []
        for i, npy_file in enumerate(selected_files):
            data = np.load(npy_file, allow_pickle=True).item()
            
            if layout_type == "Vertical Stack":
                ax1 = plt.subplot(subplot_rows, subplot_cols, 2*i + 1)
                ax2 = plt.subplot(subplot_rows, subplot_cols, 2*i + 2)
            else:
                ax1 = plt.subplot(subplot_rows, subplot_cols, i + 1)
                ax2 = plt.subplot(subplot_rows, subplot_cols, i + n_files + 1)
                
            axes.extend([ax1, ax2])
        
        fig.suptitle(self.global_title.text())
        
        # Synchronize time axes if requested
        if self.sync_time.isChecked():
            x_min = min(ax.get_xlim()[0] for ax in axes)
            x_max = max(ax.get_xlim()[1] for ax in axes)
            for ax in axes:
                ax.set_xlim(x_min, x_max)
        
        plt.tight_layout()

    def save_plot(self):
        # Get timestamp from first selected file
        selected_files = [next(f for f in self.npy_files if f.name == item.text())
                         for item in self.file_list.selectedItems()]
        if not selected_files:
            return

        data = np.load(selected_files[0], allow_pickle=True).item()
        timestamp = data['plot_info']['export_time']

        # Create plots directory if it doesn't exist
        save_dir = Path(selected_files[0]).parent / 'plots'
        save_dir.mkdir(exist_ok=True)

        # Generate base filename
        file_stems = '_'.join(f.stem for f in selected_files)
        base_name = f'multi_plot_{file_stems}_{timestamp}'

        # Save plots
        plt.savefig(save_dir / f'{base_name}.pdf')
        plt.savefig(save_dir / f'{base_name}.png', dpi=300)

    def plot_selected(self):
        self.make_plot()
        self.save_plot()
        plt.show()

    def save_selected(self):
        self.save_plot()
        plt.close()

if __name__ == "__main__":
    app = QApplication([])
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    npy_files = list(script_dir.glob('*.npy'))
    
    if npy_files:
        window = MultiFileCustomizer(npy_files)
        window.show()
        app.exec()