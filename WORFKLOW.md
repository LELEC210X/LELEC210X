# Workflow to follow to send guess easily
## Sending user
The one with the board connect via uart (those steps are not necessary as long as board is powered)
### 1. Launch uart reader
```bash
cd mcu/hands_on_main_app
uv run uart-reader.py
```

## Receiving user
Place yourself on the root folder of the project then execute those steps
### 1. Start GNURadio Companion in a external terminal
```bash
uv sync
uv run gnuradio-companion
```

### 2. Start the server
```bash
uv run leaderboard serve --open
```

### 3. Start the sending guess pipe
```bash
uv run auth --tcp-address tcp://127.0.0.1:10000 --no-authenticate | uv run python classifier_pipe.py
```