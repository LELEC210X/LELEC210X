import pickle
import sys

import librosa
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


class TaskThread(QThread):
    """Thread to handle background tasks."""

    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.task_func(
                *self.args, **self.kwargs, progress_callback=self.update_progress
            )
        except Exception as e:
            self.finished.emit(f"Error: {e}")
        else:
            self.finished.emit("Task completed")

    def update_progress(self, value):
        self.progress.emit(value)


class AudioProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio File Processor")
        self.resize(800, 600)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.layout = QVBoxLayout(self.central_widget)

        # File list
        self.file_list = QListWidget()
        self.layout.addWidget(QLabel("Selected Audio Files:"))
        self.layout.addWidget(self.file_list)

        # Buttons
        file_buttons_layout = QHBoxLayout()
        self.add_file_button = QPushButton("Add Files")
        self.add_file_button.clicked.connect(self.add_files)
        self.clear_files_button = QPushButton("Clear Files")
        self.clear_files_button.clicked.connect(self.clear_files)
        file_buttons_layout.addWidget(self.add_file_button)
        file_buttons_layout.addWidget(self.clear_files_button)
        self.layout.addLayout(file_buttons_layout)

        task_buttons_layout = QHBoxLayout()
        self.save_npy_button = QPushButton("Save as .NPY Task")
        self.save_npy_button.clicked.connect(self.save_npy_task)
        self.launch_training_button = QPushButton("Launch Training Task")
        self.launch_training_button.clicked.connect(self.launch_training_task)
        task_buttons_layout.addWidget(self.save_npy_button)
        task_buttons_layout.addWidget(self.launch_training_button)
        self.layout.addLayout(task_buttons_layout)

        # Scroll area for progress bars
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        # Temporary file list
        self.temp_file_list = []

        # Active threads
        self.active_threads = []

    def add_files(self):
        """Add files to the temporary list."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio Files", "", "Audio Files (*.wav *.mp3)"
        )
        if files:
            self.temp_file_list.extend(files)
            self.update_file_list()

    def clear_files(self):
        """Clear the temporary file list."""
        self.temp_file_list = []
        self.update_file_list()

    def update_file_list(self):
        """Update the GUI file list display."""
        self.file_list.clear()
        self.file_list.addItems(self.temp_file_list)

    def save_npy_task(self):
        """Save the preprocessing task to a .NPY file."""
        if not self.temp_file_list:
            QMessageBox.warning(self, "No Files", "Please add files before saving.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save .NPY File", "", "NumPy Files (*.npy)"
        )
        if not save_path:
            return

        progress_bar, task_label = self.create_task_ui(
            f"Saving {len(self.temp_file_list)} files to {save_path}"
        )
        thread = TaskThread(self.preprocess_audio, self.temp_file_list, save_path)
        self.setup_task_thread(thread, progress_bar, task_label)

    def launch_training_task(self):
        """Launch a training task."""
        if not self.temp_file_list:
            QMessageBox.warning(self, "No Files", "Please add files to preprocess.")
            return

        model_path, _ = QFileDialog.getSaveFileName(
            self, "Save Model", "", "Pickle Files (*.pckl)"
        )
        if not model_path:
            return

        progress_bar, task_label = self.create_task_ui(
            f"Training on {len(self.temp_file_list)} files"
        )
        thread = TaskThread(self.train_model, self.temp_file_list, model_path)
        self.setup_task_thread(thread, progress_bar, task_label)

    def create_task_ui(self, description):
        """Create UI elements for a task."""
        task_container = QWidget()
        task_layout = QVBoxLayout(task_container)
        task_label = QLabel(description)
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        task_layout.addWidget(task_label)
        task_layout.addWidget(progress_bar)
        self.scroll_layout.addWidget(task_container)
        return progress_bar, task_label

    def setup_task_thread(self, thread, progress_bar, task_label):
        """Set up signals for a task thread."""
        thread.progress.connect(progress_bar.setValue)
        thread.finished.connect(
            lambda msg: self.on_task_finished(msg, task_label, progress_bar)
        )
        self.active_threads.append(thread)
        thread.finished.connect(lambda: self.active_threads.remove(thread))
        thread.start()

    def on_task_finished(self, message, task_label, progress_bar):
        """Handle task completion."""
        task_label.setText(f"{task_label.text()} - {message}")
        progress_bar.setValue(100)

    def preprocess_audio(self, files, save_path, progress_callback):
        """Preprocess audio files into 20x20 mel spectrograms and save as .npy."""
        data = []
        for i, file in enumerate(files):
            y, sr = librosa.load(file, sr=None)
            mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=20)
            mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)
            if mel_spectrogram.shape[1] > 20:
                mel_spectrogram = mel_spectrogram[:, :20]
            elif mel_spectrogram.shape[1] < 20:
                mel_spectrogram = np.pad(
                    mel_spectrogram,
                    ((0, 0), (0, 20 - mel_spectrogram.shape[1])),
                    mode="constant",
                )
            data.append(mel_spectrogram)
            progress_callback(int((i + 1) / len(files) * 100))

        np.save(save_path, np.array(data))

    def train_model(self, files, model_path, progress_callback):
        """Train a logistic regression model on the preprocessed dataset."""
        data = []
        for i, file in enumerate(files):
            y, sr = librosa.load(file, sr=None)
            mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=20)
            mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)
            mel_spectrogram = (
                mel_spectrogram[:, :20]
                if mel_spectrogram.shape[1] >= 20
                else np.pad(
                    mel_spectrogram,
                    ((0, 0), (0, 20 - mel_spectrogram.shape[1])),
                    mode="constant",
                )
            )
            data.append(mel_spectrogram.flatten())
            progress_callback(int((i + 1) / len(files) * 50))

        labels = np.random.randint(0, 2, len(data))
        X_train, X_test, y_train, y_test = train_test_split(
            data, labels, test_size=0.2, random_state=42
        )
        model = LogisticRegression()
        model.fit(X_train, y_train)
        progress_callback(100)

        with open(model_path, "wb") as f:
            pickle.dump(model, f)


def main():
    app = QApplication(sys.argv)
    window = AudioProcessorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
