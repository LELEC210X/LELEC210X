import os
import csv
import numpy as np
from dash import Dash, dcc, html, Input, Output, State, ctx
from dash.dependencies import MATCH, ALL
import plotly.graph_objs as go
import webview
from numba import njit

# Global Defaults
OFFSET_DIVISIONS_CH1 = -6.0
OFFSET_DIVISIONS_CH2 = -6.0
VOLTAGE_DIVISIONS_CH1 = 500.0  # mV
VOLTAGE_DIVISIONS_CH2 = 500.0  # mV
TIME_DIVISIONS = 500.0  # ms
RESISTANCE = 100.0  # Ohm

# App Setup
app = Dash(__name__)
server = app.server

# Smooth Signal Function
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

# Layout
app.layout = html.Div([
    html.Div([
        html.Button('Select Folder', id='folder-select-btn', n_clicks=0),
        html.Div(id='selected-folder', style={'marginTop': '10px'}),
        html.Div(id='file-list', style={'marginTop': '20px'})
    ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    html.Div([
        html.Div([
            html.Div([
                dcc.Checklist(
                    options=[
                        {'label': 'Voltage', 'value': 'voltage'},
                        {'label': 'Power', 'value': 'power'}
                    ],
                    value=['voltage', 'power'],
                    id='plot-options',
                    inline=True
                )
            ], style={'marginBottom': '20px'}),
            html.Div([
                html.Label('Smoothing Window:'),
                dcc.Slider(1, 50, 1, value=10, id='smoothing-window-slider')
            ], style={'marginBottom': '20px'}),
            html.Div(id='file-specific-controls', style={'marginBottom': '20px'})
        ], style={'width': '75%', 'marginLeft': '20px', 'display': 'inline-block'}),
        dcc.Graph(id='signal-plot', style={'height': '60vh'})
    ])
])

# Callbacks
@app.callback(
    [Output('file-list', 'children'), Output('selected-folder', 'children')],
    [Input('folder-select-btn', 'n_clicks')]
)
def update_file_list(n_clicks):
    if n_clicks == 0:
        return ["No files loaded"], "Select a folder"

    folder_path = os.getcwd()  # Replace with file dialog if needed
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    if not files:
        return ["No CSV files found"], folder_path

    file_links = [
        html.Div([
            dcc.Checklist(
                options=[{'label': file, 'value': file}],
                id={'type': 'file-checkbox', 'index': file}
            )
        ])
        for file in files
    ]
    return file_links, folder_path


@app.callback(
    Output('signal-plot', 'figure'),
    [Input({'type': 'file-checkbox', 'index': ALL}, 'value'),
     Input('plot-options', 'value'),
     Input('smoothing-window-slider', 'value')]
)
def update_plot(selected_files, plot_options, smoothing_window):
    # Flatten selected files, handle None or empty cases
    if selected_files is None or not any(selected_files):
        return go.Figure()

    selected_files = [file for sublist in selected_files for file in (sublist or [])]

    if not selected_files:
        return go.Figure()

    folder_path = os.getcwd()
    fig = go.Figure()

    for file in selected_files:
        try:
            # Ensure correct path join
            file_path = os.path.join(folder_path, file)
            metadata, header, data = read_csv(file_path)

            if data is None or data.shape[1] < 2:
                print(f"Skipping {file}: insufficient data columns")
                continue

            time = data[:, 0]
            voltage = data[:, 1:] * VOLTAGE_DIVISIONS_CH1

            for idx, signal in enumerate(voltage.T):
                if 'voltage' in plot_options:
                    fig.add_trace(go.Scatter(x=time, y=signal, name=f'{file} Voltage {idx+1}'))

                if 'power' in plot_options:
                    current = signal / RESISTANCE
                    power = signal * current * 1e3  # Convert to mW
                    smoothed_power = smooth_signal(power, smoothing_window)
                    fig.add_trace(go.Scatter(x=time, y=smoothed_power, name=f'{file} Power {idx+1}'))
        except Exception as e:
            print(f"Error processing {file}: {e}")

    # Correct method to update figure layout
    fig.update_layout(
        title="Signal Plot",
        xaxis_title="Time (s)",
        yaxis_title="Value",
        legend_title="Signals"
    )
    return fig


# Pywebview Integration
if __name__ == '__main__':
    def run_app():
        app.run_server(debug=True, port=8050, use_reloader=False)

    run_app()
