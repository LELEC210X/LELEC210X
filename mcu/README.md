# MCU

Files related to the mcu part.

## Installation

All dependencies should be installed with the following command:

```bash
rye sync
```

## Usage

To launch the UART utility, run:

```bash
rye run uart_reader
```

or

```bash
rye run python src/mcu/uart_reader.py
```

> [!NOTE]
> The utility will launch in GUI mode by default, if needed in CLI mode, please use the `-c, --cli` flag.

### Options

- `-c, --cli`: Whether to run the CLI application.
- `-p, --port TEXT`: The serial port to read data from (default: `-- No COM --`).
- `-b, --baudrate INTEGER`: The baudrate of the serial port (default: `115200`).
- `-s, --sampling-frequency INTEGER`: The sampling frequency of the ADC (default: `10200`).
- `-m, --max-adc-value INTEGER`: The maximum value of the ADC (default: `4096`).
- `-v, --vdd FLOAT`: The voltage of the power supply (default: `3.3`).
- `-o, --plot-output-type [WEB|FILE]`: The type of output for the plot (default: `WEB`).
- `-l, --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]`: The level of logging (default: `INFO`).
- `-f, --log-file`: Whether to log to a file (Not modifiable at runtime).
- `-w, --overwrite-audio`: Whether to overwrite the audio folder.
- `-a, --audio-output-type [WAV|OGG]`: The type of output for the audio (default: `WAV`).
- `-d, --audio-output-folder TEXT`: The folder to save the audio files (default: `audio_files`).
