"""
Written by Group E 2024-2025

This module contains a easy to use GUI to train machine learning models using scikit-learn, and test them on a dataset.
"""

####################################################################################################
# Standard library imports
from typing import Dict, Tuple, Type, List
import os, sys

# Third party imports
from sklearn.model_selection import train_test_split
import librosa
import numpy as np

# GUI imports
from PyQt6.QtWidgets import (
    # ===== LAYOUTS ===== (Used to organize widgets, not widgets themselves)
    QVBoxLayout,  # Vertical box layout
    QHBoxLayout,   # Horizontal box layout
    QGridLayout,   # Grid-based layout
    QFormLayout,   # Form layout (labels + inputs)
    
    # ===== WIDGETS ===== (Visible UI elements)
    # Core Application/Windows
    QApplication,  # Manages app flow (technically not a widget, but required)
    QWidget,       # Base container for all widgets
    QMainWindow,   # Main application window (with menu/status bars)
    QDialog,       # Dialog/popup window
    
    # Buttons
    QPushButton,   # Clickable button
    QCheckBox,     # Toggleable checkbox
    QRadioButton,  # Exclusive group selection
    
    # Inputs
    QLineEdit,     # Single-line text input
    QTextEdit,     # Rich text editor
    QComboBox,     # Dropdown list
    QSpinBox,      # Integer input spinner
    QDoubleSpinBox,# Float input spinner
    QSlider,       # Slider for values
    
    # Displays
    QLabel,        # Text/image label
    QProgressBar,  # Progress indicator
    QListWidget,   # Scrollable list of items
    QListWidgetItem,# Item for QListWidget
    QScrollArea,   # Scrollable container
    QSizePolicy,   # Size policy for layouts
    
    # Dialogs
    QFileDialog,   # File/folder selection dialog
    QMessageBox,   # Alert/confirmation dialog
    QInputDialog,  # Simple input dialog
    
    # Containers
    QTabWidget,    # Tabbed interface
    QGroupBox,     # Group with title border
    QStackedWidget,# Stack of widgets (only one visible)
    
    # Advanced
    QTableWidget,  # Table with rows/columns
    QTreeWidget,   # Hierarchical tree view
    QTreeWidgetItem,# Item for QTreeWidget
    QSplitter,     # Resizable frame splitter
    QDockWidget,   # Movable window pane
    QStatusBar,    # Status bar (in QMainWindow)
    QToolBar,      # Toolbar (in QMainWindow)
)

from PyQt6.QtCore import (
    Qt,           # Core Qt namespace (common enums)
    QThread,      # Worker thread for long tasks
    pyqtSignal,   # Signal for cross-thread communication
    QTimer,       # Timer for delays
    QEventLoop,   # Blocking loop for synchronous tasks
    QCoreApplication, # Core app instance (for event loop)
    QFileInfo,    # File information (path, size, etc)
    QDir,         # Directory handling
    QUrl,         # URL handling (file paths)
    QSettings,    # Persistent application settings
    QIODevice,    # Base class for I/O operations
    QFile,        # File I/O operations
    QDataStream,  # Binary stream I/O
    QByteArray,   # Raw byte array
    QBuffer,      # Memory buffer (for I/O)
    QMimeDatabase,# MIME type database
    QMimeData,    # MIME content container
    QProcess,     # External process handling
    QTemporaryFile,# Temporary file creation
    QTranslator,  # Internationalization (i18n)
    QLocale,      # Locale settings (language, etc)
    QLibraryInfo, # Qt library information
    QSysInfo,     # System information
)

from PyQt6.QtGui import (
    QColor,       # Color value (RGB/HSV)
    QIcon,        # Window icon/image
    QPixmap,      # Image/Pixmap object
    QFont,        # Font object (family/size/etc)
    QCursor,      # Mouse cursor icon
    QPalette,     # Collection of GUI colors
    QBrush,       # Paint style for elements
    QPen,         # Line style for drawing
)

####################################################################################################
# Model training imports

from sklearn.linear_model import (
    LogisticRegression, 
    SGDClassifier, 
    RidgeClassifier, 
    PassiveAggressiveClassifier,
    Perceptron
)
from sklearn.svm import SVC, NuSVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    AdaBoostClassifier,
    BaggingClassifier
)
from sklearn.naive_bayes import (
    GaussianNB, 
    BernoulliNB, 
    MultinomialNB, 
    ComplementNB
)
from sklearn.neighbors import (
    KNeighborsClassifier, 
    RadiusNeighborsClassifier, 
    NearestCentroid
)
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis, 
    QuadraticDiscriminantAnalysis
)
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.neural_network import MLPClassifier

