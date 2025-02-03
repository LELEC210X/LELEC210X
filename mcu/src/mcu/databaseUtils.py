from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QGridLayout,
    QSpinBox,
    QTabWidget,
    QSlider,
    QSpacerItem,
    QColorDialog,
    QDoubleSpinBox,
    QLineEdit,
    QGroupBox,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
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

SUFFIX_SCALES = {
        -24: "y",
        -21: "z",
        -18: "a",
        -15: "f",
        -12: "p",
        -9: "n",
        -6: "u",
        -3: "m",
        0: "",
        3: "k",
        6: "M",
        9: "G",
        12: "T",
        15: "P",
        18: "E",
        21: "Z",
        24: "Y",
    }

def float_to_scaled_suffix(value: float):
    if value == 0:
        return (0, "")
    order = int(np.floor(np.log10(abs(value)) / 3) * 3)
    return (value / 10 ** order, SUFFIX_SCALES[order])

def scaled_suffix_to_float(value: float, suffix: str):
    # If suffix is empty, just return the given value
    if not suffix:
        return value

    # Otherwise, try matching the first character to a scale
    for order, scale in SUFFIX_SCALES.items():
        if len(suffix) > 0 and scale == suffix[0]:
            return value * 10 ** order

    # If no match found, return the original value
    return value

