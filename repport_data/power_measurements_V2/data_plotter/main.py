# main.py
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from data_types import SignalData, ChannelMetadata
from signal_processor import SignalProcessor
from csv_processor import OscilloscopeCSVProcessor
from gui import SignalViewer
import logging

def main():
    try:
        app = QApplication(sys.argv)
        viewer = SignalViewer()
        viewer.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()