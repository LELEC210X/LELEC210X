import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os

# Choose which library to use for plotting

USE_PLOT = ['matplotlib', 'plotly'][1]
SMOOTHING_WINDOW = 10

# Plot power and voltage vs time

def plot_power_matplotlib(file_path):
    data = pd.read_csv(file_path, skiprows=8)

    Rshunt = 100

    #Smooth the data
    data['CH1_Voltage(mV)'] = data['CH1_Voltage(mV)'].rolling(window=SMOOTHING_WINDOW).mean()
    data['CH2_Voltage(mV)'] = data['CH2_Voltage(mV)'].rolling(window=SMOOTHING_WINDOW).mean()

    data['Power'] = np.subtract(data['CH2_Voltage(mV)'], data['CH1_Voltage(mV)']) * data['CH2_Voltage(mV)'] / (Rshunt * 1000)
    data['Time']  = data['index'] / 1000

    trimmed_file_path = file_path[-30:] if len(file_path) > 30 else file_path.ljust(30)
    print(trimmed_file_path, 'Power:', data['Power'].abs().mean())

    fig, ax = plt.subplots()
    ax.plot(data['Time'], data['CH1_Voltage(mV)'] / 1000, label='CH1 (V)', alpha=0.5)
    ax.plot(data['Time'], data['CH2_Voltage(mV)'] / 1000, label='CH2 (V)', alpha=0.5)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Voltage (V)')
    ax.legend()
    ax.set_ylim(0, max(data['CH2_Voltage(mV)'].max(), data['CH1_Voltage(mV)'].max()) / 1000 * 1.1)

    ax2 = ax.twinx()
    ax2.plot(data['Time'], data['Power'].abs(), label='Power (mW)', color='red', alpha=0.5)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Power (mW)')
    ax2.set_title('Power & Voltage vs Time - ' + file_path)
    ax2.legend()
    ax2.set_ylim(0, data['Power'].abs().max() * 1.1)

def plot_power_plotly(file_path):
    data = pd.read_csv(file_path, skiprows=8)

    Rshunt = 100

    # Smooth the data
    data['CH1_Voltage(mV)'] = data['CH1_Voltage(mV)'].rolling(window=SMOOTHING_WINDOW).mean()
    data['CH2_Voltage(mV)'] = data['CH2_Voltage(mV)'].rolling(window=SMOOTHING_WINDOW).mean()

    data['Power'] = np.subtract(data['CH2_Voltage(mV)'], data['CH1_Voltage(mV)']) * data['CH2_Voltage(mV)'] / (Rshunt * 1000)
    data['Time']  = data['index'] / 1000

    trimmed_file_path = file_path[-30:] if len(file_path) > 30 else file_path.ljust(30)
    print(trimmed_file_path, 'Power:', data['Power'].abs().mean())

    # Create a trace for CH1 Voltage
    trace1 = go.Scatter(
        x=data['Time'],
        y=data['CH1_Voltage(mV)'] / 1000,
        mode='lines',
        name='CH1 (V)'
    )

    # Create a trace for CH2 Voltage
    trace2 = go.Scatter(
        x=data['Time'],
        y=data['CH2_Voltage(mV)'] / 1000,
        mode='lines',
        name='CH2 (V)'
    )

    # Create a trace for Power
    trace3 = go.Scatter(
        x=data['Time'],
        y=data['Power'].abs(),
        mode='lines',
        name='Power (mW)',
        yaxis='y2'
    )

    layout = go.Layout(
        title='Power & Voltage vs Time - ' + file_path,
        xaxis=dict(title='Time (s)'),
        yaxis=dict(title='Voltage (V)'),
        yaxis2=dict(title='Power (mW)', overlaying='y', side='right'),
        autosize=False,
        width=500,
        height=500,
    )

    fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
    fig.show()

if __name__ == '__main__':
    if False:
        file_number = 17
        start = 0
        end = 4
        for i in range(start, end+1):
            try:
                plot_power('data_'+str(file_number)+'_{:03d}.csv'.format(i))
            except:
                break

    # plot all files in ./data/ folder
    for file in os.listdir('data/'):
        if file.endswith('.csv'):
            if USE_PLOT == 'matplotlib':
                plot_power_matplotlib('data/' + file)
            elif USE_PLOT == 'plotly':
                plot_power_plotly('data/' + file)
            else:
                print('Invalid USE_PLOT value')
                break
plt.show()
