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
    QDoubleSpinBox,
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
import time

from utilities import convertSuffix

class DatabaseEntry:
    """Class to store the information of a database entry."""
    def __init__(self, id: str, name: str, description: str, entry_type: "GenericEntry", entry_value: any, attributes: dict = {}, reset_value: any = None):
        self.id = id
        self.name = name
        self.description = description
        self.entry_value = entry_value
        self.attributes = attributes
        self.entry_type:DatabaseEntry.GenericEntry = entry_type

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
            "entry_type": self.entry_type.serialize(),
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
            entry_type=DatabaseEntry.GenericEntry.deserialize(data["entry_type"]),
            entry_value=data["entry_value"],
            attributes=data["attributes"],
            reset_value=data["reset_value"],
        )

    # Setters

    def safe_set(self, target: Literal["name", "description", "entry_value", "attributes", "reset_value"], value: any, call_callbacks: bool = True) -> bool:
        """Set the class attribute with a lock, and runs the callbacks (by default)."""
        with self._value_lock:
            # Custom handlings
            if target == "attributes":
                self.attributes.update(value)
            elif target == "entry_value":
                if isinstance(self.entry_value, dict) and isinstance(value, dict):
                    self.entry_value.update(value)
                else:
                    self.entry_value = value
            # Default handling
            try:
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
        widget.adjustSize()
        widget.setMinimumHeight(widget.sizeHint().height()) # HACK : This is to make the text not get cropped if the wrap is not working properly
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
        layout.addStretch()
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
    
    # Per Class UI logic

    def get_value_widget(self, id: str) -> QWidget:
        """Get the value widget of the entry."""
        function_map = {
            DatabaseEntry.GenericEntry: self._get_GenericEntry_widget,
            DatabaseEntry.StringEntry: self._get_GenericEntry_widget,
            DatabaseEntry.IntEntry: lambda id: self._get_NumberEntry_widget(id, "int"),
            DatabaseEntry.FloatEntry: lambda id: self._get_NumberEntry_widget(id, "float"),
            DatabaseEntry.IntRangeEntry: lambda id: self._get_RangeEntry_widget(id, "int"),
            DatabaseEntry.FloatRangeEntry: lambda id: self._get_RangeEntry_widget(id, "float"),
            DatabaseEntry.BoolEntry: self._get_BoolEntry_widget,
            DatabaseEntry.ListEntry: lambda id: self._get_BulletEntry_widget(id, "list"),
            DatabaseEntry.DictEntry: lambda id: self._get_BulletEntry_widget(id, "dict"),
            DatabaseEntry.SuffixEntry: self._get_SuffixEntry_widget,
            DatabaseEntry.FileEntry: lambda id: QLabel("Not implemented yet"),
            DatabaseEntry.FolderEntry: lambda id: QLabel("Not implemented yet"),
            DatabaseEntry.ColorEntry: lambda id: QLabel("Not implemented yet"),
            DatabaseEntry.ComboBoxEntry: lambda id: QLabel("Not implemented yet"),
            DatabaseEntry.ButtonEntry: lambda id: QLabel("Not implemented yet"),
        }
        try:
            return function_map[self.entry_type](id)
        except KeyError:
            return QLabel("Unimplemented entry type: " + self.entry_type.__name__)
        except Exception as e:
            logging.error(f"Error getting value widget for {self.id} : {e}")
            return QLabel("Error getting value widget")

    # Classes 
    class GenericEntry:
        """Generic entry widget. (Should not be used directly if possible)"""
        @classmethod  # Change from @staticmethod to @classmethod
        def serialize(cls) -> str:
            return cls.__name__  # Use cls instead of __class__

        @staticmethod 
        def deserialize(data: str):
            for subclass in DatabaseEntry.GenericEntry.__subclasses__():  # Use GenericEntry explicitly
                if subclass.__name__ == data:
                    return subclass
            return DatabaseEntry.GenericEntry
    class StringEntry       (GenericEntry):"""String entry widget."""
    class IntEntry          (GenericEntry):"""Int entry widget."""
    class FloatEntry        (GenericEntry):"""Float entry widget."""
    class IntRangeEntry     (GenericEntry):"""Int range entry widget."""
    class FloatRangeEntry   (GenericEntry):"""Float range entry widget."""
    class BoolEntry         (GenericEntry):"""Bool entry widget."""
    class ListEntry         (GenericEntry):"""List entry widget."""
    class DictEntry         (GenericEntry):"""Dict entry widget."""
    class SuffixEntry       (GenericEntry):"""Suffix entry widget."""
    class FileEntry         (GenericEntry):"""File entry widget."""
    class FolderEntry       (GenericEntry):"""Folder entry widget."""
    class ColorEntry        (GenericEntry):"""Color entry widget."""
    class ComboBoxEntry     (GenericEntry):"""ComboBox entry widget."""
    class ButtonEntry       (GenericEntry):"""Button entry widget. (No value, only callbacks)""" # There is no value for this one, just a button

    # UI Widgets

    def _get_GenericEntry_widget(self, id: str) -> QWidget:
        """Get the generic entry widget."""
        widget = QLineEdit()

        # Callbacks
        def update_value(entry_obj: DatabaseEntry):
            widget.setText(str(self.entry_value))
            widget.setToolTip(self.description)
            widget.setReadOnly(not self.attributes.get("editable", True))
            if not self.attributes.get("editable", True):
                widget.setStyleSheet("color: #707070;")
            else:
                widget.setStyleSheet("color: #000000;")
        self.add_callback("value_up_" + id, update_value)
        update_value(self) # Initial update

        # Update the entry
        def update_entry():
            try:
                self.safe_set("entry_value", type(self.entry_value)(widget.text()))
            except ValueError:
                logging.error(f"Error setting value of {self.id} to {widget.text()} (default value widget)")
                
        #widget.editingFinished.connect(update_entry)
        widget.textEdited.connect(update_entry) # This is better for real time updates, as its not 4 times per change (like with textChanged)
        return widget
    
    def _get_NumberEntry_widget(self, id: str, entry_type: Literal["str", "float"]) -> QWidget:
        """Get the number entry widget."""
        if entry_type == "float":
            base_widget = QDoubleSpinBox()
            base_widget.setDecimals(2)
            base_widget.setSingleStep(0.5)
            base_widget.setRange(-1e255, 1e255)
        else:
            base_widget = QSpinBox()
            base_widget.setRange(-2147483648, 2147483647)

        # Callbacks
        def update_value(entry_obj: DatabaseEntry):
            base_widget.setToolTip(entry_obj.description)
            base_widget.setValue(entry_obj.entry_value)
            if not entry_obj.attributes.get("editable", True):
                base_widget.setStyleSheet("color: #707070;")
                base_widget.setReadOnly(True)
            else:
                base_widget.setStyleSheet("color: #000000;")
                base_widget.setReadOnly(False)
        self.add_callback("value_up_" + id, update_value)
        update_value(self) # Initial update

        # Update the entry
        def update_entry(value):
            self.safe_set("entry_value", value)
        base_widget.valueChanged.connect(update_entry)

        return base_widget
    
    def _get_RangeEntry_widget(self, id: str, entry_type: Literal["int", "float"]) -> QWidget: # TODO : Correct to safe_set of a dict
        """Get the range entry widget."""
        PRECISION_FACTOR = 100
        containment_widget = QWidget()
        layout = QHBoxLayout()
        containment_widget.setLayout(layout)

        # Compose the slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        numerical_entry = QDoubleSpinBox()
        numerical_entry.setDecimals(2 if entry_type == "float" else 0)
        numerical_entry.setStepType(QDoubleSpinBox.StepType.AdaptiveDecimalStepType)
        numerical_entry.setSingleStep(1/PRECISION_FACTOR)
        layout.addWidget(slider)
        layout.addWidget(numerical_entry)

        # Callbacks
        def update_value(entry_obj: DatabaseEntry):
            containment_widget.setToolTip(entry_obj.description)
            
            value_dict:dict = entry_obj.entry_value
            dict_values:list[float|int] = [float(value_dict.get(key, 0)) for key in ["min", "max", "value"]]
            min_max_val_float = [float(val)*PRECISION_FACTOR for val in dict_values]
            min_max_val_int   = [int(val) for val in min_max_val_float]

            if not entry_obj.attributes.get("editable", True):
                containment_widget.setStyleSheet("color: #707070;")
                slider.setDisabled(True)
                numerical_entry.setReadOnly(True)
            else:
                containment_widget.setStyleSheet("color: #000000;")
                slider.setDisabled(False)
                numerical_entry.setReadOnly(False)
            
            slider.setRange(min_max_val_int[0], min_max_val_int[1])
            slider.setValue(min_max_val_int[2])
            slider.setTickInterval((min_max_val_int[1]- min_max_val_int[0])//10)
            numerical_entry.setRange(dict_values[0], dict_values[1])
            numerical_entry.setValue(dict_values[2])

        self.add_callback("value_up_" + id, update_value)
        update_value(self) # Initial update

        # Slider update
        def on_slider_change(value):
            numerical_entry.setValue(value/PRECISION_FACTOR)
            self.entry_value["value"] = value/PRECISION_FACTOR
        slider.valueChanged.connect(on_slider_change)

        # Numerical entry update
        def on_numerical_entry_change(value):
            slider.setValue(int(value*PRECISION_FACTOR))
            self.entry_value["value"] = value
        numerical_entry.valueChanged.connect(on_numerical_entry_change)

        return containment_widget
        
    def _get_BoolEntry_widget(self, id: str) -> QWidget:
        """Get the bool entry widget."""
        container_widget = QWidget()
        layout = QHBoxLayout()
        container_widget.setLayout(layout)
        widget = QCheckBox()
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()

        # Callbacks
        def update_value(entry_obj: DatabaseEntry):
            widget.setToolTip(entry_obj.description)
            widget.setChecked(entry_obj.entry_value)
            if not entry_obj.attributes.get("editable", True):
                widget.setStyleSheet("color: #707070;")
                widget.setDisabled(True)
            else:
                widget.setStyleSheet("color: #000000;")
                widget.setDisabled(False)
        self.add_callback("value_up_" + id, update_value)
        update_value(self) # Initial update

        # Update the entry
        def update_entry(value):
            self.safe_set("entry_value", value)
        widget.stateChanged.connect(update_entry)

        return container_widget

    def _get_BulletEntry_widget(self, id: str, entry_type: Literal["list", "dict"]) -> QWidget: # TODO : Implement the list and dict entries
        """Get the bullet entry widget."""
        widget = QLabel("Not implemented yet")
        return widget       
    
    def _get_SuffixEntry_widget(self, id: str) -> QWidget: # TODO : Correct to safe_set of a dict
        """Get the suffix entry widget."""
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        entry_box = QLineEdit()
        suffix_box = QLabel()
        layout.addWidget(entry_box)
        layout.addWidget(suffix_box)
        
        # Callbacks
        def update_value(entry_obj: DatabaseEntry):
            string_value = convertSuffix(entry_obj.entry_value["value"])
            entry_box.setText(string_value)
            suffix_box.setText(entry_obj.entry_value["suffix"])
            entry_box.setToolTip(entry_obj.description)
            if not entry_obj.attributes.get("editable", True):
                entry_box.setStyleSheet("color: #707070;")
                entry_box.setReadOnly(True)
            else:
                entry_box.setStyleSheet("color: #000000;")
                entry_box.setReadOnly(False)
        self.add_callback("value_up_" + id, update_value)
        update_value(self)

        # Update the entry
        def update_entry(): 
            value = entry_box.text()
            new_entry_value = self.entry_value 
            float_value = convertSuffix(value)
            new_entry_value["value"] = float_value if float_value is not None else 0
            self.safe_set("entry_value", new_entry_value)
        entry_box.editingFinished.connect(update_entry)

        return widget
    
    # TODO : Implement the other entry types


####################################################################################################

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

    def add_entry(self, id: str, name: str, description: str, entry_type: DatabaseEntry.GenericEntry, entry_value: any, attributes: dict = {}) -> DatabaseEntry:
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
            # Skip hidden entries
            if entry.attributes.get("hidden", False):
                continue
            layout.addWidget(entry.get_full_widget(id))
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
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

        # Register the removal of the callbacks
        def remove_callbacks():
            for class_ in self._classes.values():
                class_.remove_gui_callbacks(id)
            self.remove_gui_callbacks(id)
        window.destroyed.connect(remove_callbacks)

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
        entry_type= DatabaseEntry.StringEntry,
        entry_value= "content1.wav",
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class1.add_entry(
        id="content2",
        name="Content 2",
        description="Content 2 description, with content wrap, because we are that strong ! But weirdly, the auto dimentioning of the window is not working properly",
        entry_type= DatabaseEntry.StringEntry,
        entry_value= "content2.wav",
    )
    class1.add_entry(
        id="content_hidden",
        name="Hidden Content",
        description="This should not be visible, and this is also a word wrap test, so that i can fix a bug",
        entry_type= DatabaseEntry.StringEntry,
        entry_value= "spoooky message",
        attributes={
            "hidden": True,
        },
    )
    ### --- ###
    class2 = database.add_class(
        id="class2",
        name="Class 2",
        description="Class 2 description, be cause why not ?",
    )
    class2.add_entry(
        id="content3",
        name="Content 3",
        description="Content 3 description (from class 2) - This is mainly to see if the class separation works",
        entry_type= DatabaseEntry.StringEntry,
        entry_value= "content3.wav",
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class2.add_entry(
        id="content4",
        name="Uneditable Content",
        description="This should not be editable, so that the user can't change it, but still copy it, whilst giving a slight hint that it is not editable",
        entry_type= DatabaseEntry.StringEntry,
        entry_value= "content4.wav",
        attributes={
            "editable": False,
        },
    )
    ### --- ###
    class3 = database.add_class(
        id="class3",
        name="Class 3 - Test all other types",
        description="Class 3 description, be cause why not ?",
    )
    class3.add_entry(
        id="content5",
        name="Integer Content",
        description="I'm trying to test all the other types, so here is an integer",
        entry_type= DatabaseEntry.IntEntry,
        entry_value= 5,
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class3.add_entry(
        id="content6",
        name="Float Content",
        description="I'm trying to test all the other types, so here is a float (its pi*100 = 314.1592653589793)",
        entry_type= DatabaseEntry.FloatEntry,
        entry_value= np.pi*100,
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class3.add_entry(
        id="content7",
        name="Int Range Content",
        description="I'm trying to test all the other types, so here is an int range",
        entry_type= DatabaseEntry.IntRangeEntry,
        entry_value= {"min": 0, "max": 10, "value": 5},
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class3.add_entry(
        id="content8",
        name="Float Range Content",
        description="I'm trying to test all the other types, so here is a float range (its pi*100 = 314.1592653589793)",
        entry_type= DatabaseEntry.FloatRangeEntry,
        entry_value= {"min": 0, "max": np.pi*100, "value": np.pi*50},
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class3.add_entry(
        id="content9",
        name="Bool Content",
        description="I'm trying to test all the other types, so here is a bool",
        entry_type= DatabaseEntry.BoolEntry,
        entry_value= True,
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class3.add_entry(
        id="content10",
        name="List Content",
        description="I'm trying to test all the other types, so here is a list",
        entry_type= DatabaseEntry.ListEntry,
        entry_value= ["item1", "item2", "item3"],
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class3.add_entry(
        id="content11",
        name="Dict Content",
        description="I'm trying to test all the other types, so here is a dict",
        entry_type= DatabaseEntry.DictEntry,
        entry_value= {"key1": "value1", "key2": "value2", "key3": "value3"},
        attributes={
            "hidden": False,
            "editable": True,
        },
    )
    class3.add_entry(
        id="content12",
        name="Suffix Content",
        description="I'm trying to test all the other types, so here is a suffix (its pi*1e9 = 3.14 G Hz)",
        entry_type= DatabaseEntry.SuffixEntry,
        entry_value= {"value": np.pi*1e9, "suffix": "Hz"},
        attributes={
            "hidden": False,
            "editable": True,
        },
    )

    return True


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

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
    content1.safe_set("attributes", {"hidden": False})
    content1.safe_set("entry_value", "new_content1.wav")
    content1.safe_set("description", "New description that is long enough to test the wrapping of the text in the GUI")

    # Make a system to add callbacks and remove them for stuff outside the database
    content1.add_callback("print_change", lambda entry: logging.info(f"Entry content1 changed to {entry.get_value()}"))
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

    # Add the hidden content, as this case is just to show the hidden content
    layout.addWidget(QLabel("Hidden content"))
    hidden_entry = class1.get_entry("content_hidden")
    layout.addWidget(hidden_entry.get_full_widget("content_hidden"))

    central_widget.setLayout(layout)
    window.show()

    sys.exit(app.exec())
    # Anything later than here has problems with the sys.exit(app.exec()) call



