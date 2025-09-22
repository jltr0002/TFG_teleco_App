"""
Preferences dialog for the antenna synthesis application.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, 
                              QComboBox, QLabel, QDialogButtonBox, QFormLayout, QSpinBox)
from PySide6.QtCore import Signal
from translations import translations
from config.settings import ConfigManager

class PreferencesDialog(QDialog):
    """Dialog for application preferences."""
    
    language_changed = Signal(str)  # Signal emitted when language changes
    font_size_changed = Signal(int)  # Signal emitted when font size changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translations.tr("preferences_title"))
        self.setModal(True)
        # Remove fixed size to allow automatic resizing
        
        # Apply current font size from parent
        if parent and hasattr(parent, 'current_font_size'):
            font = self.font()
            font.setPointSize(parent.current_font_size)
            self.setFont(font)
        
        # Flag to prevent recursive updates
        self.updating = False
        
        self.setup_ui()
        self.load_current_values()
        
        # Adjust size to content after UI is created
        self.adjustSize()
        self.setMinimumWidth(300)  # Set minimum width for usability
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Language group
        self.language_group = QGroupBox(translations.tr("language"))
        language_layout = QFormLayout(self.language_group)
        
        # Language selection
        self.language_combo = QComboBox()
        available_languages = translations.get_available_languages()
        for code, name in available_languages.items():
            self.language_combo.addItem(name, code)
        
        self.language_label = QLabel(translations.tr("language") + ":")
        language_layout.addRow(self.language_label, self.language_combo)
        layout.addWidget(self.language_group)
        
        # Font size group
        self.font_group = QGroupBox(translations.tr("font_size"))
        font_layout = QFormLayout(self.font_group)
        
        # Font size selection
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(6)
        self.font_size_spinbox.setMaximum(24)
        self.font_size_spinbox.setValue(12)  # Default value
        self.font_size_spinbox.setSuffix(" pt")
        
        self.font_size_label = QLabel(translations.tr("font_size") + ":")
        font_layout.addRow(self.font_size_label, self.font_size_spinbox)
        layout.addWidget(self.font_group)
        
        # Spacer
        layout.addStretch()
        
        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        # Connect signals
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.font_size_spinbox.valueChanged.connect(self.on_font_size_changed)
    
    def load_current_values(self):
        """Load current values."""
        current_language = translations.get_language()
        # Find the index of the current language
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_language:
                self.language_combo.setCurrentIndex(i)
                break
        
        # Load current font size from config
        config_manager = ConfigManager()
        config = config_manager.load_config()
        current_font_size = config.get('font_size', 12)
        self.font_size_spinbox.setValue(current_font_size)
    
    def on_language_changed(self, index):
        """Handle language change."""
        if self.updating:
            return
            
        language_code = self.language_combo.itemData(index)
        if language_code:
            self.updating = True
            
            # Set the language in the translations module FIRST
            translations.set_language(language_code)
            
            # Update the dialog's own UI
            self.update_ui_language()
            
            # Emit signal to update the main window (after language is set)
            self.language_changed.emit(language_code)
            
            self.updating = False
    
    def on_font_size_changed(self, value):
        """Handle font size change."""
        if self.updating:
            return
        
        # Save font size to config
        config_manager = ConfigManager()
        config = config_manager.load_config()
        config['font_size'] = value
        config_manager.save_config(config)
        
        # Emit signal
        self.font_size_changed.emit(value)
    
    def update_ui_language(self):
        """Update the UI language of this dialog."""
        try:
            # Update window title
            self.setWindowTitle(translations.tr("preferences_title"))
            
            # Update group box titles
            self.language_group.setTitle(translations.tr("language"))
            self.font_group.setTitle(translations.tr("font_size"))
            
            # Update labels
            self.language_label.setText(translations.tr("language") + ":")
            self.font_size_label.setText(translations.tr("font_size") + ":")
            
            # Update button box (recreate with new language)
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText(translations.tr("ok"))
            self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(translations.tr("cancel"))
            
        except (RuntimeError, AttributeError):
            # Dialog might be closing or widgets might be deleted, ignore the error
            pass
    
    def get_language(self) -> str:
        """Get the selected language."""
        return self.language_combo.currentData()
    
    def get_font_size(self) -> int:
        """Get the selected font size."""
        return self.font_size_spinbox.value()
    
    def closeEvent(self, event):
        """Handle close event."""
        # Disconnect signals to prevent issues when closing
        if hasattr(self, 'language_combo'):
            self.language_combo.currentIndexChanged.disconnect()
        super().closeEvent(event)