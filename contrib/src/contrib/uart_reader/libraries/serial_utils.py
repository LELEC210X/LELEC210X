# Standard Library
import logging
import sys
import time
from queue import Queue
from threading import Lock
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from serial import STOPBITS_ONE, Serial, SerialException
from serial.tools import list_ports


class SerialController(QThread):
    """
    Thread for handling serial communication with the MCU.
    It runs in the background constantly, waiting for a connection to a serial port, then waits for data and emits signals.

    If a prefix is registered, the data_received_prefix signal is emitted with the prefix and the data, and it won't be emitted by data_received_normal.
    If no prefix is registered, the data_received_normal signal is emitted with the data.
    If a error or sudden disconnection occurs, the error_occurred signal is emitted with the error message, and the data_received_normal signal is emitted with a TERMINATE string.

    Signals:
        data_received_prefix: Emitted when data is received from serial port, with the registered prefix
        data_received_normal: Emitted when data is received from serial port
        connection_state: Emitted when connection state changes
        error_occurred: Emitted when an error occurs
    """

    # Emitted when data is received from serial port, with the registered prefix
    data_received_prefix = pyqtSignal(str, str)
    # Emitted when data is received from serial port
    data_received_normal = pyqtSignal(str)
    # Emitted when connection state changes
    connection_state = pyqtSignal(bool)
    # Emitted when an error occurs
    error_occurred = pyqtSignal(str)

    # Registered prefixes
    _prefixes = set()

    # API
    def available_ports(self) -> dict:
        """
        Return a list of available serial ports and their descriptions.
        Example :
            {
                'COM1': 'Arduino Uno',
                'COM3': 'ST-Link Microcontroller',
            }
        """
        return {port.device: port.description for port in list_ports.comports()}

    def register_prefix(self, prefix: str) -> None:
        """Register a prefix to be used for data_received_prefix signal."""
        self._prefixes.add(prefix)
        self.logger.debug(f"Registered prefix: {prefix}")

    def unregister_prefix(self, prefix: str) -> None:
        """Unregister a prefix."""
        self._prefixes.discard(prefix)
        self.logger.debug(f"Unregistered prefix: {prefix}")

    def unregister_all_prefixes(self) -> None:
        """Unregister all prefixes."""
        self._prefixes.clear()
        self.logger.debug("Unregistered all prefixes")

    def write_message(self, message: str) -> None:
        """Write a message to the serial port."""
        if self.is_connected and message:
            self._write_queue.put(message)
        else:
            self.logger.warning("Cannot write message: not connected or empty message")

    def set_freeze(self, freeze: bool, buffering: bool = False) -> None:
        """Set the freeze state of the serial port."""
        self._serial_freeze = freeze
        self._serial_buffering = buffering
        if freeze:
            self.logger.debug("Serial port frozen")
        else:
            self.logger.debug("Serial port unfrozen")

    def set_write_allow(self, allow: bool) -> None:
        """Set the write state of the serial port."""
        self._serial_write_allow = allow
        if allow:
            self.logger.debug("Serial write allowed")
        else:
            self.logger.debug("Serial write blocked")

    @property
    def is_connected(self) -> bool:
        """Check if the serial port is connected."""
        return self._serial is not None and self._serial.is_open

    # Internal
    def __init__(self, logger: logging.Logger):
        super().__init__()
        self.logger = logger
        self._serial: Optional[Serial] = None
        self._running = False
        self._write_queue = Queue()
        self._lock = Lock()
        self._buffer_size = 1024 * 8
        self._thread_id = None
        self._serial_freeze = False
        self._serial_buffering = True
        self._baudrate = 115200
        self._port_request = ""
        self._serial_write_allow = True

    def try_start(self, port: str, baudrate: int) -> bool:
        """Attempt to start the serial reader thread safely"""
        try:
            # Check if thread is already running
            if self._thread_id is not None:
                self.logger.warning("Thread already running")
                return False

            # Check if port is valid
            if port not in self.available_ports():
                self.logger.error(f"Invalid port: {port}")
                return False

            # Register the port and baudrate
            self._port_request = port
            self._baudrate = baudrate

            # Start the thread
            self._running = True
            self.start()
            return True
        except Exception as e:
            # Log and return False on error, and reset the port request
            self.logger.error(f"Failed to start serial reader: {e}")
            self._port_request = ""
            self._baudrate = 115200
            return False

    def run(self) -> None:
        """Main thread loop"""
        try:
            # Initialize thread
            self._thread_id = QThread.currentThreadId()
            # Connect to serial port
            self._connect()
            # Main loop
            self._read_loop()
        except Exception as e:
            # Handle any errors
            self._handle_error(f"Thread error: {e}")
        finally:
            # Cleanup resources
            self._thread_id = None
            self._cleanup()

    def _connect(self) -> None:
        """Connect to serial port"""
        try:
            if not self._port_request:
                raise RuntimeError("No port requested")

            with self._lock:
                if self._serial is not None:
                    return

                self._serial = Serial(
                    port=self._port_request,
                    baudrate=self._baudrate,
                    timeout=1.0,
                    write_timeout=1.0,
                    bytesize=8,
                    stopbits=STOPBITS_ONE,
                )

            self.logger.success(
                f"Connected to {self._port_request} at {self._baudrate} baud"
            )
            self.connection_state.emit(True)

        except Exception as e:
            self._cleanup()
            raise RuntimeError(f"Connection failed: {e}")

    def _check_connection(self) -> bool:
        """Check if connection is still alive"""
        try:
            with self._lock:
                # Check if serial port is open
                if not self._serial:
                    return False
                # Try to get port status - will fail if disconnected
                self._serial.in_waiting
                return True
        except (SerialException, OSError):
            return False

    def _read_loop(self) -> None:
        """Main reading loop with connection monitoring"""
        accumulated_data = bytearray()

        while self._running:
            try:
                # Check connection status
                if not self._check_connection():
                    self._handle_error("Serial port disconnected unexpectedly")
                    break

                # Process write queue
                if not self._write_queue.empty() and self._serial_write_allow:
                    self._process_write_queue()

                # Read available data with timeout
                try:
                    # Read data if available and not frozen with buffering
                    if self._serial.in_waiting > 0 and not (
                        self._serial_freeze and self._serial_buffering
                    ):
                        # Read a chunk of data (not an entire line)
                        data = self._serial.read(min(self._serial.in_waiting, 1024))

                        # If frozen but not buffering, just discard the data
                        if self._serial_freeze and not self._serial_buffering:
                            continue

                        # If we have data to process
                        if data:
                            # Add to our accumulated data
                            accumulated_data.extend(data)

                            # Check if we have complete messages (separated by newlines)
                            while b"\n" in accumulated_data:
                                # Split at the first newline
                                line, accumulated_data = accumulated_data.split(
                                    b"\n", 1
                                )

                                try:
                                    # Decode and emit signals
                                    decoded = line.decode("ascii").strip()

                                    # Process prefixes
                                    if self._prefixes:
                                        # Check for prefixes
                                        for prefix in self._prefixes:
                                            if decoded.startswith(prefix):
                                                self.data_received_prefix.emit(
                                                    prefix, decoded[len(prefix) :]
                                                )
                                                break
                                        else:
                                            self.data_received_normal.emit(decoded)
                                    else:
                                        self.data_received_normal.emit(decoded)

                                except UnicodeDecodeError as e:
                                    self.logger.warning(f"Decode error: {e}")
                    else:
                        # Small sleep to prevent CPU hogging (1ms)
                        time.sleep(0.001)

                except (SerialException, OSError) as e:
                    # Handle serial port errors
                    self._handle_error(f"Serial port error: {e}")
                    break
                except Exception as e:
                    self.logger.warning(f"Processing error: {e}")
                    continue

                # Small sleep to prevent CPU hogging (1ms)
                time.sleep(0.001)

            except Exception as e:
                self._handle_error(f"Unexpected error in read loop: {e}")
                break

    def _process_write_queue(self) -> None:
        """Process pending write operations"""
        try:
            while not self._write_queue.empty():
                # Write data to serial port
                data = self._write_queue.get_nowait()
                with self._lock:
                    # Check if serial port is open
                    if self._serial and self._serial.is_open:
                        # Write data to serial port
                        self._serial.write(data.encode("ascii"))
                        self.logger.info(f"Sent: {data}")
                        # Flush to ensure data is sent
                        self._serial.flush()
                    else:
                        self.logger.warning(
                            "Serial port not open, cannot write, discarding data"
                        )
                # Mark task as done
                self._write_queue.task_done()
        except Exception as e:
            self.logger.error(f"Write error: {e}")

    def stop(self) -> bool:
        """Stop thread safely"""
        try:
            # Check if thread is running
            if self._thread_id is None:
                return True

            # Stop thread
            self.logger.debug("Stopping reader")
            self._running = False

            # Close serial port
            with self._lock:
                if self._serial:
                    try:
                        self._serial.close()
                    except:
                        pass
                    self._serial = None

            # Wait for thread to finish
            if QThread.currentThread() != self:
                if not self.wait(1000):
                    self.terminate()
                    self.wait(500)

            return True

        except Exception as e:
            self.logger.error(f"Stop error: {e}")
            return False
        finally:
            self.logger.trace("Reader stopped")  # Idk if its the right level

    def _cleanup(self) -> None:
        """Clean up resources"""
        with self._lock:
            # Close serial port
            if self._serial:
                try:
                    self._serial.close()
                except:
                    pass
                self._serial = None

            # Clear write queue
            while not self._write_queue.empty():
                try:
                    self._write_queue.get_nowait()
                except:
                    pass
        # Emit connection state
        self._running = False
        self.connection_state.emit(False)
        self.logger.debug("Cleaned up resources")

    def _handle_error(self, message: str) -> None:
        """Handle errors uniformly"""
        # Log and emit error signal
        self.logger.error(message)
        self.error_occurred.emit(message)
        self.data_received_normal.emit("TERMINATE")
        self.stop()


