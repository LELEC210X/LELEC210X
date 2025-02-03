from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QSlider,
    QColorDialog,
    QTabWidget,
    QLineEdit,
    QGroupBox,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6 import QtGui
import pathlib
from threading import Lock
import sys
import logging
import numpy as np
from typing import Literal, Callable

class DatabaseEntry:
    """Class to store the information of a database entry."""
    def __init__(self, id: str, name: str, description: str, entry_type: type, entry_value: any, attributes: dict = {}, reset_value: any = None):
        self.id = id
        self.name = name
        self.description = description
        self.entry_type = entry_type
        self.entry_value = entry_value
        self.attributes = attributes

        self.reset_value = entry_value if reset_value is None else reset_value

        self._callbacks: dict[str, Callable] = {}
        self._value_lock = Lock()
        self._callbacks_lock = Lock()

    # Reset logic

    def reset(self) -> None:
        """Reset the entry to the initial value."""
        self.entry_value = self.reset_value

    # Serialization, deserialization

    def serialize(self) -> dict:
        """Serialize the entry to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "entry_type": self.entry_type,
            "entry_value": self.entry_value,
            "attributes": self.attributes,
            "reset_value": self.reset_value,
        }
    
    @staticmethod
    def deserialize(data: dict):
        """Deserialize the entry from a dictionary."""
        return DatabaseEntry(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            entry_type=data["entry_type"],
            entry_value=data["entry_value"],
            attributes=data["attributes"],
            reset_value=data["reset_value"],
        )

    # Setters
    
    def safe_set(self, target: Literal["name", "description", "entry_type", "entry_value", "attributes", "reset_value"], value: any, call_callbacks: bool = True) -> bool:
        """Set the class attribute with a lock, and runs the callbacks (by default)."""
        with self._value_lock:
            # Custom handlings
            if target == "attributes":
                self.attributes.update(value)
            try:
                # Default handling
                setattr(self, target, value)
            except AttributeError:
                return False
        # Run the callbacks
        if call_callbacks:
            self.run_callbacks()
        return True
    
    # Getters

    def get_value(self) -> any:
        """Get the value of the entry (more explicit function, non blocking)."""
        return self.entry_value
    
    def safe_get(self, target: Literal["name", "description", "entry_type", "entry_value", "attributes", "reset_value"]) -> any:
        """Get the class attribute with a lock."""
        with self._value_lock:
            try:
                return getattr(self, target)
            except AttributeError:
                return None

    # Callbacks

    def add_callback(self, id: str, callback: Callable) -> bool:
        """Add a callback to the entry."""
        with self._callbacks_lock:
            if id in self._callbacks:
                return False
            self._callbacks[id] = callback
        return True
    
    def remove_callback(self, id: str) -> bool:
        """Remove a callback from the entry."""
        with self._callbacks_lock:
            try:
                del self._callbacks[id]
            except KeyError:
                return False
        return True
    
    def remove_gui_callbacks(self, id: str) -> int:
        """Remove all the callbacks from the entry."""
        with self._callbacks_lock:
            accumulator = 0
            for key in list(self._callbacks.keys()):
                if id in key:
                    del self._callbacks[key]
                    accumulator += 1
        return accumulator                
    
    def run_callbacks(self) -> None:
        """Run all the callbacks of the entry."""
        for callback in self._callbacks.values():
            callback(self)
            
    # UI logic

    def get_name_widget(self, id: str) -> QWidget:
        """Get the name widget of the entry."""
        widget = QLabel()
        widget.setText(self.name)
        widget.setFixedWidth(250)
        widget.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Weight.Bold))
        widget.setToolTip(self.description)
        widget.setWordWrap(True)
        def update_name(entry_obj: DatabaseEntry):
            widget.setText(self.name)
            widget.setToolTip(self.description)
        self.add_callback("name_up_" + id, update_name)
        return widget
    
    def get_description_widget(self, id: str) -> QWidget:
        """Get the description widget of the entry."""
        widget = QLabel()
        widget.setText(self.description)
        widget.setStyleSheet("color: #707070;")
        widget.setFixedWidth(250)
        widget.setFont(QtGui.QFont("Arial", 8))
        widget.setWordWrap(True)
        def update_description(entry_obj: DatabaseEntry):
            widget.setText(self.description)
            widget.setToolTip(self.description)
        self.add_callback("description_up_" + id, update_description)
        return widget
    
    def get_label_widget(self, id: str) -> QWidget:
        """Get the description widget of the entry."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        name = self.get_name_widget(id)
        description = self.get_description_widget(id)
        layout.addWidget(name)
        layout.addWidget(description)
        return widget
    
    def get_full_widget(self, id: str) -> QWidget:
        """Get the full widget of the entry."""
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        label = self.get_label_widget(id)
        value = self.get_value_widget(id)
        layout.addWidget(label)
        layout.addWidget(value)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget
    
    # FOR EACH ENTRY TYPE

    def get_value_widget(self, id: str) -> QWidget:
        """DEFAULT VALUE WIDGET"""
        widget = QLineEdit()
        widget.setText(str(self.entry_value))
        widget.setToolTip(self.description)
        widget.setReadOnly(not self.attributes.get("editable", True))
        def update_value(entry_obj: DatabaseEntry):
            widget.setText(str(self.entry_value))
            widget.setToolTip(self.description)
            widget.setReadOnly(not self.attributes.get("editable", True))
        self.add_callback("value_up_" + id, update_value)
        def update_entry():
            try:
                self.safe_set("entry_value", type(self.entry_value)(widget.text()))
            except ValueError:
                logging.error(f"Error setting value of {self.id} to {widget.text()} (default value widget)")
        widget.textChanged.connect(update_entry)
        return widget

