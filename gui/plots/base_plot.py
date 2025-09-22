from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class BasePlotWidget(QWidget):
    """A base widget for a single Matplotlib plot."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
    def clear_plot(self, message="Not computed"):
        """Clears the plot and displays a message."""
        self.ax.clear()
        self.ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12, alpha=0.5)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()