# Example usage
# -------------------------------------------------

if __name__ == "__main__":
    logger = logging.getLogger("SerialExample")
    logger.setLevel(logging.DEBUG)
    logger_handler = logging.StreamHandler(sys.stdout)
    logger_handler.setLevel(logging.DEBUG)
    logger.addHandler(logger_handler)

    # Add SUCCESS level to the logger
    logging.addLevelName(25, "SUCCESS")

    def success(self, message, *args, **kws):
        if self.isEnabledFor(25):
            self._log(25, message, args, **kws)

    logging.Logger.success = success

    # Add TRACE level to the logger
    logging.addLevelName(15, "TRACE")

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(15):
            self._log(15, message, args, **kws)

    logging.Logger.trace = trace

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Serial Communication Test")
            self.resize(600, 500)

            self.serial_controller = SerialController(logger)
            self._setup_ui()
            self._connect_signals()

        def _setup_ui(self):
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            self.layout = QVBoxLayout(central_widget)

            # Port selection
            port_layout = QHBoxLayout()
            port_layout.addWidget(QLabel("Select Port:"))
            self.port_combo = QComboBox()
            for port, desc in self.serial_controller.available_ports().items():
                self.port_combo.addItem(port)
            port_layout.addWidget(self.port_combo)
            self.connect_button = QPushButton("Connect")
            self.disconnect_button = QPushButton("Disconnect")
            port_layout.addWidget(self.connect_button)
            port_layout.addWidget(self.disconnect_button)
            self.layout.addLayout(port_layout)

            # Send message
            send_layout = QHBoxLayout()
            self.message_input = QLineEdit()
            self.message_input.setPlaceholderText("Enter message...")
            self.send_button = QPushButton("Send")
            send_layout.addWidget(self.message_input)
            send_layout.addWidget(self.send_button)
            self.layout.addLayout(send_layout)

            # Register prefix
            prefix_layout = QHBoxLayout()
            self.prefix_input = QLineEdit()
            self.prefix_input.setPlaceholderText("Prefix to register")
            self.register_prefix_button = QPushButton("Register Prefix")
            self.unregister_prefix_button = QPushButton("Unregister Prefix")
            prefix_layout.addWidget(self.prefix_input)
            prefix_layout.addWidget(self.register_prefix_button)
            prefix_layout.addWidget(self.unregister_prefix_button)
            self.layout.addLayout(prefix_layout)

            # Freeze and write allow
            check_layout = QHBoxLayout()
            self.freeze_check = QCheckBox("Freeze Serial")
            self.write_allow_check = QCheckBox("Allow Writes")
            self.write_allow_check.setChecked(True)  # default
            check_layout.addWidget(self.freeze_check)
            check_layout.addWidget(self.write_allow_check)
            self.layout.addLayout(check_layout)

            # Console
            self.console = QTextEdit()
            self.console.setReadOnly(True)
            self.layout.addWidget(self.console)

        def _connect_signals(self):
            # Buttons
            self.connect_button.clicked.connect(self.on_connect)
            self.disconnect_button.clicked.connect(self.on_disconnect)
            self.send_button.clicked.connect(self.on_send)
            self.register_prefix_button.clicked.connect(self.on_register_prefix)
            self.unregister_prefix_button.clicked.connect(self.on_unregister_prefix)
            self.freeze_check.toggled.connect(self.on_freeze_toggled)
            self.write_allow_check.toggled.connect(self.on_write_allow_toggled)

            # Serial signals
            self.serial_controller.data_received_normal.connect(self.handle_normal)
            self.serial_controller.data_received_prefix.connect(self.handle_prefix)
            self.serial_controller.connection_state.connect(
                self.handle_connection_state
            )
            self.serial_controller.error_occurred.connect(self.handle_error_occurred)

        # --------------- Event Handlers ---------------
        def on_connect(self):
            port = self.port_combo.currentText()
            # Use a default baud rate
            baudrate = 115200
            if self.serial_controller.try_start(port, baudrate):
                self.console.append(f"Attempting to connect to {port}...")
            else:
                self.console.append(f"Failed to connect to {port}.")

        def on_disconnect(self):
            self.serial_controller.stop()
            self.console.append("Disconnected")

        def on_send(self):
            message = self.message_input.text().strip()
            if message:
                self.serial_controller.write_message(message)
                self.console.append(f"Sent: {message}")
                self.message_input.clear()

        def on_register_prefix(self):
            prefix = self.prefix_input.text().strip()
            if prefix:
                self.serial_controller.register_prefix(prefix)
                self.console.append(f"Registered prefix: {prefix}")
                self.prefix_input.clear()

        def on_unregister_prefix(self):
            prefix = self.prefix_input.text().strip()
            if prefix:
                self.serial_controller.unregister_prefix(prefix)
                self.console.append(f"Unregistered prefix: {prefix}")
                self.prefix_input.clear()

        def on_freeze_toggled(self, checked: bool):
            self.serial_controller.set_freeze(checked, buffering=False)
            self.console.append(f"Freeze={checked}")

        def on_write_allow_toggled(self, checked: bool):
            self.serial_controller.set_write_allow(checked)
            self.console.append(f"Write allowed={checked}")

        # --------------- Serial Signal Slots ---------------
        def handle_normal(self, line: str):
            self.console.append(f"(normal) {line}")

        def handle_prefix(self, prefix: str, data: str):
            self.console.append(f"(prefix={prefix}) {data}")

        def handle_connection_state(self, connected: bool):
            self.console.append(f"Connection state changed: {connected}")

        def handle_error_occurred(self, error_msg: str):
            self.console.append(f"ERROR: {error_msg}")

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