class DatabaseClass:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description

        self._entries: dict[str, DatabaseEntry] = {}
        self._entries_lock = Lock()

        self._callbacks: dict[str, Callable] = {}
        self._callbacks_lock = Lock()

    def __del__(self):
        """Destructor of the class, meant to remove all references to the entries (so proper errors are seen)."""
        for entry in self._entries.values():
            del entry

    # Reset logic

    def reset(self) -> None:
        """Reset all the entries of the class."""
        for entry in self._entries.values():
            entry.reset()

    # Serialization, deserialization

    def serialize(self) -> dict:
        """Serialize the class to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "entries": {entry_id: entry.serialize() for entry_id, entry in self._entries.items()},
        }
    
    @staticmethod
    def deserialize(data: dict):
        """Deserialize the class from a dictionary."""
        class_ = DatabaseClass(
            id=data["id"],
            name=data["name"],
            description=data["description"],
        )
        for entry_id, entry_data in data["entries"].items():
            class_.add_entry(DatabaseEntry.deserialize(entry_data))
        return class_
    
    # Entry management

    def add_entry(self, id: str, name: str, description: str, entry_type: type, entry_value: any, attributes: dict = {}) -> DatabaseEntry:
        """Add an entry to the class."""
        entry = DatabaseEntry(id, name, description, entry_type, entry_value, attributes)
        with self._entries_lock:
            if id in self._entries:
                return self._entries[id]
            self._entries[id] = entry
        return entry
    
    def get_entry(self, id: str) -> DatabaseEntry:
        """Get an entry from the class."""
        with self._entries_lock:
            return self._entries[id]
        
    def remove_entry(self, id: str) -> bool:
        """Remove an entry from the class."""
        with self._entries_lock:
            try:
                del self._entries[id]
            except KeyError:
                return False
        return True
    
    # Class updates

    def safe_set(self, target: Literal["name", "description"], value: any) -> bool:
        """Set the class attribute with a lock."""
        with self._entries_lock:
            try:
                setattr(self, target, value)
            except AttributeError:
                return False
        return True
    
    # Callbacks

    def add_callback(self, id: str, callback: Callable) -> bool:
        """Add a callback to the class."""
        with self._callbacks_lock:
            if id in self._callbacks:
                return False
            self._callbacks[id] = callback
        return True
    
    def remove_callback(self, id: str) -> bool:
        """Remove a callback from the class."""
        with self._callbacks_lock:
            try:
                del self._callbacks[id]
            except KeyError:
                return False
        return True
    
    def remove_gui_callbacks(self, id: str) -> int:
        """Remove all the callbacks from the class."""
        with self._callbacks_lock:
            accumulator = 0
            for key in list(self._callbacks.keys()):
                if id in key:
                    del self._callbacks[key]
                    accumulator += 1
        return accumulator
    
    def run_callbacks(self) -> None:
        """Run all the callbacks of the class."""
        for callback in self._callbacks.values():
            callback(self)

    # UI logic

    def get_class_widget(self, id: str) -> QWidget:
        """Get the class widget."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        for entry in self._entries.values():
            layout.addWidget(entry.get_full_widget(id))
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        return widget    

