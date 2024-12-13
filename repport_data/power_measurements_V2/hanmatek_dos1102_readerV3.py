import os
import csv
import numpy as np
from dash import Dash, dcc, html, Input, Output, State, ctx
from dash.dependencies import MATCH, ALL
import dash
import plotly.graph_objs as go
from numba import njit
from plotly.subplots import make_subplots
import ast

# Global Constants
RESISTANCE = 100.0  # Ohm
VOLTAGE_SCALING = 1000.0  # Convert V to mV

# App Setup
app = Dash(__name__)
server = app.server

# Ensure Plots folder exists
PLOTS_FOLDER = os.path.join(os.getcwd(), "Plots")
os.makedirs(os.path.join(PLOTS_FOLDER, "png"), exist_ok=True)
os.makedirs(os.path.join(PLOTS_FOLDER, "pdf"), exist_ok=True)

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

def process_data(metadata, data):
    """Process raw data with proper scaling"""
    time_interval = float(metadata["Time interval        :"][0].replace('uS', '')) * 1e-6
    voltage_per_adc = float(metadata["Voltage per ADC value:"][0].replace('mV', '')) * 1e-3
    
    time = data[:, 0] * time_interval
    ch1 = data[:, 1] * voltage_per_adc * VOLTAGE_SCALING  # Convert to mV
    ch2 = data[:, 2] * voltage_per_adc * VOLTAGE_SCALING  # Convert to mV
    
    current = (ch1 - ch2) / RESISTANCE
    power = ch1 * current  # Power in mW
    
    return time, ch1, ch2, power

# Update app layout with fixed graph and scrollable controls:

app.layout = html.Div([
    # Main container with fixed height
    html.Div([
        # Left sidebar
        html.Div([
            html.Button('Select Folder', id='folder-select-btn', n_clicks=0),
            html.Div(id='selected-folder', style={'marginTop': '10px'}),
            html.Div(id='file-list', style={'marginTop': '20px'})
        ], style={
            'width': '20%',
            'position': 'fixed',
            'left': '10px',
            'top': '10px',
            'bottom': '10px',
            'overflowY': 'auto',
            'padding': '10px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '5px'
        }),

        # Main content
        html.Div([
            # Graphs container (graphs MUST be separated, as it will avoid the layout breaking)
            html.Div([
                dcc.Graph( # Secondary graph for voltage 
                    id='signal-plot-voltage',
                    style={'height': '80vh'}
                ),
                dcc.Graph( # Primary graph for power
                    id='signal-plot-power',
                    style={'height': '80vh'}
                )
            ], style={
                'marginBottom': '20px',
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '5px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'height': '80vh'
            }),

            # Save button
            html.Button(
                'Save Graphs',
                id='save-graphs-btn',
                n_clicks=0,
                style={
                    'width': '200px',
                    'height': '40px',
                    'fontSize': '16px',
                    'marginBottom': '20px',
                    'backgroundColor': '#4CAF50',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                }
            ),

            # Controls section with scroll
            html.Div([
                html.Div(id='individual-graph-controls')
            ], style={
                'height': 'calc(20vh - 60px)',
                'overflowY': 'auto',
                'padding': '15px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '5px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ], style={
            'width': '75%',
            'marginLeft': '22%',
            'paddingTop': '10px',
            'height': '100vh',
            'overflow': 'hidden'
        })
    ], style={
        'height': '100vh',
        'overflow': 'hidden'
    })
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

# Update generate_individual_controls function for better styling:
def generate_individual_controls(selected_files):
    if not selected_files:
        return []

    selected_files = [file for sublist in selected_files for file in (sublist or [])]
    controls = []
    
    for file in selected_files:
        controls.append(html.Div([
            html.H5(file, style={'marginBottom': '10px'}),
            html.Div([
                # Left column - Offsets
                html.Div([
                    html.Label('Horizontal Offset (%):'),
                    dcc.Input(
                        id={'type': 'hoffset-input', 'index': file},
                        type='number',
                        value=0,
                        style={'width': '100%', 'marginBottom': '10px'}
                    ),
                    html.Label('Vertical Offset (%):'),
                    dcc.Input(
                        id={'type': 'voffset-input', 'index': file},
                        type='number',
                        value=0,
                        style={'width': '100%'}
                    ),
                ], style={'width': '30%', 'marginRight': '20px', 'display': 'inline-block'}),
                
                # Right column - Sliders
                html.Div([
                    html.Label('Trim Range:'),
                    dcc.RangeSlider(
                        id={'type': 'trim-slider', 'index': file},
                        min=0, max=100, step=1,
                        value=[0, 100],
                        marks={0: '0%', 50: '50%', 100: '100%'},
                    ),
                    html.Label('Smoothing:'),
                    dcc.Slider(
                        id={'type': 'smoothing-slider', 'index': file},
                        min=0, max=50, step=1,
                        value=0,
                        marks={0: '0', 25: '25', 50: '50'},
                    ),
                ], style={'width': '65%', 'display': 'inline-block'})
            ], style={'display': 'flex'})
        ], style={
            'padding': '15px',
            'marginBottom': '15px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'backgroundColor': 'white'
        }))
    
    return controls

@app.callback(
    Output('individual-graph-controls', 'children'),
    [Input({'type': 'file-checkbox', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def generate_individual_controls(selected_files):
    if not selected_files:
        return []

    selected_files = [file for sublist in selected_files for file in (sublist or [])]

    controls = []
    for file in selected_files:
        controls.append(html.Div([
            html.H5(file),
            html.Label('Offset:'),
            dcc.Input(id={'type': 'offset-input', 'index': file}, type='number', value=0),
            html.Label('Trim Range:'),
            dcc.RangeSlider(id={'type': 'trim-slider', 'index': file}, min=0, max=100, step=1, value=[0, 100]),
            html.Label('Smoothing:'),
            dcc.Slider(1, 50, 1, value=10, id={'type': 'smoothing-slider', 'index': file}),
        ], style={'marginBottom': '20px'}))
    return controls

@app.callback(
    Output('signal-plot', 'figure'),
    [Input({'type': 'file-checkbox', 'index': ALL}, 'value')],
    [State({'type': 'hoffset-input', 'index': ALL}, 'value'),
     State({'type': 'voffset-input', 'index': ALL}, 'value'),
     State({'type': 'trim-slider', 'index': ALL}, 'value'),
     State({'type': 'smoothing-slider', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def update_plot(selected_file_values, hoffset_values, voffset_values, trim_range_values, smoothing_values):
    # Build selected_files list
    selected_files = []
    for val in selected_file_values:
        if val:
            selected_files.extend(val)

    if not selected_files:
        fig = make_subplots(rows=2, cols=1,
                            subplot_titles=('Voltage Signals', 'Power Analysis'),
                            vertical_spacing=0.15)
        fig.update_layout(height=800, showlegend=True)
        return fig

    # Build controls mapping
    controls = {}
    ctx_states = dash.callback_context.states
    for key, value in ctx_states.items():
        id_str, prop = key.split('.')
        id_dict = ast.literal_eval(id_str)
        index = id_dict['index']
        control_type = id_dict['type']
        if index not in controls:
            controls[index] = {}
        if control_type == 'hoffset-input':
            controls[index]['hoffset'] = value
        elif control_type == 'voffset-input':
            controls[index]['voffset'] = value
        elif control_type == 'trim-slider':
            controls[index]['trim_range'] = value
        elif control_type == 'smoothing-slider':
            controls[index]['smoothing'] = value

    # Create figure
    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Voltage Signals', 'Power Analysis'),
                        vertical_spacing=0.15)

    for file in selected_files:
        control = controls.get(file, {})
        hoffset = control.get('hoffset', 0)
        voffset = control.get('voffset', 0)
        trim_range = control.get('trim_range', [0, 100])
        smoothing = control.get('smoothing', 0)

        try:
            file_path = os.path.join(os.getcwd(), file)
            metadata, header, data = read_csv(file_path)
            if data is None or data.shape[1] < 3:
                continue

            time, ch1, ch2, power = process_data(metadata, data)

            # Apply trimming
            start_idx = int(trim_range[0] / 100 * len(time))
            end_idx = int(trim_range[1] / 100 * len(time))

            # Apply offsets
            time_offset = (hoffset / 100) * (time.max() - time.min())
            voltage_offset = (voffset / 100) * (max(ch1.max(), ch2.max()) - min(ch1.min(), ch2.min()))

            trimmed_time = time[start_idx:end_idx] + time_offset
            trimmed_ch1 = ch1[start_idx:end_idx] + voltage_offset
            trimmed_ch2 = ch2[start_idx:end_idx] + voltage_offset
            trimmed_power = power[start_idx:end_idx]

            # Apply smoothing
            if smoothing > 0:
                trimmed_ch1 = smooth_signal(trimmed_ch1, int(smoothing))
                trimmed_ch2 = smooth_signal(trimmed_ch2, int(smoothing))
                trimmed_power = smooth_signal(trimmed_power, int(smoothing))

            # Add traces
            fig.add_trace(
                go.Scatter(x=trimmed_time, y=trimmed_ch1,
                           name=f'{file} CH1',
                           line=dict(width=1)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=trimmed_time, y=trimmed_ch2,
                           name=f'{file} CH2',
                           line=dict(width=1)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=trimmed_time, y=trimmed_power,
                           name=f'{file} Power',
                           line=dict(width=1)),
                row=2, col=1
            )

        except Exception as e:
            print(f"Error processing {file}: {str(e)}")

    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Signal Analysis"
    )
    fig.update_xaxes(title_text="Time (s)", row=1, col=1)
    fig.update_xaxes(title_text="Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Voltage (mV)", row=1, col=1)
    fig.update_yaxes(title_text="Power (mW)", row=2, col=1)

    return fig

@app.callback(
    Output('save-graphs-btn', 'n_clicks'),
    [Input('save-graphs-btn', 'n_clicks')],
    [State('signal-plot', 'figure')]
)
def save_graphs(n_clicks, figure):
    if n_clicks > 0:
        png_path = os.path.join(PLOTS_FOLDER, "png", "plot.png")
        pdf_path = os.path.join(PLOTS_FOLDER, "pdf", "plot.pdf")
        fig = go.Figure(figure)
        fig.write_image(png_path)
        fig.write_image(pdf_path)
    return 0

# Run the App
if __name__ == '__main__':
    app.run_server(debug=True, port=8050, use_reloader=False)
