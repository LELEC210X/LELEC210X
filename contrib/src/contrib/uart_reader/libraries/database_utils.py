import logging
import pathlib
import sys
from threading import RLock as Lock

import numpy as np
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

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
    """Convert a float to a scaled value and suffix."""
    if value == 0:
        return (0, "")
    # Find the order of magnitude of the value
    order = int(np.floor(np.log10(abs(value)) / 3) * 3)
    return (value / 10**order, SUFFIX_SCALES[order])


def scaled_suffix_to_float(value: float, suffix: str):
    """Convert a scaled value and suffix back to a float."""
    # If suffix is empty, just return the given value
    if not suffix:
        return value

    # Otherwise, try matching the first character to a scale
    for order, scale in SUFFIX_SCALES.items():
        if len(suffix) > 0 and scale == suffix[0]:
            return value * 10**order

    # If no match found, return the original value
    return value


class ContentDatabase:
    """
    A simple, thread-safe database class that stores categories and items, synchronizing them between widgets.

    Features:
    - Thread-safe access from multiple threads.
    - Custom initialization function to populate the database.
    - Generate widgets for each element or a whole cathegory easilly.

    Supported Item Types:
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

    def __init__(
        self, initialisation_func: callable, logger: logging.Logger, debug: bool = False
    ):
        self.lock = Lock()
        self.db = {}
        self.app_path = pathlib.Path(__file__).parent.absolute()
        self.logger = logger
        self.debug = debug

        # Run the initialization function
        initialisation_func(self)

    def debug_log(self, message: str) -> None:
        """Log a message if debug is enabled (To reduce log spam, even in debug mode)."""
        if self.debug:
            self.logger.debug(message)

    def create_category(self, category_name: str) -> None:
        """Create a new category in the database."""
        with self.lock:
            # Check if the category already exists
            if category_name not in self.db:
                self.db[category_name] = {}
                self.debug_log(f"Category created: {category_name}")
            else:
                self.debug_log(f"Category already exists: {category_name}")

    def add_item(self, category_name: str, item_name: str, item_value) -> None:
        """Add a new item to a category in the database."""
        with self.lock:
            # Check if the category exists
            if category_name in self.db:
                # Check if the item already exists
                if item_name not in self.db[category_name]:
                    self.db[category_name][item_name] = item_value
                    self.debug_log(f"Item added: {item_name}")
                else:
                    self.debug_log(
                        f"Item already exists: {item_name} - {self.db[category_name][item_name]}"
                    )
            else:
                self.debug_log(f"Category does not exist: {category_name}")

    def get_item(self, category_name: str, item_name: str) -> "DatabaseElementTemplate":
        """Get an item from a category in the database."""
        with self.lock:
            # Check if the category and item exist
            if category_name in self.db:
                # Check if the item exists
                if item_name in self.db[category_name]:
                    return self.db[category_name][item_name]
                else:
                    self.debug_log(f"Item does not exist: {item_name}")
            else:
                self.debug_log(f"Category does not exist: {category_name}")
            return None

    def gen_category_widget(self, category_name: str) -> QGroupBox:
        """Generate a widget for a category in the database (using each element's generation function)."""
        with self.lock:
            # Check if the category exists
            if category_name in self.db:
                category_widget = QGroupBox(category_name)
                category_layout = QVBoxLayout()
                # Add all full widgets for each item in the category
                for item_name, item_value in self.db[category_name].items():
                    category_layout.addWidget(item_value.gen_widget_full())

                # Push up the items
                category_layout.addStretch()
                category_widget.setLayout(category_layout)
                return category_widget
            else:
                self.debug_log(f"Category does not exist: {category_name}")

    def reset_database(self) -> None:
        """Reset the database to an empty state, by signaling all items to reset."""
        with self.lock:
            for category in self.db.values():
                for item in category.values():
                    item.trigger_callbacks()

    def import_database(self, npy_file: pathlib.Path) -> None:
        """Import the values of the elements from a numpy file."""
        with self.lock:
            try:
                # Load the data from the numpy file
                data = np.load(npy_file, allow_pickle=True).item()
                # Iterate over all categories and items to set their values
                for category_name, category in data.items():
                    for item_name, item_value in category.items():
                        item = self.get_item(category_name, item_name)
                        if item:
                            item.set_value(item_value)
                self.logger.info(f"Database imported: {npy_file}")
            except Exception as e:
                self.logger.error(f"Failed to import database: {e}")

    def export_database(self, npy_file: pathlib.Path) -> None:
        """Export the values of the elements to a numpy file."""
        with self.lock:
            data = {}
            # Iterate over all categories and items to save their values
            for category_name, category in self.db.items():
                data[category_name] = {}
                for item_name, item_value in category.items():
                    data[category_name][item_name] = item_value.get_value()
            # Try to save the data to a numpy file
            try:
                np.save(npy_file, data)
                self.logger.info(f"Database exported: {npy_file}")
            except Exception as e:
                self.logger.error(f"Failed to export database: {e}")

    # ------------------ Database Element Template ------------------
    class DatabaseElementTemplate:
        """
        Template for the database element
        """

        def __init__(self, name: str, value, description: str = ""):
            self.lock = Lock()
            self.updating = False
            self.name = name
            self.description = description
            self.value = value
            self.callbacks = []

        def register_callback(self, callback: callable) -> None:
            """Register a callback to be triggered when the value changes."""
            with self.lock:
                # Add a callback to the list
                self.callbacks.append(callback)

        def trigger_callbacks(self) -> None:
            """Trigger all registered callbacks."""
            with self.lock:
                # Trigger all callbacks
                self.updating = True
                for callback in self.callbacks:
                    callback(self.value)
                self.updating = False

        def get_value(self) -> any:
            """Get the value of the element."""
            return self.value

        def set_value(self, value) -> None:
            """Set the value of the element and trigger all callbacks."""
            # If the callback is updating, return (to avoid infinite loops)
            if self.updating:
                return
            # Update the value and trigger callbacks
            self.value = value
            self.trigger_callbacks()

        # Implement these methods in the derived classes
        def __str__(self) -> str: ...
        def __repr__(self) -> str: ...
        def gen_widget_element(self) -> QWidget: ...

        # This method can be overridden in the derived classes if needed
        def gen_widget_label(self) -> QLabel:
            """Generate a label widget for the element."""
            label = QLabel(self.name)
            label.setToolTip(self.description)
            label.setFixedWidth(100)
            return label

        def gen_widget_full(self) -> QWidget:
            """Generate a full widget for the element."""
            widget = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(self.gen_widget_label())
            layout.addWidget(self.gen_widget_element())
            widget.setLayout(layout)
            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

    # ------------------ Database Element Types ------------------

    class SuffixFloat(DatabaseElementTemplate):
        """
        Float with suffix such as 1.2kHz or 1.2MHz

        Value composition :
            tuple<float, str> : (value, suffix)
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

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

        def gen_widget_element(self) -> QWidget:
            scaled_value, suffix_prefix = float_to_scaled_suffix(self.value[0])
            widget = QWidget()
            layout = QHBoxLayout()
            text_entry = QLineEdit(
                str(scaled_value) + " " + suffix_prefix
            )  # Editable text entry
            suffix_label = QLabel(self.value[1])  # Constant suffix (callback to update)
            text_entry.returnPressed.connect(lambda: self.handle_text_entry(text_entry))
            self.register_callback(lambda value: suffix_label.setText(value[1]))

            def handle_text_entry_callback(value):
                scaled_value, suffix_prefix = float_to_scaled_suffix(value[0])
                text_entry.setText(str(scaled_value) + " " + suffix_prefix)

            self.register_callback(handle_text_entry_callback)
            layout.addWidget(text_entry)
            layout.addWidget(suffix_label)
            widget.setLayout(layout)

            # Make the widget narrower
            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")

            return widget

    class Integer(DatabaseElementTemplate):
        """
        Integer value

        Value composition :
            int : value
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return str(self.value)

        def __repr__(self):
            return f"Integer: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            widget = QWidget()
            layout = QHBoxLayout()
            spin_box = QSpinBox()
            spin_box.setRange(-(2**31), 2**31 - 1)
            spin_box.setValue(self.value)
            spin_box.valueChanged.connect(lambda value: self.set_value(value))
            self.register_callback(lambda value: spin_box.setValue(value))
            layout.addWidget(spin_box)
            widget.setLayout(layout)

            # Make the widget narrower
            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

    class RangeInt(DatabaseElementTemplate):
        """
        Integer range value

        Value composition :
            tuple<int, int, int> : (value, min, max)
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return f"{self.value[0]} ({self.value[1]}-{self.value[2]})"

        def __repr__(self):
            return f"Range Integer: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the range integer."""
            widget = QWidget()
            layout = QHBoxLayout(widget)

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
            slider.valueChanged.connect(
                lambda val: (
                    self.set_value((val, self.value[1], self.value[2])),
                    value_label.setText(str(int(val))),
                )
            )

            # If this value changes from elsewhere, keep the widget in sync
            self.register_callback(
                lambda val: (
                    slider.setValue(val[0]),
                    value_label.setText(str(int(val[0]))),
                )
            )

            layout.addWidget(slider)
            layout.addWidget(value_label)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

    class RangeFloat(DatabaseElementTemplate):
        """
        Float range value

        Value composition:
            tuple<float, float, float> : (value, min, max)
        """

        # Decide how many decimals you want. For 2 decimals, factor=100
        factor = 100

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return f"{self.value[0]} ({self.value[1]}-{self.value[2]})"

        def __repr__(self):
            return f"Range Float: {self.name} - {self.value}"

        def _slider_to_float(self, slider_val: int) -> float:
            """Convert slider integer value back to a float."""
            return slider_val / self.factor

        def _float_to_slider(self, float_val: float) -> int:
            """Convert a float to the slider’s integer scale."""
            return int(float_val * self.factor)

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the range float."""
            widget = QWidget()
            layout = QHBoxLayout(widget)

            # Create a horizontal QSlider
            slider = QSlider(Qt.Orientation.Horizontal)
            # Scale the min, max, and current value
            slider.setRange(
                self._float_to_slider(self.value[1]),
                self._float_to_slider(self.value[2]),
            )
            slider.setValue(self._float_to_slider(self.value[0]))

            # Show optional ticks
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            # For a float range, pick a sensible tick interval
            slider.setTickInterval(
                self._float_to_slider((self.value[2] - self.value[1]) / 10.0) or 1
            )

            # Label to show current float value
            value_label = QLabel(f"{self.value[0]:.2f}")

            # Update DB and label on slider move
            slider.valueChanged.connect(
                lambda val_int: (
                    self.set_value(
                        (self._slider_to_float(val_int), self.value[1], self.value[2])
                    ),
                    value_label.setText(f"{self._slider_to_float(val_int):.2f}"),
                )
            )

            # Keep the slider/label in sync if the float is updated externally
            self.register_callback(
                lambda val: (
                    slider.setValue(self._float_to_slider(val[0])),
                    value_label.setText(f"{val[0]:.2f}"),
                )
            )

            layout.addWidget(slider)
            layout.addWidget(value_label)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

    class Text(DatabaseElementTemplate):
        """
        Text value

        Value composition:
            str : value
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return self.value

        def __repr__(self):
            return f"Text: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the text element."""
            widget = QWidget()
            layout = QHBoxLayout()
            text_entry = QLineEdit(self.value)
            text_entry.textChanged.connect(lambda text: self.set_value(text))
            self.register_callback(lambda text: text_entry.setText(text))
            layout.addWidget(text_entry)
            widget.setLayout(layout)
            return widget

    class Color(DatabaseElementTemplate):
        """
        Color value

        Value composition:
            tuple<int, int, int> : (r, g, b)
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return f"({self.value[0]}, {self.value[1]}, {self.value[2]})"

        def __repr__(self):
            return f"Color: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the color element."""
            widget = QWidget()
            layout = QHBoxLayout()
            color_button = QPushButton("Choose Color")
            color_button.setStyleSheet(
                f"background-color: rgb({self.value[0]}, {self.value[1]}, {self.value[2]});"  # Set initial color
            )
            color_button.clicked.connect(self.handle_color_dialog)
            self.register_callback(
                lambda color: color_button.setStyleSheet(
                    f"background-color: rgb({color[0]}, {color[1]}, {color[2]});"
                )
            )
            layout.addWidget(color_button)
            widget.setLayout(layout)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
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

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return str(self.value)

        def __repr__(self):
            return f"Boolean: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the boolean element."""
            widget = ...

            check_box = QCheckBox()
            check_box.setChecked(self.value)

            # Use toggled for a direct bool
            check_box.toggled.connect(lambda checked: self.set_value(checked))

            self.register_callback(lambda new_value: check_box.setChecked(new_value))

            widget = check_box
            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

    class List(DatabaseElementTemplate):
        """
        List of text values

        Value composition:
            list<str> : value
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return ", ".join(self.value)

        def __repr__(self):
            return f"List: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the list element."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            for i, text in enumerate(self.value):
                widget_row = QWidget()
                row_layout = QHBoxLayout(widget_row)
                spacer = QLabel()
                spacer.setFixedWidth(100)
                text_entry = QLineEdit(text)

                text_entry.textChanged.connect(
                    lambda new_text, idx=i: (
                        self.value.__setitem__(idx, new_text),
                        self.set_value(self.value),
                    )
                )

                self.register_callback(
                    lambda new_list, idx=i, txt_entry=text_entry: txt_entry.setText(
                        new_list[idx]
                    )
                )

                row_layout.setContentsMargins(0, 0, 0, 0)

                row_layout.addWidget(spacer)
                row_layout.addWidget(text_entry)
                layout.addWidget(widget_row)

            layout.addStretch()
            widget.setLayout(layout)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

    class Dictionary(DatabaseElementTemplate):
        """
        Dictionary of text values

        Value composition:
            dict<str, str> : value
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return ", ".join([f"{key}: {val}" for key, val in self.value.items()])

        def __repr__(self):
            return f"Dictionary: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the dictionary element."""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            for key, value in self.value.items():
                widget_row = QWidget()
                row_layout = QHBoxLayout(widget_row)
                key_entry = QLabel(key)
                key_entry.setFixedWidth(100)
                val_entry = QLineEdit(value)

                val_entry.textChanged.connect(
                    lambda new_text, k=key: (
                        self.value.__setitem__(k, new_text),
                        self.set_value(self.value),
                    )
                )

                self.register_callback(
                    lambda new_dict, k=key, val_entry=val_entry: (
                        val_entry.setText(new_dict[k])
                    )
                )

                row_layout.setContentsMargins(0, 0, 0, 0)

                row_layout.addWidget(key_entry)
                row_layout.addWidget(val_entry)
                layout.addWidget(widget_row)

            layout.addStretch()
            widget.setLayout(layout)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

    class File(DatabaseElementTemplate):
        """
        File value

        Value composition:
            pathlib.Path : value
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return str(self.value)

        def __repr__(self):
            return f"File: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the file element."""
            widget = QWidget()
            layout = QHBoxLayout()
            file_entry = QLineEdit(str(self.value))
            file_entry.setReadOnly(True)
            file_button = QPushButton("Choose File")
            file_button.clicked.connect(self.handle_file_dialog)
            self.register_callback(lambda value: file_entry.setText(str(value)))
            layout.addWidget(file_entry)
            layout.addWidget(file_button)
            widget.setLayout(layout)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

        def handle_file_dialog(self):
            file_path, _ = QFileDialog.getOpenFileName(
                None, "Open File", str(self.value), "All Files (*)"
            )
            if file_path:
                self.set_value(pathlib.Path(file_path))

    class Folder(DatabaseElementTemplate):
        """
        Folder value

        Value composition:
            pathlib.Path : value
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return str(self.value)

        def __repr__(self):
            return f"Folder: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the folder element."""
            widget = QWidget()
            layout = QHBoxLayout()
            folder_entry = QLineEdit(str(self.value))
            folder_entry.setReadOnly(True)
            folder_button = QPushButton("Choose Folder")
            folder_button.clicked.connect(self.handle_folder_dialog)
            self.register_callback(lambda value: folder_entry.setText(str(value)))
            layout.addWidget(folder_entry)
            layout.addWidget(folder_button)
            widget.setLayout(layout)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

        def handle_folder_dialog(self):
            folder_path = QFileDialog.getExistingDirectory(
                None, "Open Folder", str(self.value)
            )
            if folder_path:
                self.set_value(pathlib.Path(folder_path))

    class ChoiceBox(DatabaseElementTemplate):
        """
        Choice box value

        Value composition:
            tuple<int, list<str>> : (index, choices)
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return self.value[1][self.value[0]]

        def __repr__(self):
            return f"ChoiceBox: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the choice box element."""
            widget = QWidget()
            layout = QHBoxLayout()
            choice_box = QComboBox()
            choice_box.addItems(self.value[1])
            choice_box.setCurrentIndex(self.value[0])
            choice_box.currentIndexChanged.connect(
                lambda index: self.set_value((index, self.value[1]))
            )

            def choice_box_callback(index):
                choice_box.clear()
                choice_box.addItems(index[1])
                choice_box.setCurrentIndex(index[0])

            self.register_callback(choice_box_callback)
            layout.addWidget(choice_box)
            widget.setLayout(layout)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget

    class ConstantText(DatabaseElementTemplate):
        """
        Constant text value

        Value composition:
            str : value
        """

        def __init__(self, name: str, value, description: str = ""):
            super().__init__(name, value, description)

        def __str__(self):
            return self.value

        def __repr__(self):
            return f"ConstantText: {self.name} - {self.value}"

        def gen_widget_element(self) -> QWidget:
            """Generate a widget for the constant text element."""
            widget = QWidget()
            layout = QHBoxLayout()
            text_label = QLabel(self.value)
            self.register_callback(
                lambda value: text_label.setText(value)
            )  # Update the label
            layout.addWidget(text_label)
            widget.setLayout(layout)

            widget.setContentsMargins(0, 0, 0, 0)
            widget.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            return widget


# ------------------ Example Usage ------------------


def init_db(db: ContentDatabase):
    """
    Simple initialization function that creates a category
    and populates it with one SuffixFloat example item.
    """
    db.create_category("Audio Settings")
    db.add_item(
        "Audio Settings",
        "freq",
        db.SuffixFloat("Freq ", (1e3, "Hz"), "Frequency Control"),
    )
    db.add_item(
        "Audio Settings", "gain2", db.Integer("Gain2 ", 1000, "First Gain Control")
    )
    db.add_item(
        "Audio Settings",
        "gain3",
        db.RangeInt("Gain3 ", (1000, 0, 2000), "Second Gain Control"),
    )
    db.add_item(
        "Audio Settings",
        "gain4",
        db.RangeFloat("Gain4 ", (1000, 0, 2000), "Third Gain Control"),
    )
    db.add_item(
        "Audio Settings", "gain5", db.Text("Gain5 ", "1000", "Text Gain Control")
    )
    db.add_item(
        "Audio Settings", "gain6", db.Color("Gain6 ", (255, 0, 0), "Color Gain Control")
    )
    db.add_item(
        "Audio Settings", "gain7", db.Boolean("Gain7 ", True, "Boolean Gain Control")
    )
    db.add_item(
        "Audio Settings",
        "gain8",
        db.List("Gain8 ", ["1000", "2000", "3000"], "List Gain Control"),
    )
    db.add_item(
        "Audio Settings",
        "gain9",
        db.Dictionary(
            "Gain9 ", {"key1": "1000", "key2": "2000"}, "Dictionary Gain Control"
        ),
    )
    db.add_item(
        "Audio Settings",
        "gain10",
        db.File("Gain10", db.app_path / "example.txt", "File Gain Control"),
    )
    db.add_item(
        "Audio Settings",
        "gain11",
        db.Folder("Gain11", db.app_path, "Folder Gain Control"),
    )
    db.add_item(
        "Audio Settings",
        "gain12",
        db.ChoiceBox("Gain12", (0, ["1000", "2000", "3000"]), "ChoiceBox Gain Control"),
    )
    db.add_item(
        "Audio Settings",
        "gain13",
        db.ConstantText("Gain13", "1000", "ConstantText Gain Control"),
    )


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

        # Add a zone that multiplies the ints and floats
        label_function_random = QLabel("Multiplication of the 4 first values :")
        text_entry = QLineEdit("1.0")
        text_entry.setReadOnly(True)

        def text_entry_callback(value):
            suffix_float = db.get_item("Audio Settings", "freq").value[0]
            integer = db.get_item("Audio Settings", "gain2").value
            range_int = db.get_item("Audio Settings", "gain3").value[0]
            range_float = db.get_item("Audio Settings", "gain4").value[0]
            text_entry.setText(str(suffix_float * integer * range_int * range_float))

        # Register the callback to update the text entry at any change
        db.get_item("Audio Settings", "freq").register_callback(text_entry_callback)
        db.get_item("Audio Settings", "gain2").register_callback(text_entry_callback)
        db.get_item("Audio Settings", "gain3").register_callback(text_entry_callback)
        db.get_item("Audio Settings", "gain4").register_callback(text_entry_callback)

        scroll_layout.addWidget(label_function_random)
        scroll_layout.addWidget(text_entry)

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

    # Create a new main window next to it
    window2 = MainWindow(db)
    window2.resize(800, 600)
    window2.show()

    # Execute the app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
