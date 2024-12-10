# Tool to read .csv files from Hanmatek DOS1102 oscilloscope

import csv
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.widgets import Slider, Button
from numba import njit

NAME_BASE = "data_26"

OFFSET_DIVISIONS_CH1 = -6.0
OFFSET_DIVISIONS_CH2 = -6.0
VOLTAGE_DIVISIONS_CH1 = 500.0  # mV
VOLTAGE_DIVISIONS_CH2 = 500.0  # mV
TIME_DIVISIONS = 500.0  # ms
RESISTANCE = 100.0  # Ohm

stop_execution = False  # Global flag to stop execution

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

def process_data(metadata, header, data):
    time_interval = (
        float(metadata["Time interval        :"][0].replace('uS', '')) * 1e-6
    )
    voltage_per_adc_value = (
        float(metadata["Voltage per ADC value:"][0].replace('mV', '')) * 1e-3
    )
    time = data[:, 0] * time_interval
    channels = data[:, 1:] * voltage_per_adc_value
    for i in range(channels.shape[1]):
        if i == 0:
            channels[:, i] = (
                channels[:, i] - OFFSET_DIVISIONS_CH1
            ) * VOLTAGE_DIVISIONS_CH1
        else:
            channels[:, i] = (
                channels[:, i] - OFFSET_DIVISIONS_CH2
            ) * VOLTAGE_DIVISIONS_CH2
    return time, channels

@njit
def smooth_signal(signal, window_size=10):
    n = len(signal)
    smoothed = np.empty(n)
    half_window = window_size // 2
    for i in range(n):
        start = max(0, i - half_window)
        end = min(n, i + half_window + 1)
        total = 0.0
        count = 0
        for j in range(start, end):
            total += signal[j]
            count += 1
        smoothed[i] = total / count
    return smoothed