class ContentDatabase:
    """
    A simple database class that stores categories and items and synchrnoizes them with widgets.

    The database is thread-safe and can be accessed from multiple threads.

    The database can be initialized with a custom initialisation function that populates the database.

    The database can be used to generate widgets for each category.

    The possible types of items that can be added to the database are:
    - SuffixFloat
    - Integer
    - RangeInt
    - RangeFloat
    - Text
    - Color
    - Boolean
    - List
    - Dictionary    
    - File
    - Folder
    - ChoiceBox
    - ConstantText
    
    """
    def __init__(self, initialisation_func: callable, logger: logging.Logger, debug: bool = False):
        self.lock = Lock()
        self.db = {}
        self.app_path = pathlib.Path(__file__).parent.absolute()
        self.logger = logger
        self.debug = debug

        initialisation_func(self)

    def debug_log(self, message: str):
        if self.debug:
            self.logger.debug(message)

    def create_category(self, category_name: str):
        with self.lock:
            if category_name not in self.db:
                self.db[category_name] = {}
                self.debug_log(f"Category created: {category_name}")
            else:
                self.debug_log(f"Category already exists: {category_name}")

    def add_item(self, category_name: str, item_name: str, item_value):
        with self.lock:
            if category_name in self.db:
                if item_name not in self.db[category_name]:
                    self.db[category_name][item_name] = item_value
                    self.debug_log(f"Item added: {item_name}")
                else:
                    self.debug_log(f"Item already exists: {item_name} - {self.db[category_name][item_name]}")
            else:
                self.debug_log(f"Category does not exist: {category_name}")

    def get_item(self, category_name: str, item_name: str):
        with self.lock:
            if category_name in self.db:
                if item_name in self.db[category_name]:
                    return self.db[category_name][item_name]
                else:
                    self.debug_log(f"Item does not exist: {item_name}")
            else:
                self.debug_log(f"Category does not exist: {category_name}")

    def gen_category_widget(self, category_name: str):
        with self.lock:
            if category_name in self.db:
                category_widget = QGroupBox(category_name)
                category_layout = QVBoxLayout()
                # Add items to the category
                for item_name, item_value in self.db[category_name].items():
                    category_layout.addWidget(item_value.gen_widget())

                # Test add the last widget twice
                if len(self.db[category_name]) > 0:
                    category_layout.addWidget(list(self.db[category_name].values())[-1].gen_widget())

                # Push up the items
                category_layout.addStretch()
                category_widget.setLayout(category_layout)
                return category_widget
            else:
                self.debug_log(f"Category does not exist: {category_name}")

    class DatabaseElementTemplate:
        """
        Template for the database element
        """
        def __init__(self, name: str, description: str, value): 
            self.lock = Lock()
            self.updating = False
            self.name = name
            self.description = description
            self.value = value
            self.callbacks = []

        def register_callback(self, callback: callable):
            with self.lock:
                self.callbacks.append(callback)
        def trigger_callbacks(self):
            with self.lock:
                self.updating = True
                for callback in self.callbacks:
                    callback(self.value)
                self.updating = False

        def get_value(self): 
            return self.value
        
        def set_value(self, value): 
            if self.updating:
                return
            self.value = value
            self.trigger_callbacks()

        def __str__(self): ...
        def __repr__(self): ...
        def gen_widget(self): ...

    """
    The following types can be registered:
    >> Editable or not (default to editable, else, it becomes a label)
    - Suffixed Float (TextEntry with custom handler for suffixes)
    - Integer (SpinBox)
    - RangeInt (Slider)
    - RangeFloat (Slider)
    - Text (LineEdit)
    - Color (ColorDialog)
    - Boolean (CheckBox)
    - List (List of LineEdit)
    - Dictionary (List of LineEdit with label)
    - File (File Dialog)
    - Folder (File Dialog)
    
    >> Not editable
    - Date Time (Calendar)

    >> Editable
    - ChoiceBox (ComboBox)
    """

    class SuffixFloat(DatabaseElementTemplate):
        """
        Float with suffix such as 1.2kHz or 1.2MHz

        Value composition :
            tuple<float, str> : (value, suffix)
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            scaled_value, suffix_prefix = float_to_scaled_suffix(self.value[0])
            return f"{scaled_value} {suffix_prefix}{self.value[1]}"
        
        def __repr__(self): 
            return f"Suffixed Float: {self.name} - {self.value}"
        
        def handle_text_entry(self, text_entry: QLineEdit):
            text = text_entry.text().strip()
            # Return if empty
            if not text:
                return
            
            import re
            # Regex captures a float number followed by optional text (suffix)
            match = re.match(r"^([-+]?\d+(?:\.\d+)?)(.*)$", text)
            if not match:
                return  # Parsing failed
            
            # Extract the numeric part and any suffix text
            numeric_str, suffix_str = match.groups()
            numeric_str = numeric_str.strip()
            suffix_str = suffix_str.strip()  # Remove extra whitespace
            
            # Convert string to float and apply suffix
            try:
                numeric_val = float(numeric_str)
            except ValueError:
                return  # Not a valid float
            
            # Now update the internal value. We reuse the original ‘second’ element of value (e.g., "Hz")
            # or you can also parse suffix_str fully if you want to re-evaluate the unit.
            new_val = scaled_suffix_to_float(numeric_val, suffix_str)
            self.set_value((new_val, self.value[1]))

        def gen_widget(self):
            scaled_value, suffix_prefix = float_to_scaled_suffix(self.value[0])
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            text_entry = QLineEdit(str(scaled_value) + " " + suffix_prefix) # Editable text entry
            suffix_label = QLabel(self.value[1]) # Constant suffix (callback to update)
            text_entry.returnPressed.connect(lambda: self.handle_text_entry(text_entry))
            self.register_callback(lambda value: suffix_label.setText(value[1]))
            def handle_text_entry_callback(value):
                scaled_value, suffix_prefix = float_to_scaled_suffix(value[0])
                text_entry.setText(str(scaled_value) + " " + suffix_prefix)
            self.register_callback(handle_text_entry_callback)
            layout.addWidget(label)
            layout.addWidget(text_entry)
            layout.addWidget(suffix_label)
            widget.setLayout(layout)
            return widget

    class Integer(DatabaseElementTemplate):
        """
        Integer value

        Value composition :
            int : value
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return str(self.value)
        
        def __repr__(self): 
            return f"Integer: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            spin_box = QSpinBox()
            spin_box.setRange(-2**31, 2**31 - 1)
            spin_box.setValue(self.value)
            spin_box.valueChanged.connect(lambda value: self.set_value(value))
            self.register_callback(lambda value: spin_box.setValue(value))
            layout.addWidget(label)
            layout.addWidget(spin_box)
            widget.setLayout(layout)
            return widget
        
    class RangeInt(DatabaseElementTemplate):
        """
        Integer range value

        Value composition :
            tuple<int, int, int> : (value, min, max)
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return f"{self.value[0]} ({self.value[1]}-{self.value[2]})"
        
        def __repr__(self): 
            return f"Range Integer: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout(widget)

            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)

            # Make the slider horizontal
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(self.value[1], self.value[2])
            slider.setValue(self.value[0])

            # Optionally show ticks
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval((self.value[2] - self.value[1]) // 10 or 1)

            # Add a label to show the slider's value
            value_label = QLabel(str(slider.value()))

            # Update internal value and label on slider move
            slider.valueChanged.connect(lambda val: (
                self.set_value(val),
                value_label.setText(str(val))
            ))

            # If this value changes from elsewhere, keep the widget in sync
            self.register_callback(lambda val: (
                slider.setValue(val),
                value_label.setText(str(val))
            ))

            layout.addWidget(label)
            layout.addWidget(slider)
            layout.addWidget(value_label)
            return widget
        
    class RangeFloat(DatabaseElementTemplate):
        """
        Float range value

        Value composition:
            tuple<float, float, float> : (value, min, max)
        """
        def __init__(self, name: str, description: str, value):
            super().__init__(name, description, value)
            # Decide how many decimals you want. For 2 decimals, factor=100
            self.factor = 100  

        def __str__(self):
            return f"{self.value[0]} ({self.value[1]}-{self.value[2]})"
        
        def __repr__(self):
            return f"Range Float: {self.name} - {self.value}"
        
        def _slider_to_float(self, slider_val: int) -> float:
            """ Convert slider integer value back to a float. """
            return slider_val / self.factor
        
        def _float_to_slider(self, float_val: float) -> int:
            """ Convert a float to the slider’s integer scale. """
            return int(float_val * self.factor)
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout(widget)

            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)

            # Create a horizontal QSlider
            slider = QSlider(Qt.Orientation.Horizontal)
            # Scale the min, max, and current value
            slider.setRange(self._float_to_slider(self.value[1]), self._float_to_slider(self.value[2]))
            slider.setValue(self._float_to_slider(self.value[0]))

            # Show optional ticks
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            # For a float range, pick a sensible tick interval
            slider.setTickInterval(self._float_to_slider((self.value[2] - self.value[1]) / 10.0) or 1)

            # Label to show current float value
            value_label = QLabel(f"{self.value[0]:.2f}")

            # Update DB and label on slider move
            slider.valueChanged.connect(lambda val_int: (
                self.set_value(
                    (self._slider_to_float(val_int),
                    self.value[1], self.value[2])
                ),
                value_label.setText(f"{self._slider_to_float(val_int):.2f}")
            ))

            # Keep the slider/label in sync if the float is updated externally
            self.register_callback(lambda val: (
                slider.setValue(self._float_to_slider(val[0])),
                value_label.setText(f"{val[0]:.2f}")
            ))

            layout.addWidget(label)
            layout.addWidget(slider)
            layout.addWidget(value_label)
            return widget
        
    class Text(DatabaseElementTemplate):
        """
        Text value

        Value composition:
            str : value
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return self.value
        
        def __repr__(self): 
            return f"Text: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            text_entry = QLineEdit(self.value)
            text_entry.textChanged.connect(lambda text: self.set_value(text))
            self.register_callback(lambda text: text_entry.setText(text))
            layout.addWidget(label)
            layout.addWidget(text_entry)
            widget.setLayout(layout)
            return widget
        
    class Color(DatabaseElementTemplate):
        """
        Color value

        Value composition:
            tuple<int, int, int> : (r, g, b)
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return f"({self.value[0]}, {self.value[1]}, {self.value[2]})"
        
        def __repr__(self): 
            return f"Color: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            color_button = QPushButton("Choose Color")
            color_button.setStyleSheet(
                f"background-color: rgb({self.value[0]}, {self.value[1]}, {self.value[2]});"  # Set initial color
            )
            color_button.clicked.connect(self.handle_color_dialog)
            self.register_callback(lambda color: color_button.setStyleSheet(
                f"background-color: rgb({color[0]}, {color[1]}, {color[2]});"
            ))
            layout.addWidget(label)
            layout.addWidget(color_button)
            widget.setLayout(layout)
            return widget
        
        def handle_color_dialog(self):
            color = QColorDialog.getColor(QtGui.QColor(*self.value), None)
            if color.isValid():
                self.set_value((color.red(), color.green(), color.blue()))

    class Boolean(DatabaseElementTemplate):
        """
        Boolean value

        Value composition:
            bool : value
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return str(self.value)
        
        def __repr__(self): 
            return f"Boolean: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)

            check_box = QCheckBox()
            check_box.setChecked(self.value)

            # Use toggled for a direct bool
            check_box.toggled.connect(lambda checked: self.set_value(checked))

            self.register_callback(lambda new_value: check_box.setChecked(new_value))

            layout.addWidget(label)
            layout.addWidget(check_box)
            widget.setLayout(layout)
            return widget
        
    class List(DatabaseElementTemplate):
        """
        List of text values

        Value composition:
            list<str> : value
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return ", ".join(self.value)
        
        def __repr__(self): 
            return f"List: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)

            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            layout.addWidget(label)

            for i, text in enumerate(self.value):
                widget_row = QWidget()
                row_layout = QHBoxLayout(widget_row)
                spacer = QLabel()
                spacer.setFixedWidth(100)
                text_entry = QLineEdit(text)
                
                text_entry.textChanged.connect(lambda new_text, idx=i: (
                    self.value.__setitem__(idx, new_text),
                    self.set_value(self.value)
                ))

                self.register_callback(lambda new_list, idx=i, txt_entry=text_entry:
                    txt_entry.setText(new_list[idx])
                )

                row_layout.setContentsMargins(0, 0, 0, 0)

                row_layout.addWidget(spacer)
                row_layout.addWidget(text_entry)
                layout.addWidget(widget_row)
            
            layout.addStretch()
            widget.setLayout(layout)
            return widget
        
    class Dictionary(DatabaseElementTemplate):
        """
        Dictionary of text values

        Value composition:
            dict<str, str> : value
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return ", ".join([f"{key}: {val}" for key, val in self.value.items()])
        
        def __repr__(self): 
            return f"Dictionary: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)

            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            layout.addWidget(label)

            for key, value in self.value.items():
                widget_row = QWidget()
                row_layout = QHBoxLayout(widget_row)
                key_entry = QLabel(key)
                key_entry.setFixedWidth(100)
                val_entry = QLineEdit(value)

                val_entry.textChanged.connect(lambda new_text, k=key: (
                    self.value.__setitem__(k, new_text),
                    self.set_value(self.value)
                ))

                self.register_callback(lambda new_dict, k=key, val_entry=val_entry: (
                    val_entry.setText(new_dict[k])
                ))

                row_layout.setContentsMargins(0, 0, 0, 0)

                row_layout.addWidget(key_entry)
                row_layout.addWidget(val_entry)
                layout.addWidget(widget_row)
            
            layout.addStretch()
            widget.setLayout(layout)
            return widget
        
    class File(DatabaseElementTemplate):
        """
        File value

        Value composition:
            pathlib.Path : value
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return str(self.value)
        
        def __repr__(self): 
            return f"File: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            file_entry = QLineEdit(str(self.value))
            file_entry.setReadOnly(True)
            file_button = QPushButton("Choose File")
            file_button.clicked.connect(self.handle_file_dialog)
            self.register_callback(lambda value: file_entry.setText(str(value)))
            layout.addWidget(label)
            layout.addWidget(file_entry)
            layout.addWidget(file_button)
            widget.setLayout(layout)
            return widget
        
        def handle_file_dialog(self):
            file_path, _ = QFileDialog.getOpenFileName(None, "Open File", str(self.value), "All Files (*)")
            if file_path:
                self.set_value(pathlib.Path(file_path))

    class Folder(DatabaseElementTemplate):
        """
        Folder value

        Value composition:
            pathlib.Path : value
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return str(self.value)
        
        def __repr__(self): 
            return f"Folder: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            folder_entry = QLineEdit(str(self.value))
            folder_entry.setReadOnly(True)
            folder_button = QPushButton("Choose Folder")
            folder_button.clicked.connect(self.handle_folder_dialog)
            self.register_callback(lambda value: folder_entry.setText(str(value)))
            layout.addWidget(label)
            layout.addWidget(folder_entry)
            layout.addWidget(folder_button)
            widget.setLayout(layout)
            return widget
        
        def handle_folder_dialog(self):
            folder_path = QFileDialog.getExistingDirectory(None, "Open Folder", str(self.value))
            if folder_path:
                self.set_value(pathlib.Path(folder_path))

    class ChoiceBox(DatabaseElementTemplate):
        """
        Choice box value

        Value composition:
            tuple<int, list<str>> : (index, choices)
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return self.value[1][self.value[0]]
        
        def __repr__(self): 
            return f"ChoiceBox: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            choice_box = QComboBox()
            choice_box.addItems(self.value[1])
            choice_box.setCurrentIndex(self.value[0])
            choice_box.currentIndexChanged.connect(lambda index: self.set_value((index, self.value[1])))
            self.register_callback(lambda value: choice_box.setCurrentIndex(value[0]))
            layout.addWidget(label)
            layout.addWidget(choice_box)
            widget.setLayout(layout)
            return widget
        
    class ConstantText(DatabaseElementTemplate):
        """
        Constant text value

        Value composition:
            str : value
        """
        def __init__(self, name: str, description: str, value): 
            super().__init__(name, description, value)

        def __str__(self): 
            return self.value
        
        def __repr__(self): 
            return f"ConstantText: {self.name} - {self.value}"
        
        def gen_widget(self):
            widget = QWidget()
            layout = QHBoxLayout()
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            text_label = QLabel(self.value)
            self.register_callback(lambda value: text_label.setText(value)) # Update the label
            layout.addWidget(label)
            layout.addWidget(text_label)
            widget.setLayout(layout)
            return widget

def init_db(db: ContentDatabase):
    """
    Simple initialization function that creates a category
    and populates it with one SuffixFloat example item.
    """
    db.create_category("Audio Settings")
    audio_gain_item = db.SuffixFloat(
        name="Gain",
        description="Controls the gain of the audio signal",
        value=(1e3, "Hz")  # Example: 1000 Hz
    )
    db.add_item("Audio Settings", "gain", audio_gain_item)
    db.add_item("Audio Settings", "gain2", db.Integer("Gain2", "Controls the gain of the audio signal", 1000))
    db.add_item("Audio Settings", "gain3", db.RangeInt("Gain3", "Controls the gain of the audio signal", (1000, 0, 2000)))
    db.add_item("Audio Settings", "gain4", db.RangeFloat("Gain4", "Controls the gain of the audio signal", (1000, 0, 2000)))
    db.add_item("Audio Settings", "gain5", db.Text("Gain5", "Controls the gain of the audio signal", "1000"))
    db.add_item("Audio Settings", "gain6", db.Color("Gain6", "Controls the gain of the audio signal", (255, 0, 0)))
    db.add_item("Audio Settings", "gain7", db.Boolean("Gain7", "Controls the gain of the audio signal", True))
    db.add_item("Audio Settings", "gain8", db.List("Gain8", "Controls the gain of the audio signal", ["1000", "2000", "3000"]))
    db.add_item("Audio Settings", "gain9", db.Dictionary("Gain9", "Controls the gain of the audio signal", {"key1": "1000", "key2": "2000"}))
    db.add_item("Audio Settings", "gain10", db.File("Gain10", "Controls the gain of the audio signal", db.app_path / "example.txt"))
    db.add_item("Audio Settings", "gain11", db.Folder("Gain11", "Controls the gain of the audio signal", db.app_path))
    db.add_item("Audio Settings", "gain12", db.ChoiceBox("Gain12", "Controls the gain of the audio signal", (0, ["1000", "2000", "3000"])))
    db.add_item("Audio Settings", "gain13", db.ConstantText("Gain13", "Controls the gain of the audio signal", "1000"))

class MainWindow(QMainWindow):
    def __init__(self, db: ContentDatabase):
        super().__init__()
        self.db = db
        self.setWindowTitle("DatabaseUtils Example")

        # Create a central widget and layout
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        # Create a scroll area to hold all categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Generate a widget for each category and add it to scroll
        for category_name in db.db:
            cat_widget = db.gen_category_widget(category_name)
            if cat_widget:
                scroll_layout.addWidget(cat_widget)

        # Push content up and finalize
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        central_layout.addWidget(scroll_area)
        self.setCentralWidget(central_widget)

def main():
    # Create a logger
    logger = logging.getLogger("DatabaseUtilsExample")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    logger.addHandler(ch)

    # Create a Qt Application
    app = QApplication(sys.argv)

    # Create the ContentDatabase
    db = ContentDatabase(initialisation_func=init_db, logger=logger, debug=True)

    # Create and show the main window
    window = MainWindow(db)
    window.resize(800, 600)
    window.show()

    # Execute the app
    sys.exit(app.exec())

if __name__ == "__main__":
    main()