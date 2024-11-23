import argparse
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import numpy as np
import serial
from serial.tools import list_ports
import json
from classification.utils.plots import plot_specgram
from threading import Thread
from queue import Queue
import plotly.graph_objs as go
import subprocess
import base64


# Constants
MEL_PREFIX = "DF:HEX:"
CONFIG_PREFIX = "DF:CFG:"  # Follows a JSON string
FREQ_SAMPLING = 10200
MELVEC_LENGTH = 19
N_MELVECS = 19
current_config = f"melvec_length={MELVEC_LENGTH}\n n_melvecs={N_MELVECS}"

dt = np.dtype(np.uint16).newbyteorder("<")

# Queue for real-time data communication
data_queue = Queue()
history = []  # Persistent buffer for MEL spectrogram history


# Function to parse incoming serial buffer
def parse_buffer(line):
    global MELVEC_LENGTH, N_MELVECS, current_config
    line = line.strip()
    print(line)
    if line.startswith(MEL_PREFIX):
        return bytes.fromhex(line[len(MEL_PREFIX):])
    elif line.startswith(CONFIG_PREFIX):
        print("Received configuration data.")
        config = json.loads(line[len(CONFIG_PREFIX):])
        MELVEC_LENGTH = config.get("melvec_length", MELVEC_LENGTH)
        N_MELVECS = config.get("n_melvecs", N_MELVECS)
        print(f"Updated MEL vector length: {MELVEC_LENGTH}")
        print(f"Updated number of MEL vectors: {N_MELVECS}")
        current_config = f"melvec_length={MELVEC_LENGTH}\n n_melvecs={N_MELVECS}"
        return None
    else:
        return None


# Serial reader function
def reader(port, data_queue):
    ser = serial.Serial(port=port, baudrate=115200)
    while True:
        line = ""
        while not line.endswith("\n"):
            line += ser.read_until(b"\n").decode("ascii")
        buffer = parse_buffer(line)
        if buffer is not None:
            buffer_array = np.frombuffer(buffer, dtype=dt)
            data_queue.put(buffer_array)


# Dash app setup
app = dash.Dash(__name__, title="UART Reader", update_title=None)

app.layout = html.Div(
    [
        html.Div([
            html.Label("Configuration:", style={"margin-right": "10px"}),
            html.Pre(id="config-text", children="Config 1", style={"display": "inline-block", "margin-right": "10px"}),
            dcc.Upload(
                id="upload-model",
                children=html.Button("Load AI Model", style={"margin-right": "10px"}),
                multiple=False
            ),            html.Div(id="model-status", style={"display": "inline-block"})
        ], style={"padding": "10px", "display": "flex", "align-items": "center", "justify-content": "space-between"}),
        dcc.Graph(id="heatmap", style={"height": "calc(100vh - 60px)", "width": "100%"}),
        dcc.Interval(id="interval", interval=1000, n_intervals=0)
    ]
)

@app.callback(
    Output("heatmap", "figure"),
    [Input("interval", "n_intervals")]
)
def update_graph(n_intervals):
    global history
    while not data_queue.empty():
        melvec = data_queue.get()
        # Reshape and store the MEL spectrogram in history
        mel_spectrogram = melvec.reshape((N_MELVECS, MELVEC_LENGTH)).T
        history = [mel_spectrogram]
        # Keep only the last 10 spectrograms in history to limit memory usage
        if len(history) > 10:
            history.pop(0)

    # Combine the history into a single 2D array
    if history:
        combined_spectrogram = np.hstack(history)
        fig = go.Figure(
            data=go.Heatmap(
                z=combined_spectrogram,
                colorscale="Viridis",
                colorbar=dict(title="Amplitude")
            )
        )
        fig.update_layout(
            title=f"MEL Spectrogram #{n_intervals}",
            xaxis_title="Mel Vector (History)",
            yaxis_title="Frequency Bin",
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig

    # Return an empty figure if no data is available yet
    return go.Figure()

@app.callback(
    Output("config-text", "children"),
    [Input("interval", "n_intervals")]
)
def update_config_text(n_intervals):
    global current_config
    return current_config

@app.callback(
    Output("model-status", "children"),
    [Input("upload-model", "contents")],
    [State("upload-model", "filename")]
)
def load_model(contents, filename):
    if contents is None:
        return ""
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Save the uploaded file to a temporary location
    with open(filename, 'wb') as f:
        f.write(decoded)
    
    # Load the AI model based on the uploaded file
    # Replace this with your actual model loading code
    model_status = f"Loaded AI model : {filename}"
    return model_status


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--port", help="Port for serial communication")
    args = argParser.parse_args()

    print("uart-reader launched...\n")

    if args.port is None:
        print("No port specified. Here is a list of available serial ports:")
        print("================")
        ports = list(list_ports.comports())
        for p in ports:
            print(p.device)
        print("================")
        print("Launch this script with [-p PORT_REF] to access the communication port.")
    else:
        # Start the serial reader thread
        serial_thread = Thread(target=reader, args=(args.port, data_queue), daemon=True)
        serial_thread.start()

        # Run Dash server
        url = "http://127.0.0.1:8050"
        subprocess.run("clip", text=True, input=url)
        print("The URL for the Dash app has been copied to your clipboard.")
        app.run_server(debug=True, use_reloader=False, port=8050)
