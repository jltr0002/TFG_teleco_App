"""
Detachable plot window for displaying matplotlib figures in separate windows.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from translations import translations


class DetachablePlotWindow(QMainWindow):
    """A detachable window that can display a matplotlib figure."""
    
    reattach_requested = Signal(str)  # Signal emitted when user wants to reattach
    window_closed = Signal(str)  # Signal emitted when window is closed
    
    def __init__(self, plot_id: str, title: str, figure: Figure = None, parent=None):
        super().__init__(parent)
        
        self.plot_id = plot_id
        self.original_parent = parent
        self.figure = figure
        self.canvas = None
        self.toolbar = None
        
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        
        self.setup_ui()
        self.setup_actions()
        
        if figure:
            self.set_figure(figure)
    
    def setup_ui(self):
        """Setup the UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar
        self.plot_toolbar = QToolBar()
        self.addToolBar(self.plot_toolbar)
        
    def setup_actions(self):
        """Setup toolbar actions."""
        # Reattach action
        self.reattach_action = QAction(translations.tr("reattach_plot"), self)
        self.reattach_action.setToolTip(translations.tr("reattach_plot_tooltip"))
        self.reattach_action.triggered.connect(self.request_reattach)
        self.plot_toolbar.addAction(self.reattach_action)
        
        self.plot_toolbar.addSeparator()
        
        # Close action
        self.close_action = QAction(translations.tr("close"), self)
        self.close_action.setToolTip(translations.tr("close_plot_window"))
        self.close_action.triggered.connect(self.close)
        self.plot_toolbar.addAction(self.close_action)
    
    def set_figure(self, figure: Figure):
        """Set the matplotlib figure to display."""
        # Remove existing canvas and toolbar if any
        if self.canvas:
            self.main_layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None
        if self.toolbar:
            self.main_layout.removeWidget(self.toolbar)
            self.toolbar.deleteLater()
            self.toolbar = None
        
        # Create new canvas and toolbar
        self.figure = figure
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Add to layout
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.canvas)
        
        # Refresh the canvas
        self.canvas.draw()
    
    def get_figure(self):
        """Get the current matplotlib figure."""
        return self.figure
    
    def request_reattach(self):
        """Request reattachment to the main window."""
        self.reattach_requested.emit(self.plot_id)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.window_closed.emit(self.plot_id)
        event.accept()
    
    def contextMenuEvent(self, event):
        """Handle right-click context menu."""
        context_menu = QMenu(self)
        
        context_menu.addAction(self.reattach_action)
        context_menu.addSeparator()
        context_menu.addAction(self.close_action)
        
        context_menu.exec(event.globalPos())