####################################################################################################
# Models and constants

models_dict: Dict[str, Dict[str, Tuple[Type, str]]] = { # Generated by DeepSeek-R1:32B under the MIT liscence
    "Linear Models": {
        "Logistic Regression": (LogisticRegression, "Linear model for logistic regression classification"),
        "Stochastic Gradient Descent": (SGDClassifier, "Linear classifier with SGD training and regularization"),
        "Ridge Classifier": (RidgeClassifier, "Classifier using ridge regression with thresholding"),
        "Passive-Aggressive": (PassiveAggressiveClassifier, "Online learning algorithm for large-scale learning"),
        "Perceptron": (Perceptron, "Simple linear algorithm for binary classification")
    },
    
    "Support Vector Machines": {
        "Support Vector Machine (SVC)": (SVC, "C-support vector classification with kernel trick"),
        "Nu-Support Vector Machine": (NuSVC, "Nu-support vector classification with margin control"),
        "Linear Support Vector Machine": (LinearSVC, "Linear support vector classification optimized for speed")
    },
    
    "Tree-based Models": {
        "Decision Tree": (DecisionTreeClassifier, "Non-linear model using recursive partitioning"),
        "Random Forest": (RandomForestClassifier, "Ensemble of decorrelated decision trees with bagging"),
        "Extra Trees": (ExtraTreesClassifier, "Extremely randomized trees ensemble with reduced variance")
    },
    
    "Boosting Models": {
        "Gradient Boosting": (GradientBoostingClassifier, "Sequential ensemble with gradient descent optimization"),
        "Histogram Gradient Boosting": (HistGradientBoostingClassifier, "Efficient GB implementation using histograms"),
        "AdaBoost": (AdaBoostClassifier, "Adaptive boosting with emphasis on misclassified samples")
    },
    
    "Ensemble Methods": {
        "Bagging": (BaggingClassifier, "Meta-estimator for bagging-based ensemble learning")
    },
    
    "Naive Bayes Models": {
        "Gaussian Naive Bayes": (GaussianNB, "Gaussian likelihood with naive independence assumption"),
        "Bernoulli Naive Bayes": (BernoulliNB, "Bernoulli distribution for binary/boolean features"),
        "Multinomial Naive Bayes": (MultinomialNB, "Multinomial distribution for count-based features"),
        "Complement Naive Bayes": (ComplementNB, "Adaptation of MultinomialNB for imbalanced datasets")
    },
    
    "Nearest Neighbors": {
        "k-Nearest Neighbors": (KNeighborsClassifier, "Instance-based learning using k-nearest neighbors vote"),
        "Radius Neighbors": (RadiusNeighborsClassifier, "Neighbors within fixed radius for classification"),
        "Nearest Centroid": (NearestCentroid, "Simple classifier based on centroid distances")
    },
    
    "Discriminant Analysis": {
        "Linear Discriminant Analysis": (LinearDiscriminantAnalysis, "Linear decision boundaries from class statistics"),
        "Quadratic Discriminant Analysis": (QuadraticDiscriminantAnalysis, "Quadratic decision boundaries for classification")
    },
    
    "Neural Networks": {
        "Multilayer Perceptron": (MLPClassifier, "Feedforward artificial neural network classifier")
    },
    
    "Probabilistic Models": {
        "Gaussian Process": (GaussianProcessClassifier, "Probabilistic classifier based on Gaussian processes")
    }
}

# Classification classes for the dataset (Not are needed to be used, only those that are setup, will then be used and saved)
classification_classes = [
    "Unknown",
    "Birds",
    "Fire",
    "Chainsaw",
    "Handsaw",
    "Helicopter",
    "Human Voice",
    "Howling Leaves"
]

# Default model parameters for eacch model, if its not present, the default parameters will be used
model_params_per_path = {
    "Tree-based Models/Decision Tree": {
        "criterion": "gini",
        "splitter": "best",
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "min_weight_fraction_leaf": 0.0,
        "min_impurity_decrease": 0.0,
        "ccp_alpha": 0.0
    },
}

####################################################################################################
# Application logic

# Use process pools to parallelize training if needed (each job runs in a separate process)

class ModelTrainerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Model Trainer")
        self.resize(1200, 900)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

        # 3 colums: Model selection, dataset selection, and training options
        # 1 row bellow: Task management buttons
        # All widgets are resizable with the edges of the widget

        self.UI_UP()
        self.UI_DOWN()

    @classmethod
    def make_scroll_box(cls) -> Tuple[QScrollArea, QVBoxLayout]:
        """Create a scrollable box for widgets"""
        base_scroll = QScrollArea()
        base_scroll.setWidgetResizable(True)
        inner_widget = QWidget()
        inner_layout = QVBoxLayout(inner_widget)
        base_scroll.setWidget(inner_widget)
        return base_scroll, inner_layout

    def UI_UP(self):
        """Create the upper part of the window"""
        self.upper_widget = QWidget()
        self.upper_layout = QHBoxLayout(self.upper_widget)
        self.main_layout.addWidget(self.upper_widget)

        self.UI_UP_LEFT()
        #self.UI_UP_LEFT2()
        self.UI_UP_CENTER()
        self.UI_UP_RIGHT()

    def UI_UP_LEFT(self):
        # Model selection must have multiple selection buttons, and also, you need to be able to select multiple models, all models are toggle buttons
        self.model_selection_widget = QGroupBox("Model Selection")
        self.model_selection_layout = QVBoxLayout(self.model_selection_widget)
        self.upper_layout.addWidget(self.model_selection_widget)

        # Format Group box
        self.model_selection_widget.setMaximumWidth(300)

        # Selection utility
        self.model_select_all_button = QPushButton("Select All")
        self.model_deselect_all_button = QPushButton("Deselect All")
        self.model_single_select_checkbox = QCheckBox("Single Select")
        self.model_selection_layout.addWidget(self.model_select_all_button)
        self.model_selection_layout.addWidget(self.model_deselect_all_button)
        self.model_selection_layout.addWidget(self.model_single_select_checkbox)

        # Scroll area for model selection
        self.model_selection_scroll, self.model_selection_scroll_layout = self.make_scroll_box()
        self.model_selection_layout.addWidget(self.model_selection_scroll)

        # Model selection buttons
        self.model_selection_buttons = {}
        for model_type, model_dict in models_dict.items():
            model_group = QGroupBox(model_type)
            model_group_layout = QVBoxLayout(model_group)
            for model_name, (model_class, model_description) in model_dict.items():
                model_button = QCheckBox(model_name)
                model_button.setToolTip(model_description)
                model_group_layout.addWidget(model_button)
                self.model_selection_buttons[model_name] = model_button
            self.model_selection_scroll_layout.addWidget(model_group)

        # Utility connections
        def select_all_models():
            """Select all models"""
            for model_button in self.model_selection_buttons.values():
                model_button: QCheckBox
                model_button.setChecked(True)
        def deselect_all_models():
            """Deselect all models"""
            for model_button in self.model_selection_buttons.values():
                model_button: QCheckBox
                model_button.setChecked(False)
        self.model_select_all_button.clicked.connect(select_all_models)
        self.model_deselect_all_button.clicked.connect(deselect_all_models)
        def propagate_deselection():
            """Deselect all models except the one that was clicked if single select is enabled"""
            if self.model_single_select_checkbox.isChecked():
                for model_button in self.model_selection_buttons.values():
                    model_button: QCheckBox
                    if model_button is not self.sender():
                        model_button.setChecked(False)
        for model_button in self.model_selection_buttons.values():
            model_button: QCheckBox
            model_button.clicked.connect(propagate_deselection)

        # Set it to single select by default
        self.model_single_select_checkbox.setChecked(True)

        self.model_selection_scroll_layout.addStretch(999)

    def UI_UP_LEFT2(self):
        # Use of the tree widget to select the models, and also, you need to be able to select multiple models
        # You can resize the whole left side of the window to see the models better
        self.left_dock = QDockWidget("Model Selection")
        

        # Model selection buttons
        self.model_selection_buttons = {}

        # Test QTreeWidget
        tree = QTreeWidget()
        tree.setHeaderLabels(["Model", "Description"])
        self.model_selection_layout.addWidget(tree)
        for model_type, model_dict in models_dict.items():
            type_item = QTreeWidgetItem([model_type, ""])
            tree.addTopLevelItem(type_item)
            for model_name, (model_class, model_description) in model_dict.items():
                model_item = QTreeWidgetItem([model_name, model_description])
                type_item.addChild(model_item)
        tree.expandAll()

    def UI_UP_CENTER(self):
        # Dataset selection must have a file dialog to select a dataset file
        self.dataset_selection_widget = QGroupBox("Dataset Selection")
        self.dataset_selection_layout = QVBoxLayout(self.dataset_selection_widget)
        self.upper_layout.addWidget(self.dataset_selection_widget)

        # Dataset selection buttons
        self.dataset_select_button = QPushButton("Select Audio Files (.mp3, .wav)")
        self.dataset_selection_layout.addWidget(self.dataset_select_button)
        self.dataset_mel_button = QPushButton("Select MEL Files (.npy)")
        self.dataset_selection_layout.addWidget(self.dataset_mel_button)
        self.dataset_append_checkbox = QCheckBox("Append Files (instead of replacing)")
        self.dataset_selection_layout.addWidget(self.dataset_append_checkbox)

        # Assign Classes to the dataset selection
        # TODO: Add the classification assignments here, and tie it to the rest of the program
        self.dataset_selection_layout.addWidget(QLabel("Classification Assignments:"))
        self.selection_to_type = QComboBox()
        self.selection_to_type.addItems(classification_classes)
        self.dataset_selection_layout.addWidget(self.selection_to_type)
        self.selection_to_type_apply = QPushButton("Apply")
        self.dataset_selection_layout.addWidget(self.selection_to_type_apply)

        # Declare the audio and mel dataset lists
        self.audio_dataset_list: List[Tuple[str, str]] = [] # TODO : Change !!!
        self.mel_dataset_list: List[Tuple[str, str]] = []

        # Scroll area for the audio dataset selection, with alternating colors
        self.audio_group = QGroupBox("Audio Dataset")
        self.audio_group_layout = QVBoxLayout(self.audio_group)
        self.audio_list_widget = QListWidget()
        self.audio_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.audio_group_layout.addWidget(self.audio_list_widget)
        self.dataset_selection_layout.addWidget(self.audio_group)

        # Scroll area for the mel dataset selection, with alternating colors
        self.mel_group = QGroupBox("MEL Dataset")
        self.mel_group_layout = QVBoxLayout(self.mel_group)
        self.mel_list_widget = QListWidget()
        self.mel_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.mel_group_layout.addWidget(self.mel_list_widget)
        self.dataset_selection_layout.addWidget(self.mel_group)

        # Dataset selection connections
        def select_audio_files():
            """Add audio files to the dataset list"""
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Audio Files", "", "Audio Files (*.wav *.mp3)"
            )
            if files:
                if not self.dataset_append_checkbox.isChecked():
                    self.audio_dataset_list.clear()
                self.audio_dataset_list.extend((file, self.selection_to_type.currentText()) for file in files)
                self.update_dataset_list()
        def select_mel_files():
            """Add MEL files to the dataset list"""
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select MEL Files", "", "MEL Files (*.npy)"
            )
            if files:
                if not self.dataset_append_checkbox.isChecked():
                    self.mel_dataset_list.clear()
                self.mel_dataset_list.extend((file, self.selection_to_type.currentText()) for file in files)
                self.update_dataset_list()
        self.dataset_select_button.clicked.connect(select_audio_files)
        self.dataset_mel_button.clicked.connect(select_mel_files)
        self.dataset_append_checkbox.clicked.connect(self.update_dataset_list)

        # Classification assignment connections
        def apply_classification_assignment():
            """Apply the selected classification to the selected datasets"""
            selected_type = self.selection_to_type.currentText()
            for audio_item in self.audio_list_widget.selectedItems():
                self.audio_dataset_list[audio_item.row()] = (self.audio_dataset_list[audio_item.row()][0], selected_type)
            for mel_item in self.mel_list_widget.selectedItems():
                self.mel_dataset_list[mel_item.row()] = (self.mel_dataset_list[mel_item.row()][0], selected_type)
            self.update_dataset_list()
        self.selection_to_type_apply.clicked.connect(apply_classification_assignment)

        # Utility function to update the list
        self.update_dataset_list()

    def UI_UP_RIGHT(self):
        # Training options must have a button to start training
        self.training_options_widget = QGroupBox("Training Options")
        self.training_options_layout = QVBoxLayout(self.training_options_widget)
        self.upper_layout.addWidget(self.training_options_widget)
        self.training_options_widget.setFixedWidth(400)

        # Training options buttons
        self.train_button = QPushButton("Launch Training Tasks")
        self.train_button.setFixedHeight(100)
        self.training_options_layout.addWidget(self.train_button)

        def make_param(label_text, widget, row, col):
            """Make a parameter entry in the grid layout"""
            label = QLabel(label_text)
            label.setFixedHeight(10)
            self.training_options_grid.addWidget(label, row, col)
            self.training_options_grid.addWidget(widget, row, col + 1)

        # Training options subwidget
        self.training_options_subwidget = QGroupBox("Dataset Basic Preparation")
        self.training_options_grid = QGridLayout()
        self.training_options_subwidget.setLayout(self.training_options_grid)
        self.training_options_layout.addWidget(self.training_options_subwidget)

        self.test_split_mode = QComboBox()
        self.test_split_mode.addItems(["FUSE", "ONLY AUDIO", "ONLY MEL"])
        make_param("Dataset Split Mode:", self.test_split_mode, 0, 0)

        self.mel_size_param = QSpinBox()
        self.mel_size_param.setRange(1, 2000)
        self.mel_size_param.setValue(20)
        make_param("MEL Vector Size:", self.mel_size_param, 1, 0)
        
        self.mel_len_param = QSpinBox()
        self.mel_len_param.setRange(1, 2000)
        self.mel_len_param.setValue(20)
        make_param("MEL Vector Length:", self.mel_len_param, 2, 0)

        self.test_size_param = QDoubleSpinBox()
        self.test_size_param.setRange(0.0, 1.0)
        self.test_size_param.setValue(0.2)
        self.test_size_param.setSingleStep(0.01)
        make_param("Test Size:", self.test_size_param, 3, 0)

        self.random_state_param = QSpinBox()
        self.random_state_param.setRange(0, 1000)
        self.random_state_param.setValue(42)
        make_param("Random State:", self.random_state_param, 4, 0)

        # Audio Processing Parameters
        self.audio_processing_subwidget = QGroupBox("Audio Processing Parameters") # TODO: Add the audio processing parameters here
        self.audio_processing_grid = QGridLayout()
        self.audio_processing_subwidget.setLayout(self.audio_processing_grid)
        self.training_options_layout.addWidget(self.audio_processing_subwidget)

        # MEL Processing Parameters
        self.mel_processing_subwidget = QGroupBox("MEL Processing Parameters") # TODO: Add the MEL processing parameters here
        self.mel_processing_grid = QGridLayout()
        self.mel_processing_subwidget.setLayout(self.mel_processing_grid)
        self.training_options_layout.addWidget(self.mel_processing_subwidget)

        # Model Parameters
        self.model_parameter_subwidget = QGroupBox("Model Parameters")
        self.model_parameter_grid = QVBoxLayout()
        self.model_parameter_subwidget.setLayout(self.model_parameter_grid)
        self.training_options_layout.addWidget(self.model_parameter_subwidget)

        # List of groups with the model's parameters as a dictionary (Text entry)
        self.model_parameter_entries = {}
        def add_model_parameter(id, label_text):
            """Add a model parameter entry"""
            if not id in self.model_parameter_entries:
                self.model_parameter_entries[id] = (QGroupBox(label_text), QTextEdit())
                entry_layout = QVBoxLayout()
                self.model_parameter_entries[id][0].setLayout(entry_layout)
                self.model_parameter_grid.addWidget(self.model_parameter_entries[id][0])
                entry_layout.addWidget(self.model_parameter_entries[id][1])
                self.model_parameter_entries[id][1].setPlaceholderText("Enter model parameters here as a dict, that will be applied elliptically, example : \n{\n\t\"param1\": \"value1\",\n\t\"param2\": 123,\n\t\"param3\": True\n}")
        def remove_model_parameter(id):
            """Remove a model parameter entry"""
            if id in self.model_parameter_entries:
                group_box, LineEdit = self.model_parameter_entries[id]
                group_box.deleteLater()
                LineEdit.deleteLater()
                self.model_parameter_entries.pop(id)
        
        # Connect the model selection to the parameter selection
        def update_model_parameters():
            """Update the model parameters based on the selected models"""
            for model_name, model_button in self.model_selection_buttons.items():
                model_button: QCheckBox
                if model_button.isChecked():
                    add_model_parameter(model_name, model_name + " Parameters")
                else:
                    remove_model_parameter(model_name)
        for model_button in self.model_selection_buttons.values():
            model_button: QCheckBox
            model_button.clicked.connect(update_model_parameters)

        # Connect the training button to the training function
        self.train_button.clicked.connect(self.train_models)

        self.training_options_layout.addStretch(999)

    def UI_DOWN(self):
        """Create the lower part of the window"""
        self.lower_widget = QWidget()
        self.lower_layout = QHBoxLayout(self.lower_widget)
        self.main_layout.addWidget(self.lower_widget)

        # Task management must have a list of tasks and a button to cancel them
        self.task_management_widget = QGroupBox("Task Management")
        self.task_management_layout = QVBoxLayout(self.task_management_widget)
        self.lower_layout.addWidget(self.task_management_widget)

        # Add the task list
        self.task_list_widget = QListWidget()
        self.task_management_layout.addWidget(self.task_list_widget)

        # Demo for the loading bar
        # Add 5 items with progress bars
        for i in range(1, 6):
            # Create item container
            item_widget = QWidget()
            
            # Create components
            label = QLabel(f"Item {i}")
            progress = QProgressBar()
            progress.setValue(i * 20)  # 20%, 40%, etc.
            progress.setFixedHeight(20)
            progress.setMaximumWidth(200)
            
            # Setup layout
            layout = QHBoxLayout()
            layout.addWidget(label)
            layout.addWidget(progress)
            item_widget.setLayout(layout)
            
            # Add to list
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.task_list_widget.addItem(list_item)
            self.task_list_widget.setItemWidget(list_item, item_widget)

        # TODO: Add the task management buttons here

    def update_dataset_list(self):
        """Update the audio dataset list display"""
        if self.dataset_append_checkbox.isChecked():
            self.audio_list_widget.clear()
            self.mel_list_widget.clear()
        # Create custom item with a combo box for for the type
        for audio_file, audio_type in self.audio_dataset_list:
            pass
        
    def parse_model_parameters(self, text_dict_param: str) -> Dict:
        """
        Parse the model parameters from a text dictionary, it accepts the following format:
        {
            "param1": "value1",
            "param2": 123,
            "param3": True,
            "param4": None
        }
        """
        dict_param = {}
        for line in text_dict_param.split("\n"):
            if line:
                key, value = line.split(":")
                key = key.strip()
                value = value.strip()
                if value.isnumeric():
                    value = int(value)
                elif value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.lower() == "none":
                    value = None
                dict_param[key] = value
        return dict_param

    def train_models(self):
        """Train the selected models using the selected dataset"""
        # Get the selected models
        selected_models = []
        for model_name, model_button in self.model_selection_buttons.items():
            model_button: QCheckBox
            if model_button.isChecked():
                selected_models.append(model_name)
        
        # Get the selected datasets
        audio_datasets = [self.audio_dataset_list[i] for i in range(self.audio_list_widget.count())]
        mel_datasets = [self.mel_dataset_list[i] for i in range(self.mel_list_widget.count())]
        
        # Transform the audio datasets into MEL datasets
        audio_mel_datasets = [self.process_audio(audio_file) for audio_file in audio_datasets]
        mel_datasets       = [np.load(mel_file) for mel_file in mel_datasets]
        mel_vec_size = self.mel_size_param.value() # 20
        mel_vec_len = self.mel_len_param.value() # 20

        # Optionaly fuse the 2 datasets
        fuse_datasets = self.test_split_mode.currentText() # FUSE, ONLY AUDIO, ONLY MEL
        if "FUSE" in fuse_datasets:
            # Fuse the datasets
            fused_datasets = [np.concatenate((audio_mel_datasets[i], mel_datasets[i])) for i in range(len(audio_mel_datasets))]
        elif "ONLY AUDIO" in fuse_datasets:
            fused_datasets = audio_mel_datasets
        elif "ONLY MEL" in fuse_datasets:
            fused_datasets = mel_datasets

        # Transform the datasets a bit more (if needed)
        fuse_datasets = [self.process_mel(mel_data, mel_vec_size, mel_vec_len) for mel_data in fused_datasets]

        # Split the dataset into training and testing
        test_size = self.test_size_param.value() # 0.2
        random_state = self.random_state_param.value() # 42
        X, y = fused_datasets, [0] * len(fused_datasets)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

        # TODO: Add the model training here

    def process_audio(self, audio_file):
        """Process an audio file into a MEL spectrogram"""
        audio_data = librosa.load(audio_file)
        mel_data = librosa.feature.melspectrogram(audio_data[0], sr=audio_data[1])
        # TODO: Add signal processing here
        return mel_data
    
    def process_mel(self, mel_data, mel_vec_size, mel_vec_len):
        """Process a MEL spectrogram into a fixed-size vector"""
        # TODO: Add MELVEC processing here
        return mel_data

####################################################################################################
# Entry point

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModelTrainerApp()
    window.show()
    sys.exit(app.exec())