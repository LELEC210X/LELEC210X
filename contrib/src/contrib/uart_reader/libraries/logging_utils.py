import logging
import logging.handlers
import os
import pathlib
from logging import Handler, LogRecord

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QTextCursor
from PyQt6.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget


class ContentLogger:
    _custom_levels = {
        "DEBUG": logging.DEBUG,
        "TRACE": 15,
        "INFO": logging.INFO,
        "SUCCESS": 25,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __init__(
        self, name: str, file_path: str = "test_logs.log", use_file: bool = True
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.handlers = []
        self.file_use_toggle = use_file
        self.file_path = (
            pathlib.Path(__file__).parent / file_path
            if not os.path.isabs(file_path)
            else file_path
        )
        self.file_max_bytes = int(1e4)  # placeholder for future rotation logic
        self.file_backup_count = 3  # placeholder for future rotation logic
        self.default_formatter_str = "[%(asctime)s] %(levelname)-8s: %(message)s"
        self.default_date_format = "%Y-%m-%d %H:%M:%S"

        # Add custom levels to the logger instance
        for level_name, level_value in self._custom_levels.items():
            logging.addLevelName(level_value, level_name)
            # Create a custom logging method for each level
            setattr(
                self.logger,
                level_name.lower(),
                self._create_log_method(level_name, level_value),
            )

        # Automatically add a file handler if use_file is True
        if self.file_use_toggle:
            self.add_file_handler(str(self.file_path), logging.DEBUG)

    def _create_log_method(self, level_name: str, level_value: int):
        """Create a custom logging method for a specific level."""

        # This method will be added to the logger instance, and follows the same conventions as the built-in methods
        def log_method(msg, *args, **kwargs):
            if self.logger.isEnabledFor(level_value):
                self.logger._log(level_value, msg, args, **kwargs)

        return log_method

    def change_level(self, level: str):
        """Change the logger’s overall level (DEBUG, INFO, etc.)."""
        # Change the level of the logger instance
        self.logger.setLevel(self._custom_levels.get(level, logging.DEBUG))

    def change_formatter(
        self, formatter_str: str = None, datefmt: str = None, CLI_only: bool = False
    ):
        """Change the formatter and date formatter for all handlers, or only CLI if CLI_only=True."""
        # If no formatter is provided, use the default formatter
        if not formatter_str:
            formatter_str = self.default_formatter_str
        # If no date format is provided, use the default date format
        if not datefmt:
            datefmt = self.default_date_format

        # Create a new formatter with the specified format and date format
        new_formatter = logging.Formatter(formatter_str, datefmt=datefmt)
        # Apply the new formatter to all handlers
        for handler in self.handlers:
            if CLI_only and not isinstance(handler, logging.StreamHandler):
                continue
            handler.setFormatter(new_formatter)

    def change_file_path(self, file_path: str):
        """Change the file path for the file handler."""
        self.file_path = file_path
        # Find the file handler and update its file path
        file_handler = next(
            (h for h in self.handlers if isinstance(h, logging.FileHandler)), None
        )
        if file_handler:
            file_handler.baseFilename = str(self.file_path)

    def toggle_file_logging(self, level: int = logging.DEBUG):
        """Toggle file logging on/off."""
        # If the logger has no file handlers, add one
        if not any(isinstance(h, logging.FileHandler) for h in self.handlers):
            self.add_file_handler(self.file_path, level)
        else:
            self.remove_file_handler()

    def remove_file_handler(self):
        """Remove all FileHandler instances from this logger."""
        # Find all file handlers and remove them
        file_handlers = [h for h in self.handlers if isinstance(h, logging.FileHandler)]
        for fh in file_handlers:
            self.logger.removeHandler(fh)
            self.handlers.remove(fh)

    def add_file_handler(
        self,
        file_path: str,
        level: int = logging.DEBUG,
        formatter_str: str = None,
        datefmt: str = None,
    ):
        """Add a file handler with optional custom formatter and date formatter."""
        # If no formatter is provided, use the default formatter
        if not formatter_str:
            formatter_str = self.default_formatter_str
        # If no date format is provided, use the default date format
        if not datefmt:
            datefmt = self.default_date_format

        MAX_FILE_SIZE = 5  # 5MB
        handler = logging.handlers.RotatingFileHandler(
            file_path,
            mode="a",
            maxBytes=MAX_FILE_SIZE * 1024 * 1024,
            backupCount=2,
            encoding=None,
            delay=0,
        )
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(formatter_str, datefmt=datefmt))
        self.logger.addHandler(handler)
        self.handlers.append(handler)

    def setup_handler(
        self, handler: Handler, formatter_str: str = None, datefmt: str = None
    ):
        """Attach any logging.Handler with optional custom formatter and date formatter."""
        # If no formatter is provided, use the default formatter
        if not formatter_str:
            formatter_str = self.default_formatter_str
        # If no date format is provided, use the default date format
        if not datefmt:
            datefmt = self.default_date_format

        # Set the formatter and date format for the handler
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(formatter_str, datefmt=datefmt))
        self.logger.addHandler(handler)
        self.handlers.append(handler)

    def gen_gui_console(self) -> QTextEdit:
        """
        Generate a QTextEdit widget as a log receiver, limited to 200 lines.
        """

        # Custom handler for QTextEdit
        class QTextEditHandler(Handler):
            def __init__(self, text_edit: QTextEdit, max_lines: int = 200):
                """Initialize the handler with a QTextEdit widget and a maximum number of lines."""
                super().__init__()
                self.text_edit = text_edit
                self.max_lines = max_lines

            def emit(self, record: LogRecord):
                """Emit a log record to the QTextEdit widget."""
                try:
                    msg = self.format(record)
                    self.append_colored_message(record.levelname, msg)
                    self.trim_lines()
                except Exception:
                    self.handleError(record)

            def append_colored_message(self, level, message):
                """Append a message to the QTextEdit widget with a specific color based on the log level."""
                color_map = {
                    "DEBUG": "blue",
                    "INFO": "black",
                    "WARNING": "orange",
                    "ERROR": "red",
                    "CRITICAL": "darkred",
                    "TRACE": "gray",
                    "SUCCESS": "green",
                }
                # Default color is black
                color_name = color_map.get(level, "black")
                if color_name == "black":
                    self.text_edit.setTextColor(
                        self.text_edit.palette().color(QPalette.ColorRole.Text)
                    )
                else:
                    self.text_edit.setTextColor(QColor(color_name))
                self.text_edit.append(message)
                # Reset the text color to whatever qt uses by default
                self.text_edit.setTextColor(
                    self.text_edit.palette().color(QPalette.ColorRole.Text)
                )

            def trim_lines(self):
                cursor = self.text_edit.textCursor()
                # Move the cursor to the start of the document
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                # If the number of lines exceeds the maximum, remove the oldest lines
                while self.text_edit.document().blockCount() > self.max_lines:
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deleteChar()

        text_edit = QTextEdit()
        # Set the text edit to read-only and always show the vertical scroll bar
        text_edit.setReadOnly(True)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        handler = QTextEditHandler(text_edit)
        self.setup_handler(handler)
        return text_edit


