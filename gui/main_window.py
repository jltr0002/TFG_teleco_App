"""
Main window for the antenna synthesis GUI application.
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QSplitter, QTabWidget, QScrollArea, QGroupBox,
                              QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                              QComboBox, QTextEdit, QLineEdit, QFileDialog,
                              QFormLayout, QFrame, QMessageBox,
                              QCheckBox, QDialog, QDialogButtonBox,
                              QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
                              QMenu)
from PySide6.QtCore import Qt, QThread, QObject, Signal
from PySide6.QtGui import QFont
import numpy as np
from typing import Dict, Any, List
import json
import csv
import os
import re
from datetime import datetime

from methods import SchelkunoffMethod, FourierMethod, DolphChebyshevMethod
from .plotting_widget import PlottingWidget
from .detachable_plot_window import PlotManager
from translations import translations
from .preferences_dialog import PreferencesDialog
from config import ConfigManager, ConfigLimits


from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# from gui.plots.rectangular_plot import RectangularAFPlotWidget
# from gui.plots.polar_plot import PolarAFPlotWidget # (You would create this)
# from gui.plots.excitations_plot import ExcitationsPlotWidget # (You would create this)

class GlobalParametersDialog(QDialog):
    """Dialog for editing global parameters."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translations.tr("global_parameters_title"))
        self.setModal(True)
        # Remove fixed size to allow automatic resizing
        
        # Get current values from parent
        self.main_window = parent
        
        # Apply current font size from parent
        if parent and hasattr(parent, 'current_font_size'):
            font = self.font()
            font.setPointSize(parent.current_font_size)
            self.setFont(font)
        
        self.setup_ui()
        self.load_current_values()
        
        # Adjust size to content after UI is created
        self.adjustSize()
        self.setMinimumWidth(350)  # Set minimum width for usability
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Create form layout for parameters
        form_layout = QFormLayout()
        
        # Precision
        self.precision_spin = QSpinBox()
        self.precision_spin.setRange(ConfigLimits.PRECISION_MIN, ConfigLimits.PRECISION_MAX)
        form_layout.addRow(translations.tr("precision_decimals"), self.precision_spin)
        
        # Separator 1: After precision decimals
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addRow(separator1)
        
        # Input angle unit
        self.angle_input_combo = QComboBox()
        self.angle_input_combo.addItems([translations.tr("degrees"), translations.tr("radians")])
        form_layout.addRow(translations.tr("input_angle_unit"), self.angle_input_combo)
        
        # Separator 2: After input angle unit
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addRow(separator2)
        
        # Rectangular plot angle unit
        self.angle_rect_combo = QComboBox()
        self.angle_rect_combo.addItems([translations.tr("degrees"), translations.tr("radians")])
        form_layout.addRow(translations.tr("rectangular_plot_unit"), self.angle_rect_combo)
        
        # Polar plot angle unit
        self.angle_polar_combo = QComboBox()
        self.angle_polar_combo.addItems([translations.tr("degrees"), translations.tr("radians")])
        form_layout.addRow(translations.tr("polar_plot_unit"), self.angle_polar_combo)
        
        # Element phase unit
        self.element_phase_combo = QComboBox()
        self.element_phase_combo.addItems([translations.tr("degrees"), translations.tr("radians")])
        form_layout.addRow(translations.tr("element_phase_unit"), self.element_phase_combo)
        
        # Separator 3: After element phase unit
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addRow(separator3)
        
        # Rectangular plot scale
        self.rectangular_scale_combo = QComboBox()
        self.rectangular_scale_combo.addItems([translations.tr("db"), translations.tr("linear")])
        form_layout.addRow(translations.tr("rectangular_plot_scale"), self.rectangular_scale_combo)
        
        # Polar plot scale
        self.polar_scale_combo = QComboBox()
        self.polar_scale_combo.addItems([translations.tr("db"), translations.tr("linear")])
        form_layout.addRow(translations.tr("polar_plot_scale"), self.polar_scale_combo)
        
        # Separator 4: After polar plot scale
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.Shape.HLine)
        separator4.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addRow(separator4)
        
        # Resolution
        self.resolution_spin = QSpinBox()
        self.resolution_spin.setRange(ConfigLimits.RESOLUTION_MIN, ConfigLimits.RESOLUTION_MAX)
        form_layout.addRow(translations.tr("resolution"), self.resolution_spin)
        
        # Separator 5: After resolution
        separator5 = QFrame()
        separator5.setFrameShape(QFrame.Shape.HLine)
        separator5.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addRow(separator5)
        
        # Threshold
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(ConfigLimits.THRESHOLD_MIN, ConfigLimits.THRESHOLD_MAX)
        form_layout.addRow(translations.tr("threshold_db"), self.threshold_spin)
        
        # Array factor normalization
        self.normalize_checkbox = QCheckBox()
        form_layout.addRow(translations.tr("normalize_array_factor"), self.normalize_checkbox)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_current_values(self):
        """Load current values from main window, converting internal values to UI text."""
        if self.main_window:
            self.precision_spin.setValue(self.main_window.precision_decimals)
            self._set_angle_unit_combo(self.angle_input_combo, self.main_window.angle_unit_input)
            self._set_angle_unit_combo(self.angle_rect_combo, self.main_window.angle_unit_rectangular)
            self._set_angle_unit_combo(self.angle_polar_combo, self.main_window.angle_unit_polar)
            self._set_angle_unit_combo(self.element_phase_combo, self.main_window.element_phase_unit)
            self._set_scale_combo(self.rectangular_scale_combo, self.main_window.rectangular_scale)
            self._set_scale_combo(self.polar_scale_combo, self.main_window.polar_scale)
            self.resolution_spin.setValue(self.main_window.resolution)
            self.threshold_spin.setValue(self.main_window.threshold_db)
            self.normalize_checkbox.setChecked(self.main_window.normalize_array_factor)
    
    def _set_angle_unit_combo(self, combo_box, internal_value):
        """Set combo box to show translated text for internal English value."""
        if internal_value == "degrees":
            combo_box.setCurrentText(translations.tr("degrees"))
        elif internal_value == "radians":
            combo_box.setCurrentText(translations.tr("radians"))
        else:
            combo_box.setCurrentText(translations.tr("radians"))  # Default
    
    def _set_scale_combo(self, combo_box, internal_value):
        """Set combo box to show translated text for internal English value."""
        if internal_value == "dB":
            combo_box.setCurrentText(translations.tr("db"))
        elif internal_value == "linear":
            combo_box.setCurrentText(translations.tr("linear"))
        else:
            combo_box.setCurrentText(translations.tr("db"))  # Default
    
    def get_values(self):
        """Get the values from the dialog, converting UI text to internal English values."""
        return {
            'precision_decimals': self.precision_spin.value(),
            'angle_unit_input': self._get_angle_unit_value(self.angle_input_combo),
            'angle_unit_rectangular': self._get_angle_unit_value(self.angle_rect_combo),
            'angle_unit_polar': self._get_angle_unit_value(self.angle_polar_combo),
            'element_phase_unit': self._get_angle_unit_value(self.element_phase_combo),
            'rectangular_scale': self._get_scale_value(self.rectangular_scale_combo),
            'polar_scale': self._get_scale_value(self.polar_scale_combo),
            'resolution': self.resolution_spin.value(),
            'threshold_db': self.threshold_spin.value(),
            'normalize_array_factor': self.normalize_checkbox.isChecked()
        }
    
    def _get_angle_unit_value(self, combo_box):
        """Convert combo box text to internal English angle unit value."""
        current_text = combo_box.currentText()
        if current_text == translations.tr("degrees"):
            return "degrees"
        elif current_text == translations.tr("radians"):
            return "radians"
        else:
            return "radians"  # Default fallback
    
    def _get_scale_value(self, combo_box):
        """Convert combo box text to internal English scale value."""
        current_text = combo_box.currentText()
        if current_text == translations.tr("db"):
            return "dB"
        elif current_text == translations.tr("linear"):
            return "linear"
        else:
            return "dB"  # Default fallback