def interactive_plot(metadata, header, data, name):
    global stop_execution  # Access the global flag
    time, channels = process_data(metadata, header, data)
    current = (channels[:, 0] - channels[:, 1]) / RESISTANCE
    power = channels[:, 0] * current * 1e3  # Convert to mW
    smoothed_power = smooth_signal(power, 10)

    # Set up the figure and axes
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))
    plt.subplots_adjust(bottom=0.3)

    # Plot the data and keep references to the line objects
    ax_voltage = axs[0]
    voltage_lines = []
    for i in range(channels.shape[1]):
        (line,) = ax_voltage.plot(
            time, channels[:, i], label=header[i + 1], linewidth=0.5
        )
        voltage_lines.append(line)
    ax_voltage.set_xlabel('Time (s)')
    ax_voltage.set_ylabel('Voltage (mV)')
    ax_voltage.legend()
    ax_voltage.set_title('Signal')

    ax_power = axs[1]
    default_blue = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
    (line_power,) = ax_power.plot(
        time,
        power,
        label='Power (mW)',
        linewidth=0.5,
        alpha=0.5,
        color=default_blue,
    )
    (line_smoothed,) = ax_power.plot(
        time,
        smoothed_power,
        label='Smoothed Power (mW)',
        linewidth=0.5,
        color=default_blue,
    )
    ax_power.set_xlabel('Time (s)')
    ax_power.set_ylabel('Power (mW)')
    ax_power.legend()
    ax_power.set_title('Power Signal')

    # Define axes for sliders and buttons
    ax_slider_start = plt.axes([0.1, 0.15, 0.8, 0.03])
    ax_slider_end = plt.axes([0.1, 0.1, 0.8, 0.03])
    ax_button_save = plt.axes([0.7, 0.025, 0.1, 0.04])
    ax_button_close = plt.axes([0.81, 0.025, 0.1, 0.04])

    # Create sliders
    slider_start = Slider(
        ax_slider_start, 'Start', time.min(), time.max(), valinit=time.min()
    )
    slider_end = Slider(
        ax_slider_end, 'End', time.min(), time.max(), valinit=time.max()
    )

    # Create buttons
    button_save = Button(ax_button_save, 'Save Plots')
    button_close = Button(ax_button_close, 'Close All')

    def update(val):
        start = slider_start.val
        end = slider_end.val
        if start >= end:
            return
        indices = np.where((time >= start) & (time <= end))

        cropped_time = time[indices]
        cropped_channels = channels[indices]
        cropped_power = power[indices]
        cropped_smoothed_power = smoothed_power[indices]

        # Update voltage plots
        for i, line in enumerate(voltage_lines):
            line.set_data(cropped_time, cropped_channels[:, i])
        ax_voltage.set_xlim(cropped_time[0], cropped_time[-1])
        ax_voltage.relim()
        ax_voltage.autoscale_view()

        # Update power plots
        line_power.set_data(cropped_time, cropped_power)
        line_smoothed.set_data(cropped_time, cropped_smoothed_power)
        ax_power.set_xlim(cropped_time[0], cropped_time[-1])
        ax_power.relim()
        ax_power.autoscale_view()

        fig.canvas.draw_idle()

    def save_plots(event):
        start = slider_start.val
        end = slider_end.val
        if start >= end:
            print("Start time must be less than end time.")
            return
        indices = np.where((time >= start) & (time <= end))
        cropped_time = time[indices]
        cropped_channels = channels[indices]
        cropped_power = power[indices]
        cropped_smoothed_power = smoothed_power[indices]

        # Save raw plots
        fig_raw, (ax1_raw, ax2_raw) = plt.subplots(2, 1, figsize=(12, 8))
        for i in range(channels.shape[1]):
            ax1_raw.plot(
                time, channels[:, i], label=header[i + 1], linewidth=0.5
            )
        ax1_raw.set_xlabel('Time (s)')
        ax1_raw.set_ylabel('Voltage (mV)')
        ax1_raw.legend()
        ax1_raw.set_title('Full Signal - Raw')

        ax2_raw.plot(
            time,
            power,
            label='Power (mW)',
            linewidth=0.5,
            alpha=0.5,
            color=default_blue,
        )
        ax2_raw.plot(
            time,
            smoothed_power,
            label='Smoothed Power (mW)',
            linewidth=0.5,
            color=default_blue,
        )
        ax2_raw.set_xlabel('Time (s)')
        ax2_raw.set_ylabel('Power (mW)')
        ax2_raw.legend()
        ax2_raw.set_title('Full Power Signal - Raw')

        fig_raw.tight_layout()
        fig_raw.savefig(f"{name}_raw.pdf")
        fig_raw.savefig(f"{name}_raw.png")
        plt.close(fig_raw)

        # Save processed (cropped) plots
        fig_proc, (ax1_proc, ax2_proc) = plt.subplots(2, 1, figsize=(12, 8))
        for i in range(cropped_channels.shape[1]):
            ax1_proc.plot(
                cropped_time,
                cropped_channels[:, i],
                label=header[i + 1],
                linewidth=0.5,
            )
        ax1_proc.set_xlabel('Time (s)')
        ax1_proc.set_ylabel('Voltage (mV)')
        ax1_proc.legend()
        ax1_proc.set_title('Cropped Signal - Processed')

        ax2_proc.plot(
            cropped_time,
            cropped_power,
            label='Power (mW)',
            linewidth=0.5,
            alpha=0.5,
            color=default_blue,
        )
        ax2_proc.plot(
            cropped_time,
            cropped_smoothed_power,
            label='Smoothed Power (mW)',
            linewidth=0.5,
            color=default_blue,
        )
        ax2_proc.set_xlabel('Time (s)')
        ax2_proc.set_ylabel('Power (mW)')
        ax2_proc.legend()
        ax2_proc.set_title('Cropped Power Signal - Processed')

        fig_proc.tight_layout()
        fig_proc.savefig(f"{name}_processed.pdf")
        fig_proc.savefig(f"{name}_processed.png")
        plt.close(fig_proc)

        print(f"Plots saved for {name}.")

    def close_all(event):
        global stop_execution
        stop_execution = True
        plt.close(fig)

    def on_close(event):
        global stop_execution
        stop_execution = True

    # Connect events
    slider_start.on_changed(update)
    slider_end.on_changed(update)
    button_save.on_clicked(save_plots)
    button_close.on_clicked(close_all)
    fig.canvas.mpl_connect('close_event', save_plots)
    plt.show()

if __name__ == '__main__':
    for file in os.listdir():
        if file.startswith(NAME_BASE) and file.endswith('.csv'):
            metadata, header, data = read_csv(file)
            interactive_plot(metadata, header, data, file.replace('.csv', ''))
            if stop_execution:
                break  # Stop processing if the window was closed