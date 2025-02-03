import logging
from logging import Handler, LogRecord
from PyQt6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QTextCursor, QColor
from PyQt6.QtCore import Qt
import pathlib

class ContentLogger:
    def __init__(self, name: str, file_path: str = "test_logs.log", use_file: bool = True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.handlers = []
        self.file_use_toggle = use_file
        self.file_path = pathlib.Path(__file__).parent / file_path
        self.file_max_bytes = int(1e4)  # placeholder for future rotation logic
        self.file_backup_count = 3      # placeholder for future rotation logic
        self._custom_levels = {}
        self.default_formatter_str = "[%(asctime)s] %(levelname)-8s: %(message)s"
        self.default_date_format = "%Y-%m-%d %H:%M:%S"
        self._add_custom_levels()

        # Automatically add a file handler if use_file is True
        if self.file_use_toggle:
            self.add_file_handler(str(self.file_path), logging.DEBUG)

    def _add_custom_levels(self):
        """Add custom logging levels: TRACE=5, SUCCESS=25."""
        self._custom_levels = {
            'TRACE': 5,
            'SUCCESS': 25,
        }
        for level_name, level_value in self._custom_levels.items():
            logging.addLevelName(level_value, level_name)
            setattr(self.logger, level_name.lower(), self._create_log_method(level_name, level_value))

    def _create_log_method(self, level_name: str, level_value: int):
        """Create a custom logging method for a specific level."""
        def log_method(msg, *args, **kwargs):
            if self.logger.isEnabledFor(level_value):
                self.logger._log(level_value, msg, args, **kwargs)
        return log_method

    def change_level(self, level: int):
        """Change the logger’s overall level (DEBUG, INFO, etc.)."""
        self.logger.setLevel(level)

    def change_formatter(self, formatter_str: str = None, datefmt: str = None, CLI_only: bool = False):
        """Change the formatter for all handlers, or only CLI if CLI_only=True."""
        if not formatter_str:
            formatter_str = self.default_formatter_str
        if not datefmt:
            datefmt = self.default_date_format

        new_formatter = logging.Formatter(formatter_str, datefmt=datefmt)
        for handler in self.handlers:
            if CLI_only and not isinstance(handler, logging.StreamHandler):
                continue
            handler.setFormatter(new_formatter)

    def change_date_format(self, date_format: str):
        """Change only the date format using the default formatter text."""
        new_formatter = logging.Formatter(self.default_formatter_str, datefmt=date_format)
        for handler in self.handlers:
            handler.setFormatter(new_formatter)

    def toggle_file_logging(self, file_path: str, level: int = logging.DEBUG):
        """Toggle file logging on/off."""
        if not any(isinstance(h, logging.FileHandler) for h in self.handlers):
            self.add_file_handler(file_path, level)
        else:
            self.remove_file_handler()

    def remove_file_handler(self):
        """Remove all FileHandler instances from this logger."""
        file_handlers = [h for h in self.handlers if isinstance(h, logging.FileHandler)]
        for fh in file_handlers:
            self.logger.removeHandler(fh)
            self.handlers.remove(fh)

    def add_file_handler(self, file_path: str, level: int = logging.DEBUG,
                         formatter_str: str = None, datefmt: str = None):
        """Add a file handler with optional custom formatter."""
        if not formatter_str:
            formatter_str = self.default_formatter_str
        if not datefmt:
            datefmt = self.default_date_format

        handler = logging.FileHandler(file_path)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(formatter_str, datefmt=datefmt))
        self.logger.addHandler(handler)
        self.handlers.append(handler)

    def setup_handler(self, handler: Handler, formatter_str: str = None, datefmt: str = None):
        """Attach any logging.Handler with optional custom formatter."""
        if not formatter_str:
            formatter_str = self.default_formatter_str
        if not datefmt:
            datefmt = self.default_date_format

        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(formatter_str, datefmt=datefmt))
        self.logger.addHandler(handler)
        self.handlers.append(handler)

    def gen_gui_console(self) -> QTextEdit:
        """
        Generate a QTextEdit widget as a log receiver, limited to 200 lines.
        """
        class QTextEditHandler(Handler):
            def __init__(self, text_edit: QTextEdit, max_lines: int = 200):
                super().__init__()
                self.text_edit = text_edit
                self.max_lines = max_lines

            def emit(self, record: LogRecord):
                try:
                    msg = self.format(record)
                    self.append_colored_message(record.levelname, msg)
                    self.trim_lines()
                except Exception:
                    self.handleError(record)

            def append_colored_message(self, level, message):
                color_map = {
                    'DEBUG': 'gray',
                    'INFO': 'black',
                    'WARNING': 'orange',
                    'ERROR': 'red',
                    'CRITICAL': 'darkred',
                    'TRACE': 'blue',
                    'SUCCESS': 'green',
                }
                color_name = color_map.get(level, 'black')
                self.text_edit.setTextColor(QColor(color_name))
                self.text_edit.append(message)

            def trim_lines(self):
                cursor = self.text_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                while self.text_edit.document().blockCount() > self.max_lines:
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deleteChar()

        text_edit = QTextEdit()
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
    layout1.addWidget(test_button)

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
