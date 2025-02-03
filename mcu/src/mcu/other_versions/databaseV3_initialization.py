from databaseV3 import *
import os, pathlib

def generate_database() -> ContentDatabase:
    database = ContentDatabase()

    database.initialization_func(initialize_database)

    return database

def initialize_database(database: ContentDatabase) -> bool:
    # Create the hidden class
    hidden_class:DatabaseClass = database.add_class(
        id="hidden_class",
        name="Hidden Class",
        description="This class is hidden from the user and is used for internal purposes."
    )
    hidden_class.add_entry(
        id="app_version",
        name="Application Version",
        description="The version of the application.",
        entry_type= DatabaseEntry.StringEntry,
        entry_value= "5.0.0",
        attributes={
            "hidden": True,
            "editable": False,
        },
    )
    hidden_class.add_entry(
        id="app_name",
        name="Application Name",
        description="This application reads data from a UART port and displays it.",
        entry_type= DatabaseEntry.StringEntry,
        entry_value= "UART Reader for LELEC210x",
        attributes={
            "hidden": True,
            "editable": False,
        },
    )
    hidden_class.add_entry(
        id="author",
        name="Author",
        description="The author of the application.",
        entry_type= DatabaseEntry.StringEntry,
        entry_value="Group E 2024-2025",
        attributes={
            "hidden": True,
            "editable": False,
        },
    )


    # Create the File class
    file_settings:DatabaseClass = database.add_class(
        id="file_settings",
        name="File Settings",
        description="This category contains the settings for the file paths."
    )
    base_path = pathlib.Path(__file__).parent
    data_path = base_path / "data"
    file_settings.add_entry(
        id="database_file",
        name="Database File",
        description="The file that contains the database.",
        entry_type= DatabaseEntry.FileEntry,
        entry_value= str(data_path / "database.npy"),
        attributes={
            "editable": True,
        },
    )

    # Create the UART class
    serial_settings:DatabaseClass = database.add_class(
        id="serial_settings",
        name="Serial Settings",
        description="This category contains the settings for the serial port."
    )
    serial_settings.add_entry(
        id="port",
        name="Port",
        description="The port to which the device is connected.",
        entry_type= DatabaseEntry.ComboBoxEntry,
        entry_value= {
            "options": ["-- No Ports Detected --"],
            "index": 0,
        },
        attributes={
            "editable": True,
        },
    )
    serial_settings.add_entry(
        id="baudrate",
        name="Baudrate",
        description="The baudrate of the serial port.",
        entry_type= DatabaseEntry.ComboBoxEntry,
        entry_value= {
            "options": ["115200", "9600", "4800", "2400", "1200", "600", "300"],
            "index": 0,
        },
        attributes={
            "editable": True,
        },
    )