class ComputationWorker(QObject):
    """Worker thread for computation to avoid UI freezing."""
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, method, params):
        super().__init__()
        self.method = method
        self.params = params
    
    def run(self):
        try:
            result = self.method.compute(**self.params)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(translations.tr("main_window_title"))
        # Store initial geometry for reset functionality
        self.initial_geometry = (100, 100, 1400, 900)
        self.setGeometry(*self.initial_geometry)
        
        # Declare dynamic attributes for type checking
        self.inputs_form: QFormLayout
        self.inputs_group: QGroupBox
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Initialize methods
        self.methods = {
            'Schelkunoff': SchelkunoffMethod(),
            'Fourier': FourierMethod(),
            'DolphChebyshev': DolphChebyshevMethod()
        }
        
        # Load global parameters from configuration
        self.load_global_parameters()
        
        # Current results
        self.current_results = None
        
        # Store initial dock states for reset functionality
        self.initial_dock_states = {}
        
        # Initialize plot manager for detachable plots
        self.plot_manager = PlotManager(self)
        
        self.setup_ui()
        self.setup_menu()
        
        # Apply initial font size from config
        config = self.config_manager.load_config()
        initial_font_size = config.get('font_size', 12)
        self.current_font_size = initial_font_size
        self.update_font_size(initial_font_size)
        self.setup_docks()
        
        # Initialize with last used method or first method after everything is setup
        if hasattr(self, 'method_combo'):
            if self.last_method and self.last_method in self.methods:
                # Set the combo to the last used method by finding its index
                for i in range(self.method_combo.count()):
                    if self.method_combo.itemData(i) == self.last_method:
                        self.method_combo.setCurrentIndex(i)
                        break
                self.initial_method = self.last_method
            else:
                self.initial_method = self.method_combo.currentData()
            
            self.method_changed(self.initial_method)
            # Store initial input values after widgets are created
            if hasattr(self, 'input_widgets'):
                self.initial_input_values = self.get_input_values(validate_expressions=False)
    
    def load_global_parameters(self):
        """Load global parameters from configuration file."""
        config = self.config_manager.load_config()
        
        self.precision_decimals = config['precision_decimals']
        self.angle_unit_input = config['angle_unit_input']
        self.angle_unit_rectangular = config['angle_unit_rectangular']
        self.angle_unit_polar = config['angle_unit_polar']
        self.element_phase_unit = config['element_phase_unit']
        self.rectangular_scale = config['rectangular_scale']
        self.polar_scale = config['polar_scale']
        self.resolution = config['resolution']
        self.threshold_db = config['threshold_db']
        self.normalize_array_factor = config['normalize_array_factor']
        
        # Initialize method state for current session only (don't load from previous sessions)
        self.last_method = None
        self.last_method_inputs = {}
        # Store method inputs for current session only
        self.session_method_inputs = {}
    
    def save_global_parameters(self):
        """Save current global parameters to configuration file."""
        config = {
            'precision_decimals': self.precision_decimals,
            'angle_unit_input': self.angle_unit_input,
            'angle_unit_rectangular': self.angle_unit_rectangular,
            'angle_unit_polar': self.angle_unit_polar,
            'element_phase_unit': self.element_phase_unit,
            'rectangular_scale': self.rectangular_scale,
            'polar_scale': self.polar_scale,
            'resolution': self.resolution,
            'threshold_db': self.threshold_db,
            'normalize_array_factor': self.normalize_array_factor
        }
        
        self.config_manager.save_config(config)
    
    def resizeEvent(self, event):
        """Handle window resize events to update label wrapping."""
        super().resizeEvent(event)
        # Recreate widgets with new wrapping when window is resized significantly
        old_width = event.oldSize().width() if event.oldSize().isValid() else 0
        new_width = event.size().width()
        
        # Only refresh if width change is significant (more than 100 pixels)
        if abs(new_width - old_width) > 100 and hasattr(self, 'method_combo'):
            current_method_key = self.method_combo.currentData()
            if current_method_key in self.methods:
                # Store current input values before recreating widgets
                current_values = {}
                if hasattr(self, 'input_widgets'):
                    current_values = self.get_input_values(validate_expressions=False)
                
                # Recreate widgets with new adaptive wrapping
                self.method_changed(current_method_key)
                
                # Restore input values
                if current_values:
                    self.set_input_values(current_values)
    
    def set_input_values(self, values: Dict[str, Any]):
        """Set values in input widgets."""
        for name, value in values.items():
            if name in self.input_widgets:
                widget = self.input_widgets[name]
                if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                    widget.setValue(value)
                elif isinstance(widget, QComboBox):
                    index = widget.findText(str(value))
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif isinstance(widget, QLineEdit):
                    if isinstance(value, list):
                        widget.setText(", ".join(map(str, value)))
                    else:
                        widget.setText(str(value))
    
    def parse_pi_expression(self, expression: str) -> float:
        """Parse expressions like 'pi/2', '3*pi/4', 'pi', etc."""
        if not isinstance(expression, str):
            return float(expression)
        
        expression = expression.strip().lower()
        
        # Handle simple numbers
        try:
            return float(expression)
        except ValueError:
            pass
        
        # Replace 'pi' with np.pi for evaluation
        expression = expression.replace('pi', str(np.pi))
        
        # Simple validation - only allow numbers, operators, parentheses, and pi
        if re.match(r'^[0-9+\-*/().\s' + str(np.pi).replace('.', r'\.') + r']+$', expression):
            try:
                return float(eval(expression))
            except:
                raise ValueError(f"Invalid expression: {expression}")
        else:
            raise ValueError(f"Invalid characters in expression: {expression}")
    
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # Edit menu
        edit_menu = menubar.addMenu(translations.tr('edit'))
        
        # Global parameters action
        global_params_action = edit_menu.addAction(translations.tr('global_parameters'))
        global_params_action.triggered.connect(self.show_global_parameters_dialog)
        
        # Preferences action
        preferences_action = edit_menu.addAction(translations.tr('preferences'))
        preferences_action.triggered.connect(self.show_preferences_dialog)
        
        # Export menu
        export_menu = menubar.addMenu(translations.tr('export'))
        
        # Export plots submenu
        plots_menu = export_menu.addMenu(translations.tr('export_plots'))
        
        # PNG export
        png_action = plots_menu.addAction(translations.tr('export_as_png'))
        png_action.triggered.connect(lambda: self.export_plots_dialog('png'))
        
        # SVG export
        svg_action = plots_menu.addAction(translations.tr('export_as_svg'))
        svg_action.triggered.connect(lambda: self.export_plots_dialog('svg'))
        
        # Export data
        export_menu.addSeparator()
        
        # JSON export
        json_action = export_menu.addAction(translations.tr('export_data_json'))
        json_action.triggered.connect(self.export_json_dialog)
        
        # CSV export
        csv_action = export_menu.addAction(translations.tr('export_array_factor_csv'))
        csv_action.triggered.connect(self.export_csv_dialog)
        
        # View menu
        view_menu = menubar.addMenu(translations.tr('view'))
        
        # Appearance submenu
        appearance_menu = view_menu.addMenu(translations.tr('appearance'))
        
        # Reset view action
        reset_view_action = appearance_menu.addAction(translations.tr('reset_view'))
        reset_view_action.triggered.connect(self.reset_view)
        
        # Plots submenu
        plots_view_menu = view_menu.addMenu(translations.tr('plots'))
        
        # Reattach all plots action
        reattach_all_action = plots_view_menu.addAction(translations.tr('reattach_all_plots'))
        reattach_all_action.triggered.connect(self.reattach_all_plots)
        
        # Store menu references for language updates
        self.edit_menu = edit_menu
        self.export_menu = export_menu
        self.view_menu = view_menu
        self.plots_menu = plots_menu
        self.plots_view_menu = plots_view_menu
        self.appearance_menu = appearance_menu
        
        # Store action references
        self.global_params_action = global_params_action
        self.preferences_action = preferences_action
        self.png_action = png_action
        self.svg_action = svg_action
        self.json_action = json_action
        self.csv_action = csv_action
        self.reset_view_action = reset_view_action
        self.reattach_all_action = reattach_all_action
    
    def show_global_parameters_dialog(self):
        """Show the global parameters dialog."""
        dialog = GlobalParametersDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update parameters with new values
            values = dialog.get_values()
            self.update_global_parameters(values)
    
    def show_preferences_dialog(self):
        """Show the preferences dialog."""
        dialog = PreferencesDialog(self)
        # Connect signals
        dialog.language_changed.connect(self.update_language)
        dialog.font_size_changed.connect(self.update_font_size)
        dialog.exec()
    
    def update_font_size(self, font_size: int):
        """Update font size for all UI elements."""
        # Store current font size for persistence
        self.current_font_size = font_size
        
        # Create font object
        font = self.font()
        font.setPointSize(font_size)
        
        # Apply to all UI elements
        self.update_all_widgets_font(font)
        
        # Update menu bar font
        if hasattr(self, 'menuBar'):
            self.menuBar().setFont(font)
            for menu in self.menuBar().findChildren(QWidget):
                menu.setFont(font)
    
    def update_all_widgets_font(self, font):
        """Apply font to all widget types."""
        # Input widgets
        widget_types = [QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, 
                       QTextEdit, QLabel, QPushButton, QCheckBox]
        
        for widget_type in widget_types:
            for widget in self.findChildren(widget_type):
                widget.setFont(font)
        
        # Apply to group boxes and their titles
        for groupbox in self.findChildren(QGroupBox):
            groupbox.setFont(font)
        
        # Apply to tab widgets
        for tabwidget in self.findChildren(QTabWidget):
            tabwidget.setFont(font)
        
        # Apply to table widgets (for coefficients table)
        for table in self.findChildren(QTableWidget):
            table.setFont(font)
            # Also update header fonts
            if table.horizontalHeader():
                table.horizontalHeader().setFont(font)
            if table.verticalHeader():
                table.verticalHeader().setFont(font)
    
    def update_menu_language(self):
        """Update menu language without recreating them."""
        if hasattr(self, 'edit_menu'):
            self.edit_menu.setTitle(translations.tr('edit'))
        if hasattr(self, 'export_menu'):
            self.export_menu.setTitle(translations.tr('export'))
        if hasattr(self, 'view_menu'):
            self.view_menu.setTitle(translations.tr('view'))
        if hasattr(self, 'plots_menu'):
            self.plots_menu.setTitle(translations.tr('export_plots'))
        if hasattr(self, 'appearance_menu'):
            self.appearance_menu.setTitle(translations.tr('appearance'))
        
        # Update action texts
        if hasattr(self, 'global_params_action'):
            self.global_params_action.setText(translations.tr('global_parameters'))
        if hasattr(self, 'preferences_action'):
            self.preferences_action.setText(translations.tr('preferences'))
        if hasattr(self, 'png_action'):
            self.png_action.setText(translations.tr('export_as_png'))
        if hasattr(self, 'svg_action'):
            self.svg_action.setText(translations.tr('export_as_svg'))
        if hasattr(self, 'json_action'):
            self.json_action.setText(translations.tr('export_data_json'))
        if hasattr(self, 'csv_action'):
            self.csv_action.setText(translations.tr('export_array_factor_csv'))
        if hasattr(self, 'reset_view_action'):
            self.reset_view_action.setText(translations.tr('reset_view'))
        if hasattr(self, 'plots_view_menu'):
            self.plots_view_menu.setTitle(translations.tr('plots'))
        if hasattr(self, 'reattach_all_action'):
            self.reattach_all_action.setText(translations.tr('reattach_all_plots'))
    
    def update_global_parameters(self, values: Dict[str, Any]):
        """
        Update global parameters from dialog values.
        If the input angle unit changes, reset the method inputs to their defaults.
        """
        # 1. Detect if the input angle unit has changed
        old_angle_unit = self.angle_unit_input
        new_angle_unit = values['angle_unit_input']
        angle_unit_changed = (old_angle_unit != new_angle_unit)

        # Update all global parameter attributes
        self.precision_decimals = values['precision_decimals']
        self.angle_unit_input = values['angle_unit_input']
        self.angle_unit_rectangular = values['angle_unit_rectangular']
        self.angle_unit_polar = values['angle_unit_polar']
        self.element_phase_unit = values['element_phase_unit']
        self.rectangular_scale = values['rectangular_scale']
        self.polar_scale = values['polar_scale']
        self.resolution = values['resolution']
        self.threshold_db = values['threshold_db']
        self.normalize_array_factor = values['normalize_array_factor']

        # Save the updated parameters to configuration file
        self.save_global_parameters()

        # Clear plots and results since parameters changed
        if hasattr(self, 'plotting_widget'):
            self.plotting_widget.clear_plots()
        if hasattr(self, 'coefficients_table'):
            self.clear_coefficients_table()
        self.current_results = None

        # Get the current method key to refresh its view
        current_method_key = self.method_combo.currentData()
        if not current_method_key:
            return
        
        # Decide whether to restore or not, based on whether the unit changed.
        # If the unit changed, we DON'T restore (pass False).
        # If the unit did NOT change, we DO restore (pass True).
        should_restore = not angle_unit_changed
        self.method_changed(current_method_key, restore_session_state=should_restore)
    
    def update_language(self, _language_code: str):
        """Update the UI language."""
        # Update window title
        self.setWindowTitle(translations.tr("main_window_title"))
        
        # Update menu bar
        self.update_menu_language()
        
        # Update method selection group and combo
        if hasattr(self, 'method_combo'):
            # Store current selection
            current_index = self.method_combo.currentIndex()
            current_method = None
            if current_index >= 0:
                current_method = self.method_combo.itemData(current_index)
            
            # Update method selection group title
            if hasattr(self, 'method_group'):
                self.method_group.setTitle(translations.tr("method_selection"))
            
            # Update method combo box items
            self.method_combo.clear()
            for method_key, method_instance in self.methods.items():
                method_name = method_instance.name  # Use the actual name property
                self.method_combo.addItem(method_name, method_key)
            
            # Restore selection
            if current_index >= 0:
                self.method_combo.setCurrentIndex(current_index)
            
            # Update compute button
            if hasattr(self, 'compute_button'):
                self.compute_button.setText(translations.tr("compute"))
            
            # Update tab widget
            if hasattr(self, 'tab_widget'):
                self.tab_widget.setTabText(0, translations.tr("array_factor"))
                self.tab_widget.setTabText(1, translations.tr("array_elements"))
            
            # Refresh current method to update input/output labels
            if current_method:
                # Store current input values before refreshing widgets
                current_values = {}
                if hasattr(self, 'input_widgets'):
                    current_values = self.get_input_values()
                
                self.method_changed(current_method)
                
                # Restore input values after widgets are recreated
                if current_values:
                    self.set_input_values(current_values)
        
        # Update plots if there are current results
        if self.current_results and hasattr(self, 'plotting_widget'):
            # 1. Create the dictionary of global parameters for plotting.
            plotting_params = self._get_plotting_parameters()
            
            # 2. Call update_plots with the new, correct signature.
            self.plotting_widget.update_plots(self.current_results, plotting_params)
        
    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main vertical layout to include separator
        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.setSpacing(0)
        
        # Add separator line after menu bar
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_vertical_layout.addWidget(separator)
        
        # Content widget for the main interface
        content_widget = QWidget()
        main_vertical_layout.addWidget(content_widget)
        
        # Main layout for content
        main_layout = QHBoxLayout(content_widget)
        
        # Create splitter for left and right panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel (controls)
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel (plots)
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (reduced left panel size)
        splitter.setSizes([400, 1000])
        
    def create_left_panel(self) -> QWidget:
        """Create the left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Method selection
        self.method_group = QGroupBox(translations.tr("method_selection"))
        method_layout = QVBoxLayout(self.method_group)
        
        self.method_combo = QComboBox()
        # Add method names using their name property
        for method_key, method_instance in self.methods.items():
            method_name = method_instance.name  # Use the actual name property
            self.method_combo.addItem(method_name, method_key)  # Store original key as data
        self.method_combo.currentIndexChanged.connect(self.method_changed_by_index)
        method_layout.addWidget(self.method_combo)
        
        layout.addWidget(self.method_group)
        
        # Create a vertical splitter for the inputs and outputs sections
        control_splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(control_splitter)
        
        # Inputs section
        inputs_scroll = QScrollArea()
        inputs_scroll.setWidgetResizable(True)
        # Set the size policy to allow vertical and horizontal expansion
        inputs_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.inputs_widget = QWidget()
        self.inputs_layout = QVBoxLayout(self.inputs_widget)
        inputs_scroll.setWidget(self.inputs_widget)
        control_splitter.addWidget(inputs_scroll)
        
        # Outputs section
        outputs_scroll = QScrollArea()
        outputs_scroll.setWidgetResizable(True)
        # Set the size policy to allow vertical and horizontal expansion
        outputs_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.outputs_widget = QWidget()
        self.outputs_layout = QVBoxLayout(self.outputs_widget)
        outputs_scroll.setWidget(self.outputs_widget)
        control_splitter.addWidget(outputs_scroll)
        
        # Set initial splitter proportions for inputs/outputs
        control_splitter.setSizes([300, 300])
        
        # Compute button
        self.compute_button = QPushButton(translations.tr("compute"))
        self.compute_button.clicked.connect(self.compute_synthesis)
        self.compute_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        layout.addWidget(self.compute_button)
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        """Create the right panel with tabbed interface."""
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_array_factor_tab()
        self.create_array_elements_tab()
        self.create_excitation_coefficients_tab()
        
        return self.tab_widget
    
    def create_array_factor_tab(self):
        """Create Array Factor tab with independently resizable rectangular and polar plots."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Create figures for this tab
        self.af_figure = Figure(figsize=(10, 4))
        self.af_canvas = FigureCanvas(self.af_figure)
        # Create navigation toolbar for rectangular plot
        af_toolbar = NavigationToolbar(self.af_canvas, self)
        
        self.polar_figure = Figure(figsize=(8, 6))
        self.polar_canvas = FigureCanvas(self.polar_figure)
        # Create navigation toolbar for polar plot
        polar_toolbar = NavigationToolbar(self.polar_canvas, self)
        
        # Create container widgets for plot management
        self.af_container = QWidget()
        af_container_layout = QVBoxLayout(self.af_container)
        af_container_layout.setContentsMargins(0, 0, 0, 0)
        af_container_layout.addWidget(af_toolbar)
        af_container_layout.addWidget(self.af_canvas)
        
        self.polar_container = QWidget()
        polar_container_layout = QVBoxLayout(self.polar_container)
        polar_container_layout.setContentsMargins(0, 0, 0, 0)
        polar_container_layout.addWidget(polar_toolbar)
        polar_container_layout.addWidget(self.polar_canvas)
        
        # Add context menus for detaching
        self.af_canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.af_canvas.customContextMenuRequested.connect(
            lambda pos: self.show_plot_context_menu(pos, 'array_factor', self.af_canvas)
        )
        
        self.polar_canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.polar_canvas.customContextMenuRequested.connect(
            lambda pos: self.show_plot_context_menu(pos, 'polar', self.polar_canvas)
        )
        
        # Create splitter for independent resizing of plots
        af_splitter = QSplitter(Qt.Orientation.Vertical)
        af_splitter.addWidget(self.af_container)
        af_splitter.addWidget(self.polar_container)
        
        # Set initial proportions (equal sizes)
        af_splitter.setSizes([500, 500])
        
        # Allow users to resize each plot independently
        af_splitter.setChildrenCollapsible(False)  # Prevent plots from being collapsed completely
        
        layout.addWidget(af_splitter)
        
        # Add tab
        self.tab_widget.addTab(tab_widget, translations.tr("array_factor"))
    
    def create_array_elements_tab(self):
        """Create Array Elements tab with independently resizable excitations plot and elements plot."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Excitations plot
        self.excitations_figure = Figure(figsize=(8, 4))
        self.excitations_canvas = FigureCanvas(self.excitations_figure)
        # Create navigation toolbar for excitations plot
        excitations_toolbar = NavigationToolbar(self.excitations_canvas, self)
        
        # Create container for excitations plot
        self.excitations_container = QWidget()
        excitations_container_layout = QVBoxLayout(self.excitations_container)
        excitations_container_layout.setContentsMargins(0, 0, 0, 0)
        excitations_container_layout.addWidget(excitations_toolbar)
        excitations_container_layout.addWidget(self.excitations_canvas)
        
        # Elements plot
        self.elements_figure = Figure(figsize=(12, 6))
        self.elements_canvas = FigureCanvas(self.elements_figure)
        self.elements_canvas.setMinimumHeight(300)
        
        # Create container for elements plot
        self.elements_container = QWidget()
        elements_container_layout = QVBoxLayout(self.elements_container)
        elements_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add scroll area for the elements plot
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.elements_canvas)
        scroll_area.setWidgetResizable(True)
        elements_container_layout.addWidget(scroll_area)
        
        # Add context menus for detaching
        self.excitations_canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.excitations_canvas.customContextMenuRequested.connect(
            lambda pos: self.show_plot_context_menu(pos, 'excitations', self.excitations_canvas)
        )
        
        self.elements_canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.elements_canvas.customContextMenuRequested.connect(
            lambda pos: self.show_plot_context_menu(pos, 'elements', self.elements_canvas)
        )
        
        # Create splitter for independent resizing of plots
        elements_splitter = QSplitter(Qt.Orientation.Vertical)
        elements_splitter.addWidget(self.excitations_container)
        elements_splitter.addWidget(self.elements_container)
        
        # Set initial proportions (equal sizes)
        elements_splitter.setSizes([400, 400])
        
        # Allow users to resize each plot independently
        elements_splitter.setChildrenCollapsible(False)  # Prevent plots from being collapsed completely
        
        layout.addWidget(elements_splitter)
        
        # Add tab
        self.tab_widget.addTab(tab_widget, translations.tr("array_elements"))
    
    
    def create_excitation_coefficients_tab(self):
        """Create Excitation Coefficients tab with table display."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Create table widget for coefficients
        self.coefficients_table = QTableWidget()
        self.coefficients_table.setColumnCount(6)  # Index, Magnitude, Phase(°), Phase(rad), Real, Imaginary
        
        # Apply current font size if available
        if hasattr(self, 'current_font_size'):
            font = self.font()
            font.setPointSize(self.current_font_size)
            self.coefficients_table.setFont(font)
            if self.coefficients_table.horizontalHeader():
                self.coefficients_table.horizontalHeader().setFont(font)
            if self.coefficients_table.verticalHeader():
                self.coefficients_table.verticalHeader().setFont(font)
        
        # Set column headers
        headers = [
            translations.tr("coefficient_index"),
            translations.tr("coefficient_magnitude"), 
            translations.tr("coefficient_phase") + " (°)",
            translations.tr("coefficient_phase") + " (rad)",
            translations.tr("coefficient_real"),
            translations.tr("coefficient_imaginary")
        ]
        self.coefficients_table.setHorizontalHeaderLabels(headers)
        
        # Configure table appearance
        self.coefficients_table.setAlternatingRowColors(True)
        self.coefficients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.coefficients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Initially show "not computed" message
        self.coefficients_table.setRowCount(1)
        not_computed_item = QTableWidgetItem(translations.tr("not_computed_yet"))
        not_computed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.coefficients_table.setItem(0, 0, not_computed_item)
        self.coefficients_table.setSpan(0, 0, 1, 6)  # Span across all columns
        
        layout.addWidget(self.coefficients_table)
        
        # Add tab
        self.tab_widget.addTab(tab_widget, translations.tr("excitation_coefficients"))
    
    def setup_docks(self):
        """Setup plotting widget to use the tab figures."""
        # Create PlottingWidget instance to use its plotting methods
        self.plotting_widget = PlottingWidget()
        
        # Replace the plotting widget's figures with our tab figures
        self.plotting_widget.af_figure = self.af_figure
        self.plotting_widget.af_canvas = self.af_canvas
        self.plotting_widget.polar_figure = self.polar_figure
        self.plotting_widget.polar_canvas = self.polar_canvas
        self.plotting_widget.excitations_figure = self.excitations_figure
        self.plotting_widget.excitations_canvas = self.excitations_canvas
        self.plotting_widget.elements_figure = self.elements_figure
        self.plotting_widget.elements_canvas = self.elements_canvas
    
    def show_plot_context_menu(self, position, plot_id: str, canvas):
        """Show context menu for plot canvas."""
        context_menu = QMenu(self)
        
        if self.plot_manager.is_plot_detached(plot_id):
            # Plot is detached, show reattach option
            reattach_action = context_menu.addAction(translations.tr("reattach_plot"))
            reattach_action.triggered.connect(lambda: self.plot_manager.reattach_plot(plot_id))
        else:
            # Plot is attached, show detach option
            detach_action = context_menu.addAction(translations.tr("detach_plot"))
            detach_action.triggered.connect(lambda: self.detach_plot(plot_id))
        
        # Convert canvas position to global position
        global_pos = canvas.mapToGlobal(position)
        context_menu.exec(global_pos)
    
    def detach_plot(self, plot_id: str):
        """Detach a plot from the main window."""
        plot_info = self.get_plot_info(plot_id)
        if plot_info:
            self.plot_manager.detach_plot(
                plot_id, 
                plot_info['title'], 
                plot_info['figure'], 
                plot_info['container']
            )
    
    def get_plot_info(self, plot_id: str):
        """Get plot information for detachment."""
        plot_info_map = {
            'array_factor': {
                'title': translations.tr("array_factor_rectangular"),
                'figure': self.af_figure,
                'container': self.af_container
            },
            'polar': {
                'title': translations.tr("array_factor_polar"),
                'figure': self.polar_figure,
                'container': self.polar_container
            },
            'excitations': {
                'title': translations.tr("element_excitations"),
                'figure': self.excitations_figure,
                'container': self.excitations_container
            },
            'elements': {
                'title': translations.tr("array_elements"),
                'figure': self.elements_figure,
                'container': self.elements_container
            }
        }
        return plot_info_map.get(plot_id)
    
    def reattach_all_plots(self):
        """Reattach all detached plots."""
        self.plot_manager.reattach_all_plots()

    def reset_view(self):
        """Reset the view to original state."""
        # Reattach all plots first
        self.reattach_all_plots()
        
        # Reset window geometry to initial size
        if hasattr(self, 'initial_geometry'):
            self.setGeometry(*self.initial_geometry)
        
        # Reset to initial method
        if hasattr(self, 'initial_method') and hasattr(self, 'method_combo'):
            # Find the index for the initial method
            for i in range(self.method_combo.count()):
                if self.method_combo.itemData(i) == self.initial_method:
                    self.method_combo.setCurrentIndex(i)
                    break
            self.method_changed(self.initial_method)
            
            # Reset input values to initial defaults
            if hasattr(self, 'initial_input_values'):
                self.set_input_values(self.initial_input_values)
        
        # Reset tab widget to first tab
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setCurrentIndex(0)
            
        # Clear any computed results
        self.current_results = None
        
        # Clear output widgets
        for output_widget in self.output_widgets.values():
            output_widget.setPlainText(translations.tr("not_computed_yet"))
        
    def method_changed_by_index(self, index: int):
        """Handle method selection change by index."""
        if index >= 0:
            method_key = self.method_combo.itemData(index)
            if method_key:
                # Here the default value restore_session_state=True will be used,
                # which is the desired behavior.
                self.method_changed(method_key)
    
    def method_changed(self, method_key: str, restore_session_state: bool = True):
        """Handle method selection change."""
        self.clear_inputs()
        self.clear_outputs()
        
        # Clear plotting widgets when switching methods
        if hasattr(self, 'plotting_widget'):
            self.plotting_widget.clear_plots()
        
        # Clear coefficients table when switching methods
        if hasattr(self, 'coefficients_table'):
            self.clear_coefficients_table()
        
        if method_key in self.methods:
            method = self.methods[method_key]
            self.create_input_widgets(method)
            self.create_output_widgets(method)
                        
            # Only restore state if the caller requests it
            if restore_session_state:
                saved_inputs = self.session_method_inputs.get(method_key, {})
                if saved_inputs and hasattr(self, 'input_widgets'):
                    self.set_input_values(saved_inputs)
            
            # Reapply current font size to new widgets
            if hasattr(self, 'current_font_size'):
                font = self.font()
                font.setPointSize(self.current_font_size)
                self.update_all_widgets_font(font)
            
            # Clear any results (elements plot will be cleared by plotting_widget.clear_plots())
            self.current_results = None
            
            # Save current method state in session memory only (preserve text as user wrote it)
            # This is important so the session is saved after resetting
            if hasattr(self, 'method_combo'):
                current_method_key = self.method_combo.currentData()
                current_inputs = self.get_input_values(validate_expressions=False) if hasattr(self, 'input_widgets') else {}
                self.save_method_session_state(current_method_key, current_inputs)
            
    def clear_inputs(self):
        """Clear input widgets."""
        for i in reversed(range(self.inputs_layout.count())):
            self.inputs_layout.itemAt(i).widget().setParent(None)
        self.input_widgets = {}
        
    def clear_outputs(self):
        """Clear output widgets."""
        for i in reversed(range(self.outputs_layout.count())):
            self.outputs_layout.itemAt(i).widget().setParent(None)
        self.output_widgets = {}
    
    def clear_coefficients_table(self):
        """Clear coefficients table and show 'not computed' message."""
        # Clear content without clearing headers
        self.coefficients_table.setRowCount(0)
        self.coefficients_table.setRowCount(1)
        self.coefficients_table.setColumnCount(6)
        
        # Reset headers
        headers = [
            translations.tr("coefficient_index"),
            translations.tr("coefficient_magnitude"), 
            translations.tr("coefficient_phase") + " (°)",
            translations.tr("coefficient_phase") + " (rad)",
            translations.tr("coefficient_real"),
            translations.tr("coefficient_imaginary")
        ]
        self.coefficients_table.setHorizontalHeaderLabels(headers)
        
        # Show "not computed" message
        not_computed_item = QTableWidgetItem(translations.tr("not_computed_yet"))
        not_computed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.coefficients_table.setItem(0, 0, not_computed_item)
        self.coefficients_table.setSpan(0, 0, 1, 6)
    
    def _generate_coefficient_indices(self, n_elements: int, layout_type: str) -> List[int]:
        """Generate coefficient indices based on layout type and number of elements."""
        match layout_type:
            case "symmetric":
                half = n_elements // 2
                if n_elements % 2 == 0:
                    # Even: [-N/2, ..., -1, 1, ..., N/2]
                    return list(range(-half, 0)) + list(range(1, half + 1))
                else:
                    # Odd: [-(N-1)/2, ..., -1, 0, 1, ..., (N-1)/2]
                    half = (n_elements - 1) // 2
                    return list(range(-half, half + 1))
            case "unilateral" | _:
                # Default: [0, 1, ..., N-1]
                return list(range(n_elements))
    
    def update_coefficients_table(self, results: Dict[str, Any]):
        """Update coefficients table with computation results."""
        if 'element_excitations' not in results:
            return
        
        excitations = results['element_excitations']
        if excitations is None or len(excitations) == 0:
            return
        
        # Get method layout type to determine indexing
        current_method_key = self.method_combo.currentData()
        if current_method_key in self.methods:
            method = self.methods[current_method_key]
            layout_type = method.layout_type
        else:
            layout_type = "unilateral"  # Default
        
        # Get phase unit from global parameters
        # Note: Using self.element_phase_unit for phase formatting
        # phase_unit = self.element_phase_unit  # Not used in current implementation
        
        n_elements = len(excitations)
        
        # Generate coefficient indices based on layout type
        coefficient_indices = self._generate_coefficient_indices(n_elements, layout_type)
        
        # Clear existing content and set up table
        self.coefficients_table.setRowCount(0)  # Clear rows first
        self.coefficients_table.setRowCount(n_elements)
        self.coefficients_table.setColumnCount(6)
        
        # Reset headers
        headers = [
            translations.tr("coefficient_index"),
            translations.tr("coefficient_magnitude"), 
            translations.tr("coefficient_phase") + " (°)",
            translations.tr("coefficient_phase") + " (rad)",
            translations.tr("coefficient_real"),
            translations.tr("coefficient_imaginary")
        ]
        self.coefficients_table.setHorizontalHeaderLabels(headers)
        
        # Populate table
        for i, (index, excitation) in enumerate(zip(coefficient_indices, excitations)):
            # Index with Unicode subscript formatting
            def format_subscript(number):
                """Convert number to Unicode subscript characters."""
                subscript_map = {
                    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
                    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
                    '-': '₋'
                }
                return ''.join(subscript_map.get(char, char) for char in str(number))
            
            index_text = f"a{format_subscript(index)}"
            index_item = QTableWidgetItem(index_text)
            index_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Use a font that supports mathematical notation well
            font = QFont()
            font.setFamily("Times New Roman")
            font.setPointSize(14)
            index_item.setFont(font)
            
            self.coefficients_table.setItem(i, 0, index_item)
            
            # Helper function to format values with "-" for rounded zeros
            def format_value(value):
                formatted = f"{value:.{self.precision_decimals}f}"
                # Check if the formatted value is effectively zero (all zeros after decimal point)
                if float(formatted) == 0.0:
                    return "-"
                return formatted
            
            # Magnitude
            magnitude = abs(excitation)
            mag_text = format_value(magnitude)
            mag_item = QTableWidgetItem(mag_text)
            mag_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.coefficients_table.setItem(i, 1, mag_item)
            
            # Phase in degrees
            phase_deg = np.angle(excitation, deg=True)
            phase_deg_text = format_value(phase_deg)
            phase_deg_item = QTableWidgetItem(phase_deg_text)
            phase_deg_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.coefficients_table.setItem(i, 2, phase_deg_item)
            
            # Phase in radians
            phase_rad = np.angle(excitation, deg=False)
            phase_rad_text = format_value(phase_rad)
            phase_rad_item = QTableWidgetItem(phase_rad_text)
            phase_rad_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.coefficients_table.setItem(i, 3, phase_rad_item)
            
            # Real part
            real_part = excitation.real
            real_text = format_value(real_part)
            real_item = QTableWidgetItem(real_text)
            real_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.coefficients_table.setItem(i, 4, real_item)
            
            # Imaginary part
            imag_part = excitation.imag
            imag_text = format_value(imag_part)
            imag_item = QTableWidgetItem(imag_text)
            imag_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.coefficients_table.setItem(i, 5, imag_item)
        
    def _wrap_label_text(self, text: str, max_length: int = 30) -> str:
        """Wrap long label text into multiple lines."""
        if len(text) <= max_length:
            return text
            
        # Find good break points (spaces, commas, parentheses)
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_length:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
            
        return "\n".join(lines)
    
    def _get_adaptive_max_length(self) -> int:
        """Get adaptive max length based on window width."""
        window_width = self.width()
        if window_width > 1200:
            return 50  # Wide window, longer lines
        elif window_width > 800:
            return 35  # Medium window
        else:
            return 25  # Narrow window, shorter lines

    def create_input_widgets(self, method):
        """Create input widgets for the selected method using translation keys."""
        self.input_widgets = {}
        
        # Create a GroupBox with the method name and the translated word for "Inputs"
        inputs_group = QGroupBox(f"{method.name} - {translations.tr('inputs')}")
        inputs_form = QFormLayout(inputs_group)
        
        # Configure form layout to prevent overlapping
        inputs_form.setVerticalSpacing(10)  # Add vertical spacing between rows
        inputs_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)  # Align form to top
        inputs_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # Align labels to top
        inputs_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)  # Allow fields to grow
        inputs_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)  # Don't wrap rows

        # Get current input angle unit
        angle_unit_str = f"({self.angle_unit_input})"
        
        # First, add base input widgets
        for input_def in method.get_inputs(self.angle_unit_input):
            widget = self.create_input_widget(input_def)
            if widget:
                self.input_widgets[input_def['name']] = widget
                
                # Use the key to get the translated label
                label_text = translations.tr(input_def['label_key'])

                if 'angle' in input_def['name'].lower() or 'null' in input_def['name'].lower():
                    label_text += f" {angle_unit_str}"                
                
                # Create label with proper sizing
                label_widget = QLabel(label_text)
                label_widget.setWordWrap(True)  # Enable word wrapping
                label_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # Align to top
                label_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)  # Allow expansion
                label_widget.setMinimumWidth(150)  # Set minimum width to prevent text cutting
                label_widget.setMinimumHeight(25)  # Set minimum height to match widgets
                
                # Use the key for the help text (tooltip)
                if 'help_key' in input_def:
                    help_text = translations.tr(input_def['help_key'])
                    label_widget.setToolTip(help_text)
                    widget.setToolTip(help_text)
                
                inputs_form.addRow(label_widget, widget)
                
                # Connect widget signals to save state when values change
                self.connect_input_widget_signals(widget)
                
                # Special handling for number_of_beams to trigger dynamic inputs
                if input_def['name'] == 'number_of_beams' and isinstance(widget, QComboBox):
                    widget.currentTextChanged.connect(lambda text, m=method: self.update_dynamic_inputs(m))
        
        # Store reference to the form and group for dynamic updates
        self.inputs_form = inputs_form
        self.inputs_group = inputs_group
        
        # Add dynamic inputs if method supports them
        if hasattr(method, 'get_dynamic_inputs'):
            self.update_dynamic_inputs(method)
                
        self.inputs_layout.addWidget(inputs_group)
    
    def update_dynamic_inputs(self, method) -> None:
        """Update dynamic input widgets based on current values."""
        if not hasattr(method, 'get_dynamic_inputs'):
            return
        if not hasattr(self, 'inputs_form') or not hasattr(self, 'input_widgets'):
            return
        
        # Get current values for dynamic input generation
        current_values = self.get_input_values(validate_expressions=False)
        
        # Remove existing dynamic inputs
        dynamic_widgets_to_remove = []
        for name, widget in self.input_widgets.items():
            if name.startswith('beam_angles_'):
                dynamic_widgets_to_remove.append(name)
        
        # Remove dynamic widgets from form and dictionary
        for name in dynamic_widgets_to_remove:
            widget = self.input_widgets[name]
            # Find and remove the row from the form layout
            for i in range(self.inputs_form.rowCount()):
                label_item = self.inputs_form.itemAt(i, QFormLayout.ItemRole.LabelRole)
                field_item = self.inputs_form.itemAt(i, QFormLayout.ItemRole.FieldRole)
                if field_item and field_item.widget() == widget:
                    # Remove both label and field
                    if label_item:
                        label_widget = label_item.widget()
                        if label_widget:
                            label_widget.setParent(None)
                    field_widget = field_item.widget()
                    if field_widget:
                        field_widget.setParent(None)
                    break
            del self.input_widgets[name]
        
        # Get dynamic inputs and add them
        dynamic_inputs = method.get_dynamic_inputs(current_values)
        angle_unit_str = f"({self.angle_unit_input})"
        
        for input_def in dynamic_inputs:
            widget = self.create_input_widget(input_def)
            if widget:
                self.input_widgets[input_def['name']] = widget
                
                # Use the key to get the translated label
                label_text = translations.tr(input_def['label_key'])
                if 'angle' in input_def['name'].lower():
                    label_text += f" {angle_unit_str}"
                
                # Create label with proper sizing
                label_widget = QLabel(label_text)
                label_widget.setWordWrap(True)
                label_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)  # Align to top
                label_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)  # Allow expansion
                label_widget.setMinimumWidth(150)  # Set minimum width to prevent text cutting
                label_widget.setMinimumHeight(25)  # Set minimum height to match widgets
                
                # Use the key for the help text (tooltip)
                if 'help_key' in input_def:
                    help_text = translations.tr(input_def['help_key'])
                    label_widget.setToolTip(help_text)
                    widget.setToolTip(help_text)
                
                self.inputs_form.addRow(label_widget, widget)
                
                # Connect widget signals to save state when values change
                self.connect_input_widget_signals(widget)
        
    def create_input_widget(self, input_def: Dict[str, Any]) -> QWidget:
        """Create a single input widget based on definition."""
        widget_type = input_def['type']
        
        if widget_type == 'float':
            widget = QDoubleSpinBox()
            min_val = input_def.get('min', -1000) # Store the minimum
            widget.setRange(min_val, input_def.get('max', 1000))
            # Use minimum as fallback for default
            default_val = input_def.get('default', min_val) 
            widget.setValue(default_val)
            widget.setSingleStep(input_def.get('step', 0.1))
            widget.setDecimals(input_def.get('decimals', 2))
            widget.setMinimumHeight(25)
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            return widget
            
        elif widget_type == 'int':
            widget = QSpinBox()
            min_val = input_def.get('min', -1000) # Store the minimum
            widget.setRange(min_val, input_def.get('max', 1000))
            # Use minimum as fallback for default
            default_val = input_def.get('default', min_val) 
            widget.setValue(default_val)
            widget.setSingleStep(input_def.get('step', 1))
            widget.setMinimumHeight(25)
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            return widget
            
        elif widget_type == 'choice':
            widget = QComboBox()
            widget.addItems(input_def.get('choices', []))
            if 'default' in input_def:
                widget.setCurrentText(str(input_def['default']))
            widget.setMinimumHeight(25)  # Set consistent height
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            return widget
            
        elif widget_type == 'list_float':
            widget = QLineEdit()
            default_list = input_def.get('default', [])
            widget.setText(', '.join(map(str, default_list)))
            widget.setMinimumHeight(25)  # Set consistent height
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            return widget
        
        elif widget_type == 'text':
            widget = QLineEdit()
            widget.setText(input_def.get('default', '')) # Use default as string
            widget.setMinimumHeight(25)  # Set consistent height
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            return widget
            
        # Return a default widget if no matching type
        widget = QLineEdit()
        widget.setMinimumHeight(25)  # Set consistent height
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return widget
    
    def connect_input_widget_signals(self, widget: QWidget):
        """Connect signals from input widgets to save method state when values change."""
        if isinstance(widget, QDoubleSpinBox):
            widget.valueChanged.connect(self.on_input_value_changed)
        elif isinstance(widget, QSpinBox):
            widget.valueChanged.connect(self.on_input_value_changed)
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(self.on_input_value_changed)
        elif isinstance(widget, QLineEdit):
            widget.textChanged.connect(self.on_input_value_changed)
    
    def save_method_session_state(self, method_key: str, inputs: dict):
        """Save method state in session memory only (not persistent)."""
        if method_key and inputs:
            self.session_method_inputs[method_key] = inputs.copy()
    
    def on_input_value_changed(self):
        """Handle input value changes to save method state."""
        if hasattr(self, 'method_combo') and hasattr(self, 'input_widgets'):
            current_method_key = self.method_combo.currentData()
            current_inputs = self.get_input_values(validate_expressions=False)  # Don't validate when just saving state
            self.save_method_session_state(current_method_key, current_inputs)
                   
    def create_output_widgets(self, method):
        """Create output widgets for the selected method using translation keys."""
        self.output_widgets = {}
        
        # Create a GroupBox with the method name and the translated word for "Outputs"
        outputs_group = QGroupBox(f"{method.name} - {translations.tr('outputs')}")
        outputs_form = QFormLayout(outputs_group)
        
        outputs_info = method.get_outputs()
        for output_info in outputs_info:
            # Use dictionary format only
            output_key = output_info['key']
            help_key = output_info.get('help_key')
            
            # Use the key to get the translated label
            label_text = translations.tr(output_key)
            
            # Wrap long labels with adaptive length
            max_len = self._get_adaptive_max_length()
            wrapped_text = self._wrap_label_text(label_text, max_len)
            label_widget = QLabel(f"<b>{wrapped_text}:</b>")
            label_widget.setWordWrap(True)  # Enable word wrapping
            
            # Add tooltip if help_key is provided
            help_text = None
            if help_key:
                help_text = translations.tr(help_key)
                label_widget.setToolTip(help_text)
            
            # Create the text widget for the output value
            text_widget = QTextEdit()
            text_widget.setMaximumHeight(60)
            text_widget.setReadOnly(True)
            text_widget.setPlainText(translations.tr("not_computed_yet"))
            
            # Add tooltip to the text widget as well
            if help_text:
                text_widget.setToolTip(help_text)
            
            # Use the key to store the widget
            self.output_widgets[output_key] = text_widget
            outputs_form.addRow(label_widget, text_widget)
            
        self.outputs_layout.addWidget(outputs_group)
        
    def get_input_values(self, validate_expressions: bool = True) -> Dict[str, Any]:
        """Get values from input widgets.
        
        Args:
            validate_expressions: If True, validate pi expressions (for computation).
                                If False, skip validation (for saving state).
        """
        values = {}
        
        for name, widget in self.input_widgets.items():
            if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                values[name] = widget.value()
            elif isinstance(widget, QComboBox):
                values[name] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if name == 'null_angles':  # Special handling for list inputs
                    if validate_expressions:
                        try:
                            if self.angle_unit_input == "radians":
                                values[name] = [self.parse_pi_expression(x.strip()) for x in text.split(',') if x.strip()]
                            else:
                                values[name] = [float(x.strip()) for x in text.split(',') if x.strip()]
                        except Exception as e:
                            QMessageBox.warning(self, "Input Error", f"Error parsing nulls: {str(e)}")
                            values[name] = []
                    else:
                        # For saving state, just store the raw text without validation
                        values[name] = text
                elif name == 'theta0_angle':  # Special handling for theta0_angle with pi expressions
                    if validate_expressions:
                        try:
                            if self.angle_unit_input == "radians":
                                values[name] = self.parse_pi_expression(text.strip())
                            else:
                                values[name] = float(text.strip())
                        except Exception as e:
                            QMessageBox.warning(self, "Input Error", f"Error parsing main beam angle: {str(e)}")
                            values[name] = 90.0  # Default fallback
                    else:
                        # For saving state, just store the raw text without validation
                        values[name] = text
                elif name.startswith('beam_angles_'):  # Special handling for beam angle pairs with pi expressions
                    if validate_expressions:
                        try:
                            if self.angle_unit_input == "radians":
                                # Parse comma-separated pi expressions
                                angles = [self.parse_pi_expression(x.strip()) for x in text.split(',') if x.strip()]
                                values[name] = angles
                            else:
                                # Parse comma-separated float values
                                angles = [float(x.strip()) for x in text.split(',') if x.strip()]
                                values[name] = angles
                        except Exception as e:
                            QMessageBox.warning(self, "Input Error", f"Error parsing beam angles: {str(e)}")
                            values[name] = []
                    else:
                        # For saving state, just store the raw text without validation
                        values[name] = text
                else:
                    values[name] = text
            elif isinstance(widget, QWidget):  # File input container
                line_edit = widget.findChild(QLineEdit)
                if line_edit:
                    values[name] = line_edit.text().strip()
                    
        return values
        
    def compute_synthesis(self):    
        """
        Gathers input, runs the synthesis in a worker thread, and handles results.
        """
        current_index = self.method_combo.currentIndex()
        if current_index < 0:
            return
            
        current_method_name = self.method_combo.itemData(current_index)
        if current_method_name not in self.methods:
            return
            
        method = self.methods[current_method_name]
        
        try:
            input_values = self.get_input_values()
        except ValueError as e:
            # get_input_values can raise parsing errors, which we handle here.
            self.computation_error(str(e))
            return

        # Add global parameters to the input dictionary
        input_values['angle_unit'] = self.angle_unit_input
        input_values['resolution'] = self.resolution
        
        self.compute_button.setEnabled(False)
        # Translate the button text
        self.compute_button.setText(translations.tr("computing"))
        

        # --- Create worker and thread with non-conflicting names ---
        self.worker = ComputationWorker(method, input_values)
        # *** THE CRITICAL FIX for Pylance errors ***
        # Use a unique name like 'worker_thread' instead of 'thread' to avoid
        # conflict with the inherited QObject.thread() method.
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # --- Connect signals for a clean lifecycle ---
        # 1. Start the worker's run() method when the thread starts.
        self.worker_thread.started.connect(self.worker.run)
        
        # 2. Connect the worker's signals to the main window slots.
        self.worker.finished.connect(self.computation_finished)
        self.worker.error.connect(self.computation_error)
        
        # 3. Ensure the thread is quit and objects are deleted on BOTH success and error.
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        # This signal is emitted after the thread's event loop has finished.
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # 4. Start the thread.
        self.worker_thread.start()
        
    def computation_finished(self, results: Dict[str, Any]):
        """Handle computation completion."""
        self.current_results = results
        self.update_output_widgets(results)
        
        plotting_params = self._get_plotting_parameters()
        self.plotting_widget.update_plots(results, plotting_params)
        
        # Update coefficients table
        if hasattr(self, 'coefficients_table'):
            self.update_coefficients_table(results)
            
        # Elements plot is updated automatically by plotting_widget.update_plots()
            
        # Re-enable compute button
        self.compute_button.setEnabled(True)
        self.compute_button.setText(translations.tr("compute"))
        
    def computation_error(self, error_message: str):
        """
        Handles computation errors by translating the error key using a match/case structure.
        This approach is clean, readable, and scalable.
        """
        translated_error = ""
        
        # Split the error message to separate the key from potential data
        parts = error_message.split(':', 1)
        key = parts[0]

        match key:
            case "missing_parameter":
                # This case handles errors like "missing_parameter:d_lambda"
                param_name = parts[1]
                translated_param_key = self.find_label_key_for_param(param_name)
                translated_param_text = translations.tr(translated_param_key)
                translated_error = f"{translations.tr('missing_parameter')}: '{translated_param_text}'"

            case "multi_beam_angle_error":
                # This case handles dynamic errors like "multi_beam_angle_error:4:2"
                # where the values need to be formatted into the final message.
                _, expected, num_beams = error_message.split(':')
                base_message = translations.tr(key) # e.g., "{1} beams require {0} angles."
                translated_error = base_message.format(expected, num_beams)
            
            case "error_could_not_parse_beam_angles":
                # Handle "error_could_not_parse_beam_angles:1" format
                if ':' in error_message:
                    _, beam_number = error_message.split(':', 1)
                    base_message = translations.tr("error_could_not_parse_beam_angles")
                    translated_error = f"{base_message} {beam_number}"
                else:
                    translated_error = translations.tr("error_could_not_parse_beam_angles")
            
            case "error_unknown_beam_shape":
                # Handle "error_unknown_beam_shape:triangular" format
                if ':' in error_message:
                    _, beam_shape = error_message.split(':', 1)
                    base_message = translations.tr("error_unknown_beam_shape")
                    translated_error = f"{base_message}: '{beam_shape}'"
                else:
                    translated_error = translations.tr("error_unknown_beam_shape")
            
            case "error_unknown_normalization_method":
                # Handle "error_unknown_normalization_method:method_name" format
                if ':' in error_message:
                    _, method_name = error_message.split(':', 1)
                    base_message = translations.tr("error_unknown_normalization_method")
                    translated_error = f"{base_message}: '{method_name}'"
                else:
                    translated_error = translations.tr("error_unknown_normalization_method")

            case "number_of_elements_minimum" | "beam_angles_not_sorted" | "beam_angles_max_repetition" | "could_not_parse_beam_angles" | "invalid_number_of_beams" | "error_could_not_parse_null_angles" | "error_null_positions_cannot_be_empty" | "error_d_lambda_must_be_positive" | "error_resolution_must_be_at_least_16" | "error_main_beam_angle_out_of_range" | "error_number_of_elements_min_2" | "error_number_of_elements_min_1" | "error_sidelobe_level_must_be_finite" | "error_theta0_rad_out_of_range":
                # This case groups all simple, direct translation keys.
                # The pipe `|` acts as an "OR", making it very compact.
                translated_error = translations.tr(key)
            
            case _: # Default case for any unrecognized error
                # This is the fallback for any error message that doesn't match above.
                # It tries a direct translation first.
                translated_error = translations.tr(error_message)
                if translated_error == error_message: # If translation failed
                    # Wrap it in a generic error message
                    translated_error = f"{translations.tr('error_during_computation')} {error_message}"

        QMessageBox.critical(self, translations.tr("computation_error"), translated_error)
        
        # Re-enable the compute button
        self.compute_button.setEnabled(True)
        self.compute_button.setText(translations.tr("compute"))

    def find_label_key_for_param(self, param_name: str) -> str:
        """Helper to find the label key for a given parameter name."""
        current_method_key = self.method_combo.currentData()
        if current_method_key in self.methods:
            method = self.methods[current_method_key]
            for input_def in method.get_inputs(self.angle_unit_input):
                if input_def['name'] == param_name:
                    return input_def['label_key']
        return param_name # Fallback to the parameter name itself

    def update_output_widgets(self, results: Dict[str, Any]):
        """Update output widgets with new results using their keys."""
        # <<< CHANGE: Iterate over the keys in the output widgets dictionary
        for output_key, widget in self.output_widgets.items():
            if output_key in results:
                value = results[output_key]
                text = self.format_output_value(value)
                widget.setPlainText(text)
            else:
                # If a key is expected but not in the results, show 'Not available'
                widget.setPlainText(translations.tr("not_available"))
                
    def format_output_value(self, value) -> str:
        """Format output value for display."""
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                return f"{value:.{self.precision_decimals}f}"
            else:
                return str(value)
        elif isinstance(value, np.ndarray):
            if value.dtype == complex:
                formatted = [f"{x.real:.{self.precision_decimals}f}+{x.imag:.{self.precision_decimals}f}j" 
                           for x in value]
                return "\n".join(formatted)  # Show all elements
            else:
                formatted = [f"{x:.{self.precision_decimals}f}" for x in value]
                return "\n".join(formatted)  # Show all elements
        elif isinstance(value, list):
            formatted = [f"{x:.{self.precision_decimals}f}" if isinstance(x, float) else str(x) 
                        for x in value]
            return "\n".join(formatted)  # Show all elements
        else:
            return str(value)
    
    def export_to_json(self, filename: str):
        """Export inputs and outputs to JSON file."""
        if not self.current_results:
            raise ValueError("No results available to export")
        
        # Get current method and inputs
        current_method_key = self.method_combo.currentData()
        input_values = self.get_input_values()
        
        # Prepare data for JSON export
        export_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'method': current_method_key,
                'global_parameters': {
                    'precision_decimals': self.precision_decimals,
                    'angle_unit_input': self.angle_unit_input,
                    'resolution': self.resolution,
                    'threshold_db': self.threshold_db
                }
            },
            'inputs': input_values,
            'outputs': {}
        }
        
        # Convert results to JSON-serializable format
        for key, value in self.current_results.items():
            if isinstance(value, np.ndarray):
                if value.dtype == complex:
                    # Convert complex arrays to list of [real, imag] pairs
                    export_data['outputs'][key] = [[float(x.real), float(x.imag)] for x in value]
                else:
                    export_data['outputs'][key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                export_data['outputs'][key] = float(value)
            elif isinstance(value, complex):
                export_data['outputs'][key] = [float(value.real), float(value.imag)]
            elif isinstance(value, list):
                export_data['outputs'][key] = value
            else:
                export_data['outputs'][key] = str(value)
        
        # Write JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def export_array_factor_csv(self, filename: str):
        """Export array factor data to CSV file."""
        if not self.current_results:
            raise ValueError("No results available to export")
        
        required_keys = ['theta_degrees', 'theta_radians', 'af', 'normalized_af', 'af_db']
        missing_keys = [key for key in required_keys if key not in self.current_results]
        if missing_keys:
            raise ValueError(f"Array factor data not available in results: {missing_keys}")
        
        theta_deg = self.current_results['theta_degrees']
        theta_rad = self.current_results['theta_radians']
        af = self.current_results['af']
        normalized_af = self.current_results['normalized_af']
        af_db = self.current_results['af_db']
        
        # Write CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Theta (degrees)', 'Theta (radians)', 'AF (complex)', 'AF Normalized (complex)', 'AF (dB)'])
            
            # Write data
            for i in range(len(theta_deg)):
                # Format complex numbers as "real+imag*j"
                af_complex_str = f"{af[i].real:.{self.precision_decimals}f}{af[i].imag:+.{self.precision_decimals}f}j"
                af_norm_complex_str = f"{normalized_af[i].real:.{self.precision_decimals}f}{normalized_af[i].imag:+.{self.precision_decimals}f}j"
                
                writer.writerow([
                    f"{theta_deg[i]:.{self.precision_decimals}f}",
                    f"{theta_rad[i]:.{self.precision_decimals}f}",
                    af_complex_str,
                    af_norm_complex_str,
                    f"{af_db[i]:.{self.precision_decimals}f}"
                ])
    
    def export_plots(self, base_filename: str, file_format: str):
        """Export plots using the plotting widget."""
        if hasattr(self, 'plotting_widget'):
            return self.plotting_widget.export_plots(base_filename, file_format)
        else:
            raise ValueError("Plotting widget not available")
    
    def export_plots_dialog(self, file_format: str):
        """Show dialog to export plots."""
        if not self.current_results:
            QMessageBox.warning(self, translations.tr("export_error"), translations.tr("no_results_to_export"))
            return
        
        # Get current method key for default filename
        method_key = self.method_combo.currentData().lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"antenna_synthesis_{method_key}_{timestamp}"
        
        # Show save dialog
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            f"Export Plots as {file_format.upper()}", 
            default_filename,
            f"{file_format.upper()} files (*.{file_format})"
        )
        
        if filename:
            try:
                # Remove extension if present
                base_filename = filename.rsplit('.', 1)[0]
                exported_files = self.export_plots(base_filename, file_format)
                
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"Plots exported successfully:\n" + "\n".join(exported_files)
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Error exporting plots:\n{str(e)}")
    
    def export_json_dialog(self):
        """Show dialog to export data as JSON."""
        if not self.current_results:
            QMessageBox.warning(self, translations.tr("export_error"), translations.tr("no_results_to_export"))
            return
        
        # Get current method key for default filename
        method_key = self.method_combo.currentData().lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"antenna_synthesis_{method_key}_{timestamp}.json"
        
        # Show save dialog
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Data as JSON", 
            default_filename,
            "JSON files (*.json)"
        )
        
        if filename:
            try:
                self.export_to_json(filename)
                QMessageBox.information(self, "Export Successful", f"Data exported successfully to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Error exporting data:\n{str(e)}")
    
    def export_csv_dialog(self):
        """Show dialog to export array factor as CSV."""
        if not self.current_results:
            QMessageBox.warning(self, translations.tr("export_error"), translations.tr("no_results_to_export"))
            return
        
        # Get current method key for default filename
        method_key = self.method_combo.currentData().lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"array_factor_{method_key}_{timestamp}.csv"
        
        # Show save dialog
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Array Factor as CSV", 
            default_filename,
            "CSV files (*.csv)"
        )
        
        if filename:
            try:
                self.export_array_factor_csv(filename)
                QMessageBox.information(self, "Export Successful", f"Array factor data exported successfully to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Error exporting array factor:\n{str(e)}")

    def _get_plotting_parameters(self) -> Dict[str, Any]:
        """
        Gathers all global parameters relevant for plotting into a single dictionary.
        """
        # Get current method and input values for elements plot
        current_method_key = self.method_combo.currentData() if hasattr(self, 'method_combo') else 'Schelkunoff'
        input_values = self.get_input_values() if hasattr(self, 'input_widgets') else {}
        layout_type = 'symmetric'
        
        if current_method_key in self.methods:
            layout_type = self.methods[current_method_key].layout_type
        
        return {
            'threshold_db': self.threshold_db,
            'angle_unit_rectangular': self.angle_unit_rectangular,
            'angle_unit_polar': self.angle_unit_polar,
            'element_phase_unit': self.element_phase_unit,
            'rectangular_scale': self.rectangular_scale,
            'polar_scale': self.polar_scale,
            'normalize_array_factor': self.normalize_array_factor,
            # Parameters for elements plot
            'input_values': input_values,
            'layout_type': layout_type,
            'angle_unit_input': self.angle_unit_input
        }