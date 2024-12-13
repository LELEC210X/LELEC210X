import sys
import random
import json
import plotly.graph_objects as go
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer

class DynamicPlotlyGraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Plotly Graph at 60Hz")

        # Create a WebEngineView to display the Plotly graph
        self.web_view = QWebEngineView()

        # Initialize the layout
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize data
        self.x_data = list(range(100))
        self.y_data = [random.uniform(0, 1) for _ in range(100)]

        # Create the initial graph
        self.init_graph()

        # Set up a timer for dynamic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000 // 60)  # 60 FPS

    def init_graph(self):
        # Create a basic Plotly figure
        self.fig = go.Figure()
        self.fig.add_scatter(x=self.x_data, y=self.y_data, mode='lines', name='Random Data')

        # Generate the initial HTML with a unique div id
        html = self.fig.to_html(full_html=True, include_plotlyjs='cdn', div_id='my-plot')

        # Set the HTML content
        self.web_view.setHtml(html)

    def update_graph(self):
        # Generate new random data for each update
        self.y_data = [random.uniform(0, 1) for _ in range(100)]

        # Prepare the data update in JavaScript format
        js_y_data = json.dumps([self.y_data])

        # JavaScript command to update the Plotly graph
        js_command = f"""
            var graphDiv = document.getElementById('my-plot');
            Plotly.restyle(graphDiv, {{'y': {js_y_data}}}, [0]);
        """

        # Execute the JavaScript command in the web view
        self.web_view.page().runJavaScript(js_command)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicPlotlyGraphApp()
    window.show()
    sys.exit(app.exec())