####################################################################################################

class ContentDatabase:
    def __init__(self):
        self._classes: dict[str, DatabaseClass] = {}
        self._classes_lock = Lock()

        self._callbacks: dict[str, Callable] = {}
        self._callbacks_lock = Lock()

        self._initialization_func = None
        self._save_file_path = pathlib.Path("database.npy")
        self._load_file_path = pathlib.Path("database.npy")

        self._logger = None
        self.parameter_windows = []

    def __del__(self):
        """Destructor of the class, meant to remove all references to the classes (so proper errors are seen)."""
        for class_ in self._classes.values():
            del class_

    # Initialization

    def initialization_func(self, func: Callable) -> None:
        """Set the initialization function of the database."""
        self._initialization_func = func
        func(self)

    # Serialization, deserialization

    def serialize(self) -> dict:
        """Serialize the database to a dictionary."""
        return {
            "classes": {class_id: class_.serialize() for class_id, class_ in self._classes.items()},
        }
    
    @staticmethod
    def deserialize(data: dict):
        """Deserialize the database from a dictionary."""
        database = ContentDatabase()
        for class_id, class_data in data["classes"].items():
            database.add_class(DatabaseClass.deserialize(class_data))
        return database
    
    def save_to_file(self, path: pathlib.Path) -> None:
        """Save the database to a file."""
        with open(path, "wb") as file:
            np.save(file, self.serialize())
        self._save_file_path = path

    def load_from_file(self, path: pathlib.Path) -> None:
        """Load the database from a file."""
        with open(path, "rb") as file:
            data = np.load(file, allow_pickle=True)
            self = ContentDatabase.deserialize(data)
        self._load_file_path = path

    # Class management

    def add_class(self, id: str, name: str, description: str) -> DatabaseClass:
        """Add a class to the database."""
        class_ = DatabaseClass(id, name, description)
        with self._classes_lock:
            if id in self._classes:
                return self._classes[id]
            self._classes[id] = class_
        return class_
    
    def get_class(self, id: str) -> DatabaseClass:
        """Get a class from the database."""
        with self._classes_lock:
            return self._classes[id]
        
    def remove_class(self, id: str) -> bool:
        """Remove a class from the database."""
        with self._classes_lock:
            try:
                del self._classes[id]
            except KeyError:
                return False
        return True
    
    def get_short(self, class_id: str, entry_id: str) -> DatabaseEntry:
        """Get an entry from a class."""
        with self._classes_lock:
            return self._classes[class_id].get_entry(entry_id)
    
    # Callbacks

    def add_callback(self, id: str, callback: Callable) -> bool:
        """Add a callback to the database."""
        with self._callbacks_lock:
            if id in self._callbacks:
                return False
            self._callbacks[id] = callback
        return True
    
    def remove_callback(self, id: str) -> bool:
        """Remove a callback from the database."""
        with self._callbacks_lock:
            try:
                del self._callbacks[id]
            except KeyError:
                return False
        return True
    
    def remove_gui_callbacks(self, id: str) -> int:
        """Remove all the callbacks from the database."""
        with self._callbacks_lock:
            accumulator = 0
            for key in list(self._callbacks.keys()):
                if id in key:
                    del self._callbacks[key]
                    accumulator += 1
        return accumulator
    
    def run_callbacks(self) -> None:
        """Run all the callbacks of the database."""
        for callback in self._callbacks.values():
            callback(self)

    # UI logic

    def open_parameter_window(self, id: str) -> QMainWindow:
        """Open a window to set the parameters of the database."""
        # Each class is a tab
        # Each entry is a widget

        # Create the main window
        window = QMainWindow()
        window.resize(800, 600)
        window.setWindowTitle("Parametters Window - " + id)

        # Create the tab widget
        tab_widget = QTabWidget()
        tab_widget.setTabsClosable(False)

        # Create the tabs
        for class_ in self._classes.values():
            tab_widget.addTab(class_.get_class_widget(id), class_.name)

        # Add the tab widget to the window
        window.setCentralWidget(tab_widget)

        # Show the window
        window.show()

        # Keep a reference to the window to prevent it from being garbage collected
        self.parameter_windows.append(window) 

        return window