class PlotManager:
    """Manager for handling detached plots and their state."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.detached_plots = {}  # plot_id -> DetachablePlotWindow
        self.original_plots = {}  # plot_id -> original container info
        
    def detach_plot(self, plot_id: str, title: str, figure: Figure, original_container):
        """Detach a plot from the main window."""
        if plot_id in self.detached_plots:
            # Plot already detached, bring to front
            self.detached_plots[plot_id].raise_()
            self.detached_plots[plot_id].activateWindow()
            return
        
        # Store original container info
        self.original_plots[plot_id] = {
            'container': original_container,
            'figure': figure
        }
        
        # Create detached window with a new figure that shares the same content
        detached_window = DetachablePlotWindow(plot_id, title, None, self.main_window)
        
        # Copy the figure content to the detached window
        self._copy_figure_content(figure, detached_window)
        detached_window.reattach_requested.connect(self.reattach_plot)
        detached_window.window_closed.connect(self.on_plot_window_closed)
        
        self.detached_plots[plot_id] = detached_window
        
        # Simply hide the container when detached
        original_container.hide()
        
        # Show detached window
        detached_window.show()
    
    def reattach_plot(self, plot_id: str):
        """Reattach a plot to the main window."""
        if plot_id not in self.detached_plots:
            return
        
        detached_window = self.detached_plots[plot_id]
        original_info = self.original_plots[plot_id]
        
        # Get the original container
        original_container = original_info['container']
        
        # Show the original container again (it was just hidden, not modified)
        original_container.show()
        
        # Close detached window
        detached_window.close()
        
        # Clean up
        del self.detached_plots[plot_id]
        del self.original_plots[plot_id]
    
    def on_plot_window_closed(self, plot_id: str):
        """Handle when a detached plot window is closed."""
        if plot_id in self.detached_plots:
            # Reattach the plot before closing
            self.reattach_plot(plot_id)
    
    def reattach_all_plots(self):
        """Reattach all detached plots."""
        plot_ids = list(self.detached_plots.keys())
        for plot_id in plot_ids:
            self.reattach_plot(plot_id)
    
    def _update_plotting_widget_figure(self, plot_id: str, figure: Figure):
        """Update the plotting widget's figure references."""
        plotting_widget = self.main_window.plotting_widget
        
        if plot_id == 'array_factor':
            plotting_widget.af_figure = figure
        elif plot_id == 'polar':
            plotting_widget.polar_figure = figure
        elif plot_id == 'excitations':
            plotting_widget.excitations_figure = figure
        elif plot_id == 'elements':
            plotting_widget.elements_figure = figure
    
    def is_plot_detached(self, plot_id: str) -> bool:
        """Check if a plot is currently detached."""
        return plot_id in self.detached_plots
    
    def get_detached_plots(self):
        """Get list of currently detached plot IDs."""
        return list(self.detached_plots.keys())
    
    def _get_canvas_info(self, plot_id: str):
        """Get canvas information for a plot."""
        canvas_map = {
            'array_factor': self.main_window.af_canvas,
            'polar': self.main_window.polar_canvas,
            'excitations': self.main_window.excitations_canvas,
            'elements': self.main_window.elements_canvas
        }
        return canvas_map.get(plot_id)
    
    def _store_original_widgets(self, plot_id: str, container):
        """Store references to original widgets in the container."""
        widgets = []
        layout = container.layout()
        if layout:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget():
                    widgets.append(item.widget())
        return widgets
    
    def _recreate_original_structure(self, plot_id: str, container):
        """Recreate the original structure if widgets were lost."""
        layout = container.layout()
        if not layout:
            return
        
        main_window = self.main_window
        
        # Recreate the original toolbar and canvas structure
        if plot_id == 'array_factor':
            from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
            toolbar = NavigationToolbar(main_window.af_canvas, main_window)
            layout.addWidget(toolbar)
            layout.addWidget(main_window.af_canvas)
        elif plot_id == 'polar':
            from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
            toolbar = NavigationToolbar(main_window.polar_canvas, main_window)
            layout.addWidget(toolbar)
            layout.addWidget(main_window.polar_canvas)
        elif plot_id == 'excitations':
            from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
            toolbar = NavigationToolbar(main_window.excitations_canvas, main_window)
            layout.addWidget(toolbar)
            layout.addWidget(main_window.excitations_canvas)
        elif plot_id == 'elements':
            from PySide6.QtWidgets import QScrollArea
            scroll_area = QScrollArea()
            scroll_area.setWidget(main_window.elements_canvas)
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)
    
    def _copy_figure_content(self, source_figure: Figure, detached_window):
        """Copy the content from source figure to detached window."""
        import io
        
        try:
            # Save figure to bytes buffer
            buf = io.BytesIO()
            source_figure.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            # Create new figure and display the image
            figsize = source_figure.get_size_inches()
            new_figure = Figure(figsize=(float(figsize[0]), float(figsize[1])))
            ax = new_figure.add_subplot(111)
            
            # Load and display the image
            import matplotlib.image as mpimg
            img = mpimg.imread(buf, format='png')
            ax.imshow(img)
            ax.axis('off')  # Hide axes for clean display
            
            # Set the figure in the detached window
            detached_window.set_figure(new_figure)
            
        except Exception:
            # Fallback: create a simple text figure
            new_figure = Figure(figsize=(8, 6))
            ax = new_figure.add_subplot(111)
            ax.text(0.5, 0.5, f"📊 {detached_window.plot_id}\n(Plot snapshot)", 
                   ha='center', va='center', fontsize=14)
            ax.axis('off')
            detached_window.set_figure(new_figure)