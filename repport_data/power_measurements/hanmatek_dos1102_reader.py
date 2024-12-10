# Tool to read .csv files from Hanmatek DOS1102 oscilloscope

import csv
import numpy as np
import matplotlib.pyplot as plt
import os

NAME_BASE = "data_26"

OFFSET_DIVISIONS_CH1 = -6.0
OFFSET_DIVISIONS_CH2 = -6.0
VOLTAGE_DIVISIONS_CH1 = 500.0 # mV
VOLTAGE_DIVISIONS_CH2 = 500.0 # mV
TIME_DIVISIONS = 500.0 # ms (or 200ms)
RESISTANCE = 100.0 # Ohm

def read_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        metadata = {}
        data = []
        for row in reader:
            if not row:  # Skip empty rows
                continue
            if row[0].strip() == 'index':
                header = row
                break
            else:
                key = row[0].strip()
                values = row[1:]
                metadata[key] = values
        for row in reader:
            if not row:  # Skip empty rows
                continue
            try:
                data.append([float(x) for x in row])
            except ValueError:
                continue
    data = np.array(data)
    return metadata, header, data

def process_data(metadata, header, data):
    time_interval = float(metadata["Time interval        :"][0].replace('uS', '')) * 1e-6
    voltage_per_adc_value = float(metadata["Voltage per ADC value:"][0].replace('mV', '')) * 1e-3
    time = data[:,0] * time_interval
    channels = data[:,1:] * voltage_per_adc_value
    for i in range(channels.shape[1]):
        if i == 0:
            channels[:,i] = (channels[:,i] - OFFSET_DIVISIONS_CH1) * VOLTAGE_DIVISIONS_CH1
        else:
            channels[:,i] = (channels[:,i] - OFFSET_DIVISIONS_CH2) * VOLTAGE_DIVISIONS_CH2
    return time, channels

def smooth_signal(signal, window_size=10):
    window = np.ones(window_size) / window_size
    return np.convolve(signal, window, mode='same')

def plot_data(metadata, header, data, name, transparent=False):
    time, channels = process_data(metadata, header, data)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))  # Create two subplots
    for i in range(channels.shape[1]):
        ax1.plot(time, channels[:,i], label=header[i+1], linewidth=0.5)  # Make the lines thinner
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (mV)')
    ax1.legend()
    
    current = (channels[:,0] - channels[:,1]) / RESISTANCE
    power = channels[:,0] * current * 1e3  # Convert to mW
    smoothed_power = smooth_signal(power, 5)
    
    default_blue = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
    if transparent:
        ax2.plot(time, power, label='Power (mW)', linewidth=0.5, alpha=0.5, color=default_blue)
        ax2.plot(time, smoothed_power, label='Smoothed Power (mW)', linewidth=0.5, alpha=1.0, color=default_blue)
    else :
        ax2.plot(time, power, label='Power (mW)', linewidth=0.5, color=default_blue)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Power (mW)')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f"{name}.pdf")
    plt.savefig(f"{name}.png")
    #plt.show()

if __name__ == '__main__':
    for file in os.listdir():
        if file.startswith(NAME_BASE) and file.endswith('.csv'):
            metadata, header, data = read_csv(file)
            plot_data(metadata, header, data, file.replace('.csv', '') + '_processed', transparent=True)
            plot_data(metadata, header, data, file.replace('.csv', '') + '_raw', transparent=False)