# Example usage (main guard)
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    logger = ContentLogger("MyLogger", use_file=True)  # By default uses "test_logs.log"

    # First window
    window1 = QWidget()
    layout1 = QVBoxLayout(window1)
    gui_console1 = logger.gen_gui_console()
    layout1.addWidget(gui_console1)
    window1.setWindowTitle("GUI Console 1")

    # Second window
    window2 = QWidget()
    layout2 = QVBoxLayout(window2)
    gui_console2 = logger.gen_gui_console()
    layout2.addWidget(gui_console2)
    window2.setWindowTitle("GUI Console 2")

    # CLI handler
    cli_handler = logging.StreamHandler()
    logger.setup_handler(cli_handler)

    # Test logs button
    def print_test_logs():
        logger.logger.debug("Debugging started.")
        logger.logger.info("Information message.")
        logger.logger.warning("Warning: Check this!")
        logger.logger.error("Error occurred!")
        logger.logger.critical("Critical issue encountered!")
        logger.logger.trace("This is a trace log.")
        logger.logger.success("Operation was successful!")

    test_button = QPushButton("Print Test Logs")
    test_button.clicked.connect(print_test_logs)
    layout2.addWidget(test_button)

    # Toggle basic formatter
    formatter_toggle = False

    def toggle_formatter():
        global formatter_toggle
        formatter_toggle = not formatter_toggle
        if formatter_toggle:
            logger.change_formatter("%(levelname)-8s: %(message)s")
        else:
            logger.change_formatter()

    test_button2 = QPushButton("Change Formatter")
    test_button2.clicked.connect(toggle_formatter)
    layout2.addWidget(test_button2)

    # Toggle date format
    formatter_date_toggle = False

    def toggle_date_formatter():
        global formatter_date_toggle
        formatter_date_toggle = not formatter_date_toggle
        if formatter_date_toggle:
            logger.change_formatter(datefmt="%H:%M:%S")
        else:
            logger.change_formatter()

    test_button3 = QPushButton("Change Date Formatter")
    test_button3.clicked.connect(toggle_date_formatter)
    layout2.addWidget(test_button3)

    window1.resize(600, 400)
    window2.resize(600, 400)
    window1.show()
    window2.show()
    sys.exit(app.exec())
