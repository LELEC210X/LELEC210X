import sys
import time

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


class ImageAnimator2(QMainWindow):
    def __init__(self, N=10):
        super().__init__()
        self.N = N  # Number of images to display
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Animated 20x20 Images")
        self.setGeometry(100, 100, 1600, 600)  # Larger default window size

        # Main widget
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Set layout margins to zero
        layout.setSpacing(0)  # Set layout spacing to zero

        # FPS counter
        self.fps_counter = QLabel()
        layout.addWidget(self.fps_counter)
        self.current_time = time.time()
        self.fps_counter.setText("FPS: 0.00")
        self.fps_counter.setMaximumHeight(30)

        # Matplotlib Figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlim(-self.N * 1.1, 0.1)
        self.axes.set_ylim(-0.05, 1.05)
        self.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
        self.figure.tight_layout(pad=0.5)
        self.axes.set_xlabel("time")
        self.axes.set_ylabel("Mel frequency bin")

        self.data = np.random.rand(self.N, 20, 20)
        self.images = []
        for i in range(self.N):
            offset = -1.1
            X, Y = np.meshgrid(np.linspace(0, 1, 20), np.linspace(0, 1, 20))
            image = self.axes.pcolormesh(
                X + i * offset - 1.1,
                Y,
                self.data[i],
                vmin=0,
                vmax=1,
                cmap="viridis",
                shading="auto",  # Avoid gridlines
            )
            self.images.append(image)

        # Add a red square to the last image
        rectangle_dim = 1.05
        self.red_square = Rectangle(
            ((0 - 1) * 1.1 - (rectangle_dim - 1) / 2, -(rectangle_dim - 1) / 2),
            rectangle_dim,
            rectangle_dim,
            linewidth=1,
            edgecolor="red",
            facecolor="none",
        )
        self.axes.add_patch(self.red_square)

        self.ani = FuncAnimation(
            self.figure,
            self.update_plot,
            interval=10,
            blit=True,
            save_count=1,
            cache_frame_data=True,
        )

        self.show()

    def update_plot(self, frame: int):
        for i, image in enumerate(self.images):
            data = np.random.rand(20, 20)
            image.set_array(data.ravel())

        # FPS counter
        current_time = time.time()
        fps = 1 / (current_time - self.current_time)
        self.current_time = current_time
        self.fps_counter.setText(f"FPS: {fps:.2f}")

        return self.images + [self.red_square]


if __name__ == "__main__":
    app = QApplication(sys.argv)

    matplotlib.use("Qt5Agg")
    plt.style.use("fast")

    window = ImageAnimator2(N=10)  # Adjust N as needed
    sys.exit(app.exec())