####################################################################################################

def db_basics(database: ContentDatabase) -> bool:

    class1 = database.add_class(
        id="class1",
        name="Class 1",
        description="Class 1 description, be cause why not ?",
    )
    class1.add_entry(
        id="content1",
        name="Content 1",
        description="Content 1 description",
        entry_type= str,
        entry_value= "content1.wav",
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class1.add_entry(
        id="content2",
        name="Content 2",
        description="Content 2 description, with content wrap, because we are that strong !",
        entry_type= str,
        entry_value= "content2.wav",
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class2 = database.add_class(
        id="class2",
        name="Class 2",
        description="Class 2 description, be cause why not ?",
    )
    class2.add_entry(
        id="content3",
        name="Content 3",
        description="Content 3 description (from class 2)",
        entry_type= str,
        entry_value= "content3.wav",
        attributes={
            "hidden": False,
            "editable": True,
        },
    )

    return True


if __name__ == "__main__":
    # Prototype of the interface interactions with the database

    database = ContentDatabase()

    database.initialization_func(db_basics) # Make a basic database
    try:
        database.load_from_file("database.npy") # change the values and add more entries if needed
    except:
        database.save_to_file("database.npy") # Save the database to a file

    # Access the database
    class1 = database.get_class("class1")
    content1 = class1.get_entry("content1")
    # or
    content1 = database.get_short("class1", "content1")

    # Modify the database
    content1.safe_set("attributes", {"hidden": False, "editable": True})
    content1.safe_set("entry_value", "new_content1.wav")
    content1.safe_set("description", "New description that is long enough to test the wrapping of the text in the GUI")

    # Make a system to add callbacks and remove them for stuff outside the database
    content1.add_callback("print_change", lambda entry: print("Content 1 changed"))
    content1.remove_callback("print_change")

    # Start the app stuff for QT
    app = QApplication(sys.argv)

    # Test the synchronization of the parameters window
    database.open_parameter_window("window1")
    database.open_parameter_window("window2")

    # Make the gui ellements for the database, from the contents
    window = QMainWindow()
    window.setWindowTitle("Database GUI")
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    layout = QVBoxLayout()
    
    layout.addWidget(content1.get_full_widget("content1"))

    class_box = QGroupBox()
    class_box.setTitle(class1.name)
    class_layout = QVBoxLayout()
    class_box.setLayout(class_layout)
    class_layout.addWidget(class1.get_class_widget("class1"))
    layout.addWidget(class_box)

    central_widget.setLayout(layout)
    window.show()

    sys.exit(app.exec())
    # Anything later than here has problems with the sys.exit(app.exec()) call



